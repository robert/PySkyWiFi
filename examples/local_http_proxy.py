from PySkyWiFi import FileTransport, GithubTransport, TransportProtocol
from PySkyWiFi.local_http_proxy import run_local_http_proxy


if __name__ == "__main__":
    tp = TransportProtocol(
        send_pipe=FileTransport(fpath="/tmp/1"),
        rcv_pipe=FileTransport(fpath="/tmp/2") #GithubTransport(),
    )

    run_local_http_proxy(tp)