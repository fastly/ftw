===============
The YAML Format
===============

Welcome to the the FTW YAMLFormat documentation. In this document we will explain all the possible options that can be used within the YAML format. Generally this is the preferred format for writing tests in as they don't require any programming skills in order to understand and change. If you find a bug in this format please open an issue.

Metadata Parameters
==================
Metadata parameters are present once per test file and are located by convention right after the start of the file. In general, this data should give a general overview of the following tests and what they apply to. An example usage is as follows:

```
---
  meta: 
    author: "csanders-git"
    enabled: true
    name: "Tests for 920350"
    description: "This file contains tests for the ModSecurity CRS v3 rule with the ID 920350"
  ...
```  
What follows are all the possible Metadata parameters that are current suported

Author
------
**Description**: Lists the author(s).

**Syntax:** ```author: "<string>"```

**Example Usage:** ```author: "csanders-git"```

**Default Value:** ""

**Scope:** Metadata

**Version:** 0.1

Description
-----------
**Description**: A breif description of what the following tests are meant to accomplish

**Syntax:** ```description: "<string>"```

**Example Usage:** ```description: "The following is a description"```

**Default Value:** ""

**Scope:** Metadata

**Version:** 0.1

Enabled
-----------
**Description**: Determines if the tests in the file will be run 

**Syntax:** ```enabled: (true|false)```

**Example Usage:** ```enabled: false```

**Default Value:** true

**Scope:** Metadata

**Version:** 0.1

Name
-----------
**Description**: A name for the test file

**Syntax:** ```enabled: (true|false)```

**Example Usage:** ```enabled: false```

**Default Value:** ""

**Scope:** Metadata

**Version:** 0.1

*note: The filename not the name specified in this parameter is used during test execution. 

Tests Parameters
==================
The tests area is made up of multiple tests. Each test contains Stages and an optional rule_id. Within the Stage there is additional information that is outlined in Stage Paramaters

Rule_id
-----------
**Description**: Information about the test being performed, this will be included as the test name when run.

**Syntax:** ```rule_id: <integer>```

**Example Usage:** ```rule_id: 1234```

**Default Value:** TODO

**Scope:** Tests

**Version:** 0.1

Stages
-----------
**Description**: A parameter to encapsalate all the different stages of a give test

**Syntax:** ```stages: n*<individual stages>```

**Example Usage:** ```stages:```

**Default Value:** TODO

**Scope:** Tests

**Version:** 0.1


Stage Parameters
==================
There can be multiple stages per test. Each stage represents a single request/response. Each stage paramater encapsalates an input and output parameters.

Input
-----------
**Description**: A container for the parameters that will be used to construct an HTTP request

**Syntax:** ```input: <input information>```

**Example Usage:** 
```
stage: 
  input:
    dest_addr: "localhost"
    port: 80
```

**Default Value:** No Default, Required with each Stage (TODO)

**Scope:** Stage

**Version:** 0.1

Output
-----------
**Description**: A container for parameters that will describe what do after the HTTP request is sent.

**Syntax:** ```output: <output information>```

**Example Usage:** 
```
stage: 
  output: 
    status: 403
```
**Default Value:** ""

**Scope:** Stage

**Version:** 0.1

Input Parameters
==================
Items within input represent parameters that affect the construction and processing of the resulting HTTP packet.

dest_addr
-----------
**Description**: What address the packet should be sent to at the IP level

**Syntax:** ```input: <IP or DNS name>```

**Example Usage:** ```dest_addr: "129.21.3.17"```

**Default Value:** "127.0.0.1"

**Scope:** Input

**Version:** 0.1

port
-----------
**Description**: What port the packet should be sent to at the IP level

**Syntax:** ```input: <Integer>```

**Example Usage:** ```dest_addr: 8080```

**Default Value:** 80

**Scope:** Input

**Version:** 0.1

method
------
**Description**: What HTTP method should be used within the HTTP portion of the packet

**Syntax:** ```input: <string>```

**Example Usage:** ```dest_addr: "GET"```

**Default Value:** "GET"

**Scope:** Input

**Version:** 0.1

headers
-----------
**Description**: A collection that will be used to fill the header portion of the HTTP request

**Syntax:** 
```
headers: 
  header1_name: "HeaderValue"
  header2_name: "HeaderValue"
  headerN_name: "HeaderValue"
```

**Example Usage:** 
```
headers:
    User-Agent: "ModSecurity CRS 3 Tests"              
    Host: "localhost"
```

**Default Value:** ""

**Scope:** Input

**Version:** 0.1

*Note: in the future if stop_magic is enabled this will prevent automatic header values TODO*
*Note: If a Content-Type is passed and a charset attribute is set, FTW will try to encode the data with that codec. It must be a valid Python codec and the default is UTF-8.*

