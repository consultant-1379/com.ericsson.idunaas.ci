#!/bin/bash

# This script is only used for Setup EKS Cluster pipelines to set AWS paths to generated kube_config

usage () {
    echo "Usage:
        $0 [-h] [path_to_kube_config]
          Examples:
                $0 -h                         | Prints this message.
                $0 path_to_kube_config        | Update Kube_config with hardcoded AWS path"
    exit 2
}

update_config(){
     echo "Updating ${kube_config_path}"
     yq -iy '.users[0].user.exec.env+=[{"name":"AWS_PROFILE","value": "default"},{"name": "AWS_CONFIG_FILE","value":"/workdir/aws/config"},{"name": "AWS_SHARED_CREDENTIALS_FILE","value":"/workdir/aws/credentials"}]'  ${kube_config_path}
     yq -iy '.users[0].user.exec.command="/usr/local/bin/aws"' ${kube_config_path}
}

# If no paramaters specified, then print message, call usage method and exit.
if [ $# -ne 1 ]; then
    echo 1>&2 "Invalid parameters provided."; usage;
    exit 2
fi


# Main
kube_config_path=$1

update_config