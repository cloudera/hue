Scripts to stress test various parts of hue using
[wrk](https://github.com/wg/wrk). Follow
[these instructions](https://github.com/wg/wrk/wiki/Installing-Wrk-on-Linux)
to install `wrk`.

Usage
-----

To run:

```
% env LUA_PATH='./?.lua' wrk \
  -s ./stress-hue.lua \
  --duration 30s \
  --threads 5 \
  --connections 10 \
  --timeout 5s \
  --latency \
  http://localhost:8000/about \
  -- \
  --session 1234...
```

This will start 5 threads each accessing that URL 2 at a time (connections /
threads) for 30 seconds, with the sockets timing after 5 seconds if there's a
problem with the specified session cookie. Once finished, `wrk` will print out
the latency statistics:

```
Running 30s test @ http://localhost:8000/about
  5 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   692.50ms  180.14ms 983.15ms   80.90%
    Req/Sec     6.59     17.64   111.00     88.79%
  Latency Distribution
     50%  779.78ms
     75%  779.78ms
     90%  779.78ms
     99%  779.78ms
  902 requests in 30.02s, 37.89MB read
  Socket errors: connect 0, read 1, write 0, timeout 0
Requests/sec:     30.05
Transfer/sec:      1.26MB
```

If instead you want to create a unique user for each thread, you can use Hue's
demo mode by adding this to the `hue.ini`:

```
[desktop]
...
demo=true
...
```

Then just remove the `--session ...` argument.