protocol
-----------
**Description**: Specifies if the request should be using SSL/TLS or not

**Syntax:** ```protocol: (http|https)

**Example Usage:** ```protocol: http```

**Default Value:** "http"

**Scope:** Input

**Version:** 0.1

Uri
-----------
**Description**: The URI value that should be placed into the request-line of the HTTP request

**Syntax:** ```uri: <string>```

**Example Usage:** ```uri: /test.php?param=value```

**Default Value:** "/"

**Scope:** Input

**Version:** 0.1

Version
-----------
**Description**: The version value that will be provided in the request-line of the HTTP request

**Syntax:** ```version: "<string>"```

**Example Usage:** ```version: "HTTP/0.9"```

**Default Value:** "HTTP/1.1"

**Scope:** Input

**Version:** 0.1

Data
-----------
**Description**: The optional data porition of the HTTP request. Typically these are provided with the content-type header. Data can be provided as a string or as a YAML list.

**Syntax:** ```data: "<string|YAML list>"```

**Example Usage (string):** ```data: "xyz=123"``

**Example Usage (list):**
```
  data:
    - "----------397236876"
    - "Content-Disposition: form-data; name=\"text\";"
    - ""
    - "test default"
    - "----------397236876"
    - "Content-Disposition: form-data; name=\"file1\"; filename=\"a.txt\""
    - "Content-Type: text/plain"
    - ""
    - "Content of a.txt."
    - ""
    - "----------397236876--"
```

**Default Value:** "HTTP/1.1"

**Scope:** Input

**Version:** 0.1

*Note: literals \r and \n will be replaced be replaced with CRLF when stop_magic is on.*
*Note: if urlencoded content-type header is provided and parameters aren't in name=value form, data will be made empty, unless stop_magic is on.*


Save_cookie
-----------
**Description**: If there are multiple stages and save cookie is set, it will automaticlly be provided in the next stage if the site in question provides the Set-Cookie response header.

**Syntax:** ```save_cookie: (true|false)```

**Example Usage:** ```save_cookie: true```

**Default Value:** false

**Scope:** Input

**Version:** 0.1

Stop_magic
-----------
**Description**: The framework will take care of certain things automaticlly like setting content-length, encoding, etc. When stop_magic is on, the framework will not do anything automagically. 

**Syntax:** ```stop_magic: (true|false)```

**Example Usage:** ```stop_magic: true```

**Default Value:** false

**Scope:** Input

**Version:** 0.1

Encoded_request
-----------
**Description**: This argument will take a base64 encoded string that will be decoded and sent through as the request. It will override all other settings  

**Syntax:** ```encoded_request: <Base64 string>```

**Example Usage:** ```encoded_request: "R0VUIFwgSFRUUFwxLjFcclxuClxyXG4="```

**Default Value:** None

**Scope:** Input

**Version:** 0.1

*Note: literals \r and \n will be replaced be replaced with CRLF when stop_magic is on. (TODO)*

Raw_request
-----------
**Description**: This argument will take a unencoded string that will be sent through as the request. It will override all other settings  

**Syntax:** ```raw_request: <string>```

**Example Usage:** ```raw_request: "GET \ HTTP\r\n\r\n"```

**Default Value:** None

**Scope:** Input

**Version:** 0.1

*Note: literals \r and \n will be replaced be replaced with CRLF when stop_magic is on. (TODO)*
Output Parameters
==================
Items within the output represent actions that should be taken as a result of the HTTP request being made.

Status
-----------
**Description**: Checks the response code of the response to see if it matches the provided value

**Syntax:** ```status: <integer>```

**Example Usage:** ```status: 200```

**Default Value:** None

**Scope:** Output

**Version:** 0.1

html_contains
-----------
**Description**: Checks the entire response against the regular expression provided.

**Syntax:** ```html_contains: "<regex string>"```

**Example Usage:** ```html_contains: "hello-[a-z]orld"```

**Default Value:** None

**Scope:** Output

**Version:** 0.1

log_contains
-----------
**Description**: Will use the provided LogChecker (must be supplied) and run the provided regex against each one of the logs provided by LogChecker.get_logs() looking for a match. If it doesn't find a match it will raise an assertion

**Syntax:** ```log_contains: "<regex string>"```

**Example Usage:** ```log_contains: "id:1234"```

**Default Value:** None

**Scope:** Output

**Version:** 0.1

no_log_contains
-----------
**Description**: Will use the provided LogChecker (must be supplied) and run the provided regex against each one of the logs provided by LogChecker.get_logs() looking for a match. However, if it finds a match it will raise an assertion.

**Syntax:** ```no_log_contains: "<regex string>"```

**Example Usage:** ```no_log_contains: "id:1234"```

**Default Value:** None

**Scope:** Output

**Version:** 0.1


