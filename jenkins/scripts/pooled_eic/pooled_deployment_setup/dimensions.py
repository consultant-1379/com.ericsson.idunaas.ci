import datetime
import logging
from pooled_deployment_setup.base import Base
from pymongo import MongoClient

LOG = logging.getLogger(__name__)

class Dimensions(Base):
    def __init__(self):
        Base.__init__(self)


    def add_dimensions(self, file_obj):
        LOG.info("Adding EIC Dimensions to the eic_dimensions collection in mongo")

        conn = self.getMongoConnection()
        collection = conn["eic_dimensions"]

        collection.insert_many(file_obj)

        LOG.info("Objects added to eic_dimensions collection.")


    def get_appset_from_release_version(self, release_version):
        LOG.info(f"Getting data from the release version: {release_version}")

        conn = self.getMongoConnection()
        collection = conn["eic_dimensions"]
        data_obj = collection.find_one({"release_version": release_version})
        return data_obj
        
        