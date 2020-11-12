from config import *

def logaccess(addr, req, res):
        if addr[0]:
            client_ip = addr[0]
        else:
            addr[0] = "-"
        
        if "Date" in list(res["headers"].keys()):
            date = res["headers"]["Date"]
        else:
            date = "-"

        if "status_code" in list(res.keys()):
            status_code = res["status_code"]
        else:
            status_code = "-"
       
        if "Content-Length" in list(res["headers"].keys()):
            content_length = res["headers"]["Content-Length"]
        else:
            content_length = "0"

        req_line = "{} {} {}".format(req["method"], req["uri"], req["protocol"])
        access_log = '{} [{}] "{}" {} {}\n'.format(client_ip, date, req_line, res["status_code"], content_length)
    
        with open(LOG_DIRECTORY + "/" + ACCESS_LOG_FILE, "a") as file:
            file.write(access_log)