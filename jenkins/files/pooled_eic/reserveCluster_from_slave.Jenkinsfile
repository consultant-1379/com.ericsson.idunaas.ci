#!/usr/bin/env groovy
@Library('aas-muon-utils-lib') _
def bob = "bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0_pooled_from_slave.yaml"

pipeline {
    agent {
        label SLAVE_LABEL
    }
    parameters {
        string (
            name:           'JIRA_ID',
            defaultValue:   'DETS-1234',
            description:    'Jira id of this pooled deployment request'
        )
        string (
            name:           'APP_SET',
            defaultValue:   'full_eiap',
            description:    'The app-set that we trying to install to a cluster'
        )
        string (
            name:           'INT_CHART_VERSION',
            defaultValue:   '0.0.0',
            description:    'The version of the Helmfile sent in through a previous jenkins build\'s artifact.properties.'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            defaultValue:   'detsuser_docker_config',
            description:    'ARM Docker secret'
        )
        string (
            name:           'MINIO_USER_SECRET_ID',
            defaultValue:   'miniosecret',
            description:    'Minio user secret which is accessed via Jenkins credentials secret id'
        )
        string (
            name:           'PLATFORM_TYPE',
            defaultValue:   'pooled',
            description:    'Cloud provider type'
        )
        string (
            name:           'DEDICATED_NAMESPACE',
            defaultValue:   'N/A',
            description:    'Dedicated namespace used. If it is a dedicated namespace specify the NS if not, leave it as "N/A"'
        )
        string (
            name:           'EXCLUSIVE_II',
            defaultValue:   'false',
            description:    'Is the installation for an Exclusive cluster? If true it is an exclusive cluster II if False it is an normal II'
        )
        string(
            name:           'SLAVE_LABEL',
            defaultValue:   'EIAP_CICD',
            description:    'Specify the slave label that you want the job to run on (ususally IDUN_CICD_ONE_POD_H or EIAP_CICD)'
        )
        string(
            name:           'GIT_BRANCH_TO_USE',
            defaultValue:   'master',
            description:    'Put refs/heads/${GIT_BRANCH_TO_USE} in the job configuration for the git branch'
        )
    }
    options {
        timestamps()
        disableResume()
        timeout(time: 30, unit: 'MINUTES')
        durabilityHint 'PERFORMANCE_OPTIMIZED'
        disableConcurrentBuilds abortPrevious: true
    }
    environment {
        BUILD_INFO                  = "${env.BUILD_NUMBER}-${params.PLATFORM_TYPE}-${params.APP_SET}-${params.JIRA_ID}"
        DOCKER_FLAGS                = utils.getDockerFlags()
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
    }
    stages {
        stage('Set Build Description') {
            steps {
                script {
                    echo "==== Set Build Description ===="
                    currentBuild.displayName = "${env.BUILD_INFO}"
                }
            }
        }
        /*
        stage('Install docker config file to root location') {
            steps {
                echo "==== Install docker config File to root location ===="
                withCredentials ([
                    file (
                        credentialsId:  params.ARMDOCKER_USER_SECRET,
                        variable:       'DOCKERCONFIG'
                    )
                ]) {
                    sh "${bob} pooled-deployment:install-docker-config-to-root-location"
                }
            }
        }
        */
        stage('Retrieve all kube config files from MiniIO') {
            steps {

                echo "==== Retrieve all kube config files from MiniIO ===="
                withCredentials ([
                    usernameColonPassword (
                        credentialsId:  env.MINIO_USER_SECRET_ID,
                        variable:       'MINIO_CREDS'
                    )
                ]) {
                    script {
                        env.MINIO_FLAGS_NO_DOCKER_CONF  = utils.getMinioFlagsNoDockerConfig()
                        sh "${bob} pooled-deployment:retrieve-all-kubeconfig-files-from-minio"
                    }
                }
            }
        }
        stage('Select pooled deployment cluster from mongoDB') {
            steps {
                echo "==== Select Pooled Deployment Cluster from MongoDB ===="
                sh "${bob} pooled-deployment:get-cluster"
            }
        }
        stage('Archive artifact properties file' ) {
            steps {
                echo "==== Archive artifact properties file ===="
                archiveArtifacts artifacts: 'artifacts.properties', fingerprint: true, onlyIfSuccessful: true
            }
        }
        stage ('Cleaning workspace'){
            steps {
                cleanWs()
            }
        }
    }
}
