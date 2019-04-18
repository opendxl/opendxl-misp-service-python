Basic Update Event Example
==========================

This sample creates a new event on a MISP server via the MISP ``Events`` API.
The sample then performs several updates to the stored event:

* Via a request to the MISP ``Attributes`` API, adds an internal comment
  attribute to the event.
* Via a request to the MISP ``Tag`` API, applies a tag to the internal comment
  attribute.
* Via a request to the MISP ``Sighting`` API, adds a
  `sighting <https://misp.gitbooks.io/misp-book/content/sightings/#sightings>`__
  to the internal comment attribute.

The sample then retrieves the contents of the stored event — including the
associated attribute, tag, and sighting — via a call to the MISP
``Search`` API.

The sample displays the results of the calls made to each of the MISP APIs.

For more information on the MISP APIs used by this sample, see the following
links:

* New Event: `PyMISP new_event API <https://media.readthedocs.org/pdf/pymisp/master/pymisp.pdf>`__
  and `MISP REST Event API <https://misp.gitbooks.io/misp-book/content/automation/#post-events>`__
  documentation.
* Attribute: `PyMISP add_internal_comment API <https://media.readthedocs.org/pdf/pymisp/master/pymisp.pdf>`__
  and `MISP REST Attribute API <https://misp.gitbooks.io/misp-book/content/automation/#attribute-management>`__.
* Tag: `PyMISP tag API <https://media.readthedocs.org/pdf/pymisp/master/pymisp.pdf>`__ and
  `MISP REST Tag API <https://misp.gitbooks.io/misp-book/content/automation/#tag-management>`__.
* Sighting: `PyMISP sighting API <https://media.readthedocs.org/pdf/pymisp/master/pymisp.pdf>`__ and
  `MISP REST Sighting API <https://misp.gitbooks.io/misp-book/content/automation/#sightings-api>`__.
* Search: `PyMISP search API <https://media.readthedocs.org/pdf/pymisp/master/pymisp.pdf>`__ and
  `MISP REST Search API <https://misp.gitbooks.io/misp-book/content/automation/#restful-searches-with-json-result>`__.

Prerequisites
*************

* The samples configuration step has been completed (see :doc:`sampleconfig`).
* The MISP DXL Python Service is running, using the ``sample`` configuration
  (see :doc:`running`).

Running
*******

To run this sample execute the ``sample/basic/basic_update_event_example.py``
script as follows:

    .. code-block:: shell

        python sample/basic/basic_update_event_example.py

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
                "id": "170",
                "info": "OpenDXL MISP update event example",
                "locked": false,
                "org_id": "1",
                "orgc_id": "1",
                "proposal_email_lock": false,
                "publish_timestamp": "0",
                "published": false,
                "sharing_group_id": "0",
                "threat_level_id": "3",
                "timestamp": "1523287902",
                "uuid": "5acb875e-a7e4-4a73-b5f5-196cac110002"
            }
        }
        Response to the add internal comment request:
        [
            {
                "Attribute": {
                    "category": "Internal reference",
                    "comment": "This is only a test",
                    "deleted": false,
                    "disable_correlation": false,
                    "distribution": "5",
                    "event_id": "170",
                    "id": "50",
                    "object_id": "0",
                    "object_relation": null,
                    "sharing_group_id": "0",
                    "timestamp": "1523287902",
                    "to_ids": false,
                    "type": "comment",
                    "uuid": "5acb875e-44a0-402d-8265-013cac110002",
                    "value": "Added by the OpenDXL MISP update event example",
                    "value1": "Added by the OpenDXL MISP update event example",
                    "value2": ""
                }
            }
        ]
        Response to the tag request:
        {
            "message": "Tag Tagged by the OpenDXL MISP update event example(1) successfully attached to Attrib
            "name": "Tag Tagged by the OpenDXL MISP update event example(1) successfully attached to Attribute
            "url": "/tags/attachTagToObject"
        }
        Response to the sighting request:
        {
            "message": "Sighting added.",
            "name": "1 sighting successfully added.",
            "url": "/sightings/add/5acb875e-44a0-402d-8265-013cac110002"
        }
        Response to the search request for the new MISP event:
        {
            "response": [
                {
                    "Event": {
                        "Attribute": [
                            {
                                "ShadowAttribute": [],
                                "Sighting": [
                                    {
                                        "Organisation": {
                                            "id": "1",
                                            "name": "ORGNAME",
                                            "uuid": "5ac3c55a-41a4-4294-adf3-00f8ac110003"
                                        },
                                        "attribute_id": "50",
                                        "date_sighting": "1523287902",
                                        "event_id": "170",
                                        "id": "36",
                                        "org_id": "1",
                                        "source": "Seen by the OpenDXL MISP update event example",
                                        "type": "0",
                                        "uuid": "5acb875e-7a70-4bdd-8cc2-013cac110002"
                                    }
                                ],
                                "Tag": [
                                    {
                                        "colour": "#75705b",
                                        "exportable": true,
                                        "hide_tag": false,
                                        "id": "1",
                                        "name": "Tagged by the OpenDXL MISP update event example",
                                        "user_id": false
                                    }
                                ],
                                "category": "Internal reference",
                                "comment": "This is only a test",
                                "deleted": false,
                                "disable_correlation": false,
                                "distribution": "5",
                                "event_id": "170",
                                "id": "50",
                                "object_id": "0",
                                "object_relation": null,
                                "sharing_group_id": "0",
                                "timestamp": "1523287902",
                                "to_ids": false,
                                "type": "comment",
                                "uuid": "5acb875e-44a0-402d-8265-013cac110002",
                                "value": "Added by the OpenDXL MISP update event example"
                            }
                        ],
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
                        "attribute_count": "1",
                        "date": "2018-04-09",
                        "disable_correlation": false,
                        "distribution": "3",
                        "event_creator_email": "admin@admin.test",
                        "id": "170",
                        "info": "OpenDXL MISP update event example",
                        "locked": false,
                        "org_id": "1",
                        "orgc_id": "1",
                        "proposal_email_lock": false,
                        "publish_timestamp": "0",
                        "published": false,
                        "sharing_group_id": "0",
                        "threat_level_id": "3",
                        "timestamp": "1523287902",
                        "uuid": "5acb875e-a7e4-4a73-b5f5-196cac110002"
                    }
                }
            ]
        }

