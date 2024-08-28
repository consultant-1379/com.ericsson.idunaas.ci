import logging
from pooled_deployment_setup.constants import values
from pymongo import MongoClient
from jira import JIRA
from prometheus_api_client import PrometheusConnect
from minio import Minio

LOG = logging.getLogger(__name__)
class Base:
    def __init__(self):
        self.uri = values.MONGO_URI
        self.tls_cert_key = values.TLS_CERT_KEY_FILE
        self.tls_ca_file = values.TLS_CA_FILE
        self.username = values.MONGO_USERNAME
        self.password = values.MONGO_PASSWORD

        self.prometheus_host = values.PROMETHEUS_URI

        self.jira_host = values.JIRA_URL
        self.jira_pat = values.JIRA_PAT_TOKEN

        self.minio_uri = values.MINIO_URI
        # self.minio_access_key = values.MINIO_ACCESS_KEY
        # self.minio_secret_key = values.MINIO_SECRET_KEY

    def getTlsMongoConnection(self):
        LOG.debug("Creating the mongodb client")
        mongo_client = MongoClient(self.uri,
                    tls=True,
                    tlsCertificateKeyFile=self.tls_cert_key,
                    tlsCAFile=self.tls_ca_file,
                    username=self.username,
                    password=self.password,
                    authSource='admin')

        db = mongo_client.eicPooledClusterDB
        return db

    def getMongoConnection(self):
        LOG.debug("Creating the mongodb client")
        mongo_client = MongoClient(self.uri,
                    username=self.username,
                    password=self.password,
                    authSource='admin')
        db = mongo_client.eicPooledClusterDB
        return db

    def getPrometheusConnection(self):
        LOG.debug("Creating the prometheus client")

        prom_client = PrometheusConnect(url=self.prometheus_host, disable_ssl=True)
        return prom_client

    def getJiraConnection(self):
        LOG.debug("Creating the jira client")

        jira_client = JIRA(server = self.jira_host, token_auth = self.jira_pat)
        return jira_client


    def getMinioConnection(self, access_key, secret_key):
        LOG.debug("Creating the minio client")

        minio_client = Minio(self.minio_uri, access_key=access_key, secret_key=secret_key, secure=False)
        return minio_client