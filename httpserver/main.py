import socket
import sys
import os
from _thread import *
from response import generateResponse
from httprequestparser import parseRequest
from config import *
from utils.accesslog import logaccess
import error
from utils.errorlog import logerror

def threaded(c, addr):
    # print("Accepting requests from ", addr)
    while(True):
        request = b''
        while True:
            partial_request = c.recv(1024)
            
            request += partial_request
            if len(partial_request) < 1024:
                break

        try:
            request = parseRequest(request)
        except:
            data = error.getErrorPage("400", "Bad Request", "Server Could not understand the request").encode()
            content_length = len(data)
            content_type = "text/html"
            
            res = {"headers": {}, "status_code" : "400", "status_phrase": "Bad Request", "body": None, "protocol": "HTTP/1.1"}
            res["headers"]["Content-Length"] = content_length
            res["headers"]["Content-Type"] = content_type
            res["body"] = data
            logerror(addr, request, res)            
  
        try:
            res = generateResponse(addr, request)
        except:
            data = error.getErrorPage("500", "Internal Server Error", "").encode()
            content_length = len(data)
            content_type = "text/html"
            
            res = {"headers": {}, "status_code" : "500", "status_phrase": "Internal Server Error", "body": None, "protocol": "HTTP/1.1"}
            res["headers"]["Content-Length"] = content_length
            res["headers"]["Content-Type"] = content_type
            res["body"] = data
            logerror(addr, request, res)

            
        logaccess(addr, request, res)
            
        response = "{} {} {}\r\n".format(res["protocol"], res["status_code"], res["status_phrase"])
        for name, value in res["headers"].items():
            response+=f"{name}: {value}\r\n"

        response+="\r\n"
        response = response.encode()
        
        if res["body"] != None:
            response += res["body"]

        c.send(response)
        c.close()
        return

def main():
    PID = str(os.getpid())
    with open('app.pid', 'w') as file:
        file.write(PID)

    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = ("localhost", SERVER_PORT)
    listening_socket.bind(server_addr)
    listening_socket.listen(MAX_CONNECTIONS)
    # print(f'Server listening on {server_addr[0]}:{server_addr[1]}')



    while True:
        client_connection, client_addr = listening_socket.accept()
      
        start_new_thread(threaded, (client_connection, client_addr))

    listening_socket.close()

if __name__ == '__main__':
    main()