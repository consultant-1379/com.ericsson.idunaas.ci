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
            name:           'SELECTED_CLUSTER_ID',
            defaultValue:   'hall133',
            description:    'Selected cluster for pooled deployment installation.'
        )
        string (
            name:           'DOMAIN',
            defaultValue:   'google.com',
            description:    'Selected domain for pooled deployment installation.'
        )
        string (
            name:           'APP_SET',
            defaultValue:   'eric-eiap',
            description:    'Selected app set for pooled deployment installation.'
        )
        string (
            name:           'HELMFILE_VERSION',
            defaultValue:   '2.0.9-53',
            description:    'Selected helm file version for pooled deployment installation.'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'eric-eiap',
            description:    'Selected namespace for pooled deployment installation.'
        )
        string (
            name:           'TEAM_NAME',
            defaultValue:   'Team Photon',
            description:    'Team name requiring this pooled deployment installation.'
        )
        string (
            name:           'TEAM_USERS',
            defaultValue:   'egajada,qradpol',
            description:    'Comma separated list team users requiring this pooled deployment installation.'
        )
        string (
            name:           'TEAM_EMAIL',
            defaultValue:   'teamphoton@ericsson.com',
            description:    'Team email requiring this pooled deployment installation.'
        )
        string (
            name:           'START_DATE',
            defaultValue:   '12-01-2023',
            description:    'Booking starts this day'
        )
        string (
            name:           'END_DATE',
            defaultValue:   '12-01-2023',
            description:    'Booking ends this day'
        )
        string (
            name:           'BOOKING_STATUS',
            defaultValue:   'active',
            description:    'Booking ends this day'
        )
        string (
            name:           'ACTION',
            description:    'Do you want to add or remove users to specific cluster. Choices are "get", "add, "remove"'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            defaultValue:   'detsuser_docker_config',
            description:    'ARM Docker secret'
        )
        string (
            name:           'PROGRAM',
            defaultValue:   'default',
            description:    'Name of the program that the booking belongs to.'
        )
        string (
            name:           'PROJECT_MANAGER',
            defaultValue:   'default',
            description:    'Name of the project manager'
        )
        string (
            name:           'APPROVED_BY',
            defaultValue:   'default',
            description:    'Person who approved the booking'
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
            name:           'RESERVED_NAMESPACE_BOOKING',
            defaultValue:   'FALSE',
            description:    'Set to TRUE if it is a reserved namespace'
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
        BUILD_INFO                  = "${env.BUILD_NUMBER}-${params.SELECTED_CLUSTER_ID}-${params.NAMESPACE}-${params.ACTION}-${params.JIRA_ID}"
        DOCKER_FLAGS                = utils.getDockerFlags()
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        START_DATE                  = utils.convertDate(params.START_DATE)
        END_DATE                    = utils.convertDate(params.END_DATE)
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
        stage('Check K8S Connectivity') {
            steps {
                echo "==== Check K8S Connectivity ===="
                sh "${bob} do-health-check:check-eks-connectivity"
            }
        }
        stage('Create booking json file') {
            steps {
                script {
                    echo "==== Create booking json file ===="
                    create_booking_json_file()
                }
            }
        }
        stage('Add booking json to mongoDB') {
            steps {
                script {
                    echo "==== Add booking json to mongoDB ===="
                    sh "${bob} pooled-deployment:add-booking-json-to-mongoDB"
                }
            }
        }
        stage('Archive booking json file' ) {
            steps {
                echo "==== Archive booking json file ===="
                archiveArtifacts artifacts: 'booking.json', fingerprint: true, onlyIfSuccessful: true
            }
        }
        stage ('Cleaning workspace'){
            steps {
                cleanWs()
            }
        }
    }
}

def create_booking_json_file() {
    def bookingMap = [
        'jira_id'               :   "${params.JIRA_ID}",
        'team_name'             :   "${params.TEAM_NAME}",
        'team_users'            :   "${params.TEAM_USERS}",
        'cluster_name'          :   "${params.SELECTED_CLUSTER_ID}",
        'namespace'             :   "${params.NAMESPACE}",
        'app_set'               :   "${params.APP_SET}",
        'fqdn'                  :   "${params.DOMAIN}",
        'eic_version'           :   "${params.HELMFILE_VERSION}",
        'booking_start_date'    :   "${env.START_DATE}",
        'booking_end_date'      :   "${env.END_DATE}",
        'booking_status'        :   "${params.BOOKING_STATUS}",
        'team_email'            :   "${params.TEAM_EMAIL}",
        'program'               :   "${params.PROGRAM}",
        'project_manager'       :   "${params.PROJECT_MANAGER}",
        'reserved_namespace'    :   "${params.RESERVED_NAMESPACE_BOOKING}",
        'approved_by'           :   "${params.APPROVED_BY}"
    ]
    writeJSON file: 'booking.json', json: bookingMap
}
