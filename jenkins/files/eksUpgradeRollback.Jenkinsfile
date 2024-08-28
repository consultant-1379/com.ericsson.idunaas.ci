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
            name: 'ARMDOCKER_USER_SECRET',
            description: 'ARM Docker secret'
        )
        string(
            name: 'EKS_VERSION',
            description: 'EKS version required to upgrade'
        )
        string(
            name: 'INSTANCE_SIZE',
            description: 'Instance size of worker nodes'
        )
    }

    stages {
        stage('Prepare Workdir') {
            steps {
                dir('ci') {
                    sh 'git submodule update --init bob'
                    sh "${bob} git-clean"
                    sh 'git submodule sync'
                    sh 'git submodule update --init --recursive --remote'
                }
                withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                    sh 'install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json'
                }
                sh "${bob} upgrade-cluster:prepare"
            }
        }
        stage('Validate Config') {
            steps {
                sh "${bob} verify-config:validate-config"
            }
        }

        stage('Rollback') {
            steps {
                sh "${bob} upgrade-cluster:rollback-cluster"
            }
        }

    }

    post {
       always {
            echo "Fix ownership: Some files has been created with wrong ownership (root)"
            sh "${bob} fix-ownership"
            echo "Fix ownership completed"

        }
    }
}
