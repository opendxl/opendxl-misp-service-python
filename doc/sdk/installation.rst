Installation
============

Prerequisites
*************

* OpenDXL Python Client library installed
   `<https://github.com/opendxl/opendxl-client-python>`_

* The OpenDXL Python Client prerequisites must be satisfied
   `<https://opendxl.github.io/opendxl-client-python/pydoc/installation.html>`_

* MISP server installed and configured.

  The following page provides several different options for installing MISP:
   `<http://www.misp-project.org/download/>`_.

  One option for getting a MISP environment up and running fairly quickly is the
  "Docker container" approach provided at `<https://github.com/opendxl-community/docker-misp>`_.
  Note that this docker-misp project is a fork of the `<https://github.com/harvard-itsecurity/docker-misp>`_
  project.

  The opendxl-community fork aims to enable the ability to pull an all-in-one
  MISP container from `Docker Hub <https://hub.docker.com/r/opendxlcommunity/misp>`_
  and launch an image from it with little to no additional configuration. For a
  more robust  setup, it would be better to refer to the upstream
  `<https://github.com/harvard-itsecurity/docker-misp>`_ project.

* (Optional) MISP ZeroMQ notification configured.

  If you intend to use the ZeroMQ notification functionality with the OpenDXL
  MISP Python service, you will need to enable the ZeroMQ plugin in MISP.
  From the MISP web server UI, do the following:

  * Navigate to the ``Server Settings & Maintenance`` page under the
    ``Administration`` menu.
  * Select the ``Plugin Settings`` tab.
  * Expand the ``ZeroMQ`` option in the plugin list.
  * Set the ``Plugin.ZeroMQ_enable`` setting to ``true``.

  This step is needed to enable the DXL MISP service to be able to receive
  notification messages from the MISP ZeroMQ server. For more information, see
  the documentation for the
  `MISP ZeroMQ configuration <https://misp.gitbooks.io/misp-book/misp-zmq/#misp-zeromq-configuration>`__.
  and the ``zeroMqNotificationTopics`` setting in the
  :ref:`Service Configuration File <dxl_service_config_file_label>` section.

* Python 2.7.9 or higher in the Python 2.x series or 3.4.0 or higher in the Python 3.x series installed within a Windows or Linux environment.

Installation
************

This distribution contains a ``lib`` sub-directory that includes the application library files.

Use ``pip`` to automatically install the library:

    .. parsed-literal::

        pip install dxlmispservice-\ |version|\-py2.py3-none-any.whl

Or with:

    .. parsed-literal::

        pip install dxlmispservice-\ |version|\.zip

As an alternative (without PIP), unpack the dxlmispservice-\ |version|\.zip (located in the lib folder) and run the setup
script:

    .. parsed-literal::

        python setup.py install
