#!/usr/bin/env python
import socket
import ssl
import string
import errno
import time
import StringIO
import gzip
import sys

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

    def send_request(self):
        """
        Send a request and get response
        """    
        self.sock = None
        self.build_socket()
        self.request = None
        self.build_request()
        try:
            self.sock.send(self.request)
        except socket.error as exc:
            print exc
        self.response = None
        self.get_response()
        self.response_line = None
        self.response_headers = None
        self.response_data = None
        self.process_response()
        return (self.response_line, self.response_headers, self.response_data)

    def build_socket(self):
        """
        Generate either an HTTPS or HTTP socket
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Check if SSL
            if self.request_object.protocol == "https":
                ciphers = "ADH-AES256-SHA:ECDHE-ECDSA-AES128-GCM-SHA256: \
                ECDHE-RSA-AES128-GCM-SHA256:AES128-GCM-SHA256:AES128-SHA256:HIGH:"
                self.sock = ssl.wrap_socket(self.sock, ciphers=ciphers)
            self.sock.connect((self.request_object.dest_addr, self.request_object.port))
        except socket.error as msg:
            print "Error", msg
        

    def build_request(self):
        crlf = "\r\n"
        request = '#method# #url##version#%s#headers#%s#data#' % (crlf, crlf)
        request = string.replace(request, "#method#", self.request_object.method)
        # We add a space after here to account for HEAD requests with no url
        request = string.replace(request, "#url#", self.request_object.uri+" ")
        request = string.replace(request, "#version#", self.request_object.version)

        # Expand out our headers into a string
        headers = ""
        if self.request_object.headers != {}:
            for hname, hvalue in self.request_object.headers.iteritems():
                headers += str(hname)+": "+str(hvalue) + str(crlf)
        request = string.replace(request, "#headers#", headers)

        # If we have data append it
        if self.request_object.data != "":
            data = str(self.request_object.data) + str(crlf)
            request = string.replace(request, "#data#", data)
        else:
            request = string.replace(request, "#data#", "")
        self.request = request

    def get_response(self):
        """
        Get the response from the socket
        """
        # Make socket non blocking
        self.sock.setblocking(0)
        our_data = []
        data = ''
        timeout = .3
        # Beginning time
        begin = time.time()
        while True:
            # If we have data then if we're passed the timeout break
            if our_data and time.time()-begin > timeout:
                break
            # If we're dataless wait just a bit
            elif time.time()-begin > timeout*2:
                break
            # Recv data
            try:
                data = self.sock.recv(8192)
                if data:
                    our_data.append(data)
                    begin = time.time()
                else:
                    # Sleep for sometime to indicate a gap
                    time.sleep(0.2)
            except socket.error as err:
                # Check if we got a timeout
                if err.errno == errno.EAGAIN:
                    pass
                # If we didn't it's an error
                else:
                    print err
        self.response = ''.join(our_data)
        try:
            self.sock.shutdown(1)
            self.sock.close()
        except socket.error as err:
            pass
  
    def process_response(self):
        crlf = "\r\n"
        split_response = self.response.split('\r\n')
        response_line = split_response[0]
        repsonse_headers = {}
        response_data = None
        data_line = None
        for line_num in range(1,len(split_response[1:])):
            # CRLF represents the start of data
            if split_response[line_num] == '':
                data_line = line_num + 1
                break
            else:
                # Headers are all split by ':'
                header = split_response[line_num].split(":",1)
                if(len(header) != 2):
                    print "ERROR"
                    sys.exit()
                repsonse_headers[header[0]] = header[1].lstrip()
        
        if data_line != None and data_line < len(split_response):
            response_data = "\r\n".join(split_response[data_line:])

        # if the output headers say there is encoding
        if('Content-Encoding' in repsonse_headers.keys()):
            # If it is gzip then ungzip it
            if(repsonse_headers["Content-Encoding"] == "gzip"):
                buf = StringIO.StringIO(self.response)
                f = gzip.GzipFile(fileobj=buf)
                response_data = f.read()
            # if it is deflate then decompress it
            elif(repsonse_headers["Content-Encoding"] == "deflate"):
                data = StringIO.StringIO(zlib.decompress(self.response))
                response_data = data.read()
        self.response_line = response_line
        self.response_headers = repsonse_headers
        self.response_data = response_data
