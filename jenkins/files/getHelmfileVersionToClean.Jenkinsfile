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
    parameters {
        string(
            name: 'INT_CHART_VERSION',
            defaultValue: 'none',
            description: 'Integrastion Chart Version sent in through a jenkins artifact.properties.'
        )
        string(
            name: 'SLAVE_LABEL',
            defaultValue: 'IDUN_CICD_ONE_POD_H',
            description: 'Specify the slave label that you want the job to run on'
        )
        string(
            name: 'NAMESPACE',
            defaultValue: 'oss',
            description: 'Namespace to install the Chart'
        )
        string(
            name: 'PATH_TO_KUBECONFIG_FILE',
            description: 'Kubernetes configuration file to specify which environment to install on'
        )
        string(
            name: 'PATH_TO_AWS_FILES',
            defaultValue: 'NONE',
            description: 'Path within the Repo to the location of the AWS credentials and config directory'
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
                sh "install -m 600 ${PATH_TO_KUBECONFIG_FILE} ./admin.conf"
            }
        }
        stage('check platform type for aws credentials') {
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'

            }
            steps{
                sh "${bob} prepare-workdir:copy-aws-credentials"
            }
        }
        stage('Get Installed Helmfile Version'){
            steps{
                script{
                    try {
                        sh "${bob} -qq gather-installed-oss-version:installed-idun-version"
                    } catch (err) {
                        echo "WARN: Could not determine the installed version."
                    }
                }
            }
        }
        stage('Get Version to Delete'){
            steps {
                sh "${bob} get-version-to-clean"
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
