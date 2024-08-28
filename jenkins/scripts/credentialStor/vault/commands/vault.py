"""
This module implements logic to upload and download configuration to vault
"""
import logging
import hvac
LOG = logging.getLogger(__name__)

class VaultManager:
    """" Main Class for Vault Interaction """

    def __init__(self,config):
        self.config         = config
        self.client         = hvac.Client(url = self.config['endpoint'])
        self.client.token   = self.config['token']
        self.is_authenticated = self.client.is_authenticated()
        self.is_sealed  =     self.client.sys.is_sealed()

    def init_deployment(self,name):
        return

    def fetch_data(self,path):
        resp = self.client.secrets.kv.read_secret_version(path)
        data = resp['data']['data']
        return data

    def put_data(self,path,secret):
        resp = self.client.secrets.kv.v2.create_or_update_secret(path, secret)
        return resp
