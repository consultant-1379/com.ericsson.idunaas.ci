#!/usr/bin/env groovy
@Library('aas-muon-utils-lib') _
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
            name:           'JIRA_ID',
            defaultValue:   'DETS-1234',
            description:    'Jira id of this pooled deployment request'
        )
        string (
            name:           'DEPLOYMENT_TYPE',
            defaultValue:   'install',
            description:    'Deployment Type, set \"install\" or \"upgrade\"'
        )
        string (
            name:           'NAMESPACE',
            defaultValue:   'eric-eiap',
            description:    'Namespace to purge environment'
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
            name:           'CRD_NAMESPACE',
            defaultValue:   'eric-crd-ns',
            description:    'Namespace to purge environment'
        )
        string (
            name:           'ADP_DDC_USER_SECRET',
            defaultValue:   'ddc_sftpuser_credentials',
            description:    'Jenkins secret ID for default APD-DDC user password'
        )
        string (
            name:           'PLATFORM_TYPE',
            defaultValue:   'pooled',
            description:    'Cloud provider type'
        )
        string (
            name:           'GERRIT_REFSPEC',
            defaultValue:   'refs/heads/master',
            description:    'Can be used to fetch job JenkinsFile from branch (refs/heads/master) or commit (refs/changes/95/156395/1) | 95 - last 2 digits of Gerrit commit number | 156395 - is Gerrit commit number | 1 - patch number of gerrit commit | **Only to be used during testing **'
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
        stage('Install docker config file to local and root location') {
            steps {
                echo "==== Install docker config File to root location ===="
                withCredentials ([
                    file (
                        credentialsId:  params.ARMDOCKER_USER_SECRET,
                        variable:       'DOCKERCONFIG'
                    )
                ]) {
                    sh "${bob} pooled-deployment:install-docker-config-to-root-location"
                    sh "${bob} pooled-deployment:install-docker-config-to-local-location"
                }
            }
        }
        stage('Set Cluster name to bob variable') {
            steps {
                echo "==== Set Cluster name to bob variable ===="
                sh "${bob} pooled-deployment:set-selected-cluster-id"
            }
        }
        stage('Retrieve kube config file from miniIO') {
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
        stage('Check EWS Connectivity') {
            steps {
                echo "==== Check EWS Connectivity ===="
                sh "${bob} do-health-check:check-eks-connectivity"
            }
        }
        stage('Create namespaces if not exist') {
            steps {
                    echo "==== Create namespaces if not exist ===="
                    sh "${bob} create-release-namespace"
            }
        }
        stage('Check for k8s-registry-secret') {
            steps {
                sh "${bob} pooled-deployment:create-registry-secret"
            }
        }
        stage('Pre Deployment Configurations') {
            when {
                environment ignoreCase: true, name: 'DEPLOYMENT_TYPE', value: 'install'
            }
            steps {
                echo "==== Pre Deployment Configurations ===="
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
                    sh "${bob} create-credentials-secrets"
                }
            }
        }
        stage("Check storage class") {
            steps {
                echo "==== Check storage class ===="
                sh "${bob} pooled-deployment:check-storage-class"
            }
        }
    }
}
