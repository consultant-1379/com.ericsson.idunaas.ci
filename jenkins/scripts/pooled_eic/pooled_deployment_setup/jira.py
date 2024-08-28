import logging
from pooled_deployment_setup.base import Base
from jira import JIRA

LOG = logging.getLogger(__name__)

class Jira(Base):
    def __init__(self, jira_id: str):
        super().__init__()
        self.jira_id = jira_id

    def __get_jira_client_and_issue(self):
        jira = self.getJiraConnection()
        return jira, jira.issue(self.jira_id)

    def __get_valid_transitions(self):
        jira, issue = self.__get_jira_client_and_issue()
        return [(transition['id'], transition['name']) for transition in jira.transitions(issue)]

    def add_comment(self, comment: str):
        jira, issue = self.__get_jira_client_and_issue()
        jira.add_comment(issue, comment)

    def add_remote_link(self, remote_link: str):
        jira, issue = self.__get_jira_client_and_issue()
        jira.add_remote_link(issue, {"url": remote_link, "title": remote_link})

    def add_attachment(self, path_to_attachment: str):
        jira, issue = self.__get_jira_client_and_issue()
        jira.add_attachment(issue=issue, attachment=path_to_attachment)

    def add_jenkins_attachment(self, jenkins_build_url: str, artifact_name: str):
        jira, issue = self.__get_jira_client_and_issue()
        # download build artifact from Jenkins job
        # TBD
        jira.add_attachment(issue=issue, attachment=artifact_name)

    def add_watchers(self, watchers: str): 
        jira, issue = self.__get_jira_client_and_issue()
        [jira.add_watcher(issue, watcher) for watcher in watchers.split(',')]

    def transition_to(self, transition_to: str):
        jira, issue = self.__get_jira_client_and_issue()
        valid_transitions = self.__get_valid_transitions()
        LOG.info(f"Valid transitions are {valid_transitions}")
        [jira.transition_issue(issue, transition_id) for transition_id, transition_name in valid_transitions if transition_name.lower() in transition_to.lower()]
