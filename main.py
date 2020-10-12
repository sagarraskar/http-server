import socket

host = "127.0.0.1"
port = 8080


listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_addr = (host, port)
listening_socket.bind(server_addr)

listening_socket.listen(1)
print(f'Server listening on {host}:{port}')
while True:
    client_connection, client_addr = listening_socket.accept()
    request = client_connection.recv(1024).decode('utf-8')

    print('Request :')
    print(request)
    response = """
HTTP/1.1 200 OK

<html>
<head>
<title>HTTP SERVER</title>
</head>
<body>
<b>Hello World</b>
</body>
</html>
"""
    client_connection.send(response.encode('utf-8'))
    client_connection.close()