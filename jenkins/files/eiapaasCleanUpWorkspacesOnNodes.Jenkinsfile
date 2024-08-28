#!/usr/bin/env groovy
@Library('aas-muon-utils-lib') _

/******************************************************************************
                            Local Groovy Methods
******************************************************************************/
// Return a map of functions to execute.
def mapOfFunctions() {
    return [
        "Set-Temporarily-Offline"   : this.utilsNode.&setNodeTemporarilyOffline,
        "Delete-Workspaces"         : this.utilsNode.&deleteNodeWorkspaces,
        "Enable"                    : this.utilsNode.&setNodeOnline
    ]
}

// Create dictionary of either 1 or many nodes with corresponding stage and functions to execute.
def parallelStagesMap(Closure closureRef, Map functsToExecute, List onlineNodes) {
    onlineNodes.collectEntries { onlineNode ->
        ["${onlineNode}" : closureRef(onlineNode, functsToExecute)]
    }
}

// Method to dynamically generate one stage per function.
def generateStages(nodeName, functsToExecute) {
    return {
        functsToExecute.eachWithIndex { action, functToExecute, index ->
            stage("${action} ${nodeName} node") {
                functToExecute(nodeName)
            }
        }
    }
}

pipeline {
    agent {
        label 'master'
    }
    options {
        timestamps()
        disableResume()
        skipDefaultCheckout()
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder logRotator(artifactDaysToKeepStr: '5', artifactNumToKeepStr: '50', daysToKeepStr: '5', numToKeepStr: '50')
    }
    parameters {
        string(
            name:           'NODE_LABEL',
            defaultValue:   'AAS',
            description:    'Type in label associated with the node. Default is "AAS". If you wish to execute on a single node, type in the actual name of the node.'
        )
        string(
            name:           'GERRIT_REFSPEC',
            defaultValue:   'refs/heads/master',
            description:    'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )
    }
    stages {
        stage('Check Online Status') {
            steps {
                script {
                    onlineNodes = utilsNode.getOnlineNodes(params.NODE_LABEL)
                }
            }
        }
        stage('Execute Workspace Cleanups') {
            when {
                expression {
                    !onlineNodes.isEmpty()
                }
            }
            steps {
                script {
                    parallel parallelStagesMap(this.&generateStages, mapOfFunctions().subMap(['Set-Temporarily-Offline', 'Delete-Workspaces']), onlineNodes)
                }
            }
            post {
                always {
                    script {
                        parallel parallelStagesMap(this.&generateStages, mapOfFunctions().subMap(['Enable']), onlineNodes)
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}