import re

headers = {}
def parseRequest(request) :
    request_header = None
    request_body = None

    request_method = None
    request_uri = None
    protocol = None
    headers = {}
    data=None

    

    fullrequest = request.split('\r\n\r\n')
    request_header = fullrequest[0]
  
    if len(fullrequest) == 2:
        request_body = fullrequest[1]
    
    request_line = request_header.split('\r\n')[0]
    
    request_line_pattern = "^\S* \/\S* \S*$"

    if re.search(request_line_pattern, request_line) != None:
        [request_method, request_uri, protocol] = request_line.split(' ')

    rawheaders = request_header.split('\n')[1:]
    header_pattern = "^\S*:*"

    for header in rawheaders:
        if len(header) <= 1:
            continue
        if re.search(header_pattern, header) == None:
            headers = None
            return [request_method, request_uri, protocol, headers, request_body]
        
        headers[header.split(':')[0].lower()] = header.split(':')[1].strip()

    return [request_method, request_uri, protocol, headers, request_body]


# request = "GET /index.html HTTP/1.1\r\nHost:127.0.0.1\r\n\r\nname:sagar\r\nlname:raskar"


# x=parseRequest(request)
# print(x)
# request ="""GET /index.html HTTP/1.1
# Host: 127.0.0.1:8080
# Connection: keep-alive
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
# Sec-Fetch-Site: none
# Sec-Fetch-Mode: navigate
# Sec-Fetch-User: ?1
# Sec-Fetch-Dest: document
# Accept-Encoding: gzip, deflate, br
# Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,pt;q=0.7
# """

# [method, path, protocol, version, headers] = parseRequest(request)
# print('Method: ', method)
# print('Path: ', path)
# print('Protoco: ', protocol)
# print('Version: ', version)
# for header in headers:
#     print(header)