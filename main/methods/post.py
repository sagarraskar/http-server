from datetime import datetime
import time
import mimetypes
import os
from email.utils import formatdate
from error import * 
from constants import *

def post(addr, req, response):
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    if req["uri"] == "/":
        path = DOCUMENT_ROOT+"/index.html"
    else:
        path = req["uri"].split('?')[0]
        path = DOCUMENT_ROOT+path

    filename = path.split('/')[-1]
    response["headers"] = {}
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

        postfile = SERVER_ROOT + "/postdata/post.log"
        fp = open(path, 'rb')
        data = fp.read()
        fp.close()

        fp = open(postfile, "a")
        log = "{}:{} [{}] [{}]\n".format(addr[0], addr[1], date, req["body"])
        fp.write(log)
        
        last_modified = time.gmtime(os.path.getmtime(path))
        last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
        content_length = len(data)
        content_type = mimetypes.guess_type(filename)[0]
        
        response["headers"]["last-modified"] = last_modified
        response["headers"]["content-length"] = content_length
        response["headers"]["content-type"] = content_type 
    
    return response