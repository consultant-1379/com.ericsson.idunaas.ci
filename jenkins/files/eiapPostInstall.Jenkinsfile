#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 */
@Library('aas-muon-utils-lib') _
def bob = "bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(
                name: 'ENV_NAME',
                description: 'The name of the environment to gather the environment details for')
        string(
                name: 'ARMDOCKER_USER_SECRET',
                description: 'ARM Docker secret')
        string(
                name: 'IDUN_USER_SECRET',
                defaultValue: 'idun_credentials',
                description: 'Jenkins secret ID for default IDUN user password'
        )
        string(
                name: 'USERS_PW_SECRET',
                defaultValue: 'eic_user_credential',
                description: 'Jenkins secret ID for default EIC Users password'
        )
        string(
                name: 'PATH_TO_AWS_FILES',
                description: 'Path within the Repo to the location of the AWS credentials and config directory')
        string(
                name: 'NAMESPACE',
                defaultValue: 'ossdev01',
                description: 'Namespace to install the Chart' )
        string(
                name: 'SLAVE_LABEL',
                defaultValue: 'IDUN_CICD_ONE_POD_H',
                description: 'Specify the slave label that you want the job to run on')
        string(
            name: 'GAS_HOSTNAME',
            defaultValue: 'default',
            description: 'Hostname for GAS'
        )
        string(
            name: 'PATH_TO_WORKDIR',
            description: 'Specify the Path to workdir in deployments '
        )
        string(
            name: 'PODNAME',
            description: 'Name of the pod',
            defaultValue: 'create-eiap-user'
        )
        string(
            name: 'PLATFORM_TYPE',
            defaultValue: 'aws',
            description: 'Cloud provider type'
        )
    }
    environment {
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        DOCKER_FLAGS            = utils.getDockerFlags()
    }
    stages {
        stage('Prepare') {
            steps {
                sh 'git clean -xdff'
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
            }
        }
        stage('Prepare Working Directory') {
            steps {
                withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                    sh "install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json"
                }
                withCredentials( [file(credentialsId: env.ENV_NAME + "_kubeconfig", variable: 'KUBECONFIG')]) {
                    sh 'install -m 600 "${KUBECONFIG}" ./admin.conf'
                }
            }
        }
        stage('Copy AWS credentials') {
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
            }
            steps {
                sh "${bob} prepare-workdir:copy-aws-credentials"
            }
        }
        stage ('Deploy Pod'){
            steps{
                sh "${bob} create-eiap-user:deploy-pod"
            }
        }
        stage('Check DM Pod is ready') {
            steps {
                timeout (time: 3, unit: 'MINUTES') {
                    sh "${bob} create-eiap-user:check-pod-status"
                }
            }
            post {
                success {
                    echo "Pod is now in a ready state. Continuing"
                }
                failure {
                    echo "Exception thrown on waiting for pod to be ready."
                }
                aborted {
                    echo "Timeout after 3 minutes waiting for pod to be ready."
                }
            }
        }
        stage('Copy Files to Pod'){
            steps{
                sh "${bob} create-eiap-user:copy-cert"
                sh "${bob} create-eiap-user:copy-script"
                withCredentials([usernamePassword(credentialsId: params.IDUN_USER_SECRET, usernameVariable: 'IDUN_USER_USERNAME', passwordVariable: 'IDUN_USER_PASSWORD'),
                                 usernamePassword(credentialsId: params.USERS_PW_SECRET, usernameVariable: 'USERS_USERNAME', passwordVariable: 'USERS_PASSWORD')]) {
                    sh "${bob} create-eiap-user:copy-users-file"
                }
            }
        }
        stage('Create EIAP Users'){
            steps{
                withCredentials([usernamePassword(credentialsId: params.IDUN_USER_SECRET, usernameVariable: 'IDUN_USER_USERNAME', passwordVariable: 'IDUN_USER_PASSWORD')]) {
                    sh "${bob} create-eiap-user:execute-script"
                }
            }
        }
    }
    post{
        always{
            sh 'sleep 20s'
            sh  "${bob} create-eiap-user:delete-pod"
        }
    }
}
