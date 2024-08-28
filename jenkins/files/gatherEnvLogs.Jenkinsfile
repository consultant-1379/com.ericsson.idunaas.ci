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
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder logRotator(artifactDaysToKeepStr: '5', artifactNumToKeepStr: '50', daysToKeepStr: '5', numToKeepStr: '50')
    }
    parameters {
        string(name: 'ENV_NAME',
            description: 'The name of the environment'
        )
        string(name: 'NAMESPACE',
            description: 'Namespace of the environment'
        )
        string(name: 'INSTALLED_CHART_VERSION',
            description: 'Installed chart version in the environment'
        )
        string(name: 'ARMDOCKER_USER_SECRET',
            description: 'ARM Docker secret'
        )
        string(name: 'PATH_TO_AWS_FILES',
            description: 'Path within the Repo to the location of the AWS credentials and config directory'
        )
        string(name: 'IAM_AUTHENTICATOR',
            description: 'Full path within the Repo to the aws-iam-authenticator file'
        )
        string(name: 'PATH_TO_KUBECONFIG_FILE',
            description: 'Kubernetes configuration file to specify which environment'
        )
        string(name: 'SLAVE_LABEL',
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
                    sh "${bob} create-kube-config-dir"
                    sh "install -m 600 ${PATH_TO_KUBECONFIG_FILE} ./kube_config/config"
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
        stage('Gather Logs') {
            steps {
                sh "${bob} gather-deployment-logs"
            }
        }
    }
    post {
        success {
            addBadge icon: 'success.gif', text: 'Success'
            addShortText background: '', border: 0, borderColor: '', color: 'blue', link: '', text: "Retrieved ${env.ENV_NAME} : ${env.INSTALLED_CHART_VERSION} logs"
        }
        always {
            archiveArtifacts artifacts: 'logs_*.tgz', allowEmptyArchive: true
        }
    }
}