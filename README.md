# PySkyWiFi

Completely free, unbelievably stupid wi-fi on long-haul flights. Tunnel the entire internet through the "name" field on your airmiles account.

## Usage

```
# On the ground
python3 examples/remote_http_daemon.py

# In the air
python3 examples/local_http_proxy.py
curl localhost:8080 -H "X-PySkyWiFi: https://cat.ninja/fact"
```

NB: don't actually do this

## A story

The plane reached 10,000ft. I connected my laptop to the wi-fi. The network login page encouraged me to sign in to my airmiles account, free of charge, even though I hadn't yet paid for any internet. A hole in the firewall, I thought. It's a long way from London to San Francisco so I decided to stick my finger in and wiggle it around.

I logged in to my JetStreamers Diamond Altitude account and started clicking. I went to my profile page. I saw an edit button. It looked like a normal button: drop shadow, rounded corners, nothing special. I was supposed to use it to update my name, address, and so on.

But suddenly I realised that this was no ordinary button. This clickable rascal would allow me to access the entire internet through my airmiles account. This would be slow. It would be unbelievably stupid. But it would work.

Several co-workers were asking me to review their PRs because my feedback was "two weeks late" and "blocking a critical deployment." But my ideas are important too so I put on my headphones and smashed on some focus tunes. I'd forgotten to charge my headphones so Limp Bizkit started playing out of my laptop speakers. Fortunately no one else on the plane seemed to mind so we all rocked out together.

Before I could access the entire internet through my airmiles account I'd need to write a few prototypes. At first I thought that I'd write them using Go, but then I realised that if I used Python then I could call the final tool [`PySkyWiFi`](https://github.com/robert/PySkyWiFi). Obviously I did that instead.

*Read the rest of [the blog post](https://robertheaton.com/pyskywifi) for more details...*