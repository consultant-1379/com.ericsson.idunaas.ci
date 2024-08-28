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
def RETRY_ATTEMPT = 1

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    options {
        skipDefaultCheckout()
    }
    parameters {
        string (
            name:           'DEPLOYMENT_TYPE',
            defaultValue:   'upgrade',
            description:    'Deployment Type, set \"install\" or \"upgrade\"'
        )
        string(
            name:           'ARMDOCKER_USER_SECRET',
            description:    'ARM Docker secret'
        )
        string (
            name:           'PATH_TO_AWS_FILES',
            description:    'Path within the Repo to the location of the AWS credentials and config directory'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'oss',
            description:    'Namespace to install the Chart'
        )
        string (
            name:           'KUBECONFIG_FILE',
            description:    'Jenkins credential id for kubectl configuration file which is a credential type of secret file (i.e. ossautoapp01_kubeconfig).'
        )
        string (
            name:           'FUNCTIONAL_USER_SECRET',
            defaultValue:   'ossadmin-creds',
            description:    'Jenkins secret ID for ARM Registry Credentials'
        )
        string (
            name:           'GAS_HOSTNAME',
            description:    'GAS FQDN to use for backup creation'
        )
        string(
            name:           'IDUN_USER_SECRET',
            defaultValue:   'Idunaas_user_credentials',
            description:    'Jenkins secret ID for default IDUN user password'
        )
        string (
            name:           'BACKUP_USER_SECRET',
            defaultValue:   'idunaas_backup_user_credentials',
            description:    'Jenkins secret ID for default backup server username and password'
        )
        string (
            name:           'BACKUP_SERVER_REMOTE_PATH',
            defaultValue:   'backup-data',
            description:    'Remote path on SFTP Backup server to store backups'
        )
        string (
            name:           'BACKUP_SERVER',
            description:    'Server for image backup and retrieval'
        )
        string (
            name:           'BACKUP_SCOPE',
            defaultValue:   'PLATFORM',
            description:    'Scope of the backup'
        )
        string (
            name:           'INT_CHART_VERSION',
            description:    'The version of the base platform to install'
        )
        string (
            name:           'ENV_NAME',
            description:    'The name of the environment')
        string (
            name:           'AWS_ECR_URL',
            description:    'Specify the AWS Elastic Container Registry URL'
        )
        string (
            name:           'PATH_TO_WORKDIR',
            description:    'Path for the dm-pod.ymal file'
        )
        string (
            name:           'SLAVE_LABEL',
            defaultValue:   'EIAP_CICD',
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
        SUB_MODULE_PATH = "com.ericsson.idunaas.ci/"
        MINIO_USER_SECRET = 'miniosecret'
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        DOCKER_FLAGS            = utils.getDockerFlags()
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
        stage('copy aws credentials') {
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
            }
            steps {
                sh "${bob_aas} prepare-workdir:copy-aws-credentials"
            }
        }
        stage('Get Installed Chart') {
            steps {
                sh "${bob_aas} gather-installed-oss-version:installed-idun-version"
            }
        }
        stage('save and export secrets') {
            steps {
                withCredentials([usernameColonPassword(credentialsId: env.MINIO_USER_SECRET, variable: 'MINIO_CREDS')]) {
                    sh "${bob_aas} create-export-secrets-minio:backup-eic-secrets-locally"
                    sh "${bob_aas} create-export-secrets-minio:export-eic-secrets-to-minio"
                }
            }
        }
        stage('Set backup name') {
            steps {
                sh "${bob_aas} set-backup-name"
            }
        }
        stage('Set Deployment Manager pod version') {
            steps {
                sh "${bob_aas} set-dm-version"
            }
        }
        stage('Deploy dm pod') {
            steps {
                sh "${bob_aas} deploy-dm"
            }
        }
        stage('Check DM Pod is ready') {
            steps {
                timeout (time: 3, unit: 'MINUTES') {
                    sh "${bob_aas} check-pod-status:check-status"
                }
            }
            post {
                success {
                    echo "DM pod is now in a ready state. Continuing"
                }
                failure {
                    echo "Exception thrown on waiting for DM pod to be ready."
                }
                aborted {
                    echo "Timeout after 3 minutes waiting for DM pod to be ready."
                }
            }
        }
        stage('Copy workdir and mount aws cli to dm pod from ci-utils'){
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
            }
            steps {
                sh "${bob_aas} copy-utils-dm-pod-public"
            }
        }
        stage('Copy workdir to dm pod from ci-utils'){
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'ccd'
            }
            steps {
                sh "${bob_aas} copy-utils-dm-pod-ccd"
            }
        }
        stage("Backup --> Import will be done here."){
            environment {
                    IDUN_USER_SECRET_ENV = credentials("${params.IDUN_USER_SECRET}")
                    IDUN_USER_USERNAME = "${IDUN_USER_SECRET_ENV_USR}"
                    IDUN_USER_PASSWORD = "${IDUN_USER_SECRET_ENV_PSW}"

                    BACKUP_SCOPE = "${params.BACKUP_SCOPE}"
                    BACKUP_USER_SECRET_ENV = credentials("${params.BACKUP_USER_SECRET}")
                    BACKUP_USER_USERNAME = "${BACKUP_USER_SECRET_ENV_USR}"
                    BACKUP_USER_PASSWORD = "${BACKUP_USER_SECRET_ENV_PSW}"

                    BACKUP_SERVER_REMOTE_PATH = "${params.BACKUP_SERVER_REMOTE_PATH}"
            }
            stages {
                stage('Create backup') {
                    steps {
                        sh "${bob_aas} backup-export-interactive:interactive-create"
                    }
                }
                stage('Export backup') {
                    steps {
                        sh "${bob_aas} backup-export-interactive:interactive-export"
                    }
                }
            }
        }
        stage('Annotate backup') {
            steps {
                sh "${bob_aas} annotate-backup"
            }
        }
    }
    post {
        always {
            retry(count: 5){
                script{
                    if (RETRY_ATTEMPT > 1) {
                        echo "Collecting deployment time data. Retry ${RETRY_ATTEMPT} of 5. Sleeping before retry..."
                        sleep(30)
                    }
                    else {
                        echo "Collecting deployment time data. Try ${RETRY_ATTEMPT} of 5"
                    }
                    RETRY_ATTEMPT = RETRY_ATTEMPT + 1

                    sh "${bob_aas} copy-logs-folder-from-dm-pod"
                    archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
                    sh "${bob_aas} cleanup-dm"
                }
            }
        }
    }
}
