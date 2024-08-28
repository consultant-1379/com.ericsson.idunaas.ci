#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */

@Library('aas-muon-utils-lib') _
def bob = "bob/bob --qq -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }

    parameters {
        string(
            name: 'IAM_AUTHENTICATOR',
            description: 'Full path within the Repo to the aws-iam-authenticator file'
        )
        string(
            name: 'NAMESPACE',
            defaultValue: 'oss',
            description: 'Namespace to install the Chart'
        )
        string(
            name: 'PATH_TO_AWS_FILES',
            description: 'Path within the Repo to the location of the AWS credentials and config directory'
        )
        string(
            name: 'ARMDOCKER_USER_SECRET',
            description: 'ARM Docker secret'
        )
        string (
            name:           'KUBECONFIG_FILE',
            description:    'Jenkins credential id for kubectl configuration file which is a credential type of secret file (i.e. ossautoapp01_kubeconfig).'
        )
        string(
            name: 'SLAVE_LABEL',
            defaultValue: 'IDUN_CICD_ONE_POD_H',
            description: 'Specify the slave label that you want the job to run on'
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
        stage('Clean Workspace') {
            steps {
                sh 'git clean -xdff'
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
            }
        }
        stage('Install Kube Config File') {
            steps {
                withCredentials ([
                    file (
                        credentialsId:  params.KUBECONFIG_FILE,
                        variable:       'KUBECONFIG'
                    )
                ]) {
                    sh 'install -m 600 -D "${KUBECONFIG}" kube_config/config'
                    sh 'install -m 600 "${KUBECONFIG}" ./admin.conf'
                }
            }
        }
        stage('Copy AWS credentials') {
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
            }
            steps {
                sh "${bob} prepare-workdir:copy-aws-credentials"
            }
        }
        stage('Gather installed IDUN version') {
            steps {
                script {
                    sh "${bob} gather-installed-oss-version"
                }
            }
        }
        stage('Archiving artifact.properties') {
            steps {
                script {
                    archiveArtifacts 'artifact.properties'
                 }
            }
        }
    }
}
