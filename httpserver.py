
"""
    Implements a simple HTTP/1.0 Server
"""

import socket

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

# Define socket host and port

SERVER_HOST = '0.0.0.0'
SERVER_PORT = int(args.port)

# Initialize socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((SERVER_HOST, SERVER_PORT))

server_socket.listen(1)

print('Listening on port %s ... ' % SERVER_PORT)

while True:
    # Wait for client connection
    client_connection, client_address = server_socket.accept()

    # Get the client request
    request = client_connection.recv(1024).decode()
    print(request)

    # Parse HTTP headers
    headers = request.split('\n')
    filename = headers[0].split()[1]

    print(filename)

    # Get the contents of the file
    if filename == '/':
        filename = '/index.html'

    try:
        fin = open('public' + filename)
        content = fin.read()
        fin.close()

        response = 'HTTP/1.0 200 OK\n\n' + content

    except IOError:

        response = 'HTTP/1.0 404 NOT FOUND\n\n File Not Found'

    # Send HTTP response
    client_connection.sendall(response.encode())
    client_connection.close()

# Close socket
server_socket.close()


