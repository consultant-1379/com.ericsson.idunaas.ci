from xml.etree.ElementTree import tostring
from pooled_deployment_setup.masterData import MasterData
from pooled_deployment_setup.retrieveClusterInfo import GetClusterData
from pooled_deployment_setup.clusterCollectionData import Cluster
from pooled_deployment_setup.dimensions import Dimensions
from pooled_deployment_setup.constants import values
from pooled_deployment_setup.bookings import Bookings
from pooled_deployment_setup.minio import MinioData
from datetime import datetime
import bson.json_util as json_util
import logging
import json
from kubernetes import client, config

LOG = logging.getLogger(__name__)

# def verify_and_pick_cluster(clusters, kubeconfig_dir):

#     verified_clusters = {}
#     for clust in clusters:
#         LOG.info(f"Verifying cluster ---> {clust}")

#         kubeconfig = f"{kubeconfig_dir}/{clust}_kubeconfig"
#         cluster_data_obj = GetClusterData(kubeconfig)

#         ns, _, _ = cluster_data_obj.getNamespaceState(clust)
#         if ns:
#             verified_clusters[clust] = {}
#             verified_clusters[clust]['namespace'] = ns[0]

#     if not verified_clusters:
#         raise Exception(f"All clusters in the list failed verification. Please check the clusters for used CPU/memory and Namespace *Booked* status : {clusters}")

#     verified_clust_list = list(verified_clusters.keys())
#     LOG.debug(f"Dictonary of verified clusters are {verified_clusters}")

#     LOG.info(f"CPU/memory and namespace validation success for clusters : {verified_clust_list}")
#     selected_cluster_dict = {}
#     cluster_result = Cluster()

#     selected_cluster = cluster_result.check_cluster_for_min_capacity(verified_clust_list)
#     LOG.info(f"Cluster selected for install is {selected_cluster}")
#     selected_ns = verified_clusters[selected_cluster]['namespace']
#     LOG.info(f"Namespace selected for install is {selected_ns}")

#     fqdn = get_fqdn_by_namespace(selected_cluster, selected_ns)
#     LOG.info(f"FQDN selected for install is : {fqdn}")

#     ip = get_externalIP_for_namespace(selected_cluster, fqdn)
#     LOG.info(f"IP selected for install is {ip}")
#     kubeconfig = f"{kubeconfig_dir}/{selected_cluster}_kubeconfig"
#     validate_ip = validate_ip_in_cluster(ip, kubeconfig)
#     if not validate_ip:
#         raise Exception("IP already in use. Please check.")

#     selected_cluster_dict['cluster'] = selected_cluster
#     selected_cluster_dict['namespace'] = selected_ns
#     selected_cluster_dict['fqdn'] =  fqdn
#     selected_cluster_dict['ip'] = ip

#     return selected_cluster_dict



# def verify_exclusive_cluster(clust_list, kubeconfig_dir):
#     LOG.info(f"Verifying exclusive cluster {clust_list}")

#     free_exe_clusts_dict = {}
#     for clust in clust_list:
#         kubeconfig = f"{kubeconfig_dir}/{clust}_kubeconfig"
#         cluster_data_obj = GetClusterData(kubeconfig)
#         free_namespaces, booked_namespaces, reserved_namespaces = cluster_data_obj.getNamespaceState(clust)
#         if not booked_namespaces and not reserved_namespaces:
#             free_exe_clusts_dict[clust] = free_namespaces[0]

#     clusterid = list(free_exe_clusts_dict.keys())[0]
#     namespace = free_exe_clusts_dict[clusterid]

#     fqdn = get_fqdn_by_namespace(clusterid, namespace)
#     LOG.info(f"FQDN selected for install is : {fqdn}")

#     ip = get_externalIP_for_namespace(clusterid, fqdn)
#     LOG.info(f"IP selected for install is {ip}")

#     validate_ip = validate_ip_in_cluster(ip, kubeconfig)
#     if not validate_ip:
#         raise Exception("IP already in use. Please check.")

#     return namespace, fqdn, ip, clusterid




