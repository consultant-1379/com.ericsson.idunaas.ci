#!/usr/bin/env groovy

/* Note:
 *   The following Jenkins configuration is required for this pipeline to work:
 *     A Jenkins slave with the label specified in pipeline.parameters.defaultValue
 */

// imports


import com.cloudbees.plugins.credentials.SystemCredentialsProvider;
import com.cloudbees.plugins.credentials.SecretBytes
import com.cloudbees.plugins.credentials.domains.Domain;
import org.jenkinsci.plugins.plaincredentials.impl.FileCredentialsImpl;
import com.cloudbees.plugins.credentials.CredentialsScope;
import java.nio.file.*;

def addUpdateSecretFileCredential(String id, String path_to_file, String description ) {

    def filecontent = readFile path_to_file
    def secretBytes = SecretBytes.fromBytes(filecontent.getBytes())
    def credentials = new FileCredentialsImpl(CredentialsScope.GLOBAL, id, 'description', description, secretBytes)
    SystemCredentialsProvider.instance.store.addCredentials(Domain.global(), credentials)
    println("Successfully uploaded secret file ${id} to Credential Store")

}

@Library('aas-muon-utils-lib') _
def bob = "\${WORKSPACE}/ci/bob/bob  -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }

    parameters {
        string(
            name:        'FUNCTIONAL_USER_SECRET',
            description: 'Jenkins secret ID for Armdocker credentials',
            defaultValue: 'none'
        )
        string(
            name:        'ARMDOCKER_USER_SECRET',
            description: 'The Armdocker user secret',
            defaultValue: 'none'
        )
        string(
            name:         'JENKINS_USER',
            description:  'Jenkins user (used to mount Docker credentials to container)',
            defaultValue: 'none'
        )
        string(
            name:         'SLAVE_LABEL',
            defaultValue: 'IDUN_CICD_ONE_POD_H',
            description:  'The slave label of the node this job will run on'
        )
        string(
            name:        'ENV_NAME',
            description: 'The name of the environment to setup',
            defaultValue: 'none'
        )
        string(
            name:        'AWS_REGION',
            description: 'The AWS region to setup the cluster in',
            defaultValue: 'none'
        )
        string(
            name:        'K8S_VERSION',
            description: 'The Kubernetes version to install on the cluster',
            defaultValue: 'none'
        )
        string(
            name:        'VPC_ID',
            description: 'The ID of the VPC where the cluster will be deployed',
            defaultValue: 'none'
        )
        string(
            name:        'CONTROL_PLANE_SUBNET_IDS',
            description: 'The subnet IDs for the EKS control plane',
            defaultValue: 'none'
        )
        string(
            name:        'WORKER_NODE_SUBNET_ID',
            description: 'The subnet ID for the EKS worker nodes',
            defaultValue: 'none'
        )
        string(
            name:        'SECONDARY_VPC_CIDR',
            description: 'The secondary CIDR block for the VPC',
            defaultValue: 'none'
        )
        string(
            name:        'NODE_INSTANCE_TYPE',
            description: 'The instance type of the EKS worker nodes',
            defaultValue: 'none'
        )
        string(
            name:        'DISK_SIZE',
            description: 'The disk size for the deployment',
            defaultValue: 'none'
        )
        string(
            name:        'MIN_NODES',
            description: 'The minimum number of nodes in the cluster',
            defaultValue: 'none'
        )
        string(
            name:        'MAX_NODES',
            description: 'The maximum number of nodes in the cluster',
            defaultValue: 'none'
        )
        string(
            name:        'SSH_KEYPAIR_NAME',
            description: 'The name of the SSH keypair for the instance',
            defaultValue: 'none'
        )
        string(
            name:        'PRIVATE_DN',
            description: 'The private domain name for the deployment',
            defaultValue: 'none'
        )
        string(
            name:        'KUBEDOWNSCALER',
            description: 'Choose whether to install Kubedownscaler on the EKS cluster',
            defaultValue: 'none'
        )
        string(
            name:        'IAM_HOSTNAME',
            description: 'FQDN for the IAM service',
            defaultValue: 'none'
        )
        string(
            name:        'PF_HOSTNAME',
            description: 'FQDN for the PF service',
            defaultValue: 'none'
        )
        string(
            name:        'SO_HOSTNAME',
            description: 'FQDN for the SO service',
            defaultValue: 'none'
        )
        string(
            name:        'UDS_HOSTNAME',
            description: 'FQDN for the UDS service',
            defaultValue: 'none'
        )
        string(
            name:        'GAS_HOSTNAME',
            description: 'FQDN for the GAS service',
            defaultValue: 'none'
        )
        string(
            name:        'ADC_HOSTNAME',
            description: 'FQDN for the ADC service',
            defaultValue: 'none'
        )
        string(
            name:        'APPMGR_HOSTNAME',
            description: 'FQDN for the APPMGR service',
            defaultValue: 'none'
        )
        string(
            name:        'OS_HOSTNAME',
            description: 'FQDN for the OS service',
            defaultValue: 'none'
        )
        string(
            name:        'DISABLEPUBLICACCESS',
            description: 'Environment connected to ECN should be True, else False',
            defaultValue: 'none'
        )
        string(
            name:         'BACKUP_INSTANCE_TYPE',
            description:  'Instance type of backup server',
            defaultValue: 'none'
        )
        string(
            name:        'BACKUP_AMI_ID',
            description: 'AMI ID that will be used to spin up backup server',
            defaultValue: 'none'
        )
        string(
            name:        'BACKUP_DISK',
            description: 'Disk size where export backup files will be stored',
            defaultValue: 'none'
        )
        string(
            name:        'BACKUP_PASS',
            description: 'Pass Key that will be used to login on backup server',
            defaultValue: 'none'
        )
        string(
            name:        'SKIP_BACKUP_SERVER_CREATION',
            description: 'If this is equal to "true" it will skip the creation of backup server',
            defaultValue: 'none'
        )
        string(
            name:        'NAMESPACE',
            description: 'Namespace on the cluster where EIAP is installed into.'
        )
        string(
            name:        'PROMETHEUS_HOSTNAME',
            description: 'Hostname for the monitoring service (prometheus): e.g. monitoring.domain.ericsson.se',
            defaultValue: 'none'
        )
        string(
            name:        'DASHBOARD_HOSTNAME',
            description: 'Hostname for the k8s dashboard: e.g. dashboard.domain.ericsson.se',
            defaultValue: 'none'
        )
        string(
            name:         'PLATFORM_TYPE',
            defaultValue: 'aws',
            description:  'Cloud provider type'
        )
    }
    environment {
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
        DOCKER_FLAGS            = utils.getDockerFlags()
    }
    stages {
        stage('Prepare Workdir') {
            steps {
                dir('ci'){
                    sh 'git submodule update --init bob'
                    sh "${bob} git-clean"
                    sh 'git submodule sync'
                    sh 'git submodule update --init --recursive --remote'
                }
            }
        }
        stage('Generate config') {
            steps {
                echo "Start generating config.yaml"
                sh "${bob} generate-config"
                echo "Finished generating config.yaml"
            }
            post {
                success {
                    script {
                        archiveArtifacts "ci/deployments/${env.ENV_NAME}/workdir/config.yaml"
                    }
                }
            }
        }
        stage('Install Cluster') {
            steps {
                echo "Starting to provision cluster"
                sh "${bob} verify-config"
                withCredentials([
                    usernamePassword(credentialsId: env.FUNCTIONAL_USER_SECRET,
                    usernameVariable: 'FUNCTIONAL_USER_USERNAME', passwordVariable: 'FUNCTIONAL_USER_PASSWORD'),
                    file(credentialsId: params.ARMDOCKER_USER_SECRET, variable: 'DOCKERCONFIG')]){
                        sh "install -m 600 ${DOCKERCONFIG} ${HOME}/.docker/config.json"
                        sh "${bob} install-cluster"
                }
                echo "Finished install cluster"
            }
        }

        stage('Configure Cluster') {
            steps {
                echo "Starting to configure cluster"
                sh "${bob} configure-cluster"
                echo "Cluster configuration complete"
            }
        }
        stage('Configure Backup Server') {
            when {
                not {
                    environment ignoreCase: true, name: 'SKIP_BACKUP_SERVER_CREATION', value: 'true'
                }
            }
            steps {
                echo "Starting to create and configure backup server"
                sh "${bob} configure-backup-server:configure-backup-server"
                echo "Backup server creation and configuration completed"
            }
        }

    }
    post {
        always {
            echo "Fix ownership: Some files has been created with wrong ownership (root)"
            sh "${bob} fix-ownership"
            echo "Fix ownership completed"
        }
        success {
            echo "Uploading generated kube config to Jenkins Credential Store"
            sh "${bob} kube_config"
            addUpdateSecretFileCredential("${ENV_NAME}_kubeconfig","${env.WORKSPACE}/ci/deployments/${env.ENV_NAME}/workdir/config",'Kube_Config_Uploaded_by_SETUP_EKS_Cluster_JOB' ) // NOTE: the last string should not contain spaces
        }
    }
}
