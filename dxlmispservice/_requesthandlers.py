from __future__ import absolute_import
import logging

from dxlbootstrap.util import MessageUtils
from dxlclient.callbacks import RequestCallback
from dxlclient.message import ErrorResponse, Response

# Configure local logger
logger = logging.getLogger(__name__)


class MispServiceRequestCallback(RequestCallback):
    """
    Constructor parameters:

    :param dxlmispservice.app.MispService app: The Misp service application
    :param api_method: Method or function to invoke when a request is received.
    """
    def __init__(self, app, api_method):
        super(MispServiceRequestCallback, self).__init__()
        self._app = app
        self._api_method = api_method

    def on_request(self, request):
        """
        Callback invoked when a request is received.

        :param dxlclient.message.Request request: The request
        """
        logger.info("Request received on topic '%s'",
                    request.destination_topic)
        logger.debug("Payload for topic %s: %s", request.destination_topic,
                     request.payload)

        try:
            request_dict = MessageUtils.json_payload_to_dict(request) \
                if request.payload else {}
            if "event" in request_dict and \
                    type(request_dict["event"]).__name__ in ("str", "unicode") and \
                    request_dict["event"].isdigit():
                request_dict["event"] = int(request_dict["event"])

            response_data = self._api_method(**request_dict)
            if isinstance(response_data, dict) and \
                    response_data.get("errors", None):
                res = ErrorResponse(
                    request, error_message=str(response_data["errors"][0]))
            else:
                res = Response(request)
            MessageUtils.dict_to_json_payload(res, response_data)
        except Exception as ex:
            error_str = str(ex)
            logger.exception("Error handling request: %s", error_str)
            res = ErrorResponse(request,
                                error_message=MessageUtils.encode(error_str))

        self._app.client.send_response(res)
