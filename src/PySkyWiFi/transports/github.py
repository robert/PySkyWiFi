import github
from PySkyWiFi import Transport
from PySkyWiFi.base26 import b26_decode, b26_encode
from PySkyWiFi.transports import load_config


class GithubTransport(Transport):

    def __init__(self, gist_id: str, token: str, segment_data_size: int=30, sleep_for: float=0.5):
        self.gist_id = gist_id
        self.token = token

        self._segment_data_size = segment_data_size
        self._sleep_for = sleep_for

    @staticmethod
    def from_conf(block_id: int, segment_data_size: int=30, sleep_for: float=0.5) -> "GithubTransport":
        conf = load_config()
        block = conf["github"][block_id]

        return GithubTransport(block["gist_id"], block["token"], segment_data_size, sleep_for)

    def send(self, inp):
        g = github.Github(self.token)
        gist = g.get_gist(self.gist_id)

        filename = list(gist.files)[0]
        updated_content = b26_encode(inp)
        gist.edit(
            files={filename: github.InputFileContent(content=updated_content)}
        )

    def recv(self) -> str:
        g = github.Github(self.token)
        gist = g.get_gist(self.gist_id)

        filename = list(gist.files)[0]
        file_content = gist.files[filename].content
        return b26_decode(file_content)
    
    def sleep_for(self):
        return self._sleep_for
         
    def segment_data_size(self) -> int:
        return self._segment_data_size