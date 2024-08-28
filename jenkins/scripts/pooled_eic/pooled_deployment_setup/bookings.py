import datetime
import logging
from pooled_deployment_setup.base import Base
from pymongo import MongoClient
from kubernetes import client, config

LOG = logging.getLogger(__name__)

class Bookings(Base):
    def __init__(self):

        Base.__init__(self)


    def  insert_bookings(self, jira_id, team_name, team_users, cluster_name, namespace, app_set, fqdn, eic_version, 
                            booking_start_date, booking_end_date, booking_status, team_email, program, project_manager, reserved_namespace, approved_by):
        LOG.info("Inserting booking data to bookings collection..")

        conn = self.getMongoConnection()
        collection = conn["bookings"]

        start_date_obj = datetime.datetime.strptime(booking_start_date, '%d-%m-%Y')
        end_date_parsed = datetime.datetime.strptime(booking_end_date, '%d-%m-%Y')
        end_date_obj = end_date_parsed + datetime.timedelta(days=2)
        current_date = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

        LOG.info(f"booking Start Date is : {start_date_obj}")
        LOG.info(f"booking End Date is : {end_date_obj}")
        LOG.info(f"object created date is : {current_date}")

        booking = {
            "jira_id": jira_id,
            "team_name": team_name,
            "team_users": team_users,
            "cluster_name": cluster_name,
            "namespace": namespace,
            "app_set": app_set,
            "fqdn": fqdn,
            "eic_version": eic_version,
            "booking_start_date" : start_date_obj,
            "booking_end_date" : end_date_obj,
            "booking_status": booking_status,
            "team_email": team_email,
            "object_created_date": current_date,
            "program": program,
            "project_manager": project_manager,
            "reserved_namespace": reserved_namespace,
            "approved_by": approved_by
        }

        collection.insert_one(booking)

        LOG.info(f"{jira_id} added to bookings collection. Namespace is: {namespace}. Team name is : {team_name}")

    
    def find_bookings_to_remove(self):        
        LOG.info("Removing expired bookings..")

        conn = self.getMongoConnection()
        collection = conn["bookings"]
        current_date = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

        expired_bookings = collection.find(({"booking_end_date": {'$lt': current_date}}))
        expired_booking_jira_id_list = []
        for exp in expired_bookings:
            jiraID = exp["jira_id"]
            expired_booking_jira_id_list.append(jiraID)

        return expired_booking_jira_id_list
        

    def find_booking_from_jira_id(self, jiraID):

        conn = self.getMongoConnection()
        collection = conn["bookings"]

        booking_obj = collection.find_one({"jira_id": jiraID})
        if not booking_obj:
            raise Exception("No booking found for the given Jira ID.")
        return booking_obj


    def update_booking_values(self, jiraid, key, value):
        """
            This method will get a Jira_Ids and update the value passed in.
        """
        conn = self.getMongoConnection()
        collection = conn["bookings"]

        updated_data = {
            '$set': {
                f"{key}": value
            }            
        }
        collection.find_one_and_update({"jira_id": jiraid}, updated_data)
        LOG.info(f"Booking with Jira ID : {jiraid} is updated.")
    
