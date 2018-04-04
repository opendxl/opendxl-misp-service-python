from __future__ import absolute_import
import logging
import threading
import zmq

from dxlbootstrap.app import Application
from dxlclient.message import Event

# Configure local logger
logger = logging.getLogger(__name__)


class MispService(Application):
    """
    The "MISP DXL service library" application class.
    """

    _GENERAL_CONFIG_SECTION = "General"
    _GENERAL_SERVICE_UNIQUE_ID_PROP = "serviceUniqueId"
    _GENERAL_ZEROMQ_HOST = "zeroMqHost"
    _GENERAL_ZEROMQ_PORT = "zeroMqPort"
    _GENERAL_ZEROMQ_NOTIFICATION_TOPICS_CONFIG_PROP = "zeroMqNotificationTopics"

    _DEFAULT_ZEROMQ_PORT = "50000"
    _ZEROMQ_NOTIFICATIONS_EVENT_TOPIC = "/opendxl-misp/service/zeromq-notifications"
    _ZEROMQ_TOPIC_PREFIX = "misp_json_"

    def __init__(self, config_dir):
        """
        Constructor parameters:

        :param config_dir: The location of the configuration files for the
            application
        """
        super(MispService, self).__init__(config_dir, "dxlmispservice.config")
        self.__lock = threading.RLock()
        self.__destroyed = False
        self._zeromq_socket = None
        self._zeromq_thread = None
        self._service_unique_id = None

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
                                 raise_exception_if_missing=False):
        """
        Get the value for a setting in the application configuration file.

        :param str section: Name of the section in which the setting resides.
        :param str setting: Name of the setting.
        :param default_value: Value to return if the setting is not found in
            the configuration file.
        :param type return_type: Expected 'type' of the value to return.
        :param bool raise_exception_if_missing: Whether or not to raise an
            exception if the setting is missing from the configuration file.
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

        return return_value

    def on_load_configuration(self, config):
        """
        Invoked after the application-specific configuration has been loaded

        This callback provides the opportunity for the application to parse
        additional configuration properties.

        :param config: The application configuration
        """
        logger.info("On 'load configuration' callback.")

        self._service_unique_id = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_SERVICE_UNIQUE_ID_PROP)

        self._zeromq_notification_topics = self._get_setting_from_config(
            self._GENERAL_CONFIG_SECTION,
            self._GENERAL_ZEROMQ_NOTIFICATION_TOPICS_CONFIG_PROP,
            return_type=list
        )

        if self._zeromq_notification_topics:
            zeromq_host = self._get_setting_from_config(
                self._GENERAL_CONFIG_SECTION,
                self._GENERAL_ZEROMQ_HOST,
                return_type=str,
                raise_exception_if_missing=True
            )

            zeromq_port = self._get_setting_from_config(
                self._GENERAL_CONFIG_SECTION,
                self._GENERAL_ZEROMQ_PORT,
                default_value=self._DEFAULT_ZEROMQ_PORT,
                return_type=str
            )

            context = zmq.Context()
            self._zeromq_socket = context.socket(zmq.SUB)
            socket_url = "tcp://%s:%s" % (zeromq_host, zeromq_port)
            logger.info("Connecting to zeromq URL: %s", socket_url)
            self._zeromq_socket.connect(socket_url)
            for topic in self._zeromq_notification_topics:
                subscription_topic = self._ZEROMQ_TOPIC_PREFIX + topic
                logger.debug("Subscribing to zeromq topic: %s",
                             subscription_topic)
                self._zeromq_socket.subscribe(subscription_topic)
            logger.info("Waiting for zeromq notifications: %s",
                        self._zeromq_notification_topics)

            self._zeromq_poller = zmq.Poller()
            self._zeromq_poller.register(self._zeromq_socket, zmq.POLLIN)
            zeromq_thread = threading.Thread(
                target=self._process_zeromq_messages)
            zeromq_thread.daemon = True
            self._zeromq_thread = zeromq_thread
            self._zeromq_thread.start()

    def _process_zeromq_messages(self):
        while not self.__destroyed:
            try:
                socks = dict(self._zeromq_poller.poll(timeout=None))
            except zmq.ZMQError:
                socks = {}
            if self._zeromq_socket in socks and \
                socks[self._zeromq_socket] == zmq.POLLIN:
                message = self._zeromq_socket.recv_string()
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

    def destroy(self):
        super(MispService, self).destroy()
        with self.__lock:
            if not self.__destroyed:
                self.__destroyed = True
                if self._zeromq_socket:
                    logger.debug("Closing zeromq socket ...")
                    self._zeromq_socket.close()
                if self._zeromq_thread:
                    logger.debug(
                        "Waiting for zeromq message thread to terminate ...")
                    self._zeromq_thread.join()
                    logger.debug("Zeromq message thread terminated")

    def on_dxl_connect(self):
        """
        Invoked after the client associated with the application has connected
        to the DXL fabric.
        """
        logger.info("On 'DXL connect' callback.")
