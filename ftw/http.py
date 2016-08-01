#!/usr/bin/env python
from __future__ import print_function
import socket
import ssl
import string
import errno
import time
import StringIO
import gzip
import os
import sys
import re
import base64
import zlib
import Cookie
import encodings
from IPy import IP
import errors

reload(sys)
sys.setdefaultencoding('utf8')

class HttpResponse(object):
    def __init__(self, http_response, user_agent):
        self.response = http_response
        # For testing purposes HTTPResponse might be called OOL
        try:
            self.dest_addr = user_agent.request_object.dest_addr
        except AttributeError:
            self.dest_addr = '127.0.0.1'
        self.response_line = None
        self.status = None
        self.cookiejar = user_agent.cookiejar
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
            zipbuf = gzip.GzipFile(fileobj=buf)
            response_data = zipbuf.read()
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

    def check_for_cookie(self, cookie):
        # http://bayou.io/draft/cookie.domain.html
        # Check if our originDomain is an IP
        origin_is_ip = True
        try:
            IP(self.dest_addr)
        except ValueError:
            origin_is_ip = False
        for cookie_morsals in cookie.values():
            # If the coverdomain is blank or the domain is an IP set the domain to be the origin
            if cookie_morsals['domain'] == '' or origin_is_ip:
                # We want to always add a domain so it's easy to parse later
                return (cookie, self.dest_addr)
            # If the coverdomain is set it can be any subdomain
            else:
                cover_domain = cookie_morsals['domain']
                # strip leading dots
                # Find all leading dots not just first one
                # http://tools.ietf.org/html/rfc6265#section-4.1.2.3
                first_non_dot = 0
                for i in range(len(cover_domain)):
                    if cover_domain[i] != '.':
                        first_non_dot = i
                        break
                cover_domain = cover_domain[first_non_dot:]
                # We must parse the coverDomain to make sure its not in the suffix list
                psl_path = os.path.dirname(__file__) + os.path.sep + \
                'util' + os.path.sep + 'public_suffix_list.dat'
                # Check if the public suffix list is present in the ftw dir
                if os.path.exists(psl_path):
                    pass
                else:
                    raise errors.TestError(
                        'unable to find the needed public suffix list',
                        {
                            'Search_Dir': os.path.dirname(__file__),
                            'function': 'http.HttpResponse.check_for_cookie'
                        })
                try:
                    with open(psl_path, 'r') as public_suffixs:
                        for line in public_suffixs:
                            if line[:2] == '//' or line[0] == ' ' or line[0].strip() == '':
                                continue
                            if cover_domain == line.strip():
                                return False
                except IOError:
                    raise errors.TestError(
                        'unable to open the needed publix suffix list',
                        {
                            'path': psl_path,
                            'function': 'http.HttpResponse.check_for_cookie'
                        })
                # Generate Origin Domain TLD
                i = self.dest_addr.rfind('.')
                o_tld = self.dest_addr[i+1:]
                # if our cover domain is the origin TLD we ignore
                # Quick sanity check
                if cover_domain == o_tld:
                    return False
                # check if our coverdomain is a subset of our origin domain
                # Domain match (case insensative)
                if cover_domain == self.dest_addr:
                    return (cookie, self.dest_addr)
                # Domain match algorithm (rfc2965)
                bvalue = cover_domain.lower()
                hdn = self.dest_addr.lower()
                nend = hdn.find(bvalue)
                if nend is not False:
                    nvalue = hdn[0:nend]
                    # Modern browsers don't care about dot
                    if nvalue[-1] == '.':
                        nvalue = nvalue[0:-1]
                else:
                    # We don't have an address of the form
                    return False
                if nvalue == '':
                    return False
                return (cookie, self.dest_addr)

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
        if 'set-cookie' in response_headers.keys():
            try:
                cookie = Cookie.SimpleCookie()
                cookie.load(response_headers['set-cookie'])
            except Cookie.CookieError as err:
                raise errors.TestError(
                    'Error processing the cookie content into a SimpleCookie',
                    {
                        'msg': str(err),
                        'set_cookie': str(response_headers['set-cookie']),
                        'function': 'http.HttpResponse.process_response'
                    })
            # if the check_for_cookie is invalid then we don't save it
            if self.check_for_cookie(cookie) is False:
                raise errors.TestError(
                    'An invalid cookie was specified',
                    {
                        'set_cookie': str(response_headers['set-cookie']),
                        'function': 'http.HttpResponse.process_response'
                    })
            else:
                self.cookiejar.append((cookie, self.dest_addr))
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
                    'msg': 'This may be an HTTP 1.0 \'Simple Req\\Res\', it \
                    doesn\'t have HTTP headers and FTW will not parse these',
                    'response_line': str(response_line),
                    'function': 'http.HttpResponse.process_response'
                })
        self.status_msg = response_line.split(' ', 2)[2]
        self.version = response_line.split(' ', 2)[0]
        self.response_line = response_line
        self.headers = response_headers
        self.data = response_data

