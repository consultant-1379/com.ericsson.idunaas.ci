#!/bin/bash

# This script is used in a jenkins job as part of the spinnaker pipelines to pause/resume grafana alerts.
# Takes in 2 optional parameters, the deployment name and the action.
# From this we determine the alert to pause/resume for a speciific deployment on grafana.
# In absence of any parameters, the default execution is to pause all alerts for all deployments on grafana.
# Grafana url is hardcoded at the moment in the script.
# Grafana credentials are been read from the jenkins credential store.

usage () {
    echo "Usage:
        export GRAFANA_CREDS_USR=<grafana user> GRAFANA_CREDS_PSW=<grafana password>
        $(basename $0) [-h] [deployment_name action]
          Examples:
                $(basename $0) -h                   | Prints this message.
                $(basename $0) bnewidun01 pause     | Pause grafana alert for bnewidun01 environment.
                $(basename $0) bnewidun01 resume    | Resume grafana alert for bnewidun01 environment.
                $(basename $0) all pause            | Pause grafana alerts for all environments.
                $(basename $0) all resume           | Resume grafana alerts for all environment.
                $(basename $0)                      | In absence of any parameters, the default mode is to pause all alerts for all environments."
    exit -1
}

# Check that Grafana is alive and well.
getGrafanaStatusCode() {
    code=0
    responseCode=$(curl -sS -w "%{http_code}" -o grafana.log -u $GRAFANA_CREDS_USR:$GRAFANA_CREDS_PSW http://$GRAFANA_URL/org) || code="$?"
    if ! ( [ "$responseCode" -eq 200 ] && [ "$code" -eq 0 ] ); then
        echo "Cannot get a valid status response from grafana. Exiting script."
        exit -1
    fi
}

# Pause all alerts for all environments using the admin rest api.
pause_or_resume_all_alerts() {
    code=0
    responseCode=$(set -x; curl -sS -X POST http://$GRAFANA_URL/api/admin/pause-all-alerts -H 'Accept: application/json' \
        -H 'Content-Type: application/json' -d "{\"paused\":${ACTION}}" -o "all_alerts.json" -w "%{http_code}" \
        -u $GRAFANA_CREDS_USR:$GRAFANA_CREDS_PSW) || code="$?"

    if ! ( [ "$responseCode" -eq 200 ] && [ "$code" -eq 0 ] ); then
        echo "Problem with pausing/resuming alerts for all environments. Exiting script."
        exit -1
    fi
}

# Pause a specific alert for a specific environment using the standard rest api.
# First we have to query grafana for an alert that has the substring $DEPLOYMENT as part of it's name.
# Then in the response json, we can extract the alert id and use this in a rest api call to pause/resume the alert.
pause_or_resume_alert() {
    code=0
    responseCode=$(set -x; curl -sS -X GET http://$GRAFANA_URL/api/alerts?query=$DEPLOYMENT -H 'Accept: application/json' \
        -H 'Content-Type: application/json' -o "alert.json" -w "%{http_code}" \
        -u $GRAFANA_CREDS_USR:$GRAFANA_CREDS_PSW) || code="$?"

    if ! ( [ "$responseCode" -eq 200 ] && [ "$code" -eq 0 ] ); then
        echo "Problem with retrieving the alert id for $DEPLOYMENT environment . Exiting script."
        exit -1
    fi

    alertIds="$(cat alert.json | jq '.[] | .id')"
    for alertId in $alertIds; do
        ALERT_NAME="$(cat alert.json | jq '.[] | select(.id=='${alertId}') | .name')"
        echo "==> PAUSE_ALARM=${ACTION}    ALERT_ID=${alertId}    ALERT_NAME=${ALERT_NAME}"
        responseCode=$(set -x; curl -sS -X POST http://$GRAFANA_URL/api/alerts/$alertId/pause -H 'Accept: application/json' \
            -H 'Content-Type: application/json' -d "{\"paused\":${ACTION}}" -o "pause_or_resume_alert.json" \
            -w "%{http_code}" -u $GRAFANA_CREDS_USR:$GRAFANA_CREDS_PSW) || code="$?"

        if ! ( [ "$responseCode" -eq 200 ] && [ "$code" -eq 0 ] ); then
            echo "Problem with updating the alert status for $DEPLOYMENT environment. Exiting script."
            CURL_ERROR=( ${CURL_ERROR[@]} $(echo "${alertId} - ${ALERT_NAME}" | base64 -w 0) )
        fi
    done

    NUM_OF_ERROR=${#CURL_ERROR[@]}
    if [ $NUM_OF_ERROR -ne 0 ]; then
        echo "ERROR: failed to $ACTION the following alert:"
        for error_b64 in ${CURL_ERROR[@]}; do
            echo $error_b64 | base64-d
        done
        exit -1
    fi
}

### Entry of script ###
GRAFANA_URL=150.132.8.132:3000

test "$GRAFANA_CREDS_USR" == "" -o "$GRAFANA_CREDS_PSW" == "" \
    && echo "Error: missing environment variable: GRAFANA_CREDS_USR or GRAFANA_CREDS_PSW is empty." \
    && usage \
    && exit -2

# If no paramaters specified then run in default mode which is to pause all alerts for all environments.
if [ $# -lt 1 ]; then
    DEPLOYMENT="all"
    ACTION=true
fi

# If parameters detected then check they are valid for deployemnt name and action.
while test -n "$1"; do
    case "$1" in
        pause|resume)
            [ "$1" == "pause" ] && ACTION=true || ACTION=false
            shift;;
        all)
            DEPLOYMENT=all
            shift;;
        *)
            ls -l deployments/ | grep "$1" > /dev/null && DEPLOYMENT=$1 || usage;
            shift;;
    esac
done

getGrafanaStatusCode

if [ "$DEPLOYMENT" == "all" ]; then
    pause_or_resume_all_alerts
else
    pause_or_resume_alert
fi