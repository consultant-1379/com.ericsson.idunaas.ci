#!/bin/bash

NAMESPACE=$1
KUBE_CONFIG=$2

function check_for_installed_version()
{
    echo -e "Checking for current installed version \n"
    VALUE=$(kubectl --namespace "${NAMESPACE}" --kubeconfig "${KUBE_CONFIG}" get configmap eric-installed-applications -o jsonpath={.data.Installed} | /usr/local/bin/yq eval --unwrapScalar .helmfile.release -)

    if [ -z "${VALUE}" ] || [ "${VALUE}" == "None" ] || [ "${VALUE}" == "null" ]; then
        echo -e "No value found for the installed chart version."
        exit 1
    else
        echo -e "Installed chart version found : "${VALUE}""
        echo "${VALUE}" > .bob/var.oss-version
    fi
}

check_for_installed_version