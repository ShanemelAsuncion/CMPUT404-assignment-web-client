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

"""
TODO: 
[0] Implement basic HTTP GET
[0] Implement basic HTTP POST
[0] The httpclient can pass all the tests in freetests.py
[-] The webserver can pass all the tests in not-free-tests.py (you don’t have this one! it can change – but it will be fair to the user stories/requirements)
[ ] HTTP POST can post vars
[0] HTTP POST handles at least Content-Type: application/x-www-form-urlencoded
[0] httpclient can handle 404 requests and 200 requests
[0] Cumulatively together all tests must SUCCESSFULLY terminate within 150 seconds. Lack of termination is test failure.
"""

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, headers):
        headers = headers.split("\r\n")
        line = headers[0].split(" ")
        code = int(line[1])
        return code

    def get_headers(self,data):
        splitData = data.split("\r\n\r\n")
        headers = splitData[0]
        return headers

    def get_body(self, data):
        splitData = data.split("\r\n\r\n")
        body = splitData[1]
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
        # Connecting socket and send header
        host, port, path = self.getInfo(url)
        self.connect(host,port)
        Gheader = self.newGETH(host,port,path)
        self.sendall(Gheader)
        response = self.recvall(self.socket)        
        # Get response
        body = self.get_body(response)
        headers = self.get_headers(response)
        code = self.get_code(headers)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Connecting socket and send header
        host, port, path = self.getInfo(url)
        # body is from arguments
        if args != None:
            body = urllib.parse.urlencode(args)
        else:
            body = urllib.parse.urlencode('')
        Pheader = self.newPOSH(host,port,path,body)
        self.connect(host,port)
        self.sendall(Pheader)
        # Handle response
        response = self.recvall(self.socket)  
        body = self.get_body(response)
        headers = self.get_headers(response)
        code = self.get_code(headers)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def getInfo(self, url):
        # Get data info
        x = urllib.parse.urlparse(url)
        host = x.hostname
        port = x.port
        path = x.path

        # Error checking
        if path == "":
            path = "/"  # default
        if port == None:
            port = 80   # default

        return (host,port,path)

    def newGETH(self,host,port,path):
        header = f'GET {path} HTTP/1.1\r\nHost: {host}:{str(port)}\r\nConnection: close\r\n\r\n'
        return header

    def newPOSH(self,host,port,path,body):
        header = f'POST {path} HTTP/1.1\r\nHost: {host}:{port}\r\nContent-type: application/x-www-form-urlencoded\r\nContent-Length: {str(len(body))}\r\n\r\n{body}'
        return header

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
