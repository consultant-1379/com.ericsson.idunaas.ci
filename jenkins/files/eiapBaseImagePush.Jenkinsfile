#!/usr/bin/env groovy

/* Note:
 *   The following Jenkins configuration is required for this pipeline to work:
 *     A Jenkins slave with the label specified in pipeline.parameters.defaultValue
 */

def bob = "\${WORKSPACE}/ci/bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }

    parameters {
        string(
            name:         'SLAVE_LABEL',
            defaultValue: 'IDUN_CICD_ONE_POD_H',
            description:  'The slave label of the node this job will run on'
        )
        string(
            name:        'ENV_NAME',
            description: 'The name of the environment to setup',
            defaultValue: 'none'
        )
        string(
            name:        'AWS_REGION',
            description: 'The AWS region to push images in',
            defaultValue: 'eu-west-1'
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
            }
        }
        stage('Push Images from Armdocker to AWS ECR') {
            steps {
                echo "Starting to pull and push each image"
                sh "${bob} eiap-push-images"
                echo "Finished"
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
