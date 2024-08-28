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
                name: 'NAMESPACE',
                description: 'Namespace on the cluster that the deployment is installed into.'
        )
        string(
                name: 'PATH_TO_KUBECONFIG_FILE',
                description: 'Kubernetes configuration file to specify which environment to install on'
        )
        string(
                name: 'PATH_TO_AWS_FILES',
                description: 'Path within the Repo to the location of the AWS credentials and config directory'
        )
        string(
                name: 'SLAVE_LABEL',
                defaultValue: 'IDUN_CICD_ONE_POD_H',
                description: 'Label of the Jenkins slave where this jenkins job should be executed.'
        )
        string(
                name: 'ARMDOCKER_USER_SECRET',
                defaultValue: 'ossadm_docker_config',
                description: 'ARM Docker secret'
        )
        string(
                name: 'COLLECT_LOGS',
                defaultValue: 'false',
                description: 'Collect logs of EIAP in case the health check fails'
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
        DOCKER_FLAGS_DEPLOYMENT_MANAGER = utils.getDeploymentManagerFlags()
    }
    stages {
        stage('Cleaning Git Repo') {
            steps {
                sh 'git submodule update --init bob'
                sh "${bob} git-clean"
                sh 'git submodule sync'
                sh 'git submodule update --init --recursive --remote'
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
                }
            }
        }
        stage('Install AWS Files') {
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
            }
            steps {
                sh "${bob} prepare-workdir:copy-aws-credentials"
            }
        }
        stage('Install Kube Config File') {
            steps {
                sh 'install -m 600 -D ${PATH_TO_KUBECONFIG_FILE} kube_config/config'
            }
        }
        stage('Execution Health Check using Deployment Manager') {
            steps {
                sh "${bob} check-helmfile-deployment-status:execute-health-check-using-deployment-manager"
            }
        }
        stage('Checking output') {
            steps {
                script {
                    try {
                        // Fails with non-zero exit if string does not exist in log file
                        def dir1 = sh(
                            script:
                                'cd logs; ' +
                                'cat "$(ls -1rt | grep healthcheck | tail -n1)" | ' +
                                'grep "healthcheck all command completed successfully with no failures"',
                            returnStdout:true).trim()
                    } catch (Exception ex) {
                        println("Healthcheck didn't succeed: ${ex}")
                        currentBuild.result = 'FAILED'

                        if(env.COLLECT_LOGS.trim().equals("true")){
                            sh "${bob} gather-deployment-logs"
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts allowEmptyArchive: true, artifacts: '**/*.log,logs/*.tgz'
            cleanWs()
        }
        failure {
            sh  'ENVNAME=$(basename $(dirname ${PATH_TO_AWS_FILES}));'               +
                'echo "Health check failed in $ENVNAME for namespace ${NAMESPACE}. ' +
                'Check the pipeline from Spinnaker."'                                +
                ' | mail -s "Health Check Failure in $ENVNAME" '                     +
                ' -a "From: Health Check Alert <no-reply@ericsson.se>" '             +
                ' PDLTEAMMUO@pdl.internal.ericsson.com'
        }
    }
}
