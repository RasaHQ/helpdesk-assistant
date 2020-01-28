import logging
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Dict, Text, Any, Callable, Awaitable, Optional

from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import UserMessage, OutputChannel

logger = logging.getLogger(__name__)


class SnowBot(OutputChannel):
    """Output channel for Snow Chat"""

    @classmethod
    def name(cls) -> Text:
        return "snow"

    def __init__(
        self,
        snow_user: Optional[Text],
        snow_pw: Optional[Text],
    ) -> None:
        super().__init__(snow_user, snow_pw)
        self.snow_user = snow_user
        self.snow_pw = snow_pw
        self.send_retry = 0
        self.max_retry = 5

    async def _send_message(self, message_data: Dict[Text, Any]):
        message = None
        print(f"The message is: {message}")

        # TODO - Add in REST call to SNOW api to post chat message

        return message

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        """Sends text message"""
        for message_part in text.split("\n\n"):
            await self._send_message(message_part)

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Send custom json dict"""

        print(f"The json is: {json_message}")

        await self._send_message(json_message)


class SnowInput(InputChannel):
    """SNOW input channel"""

    @classmethod
    def name(cls) -> Text:
        return "snow"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(
            credentials.get("snow_user"),
            credentials.get("snow_pw"),
        )
        # pytype: enable=attribute-error

    def __init__(
        self,
        snow_user: Optional[Text],
        snow_pw: Optional[Text],
        debug_mode: bool = True,
    ) -> None:
        self.snow_user = snow_user
        self.snow_pw = snow_pw
        self.debug_mode = debug_mode

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        snow_webhook = Blueprint("snow_webhook", __name__)

        @snow_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @snow_webhook.route("/webhook", methods=["POST"])
        async def message(request: Request) -> HTTPResponse:
            output = request.json

            print(f"The output is: {output}")

            if not output:
                return response.text("")

            metadata = self.get_metadata(request)

            return response.text("", status=204)

        return snow_webhook

    def get_output_channel(self) -> OutputChannel:
        return SnowBot(self.snow_user, self.snow_pw)
