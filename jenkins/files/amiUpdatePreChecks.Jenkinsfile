#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */

def bob = "\${WORKSPACE}/ci/bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }

    parameters {
        string(
            name: 'ENV_NAME',
            description: 'Name of the Environment to Gather details for'
        )
        string(
            name:         'SLAVE_LABEL',
            defaultValue: 'IDUN_CICD_ONE_POD_H',
            description:  'The slave label of the node this job will run on'
        )
        string(
            name:         'RHEL_VERSION',
            defaultValue: '8',
            description:  'The version of Red Hat Enterprise to use in the backup server (a customized version of Ericsson)'
        )
    }

    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${env.ENV_NAME} RHEL-${env.RHEL_VERSION}"
                }
            }
        }

        stage('Prepare Workdir') {
            steps {
                dir('ci') {
                    sh 'git submodule update --init bob'
                    sh "${bob} git-clean"
                }

            }
        }

        stage('AMI Checks') {
            steps {
                dir('ci') {
                    sh "${bob} ami-checks"
                }
            }
        }

    }
    post {
        always {
            archiveArtifacts artifacts: 'ci/artifact.properties',
                             fingerprint: true,
                             followSymlinks: false,
                             onlyIfSuccessful: true
            cleanWs()
        }
    }
}
