from typing import Any
import time
from abc import ABC, abstractmethod


class Transport(ABC):

    @abstractmethod
    def send(self, inp: str):
        pass

    @abstractmethod
    def recv(self) -> str:
        pass

    @abstractmethod
    def segment_data_size(self) -> int:
        pass

    @abstractmethod
    def sleep_for(self) -> float:
        pass

    def connect_send(self):
        pass

    def connect_recv(self):
        self.send(build_connected_segment())

    def is_ready(self) -> bool:
        segment = parse_segment(self.recv())
        return segment["type"] != "END_MESSAGE"

    def close(self):
        self.send(build_end_segment())


class Protocol:

    def __init__(self, send_pipe, rcv_pipe):
        self.send_pipe = send_pipe
        self.rcv_pipe = rcv_pipe
        self.my_seq_number = 0
        self.my_ack_number = -1
        self.their_ack_number = -1

    def connect(self):
        self.send_pipe.connect_send()
        self.rcv_pipe.connect_recv()

    def close(self):
        self.rcv_pipe.close()

    def send(self, inp):
        segment_data_size = self.send_pipe.segment_data_size()
        while True:
            if self.send_pipe.is_ready():
                break
            time.sleep(self.send_pipe.sleep_for())

        for start in range(0, len(inp), segment_data_size):
            segment_data = inp[start:start+segment_data_size]
            segment = build_data_segment(self.my_seq_number, segment_data)
            self.send_pipe.send(segment)
            self.my_seq_number += 1

            while True:
                raw = self.rcv_pipe.recv()
                if raw:
                    segment = parse_segment(raw)
                    if segment["type"] == "ACK":
                        if segment["ack_number"] > self.their_ack_number:
                            self.their_ack_number = segment["ack_number"]
                            break
                time.sleep(self.send_pipe.sleep_for())

        self.send_pipe.send(build_end_segment())

    def recv(self) -> str:
        while True:
            raw = self.rcv_pipe.recv()
            if raw:
                segment = parse_segment(raw)
                if segment["type"] == "DATA":
                    if segment["seq_number"] > self.my_ack_number:
                        self.my_ack_number = segment["seq_number"]

                        ack_segment = build_ack_segment(self.my_ack_number)
                        self.send_pipe.send(ack_segment)

                        return segment["data"]

                elif segment["type"] == "END_MESSAGE":
                    return ""
            time.sleep(self.rcv_pipe.sleep_for())

    def recv_and_sleep(self) -> str:
        d = self.recv()
        time.sleep(self.rcv_pipe.sleep_for())
        return d


def build_data_segment(seq_number: int, data: str) -> str:
    seg_type = "D"
    padded_seq = f"{seq_number:06}"
    return seg_type + padded_seq + data


def build_ack_segment(ack_number: int) -> str:
    seg_type = "A"
    padded_ack = f"{ack_number:06}"
    return seg_type + padded_ack


def build_connected_segment() -> str:
    return "C"


def build_end_segment() -> str:
    return "E"


def parse_segment(raw: str) -> dict[str, Any]:
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
    else:
        return {
            "type": "UNKNOWN"
        }
