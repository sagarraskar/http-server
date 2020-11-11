from datetime import datetime
import time
import mimetypes
import os
from email.utils import formatdate
from error import * 
from config import *
from utils.errorlog import logerror

def put(addr, req, response):
    # response = {"headers": {}, "status_code": None, "status_phrase": None, "body": None}
    if req["uri"] == "/":
            path = DOCUMENT_ROOT+"/index.html"
    else:
        path = req["uri"].split('?')[0]
        path = DOCUMENT_ROOT+path

    filename = path.split('/')[-1]
    directory_path = path.split('/')[:-1]
    directory_path = "/".join(directory_path)

    if directory_path == (DOCUMENT_ROOT + PUT_DIRECTORY):
        if os.path.isfile(path):
            fp = open(path, 'rb')
            data = fp.read()
            fp.close()

            last_modified = time.gmtime(os.path.getmtime(path))
            content_length = len(data)
            e_tag = '"' + hex(int(time.mktime(last_modified)))[2:] + "-" + hex(content_length)[2:] + '"'
            
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
                        logerror(addr, req, response)

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
                    logerror(addr, req, response)

            if (condition == None or condition == True) and "if-none-match" in list(req["headers"].keys()):
                
                e_tags = req["headers"]['if-none-match'].split(",")
                if e_tags[0] == '"*"':
                    condition = False
                    response["status_code"] = "304"
                    response["status_phrase"] = "Not Modified"
                    
                
                else:
                    for i in e_tags:
                        if i == e_tag:
                            condition = False
                            response["status_code"] = "304"
                            response["status_phrase"] = "Not Modified"
                            
                            break
                    else:
                        condition = True

            if condition == None or condition == True:
                response["status_code"] = "204"
                response["status_phrase"] = "No Content"
                open(path, "w").close()
                fp = open(path, "wb")
                fp.write(req["body"])
                fp.close()
                last_modified = time.gmtime(os.path.getmtime(path))
                e_tag = '"' + hex(int(time.mktime(last_modified)))[2:] + "-" + hex(os.path.getsize(path))[2:] + '"'

                last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
                response["headers"]["Content-Location"] = "/put/" + filename
                response["headers"]["Last-Modified"] = last_modified
                response["headers"]["E-tag"] = e_tag


        else:
            response["status_code"] = "201"
            response["status_phrase"] = "Created"

            fp = open(path, "wb")
            fp.write(req["body"])
            fp.close()
            last_modified = time.gmtime(os.path.getmtime(path))
            e_tag = '"' + hex(int(time.mktime(last_modified)))[2:] + "-" + hex(os.path.getsize(path))[2:] + '"'

            last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified) 
            response["headers"]["Content-Location"] = "/put/" + filename
            response["headers"]["Last-Modified"] = last_modified
            response["headers"]["E-tag"] = e_tag
    else:
        response["status_code"] = "405"
        response["status_phrase"] = "Method Not Allowed"

        data = getErrorPage(response["status_code"], response["status_phrase"], "The requested method {} is not allowed for thie url.".format(req["method"])).encode('utf-8')
        content_length = len(data)
        content_type = "text/html"
        response["headers"]["Content-Length"] = content_length
        response["headers"]["Content-Type"] = content_type
        response["headers"]["Allow"] = "GET, HEAD, POST"
        response["body"] = data

    return response