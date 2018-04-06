from __future__ import absolute_import
from __future__ import print_function
import os
import sys

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

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# Create the client
with DxlClient(config) as client:

    # Connect to the fabric
    client.connect()

    logger.info("Connected to DXL fabric.")

    # Create the new event request
    request_topic = "/opendxl-misp/service/misp-api/new_event"
    new_event_request = Request(request_topic)

    # Set the payload for the new event request
    MessageUtils.dict_to_json_payload(new_event_request, {
        "distribution": 3,
        "info": "OpenDXL MISP new event example",
        "analysis": 1,
        "threat_level_id": 3
    })

    # Send the new event request
    new_event_response = client.sync_request(new_event_request, timeout=30)

    if new_event_response.message_type != Message.MESSAGE_TYPE_ERROR:
        # Display results for the new event request
        new_event_response_dict = MessageUtils.json_payload_to_dict(
            new_event_response)
        print("Response to the new event request:\n{}".format(
            MessageUtils.dict_to_json(new_event_response_dict,
                                      pretty_print=True)))
    else:
        print("Error invoking service with topic '{}': {} ({})".format(
            request_topic, new_event_response.error_message,
            new_event_response.error_code))
        exit(1)

    # Create the new search request
    request_topic = "/opendxl-misp/service/misp-api/search"
    search_request = Request(request_topic)

    # Set the payload for the search request
    MessageUtils.dict_to_json_payload(search_request, {
        "eventid": new_event_response_dict["Event"]["id"],
    })

    # Send the search request
    search_response = client.sync_request(search_request, timeout=30)

    if search_response.message_type != Message.MESSAGE_TYPE_ERROR:
        # Display results for the search request
        search_response_dict = MessageUtils.json_payload_to_dict(
            search_response)
        print("Response to the search request for the new MISP event:\n{}".format(
            MessageUtils.dict_to_json(search_response_dict,
                                      pretty_print=True)))
    else:
        print("Error invoking service with topic '{}': {} ({})".format(
            request_topic, search_response.error_message,
            search_response.error_code))
