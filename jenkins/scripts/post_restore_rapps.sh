#!/bin/bash

### CONSTANTS ###

SCRIPT_FULL_PATH=$(realpath $0)
SCRIPT_DIR=$(dirname $SCRIPT_FULL_PATH)
SCRIPT_NAME=$(basename $SCRIPT_FULL_PATH)
CURL='curl -s --location -k'


### FUNCTIONS ###

# privates

log_fn(){
    local severity=$1
    local message=$2
    echo "[$(date)][${SCRIPT_NAME}][${severity}]: ${message}"
}

log(){
    log_fn INFO "$1"
}

log_error(){
    local message="$1"
    log_fn ERROR "$message" >&2
    exit -1
}

list_app_instances_in_json(){
    local app_json=""
    app_json=$($CURL --request GET \
        "${APP_MGR_URL}/app-manager/lcm/app-lcm/v1/app-instances" \
        --header "Cookie: JSESSIONID=${JSESSIONID}" \
        )
    [ $? -eq 0 ] || log_error "Exit code of curl not zero"

    echo $app_json | grep -q -v -F "Access Denied" || \
        log_error "Failed to list apps: '${app_json}'"

    app_json=$(echo $app_json | jq -r -c '.appInstances')
    [ $? -eq 0 ] || log_error "extraction failed: $app_json"
    if [ "$app_json" != "null" ]; then
        echo $app_json
    fi
}

list_app_instances(){
    list_app_instances_in_json | jq -r -c '.[]'
    [ $? -eq 0 ] || log_error "jq extraction failed: cannot list app instances"
}

get_app_instance(){
    local instance_id=$1
    list_app_instances | jq -r -c 'select(.id=='${instance_id}')'
    [ $? -eq 0 ] || log_error "jq extraction failed: id=$instance_id"
}

# general

get_login_token_from_appmgr(){
    local user="$1"
    local password="$2"
    local token=$( \
        $CURL --request POST \
        --header "X-Login: $user" \
        --header "X-Password: $password" \
        "${APP_MGR_URL}/auth/v1/" \
        )
    CURL_RC=$?
    echo $token | grep -q -F UNAUTHORIZED; RC=$?
    if [ $CURL_RC -ne 0 -o $RC -eq 0 ]; then
        log_error "Login failed: token='${token}'"
    fi
    echo $token
}

list_instantiated_apps_in_json(){
    list_app_instances_in_json | jq -r -c \
        'map(select(.healthStatus=="INSTANTIATED") | {"appOnBoardingAppId": .appOnBoardingAppId, "id": .id})'
    [ "${PIPESTATUS[0]} ${PIPESTATUS[1]}" == "0 0" ] || log_error "jq extraction failed"
}

cancel_instance(){
    local instance_id=$1
    $CURL --request PUT \
        --header "Cookie: JSESSIONID=${JSESSIONID}" \
        "${APP_MGR_URL}/app-manager/lcm/app-lcm/v1/app-instances/${instance_id}"
    [ $? -eq 0 ] || log_error "curl call failed"
}

wait_until_instance_health_status_is_TERMINATED_or_FAILED(){
    local instance_id=$1
    local max_attempt=6
    local sleep_time=10
    local is_app_in_desired_state="false"
    local target_status=$(get_app_instance $instance_id | jq -r -c '.targetStatus')
    if [ "$target_status" != "TERMINATED" ]; then
        log "App (id=${instance_id}) is not in targetStatus TERMINATED ($target_status detected). Sleep $sleep_time sec"
        sleep $sleep_time
        target_status=$(get_app_instance $instance_id | jq -r -c '.targetStatus')
        if [ "$target_status" != "TERMINATED" ]; then
            get_app_instance $instance_id >&2
            log_error "targetStatus of app (id=${instance_id}) is $target_status but it is supposed to be TERMINATED"
        fi
    fi
    for i in $(seq 1 $max_attempt); do
        log "Waiting loop: attempt $i of $max_attempt"
        health_status=$(get_app_instance $instance_id | jq -r -c '.healthStatus')
        if [ "${health_status}" == "TERMINATED" -o "${health_status}" == "FAILED" ]; then
            log "App (id=${instance_id}) is in the desired state"
            is_app_in_desired_state="true"
            break
        fi
        sleep $sleep_time
    done
    if [ "${is_app_in_desired_state}" != "true" ]; then
        get_app_instance $instance_id >&2
        log_error "healthStatus of app $instance_id is $health_status but it is supposed to be TERMINATED or FAILED"
    fi
}

