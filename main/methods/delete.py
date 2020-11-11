from datetime import datetime
import time
import mimetypes
import os
from error import * 
from config import *
from utils.errorlog import logerror

def delete(addr, req, response):
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
        response["headers"]["body"] = data

        logerror(addr, req, response)

    else:
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
                    response["status_code"] = "412"
                    response["status_phrase"] = "Precondition Failed"
                    data = None
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
                data = None
                logerror(addr, req, response)

        if (condition == None or condition == True) and "if-none-match" in list(req["headers"].keys()):
            
            e_tags = req["headers"]['if-none-match'].split(",")
            if e_tags[0] == '"*"':
                condition = False
                response["status_code"] = "412"
                response["status_phrase"] = "Precondition Failed"
                data = None
                logerror(addr, req, response)
            else:
                for i in e_tags:
                    if i == e_tag:
                        condition = False
                        response["status_code"] = "402"
                        response["status_phrase"] = "Precondition Failed"
                        data = None
                        logerror(addr, req, response)
                        break
                else:
                    condition = True
        

        if condition == True:
            os.remove(path)
            response["status_code"] = "204"
            response["status_phrase"] = "No Content"
    
    return response