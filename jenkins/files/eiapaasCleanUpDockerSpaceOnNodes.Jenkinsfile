#!/usr/bin/env groovy
@Library('aas-muon-utils-lib') _

import jenkins.model.*;
import hudson.FilePath.*;

/******************************************************************************
                            Local Groovy Methods
******************************************************************************/
// Return a map of commands to execute.
def mapOfFunctions() {
    return [
        "Deleted-Stopped-Containers"    :   this.utilsDockerCommands.&deletedStoppedContainers,
        "Deleted-Dangling-Images"       :   this.utilsDockerCommands.&deletedDanglingImages,
        "Deleted-Unused-Images"         :   this.utilsDockerCommands.&deletedUnusedImages,
        "System-Df-Status"              :   this.utilsDockerCommands.&systemDfStatus,
    ]
}

// Create dictionary of either 1 or many nodes with corresponding stage and functions to execute.
def parallelStagesMap(Closure closureRef, Map functsToExecute, List onlineNodes) {
    onlineNodes.collectEntries { onlineNode ->
        ["${onlineNode}" : closureRef(onlineNode, functsToExecute)]
    }
}

/* Method to dynamically generate one stage per function.
   - generate the common docker clean stages.
   - use try catch block to catch exception and set currentBuild.result to FAILED. If exception here, pararllel branch for that node will fail and halt.
   - finally block to archive logs files and delete workspace.
*/
def generateStages(nodeName, functsToExecute) {
    return {
        node(nodeName) {
            try {
                functsToExecute.eachWithIndex { action, functToExecute, index ->
                    stage("${action} ${nodeName} node") {
                        try {
                            if (action.equalsIgnoreCase("Deleted-Unused-Images")) {
                                functToExecute(nodeName, params.DOCKER_PRUNE_FILTER_TIME)
                            }
                            else {
                                functToExecute(nodeName)
                            }
                        }
                        catch(Exception err) {
                            println("Exception occurred when executing " + action + " on " + nodeName + ":" + err.toString());
                            currentBuild.result = 'FAILED';
                        }
                    }
                }
            }
            finally {
                archiveArtifacts allowEmptyArchive: true, artifacts: '*.log', fingerprint: true
                cleanWs()
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
        string (
            name:           'DOCKER_PRUNE_FILTER_TIME',
            defaultValue:   '24h',
            description:    'This is the --filter attribute, to only remove before a certain time. For example, "--filter until=24h" is to remove images created more than 1 day (i.e 24 hours) ago'
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
        stage('Execute docker clean up') {
            when {
                expression {
                    !onlineNodes.isEmpty()
                }
            }
            steps {
                script {
                    parallel parallelStagesMap (
                        this.&generateStages,
                        mapOfFunctions().subMap(['Deleted-Stopped-Containers', 'Deleted-Dangling-Images', 'Deleted-Unused-Images', 'System-Df-Status']), onlineNodes
                    )
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
