Basic Event Notification Example
================================

This sample registers a callback to receive event notifications from the DXL
fabric when new MISP events are created. The sample creates a new event on a
MISP server via the MISP ``Events`` API. The sample waits for a corresponding
event notification from the DXL fabric via the MISP ZeroMQ plugin. The sample
displays the contents of the payload from the event notification that it
receives.

For more information on the MISP ``Events`` API, see the
`PyMISP new_event API <https://media.readthedocs.org/pdf/pymisp/master/pymisp.pdf>`__
and `MISP Event API <https://misp.gitbooks.io/misp-book/content/automation/#post-events>`__
documentation. For more information on the ZeroMQ plugin, see the documentation
for the
`MISP ZeroMQ plugin <https://misp.gitbooks.io/misp-book/misp-zmq/#misp-zeromq-configuration>`__.

Prerequisites
*************

* The samples configuration step has been completed (see :doc:`sampleconfig`).
* The MISP DXL Python Service is running, using the ``sample`` configuration
  (see :doc:`running`).
* Enable the ZeroMQ plugin and set the "Plugin_ZeroMQ_event_notification_enable"
  setting to ``true`` through the MISP web server. For more information, see
  the documentation for the
  `MISP ZeroMQ configuration <https://misp.gitbooks.io/misp-book/misp-zmq/#misp-zeromq-configuration>`__.
  This step is needed to enable the DXL MISP service to be able to receive
  event notification messages from the MISP ZeroMQ server.

Running
*******

To run this sample execute the ``sample/basic/basic_event_notification.py``
script as follows:

    .. code-block:: shell

        python sample/basic/basic_event_notification.py

The output should appear similar to the following:

    .. code-block:: shell

        Create new MISP event and wait for notification via ZeroMQ ...
        Received event:
        {
            "Event": {
                "analysis": "1",
                "attribute_count": "0",
                "date": "2018-04-09",
                "disable_correlation": false,
                "distribution": "3",
                "id": "172",
                "info": "OpenDXL MISP event notification example",
                "locked": false,
                "org_id": "1",
                "orgc_id": "1",
                "proposal_email_lock": false,
                "publish_timestamp": "0",
                "published": false,
                "sharing_group_id": "0",
                "threat_level_id": "3",
                "timestamp": "1523288047",
                "user_id": "1",
                "uuid": "5acb87ef-8c9c-4347-b0c1-196cac110002"
            },
            "EventTag": [],
            "Orgc": {
                "id": "1",
                "name": "ORGNAME",
                "uuid": "5ac3c55a-41a4-4294-adf3-00f8ac110003"
            },
            "action": "add"
        }

Details
*******

In order to enable the use of the ``new_event`` API, the ``new_event`` API
names is listed in the ``apiNames`` setting under the ``[General]`` section in
the ``sample`` "dxlmispservice.config" file that the service uses:

    .. code-block:: ini

        [General]
        apiNames=new_event,...

For more information on the configuration, see the
:ref:`Service Configuration File <dxl_service_config_file_label>` section.

The code for the sample is broken into two main sections.

The first section is responsible for registering a callback to receive
notifications for ``misp_json_event`` MISP ZeroMQ notifications:

    .. code-block:: python

        EVENT_TOPIC = "/opendxl-misp/event/zeromq-notifications/misp_json_event"

        ...

        # Create the client
        with DxlClient(config) as client:

            # Connect to the fabric
            client.connect()

            logger.info("Connected to DXL fabric.")

            # Create and add event listener
            class MyEventCallback(EventCallback):
                def on_event(self, event):
                    event_payload_dict = MessageUtils.json_payload_to_dict(event)
                    # Check the event payload to see if the OpenDXL event was triggered
                    # by the new MISP event that the sample created.
                    if "Event" in event_payload_dict and \
                        "info" in event_payload_dict["Event"] and \
                        event_payload_dict["Event"]["info"] == \
                            "OpenDXL MISP event notification example":
                        # Print the payload for the received event
                        print("Received event:\n{}".format(
                            MessageUtils.dict_to_json(event_payload_dict,
                                                      pretty_print=True)))

            # Register the callback with the client
            client.add_event_callback(EVENT_TOPIC, MyEventCallback())


When a notification is received, the contents of the event are displayed.

The second section is responsible for creating the MISP event which triggers the
MISP ZeroMQ event notification.

    .. code-block:: python

        # Create the new event request
        request_topic = "/opendxl-misp/service/misp-api/new_event"
        new_event_request = Request(request_topic)

        # Set the payload for the new event request
        MessageUtils.dict_to_json_payload(new_event_request, {
            "distribution": 3,
            "info": "OpenDXL MISP event notification example",
            "analysis": 1,
            "threat_level_id": 3
        })

        print("Create new MISP event and wait for notification via ZeroMQ ...")

        # Send the new event request
        new_event_response = client.sync_request(new_event_request, timeout=30)

        if new_event_response.message_type == Message.MESSAGE_TYPE_ERROR:
            print("Error invoking service with topic '{}': {} ({})".format(
                request_topic, new_event_response.error_message,
                new_event_response.error_code))
            exit(1)

        # Wait a few seconds for the new MISP event notification to be delivered
        # to the DXL fabric
        time.sleep(5)


After connecting to the DXL fabric, a request message is created with a topic
that targets the "new_event" method of the MISP DXL Python Service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include information to store in the MISP event.

The next step is to perform a synchronous request via the DXL fabric. The
presence of the new MISP event on the server should trigger the receipt of
the event notification above.
