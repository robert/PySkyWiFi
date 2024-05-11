from .base26 import b26_decode, b26_encode
from typing import Tuple
import json
import time
from abc import ABC, abstractmethod

import httpx


def b26_decode_with_prefix(inp: str) -> Tuple[str, str]:
    return (inp[0], b26_decode(inp[1:]))


class Transport(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def write_str(self, inp: str, prefix: str):
        pass

    @abstractmethod
    def read_str(self) -> Tuple[str, str]:
        pass


class DiscordTransport(Transport):

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    
    def connect(self):
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

    def write_str(self, inp: str, prefix: str):
        headers = {"Authorization": self._token}
        data = {"bio": prefix + b26_encode(inp)}

        response = httpx.patch("https://discord.com/api/v9/users/@me/profile", headers=headers, cookies=self._cookies, json=data)
        response.raise_for_status()

    def read_str(self) -> Tuple[str, str]:
        headers = {'Authorization': self._token}

        response = httpx.get(f'https://discord.com/api/v9/users/{self._user_id}/profile', headers=headers, cookies=self._cookies)
        response.raise_for_status()

        return b26_decode_with_prefix(response.json()['user']['bio'])


class FileTransport(Transport):

    def __init__(self, fpath: str):
        self.fpath = fpath

    def connect(self):
        pass

    def write_str(self, inp: str, prefix: str):
        b26 = b26_encode(inp)
        with open(self.fpath, 'w') as f:
            f.write(prefix + b26)

    def read_str(self) -> Tuple[str, str]:
        with open(self.fpath) as f:
            full_v = f.read()
            return (full_v[0], b26_decode(full_v[1:]))


class Protocol:

    def __init__(self, transport: Transport, my_id: str, their_id: str):
        if not self._is_id_valid(my_id):
            raise Exception(f"Invalid my_id: {my_id}")
        if not self._is_id_valid(their_id):
            raise Exception(f"Invalid their_id: {their_id}")
        
        self.transport = transport
        self.my_id = my_id
        self.their_id = their_id

    def connect(self):
        self.transport.connect()

    def write_str(self, inp):
        self.transport.write_str(inp, self.my_id)

    def read_str_blocking(self) -> Tuple[str, str]:
        while True:
            prefix, v = self.transport.read_str()
            if prefix == self.their_id:
                return v
            time.sleep(1)

    def read_str_nonblocking(self) -> str | None:
        prefix, v = self.transport.read_str()
        if prefix == self.their_id:
            return v
        else:
            return None
        
    def _is_id_valid(self, id: str):
        return len(id) == 1
   

def stock_ticker_server(protocol: Protocol, default_ticker: str):
    protocol.connect()

    ticker = default_ticker
    while True:
        v = protocol.read_str_nonblocking()
        if v:
            ticker = v

        r = httpx.get(f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}")
        if r.status_code == 200:
            price = r.json()['chart']['result'][0]['meta']['regularMarketPrice']
            data = {"ticker": ticker, "price": price}
        else:
            data = {"error": r.text}

        protocol.write_str(json.dumps(data))

        time.sleep(5)


def chat(protocol: Protocol):
    protocol.connect()

    while True:
        my_msg = input("ME: ")
        protocol.write_str(my_msg)

        their_msg = protocol.read_str_blocking()
        print(f"THEM: {their_msg}")


def stock_ticker_client(protocol: str, default_ticker: str):
    protocol.connect()

    ticker = default_ticker
    while True:
        v = input(f"ENTER NEW TICKER (or press enter to stick with {ticker}): ")
        if v:
            ticker = v
        protocol.write_str(ticker)

        their_msg = protocol.read_str_blocking()
        print(f"RESPONSE: {their_msg}")
        time.sleep(5)
