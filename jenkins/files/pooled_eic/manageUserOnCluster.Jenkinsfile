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
            name:           'ADD_TEAMS_USERS_AS_ADMINS_TO_NAMESPACE',
            defaultValue:   'NO',
            description:    'Add team users as admins to specific namespace. Choice either "YES" or "No".'
        )
        string (
            name:           'REMOVE_TEAMS_USERS_AS_ADMINS_TO_NAMESPACE',
            defaultValue:   'NO',
            description:    'Remove team users as admins to namespace. Choice either "YES" or "No".'
        )
        string (
            name:           'ADD_TEAMS_USERS_AS_ADMINS_TO_CLUSTER',
            defaultValue:   'NO',
            description:    'Add team users as admins to cluster. Choice either "YES" or "No".'
        )
        string (
            name:           'REMOVE_TEAMS_USERS_AS_ADMINS_TO_CLUSTER',
            defaultValue:   'NO',
            description:    'Remove team users as admins to cluster. Choice either "YES" or "No".'
        )
        string (
            name:           'USERS',
            defaultValue:   'egajada,qradpol',
            description:    'Comma separated list of team users'
        )
        string (
            name:           'SELECTED_CLUSTER_ID',
            defaultValue:   'hall133',
            description:    'CLuster name used to download correct kubeconfig from Minio for the environment to purge.'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'eric-eiap',
            description:    'Namespace to limit user acces'
        )
        string (
            name:           'CRD_NAMESPACE',
            defaultValue:   'eric-crd-ns',
            description:    'CRD Namespace used by users'
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
        stage('Add and annotate team users as admins to namespace') {
            when {
                environment ignoreCase: true, name: 'ADD_TEAMS_USERS_AS_ADMINS_TO_NAMESPACE', value: 'YES'
            }
            steps {
                echo "==== Add and annotate team users as admins to namespace ===="
                sh "${bob} pooled-deployment:add-annotate-users-as-admins-to-namespace"
            }
        }
        stage('Remove and annotate team users as admins to namespace') {
            when {
                environment ignoreCase: true, name: 'REMOVE_TEAMS_USERS_AS_ADMINS_TO_NAMESPACE', value: 'YES'
            }
            steps {
                echo "==== Remove and annotate team users as admins to namespace ===="
                sh "${bob} pooled-deployment:remove-annotate-users-as-admins-to-namespace"
            }
        }
        stage('Add and annotate team users as admins to cluster') {
            when {
                environment ignoreCase: true, name: 'ADD_TEAMS_USERS_AS_ADMINS_TO_CLUSTER', value: 'YES'
            }
            steps {
                echo "==== Add and annotate team users as admins to cluster ===="
                sh "${bob} pooled-deployment:add-annotate-users-as-admins-to-cluster"
            }
        }
        stage('Remove and annotate team users as admins to cluster') {
            when {
                environment ignoreCase: true, name: 'REMOVE_TEAMS_USERS_AS_ADMINS_TO_CLUSTER', value: 'REMOVE_TEAMS_USERS_AS_ADMINS_TO_CLUSTER'
            }
            steps {
                echo "==== Remove and annotate team users as admins to cluster ===="
                sh "${bob} pooled-deployment:remove-annotate-users-as-admins-to-cluster"
            }
        }
    }
}