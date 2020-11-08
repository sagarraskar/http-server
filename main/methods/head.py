from datetime import datetime
import time
import mimetypes
import os
from error import * 
from constants import *

def head(addr, req, response):
    if req["uri"] == "/":
        path = DOCUMENT_ROOT+"/index.html"
    else:
        path = req["uri"].split('?')[0]
        path = DOCUMENT_ROOT+path

    filename = path.split('/')[-1]
    
    if not os.path.isfile(path):
        response["status_code"] = "404"
        response["status_phrase"] = "Not Found"

        data = getErrorPage(response["status_code"], response["status_phrase"], "The requested URL was not found on this server.").encode('utf-8')
        content_length = len(data)
        content_type = "text/html"
        response["headers"]["Content-Length"] = content_length
        response["headers"]["Content-Type"] = content_type
    
    else:
        response["status_code"] = "200"
        response["status_phrase"] = "OK"

        fp = open(path, 'rb')
        data = fp.read()
        fp.close()

        last_modified = time.gmtime(os.path.getmtime(path))
        content_length = len(data)
        e_tag = '"' + hex(int(time.mktime(last_modified)))[2:] + "-" + hex(content_length)[2:] + '"'
        content_type = mimetypes.guess_type(filename)[0]

        condition = None
        if 'if-match' in list(req["headers"].keys()):
            e_tags = req["headers"]['if-match'].split(",")
            if e_tags[0] == '"*"':
                condition = True
            else:
                for i in e_tags:
                    if i == e_tag:
                        condition = True
                        break
                else:
                    condition = False
                    response["status_code"] = "412"
                    response["status_phrase"] = "Precondition Failed"
                    data = None

        elif 'if-unmodified-since' in list(req["headers"].keys()):
            date = req["headers"]["if-modified-since"]
            date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
            date = time.mktime(date.timetuple())

            if date > time.mktime(last_modified):
                condition = True
            else:
                condition = False
                response["status_code"] = "412"
                response["status_phrase"] = "Precondition Failed"
                data = None

        if (condition == None or condition == True) and "if-none-match" in list(req["headers"].keys()):
            
            e_tags = req["headers"]['if-none-match'].split(",")
            if e_tags[0] == '"*"':
                condition = False
                response["status_code"] = "304"
                response["status_phrase"] = "Not Modified"
                data = None
            
            else:
                for i in e_tags:
                    if i == e_tag:
                        condition = False
                        response["status_code"] = "304"
                        response["status_phrase"] = "Not Modified"
                        data = None
                        break
                else:
                    condition = True

        elif 'if-modified-since' in list(req["headers"].keys()):
            date = req["headers"]["if-modified-since"]
            date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
            date = time.mktime(date.timetuple())

            if date >= time.mktime(last_modified):
                condition = False
                print("304 Not modified")
                response["status_code"]="304"
                response["status_phrase"]="Not Modified"
                data = None
            else:
                condition = True
        
                        
        last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
        response["headers"]["Last-Modified"] = last_modified
        response["headers"]["Content-Length"] = content_length
        response["headers"]["Content-Type"] = content_type 
        response["headers"]["E-tag"] = e_tag
    
    return response

# request = {'method': 'GET', 'uri': '/', 'protocol': 'HTTP/1.1', 'headers': {'host': '127.0.0.1:8091', 'if-modified-since': 'Sun, 28 Oct 2020 08:43:22 GMT', 'connection': 'close'}, 'body': None}
# response = get(None, request)
# print(response)
