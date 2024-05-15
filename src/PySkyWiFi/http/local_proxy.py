import socket

from PySkyWiFi import Protocol


def receive_http_request(recv):
    request_data = ""
    while True:
        chunk = recv()
        if not chunk:
            break
        request_data += chunk

        if "\r\n\r\n" in request_data:
            headers, rest = request_data.split('\r\n\r\n', 1)
            if 'Content-Length: ' in headers:
                content_length = int(headers.split('Content-Length: ')[1].split('\r\n')[0])
                while len(rest) < content_length:
                    rest += recv()
            request_data = headers + '\r\n\r\n' + rest
            break
    return request_data


def receive_http_response(recv):
    response_data = ""
    while True:
        chunk = recv()
        if not chunk:
            break
        response_data += chunk
        if "\r\n\r\n" in response_data:
            headers, rest = response_data.split('\r\n\r\n', 1)

            if 'Content-Length: ' in headers:
                content_length = int(headers.split('Content-Length: ')[1].split('\r\n')[0])
                while len(rest) < content_length:
                    rest += recv()
                response_data = headers + '\r\n\r\n' + rest
                break
            elif 'Transfer-Encoding: chunked' in headers:
                while True:
                    if '\r\n' in rest:
                        size_hex, rest = rest.split('\r\n', 1)
                        size = int(size_hex, 16)
                        if size == 0:
                            break
                        while len(rest) < size:
                            rest += recv()
                        rest = rest[size:]
                        if '\r\n' in rest:
                            rest = rest.split('\r\n', 1)[1]
                response_data = headers + '\r\n\r\n' + rest
                break
    return response_data


def run(protocol: Protocol, port: int=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen(1)
    print("Server is listening on port 8080...")

    try:
        while True:
            client_connection, _ = server_socket.accept()
            request_data = receive_http_request(lambda: client_connection.recv(1024).decode('utf-8'))

            try:
                protocol.connect()

                protocol.send(request_data)
                res = receive_http_response(protocol.recv_and_sleep)
                client_connection.send(res.encode('utf-8'))
                client_connection.close()
            finally:
                protocol.close()
    finally:
        server_socket.close()
        client_connection.close()


