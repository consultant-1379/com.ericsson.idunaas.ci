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
            name:           'GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING',
            defaultValue:   'default',
            description:    'Please enter jira id (i.e. DETS-12345) to retrieve teams users associated with this booking.'
        )
        string (
            name:           'GET_BOOKINGS_DETAILS',
            defaultValue:   'default',
            description:    'Please enter jira id (i.e. DETS-12345) to retrieve all booking information.'
        )
        string (
            name:           'GET_EXPIRED_BOOKINGS',
            defaultValue:   'default',
            description:    'If yes, then we retrieve the list of expired bookings from mongoDB.'
        )
        string (
            name:           'GET_CLUSTER_LOCK_STATUS',
            defaultValue:   'default',
            description:    'This field expects the cluster name. Based on the cluster name, we retrieve the custer lock status.'
        )
        string (
            name:           'SET_CLUSTER_LOCK_STATUS_TO_TRUE',
            defaultValue:   'default',
            description:    'This field expects the cluster name. We then set the lock status of the given cluster to true in mongoDB.'
        )
       string (
            name:           'SET_CLUSTER_LOCK_STATUS_TO_FALSE',
            defaultValue:   'default',
            description:    'This field expects the cluster name. We then set the lock status of the given cluster to false in mongoDB.'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            defaultValue:   'detsuser_docker_config',
            description:    'ARM Docker secret'
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
        disableResume()
        timeout(time: 30, unit: 'MINUTES')
        durabilityHint 'PERFORMANCE_OPTIMIZED'
    }
    environment {
        BUILD_INFO                  = setBuildDescrition()
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
        stage("Retrieve Team Users associated with Booking") {
            when {
                allOf {
                    not {
                        environment ignoreCase: true, name: 'GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING',   value: 'default'
                    }
                    environment ignoreCase: true, name: 'GET_BOOKINGS_DETAILS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_EXPIRED_BOOKINGS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_CLUSTER_LOCK_STATUS',                      value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_TRUE',              value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_FALSE',             value: 'default'
                }
            }
            steps {
                script {
                    env.JIRA_ID = params.GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING
                }
                echo "==== Retrieve Team Users associated with Booking ${env.JIRA_ID} ===="
                sh "${bob} pooled-deployment:get-team-users-associated-with-booking"
                archiveArtifacts artifacts: 'users.properties', fingerprint: true, onlyIfSuccessful: true
            }      
        }
        stage("Retrieve All Booking Details associated with Jira") {
            when {
                allOf {
                    not {
                        environment ignoreCase: true, name: 'GET_BOOKINGS_DETAILS',                     value: 'default'
                    }
                    environment ignoreCase: true, name: 'GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING',       value: 'default'
                    environment ignoreCase: true, name: 'GET_EXPIRED_BOOKINGS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_CLUSTER_LOCK_STATUS',                      value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_TRUE',              value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_FALSE',             value: 'default'
                }
            }
            steps {
                script {
                    env.JIRA_ID = params.GET_BOOKINGS_DETAILS
                }
                echo "==== Retrieve All Booking Details associated with Booking ${env.JIRA_ID} ===="
                sh "${bob} pooled-deployment:get-booking-details"
                archiveArtifacts artifacts: 'booking.json, booking.properties', fingerprint: true, onlyIfSuccessful: true
            }      
        }
        stage("Retrieve Expired Bookings") {
            when {
                allOf {
                    not {
                        environment ignoreCase: true, name: 'GET_EXPIRED_BOOKINGS',                     value: 'default'
                    }
                    environment ignoreCase: true, name: 'GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING',       value: 'default'
                    environment ignoreCase: true, name: 'GET_BOOKINGS_DETAILS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_CLUSTER_LOCK_STATUS',                      value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_TRUE',              value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_FALSE',             value: 'default'
                }
            }
            steps {
                echo "==== Retrieve Expired Bookings ===="
                sh "${bob} pooled-deployment:get-expired-bookings"
                archiveArtifacts artifacts: 'expired_bookings_artifacts.json, expired_bookings_tuple.properties', fingerprint: true, onlyIfSuccessful: true
            }      
        }
        stage("Retrieve Cluster Lock status") {
            when {
                allOf {
                    not {
                        environment ignoreCase: true, name: 'GET_CLUSTER_LOCK_STATUS',                  value: 'default'
                    }
                    environment ignoreCase: true, name: 'GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING',       value: 'default'
                    environment ignoreCase: true, name: 'GET_BOOKINGS_DETAILS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_EXPIRED_BOOKINGS',                         value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_TRUE',              value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_FALSE',             value: 'default'
                }
            }
            steps {
                script {
                    env.SELECTED_CLUSTER_ID = params.GET_CLUSTER_LOCK_STATUS
                }
                echo "==== Retrieve Cluster Lock status for ${env.SELECTED_CLUSTER_ID} ===="
                sh "${bob} pooled-deployment:get-cluster-lock-status"
                archiveArtifacts artifacts: 'lock_status.properties', fingerprint: true, onlyIfSuccessful: true
            }      
        }
        stage("Set Cluster Lock status to true") {
            when {
                allOf {
                    not {
                        environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_TRUE',          value: 'default'
                    }
                    environment ignoreCase: true, name: 'GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING',       value: 'default'
                    environment ignoreCase: true, name: 'GET_BOOKINGS_DETAILS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_EXPIRED_BOOKINGS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_CLUSTER_LOCK_STATUS',                      value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_FALSE',             value: 'default'
                }
            }
            steps {
                script {
                    env.SELECTED_CLUSTER_ID = params.SET_CLUSTER_LOCK_STATUS_TO_TRUE
                }
                echo "==== Set Cluster Lock status to true for ${env.SELECTED_CLUSTER_ID} ===="
                sh "${bob} pooled-deployment:lock-cluster"
            }      
        }
        stage("Set Cluster Lock status to false") {
            when {
                allOf {
                    not {
                        environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_FALSE',         value: 'default'
                    }
                    environment ignoreCase: true, name: 'GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING',       value: 'default'
                    environment ignoreCase: true, name: 'GET_BOOKINGS_DETAILS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_EXPIRED_BOOKINGS',                         value: 'default'
                    environment ignoreCase: true, name: 'GET_CLUSTER_LOCK_STATUS',                      value: 'default'
                    environment ignoreCase: true, name: 'SET_CLUSTER_LOCK_STATUS_TO_TRUE',              value: 'default'
                }
            }
            steps {
                script {
                    env.SELECTED_CLUSTER_ID = params.SET_CLUSTER_LOCK_STATUS_TO_FALSE
                }
                echo "==== Set Cluster Lock status to false for ${env.SELECTED_CLUSTER_ID} ===="
                sh "${bob} pooled-deployment:release-lock-on-cluster"
            }      
        }
    }
}

def setBuildDescrition() {
    if (params.GET_EXPIRED_BOOKINGS.toLowerCase() != 'default') {
        return "Get Expired Bookings"
    }
    else if (params.GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING.toLowerCase() != 'default') {
        return "Get Team Users for Booking " + params.GET_TEAM_USERS_ASSOCIATED_WITH_BOOKING
    }
    else if (params.GET_BOOKINGS_DETAILS.toLowerCase() != 'default') {
        return "Get Bookings details " + params.GET_BOOKINGS_DETAILS
    }
    else if (params.GET_CLUSTER_LOCK_STATUS.toLowerCase() != 'default') {
        return "Get cluster lock status for " + params.GET_CLUSTER_LOCK_STATUS
    }
    else if (params.SET_CLUSTER_LOCK_STATUS_TO_TRUE.toLowerCase() != 'default') {
        return "Set lock status to true for " + params.SET_CLUSTER_LOCK_STATUS_TO_TRUE
    }
    else if (params.SET_CLUSTER_LOCK_STATUS_TO_FALSE.toLowerCase() != 'default') {
        return "Set lock status to false for " + params.SET_CLUSTER_LOCK_STATUS_TO_TRUE
    }
    else {
        return "${env.BUILD_NUMBER}"
    }
}