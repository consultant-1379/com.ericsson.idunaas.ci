#!/usr/bin/env groovy

/* Note:
 *   The following Jenkins configuration is required for this pipeline to work:
 *     A Jenkins slave with the label specified in pipeline.parameters.defaultValue
 */

def bob = "bob/bob --qq -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }

    parameters {
        string(
            name:        'ENV_NAME'
            description: 'The name of the environment to verify the configuration for'
        )
        string(
            name:         'ENV_DETAILS_DIR'
            defaultValue: 'deployments/conf-files'
            description:  'Path relative to the CI repo root dir of the <ENV_NAME>.conf file containing the details for the deployment'
        )
        string(
            name:         'SLAVE_LABEL'
            defaultValue: 'IDUN_CICD_ONE_POD_H'
            description:  'The slave label of the node this job will run on'
        ) 
    }

    stages {
        stage('Prepare Workdir') {
            steps {
                sh 'git clean -xdff'
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
            }
        }

        stage('Verify Config') {
	    steps {
                sh "${bob} verify-config-items"
            }
        }
    }
}
