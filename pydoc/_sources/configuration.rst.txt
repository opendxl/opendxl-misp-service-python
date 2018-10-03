Configuration
=============

The MISP DXL Python Service application requires a set of configuration files to operate.

This distribution contains a ``config`` sub-directory that includes the configuration files that must
be populated prior to running the application.

Each of these files are documented throughout the remainder of this page.

Application configuration directory:

    .. code-block:: python

        config/
            dxlclient.config
            dxlmispservice.config
            logging.config (optional)

.. _dxl_client_config_file_label:

DXL Client Configuration File (dxlclient.config)
------------------------------------------------

    The required ``dxlclient.config`` file is used to configure the DXL client that will connect to the DXL fabric.

    The steps to populate this configuration file are the same as those documented in the `OpenDXL Python
    SDK`, see the
    `OpenDXL Python SDK Samples Configuration <https://opendxl.github.io/opendxl-client-python/pydoc/sampleconfig.html>`_
    page for more information.

    The following is an example of a populated DXL client configuration file:

        .. code-block:: python

            [Certs]
            BrokerCertChain=c:\\certificates\\brokercerts.crt
            CertFile=c:\\certificates\\client.crt
            PrivateKey=c:\\certificates\\client.key

            [Brokers]
            {5d73b77f-8c4b-4ae0-b437-febd12facfd4}={5d73b77f-8c4b-4ae0-b437-febd12facfd4};8883;mybroker.mcafee.com;192.168.1.12
            {24397e4d-645f-4f2f-974f-f98c55bdddf7}={24397e4d-645f-4f2f-974f-f98c55bdddf7};8883;mybroker2.mcafee.com;192.168.1.13

.. _dxl_service_config_file_label:

