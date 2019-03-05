# MISP DXL Python Service
[![OpenDXL Bootstrap](https://img.shields.io/badge/Built%20With-OpenDXL%20Bootstrap-blue.svg)](https://github.com/opendxl/opendxl-bootstrap-python)
[![Latest PyPI Version](https://img.shields.io/pypi/v/dxlmispservice.svg)](https://pypi.python.org/pypi/dxlmispservice)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build Status](https://travis-ci.org/opendxl/opendxl-misp-service-python.png?branch=master)](https://travis-ci.org/opendxl/opendxl-misp-service-python)
[![Docker Build Status](https://img.shields.io/docker/cloud/build/opendxl/opendxl-misp-service-python.svg)](https://hub.docker.com/r/opendxl/opendxl-misp-service-python/)


## Overview

The MISP DXL Python Service exposes access to the
[MISP REST APIs](https://misp.gitbooks.io/misp-book/content/automation/#automation-api)
via the [Data Exchange Layer](http://www.mcafee.com/us/solutions/data-exchange-layer.aspx)
(DXL) fabric. The service also provides support for forwarding
[MISP ZeroMQ](https://misp.gitbooks.io/misp-book/content/misp-zmq/) message
notifications to the DXL fabric.

## Documentation

See the [Wiki](https://github.com/opendxl/opendxl-misp-service-python/wiki)
for an overview of the MISP DXL Python Service and usage examples.

See the
[MISP DXL Python Service documentation](https://opendxl.github.io/opendxl-misp-service-python/pydoc)
for installation instructions, API documentation, and usage examples.

## Installation

To start using the MISP DXL Python Service:

* Download the [Latest Release](https://github.com/opendxl/opendxl-misp-service-python/releases)
* Extract the release .zip file
* View the `README.html` file located at the root of the extracted files.
  * The `README` links to the documentation which includes installation
    instructions and usage examples.

## Docker Support

A pre-built Docker image can be used as an alternative to installing a Python
environment with the modules required for the MISP DXL Python Service.

See the
[Docker Support Documentation](https://opendxl.github.io/opendxl-misp-service-python/pydoc/docker.html)
for details.

## Bugs and Feedback

For bugs, questions and discussions please use the
[GitHub Issues](https://github.com/opendxl/opendxl-misp-service-python/issues).

## LICENSE

Copyright 2018 McAfee LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