def set_cluster_exclusive(removeOrSet, clusterid, kubeconfig):
    LOG.info(f"Setting cluster {clusterid} as an exclusive cluster")

    cluster_obj = Cluster()
    cluster_data_obj = GetClusterData(kubeconfig)
    if removeOrSet == "set":

        LOG.info(f"Checking the namespaces to see if anyone of them are booked.")
        _, booked_ns, resrved_ns = cluster_data_obj.getNamespaceState(clusterid)

        if booked_ns or resrved_ns:
            raise Exception(f"There are booked namespaces in the cluster {clusterid}. Cannot set this cluster as an exclusive cluster.")

        cluster_data = cluster_obj.get_cluster_mongo(clusterid)
        lock_status = cluster_data['lock_status']

        if lock_status is True:
             raise Exception(f"Cluster {clusterid} is locked. Please try again when it is unlocked.")

        key = "exclusive_cluster"
        value = True
        cluster_obj.update_cluster_fields(clusterid, key, value)

    elif removeOrSet == "remove":
        LOG.info(f"Removing cluster exclusivity for cluster {clusterid}.")

        _, booked_ns, reserved_ns = cluster_data_obj.getNamespaceState(clusterid)

        if booked_ns:
            LOG.warning(f"There are already booked namespaces in the cluster {booked_ns}")

        if reserved_ns:
            LOG.warning(f"There are already reserved namespaces in the cluster {reserved_ns}")

        key = "exclusive_cluster"
        value = False
        cluster_obj.update_cluster_fields(clusterid, key, value)

    else:
        raise Exception(f"Wrong action {removeOrSet}. Please check the command.")


# def get_externalIP_for_namespace(clusterid, fqdn):
#     LOG.info("Getting all external IPs assigned to the cluster")

#     cluster_ip_obj = Cluster()
#     cluster_obj = cluster_ip_obj.get_cluster_mongo(clusterid)
#     ip_dict = cluster_obj['external_lbs']
#     LOG.debug(f"IPs in the cluster are : {ip_dict}")

#     for k, v in ip_dict.items():
#         if v == fqdn:
#             return k
#     raise Exception(f"FQDN not found in mongo for cluster {clusterid} external IP dictionary")


# def get_fqdn_by_namespace(clusterid, namespace):
#     LOG.info("Getting FQDN based on the namespace.")

#     cluster_obj = Cluster()
#     cluster_data = cluster_obj.get_cluster_mongo(clusterid)
#     fqdn = cluster_data["fqdn_ns_map"][namespace]
#     return fqdn


# def validate_ip_in_cluster(ip, kubeconfig):
#     LOG.info(f"Checking if the IP selected for Install is already used in the cluster.")

#     ip_obj = GetClusterData(kubeconfig)
#     ip_list = ip_obj.getUsedExternalIp()
#     LOG.debug(f"External IPs used in the cluster are : {ip_list}")
#     if ip not in ip_list:
#         LOG.info(f"{ip} is not in used.")
#         return True


def validate_and_get_appset(release_version):
    LOG.info(f"Getting appset based on the release version : {release_version}")

    rel_version = release_version.split("-")[0]
    app_set_obj = Dimensions()
    dimension_obj = app_set_obj.get_appset_from_release_version(rel_version)

    if dimension_obj is None:
        LOG.info(f"Cannot find the release version based on the helmfile version. Getting the DEFAULT version")
        default_rel_obj = MasterData()
        default_v = default_rel_obj.get_default_release_version()
        LOG.info(f"Getting appset object from DEFAULT version")
        default_obj = app_set_obj.get_appset_from_release_version(default_v)
        return default_obj

    return dimension_obj


def check_certs_exists(cluster_id, fqdn, accesskey, secretkey):
    minio_obj = MinioData(accesskey, secretkey)
    certs_available = minio_obj.get_certificates_from_bucket(cluster_id, fqdn)

    master_obj = MasterData()
    hostname_prefixes = master_obj.get_fqdn_prefixes()

    print(type(certs_available))
    print(certs_available)

    cert_creation_for_list = []
    for prx in hostname_prefixes:
        if not any(f"{prx}.pool" in s for s in certs_available):
            cert_creation_for_list.append(prx)
        else:
            LOG.info(f"Certficate for {prx} hostname is available")

    write_create_certs_artifacts(cert_creation_for_list)


def update_cluster_res_usage(accesskey, secretkey):
    LOG.info("updating cluster resources")

    minio_obj = MinioData(accesskey, secretkey)
    minio_obj.download_files_from_bucket()

    cluster_obj = Cluster()
    cluster_data = cluster_obj.get_all_clusters_mongo()

    for data in cluster_data:
        kubeconfig = f"kubeconfigs/{data['cluster_id']}_kubeconfig"
        LOG.info(f"Update cluster cpu and mem {data['cluster_id']} with kubeconfig {kubeconfig}")
        cluster_obj.update_cpu_memory_realtime(data['cluster_id'], kubeconfig)


