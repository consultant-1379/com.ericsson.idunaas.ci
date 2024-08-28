#!/usr/bin/env groovy

/* Note:
 *   The following Jenkins configuration is required for this pipeline to work:
 *     A Jenkins slave with the label specified in pipeline.parameters.defaultValue
 */
@Library('aas-muon-utils-lib') _
def bob = "\${WORKSPACE}/ci/bob/bob --qq -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

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
            description: 'The name of the environment to run the pre-setup checks for'
        )
        string(
            name:        'AWS_REGION',
            description: 'The AWS region to setup the cluster in',
            defaultValue: 'none'
        )
        string(
            name:         'PLATFORM_TYPE',
            defaultValue: 'aws',
            description:  'Cloud provider type'
        )
    }
    environment {
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        DOCKER_FLAGS            = utils.getDockerFlags()
    }
    stages {
        stage('Prepare Workdir') {
            steps {
                dir('ci'){
                    sh 'git submodule update --init bob'
                    sh "${bob} git-clean"
                    sh 'git submodule sync'
                    sh 'git submodule update --init --recursive --remote'
                }
            }
        }

        stage('Pre-setup Checks') {
            steps {
                echo "Starting pre-setup checks"
                sh "${bob} verify-aws-tools"
                echo "Successfully completed pre-setup checks"
            }
        }
    }
}
