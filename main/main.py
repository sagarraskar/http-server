import socket
import sys
import os
from _thread import *
from response import generateResponse
from httprequestparser import parseRequest
from config import *
from utils.accesslog import accesslog

def threaded(c, addr):
    # print("Accepting requests from ", addr)
    while(True):
        request = b''
        while True:
            partial_request = c.recv(1024)
            
            request += partial_request
            if len(partial_request) < 1024:
                break
        
        # print(request[:300])
        request = parseRequest(request)

        # for header in headers:
        #     print(header)
        # connection = True

        # if "connection" in list(request["headers"].keys()):
        #     if request["headers"]["connection"] == "close":
        #         connection = False
               
        
        res = generateResponse(addr, request)
        
        access_log = accesslog(addr, request, res)

        with open(LOG_DIRECTORY + "/" + ACCESS_LOG_FILE, "a") as file:
            file.write(access_log)
            
        response = "{} {} {}\r\n".format(res["protocol"], res["status_code"], res["status_phrase"])
        for name, value in res["headers"].items():
            response+=f"{name}: {value}\r\n"

        response+="\r\n"
        response = response.encode()
        
        if res["body"] != None:
            response += res["body"]

        c.send(response)


        # if connection:
        #     continue
        
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