###################################----------Writing artifacts----------###################################

def write_reserve_cluster_artifacts(clusterid, namespace, fqdn, tags, ext_ip, apps, cpu, mem):
    LOG.info("Creating artifacts.properties file for installation")

    if apps == "reserve_namespace":
        reserve_namespace = "TRUE"
    else:
        reserve_namespace = "FALSE"

    cert_path = fqdn.split(".")[2]
    fqdn_parsed = (fqdn[1:])
    str_tags = " ".join(tags)
    with open(f"artifacts.properties", "w") as file:
        lines = [
            f"DEPLOYMENT_NAME={clusterid}\n"
            f"NAMESPACE={namespace}\n",
            f"DOMAIN={fqdn_parsed}\n",
            f"TAGS={str_tags}\n",
            f"SERVICE_MESH_IP={ext_ip}\n",
            f"FH_SNMP_ALARM_IP={ext_ip}\n",
            f"CERT_PATH={cert_path}\n",
            f"RESERVE_NAMESPACE={reserve_namespace}\n",
            f"APP_SET_CPU={cpu}\n",
            f"APP_SET_MEMORY={mem}\n",
            f"CLUSTER_NAME={clusterid}\n",
            f"NAMESPACE_NUMBER={namespace.split('-')[3]}\n"
        ]
        file.writelines(lines)

def write_find_expired_bookings_artifacts():
    LOG.info("Creating artifacts.properties with expired Jira details.")

    booking = Bookings()
    jira_list = booking.find_bookings_to_remove()
    if jira_list:
        LOG.info(f"Expired Bookings are : {jira_list}")
        data_list = []
        data_tuple = []
        for jira in jira_list:
            expired_booking_data = booking.find_booking_from_jira_id(jira)
            data_list.append(expired_booking_data)
        for tuple_data in data_list:
            data_tuple.append((tuple_data["jira_id"], tuple_data["namespace"], tuple_data["cluster_name"]))
        with open('expired_bookings_artifacts.json', 'w') as file:
            file.write(json_util.dumps(data_list))

        with open('expired_bookings_tuple.properties', 'w') as file:
            file.write("EXPIRED_BOOKINGS=" + str(data_tuple))
    else:
        LOG.info("No expired bookings found for tear down. Creating an entry with expired bookings equal to none.")
        with open('expired_bookings_tuple.properties', 'w') as file:
            file.write("EXPIRED_BOOKINGS=NONE")

def write_find_users_from_booking_artifacts(jira_id):
    LOG.info("Creating artifacts.properties with users from booking details.")

    booking = Bookings()
    obj = booking.find_booking_from_jira_id(jira_id)
    users = obj["team_users"]

    with open(f"users.properties", "w") as file:
        lines = [f"USERS={users}"]
        file.writelines(lines)

def write_booking_details_from_booking_artifacts(jira_id):
    LOG.info("Creating booking.properties with booking details.")

    booking = Bookings()
    booking_data = booking.find_booking_from_jira_id(jira_id)

    clusterid = booking_data['cluster_name']
    fqdn = f"*{booking_data['fqdn']}" # A '*' should be added just for the search. In mongo the FQDN is with a *.
    LOG.info(f"Cluster Name : {clusterid}")
    LOG.info(f"FQDN: {fqdn}")

    cluster_obj = Cluster()
    lb_ip = cluster_obj.get_externalIP_for_namespace(clusterid, fqdn)

    cert_path = booking_data['fqdn'].split(".")[2]

    appset_obj = validate_and_get_appset("0.0.0")
    tags = appset_obj["dimensions"][booking_data['app_set']]["app_set"]
    str_tags = " ".join(tags)

    with open(f"booking.properties", "w") as file:
        lines = [
            f"JIRA_ID={booking_data['jira_id']}\n"
            f"TEAM_NAME={booking_data['team_name']}\n",
            f"TEAM_USERS={booking_data['team_users']}\n",
            f"CLUSTER_NAME={booking_data['cluster_name']}\n",
            f"NAMESPACE={booking_data['namespace']}\n",
            f"APP_SET={booking_data['app_set']}\n",
            f"APP_TAGS={str_tags}\n",
            f"FQDN={booking_data['fqdn']}\n",
            f"CERT_PATH={cert_path}\n",
            f"IP_FOR_FQDN={lb_ip}\n",
            f"EIC_VERSION={booking_data['eic_version']}\n",
            f"BOOKING_STARTDATE={booking_data['booking_start_date']}\n",
            f"BOOKING_ENDDATE={booking_data['booking_end_date']}\n",
            f"BOOKING_STATUS={booking_data['booking_status']}\n",
            f"TEAM_EMAIL={booking_data['team_email']}\n",
            f"RESERVED_NAMESPACE_BOOKING={booking_data['reserved_namespace']}\n",
            f"NAMESPACE_NUMBER={booking_data['namespace'].split('-')[3]}\n"
            ]
        file.writelines(lines)


