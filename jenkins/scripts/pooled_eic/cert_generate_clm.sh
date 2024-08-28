#!/bin/bash
TAGS="$1"
DOMAIN_NAME="$2"
WORKDIR="$3"

generate_token(){
  TMPFILE=.tmp.token.$RANDOM
  curl -s   --request POST \
            --header "Content-Type: application/json" \
            --url https://clm-api.ericsson.net/vedauth/authorize/certificate \
            --data @${WORKDIR}/jenkins/scripts/pooled_eic/certs/oauth.json \
            --key ${WORKDIR}/jenkins/scripts/pooled_eic/certs/sts-oss-support.cba.clm.local.key \
            --cert ${WORKDIR}/jenkins/scripts/pooled_eic/certs/sts-oss-support.cba.clm.local.pem \
            | jq -r .access_token > $TMPFILE
  CURL_JQ_RC="${PIPESTATUS[0]}-${PIPESTATUS[1]}"
  TOKEN=$(cat $TMPFILE | tr -d '\r' | tr -d '\n')
  rm -f $TMPFILE

  [ "$CURL_JQ_RC" != "0-0" ] && \
    echo "Error: token not properly generated (CURL_JQ_RC=${CURL_JQ_RC})" && \
    exit -1
}


download_cert(){
    CERT_HOSTNAME="$1"
    cp ${WORKDIR}/jenkins/scripts/pooled_eic/templates/retrive_crt_tmpl.json ${CERT_HOSTNAME}_retrive_crt.json
    sed -i "s/CERT_CN_REPLACE/${CERT_HOSTNAME}/g" ${CERT_HOSTNAME}_retrive_crt.json

    response=$(curl -s --request POST --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json" --data  @${CERT_HOSTNAME}_retrive_crt.json --url https://clm-api.ericsson.net/vedsdk/Certificates/Retrieve --cacert ${WORKDIR}/jenkins/scripts/pooled_eic/certs/sts-oss-support.cba.clm.local.pem)
    echo "$response" | grep CertificateData || echo 1 && echo "$response" | jq -r .CertificateData | base64 -d > ${CERT_HOSTNAME}.crt

}

create_certificate_for () {
    CERT_HOSTNAME="$1"
    openssl req -new -newkey rsa:2048 -nodes -out ${CERT_HOSTNAME}.csr -keyout ${CERT_HOSTNAME}.key -subj "/C=SE/ST=Stockholm/L=Stockholm/O=Ericsson AB/OU=IT/CN=${CERT_HOSTNAME}" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf "\n[SAN]\nsubjectAltName=DNS:${CERT_HOSTNAME}"))
    csr_text=$(cat ${CERT_HOSTNAME}.csr)

    cp ${WORKDIR}/jenkins/scripts/pooled_eic/templates/cert_request_tmpl.json ${CERT_HOSTNAME}_cert_request.json
    awk -v r="${csr_text}" '{gsub(/CSR_REPLACE/,r)}1' ${CERT_HOSTNAME}_cert_request.json > tmp.json
    mv tmp.json ${CERT_HOSTNAME}_cert_request.json

    for i in {1,2,3}
    do
      echo "==== ATTEMPT $i of 3  for ${tag}${DOMAIN_NAME} ========"
      request_response=$(curl -s --request POST --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json" --data  @${CERT_HOSTNAME}_cert_request.json --url https://clm-api.ericsson.net/vedsdk/Certificates/Request --cacert ${WORKDIR}/jenkins/scripts/pooled_eic/certs/sts-oss-support.cba.clm.local.pem)
      while ( echo "$request_response" | grep "Custom Field error" )
      do
        sleep 1
        request_response=$(curl -s --request POST --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json" --data  @${CERT_HOSTNAME}_cert_request.json --url https://clm-api.ericsson.net/vedsdk/Certificates/Request --cacert ${WORKDIR}/jenkins/scripts/pooled_eic/certs/sts-oss-support.cba.clm.local.pem)
      done

      guid=$(echo "$request_response" | jq -r .Guid)
      echo "Cert $CERT_HOSTNAME guid =  $guid"

      [[ "$(download_cert $CERT_HOSTNAME)" == 1 ]] && {
        echo "==== Waiting 30s  ${tag}${DOMAIN_NAME}.crt for certificage to be generated"
        sleep  30
      } || break

      [[ "$(download_cert ${tag}${DOMAIN_NAME})" == 1 ]] && {
        echo "Certifcate cannot be download - deleting cert"
        curl -s --request DELETE --header "Authorization: Bearer $TOKEN" --header "Content-Type: application/json"  https://clm-api.ericsson.net/vedsdk/certificates/${guid}
        [[ "$1" == 1 ]] && echo "##################################### certificate $CERT_HOSTNAME is not generated and not saved in CLM #####################################\n Pleas rerun job"
      } || break

    done

}

#MAIN
generate_token

for tag in $TAGS bootstrap
do
  echo "==== Checking if ${tag}${DOMAIN_NAME}.crt exists "
  [[ "$(download_cert ${tag}${DOMAIN_NAME})" == 1 ]] && {
    echo "==== ${tag}${DOMAIN_NAME}.crt DOES NOT exists "
    echo "==== Requesting ${tag}${DOMAIN_NAME}.crt"
    create_certificate_for ${tag}${DOMAIN_NAME}
  }
done

rm -f *.json

openssl verify -CAfile intermediate-ca.crt *.crt