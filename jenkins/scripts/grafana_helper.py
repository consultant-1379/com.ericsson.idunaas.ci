import logging
import argparse
import datetime
import requests
import json
from pathlib import Path

LOG = logging.getLogger('grafana_helper')


def initialize_logging(name="default", log_level="INFO"):
    log_format = "[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s "
    log_file_path = _log_file_path(name)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(log_format))
    if log_level == "INFO":
        stream_handler.setLevel('INFO')
        logging.basicConfig(filename=log_file_path, format=log_format, level=logging.INFO)
        LOG.info("Log level set to INFO")
    elif log_level == "WARNING":
        stream_handler.setLevel('WARNING')
        logging.basicConfig(filename=log_file_path, format=log_format, level=logging.WARNING)
        LOG.warning("Log level set to WARNING")
    elif log_level == "ERROR":
        stream_handler.setLevel('ERROR')
        logging.basicConfig(filename=log_file_path, format=log_format, level=logging.ERROR)
        LOG.error("Log level set to ERROR")
    else:
        stream_handler.setLevel('DEBUG')
        logging.basicConfig(filename=log_file_path, format=log_format, level=logging.DEBUG)
        LOG.info("Log level set to DEBUG")
    logging.getLogger('').addHandler(stream_handler)
    return logging.getLogger('')


def _log_file_path(name):
    absolute_log_directory = Path.cwd() / Path('logs')
    absolute_log_directory.mkdir(parents=True, exist_ok=True)
    LOG.info(f"Logging to {absolute_log_directory}")
    return str(Path(absolute_log_directory) / datetime.datetime.now().strftime(
        f'%Y-%m-%dT%H_%M_%S%z_{name}_grafana_helper.py.log'))


def http_request(action="GET",
                 api_endpoint=None,
                 request_body=None,
                 api_token=None,
                 user=None, pwd=None,
                 log_level="INFO"):
    result = ""
    grafana_url = f"http://150.132.8.132:3000/{api_endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }

    try:
        if action == "GET":
            response = requests.get(
                url=grafana_url,
                headers=headers,
                verify=False
            )
        elif action == "POST":
            response = requests.post(
                url=grafana_url,
                headers=headers,
                data=request_body,
                verify=False
            )
    except requests.exceptions.RequestException as err:
        error_msg = f"Get request to {grafana_url} failed. Error body is: {str(err)}"
        LOG.error(error_msg)
        status_code = 500
        return status_code, result
    try:
        result = json.loads(response.text)
    except ValueError:
        # Fallback to returning the full response if the JSON response is malformed
        result = response.text

    resp_status = response.status_code
    if log_level == "DEBUG":
        result_json_str = json.dumps(result, indent=4, sort_keys=True)
        LOG.info(f"HTTP request status = {resp_status}, response body: = {result_json_str}")
    else:
        LOG.info(f"HTTP request status = {resp_status}")

    return resp_status, result


def create_datasource(datasource_name=None,
                      datasource_fqdn=None,
                      api_token=None,
                      user=None, pwd=None,
                      log_level="INFO"):
    LOG.info(
        f"Preparing to create datasource via POST request for panel with name '{datasource_name}' and FQDN {datasource_fqdn}")

    datasource_json_tmpl_data = {
        "name": datasource_name,
        "type": "prometheus",
        "typeLogoUrl": "",
        "access": "proxy",
        "url": datasource_fqdn,
        "password": "",
        "user": "",
        "database": "",
        "basicAuth": False,
        "basicAuthUser": "",
        "basicAuthPassword": "",
        "withCredentials": False,
        "isDefault": False,
        "jsonData": {
            "httpMethod": "POST",
            "tlsSkipVerify": True
        }
    }

    payload_str = json.dumps(datasource_json_tmpl_data, indent=2)
    LOG.debug(f"JSON payload for datasource creation request: {payload_str}")

    create_datasource_request_body = json.dumps(datasource_json_tmpl_data)
    LOG.info(f"Sending POST request to create the datasource...")
    create_datasource_raw_response = http_request(
        action="POST",
        api_endpoint="api/datasources",
        request_body=create_datasource_request_body,
        api_token=api_token,
        user=user, pwd=pwd,
        log_level=log_level
    )
    LOG.info("Done.")
    create_datasource_response = create_datasource_raw_response[1]
    datasource_create_response_body = json.loads(
        json.dumps(create_datasource_response, indent=4, sort_keys=True)
    )
    datasource_create_status = create_datasource_raw_response[0]
    if datasource_create_status == 409:
        LOG.error("data source with the same name already exists")
        exit(1)
    if datasource_create_status == 401:
        LOG.error("Invalid credentials")
        exit(1)
    elif datasource_create_status != 200:
        LOG.error(f"Datasource creation failed with status code {datasource_create_status}")
        exit(1)
    elif datasource_create_status == 200:
        datasource_id = datasource_create_response_body["datasource"]["id"]
        datasource_uid = datasource_create_response_body["datasource"]["uid"]
        LOG.info(
            f"Datasource '{datasource_name}' was created successfully with ID {datasource_id}, UID {datasource_uid}")
        return True

    '''Temporarily disabling the data source health check step as datasource health checks are only supported in 
    Grafana versions v9.0.x and v9.1.x health_check_datasource( datasource_id, datasource_name, datasource_fqdn, 
    api_token ) '''


