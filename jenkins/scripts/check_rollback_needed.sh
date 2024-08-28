#!/bin/bash

HELM="/usr/local/bin/helm"
HELMFILE="/usr/local/bin/helmfile"

NAMESPACE=$1
KUBE_CONFIG=$2
CHART_VERSION=$3
STATE_VALUES_FILE=$4

function check_rollback_required() {
    rollback_needed="false"
    echo "Checking if a rollback needs to be initiated..."
    ROLLBACK_BACKUP_NAME=$(kubectl get namespace "${NAMESPACE}" --kubeconfig "${KUBE_CONFIG}" -o jsonpath={.metadata.annotations.backupname})
    if [[ -z ${ROLLBACK_BACKUP_NAME} ]]; then
        echo "No backupname annotation found on the namespace ${NAMESPACE}"
        rollback_needed="false"
    else
        check_rollback_required_helmfile
    fi
    echo "ROLLBACK_REQUIRED=${rollback_needed}" >> "artifact.properties"
}

function check_rollback_required_helmfile() {
    # Get the number of releases in the deployment for a given namespace
    printf "\nCurrent releases in namespace ${NAMESPACE}:\n"
    ${HELM} list --all --namespace ${NAMESPACE} --kubeconfig ${KUBE_CONFIG} --output yaml | grep 'chart\|status'
    DEPLOYED_VERSIONS=$(helm list --all --namespace ${NAMESPACE} --kubeconfig ${KUBE_CONFIG} --output yaml | grep -i chart)
    readarray -t DEPLOYED_VERSIONS_ARRAY <<<"$DEPLOYED_VERSIONS"
    NUMBER_OF_RELEASES="${#DEPLOYED_VERSIONS_ARRAY[@]}"

    # Get the number of successfully deployed releases
    SUCCESSFUL_RELEASES=$(helm list --namespace ${NAMESPACE} --kubeconfig ${KUBE_CONFIG} --output yaml | grep -i deployed | tr -d "[:blank:]")
    readarray -t SUCCESSFUL_RELEASES_ARRAY <<<"$SUCCESSFUL_RELEASES"
    NUMBER_OF_SUCCESSFUL_RELEASES="${#SUCCESSFUL_RELEASES_ARRAY[@]}"
    printf "\nNumber of successful releases in deployment: ${NUMBER_OF_SUCCESSFUL_RELEASES} of ${NUMBER_OF_RELEASES}\n\n"

    ### 2. Check if the number of total releases matches the number of successful releases
    if [ "${NUMBER_OF_RELEASES}" == "${NUMBER_OF_SUCCESSFUL_RELEASES}" ]; then
        rollback_needed="false"
        echo "*** Number of successful releases matches number of total releases, skipping rollback"
    else
        echo "*** Number of successful releases does not match number of total releases"
        readarray -t DEPLOYED_VERSIONS_ARRAY_SORTED < <(for a in "${DEPLOYED_VERSIONS_ARRAY[@]}"; do echo "$a" | grep -Poe "([^\.]*+\.)++\d" | sed -e 's/^[[:space:]]*//'; done | sort)

        DEPLOYED_APPLICATIONS=${DEPLOYED_VERSIONS_ARRAY_SORTED[*]}
        echo "Deployed applications:" $DEPLOYED_APPLICATIONS

        ### Check if any of the installed releases of IDUN is in failed state to do a rollback
        # Get chart names from helmfile list command, awk to pull out chart name and version
        cp ${STATE_VALUES_FILE} eric-eiae-helmfile/
        CHARTS=$(${HELMFILE} --state-values-file ${STATE_VALUES_FILE} --file eric-eiae-helmfile/helmfile.yaml list | awk '{print $1}')
        printf '%s\n' "${CHARTS_ARRAY}"
        # Read output into array
        readarray -t CHARTS_ARRAY <<<"$CHARTS"
        # Remove first element which contains headings from helmfile list output
        CHARTS_ARRAY=("${CHARTS_ARRAY[@]:1}")
        printf "\n---------- Charts in helmfile ----------\n"
        printf '%s\n' "${CHARTS_ARRAY[@]}"

        printf "\n---------- Checking for failed chart ----------\n"
        for release in "${CHARTS_ARRAY[@]}"
        do
            if [[ "${DEPLOYED_VERSIONS_ARRAY_SORTED[*]}" != *"${release}"* ]]; then
                rollback_needed="false"
                echo "${release} is not deployed on system"
            else
                ${HELM} list --all --filter "${release}" --namespace "${NAMESPACE}" --kubeconfig "${KUBE_CONFIG}" --output yaml \
                | grep status |grep -iE "failed|pending-install|pending-upgrade" >/dev/null 2>&1
                if [[ $? -eq 0 ]]; then
                    rollback_needed="true"
                    echo "*** Chart ${release} is in failed or pending state, rollback is needed"
                    break
                else
                    rollback_needed="false"
                fi
            fi
        done
    fi
}

check_rollback_required