Details
*******

In order to enable the various APIs used by this sample, each of the API names
are listed in the ``apiNames`` setting under the ``[General]`` section in the
``sample`` "dxlmispservice.config" file that the service uses:

    .. code-block:: ini

        [General]
        apiNames=apiNames=new_event,search,add_internal_comment,sighting

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
                "info": "OpenDXL MISP update event example",
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

        # Extract the id of the new event from the results of the new event request
        misp_event_id = new_event_response_dict["Event"]["id"]

        # Create the add internal comment request
        request_topic = "/opendxl-misp/service/misp-api/add_internal_comment"
        add_internal_comment_request = Request(request_topic)

        # Set the payload for the add internal comment request
        MessageUtils.dict_to_json_payload(add_internal_comment_request, {
            "event": misp_event_id,
            "reference": "Added by the OpenDXL MISP update event example",
            "comment": "This is only a test"
        })

        # Send the add internal comment request
        add_internal_comment_response = client.sync_request(
            add_internal_comment_request, timeout=30)

        if add_internal_comment_response.message_type != Message.MESSAGE_TYPE_ERROR:
            # Display results for the add internal comment request
            add_internal_comment_response_dict = MessageUtils.json_payload_to_dict(
                add_internal_comment_response)
            print("Response to the add internal comment request:\n{}".format(
                MessageUtils.dict_to_json(add_internal_comment_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{}': {} ({})".format(
                request_topic, add_internal_comment_response.error_message,
                add_internal_comment_response.error_code))
            exit(1)


A request message is then created with a topic that targets the
"add_internal_comment" method of the MISP DXL Python Service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the id of the ``event`` to attach the internal comment
to. Note that the ``event`` id value is extracted from the response received for
the prior "new_event" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        # Extract the id of the internal comment from the results of the add
        # internal comment request
        internal_comment_attribute_id = \
            add_internal_comment_response_dict[0]["Attribute"]["uuid"]

        # Create the tag request
        request_topic = "/opendxl-misp/service/misp-api/tag"
        tag_request = Request(request_topic)

        # Set the payload for the tag request
        MessageUtils.dict_to_json_payload(tag_request, {
            "uuid": internal_comment_attribute_id,
            "tag": "Tagged by the OpenDXL MISP update event example"
        })

        # Send the tag request
        tag_response = client.sync_request(tag_request, timeout=30)

        if tag_response.message_type != Message.MESSAGE_TYPE_ERROR:
            # Display results for the tag request
            tag_response_dict = MessageUtils.json_payload_to_dict(tag_response)
            print("Response to the tag request:\n{}".format(
                MessageUtils.dict_to_json(tag_response_dict, pretty_print=True)))
        else:
            print("Error invoking service with topic '{}': {} ({})".format(
                request_topic, tag_response.error_message, tag_response.error_code))
            exit(1)

A request message is then created with a topic that targets the "tag" method of
the MISP DXL Python Service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``uuid`` of the attachment to apply the tag to. Note
that the ``uuid`` value is extracted from the response received for the prior
"add_internal_comment" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        # Create the sighting request
        request_topic = "/opendxl-misp/service/misp-api/sighting"
        sighting_request = Request(request_topic)

        # Set the payload for the sighting request
        MessageUtils.dict_to_json_payload(sighting_request, {
            "uuid": internal_comment_attribute_id,
            "type": "0",
            "source": "Seen by the OpenDXL MISP update event example"
        })


        # Send the sighting request
        sighting_response = client.sync_request(sighting_request, timeout=30)

        if sighting_response.message_type != Message.MESSAGE_TYPE_ERROR:
            # Display results for the sighting request
            sighting_response_dict = MessageUtils.json_payload_to_dict(
                sighting_response)
            print("Response to the sighting request:\n{}".format(
                MessageUtils.dict_to_json(sighting_response_dict,
                                          pretty_print=True)))
        else:
            print("Error invoking service with topic '{}': {} ({})".format(
                request_topic, sighting_response.error_message,
                sighting_response.error_code))
            exit(1)


A request message is then created with a topic that targets the "sighting"
method of the MISP DXL Python Service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``uuid`` of the attachment to apply the sighting to.
Note that the ``uuid`` value is extracted from the response received for the
prior "add_internal_comment" request.

The next step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.

    .. code-block:: python

        # Create the search request
        request_topic = "/opendxl-misp/service/misp-api/search"
        search_request = Request(request_topic)

        # Set the payload for the search request
        MessageUtils.dict_to_json_payload(search_request, {
            "eventid": misp_event_id
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


To confirm that the event, add internal comment attribute, tag, and sighting
were all stored properly, one last request message is created with a topic that
targets the "search" method of the MISP DXL Python Service.

The next step is to set the ``payload`` of the request message. The contents of
the payload include the ``eventid`` of the event to retrieve. Note that the
``eventid`` used in the search request is extracted from the response
received for the initial "new_event" request.

The last step is to perform a synchronous request via the DXL fabric. If the
response message is not an error, its contents are displayed.
