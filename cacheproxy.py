
"""
    Implements a simple cache proxy
"""

import socket

from urllib2 import Request, urlopen, HTTPError

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

print('Cache proxy is listening on port %s ...' % SERVER_PORT)

while True:
    # Wait for client connection
    client_connection, client_address = server_socket.accept()

    # Get the client request
    request = client_connection.recv(1024).decode()
    print(request)

    # Parse HTTP headers
    headers = request.split('\n')

    top_header = headers[0].split()
    method = top_header[0]
    filename = top_header[1]

    # Index check
    if filename == '/':
        filename = '/index.html'

    # Let's try to read the file locally

    try:
        # Check if we have this file locally
        fin = open('cache' + filename)
        content = fin.read()
        fin.close()

        # If we have it, let's send it
        print('Got from cache.')
        response = 'HTTP/1.0 200 OK\n\n' + content

    except IOError:

        # Don't have it. Have to fetch from cache
        print('Not in cache. Fetching from server.')

        # Create url
        url = 'http://127.0.0.1:8000' + filename
        q = Request(url)

        try:
            # Send req to server and get response
            response = urlopen(q)

            # Grab the header and content from the server req
            response_headers = response.info()
            content = response.read()

            cached_file = open('cache' + filename, 'w')
            cached_file.write(content)
            cached_file.close()

            response = 'HTTP/1.0 200 OK\n\n' + content

        except HTTPError:

            response = 'HTTP/1.0 404 NOT FOUND\n\n File Not Found'

    client_connection.sendall(response.encode())
    client_connection.close()

# Close socket
server_socket.close()

