#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */
@Library('aas-muon-utils-lib') _
def bob = "bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    options {
        timeout(time: 3, unit: 'MINUTES')
        buildDiscarder logRotator(artifactDaysToKeepStr: '5', artifactNumToKeepStr: '50', daysToKeepStr: '5', numToKeepStr: '50')
    }
    parameters {
        string(
            name: 'DEPLOYMENT_NAME',
            defaultValue: 'all',
            description: 'Deployment Name that we wish to pause or resume grafana alert/s on. Default is all environments.',
        )
        string(
            name: 'ACTION',
            defaultValue: 'pause',
            description: 'Choose "pause" to disable alert/s or choose "resume" to enable alert/s. Default value is pause.'
        )
        string(
            name: 'SLAVE_LABEL',
            defaultValue: 'IDUN_CICD_ONE_POD_H',
            description: 'Specify the slave label that you want the job to run on.'
        )
        string(
            name: 'API_TOKEN',
            defaultValue: 'grafana-api-token',
            description: 'The bearer token used for Grafana authentication'
        )
        string(
            name: 'PLATFORM_TYPE',
            defaultValue: 'aws',
            description: 'Cloud provider type'
        )
    }
    environment {
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        DOCKER_FLAGS = utils.getDockerFlags()
        DEPLOYMENT = params.DEPLOYMENT_NAME.toLowerCase()
        SCRIPT_ACTION = params.ACTION.toLowerCase()
    }
    stages {
        stage('Prepare') {
            steps {
                sh 'git clean -xdff'
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
            }
        }
        stage('Pause/Resume Grafana Alerts') {
            steps {
                script {
                    withCredentials([string(credentialsId: params.API_TOKEN, variable: 'API_TOKEN')]){
                        sh "${bob} do-pause-resume-grafana-alerts"
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts allowEmptyArchive: true, artifacts: '*.log,*.json'
        }
    }
}