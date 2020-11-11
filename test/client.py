import socket
import sys
from responseparser import parseresponse
from config import *


conditional_get_request1 = """GET / HTTP/1.1\r
Host: 127.0.0.1:8092\r
If-Modified-Since: Tue, 10 Nov 2020 09:07:09 GMT\r
""".encode()

conditional_get_request2 = """GET / HTTP/1.1\r
Host: 127.0.0.1:8092\r
If-None-Match: "5faa0ae5-207"\r
""".encode()

with open("iphone12.jpg", "rb") as file:
    data = file.read()

# put_request = """PUT /put/iphone12.jpg HTTP/1.1\r
# Host: 127.0.0.1:8092\r
# Content-Type: image/jpg\r
# Content-Length: {}\r
# \r
# """.format(len(data)).encode()

# put_request += data

post_request = """POST /index.html HTTP/1.1\r
Host: 127.0.0.1:8092\r
Content-Type: image/jpg\r
Content-Length: {}\r
\r
""".format(len(data)).encode()


post_request += data

def main():
    serverName = "127.0.0.1"
    serverPort = 8092
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    # TEST 1
    get_request = """GET / HTTP/1.1\r
Host: 127.0.0.1:8092\r
""".encode()

    print("Running Test 1 (Simple get request)")
    clientSocket.send(get_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break

    response = parseresponse(response)

    with open(DOCUMENT_ROOT + "/index.html", "rb") as file:
        data = file.read()

    if response["status_code"] == "200":
        for i in range(len(data)):
            if data[i] != response['body'][i]:
                print("Test 1 Failed")
                break
        else:
            print("Test 1 Passed")  
    else:
        print("Test 1 Failed")
    clientSocket.close()

    # TEST 2
    with open("iphone12.jpg", "rb") as file:
        data = file.read()

    put_request = """PUT /put/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:8092\r
Content-Type: image/jpg\r
Content-Length: {}\r
\r
""".format(len(data)).encode()

    put_request += data
    print("Running Test 2 (Conditional Get request with if-modified-since header)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(conditional_get_request1)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)

    if response["status_code"] == "304" and len(response['body']) == 0:
          print("Test 2 Passed")
    else:
        print("Test 2 Failed")

    
    # TEST 3
    print("Running Test 3 (Conditional Get request with if-none-match header)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(conditional_get_request2)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)

    if response["status_code"] == "304" and len(response['body']) == 0:
          print("Test 3 Passed")
    else:
        print("Test 3 Failed")

    # TEST 4
    print("Running Test 4 (Simple PUT request)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(put_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)

    if response["status_code"] == "201" or response["status_code"] == "204":
        with open("iphone12.jpg", "rb") as file:
            client_data = file.read()
        with open(DOCUMENT_ROOT + PUT_DIRECTORY + "/iphone12.jpg", "rb") as file:
            server_data = file.read()

        if len(client_data) == len(server_data):
            for i in range(len(client_data)):
                if client_data[i] != server_data[i]:
                    print("data not same")
                    print("Test 4 Failed")
                    break
            else:
                print("Test 4 passed")
        else:
            print("len of data not equal")
            print("Test 4 Failed")
       
    else:
        print(response["status_code"])
        print("Test 4 Failed")    

    # TEST 5
    print("Running Test 5 (Conditional PUT request)")
    get_request = """GET /put/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:8092\r
""".encode()

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(get_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)    
    e_tag = response["headers"]["e-tag"]
    # print("Previous E-tag", e_tag)

    with open("realme7pro.jpeg", "rb") as file:
        data = file.read()

    put_request = """PUT /put/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:8092\r
Content-Type: image/jpg\r
Content-Length: {}\r
\r
""".format(len(data)).encode()

    put_request += data
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(put_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)
    # print("E-tag: ", response["headers"]["e-tag"])
    with open("iphone12.jpg", "rb") as file:
        data = file.read()

    put_request = """PUT /put/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:8092\r
Content-Type: image/jpg\r
Content-Length: {}\r
If-Match: {}\r
\r
""".format(len(data), e_tag).encode()

    put_request += data
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(put_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)

    if response["status_code"] == "412":
        print("Test 5 passed")
    else:
        print(response)
        print("Test 5 Failed")

    # TEST 6
    print("Running Test 6 (POST request)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(post_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)

    if response["status_code"] == "201" and "location" in list(response["headers"].keys()):
        path = DOCUMENT_ROOT + response["headers"]["location"]
        with open("iphone12.jpg", "rb") as file:
            client_data = file.read()

        with open(path, "rb") as file:
            server_data = file.read()

        if len(client_data) == len(server_data):
            for i in range(len(client_data)):
                if client_data[i] != server_data[i]:
                    print("data not same")
                    print("Test 6 Failed")
                    break
            else:
                print("Test 6 passed")
        else:
            print("len of data not equal")
            print("Test 6 Failed")

    else:
        print("Test 6 Failed")


  

if __name__ == '__main__':
    main()