from __future__ import absolute_import
import json
import re
import sys
from tempfile import NamedTemporaryFile
import unittest
import zmq

if sys.version_info[0] > 2:
    import builtins # pylint: disable=import-error, unused-import
    from urllib.parse import quote_plus # pylint: disable=no-name-in-module, import-error, unused-import
else:
    import __builtin__ # pylint: disable=import-error
    builtins = __builtin__ # pylint: disable=invalid-name
    from urllib import quote_plus # pylint: disable=no-name-in-module, ungrouped-imports

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

# pylint: disable=wrong-import-position
from mock import patch
import requests_mock
import dxlmispservice


class StringMatches(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return re.match(self.pattern, other, re.DOTALL)


class StringDoesNotMatch(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return not re.match(self.pattern, other)


class Sample(unittest.TestCase):
    _TEST_HOSTNAME = "127.0.0.1"
    _TEST_API_KEY = "myspecialkey"
    _TEST_API_PORT = "443"

    def get_api_endpoint(self, path):
        return "https://" + self._TEST_HOSTNAME + ":" + self._TEST_API_PORT + \
               "/" + path

    def run_sample(self, sample_file, add_request_mocks_fn=None):
        sample_globals = {"__file__": sample_file}
        context = zmq.Context()
        with requests_mock.mock(case_sensitive=True) as req_mock, \
            dxlmispservice.MispService("sample") as app, \
            NamedTemporaryFile(mode="w+") as temp_config_file, \
            context.socket(zmq.PUB) as zmq_socket: # pylint: disable=no-member
            zmq_port = zmq_socket.bind_to_random_port("tcp://" +
                                                      self._TEST_HOSTNAME)
            config = ConfigParser()
            config.read(app._app_config_path)
            config.set(
                dxlmispservice.MispService._GENERAL_CONFIG_SECTION,
                dxlmispservice.MispService._GENERAL_HOST_CONFIG_PROP,
                self._TEST_HOSTNAME
            )
            config.set(
                dxlmispservice.MispService._GENERAL_CONFIG_SECTION,
                dxlmispservice.MispService._GENERAL_API_PORT_CONFIG_PROP,
                self._TEST_API_PORT
            )
            config.set(
                dxlmispservice.MispService._GENERAL_CONFIG_SECTION,
                dxlmispservice.MispService._GENERAL_API_KEY_CONFIG_PROP,
                self._TEST_API_KEY
            )
            config.set(
                dxlmispservice.MispService._GENERAL_CONFIG_SECTION,
                dxlmispservice.MispService._GENERAL_ZEROMQ_PORT_CONFIG_PROP,
                str(zmq_port)
            )
            config.write(temp_config_file)
            temp_config_file.flush()
            app._app_config_path = temp_config_file.name
            req_mock.get(self.get_api_endpoint("servers/getPyMISPVersion.json"),
                         text='{"version":"1.2.3"}')
            types_result = {"result":
                            {"categories": [
                                "Internal reference",
                                "Other"
                                ],
                             "sane_defaults":
                                 {"comment": {
                                     "default_category": "Other",
                                     "to_ids": 0
                                 }},
                             "types": ["comment"],
                             "category_type_mappings": {
                                 "Internal reference": ["comment"],
                                 "Other": ["comment"]
                             }}}
            req_mock.get(self.get_api_endpoint("attributes/describeTypes.json"),
                         text=json.dumps(types_result))
            if add_request_mocks_fn:
                add_request_mocks_fn(req_mock, zmq_socket)
            app.run()
            with open(sample_file) as f, \
                    patch.object(builtins, 'print') as mock_print:
                exec(f.read(), sample_globals) # pylint: disable=exec-used
        return (mock_print, req_mock)

    def test_basic_new_event_example(self):
        event_id = "123456"
        def add_request_mocks(req_mock, _):
            req_mock.post(self.get_api_endpoint("events"),
                          text='{"Event": {"id": "' + event_id + '"}}')
            req_mock.post(self.get_api_endpoint("events/restSearch/download"),
                          text='{"response": "searchEvent"}')
        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_new_event_example.py",
            add_request_mocks
        )

        request_count = len(req_mock.request_history)
        self.assertGreater(request_count, 1)

        new_event_request = req_mock.request_history[request_count-2]
        self.assertEqual({
            "Event": {
                "distribution": "3",
                "info": "OpenDXL MISP new event example",
                "analysis": "1",
                "published": False,
                "threat_level_id": "3"
            }}, new_event_request.json())

        search_request = req_mock.request_history[request_count-1]
        self.assertEqual(self._TEST_API_KEY,
                         search_request.headers["Authorization"])
        self.assertEqual({"eventid": event_id}, search_request.json())

        mock_print.assert_any_call(
            StringMatches(
                "Response to the new event request:.*Event.*id.*" + event_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response to the search request for the new MISP event:.*response.*searchEvent"
            ))
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

    def test_basic_update_event_example(self):
        event_id = "123456"
        attribute_uuid = "79e88e45-09eb-4f9b-ba46-c2c850b5eb03"
        def add_request_mocks(req_mock, _):
            req_mock.post(self.get_api_endpoint("events"),
                          text='{"Event": {"id": "' + event_id + '"}}')
            req_mock.post(self.get_api_endpoint("attributes/add/" + event_id),
                          text='{"Attribute": {"uuid": "' +
                          attribute_uuid + '"}}')
            req_mock.post(self.get_api_endpoint("tags/attachTagToObject"),
                          text='{"response": "tag"}')
            req_mock.post(self.get_api_endpoint("sightings/add/"),
                          text='{"response": "sighting"}')
            req_mock.post(self.get_api_endpoint("events/restSearch/download"),
                          text='{"response": "searchEvent"}')

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_update_event_example.py",
            add_request_mocks
        )
        request_count = len(req_mock.request_history)
        self.assertGreater(request_count, 4)

        attribute_request = req_mock.request_history[request_count-4]
        self.assertEqual([{
            "category": "Internal reference",
            "value": "Added by the OpenDXL MISP update event example",
            "comment": "This is only a test",
            "type": "comment",
            "to_ids": False,
            "disable_correlation": False
            }], attribute_request.json())

        tag_request = req_mock.request_history[request_count-3]
        self.assertEqual({
            "uuid": attribute_uuid,
            "tag": "Tagged by the OpenDXL MISP update event example"
        }, tag_request.json())

        sighting_request = req_mock.request_history[request_count-2]
        self.assertEqual({
            "source": "Seen by the OpenDXL MISP update event example",
            "type": "0",
            "uuid": attribute_uuid
            }, sighting_request.json())

        search_request = req_mock.request_history[request_count-1]
        self.assertEqual(self._TEST_API_KEY,
                         search_request.headers["Authorization"])
        self.assertEqual({"eventid": event_id}, search_request.json())

        mock_print.assert_any_call(
            StringMatches(
                "Response to the new event request:.*Event.*id.*" + event_id
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response to the add internal comment request:.*Attribute.*uuid.*" +
                attribute_uuid
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response to the tag request:.*response.*tag"
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response to the sighting request:.*response.*sighting"
            ))
        mock_print.assert_any_call(
            StringMatches(
                "Response to the search request for the new MISP event:.*response.*searchEvent"
            ))
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

    def test_basic_event_notification_example(self):
        event_id = "123456"
        def new_event_callback_fn(zmq_socket):
            def new_event_callback(request, context):
                context.status_code = 200
                zmq_socket.send_string(
                    'misp_json_event ' +
                    '{"Event": {"info": "' + request.json()["Event"]["info"] + \
                    '", "id": "' + event_id + '"}}')
                return '{"Event": {"id": "' + event_id + '"}}'
            return new_event_callback
        def add_request_mocks(req_mock, zmq_socket):
            req_mock.post(self.get_api_endpoint("events"),
                          text=new_event_callback_fn(zmq_socket))
        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_event_notification_example.py",
            add_request_mocks
        )
        request_count = len(req_mock.request_history)
        self.assertGreater(request_count, 1)

        mock_print.assert_any_call(
            StringMatches(
                "Received event:.*Event.*id.*" + event_id +
                ".*info.*OpenDXL MISP event notification example"
            ))
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))
