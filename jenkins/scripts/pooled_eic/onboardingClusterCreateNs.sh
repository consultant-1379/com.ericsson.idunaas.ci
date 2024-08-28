#!/bin/bash

KUBECONFIG=$1
CLUSTERID=$2

for ((i=0; i<=5; i++))
do
    NS="$CLUSTERID-eric-eic-$i"
    kubectl --kubeconfig $KUBECONFIG create namespace $NS
    kubectl --kubeconfig $KUBECONFIG annotate --overwrite namespace $NS booked=false
    kubectl --kubeconfig $KUBECONFIG annotate --overwrite namespace $NS reserved=false
done