# def health_check_datasource(datasource_id=None,
#                             datasource_name=None,
#                             datasource_fqdn=None,
#                             api_token=None):
#     LOG.info(f"Preparing to do a health check on the datasource {datasource_name} with ID '{datasource_id}'")
#     health_check_endpoint = f"api/datasources/{datasource_id}/health"
#     health_check_raw_response = http_request(
#         action="GET",
#         api_endpoint=health_check_endpoint,
#         request_body=None,
#         api_token=api_token,
#         user=user, pwd=pwd,
#         log_level=log_level
#     )
#     health_check_response = health_check_raw_response[1]
#     health_check_response_body = json.loads(
#         json.dumps(health_check_response, indent=4, sort_keys=True)
#     )
#     if health_check_response_body["status"] == "OK":
#         LOG.info(f"Health check for datasource '{datasource_name}' at {datasource_fqdn} passed")
#         return True
#     else:
#         LOG.error(
#             f"The health check did not return the expected response. Please check that the datasource "
#             f"'{datasource_name}' at {datasource_fqdn} is available and serving logs to Grafana "
#         )
#         exit(1)


def get_dashboard_uid_from_name(dashboard_name=None, api_token=None, user=None, pwd=None, log_level="INFO"):
    LOG.info(f"Searching for dashboard '{dashboard_name}' in Grafana")
    dashboard_search_response_obj = \
        json.loads(
            json.dumps(
                http_request(
                    action="GET",
                    api_endpoint="api/search?query=%",
                    request_body=None,
                    api_token=api_token,
                    user=user, pwd=pwd,
                    log_level=log_level
                )[1],
                indent=4, sort_keys=True
            )
        )
    dashboard_uid = None
    # Iterate over the search results for the dashboard UID
    for i in range(len(dashboard_search_response_obj)):
        if dashboard_search_response_obj[i]["title"] == dashboard_name:
            dashboard_uid = dashboard_search_response_obj[i]["uid"]
            LOG.info(
                f"Found dashboard '{dashboard_name}' with UID {dashboard_uid}".format(dashboard_name, dashboard_uid))
            return dashboard_uid
    if dashboard_uid is None:
        LOG.error(f"No UID matching the dashboard name '{dashboard_name}' was found")
        exit(1)


def get_target_index_in_dict(input_dict=None, target_key=None):
    LOG.info(f"Searching for target key '{target_key}' within input dict")
    target_index = None
    for i in range(len(input_dict)):
        if input_dict[i][f"{target_key}"] == target_index:
            target_index = input_dict[i][f"{target_key}"]
            LOG.info(f"Found target key '{target_key}'")
            return target_index
    if target_index is None:
        LOG.error("Could not find the index of the given target key within the provided dictionary")
        exit(1)


