#!/usr/bin/env groovy
/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */

def bob = "bob/bob --qq -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    options {
        disableConcurrentBuilds()
    }
    parameters {
        string(name: 'INT_CHART_VERSION', defaultValue: '0.0.0', description: 'Integrastion Chart Version sent in through a jenkins artifact.properties.')
        string(name: 'INT_CHART_REPO', defaultValue: 'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm/', description: 'Integration chart repo.')
        string(name: 'INT_CHART_NAME', defaultValue: 'eric-eiae-helmfile', description: 'Integration Chart name')
        string(name: 'SLAVE_LABEL', defaultValue: 'IDUN_CICD_ONE_POD_H', description: 'Specify the slave label that you want the job to run on')
        string(name: 'FUNCTIONAL_USER_SECRET', defaultValue: 'cloudman-user-creds', description: 'Jenkins secret ID for ARM Registry Credentials')
    }
    stages {
        stage('Prepare') {
            steps {
                sh 'git clean -xdff'
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
            }
        }
        stage('Get Latest CHART or HelmFile Version') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET, usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD')]) {
                    sh '''
                        if [ ${INT_CHART_VERSION} != "0.0.0" ]; then
                            echo "INT_CHART_VERSION:${INT_CHART_VERSION}" > artifact.properties
                        else
                            bob/bob --qq -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml build-ci-script-executor-image get-latest-helmfile-version
                        fi
                    '''
                }
            }
        }
        stage('Archive Artifact Properties') {
            steps {
                script {
                    archiveArtifacts 'artifact.properties'
                }
            }
        }
    }
}
