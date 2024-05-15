# PySkyWiFi

```
# On the ground
python3 examples/remote_http_daemon.py

# In the air
python3 examples/local_http_proxy.py
curl localhost:8080 -H "X-PySkyWiFi: https://cat.ninja/fact"
```

## Transports

* `FileTransport`
* `DiscordTransport`
* `GithubTransport`
* `UnitedAirlinesTransport`


How to use PySkyWiFi yourself

TODO: move to the repo

NB. do not use `PySkyWiFi` yourself. It is very stupid and probably a little illegal. I cannot stress this enough. Do not use `PySkyWiFi` (if you must then you can use it [in devmode][TODO]).

Hypothetically speaking though, you would:

1. Find a computer on the ground that you can leave running while you are flying. This could be a desktop computer, or a machine in the cloud.
1. On this machine, run `pip install PySkyWiFi`
2. Check whether `PySkyWiFi` supports your airline. If it doesn't, implement a new network layer using your airline's airmiles account (actually very easy, see [this guide][TODO] for pointers)
3. Sign up for two airmiles accounts with your airline
4. Create a config file at `~/.PySkyWiFi` and add the credentials for your airmiles accounts (see [this guide][TODO] for the schema)
5. Start the ground daemon using `XXX`

Then you would switch to the laptop which will come onto the plane with you. You would:

6. `pip install PySkyWiFi` again
7. Copy over the code that you wrote in step TODO to allow PySkyWiFi to work with your airline
8. Create the same credential config file at `~/.PySkyWiFi`

Finally, once you got on the plane you would:

9. Start the sky proxy using `XXX`
10. Run `curl localhost:1234 -H "X-PySkyWiFi: https://cat.ninja/fact"`
11. Wait for several minutes, possibly much longer
12. Hopefully you will eventually see a response
