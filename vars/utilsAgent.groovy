/* groovylint-disable DuplicateStringLiteral, LineLength, MethodParameterTypeRequired, MethodReturnTypeRequired, VariableTypeRequired */
def call(agentLabel) {
    if (agentLabel.toLowerCase() == 'kubernetes_pod') {
        return kubernetesAgent(agentLabel)
    }
    return normalAgent(agentLabel)
}

def kubernetesAgent(agentLabel) {
    return [yamlFile: 'jenkins/scripts/pooled_eic/templates/jnlpCiUtilsPod.yaml', defaultContainer: 'outer-ci-utils-container', slaveLabel: agentLabel]
}

/*def kubernetesAgent() {
    return {
        kubernetes {
            yamlFile 'jenkins/scripts/pooled_eic/templates/jnlpCiUtilsPod.yaml'
            defaultContainer 'outer-ci-utils-container'
        }
        // kubernetes {
        //     yaml '''
        //         apiVersion: v1
        //         kind: Pod

        //         spec:
        //             containers:
        //             - name: outer-ci-utils-container
        //             image: armdocker.rnd.ericsson.se/proj-idun-aas/ci-utils:latest
        //             command:
        //             - sleep
        //             args:
        //             - infinity
        //             env: 
        //                 - name: DOCKER_HOST
        //                 value: tcp://localhost:2375
        //             - name: dind-daemon
        //             image: armdocker.rnd.ericsson.se/dockerhub-ericsson-remote/docker:18-dind
        //             securityContext:
        //                 privileged: true
        //             volumeMounts:
        //                 - name: docker-graph-storage
        //                 mountPath: /var/lib/docker
        //             volumes:
        //             - name: docker-graph-storage
        //                 emptyDir: {}
        //         '''
        //     defaultContainer 'outer-ci-utils-container'
        // }
    }
}*/

def normalAgent(agentLabel) {
    return [yamlFile: 'N/A', defaultContainer: 'N/A', slaveLabel: agentLabel]
}
