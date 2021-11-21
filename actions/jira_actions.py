import logging
import pathlib
import ruamel.yaml
from typing import Dict, Text, Any
from jira import (
    JIRA,
)  # requires jira 3.1.0rc1 for the search_user function to work
from jira.resources import Customer, Priority, User

logger = logging.getLogger(__name__)

here = pathlib.Path(__file__).parent.absolute()


class JiraPy(object):
    def __init__(self):
        jira_config = (
            ruamel.yaml.safe_load(open(f"{here}/jira_credentials.yml", "r"))
            or {}
        )

        self.jira_user = jira_config.get("jira_user")
        self.jira_token = jira_config.get("jira_token")
        self.jira_url = jira_config.get("jira_url")
        self.project = jira_config.get("project")
        self.jira_obj = JIRA(
            self.jira_url, basic_auth=(self.jira_user, self.jira_token)
        )

    def handle_request(self):
        # TODO This might not be needed. In the service now version it isn't called directly by actions
        True

    def email_to_sysid(self, email) -> Dict[Text, Any]:
        result = {}
        email_result = self.jira_obj.search_users(
            None, 0, 10, True, False, email
        )
        if len(email_result) == 1:
            result["account_id"] = vars(email_result[0]).get("accountId")
        else:
            result["account_id"] = []
            result["error"] = (
                f"Could not retreive account id;  "
                f"Multiple records found for email {email}"
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
                incidents[issue.key] = issue.fields.summary
        elif isinstance(issues, list):
            result["error"] = f"No incidents on record for {email}"

        result["account_id"] = account_id
        result["incidents"] = incidents
        return result

    def create_incident(
        self, description, short_description, priority, email
    ) -> Dict[Text, Any]:
        project = self.project
        account_id = self.email_to_sysid(email).get("account_id")
        print(account_id)
        issue = self.jira_obj.create_issue(
            project=project,
            summary=short_description,
            description=description,
            issuetype={"id": "10002"},
            priority={"id": priority},
            reporter={"accountId": account_id},
        )
        return issue

    # TODO need to use this for setting priority
    @staticmethod
    def priority_db() -> Dict[str, int]:
        """Database of supported priorities"""
        priorities = {"low": 4, "medium": 3, "high": 2}
        return priorities


jira = JiraPy()

id = jira.email_to_sysid("abelincoln@example.com")
print((id))

new_issue = jira.create_incident(
    "function call with email", "test out eamil", "3", "abelincoln@example.com"
)

print(new_issue.fields.project.key)
print(new_issue)
print(new_issue.fields.issuetype.name)
print(new_issue.fields.reporter)
print(new_issue.fields.summary)
print(new_issue.fields.comment.comments)

issues = jira.retrieve_incidents("abelincoln@example.com")
print(issues)
