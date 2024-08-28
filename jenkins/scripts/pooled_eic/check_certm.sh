#!/bin/bash

PWD=$1
PATH_TO_CERTS=$2


mkdir -p $PWD/certificates/iam-http-server
mkdir -p $PWD/certificates/iam-ldap-server
mkdir -p $PWD/certificates/la-syslog-client
mkdir -p $PWD/certificates/la-http-server
mkdir -p $PWD/certificates/la-http-client
mkdir -p $PWD/certificates/enm-http-client
mkdir -p $PWD/certificates/eric-log-client-certs-cacert
mkdir -p $PWD/certificates/sef-osm-http-client
mkdir -p $PWD/certificates/sef-osm-iam-client
mkdir -p $PWD/certificates/bootstrap-http-server

#Copy Intermediate CA

cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/iam-http-server/iam-http-server.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/iam-ldap-server/iam-ldap-server.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/la-syslog-client/la-syslog-client.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/la-http-server/la-http-server.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/la-http-client/la-http-client.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/enm-http-client/enm-http-client.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/eric-log-client-certs-cacert/eric-log-client-certs-cacert.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/sef-osm-http-client/sef-osm-http-client.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/sef-osm-iam-client/sef-osm-iam-client.crt
cp $PWD/$PATH_TO_CERTS/intermediate-ca.crt $PWD/certificates/bootstrap-http-server/bootstrap-http-server.crt

#Copy certificates

cp $PWD/$PATH_TO_CERTS/th*crt $PWD/certificates/th-http-server.crt
cp $PWD/$PATH_TO_CERTS/th*key $PWD/certificates/th-http-server.key

cp $PWD/$PATH_TO_CERTS/iam*crt $PWD/certificates/iam-http-server.crt
cp $PWD/$PATH_TO_CERTS/iam*key $PWD/certificates/iam-http-server.key

cp $PWD/$PATH_TO_CERTS/la*crt $PWD/certificates/la-http-server.crt
cp $PWD/$PATH_TO_CERTS/la*key $PWD/certificates/la-http-server.key

cp $PWD/$PATH_TO_CERTS/gas*crt $PWD/certificates/gas-http-server.crt
cp $PWD/$PATH_TO_CERTS/gas*key $PWD/certificates/gas-http-server.key

cp $PWD/$PATH_TO_CERTS/adc*crt $PWD/certificates/ves-http-server.crt
cp $PWD/$PATH_TO_CERTS/adc*key $PWD/certificates/ves-http-server.key

cp $PWD/$PATH_TO_CERTS/appmgr*crt $PWD/certificates/appmgr-http-server.crt
cp $PWD/$PATH_TO_CERTS/appmgr*key $PWD/certificates/appmgr-http-server.key

cp $PWD/$PATH_TO_CERTS/gas*crt $PWD/certificates/eric-log-client-certs.crt
cp $PWD/$PATH_TO_CERTS/gas*key $PWD/certificates/eric-log-client-certs.key

cp $PWD/$PATH_TO_CERTS/gas*crt $PWD/certificates/sef-osm-http-client.crt
cp $PWD/$PATH_TO_CERTS/gas*key $PWD/certificates/sef-osm-http-client.key

cp $PWD/$PATH_TO_CERTS/iam*crt $PWD/certificates/sef-osm-iam-client.crt
cp $PWD/$PATH_TO_CERTS/iam*key $PWD/certificates/sef-osm-iam-client.key

cp $PWD/$PATH_TO_CERTS/bootstrap*crt $PWD/certificates/bootstrap-http-server.crt
cp $PWD/$PATH_TO_CERTS/bootstrap*key $PWD/certificates/bootstrap-http-server.key