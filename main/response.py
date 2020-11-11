import sys
import os
import time
from datetime import datetime
import mimetypes
import re
import error
from email.utils import formatdate
from utils.errorlog import logerror
from config import *
from methods.get import get
from methods.post import post
from methods.put import put
from methods.head import head
from methods.delete import delete

# DOCUMENT_ROOT = "/home/sagar/www/html/dist"
# serverroot = "/home/sagar/httpserver"


def generateResponse(addr, req):
    response = {"headers": {}, "protocol": "HTTP/1.1", "status_code": None, "status_phrase": None, "body": None}

    date = formatdate(timeval=None, localtime=False, usegmt=True)
    response["headers"]["Date"] = date
    response["headers"]["Server"] = "http-server1.0"
    response["headers"]["Connection"] = "close"

    if None in [req["method"], req["headers"]] or (req["protocol"] != "HTTP/1.1" and req["protocol"] != "HTTP/1.0"):
        if None in [req["method"], req["headers"]]:
            print("None in headers")
        else:
            print("protocol does not match")
        response["status_code"] = "400"
        response["status_phrase"]= "Bad Request"

        data = error.getErrorPage(response["status_code"], response["status_phrase"], f"Request could not understand the request.").encode()
        response["headers"]["Content-Length"] = len(data)
        response["headers"]["Content-Type"] = "text/html"
        response["body"] = data
        
        logerror(addr, req, response)

    elif ("host" not in list(req["headers"].keys())) or req["headers"]["host"] not in [x+":"+str(SERVER_PORT) for x in ["localhost", "127.0.0.1"]]:
        print("host not in headers")
        print(req["headers"]['host'])
        response["status_code"] = "400"
        response["status_phrase"] = "Bad Request"

        data = error.getErrorPage(response["status_code"], response["status_phrase"], f"Request could not understand the request.").encode()
        response["headers"]["Content-Length"] = len(data)
        response["headers"]["Content-Type"] = "text/html"
        response["body"] = data
        
        logerror(addr, req, response)

    elif req["method"] not in ["GET", "POST", "PUT", "DELETE", "HEAD"]:
        # print("method not implemented")
        response["status_code"] = "501"
        response["status_phrase"] = "Method Not Implemented"

        response["headers"]['Allow'] = "GET,POST,HEAD,DELETE,PUT"
        response["headers"]['Connection'] = "close"

        data = error.getErrorPage(response["status_code"], response["status_phrase"], "{} not supported for current URL".format(req["method"])).encode('utf-8')
        content_length = len(data)
        content_type = "text/html"
        response["headers"]["Content-Length"] = content_length
        response["headers"]["Content-Type"] = content_type
        response["body"] = data

        logerror(addr, req, response)


            
    elif req["method"] == "PUT":
        put(addr, req, response)

    elif req["method"] == "GET":
        get(addr, req, response)

    elif req["method"] == "HEAD":
        head(addr, req, response)

    elif req["method"] == "POST":
        post(addr, req, response)

    elif req["method"] == "DELETE":
        delete(addr, req, response)
      
    return response