class HttpUA(object):
    """
    Act as the User Agent for our regression testing
    """
    def __init__(self):
        """
        Initalize an HTTP object
        """
        self.request_object = None
        self.response_object = None
        self.request = None
        self.cookiejar = []
        self.sock = None
        self.CIPHERS = \
            'ADH-AES256-SHA:ECDHE-ECDSA-AES128-GCM-SHA256:' \
            'ECDHE-RSA-AES128-GCM-SHA256:AES128-GCM-SHA256:AES128-SHA256:HIGH:'
        self.CRLF = '\r\n'
        self.HTTP_TIMEOUT = .3
        self.RECEIVE_BYTES = 8192
        self.SOCKET_TIMEOUT = 5

    def send_request(self, http_request):
        """
        Send a request and get response
        """
        self.request_object = http_request
        self.build_socket()
        self.build_request()
        try:
            self.sock.send(self.request)
        except socket.error as err:
            raise errors.TestError(
                'We were unable to send the request to the socket',
                {
                    'msg': err,
                    'function': 'http.HttpUA.send_request'
                })  			
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
            # Check if TLS
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

    def find_cookie(self):
        """
        Find a list of all cookies for a given domain
        """
        return_cookies = []
        origin_domain = self.request_object.dest_addr
        for cookie in self.cookiejar:
            for cookie_morsals in cookie[0].values():
                cover_domain = cookie_morsals['domain']
                if cover_domain == '':
                    if origin_domain == cookie[1]:
                        return_cookies.append(cookie[0])
                else:
                    # Domain match algorithm
                    bvalue = cover_domain.lower()
                    hdn = origin_domain.lower()
                    nend = hdn.find(bvalue)
                    if nend is not False:
                        return_cookies.append(cookie[0])
        return return_cookies

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
        available_cookies = self.find_cookie()
        # If the user has requested a tracked cookie and we have one set it
        if available_cookies:
            cookie_value = ''
            if 'cookie' in self.request_object.headers.keys():
                # Create a SimpleCookie out of our provided cookie
                try:
                    provided_cookie = Cookie.SimpleCookie()
                    provided_cookie.load(self.request_object.headers['cookie'])
                except Cookie.CookieError as err:
                    raise errors.TestError(
                        'Error processing the existing cookie into a SimpleCookie',
                        {
                            'msg': str(err),
                            'set_cookie': str(self.request_object.headers['cookie']),
                            'function': 'http.HttpResponse.build_request'
                        })
                result_cookie = {}
                for cookie_key, cookie_morsal in provided_cookie.iteritems():
                    result_cookie[cookie_key] = provided_cookie[cookie_key].value
                for cookie in available_cookies:
                    for cookie_key, cookie_morsal in cookie.iteritems():
                        if cookie_key in result_cookie.keys():
                            # we don't overwrite a user specified cookie with a saved one
                            pass
                        else:
                            result_cookie[cookie_key] = cookie[cookie_key].value
                for key, value in result_cookie.iteritems():
                    cookie_value += (unicode(key) + '=' + unicode(value) + '; ')
                    # Remove the trailing semicolon
                cookie_value = cookie_value[:-2]
                self.request_object.headers['cookie'] = cookie_value
            else:
                for cookie in available_cookies:
                    for cookie_key, cookie_morsal in cookie.iteritems():
                        cookie_value += (unicode(cookie_key) + '=' + unicode(cookie_morsal.coded_value) + '; ')
                        # Remove the trailing semicolon
                    cookie_value = cookie_value[:-2]
                    self.request_object.headers['cookie'] = cookie_value

        # Expand out our headers into a string
        headers = ''
        if self.request_object.headers != {}:
            for hname, hvalue in self.request_object.headers.iteritems():
                headers += unicode(hname) + ': ' + unicode(hvalue) + self.CRLF
        request = string.replace(request, '#headers#', headers)

        # If we have data append it
        if self.request_object.data != '':
            # Before we do that see if that is a charset
            encoding = "utf-8"
            # Check to see if we have a content type and magic is off (otherwise UTF-8)
            if 'Content-Type' in self.request_object.headers.keys() and self.request_object.stop_magic is False:
                pattern = re.compile(r'\;\s{0,1}?charset\=(.*?)(?:$|\;|\s)')
                m = re.search(pattern, self.request_object.headers['Content-Type'])
                if m:
                    possible_choices = list(set(encodings.aliases.aliases.keys())) + list(set(encodings.aliases.aliases.values()))
                    choice = m.group(1)
                    # Python will allow these aliases but doesn't list them
                    choice = choice.replace('-','_')
                    choice = choice.lower()
                    if choice in possible_choices:
                        encoding = choice
            try:
                data = self.request_object.data.encode(encoding)
            except UnicodeEncodeError as err:
                raise errors.TestError(
                    'Error encoding the data with the charset specified',
                    {
                        'msg': str(err),
                        'Content-Type': str(self.request_object.headers['Content-Type']),
                        'data': unicode(self.request_object.data),
                        'function': 'http.HttpResponse.build_request'
                    })                
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
            # We do this regardless of magic if you want to send a literal 
            # '\' 'r' or 'n' use encoded request.
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
                elif sys.platform == 'win32' and \
                err.errno == errno.WSAEWOULDBLOCK:
                        pass
                elif (self.request_object.protocol == 'https' and
                    err[0] == ssl.SSL_ERROR_WANT_READ):
                        continue
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
        if ''.join(our_data) == '':
            raise errors.TestError(
                'No response from server. Request likely timed out.',
                {
                    'host': self.request_object.dest_addr,
                    'port': self.request_object.port,
                    'proto': self.request_object.protocol,
                    'msg': 'Please send the request and check Wireshark',
                    'function': 'http.HttpUA.get_response'
                })                                    
        self.response_object = HttpResponse(''.join(our_data), self)
        try:
            self.sock.shutdown(1)
            self.sock.close()
        except socket.error as err:
            raise errors.TestError(
                'We were unable to close the socket as expected.',
                {
                    'msg': err,
                    'function': 'http.HttpUA.get_response'
                })  
