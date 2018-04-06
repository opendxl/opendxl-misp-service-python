Service Methods
===============

To make a MISP API method available to the DXL fabric, the method
name should be added to the ``apiNames`` setting in the ``[General]`` section
of the :ref:`Service Configuration File <dxl_service_config_file_label>`. The
service registers a DXL request topic for each valid API name listed in the
configuration file. A JSON document with the names and values for each API
parameter should be provided with requests made for the DXL topic.

For example, to make a request to the MISP ``new_event`` API method, the
following steps could be taken:

1) Add ``new_event`` to the list of ``apiNames`` in the configuration file:

    .. code-block:: ini

        [General]
        apiNames=new_event,...

2) (Re)start the DXL MISP service.

    The service should register the following request topic on the DXL fabric:

     **/opendxl-misp/service/misp-api/new_event**

3) Send a request for the DXL topic with a JSON payload which contains the
   desired parameters, for example:

    .. code-block:: json

        {
            "distribution": 3,
            "info": "new event info",
            "analysis": 1,
            "threat_level_id": 3
        }

    The service should respond with the contents of the stored event, for
    example:

    .. code-block:: json

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

The MISP DXL Python Service APIs are basically just thin wrappers on
top of the underlying client APIs used in the
`PyMISP <https://github.com/MISP/PyMISP>`_ Python library. For a complete list
of the available API method names and parameters, see the
`pymisp.PyMISP class documentation <https://media.readthedocs.org/pdf/pymisp/latest/pymisp.pdf>`_.
