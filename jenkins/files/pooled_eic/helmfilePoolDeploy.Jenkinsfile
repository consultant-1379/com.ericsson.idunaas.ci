#!/usr/bin/env groovy

import com.cloudbees.plugins.credentials.SystemCredentialsProvider;
import com.cloudbees.plugins.credentials.SecretBytes
import com.cloudbees.plugins.credentials.domains.Domain;
import org.jenkinsci.plugins.plaincredentials.impl.FileCredentialsImpl;
import com.cloudbees.plugins.credentials.CredentialsScope;
import java.nio.file.*;     //TODO test if this like is really necessary

// all the imports relate to this function addUpdateSecretFileCredential()
def addUpdateSecretFileCredential(String id, String path_to_file, String description ) {
    def filecontent = readFile path_to_file
    def secretBytes = SecretBytes.fromBytes(filecontent.getBytes())
    def credentials = new FileCredentialsImpl(CredentialsScope.GLOBAL, id, 'description', description, secretBytes)
    SystemCredentialsProvider.instance.store.addCredentials(Domain.global(), credentials)
    println("Successfully uploaded secret file ${id} to Credential Store")
}

def exec(command){
    sh command + " > .ip.tmpfile"
    def loadbalancer_ip = readFile '.ip.tmpfile'
    sh "rm -f .ip.tmpfile"
    return loadbalancer_ip.trim()
}

def getNamespaceName(cluster_name, namespace_number){
    return cluster_name + "-eric-eic-" + namespace_number
}

def getPooledDomainName(cluster_name, namespace_number){
    def dns_suffix = ""
    if(namespace_number == "0")
        dns_suffix = cluster_name + "-eiap"
    else
        dns_suffix = cluster_name + "-x" + namespace_number
    dns_suffix = "pool." + dns_suffix + ".ews.gic.ericsson.se"
    return dns_suffix
}

def getLoadBalancerIpAddress(domain_name){
    return exec("host endpoint.${domain_name} | grep -o '[0-9][0-9]*\\.[0-9][0-9]*\\.[0-9][0-9]*\\.[0-9][0-9]*'")
}

def getBuildName(clusterid, namespace_number, eic_version, enable_tls, tags){
    def build_name = "${BUILD_NUMBER} ${clusterid}-ns-${namespace_number} ${eic_version}"
    if("${enable_tls}" == "true")
        build_name = "${build_name} TLS"
    build_name = "${build_name} ${tags} ${slave_label}"
    return build_name
}


