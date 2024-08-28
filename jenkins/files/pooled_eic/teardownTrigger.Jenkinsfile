#!/usr/bin/env groovy
@Library('aas-muon-utils-lib') _
def bob = "bob/bob -r \${WORKSPACE}/jenkins/rulesets/ruleset2.0_pooled.yaml"

pipeline {
    agent {
        label env.SLAVE_LABEL
    }
    parameters {
        string (
            name:           'EXPIRED_BOOKINGS',
            defaultValue:   '[(DETS-1234, eric-eic-0, hall144)]',
            description:    'List of tuples: [(jira_id, namespace, cluster_name), (jira_id, cluster_name)] separated by comma.'
        )
        string (
            name:           'SPINNAKER_PIPELINE_URL',
            defaultValue:   'https://spinnaker-api.rnd.gic.ericsson.se/webhooks/webhook/test',
            description:    'Spinnaker pipeline webhook url of teardown pipeline.'
        )
        string (
            name:           'RETRY_ATTEMPTS',
            defaultValue:   '3',
            description:    'Number of retry attempts.'
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
    stages {
        stage('Trigger Spinnaker Pipelines') {
            steps {
                script {
                    def cleanedExpiredBookingsList = createTubleListOfBookings(params.EXPIRED_BOOKINGS)
                    cleanedExpiredBookingsList.each { expiredBooking ->
                        def (jiraId, namespace, clusterName) = expiredBooking.split(',')
                        def retryCount = params.RETRY_ATTEMPTS.toInteger()
                        def curlCommand = buildCurlCommand(params.NIGHTLY, jiraId, clusterName, namespace, params.SPINNAKER_PIPELINE_URL)
                        echo "Triggering Spinnaker pipeline: ${curlCommand}"
                        def curlOutput = retry(curlCommand, retryCount)
                       handleCurlResponse(curlOutput)
                    }    
                }
            }
        }
    }
}

def createTubleListOfBookings(expiredBookings) {
    def tupleList = []
    expiredBookingsCleaned = expiredBookings.replaceAll(/\[|\]/, '')
    tupleList = expiredBookingsCleaned.split(/\),/)
    return tupleList.collect { it.replaceAll(/\s|\(|\)|[|]/,'')}
}

def buildCurlCommand(nightly, jiraId, clusterName, namespace, url) {
    def curlCommand = """
    curl -s -o /dev/null -w '%{http_code}' \\
        -X POST \\
        -H 'Content-Type: application/json' \\
        -d '{
            "jira_id": "${jiraId}",
            "cluster_name": "${clusterName}",
            "namespace": "${namespace}",
            "update_booking": "true",
            "update_users": "true"
        }' \\
        ${url}
    """.stripIndent()
    return curlCommand
}

def handleCurlResponse(curlOutput) {
    if (curlOutput.contains("200")) {
        echo "Spinnaker pipeline triggered successfully."
    } else {
        error("Failed to trigger Spinnaker pipeline.")
    }
}

def retry(command, retryCount) {
    def output = ""
    def attempt = 1
    while (attempt <= retryCount) {
        echo "Attempt $attempt of $retryCount"
        try {
            output = sh(script: command, returnStdout: true)
            echo "output is ${output}"
            if (output.contains("200")) {
                break
            }
        } catch (Exception e) {
            echo "Error occurred: ${e.getMessage()}"
        }
        attempt++
    }
    return output
}
