#!/bin/bash

ACTION=$1
NAMESPACE=$2
KUBE_CONFIG_PATH=$3
PASSWORD=$4
PASSWORD_DDC_ADP=$5

#VARIABLES
ECHO="/bin/echo"
KUBECTL="/usr/local/bin/kubectl"

#######################################################
# Create PG Database Secret                           #
#                                                     #
# Arguments: None                                     #
# Returns: None                                       #
#######################################################
function create_database_pg_secret()
{
    ${ECHO} "Creating PG Database Secret..."
    ${KUBECTL} create secret generic eric-eo-database-pg-secret \
        --namespace="${NAMESPACE}" \
        --from-literal=custom-user='customuser' \
        --from-literal=custom-pwd="${PASSWORD}" \
        --from-literal=super-user='postgres' \
        --from-literal=super-pwd="${PASSWORD}" \
        --from-literal=metrics-user='metricsuser' \
        --from-literal=metrics-pwd="${PASSWORD}" \
        --from-literal=replica-user='replicauser' \
        --from-literal=replica-pwd="${PASSWORD}" \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    ${ECHO} "Created PG Database Secret"
}

function create_adp_ddc_sftp_secret()
{
    ${ECHO} "Creating ADP DDC SFTP Secret..."

    ${KUBECTL} create secret generic eric-odca-diagnostic-data-collector-sftp-credentials \
        --namespace="${NAMESPACE}" \
        --from-literal=sftp_credentials.json='{"username":"sftpuser","password":"'${PASSWORD_DDC_ADP}'"}' \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    ${ECHO} "Created ADP DDC SFTP Secret"
}

#######################################################
# Create eric-helm-executor                           #
#     Clusterrolebinding                              #
# Arguments: None                                     #
# Returns: None                                       #
#######################################################
function create_crb()
{
    ${ECHO} "Creating eric-helm-executor clusterrolebindings..."
    ${KUBECTL} create clusterrolebinding ${NAMESPACE} \
        --clusterrole="cluster-admin" \
        --serviceaccount="${NAMESPACE}":"eric-lcm-helm-executor" \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    ${ECHO} "Created eric-helm-executor clusterrolebindings"
}


#######################################################
# Create appmgr secret                                #
#                                                     #
# Arguments: None                                     #
# Returns: None                                       #
#######################################################
function create_appmgr_db_credentials()
{
    ${ECHO} "Creating appmgr secret..."
    ${KUBECTL} create secret generic eric-appmgr-data-document-db-credentials \
        --namespace="${NAMESPACE}" \
        --from-literal=custom-user='customuser' \
        --from-literal=custom-pwd="${PASSWORD}" \
        --from-literal=super-user='postgres' \
        --from-literal=super-pwd="${PASSWORD}" \
        --from-literal=metrics-user='exporter' \
        --from-literal=metrics-pwd="${PASSWORD}" \
        --from-literal=replica-user='replica' \
        --from-literal=replica-pwd="${PASSWORD}" \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    ${ECHO} "Created appmgr Secret"
}

#######################################################
# Create Access Management Credentials Secret         #
#                                                     #
# Arguments: None                                     #
# Returns: None                                       #
#######################################################
function create_access-mgmt-creds()
{
    ${ECHO} "Creating Access Management Credentials Secret..."
    ${KUBECTL} create secret generic eric-sec-access-mgmt-creds \
        --namespace="${NAMESPACE}" \
        --from-literal=kcadminid='kcadmin' \
        --from-literal=kcpasswd="${PASSWORD}" \
        --from-literal=pgpasswd="${PASSWORD}" \
        --from-literal=pguserid='pguser' \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    ${ECHO} "Created Access Management Credentials Secret"
}
#######################################################
# Create SEF Authentication Proxy Secret              #
#                                                     #
# Arguments: None                                     #
# Returns: None                                       #
#######################################################
function create_sef-auth-proxy-creds()
{
    ${ECHO} "Creating SEF Authentication Proxy Secret..."
    ${KUBECTL} create secret generic eric-sec-access-mgmt-aapxy-creds \
        --namespace="${NAMESPACE}" \
        --from-literal=aapxysecret="${PASSWORD}" \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    ${ECHO} "Created SEF Authentication Proxy Secret"
}
#######################################################
# Create K8 Registry Credential Secret                #
#                                                     #
# Arguments: None                                     #
# Returns: None                                       #
#######################################################
function create_k8-registry-creds()
{
    ${ECHO} "Creating K8 Registry Secret Credentials..."
    ${KUBECTL} create secret generic k8s-registry-secret \
        --namespace ${NAMESPACE} \
        --from-file=.dockerconfigjson=./dockerconfig.json \
        --type=kubernetes.io/dockerconfigjson \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    ${KUBECTL} create secret generic k8s-registry-secret \
        --namespace eric-crd-ns \
        --from-file=.dockerconfigjson=./dockerconfig.json \
        --type=kubernetes.io/dockerconfigjson \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    if [[ $? -ne 0 ]]; then
        exit 1
    fi
    ${ECHO} "Created K8 Registry Secret."
}

