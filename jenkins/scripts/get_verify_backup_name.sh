#!/bin/bash

HELM="/usr/local/bin/helm"

NAMESPACE="$1"
KUBE_CONFIG="$2"
BACKUP_NAME="$3"

# Variable
BACKUP_VAR_FILE=".bob/var.backup_name"
OSS_CHART="eric-oss"

#######################################################
# Get backup name and verify                          #
#                                                     #
# Arguments: None                                     #
# Returns: None                                       #
#######################################################
function check_verify_backupname()
{
    echo "Checking and verifying the backup name..."
    rm -f "${BACKUP_VAR_FILE}"

    if [[ -z "$BACKUP_NAME" ]]; then
        echo "No backup name provided, looking for backupname annotation on namespace ${NAMESPACE}..."
        BACKUP_NAME=$(kubectl get namespace "${NAMESPACE}" --kubeconfig "${KUBE_CONFIG}" -o jsonpath={.metadata.annotations.backupname})
        if [[ -z ${BACKUP_NAME} ]]; then
            echo "No backupname annotation found on the namespace ${NAMESPACE}"
            exit 1
        fi
    fi

    if [[ -z "${INSTALLED_OSS}" ]]; then
        echo "Could not determine the installed IDUN version"
        exit 1
    fi

    if echo "${BACKUP_NAME}" | grep -q "${INSTALLED_OSS}"; then
        echo "${BACKUP_NAME}" > ${BACKUP_VAR_FILE}
        echo "Backup name is ${BACKUP_NAME}"
    else
        echo "Backup ${BACKUP_NAME} is not for the installed IDUN version ${INSTALLED_OSS}"
        exit 1
    fi
}

#######################################################
# Main                                                #
#                                                     #
# Arguments:                                          #
#   $1: Namespace                                     #
#   $2: Kube config file                              #
#   $3: Backup name (optional)                        #
# Returns: None                                       #
#######################################################
function main()
{
    if [[ $# -lt 2 ]]; then
        echo "Usage: $0 <namespace> <kube_config_file> [backup_name]"
        exit 1
    fi

    ${HELM} list --namespace "${NAMESPACE}" --kubeconfig "${KUBE_CONFIG}" | grep eric-oss-common-base >/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        INSTALLED_OSS=$(kubectl get namespace "${NAMESPACE}" --kubeconfig "${KUBE_CONFIG}" -o jsonpath={.metadata.annotations.idunaas/installed-helmfile})
    else
        INSTALLED_OSS=$(${HELM} list --filter "${OSS_CHART}-${NAMESPACE}" --namespace "${NAMESPACE}" --kubeconfig "${KUBE_CONFIG}" --output yaml | \
        grep -i chart | grep ${OSS_CHART} | sed 's/[^0-9.-]//g' | sed -r 's/-+//')
    fi

    check_verify_backupname
}

main "$@"

