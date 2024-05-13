import os
from PySkyWiFi import Transport
from PySkyWiFi.base26 import b26_decode, b26_encode


class FileTransport(Transport):

    def __init__(self, fpath: str, segment_data_size: int = 50, sleep_for: float=0.1):
        self.fpath = fpath
        self._segment_data_size = segment_data_size
        self._sleep_for = sleep_for

    def send(self, inp: str):
        with open(self.fpath, 'w') as f:
            f.write(b26_encode(inp))

    def recv(self) -> str:
        if not os.path.exists(self.fpath):
            return ""
        with open(self.fpath) as f:

            return b26_decode(f.read())

    def sleep_for(self):
        return self._sleep_for

    def segment_data_size(self) -> int:
        return self._segment_data_size
