import sys

from PySkyWiFi import FileTransport, Protocol, stock_ticker_server, stock_ticker_client

"""
From one machine (or terminal):

    python3 examples/stock_tickers.py server

From another machine (or termianl):

    python3 examples/stock_tickers.py client
"""

file_transport = FileTransport(
    fpath="/tmp/chat.txt",
)

if sys.argv[1] == "server":
    protocol = Protocol(
        transport=file_transport,
        my_id="s",
        their_id="c"
    )
    stock_ticker_server(protocol, "^GSPC")
else:
    protocol = Protocol(
        transport=file_transport,
        my_id="c",
        their_id="s"
    )
    stock_ticker_client(protocol, "^GSPC")