def update_dashboard_model(eiapaas_env=None,
                           dashboard_name=None,
                           oss_namespace_name=None,
                           api_token=None,
                           user=None, pwd=None,
                           log_level="INFO"):
    dashboard_uid = get_dashboard_uid_from_name(dashboard_name=dashboard_name, api_token=api_token, user=user, pwd=pwd,
                                                log_level=log_level)
    target_dashboard_endpoint = f"api/dashboards/uid/{dashboard_uid}"

    LOG.info(f"Preparing to update dashboard '{dashboard_name}' with panel for EIAPaaS environment '{eiapaas_env}'")
    LOG.info(f"The OSS namespace name for this deployment is: {oss_namespace_name}")
    LOG.info(f"The dashboard UID is: {dashboard_uid}")
    LOG.info(f"Fetching target dashboard JSON...")

    dashboard_json_obj = \
        json.loads(
            json.dumps(
                http_request(
                    action="GET",
                    api_endpoint=target_dashboard_endpoint,
                    request_body=None,
                    api_token=api_token,
                    user=user, pwd=pwd,
                    log_level=log_level
                )[1],
                indent=4, sort_keys=True
            )
        )
    LOG.info(f"Done.")

    dashboard_variables = dashboard_json_obj["dashboard"]["templating"]["list"]

    json_out = json.dumps(dashboard_json_obj, indent=4, sort_keys=True)
    LOG.debug(f"Full JSON for the dashboard to be updated: \n {json_out}")

    # Find the namespace variable within the list of template variables
    namespace_variable_index = None
    LOG.info(f"Looking for the namespace variable in the dashboard's template variables...")
    for i in range(len(dashboard_variables)):
        if dashboard_variables[i]["name"] == "namespace":
            LOG.info(f"Namespace variable found successfully.")
            namespace_variable_index = i
    if namespace_variable_index is None:
        LOG.error("The namespace dashboard variable was not found in the given dashboard. \n")
        exit(1)

    new_ns_option_json = {
        "selected": "false",
        "text": oss_namespace_name,
        "value": oss_namespace_name
    }

    # Inject the new selector corresponding to the dropdown for the namespace into the .dashboard.templating.list.{
    # namespace_variable_index}.options array of the dashboard
    dashboard_json_obj["dashboard"]["templating"]["list"][namespace_variable_index]["options"].append(
        new_ns_option_json)
    options_json = dashboard_json_obj["dashboard"]["templating"]["list"][namespace_variable_index]["options"]

    # Add the namespace to the comma-separated value corresponding to the query key
    namespaces_csv = dashboard_json_obj["dashboard"]["templating"]["list"][namespace_variable_index]["query"]
    dashboard_json_obj["dashboard"]["templating"]["list"][namespace_variable_index][
        "query"] = f"{namespaces_csv},{oss_namespace_name}"
    json_out = json.dumps(dashboard_json_obj, indent=4, sort_keys=True)
    LOG.debug(f"Updated dashboard JSON following injection of required values: \n {json_out}")
    dashboard_json = dashboard_json_obj["dashboard"]

    # Add the required fields for updating the dashboard to the payload
    update_message = f"Adding panel for environment '{eiapaas_env}' to dashboard '{dashboard_name}'"
    LOG.info(f"Building payload for dashboard update request...")
    update_dashboard_payload = {}
    update_dashboard_payload["dashboard"] = dashboard_json
    update_dashboard_payload["message"] = update_message
    update_dashboard_payload["overwrite"] = True
    update_dashboard_payload["folderUid"] = dashboard_json_obj["meta"]["folderUid"]
    target_endpoint = "api/dashboards/db"

    LOG.info(f"Done.")
    json_out = json.dumps(update_dashboard_payload, indent=4, sort_keys=True)
    LOG.debug(
        f"JSON payload for request to endpoint {target_endpoint} to update dashboard '{dashboard_name}': {json_out}")

    LOG.info(f"Sending POST request to update the dashboard...")
    http_request(
        action="POST",
        api_endpoint=target_endpoint,
        request_body=json.dumps(update_dashboard_payload),
        api_token=api_token,
        user=user, pwd=pwd,
        log_level=log_level
    )
    LOG.info(f"Done.")

    LOG.info("Dashboard was updated successfully")


def export_dashboards(api_token=None, log_level="INFO"):
    get_all_response = http_request(
        action="GET",
        api_endpoint="api/search?query=&",
        api_token=api_token,
        log_level=log_level
    )[1]
    key_filter = "type"
    uid_filter = "uid"
    dashboard_list = [obj for obj in get_all_response if obj[key_filter] == "dash-db"]
    LOG.debug(f"dashboard_list: {dashboard_list}")
    uid_list = [obj[uid_filter] for obj in dashboard_list]

    # create Base directory for dashboards
    base_dir = Path.cwd() / Path('dashboard_json')
    base_dir.mkdir(parents=True, exist_ok=True)

    for uid in uid_list:
        dashboard_response = http_request(
            action="GET",
            api_endpoint=f"api/dashboards/uid/{uid}",
            api_token=api_token,
            log_level=log_level
        )[1]
        LOG.debug(f"dashboard_response received for UID: {uid}")
        dashboard_metadata = dashboard_response["meta"]
        folder_title = dashboard_metadata["folderTitle"].replace(" ", "_")
        file_name = dashboard_metadata["slug"].replace(" ", "_")
        dashboard_export_dict = dashboard_response["dashboard"]

        # Create dir for Grafana Folder
        folder_dir = Path(base_dir) / Path(folder_title)
        folder_dir.mkdir(parents=True, exist_ok=True)

        dashboard_file_path = str(Path(folder_dir) / "{}-{}.json".format(folder_title, file_name))
        try:
            with open(dashboard_file_path, "w") as outfile:
                json.dump(dashboard_export_dict, outfile)
                LOG.info(f"Dashboard {file_name} exported successfully")
        except (IOError, OSError) as err:
            LOG.error(f"Error in creating file: {err}")


