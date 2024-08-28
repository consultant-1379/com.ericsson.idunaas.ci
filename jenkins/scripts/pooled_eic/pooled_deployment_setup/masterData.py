import logging
from pooled_deployment_setup.base import Base
from pymongo import MongoClient


LOG = logging.getLogger(__name__)

class MasterData(Base):
    def __init__(self):
        Base.__init__(self)


    def get_buffer_value(self):

        conn = self.getMongoConnection()
        master_data = conn["master_data"]        
        value = master_data.find({"buffer_value": {'$exists': True}})
        for k in value:
            buffer_value = k['buffer_value']
        LOG.info(f"Buffer value for clusters in master data is: {buffer_value}")
        return buffer_value

    def get_default_release_version(self):

        conn = self.getMongoConnection()
        master_data = conn["master_data"]        
        value = master_data.find({"default_release_version": {'$exists': True}})
        for k in value:
            default_version = k['default_release_version']
        LOG.info(f"Default release version in master data is : {default_version}")
        return default_version


    def get_fqdn_prefixes(self):

        conn = self.getMongoConnection()
        master_data = conn["master_data"]        
        value = master_data.find({"fqdn_prefixes": {'$exists': True}})
        for k in value:
            fqdn_prefixes = k['fqdn_prefixes']
        LOG.info(f"Hostname prefixes in master data is : {fqdn_prefixes}")
        return fqdn_prefixes