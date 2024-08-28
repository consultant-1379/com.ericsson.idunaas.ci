#!/usr/bin/env groovy
@Library('aas-muon-utils-lib') _
def bob = "bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0_pooled.yaml"
pipeline {
    // agent {
    //     label env.SLAVE_LABEL
    // }
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod

                spec:
                    affinity:
                        nodeAffinity:
                          requiredDuringSchedulingIgnoredDuringExecution:
                            nodeSelectorTerms:
                            - matchExpressions:
                              - key: detestenv-cert-gen
                                operator: Exists
                    containers:
                    - name: outer-ci-utils-container
                      image: armdocker.rnd.ericsson.se/proj-idun-aas/ci-utils:latest
                      command:
                      - sleep
                      args:
                      - infinity
                      env:
                        - name: DOCKER_HOST
                          value: tcp://localhost:2375
                    - name: dind-daemon
                      image: armdocker.rnd.ericsson.se/dockerhub-ericsson-remote/docker:18-dind
                      securityContext:
                        privileged: true
                      volumeMounts:
                        - name: docker-graph-storage
                          mountPath: /var/lib/docker
                    volumes:
                      - name: docker-graph-storage
                        emptyDir: {}
                '''
        }
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    // environment  {
	//     MINIO_USER_SECRET = 'miniosecret'
    // }

    parameters {
        string(name: 'DEPLOYMENT_NAME',defaultValue: 'hallXXX',description: 'This is used to determine the path certs on minio')
        choice(
            name: 'FOLDER',
            choices: ['eiap','eo-deploy', 'custom',],
            description: 'Provide folder name where your deployment is located (certs will be saved under <FOLDER>/<DEPLOYMENT_NAME>/<CERTS_PATH>.\nNOTE: Please choose custom to specify full path to certs'
        )
        string(name: 'CERTS_PATH',defaultValue: 'certificates',description: 'Certs will be saved under  <FOLDER>/<DEPLOYMENT_NAME>/<CERTS_PATH>.\nNOTE: If custom was chosen, FOLDER and DEPLOYMENT_NAME will be ignored')
        string(name: 'DOMAIN', defaultValue: '.<sample>-eiap.ews.gic.ericsson.se', description: 'Certs will be generated for <TAG>.<DOMAIN>')
        string(name: 'PREFIXES', defaultValue: 'iam gas', description: 'LIST OF PREFIXES. Certs will be generated for <prefix>.<DOMAIN>')
        string(name: 'SLAVE_LABEL', defaultValue: 'cENM2', description: 'Specify the slave label that you want the job to run on')
        string (name: 'MINIO_USER_SECRET_ID', defaultValue: 'miniosecret', description: 'Minio user secret which is accessed via Jenkins credentials secret id')

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
        stage('copy egad-ca cert') {
            steps {
                container('outer-ci-utils-container'){
                    sh "cp ${WORKSPACE}/jenkins/scripts/pooled_eic/certs/intermediate-ca.crt /etc/pki/trust/anchors/egad-ca.crt"
                    sh "update-ca-certificates"
                }
            }
        }

        stage('CLM availability') {
            steps {
                container('outer-ci-utils-container'){
                    sh "curl -sL --connect-timeout 30  https://clm-api.ericsson.net"
                }
            }
        }

        stage('GENERATE CERTS') {
            steps{
                container('outer-ci-utils-container'){
                    dir("${params.DEPLOYMENT_NAME}"){
                        sh """
                        ../jenkins/scripts/pooled_eic/cert_generate_clm.sh "${PREFIXES}" "${DOMAIN}" ..
                        """
                    }
                }
            }
        }

        stage('MOVE CERTS to MINIO') {
            steps {
                container('outer-ci-utils-container'){
                    dir("${params.DEPLOYMENT_NAME}"){
                        copy_certs_to_minio()
                        sh "tar cvfz \"certs_${params.DEPLOYMENT_NAME}_${env.BUILD_NUMBER}.tgz\" ./*"
                    }
                }
            }
            post{
                success{
                    archiveArtifacts allowEmptyArchive: true, artifacts: "${params.DEPLOYMENT_NAME}/*.tgz", followSymlinks: false
                }
            }
        }
    }
}


def copy_certs_to_minio(){
    if ("${params.FOLDER}" == "custom"){
      remote_dir = "${params.CERTS_PATH}"
    }else{
      remote_dir = "${params.FOLDER}/${params.DEPLOYMENT_NAME}/${params.CERTS_PATH}"
    }

    withCredentials([usernameColonPassword(credentialsId: "${MINIO_USER_SECRET_ID}", variable: 'MINIO_SECRET')]) {
        sh """
            cp ${WORKSPACE}/jenkins/scripts/pooled_eic/certs/tls-int-clm.crt ./intermediate-ca.crt
            docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock  --volume \$(pwd):/workdir  --volume /etc/hosts:/etc/hosts --workdir /workdir --network host --env DOCKER_HOST --group-add 0 -e MC_HOST_minio='http://${MINIO_SECRET}@minio.stsoss.seli.gic.ericsson.se:9000' armdocker.rnd.ericsson.se/dockerhub-ericsson-remote/minio/mc:latest cp -r ./ minio/${remote_dir}
        """
        // sh "cp ${WORKSPACE}/jenkins/scripts/pooled_eic/certs/tls-int-clm.crt ./intermediate-ca.crt"
        // sh "${bob} pooled-deployment:copy-certs-to-minio"
    }
}