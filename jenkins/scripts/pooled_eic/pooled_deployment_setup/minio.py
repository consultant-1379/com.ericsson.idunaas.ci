import datetime
from distutils.log import info
import logging
from pooled_deployment_setup.base import Base
from pooled_deployment_setup.constants import values
from pymongo import MongoClient
from kubernetes import client, config

LOG = logging.getLogger(__name__)

class MinioData(Base):
    def __init__(self, access_key, secret_key):

        Base.__init__(self)
        self.minio_bucket = values.MINIO_BUCKET
        # self.cluster_id = cluster_id
        self.access_key = access_key
        self.secret_key = secret_key
    
    def get_certificates_from_bucket(self, cluster_id, fqdn):

        LOG.info(f"Getting objects from bucket : {self.minio_bucket}")

        cert_dir = fqdn.split(".")[2]
        LOG.info(f"certificate path is : {cert_dir}")
        path_prefix = f"{cluster_id}/certificates/{cert_dir}/"
        LOG.info(f"path prefix is ; {path_prefix}")
        minio_conn = self.getMinioConnection(self.access_key, self.secret_key)

        cert_object_list = [] 
        if minio_conn.bucket_exists(self.minio_bucket):
            #objects = minio_conn.list_objects(self.minio_bucket, prefix="hall141/certificates/hall141-x1/", recursive=True)
            objects = minio_conn.list_objects(self.minio_bucket, prefix=path_prefix, recursive=True)
            for obj in objects:
                cert_object_list.append(obj.object_name)

        return cert_object_list


    def download_files_from_bucket(self):

        LOG.info(f"Downloading objects in bucket : {self.minio_bucket}")
        minio_conn = self.getMinioConnection(self.access_key, self.secret_key)

        if minio_conn.bucket_exists(self.minio_bucket):
            for item in minio_conn.list_objects(self.minio_bucket ,recursive=True):
                minio_conn.fget_object(self.minio_bucket, item.object_name, item.object_name)