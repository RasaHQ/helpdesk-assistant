import logging
import pathlib
import ruamel.yaml
from typing import Dict, Text, Any
from jira import (
    JIRA,
)  # requires jira 3.1.0rc1 for the search_user function to work
from jira.resources import Customer, Priority, User

logger = logging.getLogger(__name__)

cred_path = str(pathlib.Path(__file__).parent.parents[0]) + "/.vscode"


class JiraPy(object):
    def __init__(self):
        jira_config = (
            ruamel.yaml.safe_load(
                open(f"{cred_path}/jira_credentials.yml", "r")
            )
            or {}
        )

        self.jira_user = jira_config.get("jira_user")
        self.jira_token = jira_config.get("jira_token")
        self.jira_url = jira_config.get("jira_url")
        self.project = jira_config.get("project")
        self.jira_obj = JIRA(
            self.jira_url, basic_auth=(self.jira_user, self.jira_token)
        )

    def email_to_sysid(self, email) -> Dict[Text, Any]:
        result = {}
        email_result = self.jira_obj.search_users(
            None, 0, 10, True, False, email
        )
        num_records = len(email_result)
        if num_records == 1:
            result["account_id"] = vars(email_result[0]).get("accountId")
        else:
            result["account_id"] = []
            result["error"] = (
                f"Could not retreive account id;  "
                f"{num_records} records found for email {email}"
            )

        return result

    def retrieve_incidents(self, email) -> Dict[Text, Any]:
        result = {}
        incidents = {}
        email_result = self.email_to_sysid(email)
        account_id = email_result.get("account_id")
        issues = self.jira_obj.search_issues(
            f"reporter in ({account_id}) order by created DESC"
        )
        if account_id:
            for issue in issues:
                incidents[issue.key] = {
                    "summary": issue.fields.summary,
                    "created_on": issue.fields.created,
                    "status": issue.fields.status.name,
                }
        elif isinstance(issues, list):
            result["error"] = f"No incidents on record for {email}"

        result["account_id"] = account_id
        result["incidents"] = incidents
        return result

    def create_incident(
        self, description, short_description, priority, email
    ) -> Dict[Text, Any]:
        project = self.project
        email_result = self.email_to_sysid(email)
        account_id = email_result.get("account_id")
        if account_id:
            result = self.jira_obj.create_issue(
                project=project,
                summary=short_description,
                description=description,
                issuetype={"id": "10002"},
                priority={"id": priority},
                reporter={"accountId": account_id},
            )
        else:
            result = email_result.get("error")

        return result

    def delete_issue(self, issue_id):
        issue = self.jira_obj.issue(issue_id)
        issue.delete()
        return

    def change_priority(self, issue_id, priority):
        issue = self.jira_obj.issue(issue_id)
        issue.update(priority={"id": priority})

    def assigned_issues(self, account_id):
        issues = self.jira_obj.search_issues(
            f"assignee = {account_id} ORDER BY priority"
        )
        return issues

    @staticmethod
    def priority_db() -> Dict[str, int]:
        """Database of supported priorities"""
        priorities = {"low": "4", "medium": "3", "high": "2"}
        return priorities


if __name__ == "__main__":

    jira = JiraPy()

    # test assigned issues
    # email = "ADMINEMAIL" with issues assigned
    # account_id = jira.email_to_sysid(email).get("account_id")
    # my_issues = jira.assigned_issues(account_id)
    # print(my_issues)
