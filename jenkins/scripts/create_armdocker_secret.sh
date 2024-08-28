#!/bin/bash


while [ $# -gt 0 ]; do
    case "$1" in
        "--kubeconfig")
            shift
            KUBECONFIG="$1"
        ;;
        "--secret_name")
            shift
            SECRET_NAME="$1"
        ;;
        *)
            echo "[$(basename $0)] ERROR: Bad command line argument: '$1'"
            exit -1
        ;;
    esac
    shift
done

NS=$(kubectl get ns | awk '{print $1}' | sed -n '1!p')

for namespace in NS 
do
    if 


#kubectl get secret k8s-registry-secret

#kubectl --kubeconfig kube_config/config create secret generic k8s-registry-secret --from-file=.dockerconfigjson=~/.docker/config.json --type=kubernetes.io/dockerconfigjson -n <namespace>