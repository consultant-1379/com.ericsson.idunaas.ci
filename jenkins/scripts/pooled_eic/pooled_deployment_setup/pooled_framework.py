from pooled_deployment_setup.clusterCollectionData import Cluster
from pooled_deployment_setup.dimensions import Dimensions
from pooled_deployment_setup.bookings import Bookings
from pooled_deployment_setup import utils
from pooled_deployment_setup.jira import Jira
import json
import click
import logging
import traceback
import sys
import datetime

logging.basicConfig(
    level=logging.INFO)    # Level of the Root logger

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

def bookings_json_path_option(func):
    """A decorator for the file name of the bookings json file via command line argument."""
    return click.option('--bookings-file', type=click.STRING, required=False,
                        help='file name of the bookings json file'
                        )(func)

def dimensions_json(func):
    """A decorator for passing in the dimensions json via command line argument."""
    return click.option('--dimensions', type=click.STRING, required=False,
                        help='file name of the dimensions json file'
                        )(func)

def cluster_json(func):
    """A decorator for passing in the cluster json via command line argument."""
    return click.option('--cluster_data', type=click.STRING, required=False,
                        help='file name of the cluster json file'
                        )(func)

def kubeconfig(func):
    """A decorator for passing in the kubeconfig command line argument."""
    return click.option('--kubeconfig', type=click.STRING, required=False,
                        help='kubeconfig file'
                        )(func)

def kubeconfig_dir_path(func):
    """A decorator for passing in the directory for kubeconfigs in command line argument."""
    return click.option('--kubeconfig_dir', type=click.STRING, required=False,
                        help='kubeconfig directory'
                        )(func)

def cluster(func):
    """A decorator for passing in the clustername command line argument."""
    return click.option('--clusterid', type=click.STRING, required=False,
                        help='cluster ID'
                        )(func)

def app_set(func):
    """A decorator for passing in the app set via command line argument."""
    return click.option('--app-set', type=click.STRING, required=False,
                        help='app_set'
                        )(func)

def eic_helmfile_version(func):
    """A decorator for passing in the app set via command line argument."""
    return click.option('--helmfile-version', type=click.STRING, required=False,
                        help='app_set'
                        )(func)

def update_key(func):
    """A decorator for passing in the update key via command line argument."""
    return click.option('--key', type=click.STRING, required=False,
                        help='To update a collection with the key.'
                        )(func)

def update_str_value(func):
    """A decorator for passing in the String value to update a collection via command line argument."""
    return click.option('--str_value', type=click.STRING, required=False,
                        help='To update a collection with the string value.'
                        )(func)


def lock_status(func):
    """A decorator for passing in the lock status via command line argument."""
    return click.option('--lock-status', type=click.BOOL, required=False,
                        help='lock_status'
                        )(func)

def is_exclusive_clust(func):
    """A decorator for passing whether the install is an exclusive cluster install."""
    return click.option('--exclusive', type=click.STRING, required=False,
                        help='Condition to check whether the install is running on a exclusive cluster'
                        )(func)

def namespace(func):
    """A decorator for passing in the namespace via command line argument."""
    return click.option('--namespace', type=click.STRING, required=False,
                        help='the namespace'
                        )(func)

def dedicated_namespace(func):
    """A decorator for passing in the dedicated namespace for get-cluster method via command line argument."""
    return click.option('--dedicated_namespace', type=click.STRING, required=False,
                        help='the dedicated namespace used in reserved cluster jenkinsfile to pass a dedicated namespace'
                        )(func)

def domain_name(func):
    """A decorator for passing in the fqdn via command line argument."""
    return click.option('--domain', type=click.STRING, required=False,
                        help='the FQDN'
                        )(func)

def setOrRemoveExclusive(func):
    """A decorator for setting the cluster exclusive or removing exclusivity."""
    return click.option('--action', type=click.STRING, required=False,
                        help='Setting or removing cluster as exclusive.'
                        )(func)

def minio_accesskey(func):
    """A decorator for passing in the minio access key via command line argument."""
    return click.option('--minioaccess', type=click.STRING, required=False,
                        help='the minio access key'
                        )(func)

