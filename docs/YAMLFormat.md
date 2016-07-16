===============
The YAML Format
===============

Welcome to the the FTW YAMLFormat docuemntation. In this document we will explain all the possible options that can be used 


== SecDebugLog ==
'''Description''': Path to the ModSecurity debug log file. 

'''Syntax:''' <code>SecDebugLog /path/to/modsec-debug.log </code>

'''Example Usage:''' <code>SecDebugLog /usr/local/apache/logs/modsec-debug.log </code>

'''Scope:''' Any 

'''Version:''' 2.0.0


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
