import sys

from PySkyWiFi import DiscordTransport, Protocol, chat

"""
From one machine (or terminal):

    python3 examples/chat.py 0

From another machine (or termianl):

    python3 examples/chat.py 1
"""

discord_transport = DiscordTransport(
    username=YOUR_DISCORD_USERNAME_GOES_HERE,
    password=YOUR_DISCORD_PASSWORD_GOES_HERE,
)

if sys.argv[1] == "1":
    protocol = Protocol(
        transport=discord_transport,
        my_id="a",
        their_id="b"
    )
    chat(protocol)
else:
    protocol = Protocol(
        transport=discord_transport,
        my_id="b",
        their_id="a"
    )
    chat(protocol)
