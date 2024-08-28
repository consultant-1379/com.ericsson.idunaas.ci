#!/usr/bin/env groovy

/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 * - Credentials Plugin should be installed and have the secrets with the following names:
 * - pipeline changed to use bob rule for git clean
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
            name:           'TAGS',
            defaultValue:   'so pf uds adc th dmm eas',
            description:    'List of tags for applications that have to be deployed, e.g: so adc pf'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            description:    'ARM Docker secret'
        )
        string (
            name:           'IAM_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for IAM'
        )
        string (
            name:           'PF_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for PF'
        )
        string (
            name:           'SO_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for SO'
        )
        string (
            name:           'GAS_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for GAS'
        )
        string (
            name:           'UDS_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for UDS'
        )
        string (
            name:           'ADC_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for ADC'
        )
        string (
            name:           'APPMGR_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Application Manager'
        )
        string (
            name:           'OS_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Oran Support'
        )
        string (
            name:           'GR_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for EO GR'
        )
        string (
            name:           'TA_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Task Automation'
        )
        string (
            name:           'EAS_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Ericsson Adaptation Support'
        )
        string (
            name:           'TH_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Topology Handling'
        )
        string (
            name:           'CH_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Configuration Handling'
        )
        string (
            name:           'DOCKER_REGISTRY',
            defaultValue:   'armdocker.rnd.ericsson.se',
            description:    'Set this to the docker registry to execute the deployment from. Used when deploying from Officially Released CSARs'
        )
        string (
            name:           'PATH_TO_AWS_FILES',
            description:    'Path within the Repo to the location of the AWS credentials and config directory'
        )
        string (
            name:           'INT_CHART_REPO',
            defaultValue:   'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
            description:    'Integration Chart Repo'
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
            name:           'KUBECONFIG_FILE',
            description:    'Jenkins credential id for kubectl configuration file which is a credential type of secret file (i.e. ossautoapp01_kubeconfig).'
        )
        string (
            name:           'FUNCTIONAL_USER_SECRET',
            defaultValue:   'ossadmin-creds',
            description:    'Jenkins secret ID for ARM Registry Credentials'
        )
        string (
            name:           'AWS_ECR_URL',
            description:    'Specify the AWS Elastic Container Registry URL'
        )
        string (
            name:           'INT_CHART_VERSION',
            description:    'The version of base platform to install'
        )
        string (
            name:           'INT_CHART_NAME',
            description:    'Chart Name for helmfile'
        )
        string (
            name:           'AWS_REGION',
            description:    'The region where AWS account exist'
        )
        string (
            name:           'HELM_REPOSITORY_NAME',
            defaultValue:   'proj-eric-oss-drop-helm',
            description:    'Helm Chart Repository name'
        )
        string (
            name:           'PATH_TO_WORKDIR',
            description:    'Specify the Path to workdir in deployments'
        )
        string (
             name:          'IPV6_ENABLE',
             defaultValue:  'false',
             description:   'Used to enable IPV6 within the site values file when set to true'
        )
        string (
            name:           'DDP_AUTO_UPLOAD',
            defaultValue:   'false',
            description:    'Set it to true when enabling the DDP auto upload and also need to add the DDP instance details into ENV_CONFIG_FILE and SITE_VALUES_OVERRIDE_FILE'
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
        FETCH_CHARTS                = 'true'
        SUB_MODULE_PATH             = 'com.ericsson.idunaas.ci/'
        PATH_TO_HELMFILE            = "${params.INT_CHART_NAME}/helmfile.yaml"
        STATE_VALUES_FILE           = "site_values_${params.INT_CHART_VERSION}.yaml"
        HELMFILE_CHART_REPO         = "${params.INT_CHART_REPO}"
        HELMFILE_CHART_NAME         = "${params.INT_CHART_NAME}"
        HELMFILE_CHART_VERSION      = "${params.INT_CHART_VERSION}"
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
                sh "${bob_aas} prepare-workdir:copy-aws-credentials"
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
        stage('Fetch Site Values File') {
            steps {
                sh "${bob_oss} fetch-site-values"
            }
        }
        stage('Override Site Values') {
            steps {
                sh "${bob_oss} override-site-values:override-site-values"
            }
        }
        stage('Update Site Values') {
            steps {
                withCredentials ([
                    usernamePassword (
                        credentialsId:      env.FUNCTIONAL_USER_SECRET,
                        usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                        passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob_aas} update-site-values:substitute-registry-details"
                }
            }
        }
        stage('Update IpV6 Option') {
            steps {
                sh "${bob_oss} update-site-values:substitute-ipv6-enable"
            }
        }
        stage('Update Application Hosts') {
            steps {
                sh "${bob_aas} update-site-values:substitute-application-hosts"
            }
        }
        stage('Update Application Deployment Option') {
            steps {
                sh "${bob_oss} update-site-values:substitute-application-deployment-option"
            }
        }
        stage('Update Repositories File') {
            steps {
                withCredentials ([
                    usernamePassword (
                        credentialsId:      params.FUNCTIONAL_USER_SECRET,
                        usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                        passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob_oss} update-repositories-file"
                }
            }
        }
        stage('Update DDP details') {
            steps {
                withCredentials ([
                    usernamePassword (
                        credentialsId:      params.FUNCTIONAL_USER_SECRET,
                        usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                        passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob_oss} update-site-values:substitute-ddp-details"
                }
            }
        }
        stage('Get Release Details from Helmfile') {
            steps {
                sh "${bob_oss} get-release-details-from-helmfile"
            }
        }
        stage('Build CSARs') {
            steps {
                sh "${bob_oss} helmfile-charts-mini-csar-build"
            }
        }
        stage('Create Optionality File') {
            steps {
                sh "${bob_aas} create-optionality-file"
            }
        }
        stage('Push IDUN docker images to ECR') {
            steps {
                sh "${bob_aas} do-push-images-ecr"
            }
        }
    }
    post {
        success {
            archiveArtifacts "eric-eiae-helmfile/optionality.yaml"
        }
    }
}
