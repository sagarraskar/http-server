# Installation
## For linux

Create a virtual environment
$ python3 -m venv venv

Activate the virtual environment
$ source ./venv/bin/activate

Install required modules
$ pip3 install -e .

# Starting Server
Run the command
$ sudo ./run.py start

# Stop Server
Run the command
$ sudo ./run.py stop

# Restart Server
$ sudo ./run.py restart

# To configure server
edit the file /etc/httpserver/server.conf

# Log files
log files are stored in /var/log/httpserver by default

# Document Root
Document Root is /var/www/html2 by default
