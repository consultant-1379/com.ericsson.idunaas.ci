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
            name: 'AMI_ID',
            description: 'Latest AMI ID'
        )
    }

    stages {
        stage('Set build name') {
            steps {
                script {
                    currentBuild.displayName = "${env.BUILD_NUMBER} ${env.ENV_NAME}"
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
        stage('Update Backup Server AMI') {
            steps {
                sh "${bob} configure-backup-server:update-backup-server-ami"
            }
        }
    }
    post {
       always {
            echo "Fix ownership: Some files has been created with wrong ownership (root)"
            sh "${bob} fix-ownership"
            echo "Fix ownership completed"

            archiveArtifacts artifacts: '**/logs/*.log',
                             fingerprint: true,
                             followSymlinks: false,
                             onlyIfSuccessful: true
        }
        success{
            archiveArtifacts artifacts: '**/backup_server_ip.properties',
                             fingerprint: true,
                             followSymlinks: false,
                             onlyIfSuccessful: true
            cleanWs()
        }
    }
}
