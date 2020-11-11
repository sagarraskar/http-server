from config import *

def logerror(addr, req, res):
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

        if "status_phrase" in list(res.keys()):
            status_phrase = res["status_phrase"]
        else:
            status_phrase = "-"

        req_line = "{} {} {}".format(req["method"], req["uri"], req["protocol"])
        error_log = '{} [{}] "{}" {} {}\n'.format(client_ip, date, req_line, status_code, status_phrase)
        with open(LOG_DIRECTORY + "/" + ERROR_LOG_FILE, "a") as file:
            file.write(error_log)