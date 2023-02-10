#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    
    def get_host_port(self,url):
        # get the host and the port from the url
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        
        # if we don't get a port, just use 80
        if port == None:
            port = 80

        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # returns the response code from the request
        # the response code needs to be concatenated to an int from str when returned
        code = (data.split(' '))[1]
        return int(code)

    def get_headers(self,data):
        # TODO
        return None

    def get_body(self, data):
        # returns the body from the request
        body = (data.split('\r\n\r\n'))[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # GET from URL
        code = 500
        body = ""
        
        # get the host and port & connect to it
        host, port = self.get_host_port(url)
        self.connect(host,port)
        # grab the path here; in the case of no path, set the path to /
        path = urllib.parse.urlparse(url).path
        if path == "":
            path = "/" 

        # construct the request
        request = "GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nAccept: */*\r\nConnection: close\r\n\r\n".format(path=path,host=host,port=port)
        self.sendall(request)

        response = self.recvall(self.socket)
        self.close() # cLoSe yOuR sOckEtS

        print(response)

        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # POST to url
        code = 500
        body = ""

        # recycling this snippet of code from the GET handler
        # get the host and port & connect to it
        host, port = self.get_host_port(url)
        self.connect(host,port)
        # grab the path here; in the case of no path, set the path to /
        path = urllib.parse.urlparse(url).path
        if path == "":
            path = "/" 

        # set the body
        if args:
            body = urllib.parse.urlencode(args)
        
        content_length = len(body.encode('utf-8'))

        # construct the incredibly long and ugly request gah dayum she is lengthy (not body shaming)
        request = "POST {path} HTTP/1.1\r\nHost: {host}:{port}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{body}".format(path=path,host=host,port=port,content_length=content_length,body=body)
        self.sendall(request)

        response = self.recvall(self.socket)
        self.close()

        print(response)
        
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
