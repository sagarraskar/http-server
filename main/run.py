#!/usr/bin/python3

import sys
import os
from config import *
from pathlib import Path
import configparser

def createdefaultconfig():
    config = configparser.ConfigParser()
    config["SERVER"] = {
        "SERVER_PORT" : 8092, 
        "DOCUMENT_ROOT" : "/var/www/html2", 
        "POST_DIRECTORY": "/post",
        "PUT_DIRECTORY" : "/put"
    }
    config["LOG"] = {
        "LOG_DIRECTORY" : "/var/log/httpserver",
        "ACCESS_LOG_FILE": "access.log",
        "ERROR_LOG_FILE" : "error.log",
        "POST_LOG_FILE": "post.log"
    }
    config["CONNECTION"] = {
        "MAX_CONNECTIONS" : 5
    }
    with open("/etc/httpserver/server.conf", "w") as file:
        config.write(file)




def start():
    if os.path.getsize("app.pid") > 0:
        print("Server is already running")
        exit()
    print("Starting HTTP server")
    if not os.path.exists("/etc/httpserver"):
        print("Configuring server")
        Path("/etc/httpserver").mkdir(parents=True, exist_ok=True)

    if not os.path.exists(DOCUMENT_ROOT):
        Path(DOCUMENT_ROOT).mkdir(parents=True, exist_ok=True)

    if not os.path.exists(LOG_DIRECTORY):
        Path(LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)

    if not os.path.exists(POST_DIRECTORY):
        Path(POST_DIRECTORY).mkdir(parents=True, exist_ok=True)
    
    if not os.path.exists(PUT_DIRECTORY):
        Path(PUT_DIRECTORY).mkdir(parents=True, exist_ok=True)


    try:
        os.system('sudo python3 main.py &')
    except:
        print("Error startin server")
        exit()
    print("HTTP server started")

def stop():
    if os.path.getsize("app.pid") == 0:
        print("Server is not running")
        exit()
    print("Stoping HTTP server")
    with open("app.pid", "r") as file:
        PID = file.read()
        os.system(f'kill {PID}')
    fp = open("app.pid", "w").close()
    print("HTTP server stopped")


def main():
    if len(sys.argv) != 2:
        print("Usage: ./run [start | stop | restart]")

    else:
        operation = sys.argv[1]
        if operation not in ["start", "stop", "restart"]:
            print("Usage: ./run [start | stop | restart ]")
        else:
            if operation == "start":
                start()

            elif operation == "stop":
                stop()


            elif operation == "restart":
                stop()
                start()

if __name__ == "__main__":
    main()