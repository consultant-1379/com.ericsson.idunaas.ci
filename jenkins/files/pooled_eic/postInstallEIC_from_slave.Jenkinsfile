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
            description:    'Jira Id associated with this pooled deployment request'
        )
        string (
            name:           'SELECTED_CLUSTER_ID',
            defaultValue:   'hall133',
            description:    'CLuster name used to download correct kubeconfig from Minio for the environment to purge.'
        )
        string (
            name:           'DEPLOYMENT_TYPE',
            defaultValue:   'install',
            description:    'Deployment Type, set \"install\" or \"upgrade\"'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'eric-eiap',
            description:    'Namespace to install the Chart'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            defaultValue:   'detsuser_docker_config',
            description:    'ARM Docker secret'
        )
        string (
            name:           'INT_CHART_VERSION',
            defaultValue:   '2.2.0-82',
            description:    'The version of base platform to install'
        )
        string (
            name:           'MINIO_USER_SECRET_ID',
            defaultValue:   'miniosecret',
            description:    'Minio user secret which is accessed via Jenkins credentials secret id'
        )
        string (
            name:           'RESERVED_NAMESPACE_BOOKING',
            defaultValue:   'FALSE',
            description:    'Set to TRUE if it is a reserved namespace'
        )
        string (
            name:           'PLATFORM_TYPE',
            defaultValue:   'pooled',
            description:    'Cloud provider type'
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
        timeout(time: 30, unit: 'MINUTES')
        durabilityHint 'PERFORMANCE_OPTIMIZED'
    }
    environment {
        BUILD_INFO                  = "${env.BUILD_NUMBER}-${params.NAMESPACE}-${params.SELECTED_CLUSTER_ID}-${params.DEPLOYMENT_TYPE}-${params.JIRA_ID}"
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
        stage('Set Cluster name to bob variable') {
            steps {
                echo "==== Set Cluster name to bob variable ===="
                sh "${bob} pooled-deployment:set-selected-cluster-id"
            }
        }
        stage('Retrieve kube config file from MiniIO') {
            steps {
                echo "==== Retrieve kube config file from MiniIO ===="
                withCredentials ([
                    usernameColonPassword (
                        credentialsId:  env.MINIO_USER_SECRET_ID,
                        variable:       'MINIO_CREDS'
                    )
                ]) {
                    script {
                        env.MINIO_FLAGS_NO_DOCKER_CONF  = utils.getMinioFlagsNoDockerConfig()
                        sh "${bob} pooled-deployment:retrieve-kubeconfig-from-minio"
                    }
                }
            }
        }
        stage('Install kube config file to default and admin locations') {
            steps {
                echo "==== Install kube config file to default and admin locations ===="
                sh "${bob} pooled-deployment:install-kubeconfig-admin-location"
                sh "${bob} pooled-deployment:install-kubeconfig-default-location"
            }
        }
        stage ('Enable Federation to dets monitoring') {
	        steps {
                echo "==== Enable Federation to dets monitoring ===="
                sh "${bob} pooled-deployment:enable-federation"
	        }
        }
        stage ('Annotate namespace with eic version') {
            when {
                environment ignoreCase: true, name: 'RESERVED_NAMESPACE_BOOKING', value: 'false'
            }
            steps {
                echo "==== Annotate namespace with version ===="
                sh "${bob} pooled-deployment:annotate-namespace-with-version"
            }
        }
        stage ('Annotate namespace with booked true') {
	        steps {
                echo "==== Annotate namespace with version and booked true ===="
                sh "${bob} pooled-deployment:annotate-namespace-with-booked-true"
	        }
        }
        stage ('Annotate namespace with version and reserved true') {
            when {
                environment ignoreCase: true, name: 'RESERVED_NAMESPACE_BOOKING', value: 'true'
            }
            steps {
                echo "==== Annotate namespace with reserved true ===="
                sh "${bob} pooled-deployment:annotate-namespace-with-reserved-true"
            }
        }
        stage('Sleep before querying from prometheus'){
            steps {
                echo "==== Sleep before querying from prometheus ===="
                sleep(time: 3, unit: 'MINUTES')
            }
        }
        stage ('Update cluster resource usage in mongo'){
	        steps {
                echo "==== Update cluster resource usage in mongo ===="
                sh "${bob} pooled-deployment:update-cluster-resource-usage"
	        }
        }
        stage ('Unlock Cluster') {
	        steps {
                echo "==== Unlock Cluster ===="
                sh "${bob} pooled-deployment:release-lock-on-cluster"
	        }
        }
        stage ('Cleaning workspace'){
            steps {
                cleanWs()
            }
        }
    }
}
