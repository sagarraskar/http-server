import time
import datetime
import mimetypes
import os

def main(request_headers, status_code, filename): 
    path = "/home/sagar/www/html/index.html"
    fp = open(path, 'rb')
    data=fp.read()
    fp.close()
    response_headers = {}
    last_modified = time.gmtime(os.path.getmtime(path))
    content_length = len(data)
    content_type = mimetypes.guess_type(filename)[0]

    if status_code == "200" and 'range' in list(request_headers.keys()) and request_headers['range'].split('=')[0] == 'bytes':
       
        ranges = []
        date = None
        if 'if-range' in list(request_headers.keys()) and request_headers["if-range"][0] != '"':
            date = request_headers["if-range"]
            date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
            date = time.mktime(date.timetuple())

        if date == None or (date != None and date > time.mktime(last_modified)):
            raw_ranges = request_headers['range'].split('=')[1].split(',')
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
                    if lpos > len(data):
                        lpos = len(data)
                    final_ranges.append((fpos, lpos))
                    response_headers["content-range"] = "bytes " + str(final_ranges[0][0]) + "-" + str(final_ranges[0][1]) + "/" + str(content_length)
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
                    print(final_ranges[0][0], final_ranges[0][1])
                    data = data[final_ranges[0][0]: (final_ranges[0][1] + 1)]
                                
    last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)
    response_headers["last-modified"] = last_modified
    response_headers["content-length"] = content_length
    response_headers["content-type"] = content_type 
    return [response_headers, data]
[respons_headers, data] = main({"range" : "bytes=100-98"}, "200", "index.html")
print(respons_headers)
print(len(data))
print(data)