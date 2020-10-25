import sys
import os
import time
import mimetypes
import re
import error
from email.utils import formatdate

documentroot = "/home/sagar/www/html/dist"
def generateResponse(method, uri, protocol, request_headers, request_data):
    response_headers = {}
    status_code = ""
    status_phrase = ""
    response_protocol = "HTTP/1.1"
    response_headers["Date"] = formatdate(timeval=None, localtime=False, usegmt=True)
    response_headers["Server"] = "http-server1.0"

    data=b''
    if None in [method, request_headers] or (protocol != "HTTP/1.1" and protocol != "HTTP/1.0"):
        status_code += "400"
        status_phrase += "Bad Request"

        data += error.getErrorPage(status_code, status_phrase, f"Request could not understand the request.").encode()
        response_headers["Content-Length"] = len(data)
        request_headers["Content-Type"] = "text/html"
    
        
    elif ("host" not in list(request_headers.keys())) or request_headers["host"] != "127.0.0.1":
        status_code += "400"
        status_phrase += "Bad Request"

        data += error.getErrorPage(status_code, status_phrase, f"Request could not understand the request.").encode()
        response_headers["Content-Length"] = len(data)
        request_headers["Content-Type"] = "text/html"

    elif method not in ["GET", "POST", "PUT", "DELETE", "HEAD"]:
        status_code += "501"
        status_phrase += "Method Not Implemented"

        response_headers['Allow'] = "GET,POST,HEAD,DELETE,PUT"
        response_headers['Connection'] = "close"

        data += error.getErrorPage(status_code, status_phrase, f"{method} not supported for current URL").encode('utf-8')
        content_length = len(data)
        content_type = "text/html"
        response_headers["Content-Length"] = content_length
        response_headers["Content-Type"] = content_type

    elif method == "GET":
        if uri == "/":
            path = documentroot+"/index.html"
        else:
            path = uri.split('?')[0]
            path = documentroot+path
        
        filename = path.split('/')[-1]

        
        if os.path.isfile(path):
            
            
            status_code += "200"
            status_phrase += "OK"

            fp = open(path, 'rb')
            data+=fp.read()
            
            last_modified = time.gmtime(os.path.getmtime(path))
            last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
            content_length = len(data)
            content_type = mimetypes.guess_type(filename)[0]
            
            response_headers["last-modified"] = last_modified
            response_headers["content-length"] = content_length
            response_headers["content-type"] = content_type 
 
               
        else:
            status_code = "404"
            status_phrase = "Not Found"
            
            data += error.getErrorPage(status_code, status_phrase, f"The requested URL was not found on this server.").encode('utf-8')
            content_length = len(data)
            content_type = "text/html"
            response_headers["Content-Length"] = content_length
            response_headers["Content-Type"] = content_type

            
    response = f"{response_protocol} {status_code} {status_phrase}\r\n"
    for name, value in response_headers.items():
        response+=f"{name}: {value}\r\n"
    
    response+="\n"
    response = response.encode()
    response += data
    return response