delete_instances_of_onboarded_apps(){
    local onboardedapp_id=$1
    local app_list=$2
    $CURL --request DELETE \
        --header "Cookie: JSESSIONID=${JSESSIONID}"      \
        --header "Content-Type: application/json"        \
        --data-raw '{"appInstanceId" : ['${app_list}']}' \
        "${APP_MGR_URL}/app-manager/lcm/app-lcm/v1/apps/${onboardedapp_id}/app-instances"
    [ $? -eq 0 ] || log_error "Unexpected exit code"
}

wait_until_deletion_is_completed(){
    local instance_id=$1
    local max_attempt=6
    local sleep_time=10
    local is_app_in_desired_state="false"

    for i in $(seq 1 $max_attempt); do
        log "Waiting loop: attempt $i of $max_attempt"
        number_of_instances=$(get_app_instance $instance_id | jq -r -c '.id' | wc -l)
        if [ $number_of_instances -eq 0 ]; then
            is_app_in_desired_state="true"
            break
        fi
        sleep $sleep_time
    done
    if [ "${is_app_in_desired_state}" != "true" ]; then
        get_app_instance $instance_id >&2
        log_error "App $instance_id is not deleted"
    fi
}

keycloack_cleanup_steps(){
    local db_pod=""
    local db_user=""
    local client_id__client_scope__csv_b64=""

    # example: db_pod="pod/eric-appmgr-data-document-db-0"
    db_pod=$($KCTL get pod  -l app=eric-appmgr-data-document-db,role=master -o name)
    db_user=$($KCTL get secret eric-appmgr-data-document-db-credentials -o jsonpath='{.data.custom-user}' | base64 -d)
    client_id__client_scope__csv_b64=$( \
        $KCTL exec $db_pod -c eric-appmgr-data-document-db -- \
        psql -U $db_user -d app_lcm_db -c 'SELECT client_id,client_scope FROM credential_event;' --csv -t \
        | base64 -w 0; \
        [ "${PIPESTATUS[0]} ${PIPESTATUS[1]}" == "0 0" ] )
    [ $? -eq 0 ] || log_error "Unexpected exit code"

    if [ "$(echo $client_id__client_scope__csv_b64 | base64 -d | wc -l)" == "0" ]; then
        log "AppMgr database clean."
        exit 0
    fi

    $KCTL exec $db_pod -c eric-appmgr-data-document-db -- \
        psql -U $db_user -d app_lcm_db -c 'TRUNCATE TABLE credential_event;' --csv -t
    [ $? -eq 0 ] || log_error "Unexpected exit code"


    local iam_url=""
    local iam_user=""
    local iam_pswd=""
    local iam_token=""

    iam_url="https://$($KCTL get vs eric-cncs-oss-config-iam-virtualservice -o jsonpath='{.spec.hosts[0]}')"
    [ $? -eq 0 ] || log_error "Unexpected exit code"
    iam_user=$($KCTL get secret eric-sec-access-mgmt-creds -o jsonpath='{.data.kcadminid}' | base64 -d)
    [ $? -eq 0 ] || log_error "Unexpected exit code"
    iam_pswd=$($KCTL get secret eric-sec-access-mgmt-creds -o jsonpath='{.data.kcpasswd}'  | base64 -d)
    [ $? -eq 0 ] || log_error "Unexpected exit code"

    iam_token=$($CURL --request POST \
        --header 'Content-Type: application/x-www-form-urlencoded' \
        --data-urlencode 'grant_type=password'  \
        --data-urlencode "username=${iam_user}" \
        --data-urlencode "password=${iam_pswd}" \
        --data-urlencode 'client_id=admin-cli'  \
        "${iam_url}/auth/realms/master/protocol/openid-connect/token" \
        | jq -r -c .access_token; \
        [ "${PIPESTATUS[0]} ${PIPESTATUS[1]}" == "0 0" ] )
    [ $? -eq 0 ] || log_error "Unexpected exit code"


    local row_csv=""
    local client_id=""
    local client_scope=""

    for row_csv in $(echo $client_id__client_scope__csv_b64 | base64 -d); do
        client_id=$(   echo $row_csv | cut -d , -f 1)
        client_scope=$(echo $row_csv | cut -d , -f 2)

        ids=$($CURL --request GET \
            --header "Authorization: Bearer ${iam_token}" \
            "${iam_url}/auth/admin/realms/master/clients?clientId=${client_id}" \
            |  jq -r -c '.[].id' | xargs; \
            [ "${PIPESTATUS[0]} ${PIPESTATUS[1]}" == "0 0" ] )
        [ $? -eq 0 ] || log_error "Unexpected exit code"

        for id in $ids; do
            $CURL --request DELETE \
                --header "Authorization: Bearer ${iam_token}" \
                "${iam_url}/auth/admin/realms/master/clients/${id}"
            [ $? -eq 0 ] || log_error "Unexpected exit code"
        done
    done
}