def write_create_certs_artifacts(cert_list):
    LOG.info("Creating certificates.properties with cert prefixes.")
    if not cert_list:
        str_prfx = "NONE"
    else:
        str_prfx = " ".join(cert_list)

    with open('certificate_prefixes.properties', 'w') as file:
        file.write("HOSTNAME_PREFIXES=" + str_prfx)

def write_cluster_lock_status_arfifacts(cluster_dict):
    LOG.info("Creating lock_status.properties with the lock status of the cluster.")

    lock_status = cluster_dict['lock_status']
    with open('lock_status.properties', 'w') as file:
        file.write("LOCK_STATUS=" + str(lock_status))




###################################----------Annotatations in namespace----------###################################


def annotate_booking(kubeconfig, namespace, jira_id, team_name, booking_start_date, booking_end_date, fqdn):
    LOG.info(f"Annotating {namespace} with booking details")

    config.load_kube_config(kubeconfig)
    k8sCoreV1Api = client.CoreV1Api()

    annotate_res = {
        "metadata":{"annotations":{
            "Jira_id": jira_id,
            "team-name": team_name,
            "booking-start-date": booking_start_date,
            "booking-end-date": booking_end_date,
            "fqdn": fqdn}}
    }

    k8sCoreV1Api.patch_namespace(name=namespace, body=annotate_res)

def remove_annotations_for_tear_down(kubeconfig, namespace):
    LOG.info(f"Annotating {namespace} with booking details")

    config.load_kube_config(kubeconfig)
    k8sCoreV1Api = client.CoreV1Api()

    annotate_res = {
        "metadata":{"annotations":{
            "Jira_id": "",
            "team-name": "",
            "booking-start-date": "",
            "booking-end-date": "",
            "fqdn": "",
            "booked": "false",
            "reserved": "false",
            "users": "",
            "eiap-version": "N/A"}}
    }
    k8sCoreV1Api.patch_namespace(name=namespace, body=annotate_res)

###################################----------Jira Utils----------###################################

def get_easy_to_read_date_format(date_string):

    # Convert the date string to a datetime object and extract the day, month, and year
    date    = datetime.strptime(date_string, "%d-%m-%Y")
    day     = date.day
    month   = date.strftime("%B")
    year    = date.year

    # Figure out suffix for the day.
    if 4 <= day <= 20 or 24 <= day <= 30:
        return f"{day}th {month} {year}"
    else:
        suffixes = {1: "st", 2: "nd", 3: "rd"}
        return f"{day}{suffixes.get(day % 10, 'th')} {month} {year}"

def create_pipeline_details_table(eic_helmfile_version, spinnaker_pipeline_execution, jenkins_job_build_number):

    table_header = "||Pipeline Execution, Site Value and Certificate files||Links||"
    table_rows   = [
        f"|*Spinnaker*|[Spinnaker Initial Install Pipeline Execution|{spinnaker_pipeline_execution}]|",
        f"|*Jenkins*|[Helmfile Deploy Jenkins Job|{values.HELMFILE_DEPLOY_JENKINS_JOB}{jenkins_job_build_number}]|",
        f"|*Site-Values files*|Please see attached site_values_{eic_helmfile_version}.yaml file or navigate to the above helmfile-deploy jenkins job.|",
        f"|*Certificate files*|Please contact team regarding certificates.|"
    ]
    complete_table = f"{table_header}\n" + "\n".join(table_rows)
    return f"{{panel:title=Spinnaker Pipeline and Helmfile Deploy Jenkins Job Information|borderStyle=solid|borderColor=#ccc|titleBGColor=#1c8ef5|bgColor=#e8f3fe}}{complete_table}{{panel}}"

