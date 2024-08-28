#!/usr/bin/env groovy
/* groovylint-disable CompileStatic, DuplicateNumberLiteral, DuplicateStringLiteral, LineLength, MethodParameterTypeRequired, MethodReturnTypeRequired, NoDef, VariableName, VariableTypeRequired */
import groovy.transform.Field

@Field final String DOCKER_HOST         = '--env DOCKER_HOST '
@Field final String DOCKER_SOCK         = '--volume /var/run/docker.sock:/var/run/docker.sock '
@Field final String DOCKER_CONFIG       = "--volume ${WORKSPACE}/dockerconfig.json:/.docker/config.json "

@Field final String ROOT_GROUP          = '--group-add 0 '
@Field final String NETWORK_HOST        = '--network host '
@Field final String ETC_HOSTS           = '--volume /etc/hosts:/etc/hosts '

@Field final String WORKDIR             = '--workdir /workdir '
@Field final String WORKSPACE_AWS       = "--volume ${WORKSPACE}/aws:/.aws "
@Field final String WORKSPACE_WORKDIR   = "--volume ${WORKSPACE}:/workdir "

@Field final String USR_LOCAL_BIN       = '--volume /usr/local/bin:/usr/local/bin '

@Field final String AWS_CONFIG          = '-e AWS_CONFIG_FILE=/workdir/aws/config -e AWS_SHARED_CREDENTIALS_FILE=/workdir/aws/credentials '
@Field final String USR_LOCAL_AWS_CLI   = '--volume /usr/local/aws-cli:/usr/local/aws-cli '

@Field final String PLATFORM_ID         = "${params.PLATFORM_TYPE}".toLowerCase()
@Field final String MINIO_URL           = '10.117.246.166:9000'

@Field final String COMMON_ATTRIBUTES   = DOCKER_SOCK + WORKSPACE_WORKDIR + ETC_HOSTS + WORKDIR

def getMinioFlagsNoDockerConfig() {
    if (PLATFORM_TYPE == "pooled") {
         String MINIO_CREDS = "${env.MINIO_CREDS}"
         String MINIO       = '-e MC_HOST_minio=http://' + MINIO_CREDS + '@' + MINIO_URL
         return COMMON_ATTRIBUTES + NETWORK_HOST + DOCKER_HOST + ROOT_GROUP + MINIO
    }
    return COMMON_ATTRIBUTES
}

def getDockerFlagsNoDockerConfig() {
    if (PLATFORM_ID == "aws") {
        return COMMON_ATTRIBUTES + AWS_CONFIG
    }
    if (PLATFORM_ID == "pooled") {
        return COMMON_ATTRIBUTES + NETWORK_HOST + DOCKER_HOST + ROOT_GROUP
    }
    return COMMON_ATTRIBUTES
}

def getDockerFlags() {
    if (PLATFORM_ID == "aws") {
        return COMMON_ATTRIBUTES + DOCKER_CONFIG + AWS_CONFIG
    }
    if (PLATFORM_ID == "pooled") {
        return DOCKER_SOCK + WORKSPACE_WORKDIR + WORKDIR + DOCKER_CONFIG + NETWORK_HOST + DOCKER_HOST + ROOT_GROUP
    }
    return COMMON_ATTRIBUTES + DOCKER_CONFIG
}

def getDeploymentManagerFlags() {
    if (PLATFORM_ID == "aws") {
        return COMMON_ATTRIBUTES + WORKSPACE_AWS + USR_LOCAL_BIN + USR_LOCAL_AWS_CLI + AWS_CONFIG
    }
    if (PLATFORM_ID == "pooled") {
        return COMMON_ATTRIBUTES + USR_LOCAL_BIN + NETWORK_HOST + DOCKER_HOST + ROOT_GROUP
    }
    return COMMON_ATTRIBUTES + USR_LOCAL_BIN
}

def convertDate(dateString) {
    // To take account of dateString in the format YYYY-MM-DD if some-one copies it directly from the datepicker in jira booking ticket
    def dateParts = dateString.split('-')
    if (dateParts[0].length() == 4) {
            def year = dateParts[0]
            def month = dateParts[1]
            def day = dateParts[2]
            return "${day}-${month}-${year}"
    }
    return dateString
}
