#!/usr/bin/env groovy
@Library('aas-muon-utils-lib@eiap_pooled_deployments') _
def bob = "bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0_pooled.yaml"

pipeline {
    agent {
        kubernetes {
            yamlFile 'jenkins/scripts/pooled_eic/templates/jnlpCiUtilsPod.yaml'
            defaultContainer 'outer-ci-utils-container'
        }
    }
    parameters {
        string (
            name:           'PLATFORM_TYPE',
            defaultValue:   'pooled',
            description:    'Cloud provider type'
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
            name:           'INT_CHART_REPO',
            defaultValue:   'https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm',
            description:    'Integration Chart Repo'
        )
        string (
            name:           'DEPLOYMENT_TYPE',
            defaultValue:   'install',
            description:    'Deployment Type, set \"install\" or \"upgrade\"'
        )
        string (
            name:            'DEPLOYMENT_MANAGER_DOCKER_IMAGE',
            defaultValue:    'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:latest',
            description:     'The full image url and tag for the deployment manager to use for the deployment. If the tag is set to default the deployment manager details will be fetched from the dm_version.yaml file from within the helmfile tar file under test'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            defaultValue:   'detsuser_docker_config',
            description:    'ARM Docker secret'
        )
        string (
            name:           'HELM_TIMEOUT',
            defaultValue:   '5400',
            description:    'Time in seconds for the Deployment Manager to wait for the deployment to execute, default 1800'
        )
        string (
            name:           'DOCKER_TIMEOUT',
            defaultValue:   '60',
            description:    'Time in seconds for the Deployment Manager to wait for the pulling of docker images to be used for deployment'
        )
        string (
            name:           'TAGS',
            defaultValue:   'so pf uds adc th dmm eas',
            description:    'List of tags for applications that have to be deployed, e.g: so adc pf'
        )
        string (
            name:           'LA_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Log Aggregator'
        )
        string(
            name:           'KAFKA_BOOTSTRAP_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Kafka Bootstrap'
        )
        string (
            name:           'IAM_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for IAM'
        )
        string (
            name:           'SO_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for SO'
        )
        string (
            name:           'UDS_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for UDS'
        )
        string (
            name:           'PF_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for PF'
        )
        string (
            name:           'GAS_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for GAS'
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
            name:           'CH_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Configuration Handling'
        )
        string (
            name:           'TH_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Topology Handling'
        )
        string (
            name:           'OS_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Oran Support'
        )
        string (
            name:           'VNFM_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for EO EVNFM'
        )
        string (
            name:           'VNFM_REGISTRY_HOSTNAME',
            defaultValue:   'default',
            description:    'Registry Hostname for EO EVNFM'
        )
        string (
            name:           'GR_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for EO GR'
        )
        string (
            name:           'ML_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Machine Learning(ML) Application'
        )
        string (
            name:           'BDR_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Bulk Data Repository (BDR) Application'
        )
        string (
            name:           'AVIZ_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for Assurance Visualization Application'
        )
        string (
            name:           'EO_CM_HOSTNAME',
            defaultValue:   'default',
            description:    'EO_CM_HOSTNAME'
        )
        string (
            name:           'HELM_REGISTRY_HOSTNAME',
            defaultValue:   'default',
            description:    'Hostname for EO HELM Registry'
        )
        string (
            name:           'VNFLCM_SERVICE_DEPLOY',
            defaultValue:   'false',
            description:    'EO VM VNFM Deploy, set \"true\" or \"false\"'
        )
        string (
            name:           'HELM_REGISTRY_DEPLOY',
            defaultValue:   'false',
            description:    'EO HELM Registry Deploy, set \"true\" or \"false\"'
        )
        string (
            name:           'IDUN_USER_SECRET',
            defaultValue:   'idun_credentials',
            description:    'Jenkins secret ID for default IDUN user password'
        )
        string (
            name:           'PATH_TO_CERTIFICATES_FILES',
            description:    'Path within minio to the location of the certificates directory, for example hall118/certificates/hall118-x3',
            trim:           true
        )
        string (
            name:           'FULL_PATH_TO_SITE_VALUES_FILE',
            defaultValue:   'oss-integration-ci/site-values/idun/ci/template/site-values-latest.yaml',
            description:    'Full path within the com.ericsson.idunaas.ci repo to the site-values-latest.yaml or the site-values-latest-tls.yaml file, for example, site-values/idun/ci/template/site-values-latest.yaml'
        )
        string (
            name:           'PATH_TO_SITE_VALUES_OVERRIDE_FILE',
            defaultValue:   'NONE',
            description:    'Name of the site values override file to be use if required. The name of the file you supplied will be pre-appended with the path which is minio/eic-pooled/site_values_override/'
        )
        string (
            name:           'TLS_ENABLED',
            defaultValue:   'false',
            description:    'Enabling TLS for the install',
            trim:           true
        )
        string (
            name:           'NAMESPACE',
            description:    'Namespace to install the Chart'
        )
        string (
            name:           'SELECTED_CLUSTER_ID',
            defaultValue:   'hall133',
            description:    'CLuster name used to download correct kubeconfig from Minio for the environment to purge.'
        )
        string (
            name:           'FUNCTIONAL_USER_SECRET',
            defaultValue:   '3079dee4-a7d0-4a8e-b03e-7615bad7d6ec',
            description:    'Jenkins secret ID for ARM Registry Credentials'
        )
        string (
            name:           'DOCKER_REGISTRY',
            defaultValue:   'armdocker.rnd.ericsson.se',
            description:    'Set this to the docker registry to execute the deployment from. Used when deploying from Officially Released CSARs'
        )
        string (
            name:           'DOCKER_REGISTRY_CREDENTIALS',
            defaultValue:   'None',
            description:    'Jenkins secret ID for the Docker Registry. Not needed if deploying from armdocker.rnd.ericsson.se'
        )
        string (
            name:           'CRD_NAMESPACE',
            defaultValue:   'eric-crd-ns',
            description:    'Namespace which was used to deploy the CRD'
        )
        string (
            name:           'IPV6_ENABLE',
            defaultValue:   'false',
            description:    'Used to enable IPV6 within the site values file when set to true'
        )
        string (
            name:           'INGRESS_IP',
            defaultValue:   'default',
            description:    'INGRESS IP'
        )
        string (
            name:           'INGRESS_CLASS',
            defaultValue:   'default',
            description:    'ICCR ingress class name'
        )
        string (
            name:           'VNFLCM_SERVICE_IP',
            defaultValue:   '0.0.0.0',
            description:    'LB IP for the VNF LCM service'
        )
        string (
            name:           'EO_CM_IP',
            defaultValue:   'default',
            description:    'EO CM IP'
        )
        string (
            name:           'EO_CM_ESA_IP',
            defaultValue:   'default',
            description:    'EO CM ESA IP'
        )
        string (
            name:           'FH_SNMP_ALARM_IP',
            defaultValue:   'default',
            description:    'LB IP for FH SNMP Alarm Provider'
        )
        string (
            name:           'USE_DM_PREPARE',
            defaultValue:   'false',
            description:    'Set to true to use the Deploymet Manager function \"prepare\" to generate the site values file'
        )
        string (
            name:           'USE_SKIP_IMAGE_PUSH',
            defaultValue:   'false',
            description:    'Set to true to use the Deployment Manager parameter "--skip-image-check-push" in case an image push is done in advance. If false will deploy without the "--skip-image-check-push" parameter'
        )
        string (
            name:           'USE_SKIP_UPGRADE_FOR_UNCHANGED_RELEASES',
            defaultValue:   'false',
            description:    'Set to true to use the Deployment Manager parameter "--skip-upgrade-for-unchanged-releases" to skip helm upgrades for helm releases whose versions and values have not changed. If false will deploy without the "--skip-upgrade-for-unchanged-releases" parameter'
        )
        string (
            name:           'COLLECT_LOGS',
            defaultValue:   'true',
            description:    'If set to "true" (by default) - logs will be collected. If false - will not collect logs.'
        )
        string (
            name:           'COLLECT_LOGS_WITH_DM',
            defaultValue:   'false',
            description:    'If set to "false" (by default) - logs will be collected by ADP logs collection script. If true - with deployment-manager tool.'
        )
        string (
            name:           'DDP_AUTO_UPLOAD',
            defaultValue:   'false',
            description:    'Set it to true when enabling the DDP auto upload and also need to add the DDP instance details into ENV_CONFIG_FILE and SITE_VALUES_OVERRIDE_FILE'
        )
        string (
            name:           'CI_DOCKER_IMAGE',
            defaultValue:   'armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-scripts:default',
            description:    'CI Docker image to use. Mainly used in CI Testing flows'
        )
        string (
            name:           'MINIO_USER_SECRET_ID',
            defaultValue:   'miniosecret',
            description:    'Minio user secret which is accessed via Jenkins credentials secret id'
        )
        string (
            name:           'VERBOSITY',
            defaultValue:   '3',
            description:    'Verbosity can be from 0 to 4. Default is 3. Set to 4 if debug needed'
        )
        string(
            name: 'USE_CERTM',
            defaultValue: 'false',
            description: 'Set to true to use the "--use-certm" tag during the deployment'
        )
    }
    options {
        timestamps()
        timeout(time: 2, unit: 'HOURS')
        durabilityHint 'PERFORMANCE_OPTIMIZED'
    }
    environment {
        BUILD_INFO                          = "${env.BUILD_NUMBER}-${params.NAMESPACE}-${params.SELECTED_CLUSTER_ID}"
        DOCKER_FLAGS_NO_DOCKER_CONF         = utils.getDockerFlagsNoDockerConfig()
        DOCKER_FLAGS                        = utils.getDockerFlags()
        DOCKER_FLAGS_DEPLOYMENT_MANAGER     = utils.getDeploymentManagerFlags()
        USE_TAGS                            = 'true'
        STATE_VALUES_FILE                   = "site_values_${params.INT_CHART_VERSION}.yaml"
        PATH_TO_HELMFILE                    = "${params.INT_CHART_NAME}/helmfile.yaml"
        CSAR_STORAGE_INSTANCE               = 'arm.seli.gic.ericsson.se'
        CSAR_STORAGE_REPO                   = 'proj-eric-oss-drop-generic-local'
        FETCH_CHARTS                        = 'true'
        HELMFILE_CHART_NAME                 = "${params.INT_CHART_NAME}"
        HELMFILE_CHART_VERSION              = "${params.INT_CHART_VERSION}"
        HELMFILE_CHART_REPO                 = "${params.INT_CHART_REPO}"
    }
    stages {
        stage('Set Build Description') {
            steps {
                script {
                    echo "==== Checkout Repo ===="
                    currentBuild.displayName = "${env.BUILD_INFO}"
                }
            }
        }
        stage('Checkout Additional Repos') {
            stages {
                stage('Checkout oss-integration-ci repo') {
                    steps {
                        echo "==== Checkout oss-integration-ci repo ===="
                        checkout([
                            $class: 'GitSCM', branches: [[name: 'master']],
                            extensions: [
                                [$class: 'CheckoutOption', timeout: 5],
                                [$class: 'CloneOption', honorRefspec: true, noTags: false, reference: '', shallow: false, timeout: 5],
                                [$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: true, recursiveSubmodules: true, reference: '', trackingSubmodules: true],
                                [$class: 'RelativeTargetDirectory', relativeTargetDir: 'oss-integration-ci']
                            ],
                            gitTool: 'Default',
                            userRemoteConfigs: [[credentialsId: 'detsuser', url: 'https://gerrit.ericsson.se/a/OSS/com.ericsson.oss.aeonic/oss-integration-ci']]
                        ])
                    }
                }
            }
        }
        stage('Set Ci Docker Image Version') {
            steps {
                echo "==== Set Ci Docker Image Version ===="
                script {
                    env.CI_DOCKER_IMAGE = get_ci_docker_image_url("${params.CI_DOCKER_IMAGE}")
                }
            }
        }
        stage('Install docker config file to root location') {
            steps {
                echo "==== Install docker config File to root location ===="
                withCredentials ([
                    file (
                        credentialsId:  params.ARMDOCKER_USER_SECRET,
                        variable:       'DOCKERCONFIG'
                    )
                ]) {
                    sh "${bob} pooled-deployment:install-docker-config-to-root-location"
                }
            }
        }
        stage('Set Cluster name to bob variable') {
            steps {
                echo "==== Set Cluster name to bob variable ===="
                   sh "${bob} pooled-deployment:set-selected-cluster-id"
            }
        }
        stage('Retrieve kube config file from MiniIO') {
            steps {
                echo "==== Retrieve kube config file from MiniIO ===="
                withCredentials ([
                    usernameColonPassword (
                        credentialsId:  env.MINIO_USER_SECRET_ID,
                        variable:       'MINIO_CREDS'
                    )
                ]) {
                        script {
                        env.MINIO_FLAGS_NO_DOCKER_CONF  = utils.getMinioFlagsNoDockerConfig()
                        sh "${bob} pooled-deployment:retrieve-kubeconfig-from-minio"
                        }
                }
            }
        }
        stage('Retrieve site-values-override file from MiniIO') {
             when {
                not {
                    environment ignoreCase: true, name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE', value: 'NONE'
                }
            }
            steps {
                container('outer-ci-utils-container') {
                    echo "==== site-values-ovveride file from MiniIO ===="
                    withCredentials ([
                        usernameColonPassword (
                            credentialsId:  env.MINIO_USER_SECRET_ID,
                            variable:       'MINIO_CREDS'
                        )
                    ]) {
                         script {
                            env.MINIO_FLAGS_NO_DOCKER_CONF  = utils.getMinioFlagsNoDockerConfig()
                            sh "${bob} pooled-deployment:retrieve-site-values-override-from-minio"
                         }
                    }
                }
            }
        }
        stage('Install kube config file to default and admin locations') {
            steps {
                echo "==== Install kube config file to default and admin locations ===="
                sh "${bob} pooled-deployment:install-kubeconfig-admin-location"
                sh "${bob} pooled-deployment:install-kubeconfig-default-location"
            }
        }
        stage('Get cluster certificates from Minio') {
            steps {
                echo "==== Get cluster certificates from Minio ===="
                withCredentials ([
                    usernameColonPassword (
                        credentialsId:  env.MINIO_USER_SECRET_ID,
                        variable:       'MINIO_CREDS'
                    )
                ]) {
                    sh "${bob} pooled-deployment:get-from-minio-cluster-certificates"
                    sh "${bob} pooled-deployment:verify-cluster-certificates"
                }
            }
        }
        stage('Get Helmfile') {
            steps {
                echo "==== Get Helmfile ===="
                withCredentials ([
                    usernamePassword (
                        credentialsId:      params.FUNCTIONAL_USER_SECRET,
                        usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                        passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob} pooled-deployment:fetch-helmfile"
                }
            }
        }
        stage('Set Deployment Manager Version') {
            steps {
                echo "==== Set Deployment Manager Version ===="
                sh "${bob} pooled-deployment:extract-helmfile"
                sh "${bob} pooled-deployment:get-dm-full-url-version"
                script {
                    env.DEPLOYMENT_MANAGER_DOCKER_IMAGE = sh (
                        script: "cat IMAGE_DETAILS.txt | grep ^IMAGE | sed 's/.*=//'",
                        returnStdout: true
                    ).trim()
                }
            }
        }
        stage('Prepare Working Directory') {
            steps {
                echo "==== Prepare Working Directory ===="
                sh "${bob} pooled-deployment:untar-and-copy-helmfile-to-workdir"
                sh "${bob} pooled-deployment:fetch-site-values"
            }
        }
        stage('Update Global Registry within Site Values') {
            steps {
                echo "==== Update Global Registry within Site Values ===="
                withCredentials ([
                    usernamePassword (
                        credentialsId:      params.FUNCTIONAL_USER_SECRET,
                        usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                        passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob} pooled-deployment:substitute-global-registry-details"
                }
            }
        }
        stage('Enable TLS if Required') {
            when { environment ignoreCase: true, name: 'TLS_ENABLED', value: 'true' }
            steps {
                sh "${bob} pooled-deployment:enable-tls"
            }
        }
        stage('Update Site Values') {
            steps {
                echo "==== Update Site Values ===="
                withCredentials ([
                    usernamePassword (
                        credentialsId:      params.FUNCTIONAL_USER_SECRET,
                        usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                        passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob} pooled-deployment:substitute-ipv6-enable"
                    sh "${bob} pooled-deployment:substitute-application-hosts"
                    sh "${bob} pooled-deployment:substitute-application-deployment-option"
                    sh "${bob} pooled-deployment:substitute-application-service-option"
                    sh "${bob} pooled-deployment:update-user-details"
                    sh "${bob} pooled-deployment:populate-default-registry-credentials"
                }
            }
        }
        stage('Build CSARs') {
            steps {
                echo "==== Build CSARs ===="
                sh "${bob} pooled-deployment:get-release-details-from-helmfile"
                sh "${bob} pooled-deployment:helmfile-charts-mini-csar-build"
                sh "${bob} pooled-deployment:cleanup-charts-mini-csar-build"
            }
        }
        stage('Pre Deployment Manager Configuration') {
            stages {
                stage('Deployment Manager Init') {
                    steps {
                        echo "==== Pre Deployment Manager Configuration ===="
                        sh "${bob} pooled-deployment:deployment-manager-init"
                    }
                }
                stage ('Copy Certs old way') {
                    when {
                        environment ignoreCase: true, name: 'USE_CERTM', value: 'false'
                    }
                    steps {
                        echo "==== Copy Certs ===="
                        sh "${bob} pooled-deployment:copy-certificate-files"
                    }
                }
                stage ('Copy Certs for certm') {
                    when {
                        environment ignoreCase: true, name: 'USE_CERTM', value: 'true'
                    }
                    steps {
                        echo "==== Copy Certs for certm ===="
                        sh "${bob} pooled-deployment:copy-certificates-files-for-certm"
                        sh "${bob} pooled-deployment:copy-certificate-files"
                    }
                }
                stage('Prepare Site Values using DM') {
                    when {
                        environment ignoreCase: true, name: 'USE_DM_PREPARE', value: 'true'
                    }
                    steps {
                        echo "==== Prepare Site Values using DM ===="
                        script {
                            sh "${bob} pooled-deployment:rename-ci-site-values"
                            sh "${bob} pooled-deployment:deployment-manager-prepare"
                            sh "${bob} pooled-deployment:populate-prepare-dm-site-values"
                        }
                    }
                }
            }
            post {
                failure {
                    archiveArtifacts allowEmptyArchive: true, artifacts: "logs/*", fingerprint: true
                }
            }
        }
        stage('Override Site Values') {
            when {
                not {
                    environment ignoreCase: true, name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE', value: 'NONE'
                }
            }
            steps {
                echo "==== Override Site Values ===="
                sh "${bob} pooled-deployment:override-site-values"
            }
        }
        stage('Update Site Values after Override') {
            steps {
                container('outer-ci-utils-container') {
                    echo "==== Update Site Values after Override ===="
                    withCredentials ([
                        usernamePassword (
                            credentialsId:      params.FUNCTIONAL_USER_SECRET,
                            usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                            passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                        )
                    ]) {
                        sh "${bob} pooled-deployment:substitute-ipv6-enable"
                        sh "${bob} pooled-deployment:substitute-application-hosts"
                        sh "${bob} pooled-deployment:substitute-application-deployment-option"
                        sh "${bob} pooled-deployment:substitute-application-service-option"
                    }
                }
            }
        }
        stage('Update Site Values with DDP details') {
            steps {
                container('outer-ci-utils-container') {
                    echo "==== Update Site Values with DDP details ===="
                    withCredentials ([
                        usernamePassword (
                            credentialsId:      params.FUNCTIONAL_USER_SECRET,
                            usernameVariable:   'FUNCTIONAL_USER_USERNAME',
                            passwordVariable:   'FUNCTIONAL_USER_PASSWORD'
                        )
                    ]) {
                        sh "${bob} pooled-deployment:substitute-ddp-details"
                    }
                }
            }
        }
        stage ('Helmfile Deployment') {
            stages {
                stage ('Pre-Deployment Helmfile') {
                    steps {
                        echo "==== Update Site Values with DDP details ===="
                        sh "${bob} pooled-deployment:remove-local-repositories-yaml"
                        sh "${bob} pooled-deployment:print-dm-version"
                        sh "${bob} pooled-deployment:archive-dm-version"
                        sh "${bob} pooled-deployment:set-skip-image-push-parameter"
                        sh "${bob} pooled-deployment:set-skip-upgrade-for-unchanged-releases-parameter"
                        sh "${bob} pooled-deployment:set-use-certm-parameter"
                    }
                }
                stage('Deploy Helmfile') {
                    steps {
                        sh "${bob} pooled-deployment:deploy-helmfile"
                    }
                    post {
                        success {
                            sh "${bob} pooled-deployment:parse-deployment-log"
                        }
                        failure {
                            script {
                                if (params.COLLECT_LOGS.toLowerCase() == "true") {
                                    if (params.COLLECT_LOGS_WITH_DM.toLowerCase() == "true") {
                                        sh "${bob} pooled-deployment:gather-deployment-manager-logs || true"
                                    }
                                    else {
                                        sh "${bob} pooled-deployment:gather-adp-k8s-logs || true"
                                    }
                                }
                            }
                        }
                    }
                }
            }
            post {
                always {
                    sh "${bob} pooled-deployment:override-functional-password"
                }
            }
        }
    }
    post {
        always {
            sh "printenv | sort"
            archiveArtifacts allowEmptyArchive: true, artifacts: "artifact.properties, logs_*.tgz, logs/*, ci-script-executor-logs/*, ci_${env.STATE_VALUES_FILE}, ${env.STATE_VALUES_FILE}", fingerprint: true
        }
    }
}

def get_ci_docker_image_url(ci_docker_image) {
    String latest_ci_version = readFile "oss-integration-ci/VERSION_PREFIX"
    String trimmed_ci_version = latest_ci_version.trim()
    url = ci_docker_image.split(':');
    return url[0] + ":" + trimmed_ci_version;
}
