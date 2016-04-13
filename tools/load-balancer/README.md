This is for managing a load balancer (only nginx is supported at the moment) in
front of Hue. Every 60 seconds it asks Cloudera if there has been any changes
to the number of Hue servers. If so, it signals the the load balancer to add or
remove those machines from the pool. To use it, you first must copy and edit

* `etc/nginx.conf.example` -> `etc/nginx.conf`
* `etc/monitor-hue-lb.conf.example` -> `etc/monitor-hue-lb.conf`

Then, some dependencies must be installed with:

```
% pip install -r requirements.txt
```

If you want to use virtualenv, you can do:

```
% virtualenv build
% export PATH=$PATH:build/`pwd`/bin/activate
```

Finally, to start the load balancer, run:

```
% ./bin/supervisord
```

By default the load balancer is setup on `http://localhost:8000`, so access
that URL and see if it works for you.