MISP DXL Python Service (dxlmispservice.config)
-----------------------------------------------

    The required ``dxlmispservice.config`` file is used to configure the application.

    The following is an example of a populated application configuration file:

        .. code-block:: ini

            [General]
            host=mispserver1
            apiKey=12345
            apiNames=new_event,search,add_internal_comment,tag,sighting
            verifyCertificate=yes
            verifyCertBundle=mispCA.crt
            zeroMqNotificationTopics=misp_json,misp_json_sighting

    **General**

        The ``[General]`` section is used to specify the MISP server
        configuration, MISP API methods which should be available to invoke via
        DXL, and MISP ZeroMQ messages which should be forwarded on to the DXL
        fabric.

        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | Name                             | Required | Description                                                                                            |
        +==================================+==========+========================================================================================================+
        | host                             | yes      | The MISP server hostname or IP address.                                                                |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | serviceUniqueId                  | no       | An optional unique identifier used to identify the                                                     |
        |                                  |          | opendxl-misp service on the DXL fabric. If set, this                                                   |
        |                                  |          | unique identifier will be appended to the name of each event and request                               |
        |                                  |          | topic used on the fabric. For example, if the serviceUniqueId is                                       |
        |                                  |          | set to ``sample``, the request and event topic names would start with the                              |
        |                                  |          | following, respectively:                                                                               |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/service/misp-api/sample/<method>``                                                     |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/event/zeromq-notifications/sample/<zeromq-topic>``                                     |
        |                                  |          |                                                                                                        |
        |                                  |          | If serviceUniqueId is not set, request and event topic names would not                                 |
        |                                  |          | include an id segment, for example:                                                                    |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/service/misp-api/<method>``                                                            |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/event/zeromq-notifications/<zeromq-topic>``                                            |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | apiNames                         | no       | The list of MISP APIs for which corresponding request topics should be exposed                         |
        |                                  |          | to the DXL fabric, delimited by commas.                                                                |
        |                                  |          |                                                                                                        |
        |                                  |          | For example: ``new_event,search,update``                                                               |
        |                                  |          |                                                                                                        |
        |                                  |          | With this example and the ``serviceUniqueId`` setting set to                                           |
        |                                  |          | ``sample``, the request topics exposed to the DXL fabric would be:                                     |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/service/misp-api/sample/new_event``                                                    |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/service/misp-api/sample/search``                                                       |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/service/misp-api/sample/update``                                                       |
        |                                  |          |                                                                                                        |
        |                                  |          | The complete list of available API method names and parameters is available                            |
        |                                  |          | in the documentation for the pymisp.PyMISP class at                                                    |
        |                                  |          | https://media.readthedocs.org/pdf/pymisp/latest/pymisp.pdf.                                            |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | apiKey                           | no       | The MISP server's API key. Note that this property is required if one or more ``apiNames`` is          |
        |                                  |          | specified.                                                                                             |
        |                                  |          |                                                                                                        |
        |                                  |          | The API key is accessible from the MISP web server UI. Navigate to the ``Automation`` page under the   |
        |                                  |          | ``Event Actions`` menu. Copy the value which follows the text ``Your current key is:`` into this       |
        |                                  |          | property. For more information, see                                                                    |
        |                                  |          | https://misp.gitbooks.io/misp-book/content/automation/#automation-key.                                 |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | apiPort                          | no       | The MISP server's HTTP API port. Defaults to ``443``.                                                  |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | verifyCertificate                | no       | Whether to verify that MISP server's certificate was                                                   |
        |                                  |          | signed by a valid certificate authority when SSL/TLS is being                                          |
        |                                  |          | used. Defaults to ``yes``.                                                                             |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | verifyCertBundle                 | no       | A path to a CA Bundle file containing certificates of trusted                                          |
        |                                  |          | CAs. The CA Bundle is used to ensure that the MISP                                                     |
        |                                  |          | server being connected to was signed by a valid authority. Only                                        |
        |                                  |          | applicable if ``verifyCertificate`` is ``yes``.                                                        |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | clientCertificate                | no       | A path to a client certificate supplied to the MISP                                                    |
        |                                  |          | server for TLS/SSL connections. Defaults to not using a client                                         |
        |                                  |          | certificate.                                                                                           |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | clientKey                        | no       | A path to a client private key used for TLS/SSL connections made                                       |
        |                                  |          | to the MISP server. Defaults to not using a client                                                     |
        |                                  |          | private key.                                                                                           |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | zeroMqNotificationTopics         | no       | The list of topics for MISP ZeroMQ messages which should be forwarded on to the DXL fabric.            |
        |                                  |          |                                                                                                        |
        |                                  |          | For example: ``misp_json,misp_json_sighting``                                                          |
        |                                  |          |                                                                                                        |
        |                                  |          | With this example and the ``serviceUniqueId`` setting set to ``sample``, any ZeroMQ message with a     |
        |                                  |          | topic of "misp_json" or "misp_json_sighting" would be forwarded as a DXL event with the                |
        |                                  |          | following topics, respectively:                                                                        |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/event/zeromq-notifications/sample/misp_json``                                          |
        |                                  |          |                                                                                                        |
        |                                  |          | ``/opendxl-misp/event/zeromq-notifications/sample/misp_json_sighting``                                 |
        |                                  |          |                                                                                                        |
        |                                  |          | The complete list of available MISP ZeroMQ messages is available at                                    |
        |                                  |          | https://misp.gitbooks.io/misp-book/content/misp-zmq/.                                                  |
        |                                  |          |                                                                                                        |
        |                                  |          | If you intend to use the ZeroMQ notification functionality with the OpenDXL MISP Python service, you   |
        |                                  |          | will need to enable the ZeroMQ plugin in MISP. This step is needed to enable the DXL MISP service to be|
        |                                  |          | able to receive event notification messages from the MISP ZeroMQ server.                               |
        |                                  |          |                                                                                                        |
        |                                  |          | From the MISP web server UI, do the following:                                                         |
        |                                  |          |                                                                                                        |
        |                                  |          | * Navigate to the ``Server Settings & Maintenance`` page under the ``Administration`` menu.            |
        |                                  |          | * Select the ``Plugin Settings`` tab.                                                                  |
        |                                  |          | * Expand the ``ZeroMQ`` option in the plugin list.                                                     |
        |                                  |          | * Set the ``Plugin.ZeroMQ_enable`` setting to ``true``.                                                |
        |                                  |          | * Set the ``Plugin.ZeroMQ_notifications_enable`` settings to ``true`` for the corresponding topics     |
        |                                  |          |   included in this setting. For example, for the topics ``misp_json,misp_json_sighting``, the          |
        |                                  |          |   ``Plugin.ZeroMQ_event_notifications_enable`` and ``Plugin.ZeroMQ_sighting_notifications_enable``     |
        |                                  |          |   settings would need to be set to ``true``.                                                           |
        |                                  |          |                                                                                                        |
        |                                  |          | For more information, see the documentation for the                                                    |
        |                                  |          | `MISP ZeroMQ configuration <https://misp.gitbooks.io/misp-book/misp-zmq/#misp-zeromq-configuration>`__.|
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+
        | zeroMqPort                       | no       | The MISP server's ZeroMQ notification port. Defaults to ``50000``.                                     |
        +----------------------------------+----------+--------------------------------------------------------------------------------------------------------+

Logging File (logging.config)
-----------------------------

    The optional ``logging.config`` file is used to configure how the application writes log messages.
