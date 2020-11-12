from datetime import datetime
import random
import time
import mimetypes
import os
from error import * 
from config import *
from utils.errorlog import logerror

def get(addr, req, response):
    # response = {"headers": {}, "status_code": None, "status_phrase": None, "body": None}
    if req["uri"] == "/":
        path = DOCUMENT_ROOT+"/index.html"
    else:
        path = req["uri"].split('?')[0]
        path = DOCUMENT_ROOT+path

    filename = path.split('/')[-1]
    
    if not os.path.isfile(path):
        response["status_code"] = "404"
        response["status_phrase"] = "Not Found"

        data = getErrorPage(response["status_code"], response["status_phrase"],
                                    f"The requested URL was not found on this server.").encode('utf-8')
        content_length = len(data)
        content_type = "text/html"
        response["headers"]["Content-Length"] = content_length
        response["headers"]["Content-Type"] = content_type
        response["body"] = data
        logerror(addr, req, response)
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
                    # data = None
                    logerror(addr, req, response)

        elif 'if-unmodified-since' in list(req["headers"].keys()):
            date = req["headers"]["if-modified-since"]
            date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
            date = time.mktime(date.timetuple())

            if date >= time.mktime(last_modified):
                condition = True
            else:
                condition = False
                response["status_code"] = "412"
                response["status_phrase"] = "Precondition Failed"
                # data = None
                logerror(addr, req, response)

        if (condition == None or condition == True): 
            if "if-none-match" in list(req["headers"].keys()):
            
                e_tags = req["headers"]['if-none-match'].split(",")
                if e_tags[0] == '"*"':
                    condition = False
                    response["status_code"] = "304"
                    response["status_phrase"] = "Not Modified"
                    # data=None
                
                else:
                    for i in e_tags:
                        if i == e_tag:
                            condition = False
                            response["status_code"] = "304"
                            response["status_phrase"] = "Not Modified"
                            # data=b''
                            break
                    else:
                        condition = True

            elif 'if-modified-since' in list(req["headers"].keys()):
                date = req["headers"]["if-modified-since"]
                date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
                date = time.mktime(date.timetuple())

                if date >= time.mktime(last_modified):
                    condition = False
                    response["status_code"]="304"
                    response["status_phrase"]="Not Modified"
                    # data=b''
                else:
                    condition = True
            

        if (condition == None or condition == True) and 'range' in list(req["headers"].keys()) and req["headers"]['range'].split('=')[0] == 'bytes':
            range_condition = None
            if 'if-range' in list(req["headers"].keys()): 
                if req["headers"]["if-range"][0] != '"':
                    date = req["headers"]["if-range"]
                    date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
                    date = time.mktime(date.timetuple())
   
                    if date >= time.mktime(last_modified):
                        range_condition = True
                    else:
                        range_condition = False
                else:
                    request_e_tag = req["headers"]["if-range"]
                    if e_tag == request_e_tag:
                        range_condition = True
                    else:
                        range_condition = False

            if range_condition == None or range_condition == True:
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

     
                if len(final_ranges) > 0:
                    response["status_code"] = "206"
                    response["status_phrase"] = "Partial Content"
                    if len(final_ranges) == 1:
                        data = data[final_ranges[0][0]: (final_ranges[0][1] + 1)]
        
        if condition == None or condition == True:  
            if "cookie" not in req["headers"]:
                response["headers"]["Set-Cookie"] = "sessionId={}".format(random.randint(100000, 1000000))
            last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
            response["headers"]["Last-Modified"] = last_modified
            response["headers"]["Content-Length"] = content_length
            response["headers"]["Content-Type"] = content_type 
            response["headers"]["E-tag"] = e_tag
            response["headers"]["Accept-Ranges"] = "bytes"
            response["body"] = data
    
    return response
