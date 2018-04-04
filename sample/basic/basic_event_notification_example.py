from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import time

from dxlclient.callbacks import EventCallback
from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxlclient.message import Message, Request
from dxlbootstrap.util import MessageUtils

# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

EVENT_TOPIC = "/opendxl-misp/service/zeromq-notifications/misp_json_event"

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# Create the client
with DxlClient(config) as client:

    # Connect to the fabric
    client.connect()

    logger.info("Connected to DXL fabric.")

    class MyEventCallback(EventCallback):
        def on_event(self, event):
            event_payload_dict = MessageUtils.json_payload_to_dict(event)
            if "Event" in event_payload_dict and \
                "info" in event_payload_dict["Event"] and \
                "OpenDXL" in event_payload_dict["Event"]["info"]:
                print("Received event:\n{}".format(
                    MessageUtils.dict_to_json(event_payload_dict,
                                              pretty_print=True)))

    client.add_event_callback(EVENT_TOPIC, MyEventCallback())

    request_topic = "/opendxl-misp/service/misp-api/new_event"
    new_event_request = Request(request_topic)
    MessageUtils.dict_to_json_payload(new_event_request, {
        "distribution": 3,
        "info": "OpenDXL MISP event notification example",
        "analysis": 1,
        "threat_level_id": 3
    })

    print("Create new MISP event and wait for notification via zeromq ...")
    new_event_response = client.sync_request(new_event_request, timeout=30)

    if new_event_response.message_type == Message.MESSAGE_TYPE_ERROR:
        print("Error invoking service with topic '{}': {} ({})".format(
            request_topic, new_event_response.error_message,
            new_event_response.error_code))
        exit(1)

    time.sleep(5)
