#!/bin/bash

test -z "$1" && \
    echo "Error: please provide the environment name" && \
    exit -1

ENV_NAME=$1
RHEL_VERSION=${2:-8}
TMP_FILE=$(mktemp)
ARTIFACTS_FILE=artifact.properties
AWSREGION=$(aws configure get region)
AWS="aws --region $AWSREGION --no-cli-pager"


echo "=== Getting the AMI of Backup Server ==="

AMI=$( \
    $AWS ec2 describe-instances \
    | jq -r '.Reservations[].Instances |
             map({amiid: .ImageId,tags: .Tags}) |
             map(select(.tags != null)) |
             map({amiid: .amiid,tags: .tags |
             map(select(.Key == "Name" and .Value == "Backup Server"))}) |
             map(select(.tags | length > 0)) |
             .[].amiid')

echo "CURRENT_BACKUP_AMI_ID=${AMI}" >> $ARTIFACTS_FILE


echo "=== Getting latest AMI for Ericsson Red Hat Enterprise Linux ${RHEL_VERSION} ==="

$AWS ec2 describe-images \
    --owners 430170170793 \
    | jq -r '.Images |
             map({ "name": .Name, "amiid": .ImageId }) |
             map(select(.name | length > 0)) |
             map(select(.name | startswith("Ericsson RHEL '${RHEL_VERSION}'"))) |
             . |=sort_by(.name) | reverse | .[0]' \
    > ${TMP_FILE}

cat $TMP_FILE >&2

AMI=$(cat $TMP_FILE | jq -r .amiid)
echo "LATEST_RHEL_AMI_ID=${AMI}" >> $ARTIFACTS_FILE
rm $TMP_FILE


echo "=== Getting the name of the second EKS cluster (if any) ==="

CLUSTER_LIST=$( \
    $AWS eks list-clusters \
    | jq -r '.clusters[]' \
    | xargs)

for CL in $CLUSTER_LIST; do
    grep -l $CL ${CI_REPO_FOLDER}deployments/*/workdir/kube_config/config \
    | sed -e "s@${CI_REPO_FOLDER}deployments/@@" -e 's@/workdir/kube_config/config@@'
done > $TMP_FILE

N=$(cat $TMP_FILE | wc -l)
test $N -gt 2 && \
    echo "Error: more than 2 EKS clusters in the same environment" && \
    rm $TMP_FILE && \
    exit -2

test $N -eq 2 && \
    OTHER_ENV=$(cat $TMP_FILE | grep -v $ENV_NAME)

echo "OTHER_ENV=${OTHER_ENV}" >> $ARTIFACTS_FILE
rm $TMP_FILE

