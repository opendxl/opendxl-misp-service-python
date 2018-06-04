Basic New Event Example
=======================

This sample creates a new event on a MISP server via the MISP ``Events`` API.
The sample then retrieves the contents of the stored event via a call to the
MISP ``Search`` API. The sample displays the results of the calls to the
``Events`` and ``Search`` APIs.

For more information on the MISP ``Events`` API, see the
`PyMISP new_event API <https://media.readthedocs.org/pdf/pymisp/master/pymisp.pdf>`__
and `MISP REST Event API <https://misp.gitbooks.io/misp-book/content/automation/#post-events>`__
documentation.

Prerequisites
*************

* The samples configuration step has been completed (see :doc:`sampleconfig`).
* The MISP DXL Python Service is running, using the ``sample`` configuration
  (see :doc:`running`).

Running
*******

To run this sample execute the ``sample/basic/basic_new_event_example.py``
script as follows:

    .. code-block:: shell

        python sample/basic/basic_new_event_example.py

The output should appear similar to the following:

    .. code-block:: shell

        Response to the new event request:
        {
            "Event": {
                "Attribute": [],
                "Galaxy": [],
                "Object": [],
                "Org": {
                    "id": "1",
                    "name": "ORGNAME",
                    "uuid": "5ac3c55a-41a4-4294-adf3-00f8ac110003"
                },
                "Orgc": {
                    "id": "1",
                    "name": "ORGNAME",
                    "uuid": "5ac3c55a-41a4-4294-adf3-00f8ac110003"
                },
                "RelatedEvent": [],
                "ShadowAttribute": [],
                "analysis": "1",
                "attribute_count": "0",
                "date": "2018-04-09",
                "disable_correlation": false,
                "distribution": "3",
                "event_creator_email": "admin@admin.test",
                "id": "169",
                "info": "OpenDXL MISP new event example",
                "locked": false,
                "org_id": "1",
                "orgc_id": "1",
                "proposal_email_lock": false,
                "publish_timestamp": "0",
                "published": false,
                "sharing_group_id": "0",
                "threat_level_id": "3",
                "timestamp": "1523287869",
                "uuid": "5acb873d-a914-4f9f-92b9-196cac110002"
            }
        }
        Response to the search request for the new MISP event:
        {
            "response": [
                {
                    "Event": {
                        "Attribute": [],
                        "Galaxy": [],
                        "Object": [],
                        "Org": {
                            "id": "1",
                            "name": "ORGNAME",
                            "uuid": "5ac3c55a-41a4-4294-adf3-00f8ac110003"
                        },
                        "Orgc": {
                            "id": "1",
                            "name": "ORGNAME",
                            "uuid": "5ac3c55a-41a4-4294-adf3-00f8ac110003"
                        },
                        "RelatedEvent": [],
                        "ShadowAttribute": [],
                        "analysis": "1",
                        "attribute_count": "0",
                        "date": "2018-04-09",
                        "disable_correlation": false,
                        "distribution": "3",
                        "event_creator_email": "admin@admin.test",
                        "id": "169",
                        "info": "OpenDXL MISP new event example",
                        "locked": false,
                        "org_id": "1",
                        "orgc_id": "1",
                        "proposal_email_lock": false,
                        "publish_timestamp": "0",
                        "published": false,
                        "sharing_group_id": "0",
                        "threat_level_id": "3",
                        "timestamp": "1523287869",
                        "uuid": "5acb873d-a914-4f9f-92b9-196cac110002"
                    }
                }
            ]
        }

Details
*******

In order to enable the use of the ``new_event`` and ``search`` APIs, both API
names are listed in the ``apiNames`` setting under the ``[General]`` section in
the ``sample`` "dxlmispservice.config" file that the service uses:

    .. code-block:: ini

        [General]
        apiNames=new_event,search...

For more information on the configuration, see the
:ref:`Service Configuration File <dxl_service_config_file_label>` section.

The majority of the sample code is shown below:

    .. code-block:: python

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


After connecting to the DXL fabric, a request message is created with a topic
that targets the "new_event" method of the MISP DXL Python Service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include information to store in the MISP event.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

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


To confirm that the event was stored properly, a second request message is
created with a topic that targets the "search" method of the MISP DXL
service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``eventid`` of the event to retrieve. Note that the
``eventid`` used in the search request is extracted from the response
received for the prior "new_event" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.
