import socket
import sys
from _thread import *
from response import generateResponse
from httprequestparser import parseRequest


def threaded(c, addr):
    print("Accepting requests from ", addr)
    while(True): 
        request = c.recv(1024).decode('utf-8')
           
        [request_method, request_uri, protocol, headers, request_data] = parseRequest(request)

        # for header in headers:
        #     print(header)
        connection = True
        
        if "connection" in headers:
            if headers["connection"] == "close":
                connection = False
                

        response = generateResponse(addr, request_method, request_uri, protocol, headers, request_data)

        c.send(response)

        if connection:
            continue
        c.close()
        return

def main():
    host = "127.0.0.1"
    port = 8092


    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = (host, port)
    listening_socket.bind(server_addr)
    listening_socket.listen(1)
    print(f'Server listening on {host}:{port}')



    while True:
        client_connection, client_addr = listening_socket.accept()
      
        start_new_thread(threaded, (client_connection, client_addr))

    listening_socket.close()

if __name__ == '__main__':
    main()