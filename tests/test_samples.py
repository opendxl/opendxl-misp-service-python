from __future__ import absolute_import
import copy
import json
import os
import re
import sys
from tempfile import NamedTemporaryFile
import unittest
import zmq

if sys.version_info[0] > 2:
    import builtins  # pylint: disable=import-error, unused-import
    from urllib.parse import quote_plus  # pylint: disable=no-name-in-module, import-error, unused-import
else:
    import __builtin__  # pylint: disable=import-error
    builtins = __builtin__  # pylint: disable=invalid-name
    from urllib import quote_plus  # pylint: disable=no-name-in-module, ungrouped-imports

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

    @staticmethod
    def expected_print_output(title, detail):
        return_value = title + json.dumps(
            detail, sort_keys=True,
            separators=(".*", ": ")).replace("{", ".*")
        return re.sub(r"[\[}\]]", "", return_value)

    @staticmethod
    def _run_sample(app, sample_file):
        app.run()
        with open(sample_file) as f, \
                patch.object(builtins, 'print') as mock_print:
            sample_globals = {"__file__": sample_file}
            exec(f.read(), sample_globals)  # pylint: disable=exec-used
        return mock_print

    def run_sample(self, sample_file, add_request_mocks_fn=None):
        context = zmq.Context()
        with dxlmispservice.MispService("sample") as app:
            config = ConfigParser()
            config.read(app._app_config_path)

            use_mock_requests = not config.has_option(
                dxlmispservice.MispService._GENERAL_CONFIG_SECTION,
                dxlmispservice.MispService._GENERAL_API_KEY_CONFIG_PROP
            ) or not config.get(
                dxlmispservice.MispService._GENERAL_CONFIG_SECTION,
                dxlmispservice.MispService._GENERAL_API_KEY_CONFIG_PROP
            )

            if use_mock_requests:
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

                with requests_mock.mock(case_sensitive=True,
                                        real_http=True) as req_mock, \
                        context.socket(
                            zmq.PUB) as zmq_socket:  # pylint: disable=no-member
                    zmq_port = zmq_socket.bind_to_random_port("tcp://" +
                                                              self._TEST_HOSTNAME)

                    config.set(
                        dxlmispservice.MispService._GENERAL_CONFIG_SECTION,
                        dxlmispservice.MispService._GENERAL_ZEROMQ_PORT_CONFIG_PROP,
                        str(zmq_port)
                    )
                    with NamedTemporaryFile(mode="w+", delete=False) \
                        as temp_config_file:
                        config.write(temp_config_file)
                    try:
                        app._app_config_path = temp_config_file.name
                        req_mock.get(
                            self.get_api_endpoint("servers/getPyMISPVersion.json"),
                            text='{"version":"1.2.3"}')
                        types_result = {
                            "result":
                                {
                                    "categories": [
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
                                    }
                                }
                        }
                        req_mock.get(
                            self.get_api_endpoint("attributes/describeTypes.json"),
                            text=json.dumps(types_result))

                        if add_request_mocks_fn:
                            add_request_mocks_fn(req_mock, zmq_socket)
                        mock_print = self._run_sample(app, sample_file)
                    finally:
                        os.remove(temp_config_file.name)
            else:
                mock_print = self._run_sample(app, sample_file)
                req_mock = None
        return (mock_print, req_mock)

    def test_basic_new_event_example(self):
        mock_event_id = "123456"
        expected_event_detail = {
            "Event": {
                "distribution": "3",
                "info": "OpenDXL MISP new event example",
                "analysis": "1",
                "published": False,
                "threat_level_id": "3"
            }}

        def add_request_mocks(req_mock, _):
            event_detail_with_id = copy.deepcopy(expected_event_detail)
            event_detail_with_id["Event"]["id"] = mock_event_id
            req_mock.post(self.get_api_endpoint("events"),
                          text=json.dumps(event_detail_with_id))
            event_response_data = {"response": event_detail_with_id}
            req_mock.post(self.get_api_endpoint("events/restSearch/download"),
                          text=json.dumps(event_response_data))

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_new_event_example.py",
            add_request_mocks
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertGreater(request_count, 1)

            new_event_request = req_mock.request_history[request_count - 2]
            self.assertEqual(expected_event_detail, new_event_request.json())

            search_request = req_mock.request_history[request_count - 1]
            self.assertEqual(self._TEST_API_KEY,
                             search_request.headers["Authorization"])
            self.assertEqual({"eventid": mock_event_id}, search_request.json())

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response to the new event request:", expected_event_detail)
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response to the search request for the new MISP event:.*",
                    expected_event_detail
                )
            )
        )
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

    def test_basic_update_event_example(self):
        mock_event_id = "123456"
        expected_event_detail = {
            "Event": {
                "distribution": "3",
                "info": "OpenDXL MISP update event example",
                "analysis": "1",
                "published": False,
                "threat_level_id": "3"
            }}
        mock_attribute_uuid = "79e88e45-09eb-4f9b-ba46-c2c850b5eb03"
        expected_attribute_detail = {
            "category": "Internal reference",
            "value": "Added by the OpenDXL MISP update event example",
            "comment": "This is only a test",
            "type": "comment",
            "to_ids": False,
            "disable_correlation": False
        }
        expected_tag_name = "Tagged by the OpenDXL MISP update event example"
        expected_event_after_update = {
            "Event": {
                "Attribute": [
                    {
                        "Sighting": [
                            {
                                "source": "Seen by the OpenDXL MISP update event example",
                                "type": "0"
                            }
                        ],
                        "Tag": [
                            {
                                "name": "Tagged by the OpenDXL MISP update event example"
                            }
                        ]
                    }
                ]
            }
        }

        def add_request_mocks(req_mock, _):
            event_detail_with_id = copy.deepcopy(expected_event_detail)
            event_detail_with_id["Event"]["id"] = mock_event_id
            req_mock.post(self.get_api_endpoint("events"),
                          text=json.dumps(event_detail_with_id))
            expected_attribute_detail_with_id = expected_attribute_detail.copy()
            expected_attribute_detail_with_id["uuid"] = mock_attribute_uuid
            req_mock.post(
                self.get_api_endpoint("attributes/add/" + mock_event_id),
                text=json.dumps(
                    {"Attribute": expected_attribute_detail_with_id}))
            req_mock.post(self.get_api_endpoint("tags/attachTagToObject"),
                          text='{"name": "Tag ' + expected_tag_name + '"}')
            req_mock.post(self.get_api_endpoint("sightings/add/"),
                          text='{"message": "1 sighting successfuly added"}')
            req_mock.post(self.get_api_endpoint("events/restSearch/download"),
                          text=json.dumps(expected_event_after_update))

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_update_event_example.py",
            add_request_mocks
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertGreater(request_count, 4)

            attribute_request = req_mock.request_history[request_count - 4]
            self.assertEqual([expected_attribute_detail],
                             attribute_request.json())

            tag_request = req_mock.request_history[request_count - 3]
            self.assertEqual({
                "uuid": mock_attribute_uuid,
                "tag": expected_tag_name
            }, tag_request.json())

            sighting_request = req_mock.request_history[request_count - 2]
            self.assertEqual({
                "source": "Seen by the OpenDXL MISP update event example",
                "type": "0",
                "uuid": mock_attribute_uuid
            }, sighting_request.json())

            search_request = req_mock.request_history[request_count - 1]
            self.assertEqual(self._TEST_API_KEY,
                             search_request.headers["Authorization"])
            self.assertEqual({"eventid": mock_event_id}, search_request.json())

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response to the new event request:",
                    expected_event_detail)
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response to the add internal comment request:",
                    {"Attribute": expected_attribute_detail})
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                'Response to the tag request:.*name": "Tag ' + expected_tag_name
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                'Response to the sighting request:.*message": "' +
                "1 sighting successfuly added"
            )
        )
        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Response to the search request for the new MISP event:",
                    expected_event_after_update)
            )
        )

        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))

    def test_basic_event_notification_example(self):
        mock_event_id = "123456"
        expected_event_detail = {
            "Event": {
                "distribution": "3",
                "info": "OpenDXL MISP event notification example",
                "analysis": "1",
                "published": False,
                "threat_level_id": "3"
            }}

        def new_event_callback_fn(zmq_socket):
            def new_event_callback(request, context):
                context.status_code = 200
                event_detail_with_id = request.json()
                event_detail_with_id["Event"]["id"] = mock_event_id
                event_json_with_id = json.dumps(event_detail_with_id)
                zmq_socket.send_string('misp_json_event ' + event_json_with_id)
                return event_json_with_id

            return new_event_callback

        def add_request_mocks(req_mock, zmq_socket):
            req_mock.post(self.get_api_endpoint("events"),
                          text=new_event_callback_fn(zmq_socket))

        mock_print, req_mock = self.run_sample(
            "sample/basic/basic_event_notification_example.py",
            add_request_mocks
        )

        if req_mock:
            request_count = len(req_mock.request_history)
            self.assertGreater(request_count, 1)

        mock_print.assert_any_call(
            StringMatches(
                self.expected_print_output(
                    "Received event:.*",
                    expected_event_detail
                )
            )
        )
        mock_print.assert_any_call(StringDoesNotMatch("Error invoking request"))