pipeline {
    agent {
        label SLAVE_LABEL
    }
    parameters {
        string(
            name:           'CLUSTER_NAME',
            defaultValue:   'hall144',
            description:    'Cluster name'
        )
        string(
            name:           'NAMESPACE_NUMBER',
            defaultValue:   '0',
            description:    'Number of the namespace to install EIC'
        )
        string(
            name:           'EIC_VERSION',
            defaultValue:   '0.0.0',
            description:    'The version of base platform to install'
        )
        string(
            name:           'TAGS',
            defaultValue:   'adc th dmm appmgr ch eas os pmh',
            description:    'List of tags for applications that have to be deployed, e.g: so adc pf'
        )
        string(
            name:           'ENABLE_TLS',
            defaultValue:   'false',
            description:    'set to "true" to enable mTLS in EIC'
        )
        string(
            name:           'CUSTOM_SITE_VALUES_FILENAME',
            defaultValue:   'NONE',
            description:    'The file will be taken from minio in eic-pooled/site_values_override/<CUSTOM_SITE_VALUES_FILENAME>'
        )
        string(
            name:           'SLAVE_LABEL',
            defaultValue:   'EIAP_CICD',
            description:    'Specify the slave label that you want the job to run on (ususally IDUN_CICD_ONE_POD_H or EIAP_CICD)'
        )
        string(
            name:           'GIT_BRANCH_TO_USE',
            defaultValue:   'master',
            description:    'Put refs/heads/${GIT_BRANCH_TO_USE} in the job configuration for the git branch'
        )
    }
    environment  {
        SHARED_FOLDER       = "../pooled.share"
        INT_CHART_VERSION   = "${EIC_VERSION}"
        NAMESPACE           = getNamespaceName(CLUSTER_NAME, NAMESPACE_NUMBER)
        DOMAIN              = getPooledDomainName(CLUSTER_NAME, NAMESPACE_NUMBER)
        LOADBALANCER_IP     = getLoadBalancerIpAddress(DOMAIN)
        SITE_VALUES         = "${SHARED_FOLDER}/${NAMESPACE}/site_values_${INT_CHART_VERSION}_${NAMESPACE}_${BUILD_NUMBER}.yaml"
        KUBE_CONFIG_FILE    = "${SHARED_FOLDER}/${NAMESPACE}/${CLUSTER_NAME}_kubeconfig"
        KUBECONFIG_SECRET   = "${CLUSTER_NAME}_kubeconfig"
        CERTS_DIR           = "${SHARED_FOLDER}/${NAMESPACE}/certificates"
        MINIO_STS           = "stsoss"
        MINIO_STS_HOST      = "http://minio.stsoss.seli.gic.ericsson.se:9000"
        MINIOCLI            = "${SHARED_FOLDER}/bin/miniocli --config-dir ${SHARED_FOLDER}/.miniocli"
        YQ                  = "${SHARED_FOLDER}/bin/yq"
        CA_CRT_PATH         = "jenkins/scripts/pooled_eic/certs/PhotonCA.crt"
        CA_KEY_PATH         = "jenkins/scripts/pooled_eic/certs/PhotonCA.key"
    }
    stages {
        stage ('Prepare Workspace and Shared folder'){
            steps {
                script{
                    currentBuild.displayName = getBuildName(CLUSTER_NAME, NAMESPACE_NUMBER, INT_CHART_VERSION, ENABLE_TLS, TAGS)
                }

                sh "bash jenkins/scripts/pooled_eic/preliminary_check_for_helmfilePoolDeploy.sh ${SHARED_FOLDER}"

                withCredentials([usernamePassword( credentialsId: 'miniosecret',
                                       usernameVariable: 'MINIO_USR',
                                       passwordVariable: 'MINIO_PSW')]) {
                    sh "${MINIOCLI} alias set ${MINIO_STS} \
                            ${MINIO_STS_HOST} ${MINIO_USR} ${MINIO_PSW}"
                    sh "rm   -rf  ${SHARED_FOLDER}/${NAMESPACE}"
                    sh "mkdir -p  ${SHARED_FOLDER}/${NAMESPACE}"
                }
            }
        }
        stage ('Getting the latest EIC version if 0.0.0 is provided'){
            when{expression {EIC_VERSION == '0.0.0'}}
            steps {
                script{
                    // withCredentials([usernameColonPassword(credentialsId: 'detsuser', variable: 'DETSUSER')]) {
                    withCredentials([usernamePassword( credentialsId: 'detsuser',
                                                       usernameVariable: 'REPO_USR',
                                                       passwordVariable: 'REPO_PSW')]) {
                        INT_CHART_VERSION = exec(
                            "bash jenkins/scripts/pooled_eic/get_latest_eic_version.sh"   +
                                                                " --username ${REPO_USR}" +
                                                                " --password ${REPO_PSW}" )

                        currentBuild.displayName = getBuildName(CLUSTER_NAME, NAMESPACE_NUMBER, INT_CHART_VERSION, ENABLE_TLS, TAGS)
                        SITE_VALUES         = "${SHARED_FOLDER}/${NAMESPACE}/site_values_${INT_CHART_VERSION}_${NAMESPACE}_${BUILD_NUMBER}.yaml"
                    }
                }
            }
        }
        stage ('Get kube_config file from MinIO and update JenkinsSecret'){
            steps {

                sh "${MINIOCLI} cp ${MINIO_STS}/eic-pooled/kubeconfigs/${CLUSTER_NAME}_kubeconfig ${KUBE_CONFIG_FILE}"
                addUpdateSecretFileCredential("${KUBECONFIG_SECRET}", "${KUBE_CONFIG_FILE}",
                    'Kube_Config_Uploaded_by_helmfilePoolDeploy' ) // NOTE: the last string should not contain spaces
            }
        }
        stage ('Generate HTTPS Certificates'){
            steps {
                echo "Generating HTTPS Certificates"
                sh """
                    rm -rf ${CERTS_DIR}
                    mkdir -p ${CERTS_DIR}
                    bash jenkins/scripts/pooled_eic/generate-tls-certs.v2.sh \
                        --dns-domain "${DOMAIN}"  \
                        --ca-crt "${CA_CRT_PATH}" \
                        --ca-key "${CA_KEY_PATH}" \
                        --folder "${CERTS_DIR}"
                    bash jenkins/scripts/pooled_eic/create_new_certs.sh ${CERTS_DIR} --with-enm
                """
                sh "tar cz ${CERTS_DIR} > auto_generated_certs.tar.gz"
                archiveArtifacts    artifacts: 'auto_generated_certs.tar.gz',
                                    allowEmptyArchive: true,
                                    followSymlinks: false
            }
        }
        stage ('Prepare site_values file'){
            steps {
                echo "Preparing site_values file"
                script {
                    def default_site_values = "site-values/idun/ci/template/site-values-latest.yaml"
                    if(CUSTOM_SITE_VALUES_FILENAME == "NONE"){
                        dir ('oss-integration-ci'){
                            git credentialsId: 'detsuser',
                                url: 'ssh://gerrit.ericsson.se:29418/OSS/com.ericsson.oss.aeonic/oss-integration-ci',
                                branch: 'master'
                        }
                        sh "cp oss-integration-ci/${default_site_values} ${SITE_VALUES}"
                    } else {
                        sh "${MINIOCLI} cp ${MINIO_STS}/eic-pooled/site_values_override/${CUSTOM_SITE_VALUES_FILENAME} ${SITE_VALUES}"
                    }

                    if(ENABLE_TLS.toLowerCase() == "true"){
                        def tls = '{"global":{"security":{"tls":{"enabled":true}}}}'
                        sh "${YQ} -P -i '. *= ${tls}' ${SITE_VALUES}"
                    }
                    sh "cp ${SITE_VALUES} ."
                    archiveArtifacts    artifacts: "site_values_*",
                                        allowEmptyArchive: true,
                                        followSymlinks: false
                }
            }
        }
        /*
        stage (''){
            steps {
                echo ""
            }
        }
        */
        stage ('RUNNING EIAP_deploy_helmfile'){
            steps {
                echo "Running install job"
                script{
                    echo "--- Constants used in this job ---"
                    echo "SHARED_FOLDER       =         $SHARED_FOLDER       "
                    echo "MINIO_STS           =         $MINIO_STS           "
                    echo "MINIO_STS_HOST      =         $MINIO_STS_HOST      "
                    echo "MINIOCLI            =         $MINIOCLI            "
                    echo "YQ                  =         $YQ                  "
                    echo "CA_CRT_PATH         =         $CA_CRT_PATH         "
                    echo "CA_KEY_PATH         =         $CA_KEY_PATH         "

                    echo "--- Parameters ---"
                    echo "CLUSTER_NAME                = $CLUSTER_NAME                "
                    echo "NAMESPACE_NUMBER            = $NAMESPACE_NUMBER            "
                    echo "EIC_VERSION                 = $EIC_VERSION                 "
                    echo "TAGS                        = $TAGS                        "
                    echo "ENABLE_TLS                  = $ENABLE_TLS                  "
                    echo "CUSTOM_SITE_VALUES_FILENAME = $CUSTOM_SITE_VALUES_FILENAME "
                    echo "SLAVE_LABEL                 = $SLAVE_LABEL                 "
                    echo "GIT_BRANCH_TO_USE           = $GIT_BRANCH_TO_USE           "

                    echo "--- Calculated values ---"
                    echo "INT_CHART_VERSION   =         $INT_CHART_VERSION   "
                    echo "NAMESPACE           =         $NAMESPACE           "
                    echo "DOMAIN              =         $DOMAIN              "
                    echo "LOADBALANCER_IP     =         $LOADBALANCER_IP     "
                    echo "SITE_VALUES         =         $SITE_VALUES         "
                    echo "KUBE_CONFIG_FILE    =         $KUBE_CONFIG_FILE    "
                    echo "CERTS_DIR           =         $CERTS_DIR           "

                    build job: 'EIC_Pooled_Deployments/EIAP_helmfile_deploy_oss-integration-ci',
                    parameters: [
                        string(name: 'TAGS'                         , value: "${TAGS}"               ),
                        string(name: 'INT_CHART_VERSION'            , value: "${INT_CHART_VERSION}"  ),
                        string(name: 'INT_CHART_REPO'               , value: "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm"  ),
                        string(name: 'ARMDOCKER_USER_SECRET'        , value: "detsuser_docker_config"),
                        string(name: 'HELM_TIMEOUT'                 , value: "5400"                  ),
                        string(name: 'IAM_HOSTNAME'                 , value: "iam.${DOMAIN}"         ),
                        string(name: 'SO_HOSTNAME'                  , value: "so.${DOMAIN}"          ),
                        string(name: 'UDS_HOSTNAME'                 , value: "uds.${DOMAIN}"         ),
                        string(name: 'EIC_HOSTNAME'                 , value: "eic.${DOMAIN}"         ),
                        string(name: 'PF_HOSTNAME'                  , value: "pf.${DOMAIN}"          ),
                        string(name: 'GAS_HOSTNAME'                 , value: "gas.${DOMAIN}"         ),
                        string(name: 'LA_HOSTNAME'                  , value: "la.${DOMAIN}"          ),
                        string(name: 'ML_HOSTNAME'                  , value: "ml.${DOMAIN}"          ),
                        string(name: 'KAFKA_BOOTSTRAP_HOSTNAME'     , value: "bootstrap.${DOMAIN}"   ),
                        string(name: 'ADC_HOSTNAME'                 , value: "adc.${DOMAIN}"         ),
                        string(name: 'APPMGR_HOSTNAME'              , value: "appmgr.${DOMAIN}"      ),
                        string(name: 'OS_HOSTNAME'                  , value: "os.${DOMAIN}"          ),
                        string(name: 'GR_HOSTNAME'                  , value: "gr.${DOMAIN}"          ),
                        string(name: 'TA_HOSTNAME'                  , value: "ta.${DOMAIN}"          ),
                        string(name: 'EAS_HOSTNAME'                 , value: "eas.${DOMAIN}"         ),
                        string(name: 'TH_HOSTNAME'                  , value: "th.${DOMAIN}"          ),
                        string(name: 'CH_HOSTNAME'                  , value: "ch.${DOMAIN}"          ),
                        string(name: 'FULL_PATH_TO_SITE_VALUES_FILE', value: "${SITE_VALUES}"        ),
                        /*
                        string(name: 'PATH_TO_SITE_VALUES_OVERRIDE_FILE', value: "NONE"),
                        */
                        string(name: 'PATH_TO_CERTIFICATES_FILES'   , value: "${CERTS_DIR}"          ),
                        string(name: 'NAMESPACE'                    , value: "${NAMESPACE}"          ),
                        string(name: 'KUBECONFIG_FILE'              , value: "${KUBECONFIG_SECRET}"  ),
                        string(name: 'FUNCTIONAL_USER_SECRET'       , value: "detsuser"              ),
                        string(name: 'SLAVE_LABEL'                  , value: "${SLAVE_LABEL}"        ),
                        string(name: 'CRD_NAMESPACE'                , value: "eric-crd-ns"           ),
                        string(name: 'DEPLOY_ALL_CRDS'              , value: "true"                  ),
                        string(name: 'INGRESS_IP'                   , value: "${LOADBALANCER_IP}"    ),
                        string(name: 'FH_SNMP_ALARM_IP'             , value: "${LOADBALANCER_IP}"    ),
                        string(name: 'COLLECT_LOGS'                 , value: "false"                 ),
                        string(name: 'USE_CERTM'                    , value: "true"                  )
                                ]
                }
            }
        }
        stage ('Cleaning workspace'){
            steps {
                cleanWs()
            }
        }
    }
}


