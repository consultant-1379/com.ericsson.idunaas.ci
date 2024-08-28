#!/bin/python3
import os
import logging
import argparse
import base64
import configparser
from commands.vault import VaultManager
import yaml
import datetime
from pathlib import Path
LOG = logging.getLogger('vault_cli')




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
        f'%Y-%m-%dT%H_%M_%S%z_{name}_vault_client.py.log'))


def upload_aws(environment,path_to_file):
    if path_to_file.exists():
        credential_path = os.path.join(path_to_file,"credentials")
        LOG.info(credential_path)
        vault_path = 'deployments/' + environment + '/aws'
        credential = configparser.RawConfigParser()
        credential.read(credential_path)
        _data = dict(credential.items('default'))

        config_path = os.path.join(path_to_file,"config")
        config = configparser.RawConfigParser()
        config.read(config_path)
        _data.update(dict(config.items('default')))
        try:
            _vault.put_data(vault_path,_data)
        except Exception as err:
            LOG.error(f"Error: {err}")
            LOG.debug(f"Debug output: {err}")
            return False
    else:
        LOG.error("Unable to locate folder with aws credentials and config files")
        return False


def upload_certificates(environment,path_to_file):
    if path_to_file.exists():
        workdir_path_vault = 'deployments/' + environment + '/workdir/certificates' 
        certificate_path = path_to_file
        certificates = [f for f in os.listdir(certificate_path) if os.path.isfile(os.path.join(certificate_path, f))]
        _dict = {}
        for cert in certificates:
            _cert = open(os.path.join(certificate_path,cert),"rb").read()
            enc_cert = base64.b64encode(_cert).decode('ascii')
            _dict[cert] = enc_cert
        _vault.put_data(workdir_path_vault, _dict)
        
    else: 
        LOG.error("Unable to locate folders with certificates")
        return False

"""
def upload_kube(environment,deployment_dir):
    if deployment_dir.exists():
        kube_config_path = os.path.join(deployment_dir, os.path.join(environment,"workdir/kube_config",""),"config")
        vault_path = 'deployments/' + environment + '/kube_config/'
        kube_config = open(kube_config_path,"rb").read()
        enc_kube_config = base64.b64encode(kube_config).decode('ascii')
        _vault.put_data(vault_path, dict(kube_config=enc_kube_config))
    else:
        return False


def upload_config(environment,deployment_dir):
    if deployment_dir.exists():
        config_path = os.path.join(deployment_dir, os.path.join(environment,"workdir",""),"config.yaml")
        vault_path = 'deployments/' + environment + '/config'
        with open(config_path, 'r') as configfile:
            try:
                _data = yaml.safe_load(configfile)
            except yaml.YAMLError as exc:
                print(exc)
        _vault.put_data(vault_path,_data)

def upload_ssh_key(environment,deployment_dir):
    if deployment_dir.exists():
        workdir_path_vault = 'deployments/' + environment + '/workdir'
        config_path_vault = 'deployments/' + environment + '/config'
        key_name = _vault.fetch_data(config_path_vault)['SshKeyPairName']
        ssh_key_path = os.path.join(deployment_dir, os.path.join(environment,"keypair",""),key_name + ".pem")
        ssh_key = open(ssh_key_path,"rb").read()
        enc_ssh_key = base64.b64encode(ssh_key).decode('ascii')
        _vault.put_data(workdir_path_vault, dict(key_pair=enc_ssh_key))
    else:
        return False

def upload_site_vaule_override(environment,deployment_dir):
    if deployment_dir.exists():
        site_value_path = os.path.join(deployment_dir, os.path.join(environment,"workdir",""),"site-values-override.yaml")
        vault_path = 'deployments/' + environment + '/workdir/site-values'
        site_value = open(site_value_path,"rb").read()
        enc_site_value =  base64.b64encode(site_value).decode('ascii')
        _vault.put_data(vault_path, dict(site_value_override=enc_site_value))

    else:
        return False

"""
def download_aws(name,deployment_dir):
    creadential_path = os.path.join(deployment_dir,name + "/aws/","credentials")
    config_path = os.path.join(deployment_dir,name + "/aws/","config")

    path = 'deployments/' + name + '/aws'
    data = _vault.fetch_data(path)
    credential = configparser.ConfigParser()
    credential.add_section('default')
    credential.set('default','aws_access_key_id',data['aws_access_key_id'])
    credential.set('default','aws_secret_access_key',data['aws_secret_access_key'])
    credential.set('default','role_arn',data['role_arn'])
    credential.set('default','region',data['region'])
    credential.set('default','source_profile',data['source_profile'])
    os.makedirs(os.path.dirname(creadential_path), exist_ok=True)
    with open(creadential_path,'w') as configfile:
        credential.write(configfile)

    config = configparser.ConfigParser()
    config.add_section('default')
    config.set('default','region',data['region'])
    config.set('default','role_arn',data['role_arn'])
    config.set('default','sts_regional_endpoints','regional')
    config.set('default','output','json')
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path,'w') as configfile:
      config.write(configfile)


