
"""
    Implements a simple cache proxy
"""

import socket
from urllib.request import Request, urlopen, HTTPError
import argparse


def main():
    # Get port command line argument
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

        # Get the file
        content = fetch_file(filename)

        # If we have the file, return it, otherwise 404
        if content:
            response = 'HTTP/1.0 200 OK\n\n' + content
        else:
            response = 'HTTP/1.0 404 NOT FOUND\n\n File Not Found'

        # Send the response and close the connection
        client_connection.sendall(response.encode())
        client_connection.close()

    # Close socket
    server_socket.close()


def fetch_file(filename):
    # Let's try to read the file locally first
    file_from_cache = fetch_from_cache(filename)

    if file_from_cache:
        print('Fetched successfully from cache.')
        return file_from_cache
    else:
        print('Not in cache. Fetching from server.')
        file_from_server = fetch_from_server(filename)

        if file_from_server:
            save_in_cache(filename, file_from_server)
            return file_from_server
        else:
            return None


def fetch_from_cache(filename):
    try:
        # Check if we have this file locally
        fin = open('cache' + filename)
        content = fin.read()
        fin.close()
        # If we have it, let's send it
        return content
    except IOError:
        return None


def fetch_from_server(filename):
    url = 'http://127.0.0.1:8000' + filename
    q = Request(url)

    try:
        response = urlopen(q)
        # Grab the header and content from the server req
        response_headers = response.info()
        content = response.read().decode('utf-8')
        return content
    except HTTPError:
        return None


def save_in_cache(filename, content):
    print('Saving a copy of {} in the cache'.format(filename))
    cached_file = open('cache' + filename, 'w')
    cached_file.write(content)
    cached_file.close()

if __name__ == '__main__':
    main()
