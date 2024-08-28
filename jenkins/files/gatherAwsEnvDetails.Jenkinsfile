#!/usr/bin/env groovy

/* Note:
 *   The following Jenkins configuration is required for this pipeline to work:
 *     A Jenkins slave with the label specified in pipeline.parameters.defaultValue
 */

def bob = "\${WORKSPACE}/ci/bob/bob -r \${WORKSPACE}/ci/jenkins/rulesets/ruleset2.0.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }

    parameters {
        string(
            name:         'SLAVE_LABEL',
            defaultValue: 'IDUN_CICD_ONE_POD_H',
            description:  'The slave label of the node this job will run on'
        )
        string(
            name:        'ENV_NAME',
            description: 'The name of the environment to gather the environment details for',
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
            name:        'BACKUP_PASS_SECRET',
            description: 'Jenkins secret of the password to conncect to the backup service',
            defaultValue: 'none'
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

        stage('Gather Env Details') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.BACKUP_PASS_SECRET, usernameVariable: 'BACKUP_USER', passwordVariable: 'BACKUP_PASS')]) {
                    sh "${bob} verify-folder generate-artifact-properties"
                }
            }
        }

        stage('Archive artifact.properties') {
            steps {
                script {
                    archiveArtifacts 'artifact.properties'
                }
            }
        }
    }
}
