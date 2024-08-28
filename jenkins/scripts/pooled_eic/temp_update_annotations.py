#!/usr/bin/python3

from  kubernetes import client, config
from pymongo import MongoClient
import os
import subprocess



def generate_kube_client(kubeconfig):

    print(f"Generating the client for {kubeconfig}")
    config.load_kube_config(kubeconfig)
    k8s_api_client = client.CoreV1Api()

    return k8s_api_client


def get_mongo_connection():
    
    print(f"generating mongo client")
    mongo_client = MongoClient("mongodb+srv://eic-pool-deployments-svc.mongodb-operator.svc.cluster.local/eicPooledClusterDB?replicaSet=eic-pool-deployments&ssl=false", 
                username="pooluser", 
                password="idunEricss0n")
    db = mongo_client.eicPooledClusterDB
    return db


def get_clusters_from_mongo():

    conn = get_mongo_connection()
    collection = conn["clusters"]

    clusters_bson = collection.find()
    clusters = []
    for data in clusters_bson:
        print(f"Cluster appended is : {data['cluster_id']}")
        clusters.append(data['cluster_id'])

    return clusters


def execute_command(command):
    """
    Execute a command on shell
    :param command: Command to be executed
    :return: Command Response
    """

    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout_value = proc.communicate()[0].decode("utf-8")

    return_value = proc.returncode

    if return_value != 0:
        raise Exception("Failed to execute command - {0}. Error is - {1}".format(command, stdout_value))

    return stdout_value


def update_ns_reserve_annotations(clusterid):
    print(f"updating annotations for cluster: {clusterid} ")

    kubeconfig = f"kubeconfigs/{clusterid}_kubeconfig"
    k8s_client = generate_kube_client(kubeconfig)
    namespaces = k8s_client.list_namespace()

    for ns in namespaces.items:
        if ns.metadata.name.startswith(clusterid):
            #  if "reserved" in ns.metadata.annotations:
            annotate_cmd = f"kubectl --kubeconfig {kubeconfig} annotate --overwrite namespace {ns.metadata.name} reserved=false"
            result = execute_command(annotate_cmd)
            print(f"{result}")
    




def main():

    print(f"Getting clusters from mongo")

    clusters_res = get_clusters_from_mongo()

    for clust in clusters_res:
        update_ns_reserve_annotations(clust)



if __name__ == '__main__':
    main()