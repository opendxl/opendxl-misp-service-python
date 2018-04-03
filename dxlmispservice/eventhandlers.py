from __future__ import absolute_import
import logging

from dxlclient.callbacks import EventCallback
from dxlbootstrap.util import MessageUtils


# Configure local logger
logger = logging.getLogger(__name__)


class MispEventCallback(EventCallback):
    """
    'misp_event' event handler registered with topic '/opendxl-misp/service/notifications'
    """

    def __init__(self, app):
        """
        Constructor parameters:

        :param app: The application this handler is associated with
        """
        super(MispEventCallback, self).__init__()
        self._app = app

    def on_event(self, event):
        """
        Invoked when an event message is received.

        :param event: The event message
        """
        # Handle event
        logger.info("Event received on topic: '%s' with payload: '%s'",
                    event.destination_topic, MessageUtils.decode_payload(event))
