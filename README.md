# PySkyWiFi

```
# On the ground
python3 examples/remote_http_proxy.py

# In the air
python3 examples/local_http_proxy.py
curl localhost:8080 -H "X-PySkyWiFi: https://cat.ninja/fact"
```

## Transports

* `FileTransport`
* `DiscordTransport`
* `GithubTransport`
* `VirginAtlanticTransport`