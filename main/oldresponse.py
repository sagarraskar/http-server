import sys
import os
import time
from datetime import datetime
import mimetypes
import re
import error
from email.utils import formatdate
from constants import *

# DOCUMENT_ROOT = "/home/sagar/www/html/dist"
serverroot = "/home/sagar/httpserver"


def generateResponse(addr, req):
    response_headers = {}
    status_code = ""
    status_phrase = ""
    response_protocol = "HTTP/1.1"
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    response_headers["Date"] = date
    response_headers["Server"] = "http-server1.0"

    data = b''
    if None in [req["method"], req["headers"]] or (req["protocol"] != "HTTP/1.1" and req["protocol"] != "HTTP/1.0"):
        if None in [req["method"], req["headers"]]:
            print("None in headers")
        else:
            print("protocol does not match")
        status_code += "400"
        status_phrase += "Bad Request"

        data += error.getErrorPage(status_code, status_phrase,
                                   f"Request could not understand the request.").encode()
        response_headers["Content-Length"] = len(data)
        req["headers"]["Content-Type"] = "text/html"

    elif ("host" not in list(req["headers"].keys())) or req["headers"]["host"] not in [x+":"+str(SERVER_PORT) for x in SERVER_ADDR]:
        print("host not in headers")
        print(req["headers"]['host'])
        status_code += "400"
        status_phrase += "Bad Request"

        data += error.getErrorPage(status_code, status_phrase,
                                   f"Request could not understand the request.").encode()
        response_headers["Content-Length"] = len(data)
        req["headers"]["Content-Type"] = "text/html"

    elif req["method"] not in ["GET", "POST", "PUT", "DELETE", "HEAD"]:
        print("method not implemented")
        status_code += "501"
        status_phrase += "Method Not Implemented"

        response_headers['Allow'] = "GET,POST,HEAD,DELETE,PUT"
        response_headers['Connection'] = "close"

        data += error.getErrorPage(status_code, status_phrase,
                                   "{} not supported for current URL".format(req["method"])).encode('utf-8')
        content_length = len(data)
        content_type = "text/html"
        response_headers["Content-Length"] = content_length
        response_headers["Content-Type"] = content_type

    elif req["method"] == "PUT":
        if req["uri"] == "/":
                path = DOCUMENT_ROOT+"/index.html"
        else:
            path = req["uri"].split('?')[0]
            path = DOCUMENT_ROOT+path

        filename = path.split('/')[-1]
        directory_path = path.split('/')[:-1]
        directory_path = "/".join(directory_path)

        if directory_path == (DOCUMENT_ROOT + "/put"):
            if os.path.isfile(path):
                status_code = "204"
                status_phrase = "No Content"
                open(path, "w").close()
                fp = open(path, "wb")
                fp.write(req["body"])
                response_headers["Content-Location"] = "/put/" + filename

            else:
                status_code = "201"
                status_phrase = "Created"

                fp = open(path, "wb")
                fp.write(req["body"])
                response_headers["Content-Location"] = "/put/" + filename

        else:
            status_code = "405"
            status_phrase = "Method Not Allowed"

            data += error.getErrorPage(status_code, status_phrase,
                                       "The requested method {} is not allowed for thie url.".format(req["method"])).encode('utf-8')
            content_length = len(data)
            content_type = "text/html"
            response_headers["Content-Length"] = content_length
            response_headers["Content-Type"] = content_type
            response_headers["Allow"] = "GET, HEAD, POST"

    else:
        if req["uri"] == "/":
                path = DOCUMENT_ROOT+"/index.html"
        else:
            path = req["uri"].split('?')[0]
            path = DOCUMENT_ROOT+path

        filename = path.split('/')[-1]

        if not os.path.isfile(path):
            status_code = "404"
            status_phrase = "Not Found"

            data += error.getErrorPage(status_code, status_phrase,
                                       f"The requested URL was not found on this server.").encode('utf-8')
            content_length = len(data)
            content_type = "text/html"
            response_headers["Content-Length"] = content_length
            response_headers["Content-Type"] = content_type

        elif req["method"] == "GET":
            status_code = "200"
            status_phrase = "OK"

            fp = open(path, 'rb')
            data += fp.read()
            fp.close()

            last_modified = time.gmtime(os.path.getmtime(path))
            content_length = len(data)
            e_tag = '"' + hex(int(time.mktime(last_modified)))[2:] + "-" + hex(content_length)[2:] + '"'
            content_type = mimetypes.guess_type(filename)[0]

            condition = None
            if 'if-match' in list(req["headers"].keys()):
                e_tags = req["headers"]['if-match'].split(",")
                if e_tags[0] != '"*"':
                    for i in e_tags:
                        if i == e_tag:
                            condition = True
                            break
                    else:
                        status_code = "412"
                        status_phrase = "Precondition Failed"
                        data = b''

            elif 'if-unmodified-since' in list(req["headers"].keys()):
                date = req["headers"]["if-modified-since"]
                date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
                date = time.mktime(date.timetuple())

                if date > time.mktime(last_modified):
                    condition = True
                else:
                    condition = False
                    status_code = "412"
                    status_phrase = "Precondition Failed"
                    data = b''

            if (not condition or condition == True) and "if-none-match" in list(req["headers"].keys()):
                
                e_tags = req["headers"]['if-none-match'].split(",")
                if e_tags[0] == '"*"':
                    condition = False
                    status_code = "304"
                    status_phrase = "Not Modified"
                    data=b''
                
                else:
                    for i in e_tags:
                        if i == e_tag:
                            condition = False
                            status_code = "304"
                            status_phrase = "Not Modified"
                            data=b''
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
                    status_code="304"
                    status_phrase="Not Modified"
                    data=b''
                else:
                    condition = True
            

            if condition == True and 'range' in list(req["headers"].keys()) and req["headers"]['range'].split('=')[0] == 'bytes':
                ranges = []
                date = None
                if 'if-range' in list(req["headers"].keys()) and req["headers"]["if-range"][0] != '"':
                    date = req["headers"]["if-range"]
                    date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
                    date = time.mktime(date.timetuple())

                if date == None or (date != None and date > time.mktime(last_modified)):
                    raw_ranges = req["headers"]['range'].split('=')[1].split(',')
                    final_ranges = []
                    if len(raw_ranges) == 1:
                        fpos = None # first-byte-pos
                        lpos = None # last-byte-post
                        if raw_ranges[0][0] == "-":
                            fpos = len(data)-int(raw_ranges[0][1:])+1
                            lpos = int(raw_ranges[0][1:])
                            
                        elif raw_ranges[0][-1] == "-":
                            fpos = int(raw_ranges[0][:-1])
                            lpos = len(data)
                        else:
                            [fpos, lpos] = [int(x) for x in raw_ranges[0].split("-")]
                            
                        if lpos >= fpos:
                            final_ranges.append((fpos, lpos))
                            req["headers"]["content-range"] = "bytes " + str(final_ranges[0][0]) + "-" + str(final_ranges[0][1]) + "/" + str(content_length)
                            content_length = final_ranges[0][1] - final_ranges[0][0] + 1

                    # elif len(raw_ranges) > 1 and len(raw_ranges) < 10 :
                    #     for range in raw_ranges:
                    #         fpos = None # first-byte-pos
                    #         lpos = None # last-byte-post
                    #         if range[0] == "-":
                    #             fpos = len(data)-int(range[1:])+1
                    #             lpos = int(range[1:])
                                
                    #         elif range[-1] == "-":
                    #             fpos = int(range[:-1])
                    #             lpos = len(data)
                    #         else:
                    #             [fpos, lpos] = [int(x) for x in range.split("-")]
                                
                    #         if lpos >= fpos:
                    #             final_ranges.append((fpos, lpos))
                        

                    if len(final_ranges) > 0:
                        status_code = "206"
                        status_phrase = "Partial Content"
                        if len(final_ranges) == 1:
                            data = data[final_ranges[0][0]: (final_ranges[0][1] + 1)]
                            
            last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
            response_headers["Last-Modified"] = last_modified
            response_headers["Content-Length"] = content_length
            response_headers["Content-Type"] = content_type 
            response_headers["E-tag"] = e_tag
        
        elif req["method"] == "HEAD":
            status_code += "200"
            status_phrase += "OK"

            fp = open(path, 'rb')
            data+=fp.read()
            fp.close()
            
            last_modified = time.gmtime(os.path.getmtime(path))
            content_length = len(data)
            e_tag = '"' + hex(int(time.mktime(last_modified)))[2:] + "-" + hex(content_length)[2:] + '"'
            content_type = mimetypes.guess_type(filename)[0]
            
            condition = None
            if 'if-match' in list(req["headers"].keys()):
                e_tags = req["headers"]['if-match'].split(",")
                if e_tags[0] != '"*"':
                    for i in e_tags:
                        if i == e_tag:
                            condition = True
                            break
                    else:
                        status_code = "412"
                        status_phrase = "Precondition Failed"
                        data = b''

            elif 'if-unmodified-since' in list(req["headers"].keys()):
                date = req["headers"]["if-modified-since"]
                date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
                date = time.mktime(date.timetuple())

                if date > time.mktime(last_modified):
                    condition = True
                else:
                    condition = False
                    status_code = "412"
                    status_phrase = "Precondition Failed"
                    data = b''

            if (not condition or condition == True) and "if-none-match" in list(req["headers"].keys()):
                
                e_tags = req["headers"]['if-none-match'].split(",")
                if e_tags[0] == '"*"':
                    condition = False
                    status_code = "304"
                    status_phrase = "Not Modified"
                    data=b''
                
                else:
                    for i in e_tags:
                        if i == e_tag:
                            condition = False
                            status_code = "304"
                            status_phrase = "Not Modified"
                            data=b''
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
                    status_code="304"
                    status_phrase="Not Modified"
                    data=b''
                else:
                    condition = True
            
            
            last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
            response_headers["Last-Modified"] = last_modified
            response_headers["Content-Length"] = content_length
            response_headers["Content-Type"] = content_type 
            response_headers["E-tag"] = e_tag
            data=b''
            
        elif req["method"] == "POST":
            status_code += "200"
            status_phrase += "OK"

            postfile = serverroot + "/postdata/post.log"
            fp = open(path, 'rb')
            data+=fp.read()
            fp.close()

            fp = open(postfile, "a")
            log = "{}:{} [{}] [{}]\n".format(addr[0], addr[1], date, req["body"])
            fp.write(log)
            
            last_modified = time.gmtime(os.path.getmtime(path))
            last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
            content_length = len(data)
            content_type = mimetypes.guess_type(filename)[0]
            
            response_headers["last-modified"] = last_modified
            response_headers["content-length"] = content_length
            response_headers["content-type"] = content_type 
    
        elif req["method"] == "DELETE":
            fp = open(path, 'rb')
            data += fp.read()
            fp.close()

            last_modified = time.gmtime(os.path.getmtime(path))
            content_length = len(data)
            e_tag = '"' + hex(int(time.mktime(last_modified)))[2:] + "-" + hex(content_length)[2:] + '"'
            content_type = mimetypes.guess_type(filename)[0]

            condition = None
            if 'if-match' in list(req["headers"].keys()):
                e_tags = req["headers"]['if-match'].split(",")
                if e_tags[0] != '"*"':
                    for i in e_tags:
                        if i == e_tag:
                            condition = True
                            break
                    else:
                        status_code = "412"
                        status_phrase = "Precondition Failed"
                        data = b''

            elif 'if-unmodified-since' in list(req["headers"].keys()):
                date = req["headers"]["if-modified-since"]
                date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
                date = time.mktime(date.timetuple())

                if date > time.mktime(last_modified):
                    condition = True
                else:
                    condition = False
                    status_code = "412"
                    status_phrase = "Precondition Failed"
                    data = b''

            if (not condition or condition == True) and "if-none-match" in list(req["headers"].keys()):
                
                e_tags = req["headers"]['if-none-match'].split(",")
                if e_tags[0] == '"*"':
                    condition = False
                    status_code = "412"
                    status_phrase = "Precondition Failed"
                    data=b''
                
                else:
                    for i in e_tags:
                        if i == e_tag:
                            condition = False
                            status_code = "402"
                            status_phrase = "Precondition Failed"
                            data=b''
                            break
                    else:
                        condition = True
            

            if condition == True:
                os.remove(path)
                status_code = "204"
                status_phrase = "No Content"

            
            
    response = f"{response_protocol} {status_code} {status_phrase}\r\n"
    for name, value in response_headers.items():
        response+=f"{name}: {value}\r\n"
    
    response+="\n"
    response = response.encode()
    response += data
    # print(response)
    return response


