#!/bin/bash

# default values
DOCKERCONFIG=/workdir/dockerconfig.json

# extract parameters:
while [ $# -gt 0 ]; do
    case "$1" in
        "--namespace")
            shift
            NAMESPACE="$1"
        ;;
        "--kubeconfig")
            shift
            KUBECONFIG="$1"
        ;;
        "--dockerconfig")
            shift
            DOCKERCONFIG="$1"
        ;;
        *)
            echo "[$(basename $0)] ERROR: Bad command line argument: '$1'"
            echo "$0 --action <ADD-USER || REMOVE-USER || ADD-ADMIN || REMOVE_ADMIN> --users <Eg: 'zshicna,zlaigar,zmcddec' > --namespace <eic namespace> --clusterid <cluster ID> --kubeconfig <kubeconfig file>"
            exit -1
        ;;
    esac
    shift
done

function add_registry_secret() {

    if kubectl --kubeconfig $KUBECONFIG --namespace $NAMESPACE get secret k8s-registry-secret; then
        echo "Secret exists in namespace ${NAMESPACE}"
        kubectl --kubeconfig $KUBECONFIG --namespace $NAMESPACE delete secret k8s-registry-secret
    fi
    kubectl --kubeconfig $KUBECONFIG create secret generic k8s-registry-secret --from-file=.dockerconfigjson=$DOCKERCONFIG --type=kubernetes.io/dockerconfigjson -n $NAMESPACE

    if kubectl --kubeconfig $KUBECONFIG --namespace eric-crd-ns get secret k8s-registry-secret; then
        echo "Secret exists in namespace eric-crd-ns"
        kubectl --kubeconfig $KUBECONFIG --namespace eric-crd-ns delete secret k8s-registry-secret
    fi
    kubectl --kubeconfig $KUBECONFIG create secret generic k8s-registry-secret --from-file=.dockerconfigjson=$DOCKERCONFIG --type=kubernetes.io/dockerconfigjson -n eric-crd-ns
}

add_registry_secret