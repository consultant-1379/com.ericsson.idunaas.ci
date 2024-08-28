#!/usr/bin/env groovy
/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */
@Library('aas-muon-utils-lib') _
def bob_aas = "bob/bob -r \${WORKSPACE}/com.ericsson.idunaas.ci/jenkins/rulesets/ruleset2.0.yaml"
def bob_oss = "bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

def getCiDockerImageUrl() {
    return "${params.CI_DOCKER_IMAGE}".contains('default') ? "${params.CI_DOCKER_IMAGE}".split(':')[0] + ":" + readFile("${params.VERSION_PREFIX_FILE}").trim() : "${params.CI_DOCKER_IMAGE}"
}

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    options {
        timeout(15)
        timestamps()
        disableResume()
        skipDefaultCheckout()
        durabilityHint 'PERFORMANCE_OPTIMIZED'
        buildDiscarder logRotator(artifactDaysToKeepStr: '5', artifactNumToKeepStr: '50', daysToKeepStr: '5', numToKeepStr: '50')
    }
    parameters {
        string (
            name:           'INT_CHART_VERSION',
            defaultValue:   '0.0.0',
            description:    'The version of the Helmfile sent in through a previous jenkins build\'s artifact.properties.'
        )
        string (
            name:           'INT_CHART_REPO',
            defaultValue:   'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
            description:    'The repository in which the Helmfile is stored.'
        )
        string (
            name:           'INT_CHART_NAME',
            defaultValue:   'eric-eiae-helmfile',
            description:    'The name of the Helmfile to be searched'
        )
        string (
            name:           'FUNCTIONAL_USER_SECRET',
            defaultValue:   'ossadmin-creds',
            description:    'Jenkins secret ID for ARM Registry Credentials'
        )
        string (
            name:           'CI_DOCKER_IMAGE',
            defaultValue:   'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
            description:    'CI Docker image to use. Mainly used in CI Testing flows'
        )
        string (
            name:           'VERSION_PREFIX_FILE',
            defaultValue:   'VERSION_PREFIX',
            description:    'VERSION_PREFIX file that exists in the root folder of the oss-integration-ci repo'
        )
        string (
            name:           'SPINNAKER_PIPELINE_ID',
            defaultValue:   '45454JHGHG865656',
            description:    'Unique spinnaker pipeline this jenkins job is associated with'
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
        string (
            name:           'PLATFORM_TYPE',
            defaultValue:   'aws',
            description:    'Cloud provider type'
        )
    }
    environment {
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        DOCKER_FLAGS                = utils.getDockerFlags()
    }
    stages {
        stage('Checkout Repos') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '${OSS_INTEGRATION_CI_BRANCH}']],
                    extensions: [[$class: 'CheckoutOption', timeout: 5],
                    [$class: 'CloneOption', honorRefspec: true, noTags: true, reference: '', shallow: false, timeout: 5],
                    [$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: true, recursiveSubmodules: true, reference: '', timeout: 5, trackingSubmodules: true],
                    [$class: 'CleanBeforeCheckout']], userRemoteConfigs: [[url: '${GERRIT_MIRROR}/OSS/com.ericsson.oss.aeonic/oss-integration-ci']]])
            }
        }
        stage('Get HelmFile Version from INT_CHART_VERSION parameter') {
            when {
                not {
                    environment ignoreCase: true, name: 'INT_CHART_VERSION', value: '0.0.0'
                }
            }
            steps {
                sh "${bob_aas} prepare-workdir:set-chart-version"
                sh "${bob_aas} prepare-workdir:write-to-properties"
            }
        }
        stage('Get Latest HelmFile Version from Repo using oss-integration-ci ci docker image') {
            when {
                environment ignoreCase: true, name: 'INT_CHART_VERSION', value: '0.0.0'
            }
            environment {
                CI_DOCKER_IMAGE = getCiDockerImageUrl()
            }
            steps {
                withCredentials ([
                    usernamePassword (
                        credentialsId:      env.FUNCTIONAL_USER_SECRET,
                        usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                        passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob_oss} get-latest-helmfile-version"
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'artifact.properties', fingerprint: true, followSymlinks: false, onlyIfSuccessful: true
            cleanWs()
        }
    }
}