def minio_secretkey(func):
    """A decorator for passing in the minio secret key via command line argument."""
    return click.option('--miniosecret', type=click.STRING, required=False,
                        help='the minio secret key'
                        )(func)

#------------------------------------- Jira options -------------------------------------

def jira_id(func):
    """A decorator for passing in the jira id status via command line argument."""
    return click.option('--jira-id', type=click.STRING, required=False,
                        help='jira_id'
                        )(func)

def comment(func):
    """A decorator for passing in the jira comment via command line argument."""
    return click.option('--comment', type=click.STRING, required=False,
                        help='comment'
                        )(func)

def path_to_attachment(func):
    """A decorator for passing in path to jira attachment via command line argument."""
    return click.option('--path-to-attachment', type=click.STRING, required=False,
                        help='path_to_attachment'
                        )(func)

def jenkins_build_url(func):
    """A decorator for passing in path to jenkins job build url to the jira via command line argument."""
    return click.option('--jenkins-build-url', type=click.STRING, required=False,
                        help='jenkins_build_url'
                        )(func)

def artifact_name(func):
    """A decorator for passing in path to the jenkins build artifact to the jira via command line argument."""
    return click.option('--artifact-name', type=click.STRING, required=False,
                        help='artifact_name'
                        )(func)

def team_users(func):
    """A decorator for passing in a string of team users to add to the jira via command line argument."""
    return click.option('--team-users', type=click.STRING, required=False,
                        help='team_users'
                        )(func)

def start_date(func):
    """A decorator for passing in a string of start date to add to the jira via command line argument."""
    return click.option('--start-date', type=click.STRING, required=False,
                        help='start_date'
                        )(func)

def end_date(func):
    """A decorator for passing in a string of end date to add to the jira via command line argument."""
    return click.option('--end-date', type=click.STRING, required=False,
                        help='end_date'
                        )(func)

def transition_to(func):
    """A decorator for passing in the state to transition the jira to via command line argument."""
    return click.option('--transition-to', type=click.STRING, required=False,
                        help='transition_to'
                        )(func)

def jira_json_path_option(func):
    """A decorator for the file name of the jira json file via command line argument."""
    return click.option('--jira-file', type=click.STRING, required=False,
                        help='file name of the jira json file'
                        )(func)

def spinnaker_pipeline_execution(func):
    """A decorator for passing in the spinnaker pipeline execution url to the jira to via command line argument."""
    return click.option('--spinnaker-pipeline-execution', type=click.STRING, required=False,
                        help='spinnaker_pipeline_execution'
                        )(func)

def jenkins_job_build_number(func):
    """A decorator for passing in the helmfile deploy jenkins job build number to the jira to via command line argument."""
    return click.option('--jenkins-job-build-number', type=click.STRING, required=False,
                        help='jenkins_job_build_number'
                        )(func)

