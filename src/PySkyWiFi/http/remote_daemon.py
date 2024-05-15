from urllib.parse import urlparse

from PySkyWiFi import Protocol
from PySkyWiFi.http.local_proxy import receive_http_request

import httpx
from httpx import Request


def parse_request(request_data):
    """Parse the raw HTTP request data into components."""
    headers = {}
    lines = request_data.split('\r\n')
    request_line = lines[0]
    method, full_path, _ = request_line.split()
    url_parts = full_path.split('://', 1)[-1].split('/', 1)
    host = url_parts[0].split(':')[0]
    path = '/' + url_parts[1] if len(url_parts) > 1 else '/'
    scheme = 'https' if '443' in url_parts[0] else 'http'

    i = 1
    while lines[i] and ':' in lines[i]:
        key, value = lines[i].split(':', 1)
        headers[key.strip()] = value.strip()
        i += 1
    body = '\r\n'.join(lines[i+1:])

    return method, scheme, host, path, headers, body


def send_http_request(request_data):
    method, _, _, _, headers, body = parse_request(request_data)
    url = headers["X-PySkyWiFi"]
    headers["Host"] = urlparse(url).hostname

    with httpx.Client() as client:
        request = Request(method, url, headers=headers, content=body.encode())
        response = client.send(request)

        headers = "\r\n".join(f'{key}: {value}' for key, value in response.headers.items() if key != "transfer-encoding")
        response = f"""HTTP/1.1 {response.status_code} {response.reason_phrase}\r\n""" + headers + "\r\n\r\n" + response.text + "\r\n\r\n"

        return response


def run(protocol: Protocol):
    while True:
        try:
            protocol.connect()

            req = receive_http_request(protocol.recv_and_sleep)
            res = send_http_request(req)
            protocol.send(res)
        finally:
            protocol.close()
