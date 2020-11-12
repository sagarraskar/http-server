import socket
import os
import sys
from responseparser import parseresponse
from config import *



def main():
    serverName = "127.0.0.1"
    serverPort = SERVER_PORT
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    # TEST 1 (Simple GET request)
    get_request = """GET / HTTP/1.1\r
Host: 127.0.0.1:{}\r
""".format(SERVER_PORT).encode()

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
        e_tag = response["headers"]["e-tag"]
        last_modified = response["headers"]["last-modified"]
        for i in range(len(data)):
            if data[i] != response['body'][i]:
                print("Test 1 Failed")
                break
        else:
            print("Test 1 Passed")  
    else:
        print("Test 1 Failed")
    clientSocket.close()

    # TEST 2 (conditional GET request)
    conditional_get_request1 = """GET / HTTP/1.1\r
Host: 127.0.0.1:{}\r
If-Modified-Since: {}\r
""".format(SERVER_PORT, last_modified).encode()

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

    
    # TEST 3 (Conditional get request(if-none-match))
    conditional_get_request2 = """GET / HTTP/1.1\r
Host: 127.0.0.1:{}\r
If-None-Match: {}\r
""".format(SERVER_PORT, e_tag).encode()

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

    # TEST 4 (Simple PUT Request)
    with open("iphone12.jpg", "rb") as file:
        data = file.read()

    put_request = """PUT {}/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:{}\r
Content-Type: image/jpg\r
Content-Length: {}\r
\r
""".format(PUT_DIRECTORY, SERVER_PORT, len(data)).encode()
    put_request += data
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

    # TEST 5 (Conditional PUT Request)
    print("Running Test 5 (Conditional PUT request)")
    get_request = """GET {}/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:{}\r
""".format(PUT_DIRECTORY, SERVER_PORT).encode()

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

    put_request = """PUT {}/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:{}\r
Content-Type: image/jpg\r
Content-Length: {}\r
\r
""".format(PUT_DIRECTORY, SERVER_PORT, len(data)).encode()

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

    put_request = """PUT {}/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:{}\r
Content-Type: image/jpg\r
Content-Length: {}\r
If-Match: {}\r
\r
""".format(PUT_DIRECTORY, SERVER_PORT, len(data), e_tag).encode()

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

    # TEST 6 (POST REQUEST)

    with open("iphone12.jpg", "rb") as file:
        data = file.read()
    post_request = """POST /index.html HTTP/1.1\r
Host: 127.0.0.1:{}\r
Content-Type: image/jpg\r
Content-Length: {}\r
\r
""".format(SERVER_PORT, len(data)).encode()


    post_request += data
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


    # TEST 7 (404 Not Found)
    request = """GET /about.html HTTP/1.1\r
Host: 127.0.0.1:{}\r
""".format(SERVER_PORT).encode()
    print("Running Test 7 (404 Not Found)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)
    if response["status_code"] == "404":
        print("Test 7 passed")
    else:
        print("Test 7 Failed")

    # TEST 8 (400 Bad Request)
    request = """GET / http/1.1\r
Host: 127.0.0.1:{}\r
""".format(SERVER_PORT).encode()
    print("Running Test 8 (400 Bad Request)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)
    if response["status_code"] == "400":
        print("Test 8 passed")
    else:
        print("Test 8 Failed")

    # TEST 9 (501 Method Not Implemented)
    request = """OPTION / HTTP/1.1\r
Host: 127.0.0.1:{}\r
""".format(SERVER_PORT).encode()
    print("Running Test 9 (501 Method Not Implemented)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)
    if response["status_code"] == "501" and "allow" in list(response["headers"].keys()):
        print("Test 9 passed")
    else:
        print("Test 9 Failed")

    # TEST 10 (405 Method Not Allowed)

    with open("iphone12.jpg", "rb") as file:
        data = file.read()

    request = """PUT /iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:{}\r
Content-Type: image/jpg\r
Content-Length: {}\r
\r
""".format(SERVER_PORT, len(data)).encode()

    request += data
    print("Running Test 10 (405 Method Not Allowed)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)
    if response["status_code"] == "405" and "allow" in list(response["headers"].keys()):
        print("Test 10 passed")
    else:
        print("Test 10 Failed")


    # TEST 11 (Range request)

    range_request = """GET / HTTP/1.1\r
Host: 127.0.0.1:{}\r
Range: bytes=100-200\r
""".format(SERVER_PORT).encode()

    print("Running Test 11 (Range request)")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(range_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)
    with open(DOCUMENT_ROOT + "/index.html", "rb") as file:
        data = file.read()

    if response["status_code"] == "206":
        e_tag = response["headers"]["e-tag"]
        last_modified = response["headers"]["last-modified"]
        data = data[100:201]
        if len(data) == len(response['body']):
            for i in range(len(data)):
                if data[i] != response['body'][i]:
                    print("data not equal")
                    print("Test 11 Failed")
                    break
            else:
                print("Test 11 Passed") 
        else:
            print("len not equal")
            print("Test 11 Failed")
    else:
        print(response["status_code"], response["status_phrase"])
        print("Test 11 Failed")

    # TEST 12 (Conditional Range request (If-Range with HTTP date))

    range_request = """GET / HTTP/1.1\r
Host: 127.0.0.1:{}\r
Range: bytes=100-200\r
If-Range: {}\r
""".format(SERVER_PORT, last_modified).encode()

    print("Running Test 12 (Conditional Range request (If-Range with HTTP date))")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(range_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)
    with open(DOCUMENT_ROOT + "/index.html", "rb") as file:
        data = file.read()

    if response["status_code"] == "206":
        data = data[100:201]
        if len(data) == len(response['body']):
            for i in range(len(data)):
                if data[i] != response['body'][i]:
                    print("data not equal")
                    print("Test 12 Failed")
                    break
            else:
                print("Test 12 Passed") 
        else:
            print("len not equal")
            print("Test 12 Failed")
    else:
        print(response["status_code"], response["status_phrase"])
        print("Test 12 Failed")

    # TEST 13 (Conditional Range request (If-Range with HTTP date))

    range_request = """GET / HTTP/1.1\r
Host: 127.0.0.1:{}\r
Range: bytes=100-200\r
If-Range: {}\r
""".format(SERVER_PORT, e_tag).encode()

    print("Running Test 13 (Conditional Range request(If-Range with E-tag))")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(range_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)
    with open(DOCUMENT_ROOT + "/index.html", "rb") as file:
        data = file.read()

    if response["status_code"] == "206":
        data = data[100:201]
        if len(data) == len(response['body']):
            for i in range(len(data)):
                if data[i] != response['body'][i]:
                    print("data not equal")
                    print("Test 13 Failed")
                    break
            else:
                print("Test 13 Passed") 
        else:
            print("len not equal")
            print("Test 13 Failed")
    else:
        print(response["status_code"], response["status_phrase"])
        print("Test 13 Failed")

    # TEST 14 (DELETE request)
    delete_request = """DELETE {}/iphone12.jpg HTTP/1.1\r
Host: 127.0.0.1:{}\r
""".format(PUT_DIRECTORY, SERVER_PORT).encode()

    print("Running Test 14 (DELETE request))")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(delete_request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)

    if response["status_code"] == "204":
        if os.path.exists(DOCUMENT_ROOT + PUT_DIRECTORY + "/iphone12.jpg"):
            print("TEST 14 Failed")
        else:
            print("TEST 14 Passed")
    else:
        print("TEST 14 Failed")

    # TEST 15 (Test for Cookie)
    request = """GET / HTTP/1.1\r
Host: 127.0.0.1:{}\r
""".format(SERVER_PORT).encode()

    print("Running Test 15 (TEST for cookie))")
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    clientSocket.send(request)
    response = b''
    while True:
        partial_response = clientSocket.recv(1024)
        
        response += partial_response
        if len(partial_response) < 1024:
            break
        
    response = parseresponse(response)

    if response["status_code"] == "200":
        if "set-cookie" in list(response["headers"].keys()):
            print("TEST 15 Passed")
        else:
            print("TEST 15 Failed")
    else:
        print("TEST 15 Failed")

if __name__ == '__main__':
    main()