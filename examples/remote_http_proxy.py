from PySkyWiFi import FileTransport, GithubTransport, TransportProtocol
from PySkyWiFi.remote_http_proxy import run_remote_http_proxy


if __name__ == "__main__":
    tp = TransportProtocol(
        send_pipe=FileTransport(fpath="/tmp/2"), #GithubTransport(),
        rcv_pipe=FileTransport(fpath="/tmp/1"),
    )
    run_remote_http_proxy(tp)