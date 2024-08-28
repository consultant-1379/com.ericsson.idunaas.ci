#!/usr/bin/env groovy

/* Note:
 *   The following Jenkins configuration is required for this pipeline to work:
 *     A Jenkins slave with the label specified in pipeline.parameters.defaultValue
 */
@Library('aas-muon-utils-lib') _
def bob = "\${WORKSPACE}/bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

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
            description: 'The name of the environment to setup'
        )
        string(
            name:         'DASHBOARD_NAME',
            description:  "The name of the Grafana Dashboard e.g. EIAPaaS Overall Monitoring"
        )
        string(
            name:        'DATASOURCE_FQDN',
            description: "The FQDN of the Prometheus or other datasource for the given EIAPaaS environment e.g. 'https://prometheus.212442621681.eu-west-1.ac.ericsson.se'"
        )
        string(
            name:         'NAMESPACE',
            description:  "The name of the oss namespace for the given EIAPaaS deployment e.g. 'ossdev01'"
        )
        string(
            name:        'API_TOKEN',
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
        DOCKER_FLAGS            = utils.getDockerFlags()
    }
    stages {
        stage('Prepare Workdir') {
            steps {
                    sh 'git submodule update --init bob'
                    sh "${bob} git-clean"
                    sh 'git submodule sync'
                    sh 'git submodule update --init --recursive --remote'
            }
        }

        stage('Add Grafana Panel') {
            steps {
                withCredentials([string(credentialsId: params.API_TOKEN, variable: 'API_TOKEN')]){
                    echo "Jenkins: Preparing to invoke grafana_helper.py to add panel to dashboard"
                    sh "${bob} add-panel-to-dashboard"
                    echo "Jenkins: Finished invocation of grafana_helper.py script"
                }
            }
        }
    }
}