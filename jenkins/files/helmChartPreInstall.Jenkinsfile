#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 */

def bob = "bob/bob --qq -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string(name: 'DEPLOYMENT_TYPE',
                defaultValue: 'upgrade',
                description: 'Deployment Type, set \"install\" or \"upgrade\"' )
        string(name: 'ARMDOCKER_USER_SECRET',
                description: 'ARM Docker secret')
        string(name: 'PATH_TO_AWS_FILES',
                description: 'Path within the Repo to the location of the AWS credentials and config directory')
        string(name: 'IAM_AUTHENTICATOR',
                description: 'Full path within the Repo to the aws-iam-authenticator file')
        string(name: 'NAMESPACE',
                defaultValue: 'oss',
                description: 'Namespace to install the Chart' )
        string(name: 'PATH_TO_KUBECONFIG_FILE',
                description: 'Kubernetes configuration file to specify which environment to install on' )
        string(name: 'FUNCTIONAL_USER_SECRET',
                defaultValue: 'ossadmin-creds',
                description: 'Jenkins secret ID for ARM Registry Credentials')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'IDUN_CICD_ONE_POD_H',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'IDUN_USER_SECRET',
                defaultValue: 'Idunaas_user_credentials',
                description: 'Jenkins secret ID for default IDUN user password')
    }
    stages {
        stage('Prepare') {
            steps {
                sh 'git clean -xdff'
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
            }
        }
        stage('Prepare Working Directory') {
            steps {
                withCredentials([file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]) {
                    sh "install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json"
                    sh "install -m 755 ${IAM_AUTHENTICATOR} aws-iam-authenticator"
                    sh "install -m 600 ${PATH_TO_KUBECONFIG_FILE} ./admin.conf"
                    sh "${bob} prepare-workdir:copy-aws-credentials"
                }
            }
        }
        stage('Cleanup installed IDUN release') {
            steps {
                script {
                    if (env.DEPLOYMENT_TYPE == 'install') {
                        withCredentials([usernamePassword(credentialsId: env.IDUN_USER_SECRET, usernameVariable: 'IDUN_USER_USERNAME', passwordVariable: 'IDUN_USER_PASSWORD')]) {
                            sh "${bob} remove-installed-release remove-installed-pvcs remove-installed-secrets"
                        }
                    }
                }
            }
        }
        stage('Pre Deployment Configurations') {
            steps {
                script {
                    if (env.DEPLOYMENT_TYPE == 'install') {
                        withCredentials([usernamePassword(credentialsId: env.IDUN_USER_SECRET, usernameVariable: 'IDUN_USER_USERNAME', passwordVariable: 'IDUN_USER_PASSWORD')]) {
                            sh "${bob} create-release-namespace create-credentials-secrets"
                        }
                    }
                }
            }
        }
    }
}
