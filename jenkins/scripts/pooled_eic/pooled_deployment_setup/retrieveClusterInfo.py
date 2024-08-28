from unicodedata import name
from xml.dom.expatbuilder import Namespaces
from prometheus_api_client import PrometheusConnect
import requests
import json
import logging
import os
from pooled_deployment_setup.base import Base
from kubernetes import client, config
from retry import retry


LOG = logging.getLogger(__name__)

class GetClusterData(Base):
    def __init__(self, kubeconfig):
        Base.__init__(self)
        self.kubeconfig = kubeconfig
        self.k8sConfigClient = config.load_kube_config(self.kubeconfig)
        self.k8sCoreV1Api = client.CoreV1Api()

    @retry(tries=7, delay=2)
    def getTotalMemory(self, clusterid):

        client = self.getPrometheusConnection()

        LOG.info("Retrieving Total Memory")
        # query = f"sum(kube_node_status_allocatable{{vpod='EIAP', dc='ews0', program=~'DETS', cluster_id=~'{clusterid}', resource='memory'}})"
        query = f"sum(kube_node_status_allocatable{{program=~'DETS', cluster_id=~'{clusterid}', resource='memory'}})"
        total_capacity = client.custom_query(query=query)

        if len(total_capacity) < 1 or "value" not in total_capacity[0] or len(total_capacity[0]["value"]) < 2:
            LOG.error(f"Query is {query}")
            raise Exception(f"Unexpected data structure : {total_capacity}")
            
        tot_cap = total_capacity[0]["value"][1]
        total_capacity_gb = round(float(tot_cap)/(1024**3), 1)

        return total_capacity_gb


    @retry(tries=7, delay=2)
    def getUsedMemory(self, clusterid):

        client = self.getPrometheusConnection()

        LOG.info("Getting namespaces from the cluster")
        ns_obj = self.getClusterNamespaces()
        namespaces_list = []
        for ns in ns_obj.items:
            namespaces_list.append(ns.metadata.name)

        ns_string = '|'.join(namespaces_list)

        LOG.info("Retrieving Used Memory")

        # query = f"sum(kube_pod_container_resource_requests{{vpod='EIAP',dc='ews0', program=~'DETS', cluster_id=~'{clusterid}', resource='memory', namespace=~'({ns_string})'}})"
        query = f"sum(kube_pod_container_resource_requests{{program=~'DETS', cluster_id=~'{clusterid}', resource='memory', namespace=~'({ns_string})'}})"
        used_cluster_mem = client.custom_query(query=query)

        if len(used_cluster_mem) < 1 or "value" not in used_cluster_mem[0] or len(used_cluster_mem[0]["value"]) < 2:
            LOG.error(f"Query is {query}")
            raise Exception(f"Unexpected data structure : {used_cluster_mem}")

        used_cluster_mem_val = used_cluster_mem[0]["value"][1]
        used_cluster_mem_gb = round(float(used_cluster_mem_val)/(1024**3), 1)

        return used_cluster_mem_gb


    @retry(tries=7, delay=2)
    def getTotalCpu(self, clusterid):

        client = self.getPrometheusConnection()

        LOG.info("Retrieving Total CPU")
        # query = f"sum(kube_node_status_allocatable{{vpod='EIAP', dc='ews0', program=~'DETS', cluster_id=~'{clusterid}', resource='cpu'}})"
        query = f"sum(kube_node_status_allocatable{{program=~'DETS', cluster_id=~'{clusterid}', resource='cpu'}})"
        total_cpu = client.custom_query(query=query)

        if len(total_cpu) < 1 or "value" not in total_cpu[0] or len(total_cpu[0]["value"]) < 2:
            LOG.error(f"Query is {query}")
            raise Exception(f"Unexpected data structure : {total_cpu}")

        total_cpu_val = total_cpu[0]["value"][1]
        rounded_value = round(float(total_cpu_val), 1)
        return rounded_value


    @retry(tries=7, delay=2)
    def getUsedCpu(self, clusterid):

        client = self.getPrometheusConnection()

        LOG.info("Getting namespaces from the cluster")
        ns_obj = self.getClusterNamespaces()
        namespaces_list = []
        for ns in ns_obj.items:
            namespaces_list.append(ns.metadata.name)

        ns_string = '|'.join(namespaces_list)

        LOG.info("Retrieving Used CPU from Prometheus")
        # query = f"sum(kube_pod_container_resource_requests{{vpod='EIAP',dc='ews0', program=~'DETS', cluster_id=~'{clusterid}', resource='cpu', namespace=~'({ns_string})'}})"
        query = f"sum(kube_pod_container_resource_requests{{program=~'DETS', cluster_id=~'{clusterid}', resource='cpu', namespace=~'({ns_string})'}})"
        used_cluster_CPU = client.custom_query(query=query)

        if len(used_cluster_CPU) < 1 or "value" not in used_cluster_CPU[0] or len(used_cluster_CPU[0]["value"]) < 2:
            LOG.error(f"Query is {query}")
            raise Exception(f"Unexpected data structure : {used_cluster_CPU}")

        used_cluster_cpu_val = used_cluster_CPU[0]["value"][1]
        rounded_value = round(float(used_cluster_cpu_val), 1)
        return rounded_value


    def validate_ip_in_cluster(self, ip):
        LOG.info(f"Checking if the IP selected for Install is already used in the cluster.")

        ip_list = self.getUsedExternalIp()
        LOG.debug(f"External IPs used in the cluster are : {ip_list}")
        if ip not in ip_list:
            LOG.info(f"{ip} is not in used.")
            return True        

    def getClusterNamespaces(self):

        LOG.info("Reading cluster namespaces")
        created_ns = self.k8sCoreV1Api.list_namespace()
        return created_ns

        
    def getNamespacedResourceQuotas(self, namespace):

        LOG.info("Getting resource quotas for the namespace")
        quotaDict = self.k8sCoreV1Api.list_namespaced_resource_quota(namespace)
        
        return quotaDict


    def getUsedExternalIp(self):

        LOG.info("Reading cluster services to get External IPs")

        services = self.k8sCoreV1Api.list_service_for_all_namespaces()

        externalIp_list = []
        for svc in services.items:
            if svc.spec.load_balancer_ip != None:
                externalIp_list.append(svc.spec.load_balancer_ip)

        return set(externalIp_list)
        
        
    def getNamespaceState(self, clusterid):
        LOG.info(f"Validating namespace for EIC installation in cluster {clusterid}")

        ns_items = self.getClusterNamespaces()

        free_ns = []
        booked_ns = []
        reserved_ns = []
        for ns in ns_items.items:
            if ns.metadata.name.startswith(clusterid):
                if ns.metadata.annotations is not None:
                    if "booked" in ns.metadata.annotations and "reserved" in ns.metadata.annotations:
                        if (ns.metadata.annotations["booked"] == "false" and ns.metadata.annotations["reserved"] == "false"):
                            LOG.info(f"Cluster --> {clusterid}. Free namespace : {ns.metadata.name}")
                            LOG.info(f"Cluster --> {clusterid}. Booking status of the namespace {ns.metadata.name} is: {ns.metadata.annotations['booked']}")
                            LOG.info(f"Cluster --> {clusterid}. Reserved status of the namespace {ns.metadata.name} is: {ns.metadata.annotations['reserved']}")
                            free_ns.append(ns.metadata.name)

                        elif (ns.metadata.annotations["booked"] == "true" and ns.metadata.annotations["reserved"] == "false"):
                            LOG.warning(f"Cluster --> {clusterid}. Namespace {ns.metadata.name} is already booked or cannot be used.")
                            LOG.info(f"Cluster --> {clusterid}. Booked status of the namespace {ns.metadata.name} is : {ns.metadata.annotations['booked']}")
                            LOG.info(f"Cluster --> {clusterid}. Reserved status of the namespace {ns.metadata.name} is: {ns.metadata.annotations['reserved']}")
                            booked_ns.append(ns.metadata.name)

                        elif (ns.metadata.annotations["reserved"] == "true" and ns.metadata.annotations["booked"] == "true"):
                            LOG.info(f"Cluster --> {clusterid}. Reserved namespace : {ns.metadata.name} is already reserved or cannot be used.")
                            LOG.info(f"Cluster --> {clusterid}. Booked status of the namespace {ns.metadata.name} is : {ns.metadata.annotations['booked']}")
                            LOG.info(f"Cluster --> {clusterid}. Reserved status of the namespace {ns.metadata.name} is: {ns.metadata.annotations['reserved']}")
                            reserved_ns.append(ns.metadata.name)

                        else:
                            LOG.warning(f"Wrong combination of annotation in the namespace : {ns.metadata.name}")
                            LOG.info(f"Cluster --> {clusterid}. Booked status of the namespace {ns.metadata.name} is : {ns.metadata.annotations['booked']}")
                            LOG.info(f"Cluster --> {clusterid}. Reserved status of the namespace {ns.metadata.name} is: {ns.metadata.annotations['reserved']}")

                    else:
                        LOG.warning(f"Cluster --> {clusterid}. *booked* annotation or *reserved* not found in the namespace {ns.metadata.name}. Please investigate")
                else:
                    LOG.warning(f"Cluster --> {clusterid}. No annotations found in the namespace {ns.metadata.name}. Please investigate")

        return free_ns, booked_ns, reserved_ns


    def getReservedNamespaceQuotas(self, reserved_ns):

        faulty_ns_list = []
        res_cpu_list = []
        res_mem_list = []
        for ns in reserved_ns:                        
            quotas = self.getNamespacedResourceQuotas(ns)
            # LOG.info(f"Length of the quota is : {len(quotas.items)}")
            # LOG.info(f"Quota is : {quotas}")
            if len(quotas.items) != 0:
                if "limits.cpu" in quotas.items[0].spec.hard and "limits.memory" in quotas.items[0].spec.hard:
                    # LOG.info(f"Resources quotas for the namespace {ns} are : {quotas}")
                    LOG.info(f"HARD limit for CPU in namespace {ns} is : {quotas.items[0].spec.hard['limits.cpu']}")
                    LOG.info(f"HARD limit for MEMORY in namespace {ns} is : {quotas.items[0].spec.hard['limits.memory']}")
                    res_cpu_list.append(quotas.items[0].spec.hard['limits.cpu'])
                    res_mem_list.append(quotas.items[0].spec.hard['limits.memory'])
                else:
                    LOG.warning(f"Please check the resourceQuotaObject set in namespace {ns}, no hard cpu and mem limit found. \n"
                                    "If no resource Quota created for the ns, please investigate it.")
                    faulty_ns_list.append(ns)
            else:
                LOG.warning(f"No quotas found for the reserved NS: {ns}. Please investigate this.")
                faulty_ns_list.append(ns)

        res_cpu_list_to_float = [float(i) for i in res_cpu_list]
        res_mem_list_to_float = [float(i) for i in res_mem_list]
        total_reserved_cpu = sum(res_cpu_list_to_float)
        total_reserved_memory = sum(res_mem_list_to_float)

        LOG.info(f"Total Reserved CPU in the cluster is : {total_reserved_cpu}")
        LOG.info(f"Total Reserved Memory in the cluster is : {total_reserved_memory}")


        return total_reserved_cpu, total_reserved_memory, faulty_ns_list