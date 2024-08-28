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
            name:           'STAGE',
            defaultValue:   'default',
            description:    'Stage along the pipeline we are at.'
        )
        string (
            name:           'PROJECT_MANAGER',
            defaultValue:   'default',
            description:    'Project manager associated with Jira.'
        )
        string (
            name:           'TEAM_NAME',
            defaultValue:   'default',
            description:    'Team name associated with Jira.'
        )
        string (
            name:           'TEAM_USERS',
            defaultValue:   'default',
            description:    'Team users associated with Jira.'
        )
        string (
            name:           'PROGRAM',
            defaultValue:   'default',
            description:    'Program name associated with Jira.'
        )
        string (
            name:           'APPROVED',
            defaultValue:   'default',
            description:    'Who approved the work, usually the project manager.'
        )
        string (
            name:           'START_DATE',
            defaultValue:   'default',
            description:    'Start date associated with Jira.'
        )
        string (
            name:           'END_DATE',
            defaultValue:   'default',
            description:    'End date associated with Jira.'
        )
        string (
            name:           'CLUSTER_ID',
            defaultValue:   'default',
            description:    'Cluster name associated with Jira.'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'default',
            description:    'Namespace associated with Jira.'
        )
        string (
            name:           'DOMAIN',
            defaultValue:   'default',
            description:    'Domain associated with Jira.'
        )
        string (
            name:           'EIC_VERSION',
            defaultValue:   'default',
            description:    'Helmfile Verion associated with Jira.'
        )
        string (
            name:           'COMMENT',
            defaultValue:   'default',
            description:    'Comment that will be added to Jira'
        )
        string (
            name:           'SPINNAKER_PIPELINE_EXECUTION',
            defaultValue:   'default',
            description:    'Spinnaker pipeline execution url.'
        )
        string (
            name:           'JENKINS_JOB_NAME',
            defaultValue:   'default',
            description:    'Jenkins job name where artifact lives.'
        )
        string (
            name:           'JENKINS_JOB_BUILD_NUMBER',
            defaultValue:   'default',
            description:    'Jenkins job build number where artifact lives.'
        )
        string (
            name:           'ARTIFACT_NAME',
            defaultValue:   'default',
            description:    'Name of artifact, some file, that resides in the workspace.'
        )
        string (
            name:           'TRANSITION_TO',
            defaultValue:   'default',
            description:    'State to transition jira to'
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
        timeout(time: 10, unit: 'MINUTES')
        durabilityHint 'PERFORMANCE_OPTIMIZED'
    }
    environment {
        DOCKER_FLAGS                = utils.getDockerFlags()
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        JENKINS_JOB_NAME            = removeJobSubStringPart(params.JENKINS_JOB_NAME)
        START_DATE                  = utils.convertDate(params.START_DATE)
        END_DATE                    = utils.convertDate(params.END_DATE)
    }
    stages {
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
        stage('Validate Team User Ids') {
            when {
                environment ignoreCase: true, name: 'STAGE', value: 'VALIDATE_TEAM_USER_IDS'
            }
            steps {
                echo "==== Validate Team User Ids ===="
                sh "${bob} pooled-deployment:validate-jira-team-user-ids"
            }
        }
        stage('Flow Complete Initial Install') {
            when {
                environment ignoreCase: true, name: 'STAGE', value: 'FLOW_COMPLETE_INITIAL_INSTALL'
            }
            steps {
                copyArtifacts filter: params.ARTIFACT_NAME, fingerprintArtifacts: true, projectName: env.JENKINS_JOB_NAME, selector: specific(params.JENKINS_JOB_BUILD_NUMBER)
                script {
                    create_jira_json_file()
                }
                sh "${bob} pooled-deployment:add-jira-comment"
                sh "${bob} pooled-deployment:add-jira-attachment"
                sh "${bob} pooled-deployment:add-jira-pipeline-details"
                sh "${bob} pooled-deployment:add-jira-installation-details"
                sh "${bob} pooled-deployment:add-jira-team-users-details"
                sh "${bob} pooled-deployment:add-jira-how-to-guide-details"
                sh "${bob} pooled-deployment:transition-jira"
            }
        }
        stage ('Cleaning workspace'){
            steps {
                cleanWs()
            }
        }
    }
}

def create_jira_json_file() {
    def jiraMap = [
        'jira_id'               :   "${params.JIRA_ID}",
        'team_name'             :   "${params.TEAM_NAME}",
        'program'               :   "${params.PROGRAM}",
        'project_manager'       :   "${params.PROJECT_MANAGER}",
        'approved'              :   "${params.APPROVED}",
        'booking_start_date'    :   "${env.START_DATE}",
        'booking_end_date'      :   "${env.END_DATE}",
        'cluster_name'          :   "${params.CLUSTER_ID}",
        'namespace'             :   "${params.NAMESPACE}",
        'domain'                :   "${params.DOMAIN}",
        'eic_version'           :   "${params.EIC_VERSION}"
    ]
    writeJSON file: 'jira.json', json: jiraMap
}

def removeJobSubStringPart(inputString) {
    return inputString.replace("/job/", "/")
}
