#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 */
@Library('aas-muon-utils-lib') _
def bob = "bob/bob --qq -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {

        string(name: 'PATH_TO_ENM_CONFIG',
                description: 'Path within the Repo to the location of the ENM config File')
        string(name: 'PATH_TO_EOCM_CONFIG',
                description: 'Path within the Repo to the location of the EOCM config File' )
        string(name: 'HOSTNAME',
                defaultValue: 'default',
                description: 'Hostname for SO/GAS')
        string(name: 'USERNAME',
                defaultValue: 'default',
                description: 'Username for SO/GAS')
        string(name: 'ENM_USER_SECRET',
                defaultValue: 'enm',
                description: 'ENM Administrator Secret' )
        string(name: 'EOCM_USER_SECRET',
                defaultValue: 'eocm',
                description: 'ECM user secret')
        string(name: 'SLAVE_LABEL',
                defaultValue: 'IDUN_CICD_ONE_POD_H',
                description: 'Specify the slave label that you want the job to run on')
        string(name: 'IDUN_USER_SECRET',
                defaultValue: 'idun_credentials',
                description: 'Jenkins secret ID for default IDUN user password')
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
        stage('Create EOCM Subsystem') {
            when { expression { return fileExists (env.PATH_TO_EOCM_CONFIG) } }
            steps {
                withCredentials([usernamePassword(credentialsId: env.IDUN_USER_SECRET, usernameVariable: 'IDUN_USER_USERNAME', passwordVariable: 'IDUN_USER_PASSWORD'), usernamePassword(credentialsId: env.EOCM_USER_SECRET, usernameVariable: 'EOCM_USER', passwordVariable: 'EOCM_USER_PASSWORD')]) {
                    sh "${bob} update-subsystem-values:substitute-eocm-details"
                    sh "${bob} create-eocm-subsystem"
                }
            }
        }
        stage('Create ENM Subsystem') {
            when { expression { return fileExists (env.PATH_TO_ENM_CONFIG) } }
            steps {
                withCredentials([usernamePassword(credentialsId: env.IDUN_USER_SECRET, usernameVariable: 'IDUN_USER_USERNAME', passwordVariable: 'IDUN_USER_PASSWORD'), usernamePassword(credentialsId: env.ENM_USER_SECRET, usernameVariable: 'ENM_USER', passwordVariable: 'ENM_USER_PASSWORD')]) {
                    sh "${bob} update-subsystem-values:substitute-enm-details"
                    sh "${bob} create-enm-subsystem"
                }
            }
        }
    }
}
