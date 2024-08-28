from pooled_deployment_setup.masterData import MasterData
from pooled_deployment_setup.base import Base
from pooled_deployment_setup.retrieveClusterInfo import GetClusterData
import socket
import logging
import operator

LOG = logging.getLogger(__name__)

class Cluster(Base):
    def __init__(self):

        Base.__init__(self)



    def get_cluster_data_from_ews(self, clusterid):
        LOG.info("Retrieving cluster data from EWS")
        cluster_data = {
            "cluster_id": f"{clusterid}",
            "path_to_certs": f"minio/eic/{clusterid}/certificates/",
            "kubeconfig_path": f"minio/eic/kubeconfigs/{clusterid}_kubeconfig",
            "lock_status": False,
            "external_lbs": {},
            "fqdn_ns_map": {}
        }

        hostnames = [f"pool.{clusterid}-eiap.ews.gic.ericsson.se",
                    f"pool.{clusterid}-x1.ews.gic.ericsson.se",
                    f"pool.{clusterid}-x2.ews.gic.ericsson.se",
                    f"pool.{clusterid}-x3.ews.gic.ericsson.se",
                    f"pool.{clusterid}-x4.ews.gic.ericsson.se",
                    f"pool.{clusterid}-x5.ews.gic.ericsson.se",
                    f"pool.{clusterid}-x6.ews.gic.ericsson.se"]

        for ns, hostname in enumerate(hostnames):
                # Different ways of DNS resolution
                ## result = subprocess.run(["nslookup", hostname], capture_output=True, text=True)
                #
                ## result = execute_command(f"host endpoint.{hostname} | grep -o '[0-9][0-9]*\\.[0-9][0-9]*\\.[0-9][0-9]*\\.[0-9][0-9]*'")
                ## output_lines = result.split("\n")
                ## ip = output_lines[4].split(":")[1].strip()

                ip = socket.gethostbyname(hostname)

                # Print the second address
                LOG.info(f'dns_lookup({hostname}) = {ip}')

                # Append to cluster_data "external_lbs" and "fqdn_ns_map"
                cluster_data["external_lbs"][ip] = ("*." + hostname)
                cluster_data["fqdn_ns_map"][f"{clusterid}-eric-eic-{ns}"] = ("*." + hostname)


        return cluster_data

    def create_clusters(self, file_obj):
        LOG.info("Adding all cluster data to the clusters collection in mongo")

        conn = self.getMongoConnection()
        collection = conn["clusters"]
        collection.insert_many(file_obj)

        LOG.info("Objects added to clusters collection.")


    def create_single_cluster(self, cluster_data):
        LOG.info("Adding Cluster Data to the clusters collection in mongo")

        conn = self.getMongoConnection()
        collection = conn["clusters"]
        collection.insert_one(cluster_data)

        LOG.info("Objects added to clusters collection.")

    def remove_single_cluster(self, cluster_id):
        LOG.info("Removing Cluster Data from the the clusters collection in mongo")

        conn = self.getMongoConnection()
        collection = conn["clusters"]
        collection.delete_one({"cluster_id" : cluster_id})
        LOG.info(f"Cluster {'cluster_id'} removed from clusters collection.")


    def get_cluster_based_on_app_set(self, appset_cpu, appset_memory, kubeconfig_dir, dedicated_ns):
        LOG.info("Retrieving cluster based on the app-set cpu and memory")

        conn = self.getMongoConnection()
        collection = conn["clusters"]

        if dedicated_ns == "N/A":
            LOG.info(f"Default Method: No dedicated namespaces")
            data = collection.find()
        else:
            dedicated_cluster_id = dedicated_ns.split("-")[0]
            LOG.info(f"Dedicated Namespace method: Cluster for dedicated namespace is : {dedicated_cluster_id}")
            data = collection.find({"cluster_id": dedicated_cluster_id})

        master_obj = MasterData()
        buffer_value = master_obj.get_buffer_value()

        cluster_result = []
        for v in data:
            kubeconfig = f"{kubeconfig_dir}/{v['cluster_id']}_kubeconfig"

            LOG.info(f"CLUSTER DATA is : ***************** {v}")
            LOG.info(f"USED CPU is     : ***************** {v['used_cpu']}")
            used_cpu, used_memory = self.validate_cluster_with_prometheus(v['cluster_id'], kubeconfig, v['used_cpu'], v['used_memory'])

            LOG.info(f"Checking for reserved namespaces in  cluster : {v['cluster_id']} ")
            cluster_data_obj = GetClusterData(kubeconfig)
            _, _, reserved_ns = cluster_data_obj.getNamespaceState(v['cluster_id'])

            if reserved_ns:
                reserved_cpu_tot, reserved_mem_tot, res_faulty_ns_list = cluster_data_obj.getReservedNamespaceQuotas(reserved_ns)

                appset_and_used_cpu = used_cpu + appset_cpu + reserved_cpu_tot
                appset_and_used_mem = used_memory + appset_memory + reserved_mem_tot

            if not reserved_ns:
                LOG.info(f"No reserved namespaces found for cluster {v['cluster_id']}")
                res_faulty_ns_list = [] # initialized an empty list since when there are no reserved namespaces, there won't be faulty reserved namespaces.

                appset_and_used_cpu = used_cpu + appset_cpu
                appset_and_used_mem = used_memory + appset_memory

            total_cpu = v['total_cpu']
            total_memory = v['total_memory']

            buffered_cpu = total_cpu*buffer_value
            buffered_mem = total_memory*buffer_value

            buffered_total_cpu = total_cpu - buffered_cpu
            buffered_total_mem = total_memory - buffered_mem

            LOG.info(f"Cluster total CPU capacity : {total_cpu}")
            LOG.info(f"Cluster total Memory capacity : {total_memory}")
            LOG.info(f"Cluster total CPU capacity after buffer : {buffered_total_cpu}")
            LOG.info(f"Cluster total Memory capacity after buffer : {buffered_total_mem}")
            LOG.info(f"App_set CPU is : {appset_cpu}")
            LOG.info(f"App_set Memory is : {appset_memory}")
            LOG.info(f"Total used CPU with the app_set : {appset_and_used_cpu}")
            LOG.info(f"Total used Memory with the app_set : {appset_and_used_mem}")

            lock_status = v['lock_status']

            if ("exclusive_cluster" in v and v['exclusive_cluster'] is False) or "exclusive_cluster" not in v:
                # LOG.info(f"Exclusive cluster status is : {v['exclusive_cluster']}")
                if lock_status is False:
                    if appset_and_used_cpu < buffered_total_cpu and appset_and_used_mem < buffered_total_mem:
                        if res_faulty_ns_list:
                            LOG.warning(f"There are faulty reserved namespaces {res_faulty_ns_list}, Cluster {v['cluster_id']} will not be selected as a valid cluster for the II")
                        else:
                            LOG.info(f"************************************************* Cluster appended is : {v['cluster_id']}")
                            cluster_result.append(v['cluster_id'])

        if not cluster_result:
            raise Exception(f"No cluster found that can install the appset")
        LOG.info(f"Clusters that can accomodate the given app set are : {cluster_result}")

        data_dict_cluster = self.verify_and_pick_cluster(cluster_result, kubeconfig_dir, dedicated_ns)
        LOG.info(f"selected cluster dictionary is with all data required for II : {data_dict_cluster}")
        return data_dict_cluster





    def verify_and_pick_cluster(self, clusters, kubeconfig_dir, dedicatedns):

        verified_clusters = {}
        for clust in clusters:
            LOG.info(f"Verifying cluster ---> {clust}")

            kubeconfig = f"{kubeconfig_dir}/{clust}_kubeconfig"
            cluster_data_obj = GetClusterData(kubeconfig)

            ns, _, _ = cluster_data_obj.getNamespaceState(clust)
            if ns:
                if dedicatedns == "N/A":
                    namespace_picked = ns[0]
                else:
                    if dedicatedns in ns:
                        namespace_picked = dedicatedns
                    else:
                        raise Exception(f"Dedicated namespace validation failed : {dedicatedns} - Namespace is reserved or booked.")

                fqdn = self.get_fqdn_by_namespace(clust, namespace_picked)
                ip = self.get_externalIP_for_namespace(clust, fqdn)
                validate_ip = cluster_data_obj.validate_ip_in_cluster(ip)
                if validate_ip:
                    verified_clusters[clust] = {}
                    LOG.info(f"IP validation successfull for cluster {clust}, namespace {namespace_picked} and fqdn {fqdn}. Adding the cluster and namespace to verified list")
                    verified_clusters[clust]['namespace'] = namespace_picked
                    verified_clusters[clust]['fqdn'] = fqdn
                    verified_clusters[clust]['ip'] = ip

        if not verified_clusters:
            raise Exception(f"All clusters in the list failed verification. Please check the clusters namespace *Booked* status : {clusters}")

        verified_clust_list = list(verified_clusters.keys())
        LOG.info(f"Dictonary of verified clusters are {verified_clusters}")

        selected_cluster_dict = {}

        selected_cluster = self.check_cluster_for_min_capacity(verified_clust_list)
        LOG.info(f"Cluster selected for install is {selected_cluster}")

        selected_ns = verified_clusters[selected_cluster]['namespace']
        LOG.info(f"Namespace selected for install is {selected_ns}")

        selected_fqdn = verified_clusters[selected_cluster]['fqdn']
        LOG.info(f"FQDN selected for install is : {selected_fqdn}")

        selected_ip = verified_clusters[selected_cluster]['ip']
        LOG.info(f"IP selected for install is : {selected_ip}")

        selected_cluster_dict['cluster'] = selected_cluster
        selected_cluster_dict['namespace'] = selected_ns
        selected_cluster_dict['fqdn'] =  selected_fqdn
        selected_cluster_dict['ip'] = selected_ip

        return selected_cluster_dict


    def verify_exclusive_cluster(self, clust_list, kubeconfig_dir):
        LOG.info(f"Verifying exclusive cluster {clust_list}")

        free_exe_clusts_dict = {}
        for clust in clust_list:
            kubeconfig = f"{kubeconfig_dir}/{clust}_kubeconfig"
            cluster_data_obj = GetClusterData(kubeconfig)
            free_namespaces, booked_namespaces, reserved_namespaces = cluster_data_obj.getNamespaceState(clust)
            LOG.info(f"List of booked namspaces in cluster {clust} are : {booked_namespaces}")
            LOG.info(f"List of reserved namspaces in cluster {clust} are : {reserved_namespaces}")
            if not booked_namespaces and not reserved_namespaces:
                free_exe_clusts_dict[clust] = free_namespaces[0]

        if not free_exe_clusts_dict:
            raise Exception("No Valid Exclusive cluster found.")

        clusterid = list(free_exe_clusts_dict.keys())[0]
        namespace = free_exe_clusts_dict[clusterid]

        fqdn = self.get_fqdn_by_namespace(clusterid, namespace)
        LOG.info(f"FQDN selected for install is : {fqdn}")

        ip = self.get_externalIP_for_namespace(clusterid, fqdn)
        LOG.info(f"IP selected for install is {ip}")

        kubeconfig = f"{kubeconfig_dir}/{clusterid}_kubeconfig"
        ip_obj = GetClusterData(kubeconfig)
        validate_ip = ip_obj.validate_ip_in_cluster(ip, kubeconfig)
        if not validate_ip:
            raise Exception("IP already in use. Please check.")

        return namespace, fqdn, ip, clusterid


    def validate_cluster_with_prometheus(self, clusterid, kubeconfig, mongo_cpu_value, mongo_mem_value):

        LOG.info(f"mongo value for cpu in cluster {clusterid} : {mongo_cpu_value}")
        LOG.info(f"mongo value for memory in cluster {clusterid} : {mongo_mem_value}")

        prom_cluster_data = GetClusterData(kubeconfig=kubeconfig)
        mem_used = prom_cluster_data.getUsedMemory(clusterid)
        cpu_used = prom_cluster_data.getUsedCpu(clusterid)

        mem_used_lower = mem_used - 2
        mem_used_upper = mem_used + 2
        cpu_used_lower = cpu_used - 2
        cpu_used_upper = cpu_used + 2

        if (cpu_used_lower <= mongo_cpu_value <= cpu_used_upper) and (mem_used_lower <= mongo_mem_value <= mem_used_upper):
            LOG.info(f"CPU and memory values are in range for {clusterid}. Proceeding to the next stage.")
            return mongo_cpu_value, mongo_mem_value
        else:
            LOG.warning(f"There is a mismatch in CPU and memory values in mongo and prometheus for the cluster : {clusterid}")

            result = self.update_cpu_memory_realtime(clusterid, kubeconfig)
            return result['used_cpu'], result['used_memory']


    def check_cluster_for_min_capacity(self, cluster_result):
        LOG.info("Retrieving a specific cluster based on min capacity for installation")

        conn = self.getMongoConnection()
        collection = conn["clusters"]

        cluster_info = {}
        for k in cluster_result:
            cluster_dict = collection.find_one({"cluster_id": k})
            remaning_cpu = cluster_dict['total_cpu'] - cluster_dict['used_cpu']
            cluster_info[k] = remaning_cpu

        allocated_cluster = min(cluster_info.items(), key=operator.itemgetter(1))[0]
        return allocated_cluster


    def get_cluster_mongo(self, clusterID):
        LOG.info("Retrieving cluster from mongo")

        conn = self.getMongoConnection()
        collection = conn["clusters"]
        cluster_obj = collection.find_one({"cluster_id": clusterID})
        if not cluster_obj:
            raise Exception("No cluster found for the given cluster ID.")
        return cluster_obj


    def get_all_clusters_mongo(self):
        LOG.info("Retrieving all clusters from mongo")
        conn = self.getMongoConnection()
        collection = conn["clusters"]
        data = collection.find()
        return data

    def get_fqdn_by_namespace(self, clusterid, namespace):
        LOG.info("Getting FQDN based on the namespace.")

        cluster_data = self.get_cluster_mongo(clusterid)
        fqdn = cluster_data["fqdn_ns_map"][namespace]
        return fqdn

    def get_externalIP_for_namespace(self, clusterid, fqdn):
        LOG.info("Getting all external IPs assigned to the cluster")

        cluster_obj = self.get_cluster_mongo(clusterid)
        ip_dict = cluster_obj['external_lbs']
        LOG.debug(f"IPs in the cluster are : {ip_dict}")

        for k, v in ip_dict.items():
            if v == fqdn:
                return k
        raise Exception(f"FQDN not found in mongo for cluster {clusterid} external IP dictionary")

    def get_exclusive_clusters(self):
        LOG.info("Retrieving exclusive clusters from mongo")
        conn = self.getMongoConnection()
        collection = conn["clusters"]
        cluster_obj = collection.find()

        exclusive_clust_list = []
        for cluster in cluster_obj:
            if ("exclusive_cluster" in cluster and cluster['exclusive_cluster'] is True):
                exclusive_clust_list.append(cluster['cluster_id'])

        return exclusive_clust_list


    def update_cluster_fields(self, clusterID, key, value):
        LOG.info(f"Updating {key} to : {value}")

        conn = self.getMongoConnection()
        collection = conn["clusters"]

        updated_data = {
            '$set': {
                f"{key}": value
            }
        }
        collection.find_one_and_update({"cluster_id": clusterID}, updated_data)
        LOG.info("Data Updated.")


    def update_cpu_memory_realtime(self, clusterid, kubeconfig):
        LOG.info(f"Updating cluster {clusterid} memory and cpu from realtime data")

        cluster_data_obj = GetClusterData(kubeconfig)
        mem_used = cluster_data_obj.getUsedMemory(clusterid)
        mem_total = cluster_data_obj.getTotalMemory(clusterid)
        cpu_tot = cluster_data_obj.getTotalCpu(clusterid)
        cpu_used = cluster_data_obj.getUsedCpu(clusterid)

        LOG.info(f"total memory of cluster is : {mem_total}")
        LOG.info(f"total CPU of cluster is : {cpu_tot}")
        LOG.info(f"Used memory of cluster is : {mem_used}")
        LOG.info(f"Used CPU of the cluster is : {cpu_used}")
        LOG.info("Inserting cpu and mem data to clusters collection..")

        conn = self.getMongoConnection()
        collection = conn["clusters"]

        updated_data = {
            '$set': {
                "total_cpu": cpu_tot,
                "total_memory": mem_total,
                "used_cpu": cpu_used,
                "used_memory": mem_used
            }
        }

        result_id = collection.find_one_and_update({"cluster_id": clusterid}, updated_data)
        LOG.info(f"Cluster {clusterid} resources are updated in Clusters collection. ID is: " + str(result_id) )
        return result_id
