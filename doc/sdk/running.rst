Running
=======

Once the application library has been installed and the configuration files are populated it can be started by
executing the following command line:

    .. parsed-literal::

        python -m dxlmispservice <configuration-directory>

    The ``<configuration-directory>`` argument must point to a directory containing the configuration files
    required for the application (see :doc:`configuration`).

For example:

    .. parsed-literal::

        python -m dxlmispservice config

Output
------

The output from starting the service with the ``sample`` sub-directory
configuration should appear similar to the following:

    .. code-block:: shell

        Running application ...
        On 'run' callback.
        On 'load configuration' callback.
        Connecting to MISP API URL: https://172.17.0.3:443
        Connecting to MISP ZeroMQ URL: tcp://172.17.0.3:50000
        Subscribing to MISP ZeroMQ topic: misp_json_event ...
        Incoming message configuration: queueSize=1000, threadCount=10
        Message callback configuration: queueSize=1000, threadCount=10
        Attempting to connect to DXL fabric ...
        Connected to DXL fabric.
        Registering service: misp_service
        Registering request callback: misp_new_event_requesthandler. Topic: /opendxl-misp/service/misp-api/new_event.
        Registering request callback: misp_search_requesthandler. Topic: /opendxl-misp/service/misp-api/search.
        Registering request callback: misp_add_internal_comment_requesthandler. Topic: /opendxl-misp/service/misp-api/add_internal_comment.
        Registering request callback: misp_tag_requesthandler. Topic: /opendxl-misp/service/misp-api/tag.
        Registering request callback: misp_sighting_requesthandler. Topic: /opendxl-misp/service/misp-api/sighting.
        On 'DXL connect' callback.
