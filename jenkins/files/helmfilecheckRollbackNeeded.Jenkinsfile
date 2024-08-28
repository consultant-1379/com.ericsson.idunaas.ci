#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 */
@Library('aas-muon-utils-lib') _
def bob_aas = "bob/bob -r \${WORKSPACE}/com.ericsson.idunaas.ci/jenkins/rulesets/ruleset2.0.yaml"
def bob_oss = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    options {
        skipDefaultCheckout()
    }
    parameters {
        string (
            name:           'INT_CHART_VERSION',
            description:    'The version of base platform to install'
        )
        string (
            name:           'INT_CHART_NAME',
            defaultValue:   'eric-eiae-helmfile',
            description:    'Integration Chart Name'
        )
        string (
            name:           'INT_CHART_REPO',
            defaultValue:   'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
            description:    'Integration Chart Repo'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            description:    'ARM Docker secret'
        )
        string (
            name:           'PATH_TO_AWS_FILES',
            description:    'Path within the Repo to the location of the AWS credentials and config directory'
        )
        string (
            name:           'FULL_PATH_TO_SITE_VALUES_FILE',
            defaultValue:   'site-values/idun/ci/template/site-values-latest.yaml',
            description:    'Full path within the oss-integration-ci repo to the idun template site-values-latest.yaml file'
        )
        string (
            name:           'KUBECONFIG_FILE',
            description:    'Jenkins credential id for kubectl configuration file which is a credential type of secret file (i.e. ossautoapp01_kubeconfig).'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'oss',
            description:    'Namespace to install the Chart'
        )
        string (
            name:           'FUNCTIONAL_USER_SECRET',
            defaultValue:   'ossadmin-creds',
            description:    'Jenkins secret ID for ARM Registry Credentials'
        )
        string (
            name:           'SLAVE_LABEL',
            defaultValue:   'IDUN_CICD_ONE_POD_H',
            description:    'Specify the slave label that you want the job to run on'
        )
        string (
            name:           'OSS_INTEGRATION_CI_BRANCH',
            defaultValue:   'master',
            description:    'The name of the branch to check out from oss-integration-ci repo'
        )
        string(
            name: 'PLATFORM_TYPE',
            defaultValue: 'aws',
            description: 'Cloud provider type'
        )
    }
    environment {
        BUILD_INFO              = "${params.KUBECONFIG_FILE.split("-|_")[0]} helmfile ${params.INT_CHART_VERSION}"
        SUB_MODULE_PATH         = 'com.ericsson.idunaas.ci/'
        HELMFILE_CHART_REPO     = "${params.INT_CHART_REPO}"
        HELMFILE_CHART_NAME     = "${params.INT_CHART_NAME}"
        HELMFILE_CHART_VERSION  = "${params.INT_CHART_VERSION}"
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        DOCKER_FLAGS            = utils.getDockerFlags()
    }
    stages {
        stage('Set Build Description') {
            steps {
                buildName "${env.BUILD_INFO}"
            }
        }
        stage('Checkout Repos') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '${OSS_INTEGRATION_CI_BRANCH}']],
                    extensions: [[$class: 'CheckoutOption', timeout: 5],
                    [$class: 'CloneOption', honorRefspec: true, noTags: true, reference: '', shallow: false, timeout: 5],
                    [$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: true, recursiveSubmodules: true, reference: '', timeout: 5, trackingSubmodules: true],
                    [$class: 'CleanBeforeCheckout']], userRemoteConfigs: [[url: '${GERRIT_MIRROR}/OSS/com.ericsson.oss.aeonic/oss-integration-ci']]])
            }
        }
        stage('Install Docker Config File') {
            steps {
                withCredentials ([
                    file (
                        credentialsId:  params.ARMDOCKER_USER_SECRET,
                        variable:       'DOCKERCONFIG'
                    )
                ]) {
                    sh 'install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json'
                    sh 'install -m 600 ${DOCKERCONFIG} ./dockerconfig.json'
                }
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
        stage('Prepare Working Directory') {
            steps {
                sh "${bob_aas} prepare-workdir:set-chart-version"
            }
        }
        stage('Copy AWS credentials') {
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
            }
            steps {
                sh "${bob_aas} prepare-workdir:copy-aws-credentials"
            }
        }
        stage('Fetch Site Values File') {
            steps {
                sh "${bob_oss} fetch-site-values"
            }
        }
        stage('Fetch Helmfile') {
            steps {
                withCredentials ([
                    usernamePassword (
                        credentialsId:      params.FUNCTIONAL_USER_SECRET,
                        usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                        passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob_oss} helmfile:fetch-helmfile"
                }
            }
        }
        stage('Untar Helmfile and Copy to Workdir') {
            steps {
                sh "${bob_oss} untar-and-copy-helmfile-to-workdir"
            }
        }
        stage('Check if a rollback is needed') {
            steps {
                sh "${bob_aas} check-rollback-needed"
            }
            post {
                success {
                    archiveArtifacts 'artifact.properties'
                }
            }
        }
    }
}