def create_installation_details_table(jira_id, team_name, program, project_manager, approved, cluster_name, namespace, domain, eic_version, booking_start_date, booking_end_date):

    grafana_url  = f"{values.GRAFANA_CCD_RESOURCE_DASHBOARD}{cluster_name}&var-Namespace={namespace.lstrip('.')}&from=now-1h&to=now"
    table_header = "||Booking Details||Information||"
    table_rows   = [
        f"|*Ticket Number*|[{jira_id}|{values.JIRA_URL}/browse/{jira_id}]|",
        f"|*Program*|{program}|",
        f"|*Team*|{team_name}|",
        f"|*Project Manager*|{project_manager}|",
        f"|*Approved*|{approved}|",
        f"|*Start Date*|{get_easy_to_read_date_format(booking_start_date)}|",
        f"|*Timebox End Date*|{get_easy_to_read_date_format(booking_end_date)}|",
        f"|*Cluster Name*|{cluster_name}|",
        f"|*Namespace*|{namespace.lstrip('.')}|",
        f"|*Domain*|{domain}|",
        f"|*EIC Version Installed*|{eic_version}|",
        f"|*Grafana Dashboard*|[Grafana CCD Resource Allocation Dashboard for Cluster {cluster_name} and Namepace {namespace.lstrip('.')}|{grafana_url}]|",
        f"|*Log Viewer*|gas{domain}|"
    ]
    complete_table = f"{table_header}\n" + "\n".join(table_rows)
    return f"{{panel:title=Booking Details|borderStyle=solid|borderColor=#ccc|titleBGColor=#1c8ef5|bgColor=#e8f3fe}}{complete_table}{{panel}}"

def create_team_users_details_table(team_users, booking_start_date, booking_end_date):
    booking_start_date = get_easy_to_read_date_format(booking_start_date)
    booking_end_date   = get_easy_to_read_date_format(booking_end_date)

    table_header    = "||Team Member Name||Team Member Email||Team Member Signum||Access"
    table_rows      = [f"|*{user[0]}*|{user[1]}|{user[2]}|{booking_start_date} - {booking_end_date}" for user in team_users]

    complete_table = f"{table_header}\n" + "\n".join(table_rows)
    return f"{{panel:title=List of Team Members granted Administrator access to the namespace for allocated time period|borderStyle=solid|borderColor=#ccc|titleBGColor=#1c8ef5|bgColor=#e8f3fe}}{complete_table}{{panel}}"

def create_how_to_guide_details(namespace):

    namespace_less_dot = namespace.lstrip(".")

    table_header1 = "||How To Guides||Confluence Links||"
    table_rows1 = [
        f"|*{values.ORDER}*|{values.ORDER_ACCESS_CONFLUENCE}|",
        f"|*{values.TROUBLESHOOT}*|{values.TROUBLESHOOT_CONFLUENCE}|"
    ]
    complete_table1 = f"{table_header1}\n" + "\n".join(table_rows1)

    table_header2 = "||Rancher Support||Information||"
    table_rows2 = [
        f"|*Rancher*|{values.RANCHER}|",
        f"|*IDM*|{values.IDM_ROLE_URL}|"
    ]
    complete_table2 = f"{table_header2}\n" + "\n".join(table_rows2)

    table_header3 = "||User Group||Name||"
    table_rows3 = [
        f"|*User Group*|{values.USER_GROUP}{namespace_less_dot}|"
    ]
    complete_table3 = f"{table_header3}\n" + "\n".join(table_rows3)

    table_header4 = "||Support with booking||Support Template||"
    table_rows4 = [
        f"|*Clone the support template*|{values.TEMPLATE}|"
    ]
    complete_table4 = f"{table_header4}\n" + "\n".join(table_rows4)

    table_header5 = "||Access||Roles required and allocated time period||"
    table_rows5 = [
        f"|*Access*|{values.IDM_APPLIED_FOR}|",
        f"|*Granted Access Period*|{values.ACCESS}|"
    ]
    complete_table5 = f"{table_header5}\n" + "\n".join(table_rows5)

    return f"{{panel:title=Additional Links and How to Guides|borderStyle=solid|borderColor=#ccc|titleBGColor=#1c8ef5|bgColor=#e8f3fe}}{complete_table1}\n{complete_table2}\n{complete_table3}\n{complete_table4}\n{complete_table5}{{panel}}"

############################################################################################################