### MAIN ###

if [ -z "$4" ]; then
    echo "Usage: $0 <kubeconfig> <namespace> <appmgr_user> <appmgr_password>"
    exit -1
fi

for cmd in jq kubectl curl; do
    which --skip-alias --skip-functions $cmd &>/dev/null \
        || log_error "Command '${cmd}' not available"
done

KCTL="kubectl --kubeconfig $1 -n $2"
$KCTL get pods &>/dev/null || log_error "kubeconfig or namespace not correct"

APP_MGR_URL="https://$($KCTL get vs eric-oss-app-mgr-virtual-service -o jsonpath='{.spec.hosts[0]}')"
JSESSIONID=$(get_login_token_from_appmgr $3 $4)
[ $? -eq 0 ] || exit -2

# example of RAPPS_JSON: [{"appOnBoardingAppId":1,"id":1},{"appOnBoardingAppId":3,"id":2}]
RAPPS_JSON=$(list_instantiated_apps_in_json)
[ $? -eq 0 ] || exit -3

if [ "X${RAPPS_JSON}" == "X" ]; then
    log "Environment clean: no rApps need to be cleaned."
    exit 0
fi


RAPPS_LST=$(echo $RAPPS_JSON | jq -r -c '.[] | .id' | xargs)
[ $? -eq 0 ] || exit -4

for INSTANCE_ID in $RAPPS_LST; do
    cancel_instance $INSTANCE_ID
done

for INSTANCE_ID in $RAPPS_LST; do
    wait_until_instance_health_status_is_TERMINATED_or_FAILED $INSTANCE_ID
done

for ONB_ID in $(echo "$RAPPS_JSON" | jq -r -c '.[] | .appOnBoardingAppId' | sort -u); do
    APP_IDS=$(echo $RAPPS_JSON | jq -r -c 'map(select(.appOnBoardingAppId=='${ONB_ID}')) | .[].id' | xargs | tr ' ' ',')
    delete_instances_of_onboarded_apps $ONB_ID $APP_IDS
done

for INSTANCE_ID in $RAPPS_LST; do
    wait_until_deletion_is_completed $INSTANCE_ID
done

keycloack_cleanup_steps

log "Post Restore Cleanup for rApps completed"