def download_cert(environment,deployment_dir):
    cert_path_vault = 'deployments/' + environment + '/workdir/certificates'
    cert_path       = os.path.join(deployment_dir, os.path.join(environment,"workdir/certificates"),"")
    os.makedirs(cert_path,exist_ok=True)
    certificates = _vault.fetch_data(cert_path_vault)
    for cert in certificates:
        cert_decode = base64.b64decode(certificates[cert])
        with open(os.path.join(cert_path,cert),'wb') as cert_file:
            cert_file.write(cert_decode)
"""

def download_kube(name,deployment_dir):
    config_path =  os.path.join(deployment_dir,name + "/workdir/kube_config","config")
    path = 'deployments/' + name + '/kube_config'
    data = _vault.fetch_data(path)
    kube_config = base64.b64decode(data['kube_config'])
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path,'wb') as configfile:
        configfile.write(kube_config)

def download_ssh_key(name,deployment_dir):
    data = _vault.fetch_data('deployments/' + name + '/workdir')
    ssh_key = base64.b64decode(data['key_pair'])
    key_name = _vault.fetch_data('deployments/' + name + '/config')['SshKeyPairName']
    ssh_key_path = os.path.join(deployment_dir, os.path.join(name,"keypair",""),key_name + ".pem")
    os.makedirs(os.path.dirname(ssh_key_path), exist_ok=True)
    with open(ssh_key_path,'wb') as key_file:
        key_file.write(ssh_key)


def download_config(name,deployment_dir):
    config_path =  os.path.join(deployment_dir,name + "/workdir/","config.yaml")
    path = 'deployments/' + name + '/config'
    data = _vault.fetch_data(path)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as configfile:
        yaml.dump(data, configfile,allow_unicode=True)


def download_site_vaules_override(environment,deployment_dir):
    data = _vault.fetch_data('deployments/' + environment + '/workdir/site-values')
    site_value_path = os.path.join(deployment_dir, os.path.join(environment,"workdir"),"")
    site_value_decoded = base64.b64decode(data["site_value_override"])
    os.makedirs(site_value_path,exist_ok=True)
    with open(os.path.join(site_value_path,"site-values-override.yaml"),'wb') as site_file:
        site_file.write(site_value_decoded)

def download_deployment(environment,deployment_dir):
    download_ssh_key(environment,deployment_dir)
    download_kube(environment,deployment_dir)
    download_aws(environment,deployment_dir)
    download_cert(environment,deployment_dir)
    download_config(environment,deployment_dir)
    download_site_vaules_override(environment,deployment_dir)

"""
def param_to_log_level(param):
    if param.lower() in 'info':
        return "INFO"
    if param.lower() in 'debug':
        return "DEBUG"
    if param.lower() in 'warning':
        return "WARNINIG"
    if param.lower() in 'error':
        return "ERROR"
    else:
        LOG.error("Log level must be one of 'INFO','WARNINIG,'ERROR' or 'DEBUG'")
        raise argparse.ArgumentTypeError(
            "One of 'INFO','WARNINIG','ERROR' or 'DEBUG' expected as value for --log-level parameter")