function delete_k8-registry-creds()
{
    for ns in ${NAMESPACE} eric-crd-ns
    do
      ${KUBECTL} get secrets --namespace ${ns} --kubeconfig ${KUBE_CONFIG_PATH} k8s-registry-secret; RC=$?
      if [[ $RC -eq 0 ]]
      then
        ${ECHO} "Deleting K8 Registry Secret Credentials..."
        ${KUBECTL} delete secrets k8s-registry-secret --namespace ${ns} --kubeconfig ${KUBE_CONFIG_PATH} || exit 1
      else
        ${ECHO} "'k8s-registry-secret' Secret not present in '${ns}' namespace"
      fi
    done
}

function delete_secrets() {
    secrets=$(${KUBECTL} get secret --namespace="${NAMESPACE}" --kubeconfig "${KUBE_CONFIG_PATH}" -o=jsonpath='{.items[*].metadata.name}')

    for secret_name in $secrets; do
        if [[ $secret_name != *"token"* && $secret_name != *"helm"* ]]; then
            ${ECHO} "Deleting Secret ${secret_name}..."
            ${KUBECTL} delete secret "${secret_name}" --namespace="${NAMESPACE}" --kubeconfig "${KUBE_CONFIG_PATH}"
            if [[ $? -ne 0 ]]; then
                ${ECHO} "Failed to delete Secret ${secret_name}"
                exit 1
            fi
            ${ECHO} "Deleted Secret ${secret_name}"
        else
            ${ECHO} "Ignoring Secret ${secret_name}"
        fi
    done
}

function delete_secret()
{
    secret_name=${1}
    ${KUBECTL} get secret "${secret_name}" \
        --namespace="${NAMESPACE}" \
        --kubeconfig "${KUBE_CONFIG_PATH}" >/dev/null 2>&1
    if [[ $? -eq 0 ]];then
        ${ECHO} "Deleting Secret ${secret_name}..."
        ${KUBECTL} delete secret "${secret_name}" \
            --namespace="${NAMESPACE}" \
            --kubeconfig "${KUBE_CONFIG_PATH}"
        if [[ $? -ne 0 ]];then
            exit 1
        fi
        ${ECHO} "Deleted Secret ${secret_name}"
    else
        ${ECHO} "Secret ${secret_name} does not exist"
    fi
}

function delete_crb()
{
    crb_name=${1}
    ${KUBECTL} get clusterrolebinding "${crb_name}" \
        --kubeconfig "${KUBE_CONFIG_PATH}" >/dev/null 2>&1
    if [[ $? -eq 0 ]];then
        ${ECHO} "Deleting clusterrolebinding ${crb_name}..."
        ${KUBECTL} delete clusterrolebinding "${crb_name}" \
            --kubeconfig "${KUBE_CONFIG_PATH}"
        if [[ $? -ne 0 ]];then
            exit 1
        fi
        ${ECHO} "Deleted clusterrolebinding ${crb_name}"
    else
        ${ECHO} "clusterrolebinding ${crb_name} does not exist"
    fi
}

if [[ ${ACTION} == "create" ]];then
    create_database_pg_secret
    create_access-mgmt-creds
    create_appmgr_db_credentials
    create_crb
    create_k8-registry-creds
    create_adp_ddc_sftp_secret
    create_sef-auth-proxy-creds
else
    delete_secrets
    delete_crb ${NAMESPACE}
    delete_k8-registry-creds
fi

