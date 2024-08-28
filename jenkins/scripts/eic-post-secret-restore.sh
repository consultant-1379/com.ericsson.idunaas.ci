#!/bin/bash

#self init
ECHO="/bin/echo"
KUBECTL="/usr/local/bin/kubectl"
pname=`basename $0`
adir=$(readlink -f $(dirname "$0"))
${ECHO} -e "-running $pname from $adir"
POSITIVE_INTEGER_REGEX="^[1-9]{1}[0-9]*$"

function helpm {
  ${ECHO} -e "help: \n-c kms-replica-count \n-k </path/to/kubectl.config> \n-n <namespace>"
}

# timeout?
while getopts '?:n:k:c:' ess && [[ $# -gt 0 ]] ; do
  case ${ess} in
        n)
                nsp=${OPTARG}
                ;;
        k)
                kubeconfig=${OPTARG}
                ;;
        c)
                count=${OPTARG}
                ;;
        ?)      helpm; exit 1
                ;;
  esac
done

function error {
  helpm
  ${ECHO} -e "Error $err"
  exit 1
}

if [[ -z "$nsp" ]] ; then
   err="namespace"
   error
fi

#Run KMS post restore step
function post_restore_kms() {
    KMS_REPLICA_COUNT="${count}"
    ${ECHO} "${count}"
    ${KUBECTL} get statefulset --kubeconfig "$kubeconfig" --namespace "$nsp" eric-sec-key-management-main
    if [ $? -eq 1 ] || [[ ! "$KMS_REPLICA_COUNT" =~ $POSITIVE_INTEGER_REGEX ]]; then
        ${ECHO} "no eric-sec-key-management-main deployment found, KMS_REPLICA_COUNT=$(${ECHO} "$KMS_REPLICA_COUNT")"
    else
      #Scale kms back up
      ${KUBECTL} scale statefulset eric-sec-key-management-main --replicas="$KMS_REPLICA_COUNT" --kubeconfig "$kubeconfig" --namespace "$nsp"
      ready_pods=0
      until [ $ready_pods -eq "$KMS_REPLICA_COUNT" ]
      do
        ${ECHO} "waiting until all eric-sec-key-management-main pods are in running state"
        if [ -n "$(${KUBECTL} get statefulset --kubeconfig "$kubeconfig" --namespace "$nsp" eric-sec-key-management-main -o jsonpath="{.status.readyReplicas}")" ]
        then
          ready_pods=$(${KUBECTL} get statefulset --kubeconfig "$kubeconfig" --namespace "$nsp" eric-sec-key-management-main -o jsonpath="{.status.readyReplicas}")
        fi
        sleep 5s
      done
      ${ECHO} "all eric-sec-key-management-main pods are in running state"
    fi

    ${ECHO} "all KMS post restore steps are completed"
}

#Run PMSCH post restore step
function post_restore_pmsch() {
  pmsch_pods=( $(${KUBECTL} get pods --kubeconfig "$kubeconfig" --namespace "$nsp" -o name | grep -E 'eric-oss-pm-stats-(calculator|exporter|query-service)') )
  if [ $? -eq 1 ] || [[ ${#pmsch_pods[@]} -eq 0 ]]; then
      ${ECHO} "no eric-oss-pm-stats-calc-handling pods found"
  else
    #Restart eric-oss-pm-stats-calculator, eric-oss-pm-stats-exporter, eric-oss-pm-stats-query-service pods
    for pod in "${pmsch_pods[@]}"
    do
      ${ECHO} "deleting pod $pod"
      ${KUBECTL} delete --kubeconfig "$kubeconfig" --namespace "$nsp" $pod
    done
    #Check deployment status
    timeout=300s
    ${KUBECTL} rollout status deployment --kubeconfig "$kubeconfig" --namespace "$nsp" eric-oss-pm-stats-calculator --timeout $timeout || ${ECHO} "rollout of eric-oss-pm-stats-calculator deloyment reached timeout $timeout"
    ${KUBECTL} rollout status deployment --kubeconfig "$kubeconfig" --namespace "$nsp" eric-oss-pm-stats-exporter --timeout $timeout || ${ECHO} "rollout of eric-oss-pm-stats-exporter deloyment reached timeout $timeout"
    ${KUBECTL} rollout status deployment --kubeconfig "$kubeconfig" --namespace "$nsp" eric-oss-pm-stats-query-service --timeout $timeout || ${ECHO} "rollout of eric-oss-pm-stats-query-service deloyment reached timeout $timeout"

    ${ECHO} "all eric-oss-pm-stats-calc-handling pods are in running state"
  fi

  ${ECHO} "all PMSCH post restore steps are completed"
}

function post_restore_pm_kpi_bragent() {
    KPI_BRAGENT_REPLICA_COUNT=$( ${KUBECTL} get deployment --kubeconfig "$kubeconfig" --namespace "$nsp" eric-pm-kpi-data-bragent -o jsonpath="{.spec.replicas}" )
    if [ $? -eq 1 ] || [[ ! "$KPI_BRAGENT_REPLICA_COUNT" =~ $POSITIVE_INTEGER_REGEX ]]; then
        ${ECHO} "no eric-pm-kpi-data-bragent deployment found, KPI_BRAGENT_REPLICA_COUNT=$(${ECHO} "$KPI_BRAGENT_REPLICA_COUNT")"
    else
      ${ECHO} "$KPI_BRAGENT_REPLICA_COUNT"
      ${KUBECTL} rollout restart deployment --kubeconfig "$kubeconfig" --namespace "$nsp" eric-pm-kpi-data-bragent
      ${KUBECTL} rollout restart statefulset --kubeconfig "$kubeconfig" --namespace "$nsp" eric-pm-kpi-data
      ready_pods=0
      until [[ $ready_pods -eq "$KPI_BRAGENT_REPLICA_COUNT" ]]
      do
        ${ECHO} "waiting until eric-pm-kpi-data-bragent pod is in running state"
        if [ -n "$(${KUBECTL} get deployment --kubeconfig "$kubeconfig" --namespace "$nsp" eric-pm-kpi-data-bragent -o jsonpath="{.status.readyReplicas}")" ]
        then
          ready_pods=$(${KUBECTL} get deployment --kubeconfig "$kubeconfig" --namespace "$nsp" eric-pm-kpi-data-bragent -o jsonpath="{.status.readyReplicas}")
        fi
        sleep 5s
      done
      ${ECHO} "kpi-data-bragent pod is in running state"
      timeout=200s
      ${KUBECTL} rollout status statefulset --kubeconfig "$kubeconfig" --namespace "$nsp" eric-pm-kpi-data --timeout $timeout || ${ECHO} "rollout of eric-pm-kpi-data sts reached timeout $timeout"
      ${ECHO} "eric-pm-kpi-data pod is in running state"

    fi
    ${ECHO} "kpi-data-bragent pod restarted"
    ${ECHO} "eric-pm-kpi-data pod restarted"

}

post_restore_kms
post_restore_pmsch
post_restore_pm_kpi_bragent