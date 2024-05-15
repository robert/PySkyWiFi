import sys

from PySkyWiFi import Protocol
from PySkyWiFi.transports.file import FileTransport
from PySkyWiFi.transports.github import GithubTransport
from PySkyWiFi.transports.united_airlines import UnitedAirlinesTransport
from PySkyWiFi.http.remote_daemon import run


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "github":
        print("Using GithubTransport...")
        p = Protocol(
            send_pipe=GithubTransport.from_conf(2),
            rcv_pipe=GithubTransport.from_conf(1),
        )
    else:
        print("Using FileTransport...")
        p = Protocol(
            send_pipe=FileTransport(fpath="/tmp/2"),
            rcv_pipe=FileTransport(fpath="/tmp/1")  # UnitedAirlinesTransport.from_conf(1),
        )
    run(p)