def get_alert_dashboard(env_name: str, api_token: str, log_level: str) -> list:
    """ Function to get the list of Alert Dashboard IDs to pause/resume.
    Args:
        env_name (str):The Environment name to get the list of Alert Dashboards.
        api_token (str): Token to communicate with Grafana API.
        log_level (str): Level of logging.
    Returns:
        List of Alert Dashboard IDs for the specified env_name.
    """
    api_endpoint = f'api/alerts?query={env_name}'
    api_token = api_token
    _, alerts = http_request(api_endpoint=api_endpoint, api_token=api_token, log_level=log_level)
    if len(alerts) > 0:
        return alerts
    else:
        raise Exception(f'No Alert Dashboard for {env_name} environment')


def resume_alert(alert_id: str, alert_name: str, api_token: str, log_level: str):
    """Function to pause Alerts.
    Args:
        alert_id (str): The alert ID to be resumed.
        alert_name (str): The name of the alert to be resumed.
        api_token (str): Token to communicate with Grafana API.
        log_level (str): Level of logging.
    """
    LOG.info(f'Resuming alert for {alert_name}')
    api_endpoint = f'api/alerts/{alert_id}/pause'
    request_body = json.dumps({
        "paused": False
    })
    status_code, response = http_request(action='POST',
                                         api_endpoint=api_endpoint,
                                         request_body=request_body,
                                         api_token=api_token,
                                         log_level=log_level)
    if status_code != 200:
        raise Exception(response)

    LOG.info(f'Alert resumed for {alert_name}')


def pause_alert(alert_id: str, alert_name: str, api_token: str, log_level: str):
    """Function to pause Alerts.

    Args:
        alert_id (str): The alert ID to be paused.
        alert_name (str): The name of the alert to be paused.
        api_token (str): Token to communicate with Grafana API.
        log_level (str): Level of logging.
    """
    LOG.info(f'Pausing alert for {alert_name}')
    api_endpoint = f'api/alerts/{alert_id}/pause'
    request_body = json.dumps({
        "paused": True
    })
    status_code, response = http_request(action='POST',
                                         api_endpoint=api_endpoint,
                                         request_body=request_body,
                                         api_token=api_token,
                                         log_level=log_level)
    if status_code != 200:
        raise Exception(response)

    LOG.info(f'Alert paused for {alert_name}')


