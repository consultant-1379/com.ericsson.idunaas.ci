#!/usr/bin/env groovy
@Library('aas-muon-utils-lib') _
def bob = "bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0_pooled.yaml"

pipeline {
    agent {
        kubernetes {
            yamlFile 'jenkins/scripts/pooled_eic/templates/jnlpCiUtilsPod.yaml'
            defaultContainer 'outer-ci-utils-container'
        }
    }
    parameters {
        string (
            name:           'JIRA_ID',
            defaultValue:   'DETS-1234',
            description:    'Jira id of this pooled deployment request'
        )        
        string (
            name:           'NAMESPACE',
            defaultValue:   'eric-eiap',
            description:    'Namespace to limit user acces'
        )
        string (
            name:           'SELECTED_CLUSTER_ID',
            defaultValue:   'hall133',
            description:    'CLuster name used to download correct kubeconfig from Minio for the environment to purge.'
        )
        string (
            name:           'INT_CHART_VERSION',
            defaultValue:   '0.0.0',
            description:    'Installed helmfile version'
        )
        string (
            name:           'BOOKING_END_DATE',
            defaultValue:   'default',
            description:    'This param is used only for booking extension pipeline. For the rest leave it as default.'
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
            name:           'GERRIT_REFSPEC',
            defaultValue:   'refs/heads/master',
            description:    'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )
        string (
            name:           'BOOKING_EXTENSION',
            defaultValue:   'FALSE',
            description:    'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
        )
    }
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        durabilityHint 'PERFORMANCE_OPTIMIZED'
    }
    environment {
        BUILD_INFO                  = "${env.BUILD_NUMBER}-${params.SELECTED_CLUSTER_ID}-${params.NAMESPACE}-${params.JIRA_ID}"
        DOCKER_FLAGS                = utils.getDockerFlags()
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        BOOKING_END_DATE            = utils.convertDate(params.BOOKING_END_DATE)
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
        stage('Check K8S Connectivity') {
            steps {
                echo "==== Check K8S Connectivity ===="
                sh "${bob} do-health-check:check-eks-connectivity"
            }
        }
        stage('Annotate team users to namespace') {
            steps {
                echo "==== Annotate team users to namespace ===="
                sh "${bob} pooled-deployment:annotate-users-in-namespace"
            }
        }
        stage('Update booking with EIC version') {
            steps {
                echo "==== Update booking with EIC version ===="
                sh "${bob} pooled-deployment:update-booking-helmfile-version"
            }
        }
        stage('Update booking with extended End Date') {
            when {
                environment ignoreCase: true, name: 'BOOKING_EXTENSION', value: 'true'
            }
            steps {
                echo "==== Update booking with EIC version and annotate namespace ===="
                sh "${bob} pooled-deployment:update-booking-end-date"
            }
        } 
        stage('Annotate namespace with booking details') {
            steps {
                echo "==== Annotate namespace with booking details ===="
                sh "${bob} pooled-deployment:annotate-namespace-booking-details"
            }
        }
    }
}