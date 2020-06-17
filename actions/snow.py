import logging
import requests
import json
import pathlib
import ruamel.yaml
from typing import Dict, Text, Any

logger = logging.getLogger(__name__)

here = pathlib.Path(__file__).parent.absolute()

json_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


class SnowAPI(object):
    """class to connect to the ServiceNow API"""

    def __init__(self):
        snow_config = (
            ruamel.yaml.safe_load(open(f"{here}/snow_credentials.yml", "r"))
            or {}
        )
        self.snow_user = snow_config.get("snow_user")
        self.snow_pw = snow_config.get("snow_pw")
        self.snow_instance = snow_config.get("snow_instance")
        self.localmode = snow_config.get("localmode", True)
        self.base_api_url = "https://{}/api/now".format(self.snow_instance)

    def handle_request(
        self, request_method=requests.get, request_args={}
    ) -> Dict[Text, Any]:
        result = dict()
        try:
            response = request_method(**request_args)
            result["status_code"] = response.status_code
            if response.status_code >= 200 < 300:
                result["content"] = response.json()
            else:
                error = (
                    f"ServiceNow error: {response.status_code}: "
                    f'{response.json().get("error",{}).get("message")}'
                )
                logger.debug(error)
                result["error"] = error
        except requests.exceptions.Timeout:
            error = "Could not connect to ServiceNow (Timeout)"
            logger.debug(error)
            result["error"] = error
        return result

    def email_to_sysid(self, email) -> Dict[Text, Any]:
        lookup_url = (
            f"{self.base_api_url}/table/sys_user?"
            f"sysparm_query=email={email}&sysparm_display_value=true"
        )
        request_args = {
            "url": lookup_url,
            "auth": (self.snow_user, self.snow_pw),
            "headers": json_headers,
        }
        result = self.handle_request(requests.get, request_args)
        records = result.get("content", {}).get("result")
        if len(records) == 1:
            caller_id = records[0].get("sys_id")
            result["caller_id"] = caller_id
        elif isinstance(records, list):
            result["caller_id"] = []
            result["error"] = (
                f"Could not retrieve caller id; "
                f"{records} records found for email {email}"
            )
        return result

    def retrieve_incidents(self, email) -> Dict[Text, Any]:
        result = self.email_to_sysid(email)
        caller_id = result.get("caller_id")
        if caller_id:
            incident_url = (
                f"{self.base_api_url}/table/incident?"
                f"sysparm_query=caller_id={caller_id}"
                f"&sysparm_display_value=true"
            )
            request_args = {
                "url": incident_url,
                "auth": (self.snow_user, self.snow_pw),
                "headers": json_headers,
            }
            result = self.handle_request(requests.get, request_args)
            incidents = result.get(  # pytype: disable=attribute-error
                "content", {}  # pytype: disable=attribute-error
            ).get(  # pytype: disable=attribute-error
                "result"  # pytype: disable=attribute-error
            )  # pytype: disable=attribute-error
            if incidents:
                result["incidents"] = incidents
            elif isinstance(incidents, list):
                result["error"] = f"No incidents on record for {email}"
        return result

    def create_incident(
        self, description, short_description, priority, email
    ) -> Dict[Text, Any]:
        result = self.email_to_sysid(email)
        caller_id = result.get("caller_id")
        if caller_id:
            incident_url = f"{self.base_api_url}/table/incident"
            data = {
                "opened_by": caller_id,
                "short_description": short_description,
                "description": description,
                "urgency": priority,
                "caller_id": caller_id,
                "comments": description,
            }
            request_args = {
                "url": incident_url,
                "auth": (self.snow_user, self.snow_pw),
                "headers": json_headers,
                "data": json.dumps(data),
            }
            result = self.handle_request(requests.post, request_args)
        return result

    @staticmethod
    def priority_db() -> Dict[str, int]:
        """Database of supported priorities"""
        priorities = {"low": 3, "medium": 2, "high": 1}
        return priorities
