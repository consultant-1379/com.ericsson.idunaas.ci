#!/usr/bin/env groovy
@Library('aas-muon-utils-lib') _
def bob = "bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0_pooled_from_slave.yaml"

pipeline {
    agent {
        label SLAVE_LABEL
    }
    parameters {
        string (
            name:           'JIRA_ID',
            defaultValue:   'DETS-1234',
            description:    'Jira id of this pooled deployment request'
        )
        string (
            name:           'UPDATE_BOOKING',
            defaultValue:   'TRUE',
            description:    'If it is set to TRUE it will remove the booking. Set this to True only for the nightly tear down or if you want to expire a booking.'
        )
        string (
            name:           'UNLOCK_CLUSTER',
            defaultValue:   'TRUE',
            description:    'Default value is TRUE. IF it is true it will unlock cluster after teardown. If it is False (only used in re-install pipeline) it will unlock after the full reinstallation process.'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'eric-eiap',
            description:    'Namespace to purge environment'
        )
        string (
            name:           'CRD_NAMESPACE',
            defaultValue:   'eric-crd-ns',
            description:    'CRD Namespace to purge'
        )
        string (
            name:           'SELECTED_CLUSTER_ID',
            defaultValue:   'hall133',
            description:    'CLuster name used to download correct kubeconfig from Minio for the environment to purge.'
        )
        string (
            name:           'ARMDOCKER_USER_SECRET',
            defaultValue:   'detsuser_docker_config',
            description:    'ARM Docker secret. Either "ossadm_docker_config" for Fem2s11 or "detsuser_docker" for CCD Jenkins'
        )
        string (
            name:           'IDUN_USER_SECRET',
            defaultValue:   'idun_credentials',
            description:    'Jenkins secret ID for default IDUN user password. Either "idun_credentials" for Fem2s11 or "idun_user_quoted" for CCD Jenkins'
        )
        string (
            name:           'MINIO_USER_SECRET_ID',
            defaultValue:   'miniosecret',
            description:    'Minio user secret which is accessed via Jenkins credentials secret id'
        )
        string (
            name:           'PLATFORM_TYPE',
            defaultValue:   'pooled',
            description:    'Cloud provider type'
        )
        string (
            name:           'RESERVED_NAMESPACE_BOOKING',
            defaultValue:   'FALSE',
            description:    'If it is a reserved namespace, resourcequotas needs to be removed from namespace.'
        )
        string (
            name:           'EXTERNAL_RESERVE_NAMESPACE_EXECUTION',
            defaultValue:   'FALSE',
            description:    'If it is a reserved namespace, the shared external job used by customers should not remove the annotations.'
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
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        durabilityHint 'PERFORMANCE_OPTIMIZED'
    }
    environment {
        BUILD_INFO                  = "${env.BUILD_NUMBER}-${params.NAMESPACE}-${params.SELECTED_CLUSTER_ID}-${params.JIRA_ID}"
        DOCKER_FLAGS                = utils.getDockerFlags()
        DOCKER_FLAGS_NO_DOCKER_CONF = utils.getDockerFlagsNoDockerConfig()
    }
    stages {
	    stage('Set Build Description') {
            steps {
                script {
                    echo "==== Set Build Description ===="
                    currentBuild.displayName = "${env.BUILD_INFO}"
                }
            }
        }
        stage ('lock Cluster') {
	        steps {
                echo "==== Lock Cluster ===="
                sh "${bob} pooled-deployment:lock-cluster"
	        }
        }
        /*
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
        */
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
        stage('Install kube config file to default and admin locations') {
            steps {
                echo "==== Install kube config file to default and admin locations ===="
                sh "${bob} pooled-deployment:install-kubeconfig-admin-location"
                sh "${bob} pooled-deployment:install-kubeconfig-default-location"
            }
        }
        stage('Check K8S Connectivity') {
            steps {
                echo "==== Check K8S Connectivity ===="
                sh "${bob} do-health-check:check-eks-connectivity"
            }
        }
        stage('Cleanup ALL Helm Charts') {
            steps {
                echo "==== Cleanup ALL Helm Charts ===="
                sh "${bob} pooled-deployment:remove-all-charts"
            }
        }
        stage('Cleanup Installed PVCS and Secrets') {
            steps {
                echo "==== Cleanup Installed PVCS and Secrets ===="
                withCredentials ([
                    usernamePassword (
                        credentialsId:      params.IDUN_USER_SECRET,
                        usernameVariable:   'IDUN_USER_USERNAME',
                        passwordVariable:   'IDUN_USER_PASSWORD'
                    )
                ]) {
                    sh "${bob} remove-installed-pvcs remove-installed-secrets remove-installed-jobs"
                }
            }
        }
        stage('Remove Network Policies 12') {
            steps {
                echo "==== Remove Network Policies ===="
                sh "${bob} remove-network-policies"
                sh "${bob} remove-destinationrules"
            }
        }
        stage('Cleaning out annotations') {
             when {
                environment ignoreCase: true, name: 'EXTERNAL_RESERVE_NAMESPACE_EXECUTION', value: 'false'
            }
            steps {
                echo "==== Cleaning out annotations in the namespace ===="
                sh "${bob} pooled-deployment:clear-namespace-annotations"
            }
        }
        stage('Remove resource quotas set in namespace') {
            when {
                environment ignoreCase: true, name: 'RESERVED_NAMESPACE_BOOKING', value: 'true'
            }
            steps {
                echo "==== Remove resource quotas set in namespace ===="
                sh "${bob} pooled-deployment:remove-resource-quotas"
            }
        }
        // stage('Delete CRD Namespace'){
        //     steps {
        //         echo "==== Delete CRD Namespacee ===="
        //         sh returnStatus: true, script: "kubectl --kubeconfig ./admin.conf get ns ${params.CRD_NAMESPACE} && kubectl --kubeconfig ./admin.conf delete ns ${params.CRD_NAMESPACE}"
        //     }
        // }
        stage('Sleep before querying from prometheus'){
            steps {
                echo "==== Sleep before querying from prometheus ===="
                sleep(time: 3, unit: 'MINUTES')
            }
        }
        stage ('Update cluster resource usage in mongo'){
	        steps {
                echo "==== Update cluster resource usage in mongo ===="
                sh "${bob} pooled-deployment:update-cluster-resource-usage"
	        }
        }
        stage ('Unlock Cluster') {
            when {
                environment ignoreCase: true, name: 'UNLOCK_CLUSTER', value: 'true'
            }
	        steps {
                echo "==== Unlock Cluster ===="
                sh "${bob} pooled-deployment:release-lock-on-cluster"
	        }
        }
        stage("Update booking to Expired"){
            when {
                environment ignoreCase: true, name: 'UPDATE_BOOKING', value: 'true'
            }
            steps {
                echo "==== Update booking status to EXPIRED ===="
                sh "${bob} pooled-deployment:remove-booking"
            }
        }
        stage ('Cleaning workspace'){
            steps {
                cleanWs()
            }
        }
    }
}