def process_cmd_line_args():
    # Process the command line arguments
    description = 'Team Muon helper utility for running tasks programmatically against Grafana \n'
    # Adding a parent parser for arguments common to multiple sub-commands
    parent_parser = argparse.ArgumentParser(description='Grafana Helper Tool',
                                            add_help=False)
    parent_parser.add_argument(
        '--log-level', '-l',
        type=param_to_log_level,
        nargs='?',
        metavar="log_level",
        required=False,
        default="INFO",
        help=(
            "The log level. Must be one of 'INFO', 'WARNING', 'ERROR' or 'DEBUG'. \n"
            "The default value if omitted is 'INFO', if 'DEBUG' log level is set, JSON output will be displayed in "
            "the logs "
        )
    )
    parent_parser.add_argument(
        '--api_token', '-b',
        metavar="api_token",
        required=True,
        help="The bearer token used for Grafana authentication, as a plaintext string"
    )

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest="subcommand")

    # Subparser for 'add_env_to_dashboard' command
    add_subparser = subparsers.add_parser('add', parents=[parent_parser],
                                          formatter_class=argparse.RawTextHelpFormatter,
                                          help="Add an environment to a supported target dashboard"
                                          )

    add_subparser.add_argument(
        '--env_name', '-e',
        metavar="env_name",
        required=True,
        help="The name of the EIAPaaS deployment to add to the target dashboard e.g. 'idunaasdev01'"
    )
    add_subparser.add_argument(
        '--dashboard_name', '-n',
        metavar="dashboard_name",
        required=True,
        help="The name of the dashboard to add the panel to e.g. 'eiapaas-overall-dashboard-clone'"
    )
    add_subparser.add_argument(
        '--datasource_fqdn', '-d',
        metavar="datasource_fqdn",
        required=True,
        help="The FQDN of the Prometheus or other datasource for the given EIAPaaS environment e.g. "
             "'https://prometheus.212442621681.eu-west-1.ac.ericsson.se' "
    )
    add_subparser.add_argument(
        '--oss-namespace-name', '-o',
        metavar="oss_namespace_name",
        required=True,
        help="The name of the oss namespace for the given EIAPaaS deployment e.g. 'ossdev01'"
    )
    add_subparser.add_argument(
        '--grafana_user', '-u',
        metavar="grafana_user",
        required=False,
        help="The Grafana user to use for authentication"
    )
    add_subparser.add_argument(
        '--grafana_pwd', '-p',
        metavar="grafana_pwd",
        required=False,
        help="The password for the Grafana user"
    )

    # Subparser for 'Export Dashboard' command
    export_subparser = subparsers.add_parser('export', parents=[parent_parser],
                                             formatter_class=argparse.RawTextHelpFormatter,
                                             help="Export all Dashboard JSONs into local dir"
                                             )
    export_subparser.add_argument(
        '--env_name', '-e',
        metavar="env_name",
        required=False,
        default="all"
    )

    # Subparser for 'Alarm Dashboard' command
    alert_subparser = subparsers.add_parser('alert', parents=[parent_parser],
                                            formatter_class=argparse.RawTextHelpFormatter,
                                            help="Pause/Resume Grafana Alerts"
                                            )
    alert_subparser.add_argument(
        '--env_name', '-e',
        metavar="env_name",
        required=True,
    )
    alert_subparser.add_argument(
        '--action',
        metavar='action',
        choices=['pause', 'resume'],
        help='Action to pause/resume alarm',
        required=True
    )

    args = parser.parse_args()
    return args


def param_to_log_level(param):
    if param.lower() in 'info':
        return "INFO"
    if param.lower() in 'debug':
        return "DEBUG"
    if param.lower() in 'warning':
        return "WARNING"
    if param.lower() in 'error':
        return "ERROR"
    else:
        LOG.error("Log level must be one of 'INFO','WARNING','ERROR' or 'DEBUG'")
        raise argparse.ArgumentTypeError(
            "One of 'INFO' ,'WARNING','ERROR' or 'DEBUG' expected as value for --log-level parameter")


def main():
    global logger
    args = process_cmd_line_args()
    try:
        logger = initialize_logging(name=args.env_name, log_level=args.log_level)
    except AttributeError:
        LOG.error("Insufficient arguments, Please use --help")
    LOG.warning("Please ensure the datasource name is unique")
    LOG.info(f"Invoking grafana_helper.py with arguments: \n {args}")

    try:
        if args.subcommand == 'add':
            LOG.info(f"Preparing to add panel for environment '{args.env_name}' to dashboard '{args.dashboard_name}'")
            create_datasource(
                args.env_name,
                args.datasource_fqdn,
                args.api_token,
                args.grafana_user,
                args.grafana_pwd,
                args.log_level
            )
            update_dashboard_model(
                args.env_name,
                args.dashboard_name,
                args.oss_namespace_name,
                args.api_token,
                args.grafana_user,
                args.grafana_pwd,
                args.log_level
            )
            LOG.info("Execution completed")
        if args.subcommand == 'export':
            LOG.info("Preparing to export all Dashboards from Grafana in JSON format into local dir")
            export_dashboards(args.api_token, args.log_level)
        if args.subcommand == 'alert':
            LOG.info(f'Alert Command - Gathering Alert Dashboard ID for {args.env_name}')
            alerts = get_alert_dashboard(env_name=args.env_name, api_token=args.api_token, log_level=args.log_level)
            if args.action == 'pause':
                LOG.info(f'Pausing all the alerts for {args.env_name}')
                for alert in alerts:
                    pause_alert(alert_id=alert['id'], alert_name=alert['name'], api_token=args.api_token,
                                log_level=args.log_level)
            elif args.action == 'resume':
                LOG.info(f'Resuming all the alerts for {args.env_name}')
                for alert in alerts:
                    resume_alert(alert_id=alert['id'], alert_name=alert['name'], api_token=args.api_token,
                                 log_level=args.log_level)

    except Exception as err:
        LOG.error(f"Error: {err}")
        LOG.debug(f"Debug output: {err}")
        exit(1)


if __name__ == '__main__':
    main()