@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Pooled deployment manager."""


#####################------Booking Methods------#####################

@cli.command('add-booking')
@kubeconfig
@bookings_json_path_option
def add_booking(kubeconfig, bookings_file):

    LOG.info("reading booking json file")
    try:

        with open(bookings_file) as file:
            file_obj = json.load(file)

        booking = Bookings()
        booking.insert_bookings(**file_obj)

        utils.annotate_booking(
            kubeconfig,
            file_obj["namespace"],
            file_obj["jira_id"],
            file_obj["team_name"],
            file_obj["booking_start_date"],
            file_obj["booking_end_date"],
            file_obj["fqdn"])

    except Exception as e:
        LOG.error('Add booking failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Booking added successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)


@cli.command('find-expired-bookings')
def find_expired_booking():

    LOG.info("Finding booking to be removed")
    try:

        utils.write_find_expired_bookings_artifacts()

    except Exception as e:
        LOG.error('Finding expired bookings failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('find expired booking methods ran successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)


@cli.command('remove-booking')
@jira_id
def remove_booking(jira_id):
    LOG.info(f"Removing booking for Jira ID : {jira_id}")
    try:

        key = "booking_status"
        value = "EXPIRED"
        booking = Bookings()
        # booking.set_booking_to_expire(jira_id)
        booking.update_booking_values(jira_id, key, value)

    except Exception as e:
        LOG.error('Updating the booking status failed.')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Method executed successfully.')
        exit_code = 0
    finally:
        sys.exit(exit_code)


@cli.command('get-users-from-booking')
@jira_id
def get_users_from_booking(jira_id):
    LOG.info(f"Getting users in booking for Jira ID : {jira_id}")
    try:

        utils.write_find_users_from_booking_artifacts(jira_id)

    except Exception as e:
        LOG.error('Updating the users in artifacts has failed.')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Method executed successfully.')
        exit_code = 0
    finally:
        sys.exit(exit_code)



@cli.command('get-booking-details')
@jira_id
def get_booking_details(jira_id):
    LOG.info(f"Getting booking details for Jira ID : {jira_id}")
    try:

        utils.write_booking_details_from_booking_artifacts(jira_id)

    except Exception as e:
        LOG.error('Updating the booking details in artifacts has failed.')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Method executed successfully.')
        exit_code = 0
    finally:
        sys.exit(exit_code)



# @cli.command('update-booking-helmfile-version')
# @jira_id
# @eic_helmfile_version
# def update_booking_eic_version(jira_id, helmfile_version):

#     LOG.info(f"Reading booking from Jira ID {jira_id}")
#     try:
#         key = "eic_version"
#         value = helmfile_version

#         booking = Bookings()
#         booking.update_booking_values(jira_id, key, value)

#     except Exception as e:
#         LOG.error('Update booking failed with the following error')
#         LOG.debug(traceback.format_exc())
#         LOG.error(e)
#         exit_code = 1

#     else:
#         LOG.info('Booking updated successfully')
#         exit_code = 0
#     finally:
#         sys.exit(exit_code)



@cli.command('update-booking-namespace-annotations')
@kubeconfig
@jira_id
def annotate_namespace(kubeconfig, jira_id):

    LOG.info(f"Reading booking from Jira ID {jira_id}")
    try:
        booking = Bookings()
        booking_data = booking.find_booking_from_jira_id(jira_id)
        LOG.info(f"Annotating namespace with current booking details for Jira ID {jira_id} which was removed in re-installation.")

        utils.annotate_booking(
                kubeconfig,
                booking_data["namespace"],
                jira_id,
                booking_data["team_name"],
                booking_data["booking_start_date"],
                booking_data["booking_end_date"],
                booking_data["fqdn"])

    except Exception as e:
        LOG.error('Update booking failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Booking updated successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)



# @cli.command('update-booking-end-date')
# @jira_id
# @extended_end_date
# def update_booking_end_date(jira_id, end_date):

#     LOG.info(f"Reading booking from Jira ID {jira_id}")
#     try:
#         end_date_parsed = datetime.datetime.strptime(end_date, '%d-%m-%Y')
#         end_date_obj = end_date_parsed + datetime.timedelta(days=2)

#         key = "booking_end_date"
#         value = end_date_obj

#         booking = Bookings()
#         booking.update_booking_values(jira_id, key, value)

#     except Exception as e:
#         LOG.error('Update booking failed with the following error')
#         LOG.debug(traceback.format_exc())
#         LOG.error(e)
#         exit_code = 1

#     else:
#         LOG.info('Booking updated successfully')
#         exit_code = 0
#     finally:
#         sys.exit(exit_code)



@cli.command('update-booking-values')
@jira_id
@update_key
@update_str_value
def update_booking_values(jira_id, key, str_value):

    LOG.info(f"Reading booking from Jira ID {jira_id}. Updating KEY : {key} with VALUE {str_value}.")
    try:
        if key == "booking_end_date":
            date_parsed = datetime.datetime.strptime(str_value, '%d-%m-%Y')
            date_obj = date_parsed + datetime.timedelta(days=2)
            update_value = date_obj
        else:
            update_value = str_value

        booking = Bookings()
        booking.update_booking_values(jira_id, key, update_value)

    except Exception as e:
        LOG.error('Update booking failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Booking updated successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)


#####################------Diemension Methods------#####################

@cli.command('add-dimensions')
@dimensions_json
def add_dimensions(dimensions):

    LOG.info("reading booking json file")
    try:
        with open(dimensions) as file:
            file_obj = json.load(file)

        dimension = Dimensions()
        dimension.add_dimensions(file_obj)

    except Exception as e:
        LOG.error('Add dimensions failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info('Dimensions added successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)


#####################------Cluster Operational Methods------#####################

@cli.command('update-cluster-res-all-clusters')
@minio_accesskey
@minio_secretkey
def update_cluster_resources_all_clusters(minioaccess, miniosecret):
    LOG.info("Updating cluster")

    try:
        # cluster_obj = Cluster()
        # cluster_obj.update_cpu_memory_realtime(clusterid, kubeconfig)
        utils.update_cluster_res_usage(minioaccess, miniosecret)

    except Exception as e:
        LOG.error('Updating cluster resources in Clusters collection failed.')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        exit_code = 0
    finally:
        sys.exit(exit_code)


@cli.command('update-cluster-res')
@cluster
@kubeconfig
def update_single_cluster_resources(clusterid, kubeconfig):
    LOG.info("Updating cluster")

    try:
        cluster_obj = Cluster()
        cluster_obj.update_cpu_memory_realtime(clusterid, kubeconfig)


    except Exception as e:
        LOG.error('Updating cluster resources in Clusters collection failed.')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        exit_code = 0
    finally:
        sys.exit(exit_code)


@cli.command('create-all-clusters')
@cluster_json
def create_all_clusters(cluster_data):
    LOG.info("Creating all clusters")

    try:
        with open(cluster_data) as file:
            file_obj = json.load(file)

            clusters = Cluster()
            clusters.create_clusters(file_obj['cluster_id'])

    except Exception as e:
        LOG.error('Add clusters failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Clusters added successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)


@cli.command('create-cluster')
@cluster
def create_clusters(clusterid):
    LOG.info("Creating the cluster")

    try:
        cluster = Cluster()
        cluster_data = cluster.get_cluster_data_from_ews(clusterid)
        cluster.create_single_cluster(cluster_data)

    except Exception as e:
        LOG.error('Add cluster failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Cluster added successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)

@cli.command('remove-cluster')
@cluster
def remove_clusters(clusterid):
    LOG.info("Removing the cluster")

    try:
        cluster = Cluster()
        cluster.remove_single_cluster(clusterid)

    except Exception as e:
        LOG.error('Remove cluster failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info('Cluster removed successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)


@cli.command('get-cluster')
@app_set
@eic_helmfile_version
@kubeconfig_dir_path
@is_exclusive_clust
@dedicated_namespace
def select_cluster_for_install(app_set, helmfile_version, kubeconfig_dir, exclusive, dedicated_namespace):
    LOG.info("Verifying used CPU and memory data in prometheus and validating against mongodb")

    try:
        appset_obj = utils.validate_and_get_appset(helmfile_version)
        app_set_cpu = appset_obj["dimensions"][app_set]["cpu"]
        app_set_mem = appset_obj["dimensions"][app_set]["memory"]
        tags = appset_obj["dimensions"][app_set]["app_set"]

        LOG.info(f"App-Set total CPU :  {app_set_cpu}")
        LOG.info(f"App-Set total Memory : {app_set_mem}")

        cluster_result = Cluster()
        if exclusive == "true" and dedicated_namespace == "N/A" and app_set != "reserve_namespace":
            LOG.info("Entering Exclusive cluster methods")
            cluster_result_val = cluster_result.get_exclusive_clusters()
            if not cluster_result_val:
                raise Exception("No exclusive clusters found. Please set the clusters as Exclusive before running the II")

            namespace, fqdn, ip, cluster = cluster_result.verify_exclusive_cluster(cluster_result_val, kubeconfig_dir) # Kubeconfig path kubeconfig = f"{kubeconfig_dir}/{cluster}_kubeconfig" is done inside this method.

        elif exclusive == "false":
            LOG.info("Entering normal II reserve cluster methods")
            cluster_data_dict = cluster_result.get_cluster_based_on_app_set(app_set_cpu, app_set_mem, kubeconfig_dir, dedicated_namespace) # Kubeconfig path kubeconfig = f"{kubeconfig_dir}/{cluster}_kubeconfig" is done inside this method.
            cluster = cluster_data_dict['cluster']
            namespace = cluster_data_dict['namespace']
            fqdn = cluster_data_dict['fqdn']
            ip = cluster_data_dict['ip']

        else:
            raise Exception("Wrong combination of inputs. Please check Exclusive, dedicated_ns reserve namespace input params.")

        set_lock_status = True
        key = "lock_status"
        cluster_result.update_cluster_fields(cluster, key, set_lock_status)

        utils.write_reserve_cluster_artifacts(cluster, namespace, fqdn, tags, ip, app_set, app_set_cpu, app_set_mem)

    except Exception as e:
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info("Cluster data required for II or UG is stored in artifacts.properties.")
        exit_code = 0

    finally:
        sys.exit(exit_code)


@cli.command('set-lockstatus')
@lock_status
@cluster
def updat_cluster_lock_status(lock_status, clusterid):
    LOG.info(f"Updating lock status for cluster {clusterid}")
    try:
        cluster = Cluster()
        key = "lock_status"
        cluster.update_cluster_fields(clusterid, key, lock_status)

    except Exception as e:
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info("Executed successfully")
        exit_code = 0

    finally:
        sys.exit(exit_code)


@cli.command('check-lockstatus')
@cluster
def check_lock_status(clusterid):
    LOG.info(f"Checking lock status for cluster {clusterid}")
    try:
        cluster = Cluster()
        cluster_data = cluster.get_cluster_mongo(clusterid)
        utils.write_cluster_lock_status_arfifacts(cluster_data)

    except Exception as e:
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info("Executed successfully")
        exit_code = 0

    finally:
        sys.exit(exit_code)


@cli.command('remove-annotations')
@kubeconfig
@namespace
def remove_annotation_tear_down(kubeconfig, namespace):

    LOG.info(f"Removing annotations in namespace {namespace}")
    try:
        utils.remove_annotations_for_tear_down(kubeconfig, namespace)

    except Exception as e:
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info("Removing annotations are successfull.")
        exit_code = 0

    finally:
        sys.exit(exit_code)


@cli.command('check-certs')
@cluster
@domain_name
@minio_accesskey
@minio_secretkey
def check_certs(clusterid, domain, minioaccess, miniosecret):

    LOG.info(f"Checking  certs for {domain} in cluster {clusterid}")
    try:
        utils.check_certs_exists(clusterid, domain, minioaccess, miniosecret)

    except Exception as e:
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info("Certs check is successfull")
        exit_code = 0

    finally:
        sys.exit(exit_code)


@cli.command('set-cluster-exclusive')
@setOrRemoveExclusive
@cluster
@kubeconfig
def set_or_remove_exclusive_cluster(action, clusterid, kubeconfig):

    try:
        utils.set_cluster_exclusive(action, clusterid, kubeconfig)

    except Exception as e:
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1

    else:
        LOG.info("Method executed successfully.")
        exit_code = 0

    finally:
        sys.exit(exit_code)


#####################------Jira Methods------#####################
@cli.command('validate-jira-team-user-ids')
@team_users
def validate_jira_team_user_ids(team_users):
    LOG.info(f"Validating team user id's before proceeding.")

    invalid_ids = []
    found_invalid_ids = False

    try:
        jira = Jira(jira_id)
        jira_conn = jira.getJiraConnection()

        for team_user in team_users.split(','):
            try:
                jira_conn.user(id=team_user.lower())
            except Exception as e:
                found_invalid_ids = True
                invalid_ids.append(team_user)
        if found_invalid_ids:
            raise Exception(f"Invalid team user id's found: {invalid_ids}")
    except Exception as e:
        LOG.error(f"Problem trying to validate team user id's. Please investigate")
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info(f"Validation of team user id's successful.")
        exit_code = 0
    finally:
        sys.exit(exit_code)

@cli.command('add-jira-comment')
@jira_id
@comment
def add_jira_comment(jira_id, comment):
    LOG.info(f"Adding comment: {comment} to jira: {jira_id}.")
    try:
        jira = Jira(jira_id)
        jira.add_comment(comment)
    except Exception as e:
        LOG.error(f"Adding comment to jira {jira_id} failed with the following error")
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info('Added jira comment successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)

@cli.command('add-jira-pipeline-details')
@jira_id
@eic_helmfile_version
@spinnaker_pipeline_execution
@jenkins_job_build_number
def add_jira_pipeline_details(jira_id, helmfile_version, spinnaker_pipeline_execution, jenkins_job_build_number):
    LOG.info(f"Adding pipeline details to jira: {jira_id}.")
    try:
        jira = Jira(jira_id)
        jira.add_comment(utils.create_pipeline_details_table(helmfile_version, spinnaker_pipeline_execution, jenkins_job_build_number))
    except Exception as e:
        LOG.error(f"Adding pipeline details comment to jira {jira_id} failed with the following error.")
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info('Added pipeline details comment successfully.')
        exit_code = 0
    finally:
        sys.exit(exit_code)

@cli.command('add-jira-installation-details')
@jira_id
@jira_json_path_option
def add_jira_installation_details(jira_id, jira_file):
    LOG.info(f"Adding installation details to jira: {jira_id}.")
    try:
        with open(jira_file) as file:
            file_obj = json.load(file)

        jira = Jira(jira_id)
        jira.add_comment(utils.create_installation_details_table(**file_obj))
    except Exception as e:
        LOG.error(f"Adding installation details comment to jira {jira_id} failed with the following error.")
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info('Added installation details comment successfully.')
        exit_code = 0
    finally:
        sys.exit(exit_code)

@cli.command('add-jira-team-users-details')
@jira_id
@team_users
@start_date
@end_date
def add_jira_team_users_details(jira_id, team_users, start_date, end_date):
    LOG.info(f"Adding team users {team_users} detail to jira: {jira_id}.")

    try:
        full_names, emails = [], []
        jira = Jira(jira_id)
        jira_conn = jira.getJiraConnection()

        for team_user in team_users.split(','):
            try:
                user = jira_conn.user(id=team_user.lower())
                full_names.append(user.displayName)
                emails.append(user.emailAddress)
            except Exception as e:
                full_names.append(f"Could not find valid full name for user with id {team_user}")
                emails.append('N/A')
        jira.add_comment(utils.create_team_users_details_table(list(zip(full_names, emails, team_users.lower().split(','))), start_date, end_date))
    except Exception as e:
        LOG.error(f"Adding team users details comment to jira {jira_id} failed with the following error")
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info('Added team users details comment successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)

@cli.command('add-jira-how-to-guide-details')
@jira_id
@namespace
def add_jira_how_to_guide_details(jira_id, namespace):
    LOG.info(f"Adding how to guide details to to jira: {jira_id}.")
    try:
        jira = Jira(jira_id)
        jira.add_comment(utils.create_how_to_guide_details(namespace))
    except Exception as e:
        LOG.error(f"Adding how to guide details to jira {jira_id} failed with the following error")
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info('Added how to guide details comment successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)

@cli.command('add-jira-attachment')
@jira_id
@path_to_attachment
def add_jira_attachment(jira_id, path_to_attachment):
    LOG.info(f"Adding attachment: {path_to_attachment} to jira: {jira_id}.")
    try:
        jira = Jira(jira_id)
        jira.add_attachment(path_to_attachment)
    except Exception as e:
        LOG.error(f"Adding attachment to jira {jira_id} failed with the following error")
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info('Added jira attachment successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)

@cli.command('transition-jira-to')
@jira_id
@transition_to
def transition_jira_to(jira_id, transition_to):
    LOG.info(f"Transitioning jira: {jira_id} to {transition_to}")
    try:
        jira = Jira(jira_id)
        jira.transition_to(transition_to)
    except Exception as e:
        LOG.error(f"Transitioning jira {jira_id} to {transition_to} failed with the following error")
        LOG.debug(traceback.format_exc())
        LOG.error(e)
        exit_code = 1
    else:
        LOG.info('Transitioned jira successfully')
        exit_code = 0
    finally:
        sys.exit(exit_code)
