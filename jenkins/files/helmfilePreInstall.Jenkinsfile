#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 */
@Library('aas-muon-utils-lib') _
def bob_aas = "com.ericsson.idunaas.ci/bob/bob -r \${WORKSPACE}/com.ericsson.idunaas.ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string (
            name:           'DEPLOYMENT_TYPE',
            defaultValue:   'upgrade',
            description:    'Deployment Type, set \"install\" or \"upgrade\"'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'oss',
            description:    'Namespace to purge environment'
        )
        string (
            name:           'KUBECONFIG_FILE',
            description:    'Jenkins credential id for kubectl configuration file which is a credential type of secret file (i.e. ossautoapp01_kubeconfig).'
        )
        string (
            name:           'PATH_TO_AWS_FILES',
            defaultValue:   'default',
            description:    'Path within the Repo to the location of the AWS credentials and config directory'
        )
        string (
            name:           'FULL_PATH_TO_SITE_VALUES_FILE',
            defaultValue:   'site-values/idun/ci/template/site-values-latest.yaml',
            description:    'Full path within the oss-integration-ci repo to the idun template site-values-latest.yaml file'
        )
        string (
            name:           'PATH_TO_SITE_VALUES_OVERRIDE_FILE',
            description:    'Full path within com.ericsson.idunaas.ci repo to the site-values-override.yaml file'
        )
        string (
            name:           'DOCKER_REGISTRY',
            defaultValue:   'armdocker.rnd.ericsson.se',
            description:    'Set this to the docker registry to execute the deployment from. Used when deploying from Officially Released CSARs'
        )
        string (
            name:           'IDUN_USER_SECRET',
            defaultValue:   'idun_credentials',
            description:    'Jenkins secret ID for default IDUN user password'
        )
        string (
            name:           'ADP_DDC_USER_SECRET',
            defaultValue:   'ddc_sftpuser_credentials',
            description:    'Jenkins secret ID for default APD-DDC user password'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            defaultValue:   'ossadm_docker_config',
            description:    'ARM Docker secret'
        )
        string (
            name:           'FUNCTIONAL_USER_SECRET',
            defaultValue:   'ossadmin-creds',
            description:    'Jenkins secret ID for ARM Registry Credentials'
        )
        string (
            name:           'INT_CHART_REPO',
            defaultValue:   'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
            description:    'Integration Chart Repo'
        )
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
        ENV_NAME                = "${params.KUBECONFIG_FILE.split("-|_")[0]}"
        BUILD_INFO              = "${ENV_NAME} helmfile ${params.INT_CHART_VERSION}"
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
                script {
                    buildDescription "${env.BUILD_INFO}"
                    currentBuild.displayName = "${env.BUILD_INFO}"
                }
            }
        }
        stage('Checkout Repos') {
            steps {
                dir('com.ericsson.idunaas.ci') {
                    sh 'git submodule update --init bob'
                }
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
        stage('Copy aws credentials') {
            when {
                environment ignoreCase: true, name: 'PLATFORM_TYPE', value: 'aws'
            }
            steps {
                sh "${bob_aas} prepare-workdir:copy-aws-credentials"
            }
        }
//         stage('Fetch Helmfile') {
//             steps {
//                 withCredentials ([
//                     usernamePassword (
//                         credentialsId:      params.FUNCTIONAL_USER_SECRET,
//                         usernameVariable:   'FUNCTIONAL_USER_USERNAME',
//                         passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
//                     )
//                 ]) {
//                     sh "${bob_oss} helmfile:fetch-helmfile"
//                 }
//             }
//         }
//         stage('Untar Helmfile and Copy to Workdir') {
//             steps {
//                 sh "${bob_oss} untar-and-copy-helmfile-to-workdir"
//             }
//         }
//         stage('Fetch Site Values File') {
//             steps {
//                 sh "${bob_oss} fetch-site-values"
//             }
//         }
        stage('Check EKS Connectivity') {
            steps {
                sh "${bob_aas} do-health-check:check-eks-connectivity"
            }
        }
        stage('Create namespace if not exist') {
            steps {
                sh "${bob_aas} create-release-namespace"
            }
        }
        stage('Clean up and Pre Deployment Configuration') {
            when {
                environment ignoreCase: true, name: 'DEPLOYMENT_TYPE', value: 'install'
            }
            stages {
                stage('Cleanup Installed Releases'){
                    steps{
                        sh "${bob_aas} remove-helm3-installed-release"
                    }
                }
                stage('Cleanup Helm file Annotation'){
                    steps{
                        sh "${bob_aas} cleanup-helmfile-annotation"
                    }
                }
                stage('Cleanup Installed PVCS') {
                    steps {
                        sh "${bob_aas} remove-installed-pvcs"
                    }
                }
                stage('Cleanup Installed Secrets') {
                    steps {
                        withCredentials ([
                            usernamePassword (
                                credentialsId:      env.IDUN_USER_SECRET,
                                usernameVariable:   'IDUN_USER_USERNAME',
                                passwordVariable:   'IDUN_USER_PASSWORD'
                            )
                        ]) {
                            sh "${bob_aas} remove-installed-secrets"
                        }
                    }
                }
                stage('Cleanup Installed jobs') {
                    steps {
                         sh "${bob_aas} remove-installed-release:remove-installed-jobs"
                    }
                }
                stage('Remove Network Policies') {
                    steps {
                        sh "${bob_aas} remove-network-policies"
                    }
                }
                stage('Pre Deployment Configurations') {
                    steps {
                        sh "${bob_aas} check-certificate-health"
                        withCredentials ([
                            usernamePassword (
                                credentialsId:      env.IDUN_USER_SECRET,
                                usernameVariable:   'IDUN_USER_USERNAME',
                                passwordVariable:   'IDUN_USER_PASSWORD'
                            ),
                            usernamePassword (
                                credentialsId:      env.ADP_DDC_USER_SECRET,
                                usernameVariable:   'ADP_DDC_USER_USERNAME',
                                passwordVariable:   'ADP_DDC_USER_PASSWORD'
                            )
                        ]) {
                            sh "${bob_aas} create-credentials-secrets"
                        }
                    }
                }
            }
        }
    }
    post {
        success{
            cleanWs()
        }
    }
}