def process_cmd_line_args():

    description = 'Team Muon helper utility to programatically upload and download creadentials to vault'
    parent_parser = argparse.ArgumentParser(description="Command line to interact vault",add_help=False)


    parent_parser.add_argument(
        '-l','--log-level',
        type=param_to_log_level,
        nargs='?',
        metavar="log_level",
        required=False,
        default="INFO",
        help=(
            "The log level must be one of 'INFO','WARNING,'ERROR' or 'DEBUG'. \n"
            "Default value set to 'INFO'"
        )
    )
    parent_parser.add_argument(
        '--vault_token', '-t',
        metavar="vault_token",
        required=True,
        help="Vault token used to authenticate VAULT server"
    )
    parent_parser.add_argument(
        '--vault_endpoint', '-v',
        metavar="vault_endpoint",
        required=True,
        help="Vault server endpoint"
    )

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest="subcommand")
    ## Subparser for 'upload_aws ' command
    upload_aws_subparser = subparsers.add_parser('put_aws', parents=[parent_parser],formatter_class=argparse.RawTextHelpFormatter,
                                             help="Upload aws config and credential file inside specified folder to vault"
                                             )
    upload_aws_subparser.add_argument(
       '--env_name','-e',
       metavar="env_name",
       required=True,
       help="Deployment environment name"
    )

    upload_aws_subparser.add_argument(
        '--path_to_file', '-p',
        metavar="path_to_file",
        required=True,
        type=Path,
        help="Path to aws directory"
    )

     ## Subparser for 'download_aws' command
    download_certificates_subparser = subparsers.add_parser('get_aws', parents=[parent_parser],formatter_class=argparse.RawTextHelpFormatter,
                                             help="download aws config and credentials from vault to deployment directory"
                                             )
    download_certificates_subparser.add_argument(
       '--env_name','-e',
       metavar="env_name",
       required=True,
       help="Deployment environment name"
    )

    download_certificates_subparser.add_argument(
        '--deployment_dir', '-d',
        metavar="deployment_dir",
        required=True,
        type=Path,
        help="Path to deployment directory"
    )

    ## Subparser for 'upload_certificate' command
    upload_certificates_subparser = subparsers.add_parser('put_certificates', parents=[parent_parser],formatter_class=argparse.RawTextHelpFormatter,
                                             help="Upload all certificates inside specified folder to vault"
                                             )
    upload_certificates_subparser.add_argument(
       '--env_name','-e',
       metavar="env_name",
       required=True,
       help="Deployment environment name"
    )

    upload_certificates_subparser.add_argument(
        '--path_to_file', '-p',
        metavar="path_to_file",
        required=True,
        type=Path,
        help="Path to certificates directory"
    )


    ## Subparser for 'download_certificate' command
    download_certificates_subparser = subparsers.add_parser('get_certificates', parents=[parent_parser],formatter_class=argparse.RawTextHelpFormatter,
                                             help="download all certificates from vault to deployment directory"
                                             )
    download_certificates_subparser.add_argument(
       '--env_name','-e',
       metavar="env_name",
       required=True,
       help="Deployment environment name"
    )

    download_certificates_subparser.add_argument(
        '--deployment_dir', '-d',
        metavar="deployment_dir",
        required=True,
        type=Path,
        help="Path to deployment directory"
    )


    args = parser.parse_args()
    return args


def main():
    global logger
    args = process_cmd_line_args()
    try:
        logger = initialize_logging(name=args.env_name, log_level=args.log_level)
    except AttributeError:
        LOG.error("Insufficient arguments, Please use --help")
    LOG.info(f"Invoking vault.py with arguments: \n ")

    try:
        _config = {
             'endpoint' : args.vault_endpoint,
             'token'    : args.vault_token
        }
        global _vault
        _vault = VaultManager(_config)
        if _vault.is_sealed == True:
            LOG.error("VAULT is in sealed state. Follow procedure to unseal")
        if _vault.is_authenticated == False:
            LOG.error("Invalid VAULT token passed.")
            exit(1)
    except Exception as err:
        LOG.error(f"Error: {err}")
        LOG.debug(f"Debug output: {err}")
        exit(1)
    try:
        if args.subcommand == 'put_aws':
            LOG.info(f"Uploading aws credentials for environment '{args.env_name}' to vault '{args.vault_endpoint}'")
            upload_aws(
                args.env_name,
                args.path_to_file
            )
            LOG.info("Succesfully uploaded to vault '{args.vault_endpoint}'")
        if args.subcommand == 'get_aws':
            LOG.info(f"Downloading aws credentials from vault '{args.vault_endpoint}' for environment '{args.env_name}' to '{args.deployment_dir}'")
            download_aws(
                args.env_name,
                args.deployment_dir
            )
            LOG.info(f"Succesfully downloaded from vault '{args.vault_endpoint}'")
        if args.subcommand == 'put_certificates':
            LOG.info(f"Uploading certificates from '{args.path_to_file}' for environment '{args.env_name}' to vault '{args.vault_endpoint}'")
            upload_certificates(
                args.env_name,
                args.path_to_file
            )
            LOG.info(f"Succesfully uploaded to vault '{args.vault_endpoint}'")
        if args.subcommand == 'get_certificates':
            LOG.info(f"Downloading certificates from vault '{args.vault_endpoint}' for environment '{args.env_name}' to '{args.deployment_dir}'")
            download_cert(
                args.env_name,
                args.deployment_dir
            )
            LOG.info(f"Succesfully downloaded from vault '{args.vault_endpoint}'")


    except Exception as err:
        LOG.error(f"Error: {err}")
        LOG.debug(f"Debug output: {err}")
        exit(1)

if __name__ == '__main__':
    main()


