from __future__ import absolute_import
import logging
import os
import threading
import zmq
from pymisp import PyMISP

from dxlbootstrap.app import Application
from dxlclient import ServiceRegistrationInfo
from dxlclient.message import Event
from dxlmispservice._requesthandlers import MispServiceRequestCallback

# Configure local logger
logger = logging.getLogger(__name__)


class MispService(Application):
    """
    The "MISP DXL Python Service" application class.
    """

    #: The base name for MISP DXL Python Service and topics.
    _SERVICE_BASE_NAME = "/opendxl-misp"
    #: The DXL Python Service type for the MISP API.
    _SERVICE_TYPE = _SERVICE_BASE_NAME + "/service/misp-api"

    #: The name of the "General" section within the application configuration
    #: file.
    _GENERAL_CONFIG_SECTION = "General"
    #: The property used to specify a unique service discriminator to the
    #: application configuration file. The discriminator, if set, is added to
    #: each of the MISP API topics registered with and each of the MISP event
    #: notifications delivered through the DXL fabric.
    _GENERAL_SERVICE_UNIQUE_ID_PROP = "serviceUniqueId"
    #: The property used to specify the hostname or IP address of an
    #: MISP server in the application configuration file.
    _GENERAL_HOST_CONFIG_PROP = "host"
    #: The property used to specify the port number of the MISP API server in
    #: the application configuration file.
    _GENERAL_API_PORT_CONFIG_PROP = "apiPort"
    #: The property used to specify the MISP API key in the application
    #: configuration file.
    _GENERAL_API_KEY_CONFIG_PROP = "apiKey"
    #: The property used to specify the list of accessible MISP APIs in the
    #: application configuration file
    _GENERAL_API_NAMES_CONFIG_PROP = "apiNames"
    #: The property used to specify in the application configuration file a
    #: path to a client certificate which is supplied to the MISP
    #: server for TLS/SSL connections.
    _GENERAL_CLIENT_CERTIFICATE_CONFIG_PROP = "clientCertificate"
    #: The property used to specify in the application configuration file a
    #: private key to use when making TLS/SSL connnections to a MISP
    #: server.
    _GENERAL_CLIENT_KEY_CONFIG_PROP = "clientKey"
    #: The property used to specify in the application configuration file
    #: whether or not the MISP server certificate was signed by
    #: a valid certificate authority.
    _GENERAL_VERIFY_CERTIFICATE_CONFIG_PROP = "verifyCertificate"
    #: The property used to specify in the application configuration file
    #: a path to a bundle of trusted CA certificates to use for validating the
    #: MISP server's certificate.
    _GENERAL_VERIFY_CERT_BUNDLE_CONFIG_PROP = "verifyCertBundle"
    #: The property used to specify the port number of the MISP ZeroMQ server in
    #: the application configuration file.
    _GENERAL_ZEROMQ_PORT_CONFIG_PROP = "zeroMqPort"
    #: The property used to specify in the application configuration file the
    #: names of the MISP ZeroMQ topics for which corresponding events should be
    #: delivered to the DXL fabric.
    _GENERAL_ZEROMQ_NOTIFICATION_TOPICS_CONFIG_PROP = "zeroMqNotificationTopics"

    #: Default port number at which the MISP API server is expected to be hosted.
    _DEFAULT_API_PORT = 443
    #: Default port number at which the MISP ZeroMQ server is expected to be hosted.
    _DEFAULT_ZEROMQ_PORT = 50000

    #: The base name for DXL topics delivered for MISP ZeroMQ notifications.
    _ZEROMQ_NOTIFICATIONS_EVENT_TOPIC = _SERVICE_BASE_NAME + \
                                        "/event/zeromq-notifications"

    def __init__(self, config_dir):
        """
        Constructor parameters:

        :param config_dir: The location of the configuration files for the
            application
        """
        super(MispService, self).__init__(config_dir, "dxlmispservice.config")
        self.__lock = threading.RLock()
        self.__destroyed = False
        self._service_unique_id = None
        self._api_client = None
        self._api_names = ()
        self._zeromq_context = None
        self._zeromq_notification_topics = None
        self._zeromq_poller = None
        self._zeromq_misp_sub_socket = None
        self._zeromq_shutdown_push_socket = None
        self._zeromq_shutdown_pull_socket = None
        self._zeromq_thread = None

    @property
    def client(self):
        """
        The DXL client used by the application to communicate with the DXL
        fabric
        """
        return self._dxl_client

    @property
    def config(self):
        """
        The application configuration (as read from the "dxlmispservice.config" file)
        """
        return self._config

    def on_run(self):
        """
        Invoked when the application has started running.
        """
        logger.info("On 'run' callback.")

    def _get_setting_from_config(self, section, setting,
                                 default_value=None,
                                 return_type=str,
                                 raise_exception_if_missing=False,
                                 is_file_path=False):
        """
        Get the value for a setting in the application configuration file.

        :param str section: Name of the section in which the setting resides.
        :param str setting: Name of the setting.
        :param default_value: Value to return if the setting is not found in
            the configuration file.
        :param type return_type: Expected 'type' of the value to return.
        :param bool raise_exception_if_missing: Whether or not to raise an
            exception if the setting is missing from the configuration file.
        :param bool is_file_path: Whether or not the value for the setting
            represents a file path. If set to 'True' but a file cannot be
            found for the setting, a ValueError is raised.
        :return: Value for the setting.
        :raises ValueError: If the setting cannot be found in the configuration
            file and 'raise_exception_if_missing' is set to 'True', the
            type of the setting found in the configuration file does not
            match the value specified for 'return_type', or 'is_file_path' is
            set to 'True' but no file can be found which matches the value
            read for the setting.
        """
        config = self.config
        if config.has_option(section, setting):
            getter_methods = {str: config.get,
                              list: config.get,
                              bool: config.getboolean,
                              int: config.getint,
                              float: config.getfloat}
            try:
                return_value = getter_methods[return_type](section, setting)
            except ValueError as ex:
                raise ValueError(
                    "Unexpected value for setting {} in section {}: {}".format(
                        setting, section, ex))
            if return_type == str:
                return_value = return_value.strip()
                if len(return_value) is 0 and raise_exception_if_missing:
                    raise ValueError(
                        "Required setting {} in section {} is empty".format(
                            setting, section))
            elif return_type == list:
                return_value = [item.strip()
                                for item in return_value.split(",")]
                if len(return_value) is 1 and len(return_value[0]) is 0 \
                        and raise_exception_if_missing:
                    raise ValueError(
                        "Required setting {} in section {} is empty".format(
                            setting, section))
        elif raise_exception_if_missing:
            raise ValueError(
                "Required setting {} not found in {} section".format(setting,
                                                                     section))
        else:
            return_value = default_value

        if is_file_path and return_value:
            return_value = self._get_path(return_value)
            if not os.path.isfile(return_value):
                raise ValueError(
                    "Cannot find file for setting {} in section {}: {}".format(
                        setting, section, return_value))

        return return_value

    def on_load_configuration(self, config):
        """
        Invoked after the application-specific configuration has been loaded

        This callback provides the opportunity for the application to parse
        additional configuration properties.

        :param configparser.ConfigParser config: The application configuration
        """
        logger.info("On 'load configuration' callback.")

        self._service_unique_id = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_SERVICE_UNIQUE_ID_PROP)

        host = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_HOST_CONFIG_PROP,
            raise_exception_if_missing=True)

        api_port = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_API_PORT_CONFIG_PROP,
            return_type=int,
            default_value=self._DEFAULT_API_PORT)

        self._api_names = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_API_NAMES_CONFIG_PROP,
            return_type=list,
            default_value=[])

        # Only validate MISP API configuration and connect to a MISP API server
        # if at least one API name was specified in the configuration file.
        if self._api_names:
            api_key = self._get_setting_from_config(
                self._GENERAL_CONFIG_SECTION,
                self._GENERAL_API_KEY_CONFIG_PROP,
                raise_exception_if_missing=True
            )
            api_url = "https://{}:{}".format(host, api_port)

            verify_certificate = self._get_setting_from_config(
                self._GENERAL_CONFIG_SECTION,
                self._GENERAL_VERIFY_CERTIFICATE_CONFIG_PROP,
                return_type=bool,
                default_value=True
            )
            if verify_certificate:
                verify_cert_bundle = self._get_setting_from_config(
                    self._GENERAL_CONFIG_SECTION,
                    self._GENERAL_VERIFY_CERT_BUNDLE_CONFIG_PROP,
                    is_file_path=True
                )
                if verify_cert_bundle:
                    verify_certificate = verify_cert_bundle

            client_certificate = self._get_setting_from_config(
                self._GENERAL_CONFIG_SECTION,
                self._GENERAL_CLIENT_CERTIFICATE_CONFIG_PROP,
                is_file_path=True
            )
            client_key = self._get_setting_from_config(
                self._GENERAL_CONFIG_SECTION,
                self._GENERAL_CLIENT_KEY_CONFIG_PROP,
                is_file_path=True
            )

            if client_certificate:
                if client_key:
                    cert = (client_certificate, client_key)
                else:
                    cert = client_certificate
            else:
                cert = None

            logger.info("Connecting to MISP API URL: %s", api_url)
            self._api_client = PyMISP(api_url, api_key,
                                      ssl=verify_certificate, cert=cert)

        self._zeromq_notification_topics = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_ZEROMQ_NOTIFICATION_TOPICS_CONFIG_PROP,
            return_type=list,
            default_value=[])

        # Only validate MISP ZeroMQ configuration and connect to a MISP ZeroMQ
        # server if at least one ZeroMQ topic was specified in the
        # configuration file.
        if self._zeromq_notification_topics:
            zeromq_port = self._get_setting_from_config(
                self._GENERAL_CONFIG_SECTION,
                self._GENERAL_ZEROMQ_PORT_CONFIG_PROP,
                default_value=self._DEFAULT_ZEROMQ_PORT,
                return_type=int
            )
            self._setup_zeromq_sockets(host, zeromq_port)

    @staticmethod
    def _create_zeromq_socket(context, host, socket_type, description,
                              port=None, topics=None, log_level=logging.INFO):
        """
        Create a ZeroMQ socket and, optionally, subscribe the socket to
        one or more topics.

        :param context: The ZeroMQ context.
        :param str host: The host to which to connect.
        :param str socket_type: The ZeroMQ socket type - zmq.PUB, zmq.SUB,
            zmq.PULL, zmq.PUSH, etc.
        :param description: Description of the ZeroMQ socket - used in
            logging messages.
        :param int port: The ZeroMQ port to which to connect. If `None` or `0`,
            the socket will be bound to a random port.
        :param list(str) topics: List of topics to which to subscribe the
            socket.
        :param int log_level: Level at which to log socket messages
        :return: A tuple containing the ZeroMQ socket as the first element
            and port to which the socket is attached as the second element.
        :rtype: (socket, int)
        """

        socket = context.socket(socket_type)
        base_socket_url = "tcp://{}".format(host)

        if port:
            socket_url = "{}:{}".format(base_socket_url, port)
            logger.log(log_level, "Connecting to %s ZeroMQ URL: %s",
                       description, socket_url)
            socket.connect(socket_url)
        else:
            logger.log(log_level, "Binding to %s ZeroMQ URL: %s",
                       description, base_socket_url)
            port = socket.bind_to_random_port(base_socket_url)
            socket_url = "{}:{}".format(base_socket_url, port)
            logger.debug("Bound %s ZeroMQ URL: %s", description, socket_url)

        socket.setsockopt(zmq.LINGER, 0)  # pylint: disable=no-member

        if topics:
            for topic in topics:
                logger.log(log_level, "Subscribing to %s ZeroMQ topic: %s ...",
                           description, topic)
                socket.subscribe(topic)

        return socket, port

    def _setup_zeromq_sockets(self, host, port):
        """
        Connect to the ZeroMQ socket hosted by the MISP server, subscribe for
        notifications for configured topics, and start a background thread
        which polls for MISP notifications. Also setup a 'shutdown' ZeroMQ
        socket to be used internally for terminating the MISP notification poll
        at service shutdown time.

        :param str host: Host name / ip address of the MISP ZeroMQ server.
        :param int port: Port at which the MISP ZeroMQ server is hosted.
        """
        self._zeromq_context = zmq.Context()

        self._zeromq_misp_sub_socket, _ = self._create_zeromq_socket(
            self._zeromq_context, host,
            zmq.SUB,  # pylint: disable=no-member
            "MISP", port=port, topics=self._zeromq_notification_topics)

        shutdown_host = "127.0.0.1"

        self._zeromq_shutdown_pull_socket, shutdown_port = \
            self._create_zeromq_socket(
                self._zeromq_context, shutdown_host,
                zmq.PULL,  # pylint: disable=no-member
                "Shutdown PULL", log_level=logging.DEBUG)

        self._zeromq_shutdown_push_socket, _ = self._create_zeromq_socket(
            self._zeromq_context, shutdown_host,
            zmq.PUSH,  # pylint: disable=no-member
            "Shutdown PUSH", port=shutdown_port, log_level=logging.DEBUG)

        self._zeromq_poller = zmq.Poller()
        self._zeromq_poller.register(self._zeromq_misp_sub_socket, zmq.POLLIN)
        self._zeromq_poller.register(self._zeromq_shutdown_pull_socket,
                                     zmq.POLLIN)

        zeromq_thread = threading.Thread(
            target=self._process_zeromq_misp_messages)
        zeromq_thread.daemon = True
        self._zeromq_thread = zeromq_thread
        self._zeromq_thread.start()

    def _process_zeromq_misp_messages(self):
        """
        Poll for MISP ZeroMQ notifications. On receipt of a notification,
        send a corresponding event to the DXL fabric.
        """
        while not self.__destroyed:
            try:
                socks = dict(self._zeromq_poller.poll(timeout=None))
            # A ZMQError could be raised if the socket is shut down while
            # blocked in a poll.
            except zmq.ZMQError:
                socks = {}
            if self._zeromq_misp_sub_socket in socks and \
                    socks[self._zeromq_misp_sub_socket] == zmq.POLLIN:
                message = self._zeromq_misp_sub_socket.recv_string()
                topic, _, payload = message.partition(" ")
                logger.debug("Received notification for %s", topic)
                full_event_topic = "{}{}/{}".format(
                    self._ZEROMQ_NOTIFICATIONS_EVENT_TOPIC,
                    "/{}".format(self._service_unique_id)
                    if self._service_unique_id else "",
                    topic)
                event = Event(full_event_topic)
                logger.debug("Forwarding notification to %s ...",
                             full_event_topic)
                event.payload = payload
                self.client.send_event(event)

    @staticmethod
    def _close_zeromq_socket(socket, description):
        """
        Close the supplied ZeroMQ socket.

        :param socket: The ZeroMQ socket to close.
        :param description: Description of the ZeroMQ socket - used in
            logging messages.
        """
        if socket:
            logger.debug("Closing ZeroMQ %s socket ...", description)
            socket.close()
            logger.debug("ZeroMQ %s socket closed", description)

    def destroy(self):
        """
        Destroys the application (disconnects from fabric and frees resources
        allocated to handle ZeroMQ notifications)
        """
        super(MispService, self).destroy()
        with self.__lock:
            if not self.__destroyed:
                self.__destroyed = True
                self._close_zeromq_socket(self._zeromq_misp_sub_socket, "MISP")
                if self._zeromq_shutdown_push_socket:
                    # Send message to the Shutdown PULL socket to interrupt
                    # the ZeroMQ polling operation
                    self._zeromq_shutdown_push_socket.send_string("interrupt")
                if self._zeromq_thread:
                    logger.debug(
                        "Waiting for ZeroMQ message thread to terminate ...")
                    self._zeromq_thread.join()
                    logger.debug("ZeroMQ message thread terminated")
                self._close_zeromq_socket(self._zeromq_shutdown_push_socket,
                                          "Shutdown PUSH")
                self._close_zeromq_socket(self._zeromq_shutdown_pull_socket,
                                          "Shutdown PULL")
                if self._zeromq_poller:
                    if self._zeromq_misp_sub_socket:
                        self._zeromq_poller.unregister(
                            self._zeromq_misp_sub_socket)
                    if self._zeromq_shutdown_pull_socket:
                        self._zeromq_poller.unregister(
                            self._zeromq_shutdown_pull_socket)
                if self._zeromq_context:
                    logger.debug("Terminating ZeroMQ context...")
                    self._zeromq_context.term()
                    logger.debug("ZeroMQ context terminated")

    def on_dxl_connect(self):
        """
        Invoked after the client associated with the application has connected
        to the DXL fabric.
        """
        logger.info("On 'DXL connect' callback.")

    def _get_api_method(self, api_name):
        """
        Retrieve an instance method from the PyMISP API client object.

        :param str api_name: String name of the instance method object to
            retrieve from the PyMISP client object.
        :return: Matching instancemethod if available, else None.
        :rtype: instancemethod
        """
        api_method = None
        if hasattr(self._api_client, api_name):
            api_attr = getattr(self._api_client, api_name)
            if callable(api_attr):
                api_method = api_attr
        return api_method

    def on_register_services(self):
        """
        Invoked when services should be registered with the application
        """
        api_methods = []
        for api_name in self._api_names:
            api_method = self._get_api_method(api_name)
            if api_method:
                api_methods.append(api_method)
            else:
                logger.warning("MISP API name is invalid: %s",
                               api_name)

        if api_methods:
            logger.info("Registering service: misp_service")
            service = ServiceRegistrationInfo(
                self._dxl_client,
                self._SERVICE_TYPE)

            for api_method in api_methods:
                api_method_name = api_method.__name__
                topic = "{}{}/{}".format(
                    self._SERVICE_TYPE,
                    "/{}".format(self._service_unique_id)
                    if self._service_unique_id else "",
                    api_method_name)
                logger.info(
                    "Registering request callback: %s%s_%s_%s. Topic: %s.",
                    "misp",
                    "_{}".format(self._service_unique_id)
                    if self._service_unique_id else "",
                    api_method_name,
                    "requesthandler",
                    topic)
                self.add_request_callback(
                    service,
                    topic,
                    MispServiceRequestCallback(self, api_method),
                    False)

            self.register_service(service)
