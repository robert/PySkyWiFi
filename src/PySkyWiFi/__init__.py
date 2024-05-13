from .base26 import b26_decode, b26_encode
from typing import Tuple
import yaml
import time
from abc import ABC, abstractmethod
import os

import github

import httpx


CONFIG_PATH = os.path.expanduser("~/.PySkyWiFi")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


class Transport(ABC):

    @abstractmethod
    def write(self, inp: str):
        pass

    @abstractmethod
    def recv(self) -> str:
        pass

    @abstractmethod
    def segment_data_size(self):
        pass

    @abstractmethod
    def sleep_for(self):
        pass

    def connect_write(self):
        pass

    def connect_recv(self):
        self.write(build_connected_segment())

    def is_ready(self) -> bool:
        segment = parse_segment(self.recv())
        return segment["type"] != "END_MESSAGE"
    
    def disconnect(self):
        self.write(build_end_segment())


class GithubTransport(Transport):

    def __init__(self, gist_id: str=None, token: str=None, segment_data_size: int=30, sleep_for: float=0.5):
        conf = load_config()

        self.gist_id = gist_id or conf["github"]["gist_id"]
        self.token = token or conf["github"]["token"]

        self._segment_data_size = segment_data_size
        self._sleep_for = sleep_for

    def write(self, inp):
        g = github.Github(self.token)
        gist = g.get_gist(self.gist_id)

        filename = list(gist.files)[0]
        updated_content = b26_encode(inp)
        gist.edit(
            files={filename: github.InputFileContent(content=updated_content)}
        )

    def recv(self):
        g = github.Github(self.token)
        gist = g.get_gist(self.gist_id)

        filename = list(gist.files)[0]
        file_content = gist.files[filename].content
        return b26_decode(file_content)
    
    def sleep_for(self):
        return self._sleep_for
         
    def segment_data_size(self):
        return self._segment_data_size


class DiscordTransport(Transport):

    def __init__(self, username: str, password: str, segment_data_size: int=15, sleep_for: float=1.0):
        self.username = username
        self.password = password
        self._segment_data_size = segment_data_size
        self._sleep_for = sleep_for
        self._token = None
    
    def connect_write(self):
        self._auth()

    def connect_recv(self):
        self._auth()
        super()

    def is_ready(self):
        return self._token and super()

    def write(self, inp: str):
        headers = {"Authorization": self._token}
        data = {"bio": inp}

        response = httpx.patch("https://discord.com/api/v9/users/@me/profile", headers=headers, cookies=self._cookies, json=data)
        response.raise_for_status()

    def recv(self) -> str:
        headers = {'Authorization': self._token}

        response = httpx.get(f'https://discord.com/api/v9/users/{self._user_id}/profile', headers=headers, cookies=self._cookies)
        response.raise_for_status()

        return response.json()['user']['bio']
    
    def sleep_for(self):
        return self.sleep_for
        
    def segment_data_size(self):
        return self._segment_data_size
    
    def _auth(self):
        data = {
            'login': self.username,
            'password': self.password,
        }
        response = httpx.post('https://discord.com/api/v9/auth/login', json=data)
        response.raise_for_status()

        res_data = response.json()

        self._cookies = response.cookies
        self._user_id = res_data['user_id']
        self._token = res_data['token']


class FileTransport(Transport):

    def __init__(self, fpath: str, segment_data_size: int = 50, sleep_for: float=0.1):
        self.fpath = fpath
        self._segment_data_size = segment_data_size
        self._sleep_for = sleep_for

    def write(self, data: str):
        with open(self.fpath, 'w') as f:
            f.write(b26_encode(data))

    def recv(self) -> str:
        if not os.path.exists(self.fpath):
            return None
                          
        with open(self.fpath) as f:
            return b26_decode(f.read())
        
    def sleep_for(self):
        return self._sleep_for
    
    def segment_data_size(self):
        return self._segment_data_size


class TransportProtocol:

    def __init__(self, send_pipe, rcv_pipe):
        self.send_pipe = send_pipe
        self.rcv_pipe = rcv_pipe
        self.my_seq_number = 0
        self.my_ack_number = -1
        self.their_ack_number = -1

    def connect(self):
        self.send_pipe.connect_write()
        self.rcv_pipe.connect_recv()

    def disconnect(self):
        self.rcv_pipe.disconnect()

    def write(self, inp):
        segment_data_size = self.send_pipe.segment_data_size()
        while True:
            if self.send_pipe.is_ready():
                break
            time.sleep(self.send_pipe.sleep_for())

        for start in range(0, len(inp), segment_data_size):
            segment_data = inp[start:start+segment_data_size]
            segment = build_data_segment(self.my_seq_number, segment_data)
            self.send_pipe.write(segment)
            self.my_seq_number += 1

            while True:
                raw = self.rcv_pipe.recv()
                if raw:
                    segment = parse_segment(raw)
                    if segment["type"] == "ACK":
                        if segment["ack_number"] > self.their_ack_number:
                            self.their_ack_number = segment["ack_number"]
                            print(segment_data)
                            break
                time.sleep(self.send_pipe.sleep_for())

        self.send_pipe.write(build_end_segment())

    def recv(self) -> str:
        while True:
            raw = self.rcv_pipe.recv()
            if raw:
                segment = parse_segment(raw)
                if segment["type"] == "DATA":
                    if segment["seq_number"] > self.my_ack_number:
                        self.my_ack_number = segment["seq_number"]
                        
                        ack_segment = build_ack_segment(self.my_ack_number)
                        self.send_pipe.write(ack_segment)
                        print(segment["data"])

                        return segment["data"]

                elif segment["type"] == "END_MESSAGE":
                    return ""
            time.sleep(self.rcv_pipe.sleep_for())

    def recv_and_sleep(self) -> str:
        d = self.recv()
        time.sleep(self.rcv_pipe.sleep_for())
        return d


def build_data_segment(seq_number: int, data: str):
    seg_type = "D"
    padded_seq = f"{seq_number:06}"
    return seg_type + padded_seq + data


def build_ack_segment(ack_number: int):
    seg_type = "A"
    padded_ack = f"{ack_number:06}"
    return seg_type + padded_ack


def build_connected_segment():
    return "C"


def build_end_segment():
    return "E"


def parse_segment(raw: str):
    segment_type = raw[0]

    if segment_type == "D":
        seq_number = int(raw[1:7])
        body = raw[7:]
        return {
            "type": "DATA",
            "seq_number": seq_number,
            "data": body,
        }
    elif segment_type == "A":
        ack_number = int(raw[1:])
        return {
            "type": "ACK",
            "ack_number": ack_number,
        }
    elif segment_type == "C":
        return {
            "type": "CONNECTED"
        }
    elif segment_type == "E":
        return {
            "type": "END_MESSAGE"
        }
