#!/usr/bin/env groovy

/* groovylint-disable MethodParameterTypeRequired, MethodReturnTypeRequired, ParameterName, NoDef */
/* groovylint-disable DuplicateStringLiteral, LineLength, CompileStatic, VariableTypeRequired */

def deletedStoppedContainers(nodeName) {
    sh 'docker container prune -f >deletedDanglingImages-' + nodeName + '.log 2> /dev/null'
}

def deletedDanglingImages(nodeName) {
    sh 'docker images --quiet --filter=dangling=true 2> /dev/null | xargs --no-run-if-empty 2> /dev/null docker rmi >deletedStoppedContainers-' + nodeName + '.log 2> /dev/null'
}

def deletedUnusedImages(nodeName, docker_prune_filter_time = '24h') {
    sh 'docker image prune -a -f --filter until=' + docker_prune_filter_time + ' >deletedUnusedImages-' + nodeName + '.log 2> /dev/null'
}

def systemDfStatus(nodeName) {
    sh 'docker system df >systemDfStatus-' + nodeName + '.log 2> /dev/null'
}
