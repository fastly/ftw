#!/usr/bin/env python
import socket
import ssl
import string
import errno
import time
import StringIO
import gzip
import errors
import sys
import re
import base64


class HttpResponse(object):
    def __init__(self, http_response):
        self.response = http_response
        self.response_line = None
        self.status = None
        self.status_msg = None
        self.version = None
        self.headers = None
        self.data = None
        self.CRLF = '\r\n'
        self.process_response()

    def parse_content_encoding(self, response_headers, response_data):
        """
        Parses a response that contains Content-Encoding to retrieve
        response_data
        """
        if response_headers['content-encoding'] == 'gzip':
            buf = StringIO.StringIO(response_data)
            f = gzip.GzipFile(fileobj=buf)
            response_data = f.read()
        elif response_headers['content-encoding'] == 'deflate':
            data = StringIO.StringIO(zlib.decompress(response_data))
            response_data = data.read()
        else:
            raise errors.TestError(
                'Received unknown Content-Encoding',
                {
                    'content-encoding':
                        str(response_headers['content-encoding']),
                    'function': 'http.HttpResponse.parse_content_encoding'
                })
        return response_data

    def process_response(self):
        """
        Parses an HTTP response after an HTTP request is sent
        """
        split_response = self.response.split(self.CRLF)
        response_line = split_response[0]
        response_headers = {}
        response_data = None
        data_line = None
        for line_num in range(1, len(split_response[1:])):
            # CRLF represents the start of data
            if split_response[line_num] == '':
                data_line = line_num + 1
                break
            else:
                # Headers are all split by ':'
                header = split_response[line_num].split(':', 1)
                if len(header) != 2:
                    raise errors.TestError(
                        'Did not receive a response with valid headers',
                        {
                            'header_rcvd': str(header),
                            'function': 'http.HttpResponse.process_response'
                        })
                response_headers[header[0].lower()] = header[1].lstrip()

        if data_line is not None and data_line < len(split_response):
            response_data = self.CRLF.join(split_response[data_line:])

        # if the output headers say there is encoding
        if 'content-encoding' in response_headers.keys():
            response_data = self.parse_content_encoding(
                response_headers, response_data)
        if len(response_line.split(' ', 2)) != 3:
            raise errors.TestError(
                'The HTTP response line returned the wrong args',
                {
                    'response_line': str(response_line),
                    'function': 'http.HttpResponse.process_response'
                })
        try:
            self.status = int(response_line.split(' ', 2)[1])
        except ValueError:
            raise errors.TestError(
                'The status num of the response line isn\'t convertable',
                {
                    'response_line': str(response_line),
                    'function': 'http.HttpResponse.process_response'
                })
        self.status_msg = response_line.split(' ', 2)[2]
        self.version = response_line.split(' ', 2)[0]
        self.response_line = response_line
        self.headers = response_headers
        self.data = response_data


"""This script will handle all the HTTP requests and responses"""


class HttpUA(object):
    """
    Act as the User Agent for our regression testing
    """
    def __init__(self, http_request):
        """
        Initalize an HTTP object
        """
        self.request_object = http_request
        self.response_object = None
        self.request = None
        self.sock = None
        self.CIPHERS = \
            'ADH-AES256-SHA:ECDHE-ECDSA-AES128-GCM-SHA256:' \
            'ECDHE-RSA-AES128-GCM-SHA256:AES128-GCM-SHA256:AES128-SHA256:HIGH:'
        self.CRLF = '\r\n'
        self.HTTP_TIMEOUT = .3
        self.RECEIVE_BYTES = 8192
        self.SOCKET_TIMEOUT = 5

    def send_request(self):
        """
        Send a request and get response
        """
        self.build_socket()
        self.build_request()
        try:
            self.sock.send(self.request)
        except socket.error as exc:
            print exc
        finally:
            self.get_response()

    def build_socket(self):
        """
        Generate either an HTTPS or HTTP socket
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.SOCKET_TIMEOUT)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # self.sock.setblocking(0)
            # Check if SSL
            if self.request_object.protocol == 'https':
                self.sock = ssl.wrap_socket(self.sock, ciphers=self.CIPHERS)
            self.sock.connect(
                (self.request_object.dest_addr, self.request_object.port))
        except socket.error as msg:
            raise errors.TestError(
                'Failed to connect to server',
                {
                    'host': self.request_object.dest_addr,
                    'port': self.request_object.port,
                    'proto': self.request_object.protocol,
                    'message': msg,
                    'function': 'http.HttpUA.build_socket'
                })

    def build_request(self):
        request = '#method# #uri##version#%s#headers#%s#data#' % \
                  (self.CRLF, self.CRLF)
        request = string.replace(
            request, '#method#', self.request_object.method)
        # We add a space after here to account for HEAD requests with no url
        request = string.replace(
            request, '#uri#', self.request_object.uri + ' ')
        request = string.replace(
            request, '#version#', self.request_object.version)

        # Expand out our headers into a string
        headers = ''
        if self.request_object.headers != {}:
            for hname, hvalue in self.request_object.headers.iteritems():
                headers += str(hname) + ': ' + str(hvalue) + str(self.CRLF)
        request = string.replace(request, '#headers#', headers)

        # If we have data append it
        if self.request_object.data != '':
            data = str(self.request_object.data)
            request = string.replace(request, '#data#', data)
        else:
            request = string.replace(request, '#data#', '')
        # If we have a Raw Request we should use that instead
        if self.request_object.raw_request is not None:
            if self.request_object.encoded_request is not None:
                raise errors.TestError(
                    'Cannot specify both raw and encoded modes',
                    {
                        'function': 'http.HttpUA.build_request'
                    })
            request = self.request_object.raw_request
            # Check for newlines (without CR prior)
            request = re.sub(r'(?<!x)\n', self.CRLF, request)
            request = request.decode('string_escape')
        if self.request_object.encoded_request is not None:
            request = base64.b64decode(self.request_object.encoded_request)
            request = request.decode('string_escape')
        # if we have an Encoded request we should use that
        self.request = request

    def get_response(self):
        """
        Get the response from the socket
        """
        # Make socket non blocking
        self.sock.setblocking(0)
        our_data = []
        # Beginning time
        begin = time.time()
        while True:
            # If we have data then if we're passed the timeout break
            if our_data and time.time() - begin > self.HTTP_TIMEOUT:
                break
            # If we're dataless wait just a bit
            elif time.time() - begin > self.HTTP_TIMEOUT * 2:
                break
            # Recv data
            try:
                data = self.sock.recv(self.RECEIVE_BYTES)
                if data:
                    our_data.append(data)
                    begin = time.time()
                else:
                    # Sleep for sometime to indicate a gap
                    time.sleep(self.HTTP_TIMEOUT)
            except socket.error as err:
                # Check if we got a timeout
                if err.errno == errno.EAGAIN:
                    pass
                # SSL will return SSLWantRead instead of EAGAIN
                elif (self.request_object.protocol == 'https' and
                      sys.exc_info()[0].__name__ == 'SSLWantReadError'):
                    pass
                # If we didn't it's an error
                else:
                    raise errors.TestError(
                        'Failed to connect to server',
                        {
                            'host': self.request_object.dest_addr,
                            'port': self.request_object.port,
                            'proto': self.request_object.protocol,
                            'message': err,
                            'function': 'http.HttpUA.get_response'
                        })
        self.response_object = HttpResponse(''.join(our_data))
        try:
            self.sock.shutdown(1)
            self.sock.close()
        except socket.error as err:
            print err
