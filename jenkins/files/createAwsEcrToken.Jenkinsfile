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
        string(
            name: 'ARMDOCKER_USER_SECRET',
            description: 'ARM Docker secret'
        )
        string(
            name: 'PATH_TO_AWS_FILES',
            description: 'Path within the Repo to the location of the AWS credentials and config directory'
        )
        string(
            name: 'SLAVE_LABEL',
            defaultValue: 'IDUN_CICD_ONE_POD_H',
            description: 'Specify the slave label that you want the job to run on'
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
                sh 'git submodule update --init bob'
                sh "${bob} git-clean"
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
            }
        }
        stage('Prepare Working Directory') {
            steps {
                sh "${bob} prepare-workdir:copy-aws-credentials"
                withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                    sh "install -m 600 ${DOCKERCONFIG} ./dockerconfig.json"
                }
            }
        }
        stage('Generate AWS ECR Token') {
            steps {
                sh "${bob} generate-aws-ecr-token"
            }
        }
        stage('Archive AWS ECR TOKEN File') {
            steps {
                archiveArtifacts artifacts: 'artifact.properties', fingerprint: true, onlyIfSuccessful: true
            }
        }
        stage ('Delete Workspace') {
            steps {
                cleanWs()
            }
        }
    }
}