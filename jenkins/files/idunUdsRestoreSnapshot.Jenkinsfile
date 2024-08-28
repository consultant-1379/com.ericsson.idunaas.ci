#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 */
@Library('aas-muon-utils-lib') _
def bob = "bob/bob --qq -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'ENV_NAME',
                description: 'Name of the Environment')
        string(name: 'ARMDOCKER_USER_SECRET',
                description: 'ARM Docker secret')
        string(name: 'PATH_TO_AWS_FILES',
                description: 'Path within the Repo to the location of the AWS credentials and config directory')
        string(name: 'NAMESPACE',
                description: 'Namespace to install the Chart' )
        string(name: 'PATH_TO_KUBECONFIG_FILE',
                description: 'Kubernetes configuration file to specify which environment to install on' )
        string(name: 'SLAVE_LABEL',
                defaultValue: 'IDUN_CICD_ONE_POD_H',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'CASSANDRA_USER_SECRET',
                defaultValue: 'idunaas_cassandra_credentials',
                description: 'Jenkins secret ID for Cassandra Credentials')
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
                    sh "install -m 600 ${PATH_TO_KUBECONFIG_FILE} ./admin.conf"
                }
            }
        }
        stage('Copy aws credentials') {
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
            }
            steps {
                sh "${bob} prepare-workdir:copy-aws-credentials"
            }
        }
        stage('Restore cassandra snapshot to cleanup UDS') {
            steps {
                sh "${bob} uds-snapshot-restore uds-backend-job-wait"
            }
        }
        stage('Check the key in DB and delete kafka topics if no match') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.CASSANDRA_USER_SECRET, usernameVariable: 'CASSANDRA_USERNAME', passwordVariable: 'CASSANDRA_PASSWORD')]) {
                    sh "${bob} uds-kafka-topics-delete"
                }
            }
        }
    }
}
