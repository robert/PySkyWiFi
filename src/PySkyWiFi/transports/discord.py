import httpx
from PySkyWiFi import Transport
from PySkyWiFi.transports import load_config


class DiscordTransport(Transport):

    def __init__(self, username: str | None=None, password: str | None=None, segment_data_size: int=15, sleep_for: float=1.0):
        conf = load_config()

        self.username = username or conf["discord"]["username"]
        self.password = password or conf["discord"]["password"]

        self._segment_data_size = segment_data_size
        self._sleep_for = sleep_for
        self._token = None

    def connect_send(self):
        self._auth()

    def connect_recv(self):
        self._auth()
        super()

    def is_ready(self) -> bool:
        return self._token is not None and super().is_ready()

    def send(self, inp: str):
        headers = {"Authorization": self._token}
        data = {"bio": inp}

        response = httpx.patch("https://discord.com/api/v9/users/@me/profile", headers=headers, cookies=self._cookies, json=data)
        response.raise_for_status()

    def recv(self) -> str:
        headers = {'Authorization': self._token}

        response = httpx.get(f'https://discord.com/api/v9/users/{self._user_id}/profile', headers=headers, cookies=self._cookies)
        response.raise_for_status()

        return response.json()['user']['bio']

    def sleep_for(self) -> float:
        return self._sleep_for

    def segment_data_size(self) -> int:
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
