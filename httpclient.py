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
import urllib.parse as parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return self.body

class HTTPClient(object):
    
    def get_host_port(self,url):
        strurl = parse.urlparse(url)
        url2 = strurl.netloc
        try: 
            alist = url2.split(':')
            host = alist[0]
            port = int(alist[1])

        except:
            host = url2
            port = 80
        
        if strurl.path == "":
            path = "/"
        else:
            path = strurl.path
        return url2, path, host, port
        

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        alist = data.split('\r\n')
        blist = alist[0].split(' ')
        return int(blist[1])

    def get_headers(self,data):
        alist = data.split('\r\n\r\n')
        return alist[0]

    def get_body(self, data):
        alist = data.split('\r\n\r\n')
        return alist[1]
    
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
        netloc,path,host,port = self.get_host_port(url)
        
        data = "GET "+ path + " HTTP/1.1\r\nHost:" + netloc + "\r\nConnection: close\r\n\r\n"
        print(data)
        self.connect(host,port)
        self.sendall(data) 
        recdata = self.recvall(self.socket)
        self.close()
        header = self.get_headers(recdata)
        body = self.get_body(recdata)
        code = self.get_code(header)
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        netloc,path,host,port = self.get_host_port(url)
        
        if args == None:
            contlen = 0
            cont = ""
        else:
            cont = parse.urlencode(args)
            contlen = len(cont)
        
        data = "POST "+ path + " HTTP/1.1\r\nHost:"+ netloc + "\r\nConnection: close\r\nContent-Length:"+ str(contlen) + "\r\n\r\n" + cont
        #print(data)
        self.connect(host,port)
        self.sendall(data) 
        recdata = self.recvall(self.socket)
        self.close()
        header = self.get_headers(recdata)
        body = self.get_body(recdata)
        code = self.get_code(header)

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
