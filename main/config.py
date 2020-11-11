import configparser

config = configparser.ConfigParser()
config.read("/etc/httpserver/server.conf")

# DOCUMENT_ROOT = "/var/www/html"
# SERVER_PORT = 8092
# POST_DIRECTORY =  "/post"
# PUT_DIRECTORY = "/put"
# LOG_DIRECTORY = "/var/log/httpserver"
# ACCESS_LOG_FILE = "access.log"
# ERROR_LOG_FILE = "error.log"
# POST_LOG_FILE = "post.log"

# MAX_CONNECTIONS = 5

DOCUMENT_ROOT = config["SERVER"]["DOCUMENT_ROOT"]
SERVER_PORT = int(config["SERVER"]["SERVER_PORT"])
POST_DIRECTORY =  config["SERVER"]["POST_DIRECTORY"]
PUT_DIRECTORY = config["SERVER"]["PUT_DIRECTORY"]
LOG_DIRECTORY = config["LOG"]["LOG_DIRECTORY"]
ACCESS_LOG_FILE = config["LOG"]["ACCESS_LOG_FILE"]
ERROR_LOG_FILE = config["LOG"]["ERROR_LOG_FILE"]
POST_LOG_FILE = config["LOG"]["POST_LOG_FILE"]

MAX_CONNECTIONS = int(config["CONNECTION"]["MAX_CONNECTIONS"])
