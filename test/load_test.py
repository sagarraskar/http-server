import socket
import time
import threading
from responseparser import parseresponse
import sys
from config import *

def getrequest():
    serverName = "127.0.0.1"
    serverPort = SERVER_PORT
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))  
    request = """GET / HTTP/1.1\r
Host: 127.0.0.1:{}\r
""".format(SERVER_PORT).encode()

    clientSocket.send(request)
    response = clientSocket.recv(1024)
    response = parseresponse(response)
    if response["status_code"] == "200":
        print("response received")
    else:
        print("bad response")

    return

def load_test(requests):
    starttime = int(round(time.time() * 1000))
    threads = []
    for i in range(requests):  
        threads.append(threading.Thread(target=getrequest))
        threads[i].start()

    for t in threads:
        t.join()
    

    endtime = int(round(time.time() * 1000))

    print("Time required : ", endtime - starttime, " milliseconds")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 load_test.py <no_of_requests>")
        exit()

    requests = int(sys.argv[1])
    load_test(requests)