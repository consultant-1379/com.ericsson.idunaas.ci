#!/bin/bash

[ -z "$1" ] && { echo "Error: please give the path to the shared folder"; exit -1; }

SHARED_FOLDER=$1
BIN_FOLDER="${SHARED_FOLDER}/bin"
MC="${BIN_FOLDER}/miniocli"
YQ="${BIN_FOLDER}/yq"

mkdir -p "${BIN_FOLDER}" || { echo "Error: impossible to create folder tree '${BIN_FOLDER}'"; exit -2; }
#cd "${BIN_FOLDER}"       || { echo "Error: impossible to cd into folder '${BIN_FOLDER}'";     exit -3; }

[ ! -e "$MC" ] && { \
    curl -s -L -o "$MC"  https://dl.min.io/client/mc/release/linux-amd64/mc; \
    chmod 755 "$MC"; \
}
$MC --version || { echo "Error: impossible to install $MC"; exit -4; }

[ ! -e "$YQ" ] && { \
    curl -s -L -o "$YQ"  https://github.com/mikefarah/yq/releases/download/v4.40.3/yq_linux_amd64; \
    chmod 755 "$YQ"; \
}
$YQ --version || { echo "Error: impossible to install $YQ"; exit -5; }


# jq --version  || { echo "Error: jq not found"; exit -6; }