===============
The YAML Format
===============

Welcome to the the FTW YAMLFormat docuemntation. In this document we will explain all the possible options that can be used within the YAML format. Generally this is the prefereed format for writing tests in as they don't require any programming skills in order to understand and change. If you find a bug in this format please open an issue.

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
**Description**: Information about the test being performed, this will be included as the test name when run.

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
**Description**: Information about the test being performed, this will be included as the test name when run.

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


Our YAML files support quite a few parameters that may seem slightly odd at first, if you expected it to simply act as a lone request. 

Each file can contain multiple seperators at the top level. These are meant to be used as metadata to delimiate where certain test types begin and end, they are not used by our tool.

The next level should specify that it is a 'test'. Tests can contain multiple requests and checks so we use these to indicate when one test is over and the next begins. 

Each 'test' can have a single 'meta' section which indicates information about the test.

Each test can also have as many 'input' and 'output' sections as it needs to complete its task. The 'input' section should roughly equate to an HTTP request. The output section determines what should be checked after that request is made. Each input <i>Requires</i> an out, even if it's just an empty output.

What can the inputs support:
    Inputs can construct an HTTP request by parts or supply a RAW http request
    They also have support for keeping track of cookies during a given test.
    In general you may supply socket information such as 
    addrDest - DNS/IP information for the remote server (default: localhost)
    Protocol - HTTP or HTTPS are supported
    port - the destination port the webserver runs on

What can the outputs support:
