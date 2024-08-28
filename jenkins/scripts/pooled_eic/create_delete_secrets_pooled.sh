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


function create_testware_resources_secret()
{
    ${ECHO} "Creating testware-resources Secret..."

    local API_URL="http://api.dev-staging-report.ews.gic.ericsson.se/api"
    local GUI_URL="http://gui.dev-staging-report.ews.gic.ericsson.se/staging-tests"
    local DATABASE_URL="postgresql://testware_user:testware@kroto017.rnd.gic.ericsson.se:30001/staging"

    local api_url_encoded=$(echo "$API_URL" | base64 -w 0)
    local gui_url_encoded=$(echo "$GUI_URL" | base64 -w 0)
    local database_url_encoded=$(echo "$DATABASE_URL" | base64 -w 0)

    ${KUBECTL} create secret generic testware-resources-secret \
        --namespace="${NAMESPACE}" \
        --from-literal=api_url=$api_url_encoded \
        --from-literal=gui_url=$gui_url_encoded \
        --from-literal=database_url=$database_url_encoded \
        --kubeconfig "${KUBE_CONFIG_PATH}"
    if [[ $? -ne 0 ]];then
        exit 1
    fi
    ${ECHO} "Created testware-resources Secret"
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
    create_adp_ddc_sftp_secret
else
    delete_secret eric-eo-database-pg-secret
    delete_secret eric-sec-access-mgmt-creds
    delete_secret eric-appmgr-data-document-db-credentials
    delete_secret gas-tls-secret
    delete_secret iam-cacert-secret
    delete_secret iam-tls-secret
    delete_secret pf-tls-secret
    delete_secret so-tls-secret
    delete_secret uds-tls-secret
    delete_secret app-mgr-tls-secret
    delete_secret eric-data-coordinator-zk
    delete_secret eric-data-message-bus-kf
    delete_secret eric-sec-sip-tls-bootstrap-ca-cert
    delete_secret eric-sec-sip-tls-trusted-root-cert
    delete_secret eric-odca-diagnostic-data-collector-sftp-credentials
    delete_secret testware-resources-secret
    delete_crb ${NAMESPACE}

fi

