import re

def parseresponse(response) :
    response_header = None
    response_body = None

    status_code = None
    status_phrase = None
    protocol = None
    headers = {}
    data=None


    fullresponse = response.split(b'\r\n\r\n')
    response_header = fullresponse[0]
  
    if len(fullresponse) == 2:
        response_body = fullresponse[1]
    
    response_header = response_header.decode()

    
    response_line = response_header.split('\r\n')[0]
    # print(response_line)

    [protocol, status_code] = response_line.split(' ')[:2]
    status_phrase = (' ').join(response_line.split(' ')[2: ])

    rawheaders = response_header.split('\r\n')[1:]

    for header in rawheaders:
        if len(header) <= 1:
            continue
        
        headers[header.split(':', 1)[0].lower()] = header.split(':', 1)[1].strip()

    response = {"status_code" : status_code, "status_phrase": status_phrase, "protocol" : protocol, "headers" : headers, "body": response_body}
  
    return response
