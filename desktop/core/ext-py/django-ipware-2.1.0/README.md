Django IPware
====================

**A Django application to retrieve client's IP address**

[![status-image]][status-link]
[![version-image]][version-link]
[![coverage-image]][coverage-link]

Overview
====================

**Best attempt** to get client's IP address while keeping it **DRY**.

Notice
====================

There is not a good `out-of-the-box` solution against fake IP addresses, aka `IP Address Spoofing`.
You are encouraged to read the ([Advanced users](README.md#advanced-users)) section of this page and
use `trusted_proxies_ips` and/or `proxy_count` features to match your needs, especially `if` you are
planning to include `ipware` in any authentication, security or `anti-fraud` related architecture.


How to install
====================

    1. easy_install django-ipware
    2. pip install django-ipware
    3. git clone http://github.com/un33k/django-ipware
        a. cd django-ipware
        b. run python setup.py install
    4. wget https://github.com/un33k/django-ipware/zipball/master
        a. unzip the downloaded file
        b. cd into django-ipware-* directory
        c. run python setup.py install


How to use
====================

   ```python
    # In a view or a middleware where the `request` object is available

    from ipware import get_client_ip
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
       # Unable to get the client's IP address
    else:
        # We got the client's IP address
        if is_routable:
            # The client's IP address is publicly routable on the Internet
        else:
            # The client's IP address is private

    # Order of precedence is (Public, Private, Loopback, None)
   ```


Advanced users:
====================

- ### Precedence Order
The default meta precedence order is top to bottom.  However, you may customize the order
by providing your own `IPWARE_META_PRECEDENCE_ORDER` by adding it to your project's settings.py

   ```python
    # The default meta precedence order
    IPWARE_META_PRECEDENCE_ORDER = (
        'HTTP_X_FORWARDED_FOR', 'X_FORWARDED_FOR',  # <client>, <proxy1>, <proxy2>
        'HTTP_CLIENT_IP',
        'HTTP_X_REAL_IP',
        'HTTP_X_FORWARDED',
        'HTTP_X_CLUSTER_CLIENT_IP',
        'HTTP_FORWARDED_FOR',
        'HTTP_FORWARDED',
        'HTTP_VIA',
        'REMOTE_ADDR',
    )
   ```
**Alternativley**, you can provide your custom `request header meta precedence order` when calling `get_client_ip()`.
```python
get_client_ip(request, request_header_order=['X_FORWARDED_FOR'])
get_client_ip(request, request_header_order=['X_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR'])
```

- ### Private Prefixes

You may customize the prefixes to indicate an IP addresses private. This is done by adding your
own `IPWARE_PRIVATE_IP_PREFIX` to your project's settings.py.  IP addresses matching the following
prefixes are considered `private` & are **not** publicly routable.

   ```python
   # The default private IP prefixes
   IPWARE_PRIVATE_IP_PREFIX = getattr(settings,
      'IPWARE_PRIVATE_IP_PREFIX', (
        '0.',  # messages to software
        '10.',  # class A private block
        '100.64.',  '100.65.',  '100.66.',  '100.67.',  '100.68.',  '100.69.',
        '100.70.',  '100.71.',  '100.72.',  '100.73.',  '100.74.',  '100.75.',
        '100.76.',  '100.77.',  '100.78.',  '100.79.',  '100.80.',  '100.81.',
        '100.82.',  '100.83.',  '100.84.',  '100.85.',  '100.86.',  '100.87.',
        '100.88.',  '100.89.',  '100.90.',  '100.91.',  '100.92.',  '100.93.',
        '100.94.',  '100.95.',  '100.96.',  '100.97.',  '100.98.',  '100.99.',
        '100.100.', '100.101.', '100.102.', '100.103.', '100.104.', '100.105.',
        '100.106.', '100.107.', '100.108.', '100.109.', '100.110.', '100.111.',
        '100.112.', '100.113.', '100.114.', '100.115.', '100.116.', '100.117.',
        '100.118.', '100.119.', '100.120.', '100.121.', '100.122.', '100.123.',
        '100.124.', '100.125.', '100.126.', '100.127.',  # carrier-grade NAT
        '169.254.',  # link-local block
        '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.',
        '172.24.', '172.25.', '172.26.', '172.27.',
        '172.28.', '172.29.', '172.30.', '172.31.',  # class B private blocks
        '192.0.0.',  # reserved for IANA special purpose address registry
        '192.0.2.',  # reserved for documentation and example code
        '192.168.',  # class C private block
        '198.18.', '198.19.',  # reserved for inter-network communications between two separate subnets
        '198.51.100.',  # reserved for documentation and example code
        '203.0.113.',  # reserved for documentation and example code
        '224.', '225.', '226.', '227.', '228.', '229.', '230.', '231.', '232.',
        '233.', '234.', '235.', '236.', '237.', '238.', '239.',  # multicast
        '240.', '241.', '242.', '243.', '244.', '245.', '246.', '247.', '248.',
        '249.', '250.', '251.', '252.', '253.', '254.', '255.',  # reserved
      ) + (
        '::',  # Unspecified address
        '::ffff:', '2001:10:', '2001:20:'  # messages to software
        '2001::',  # TEREDO
        '2001:2::',  # benchmarking
        '2001:db8:',  # reserved for documentation and example code
        'fc00:',  # IPv6 private block
        'fe80:',  # link-local unicast
        'ff00:',  # IPv6 multicast
      )
  )
  ```

- ### Trusted Proxies

If your Django server is behind one or more known proxy server(s), you can filter out unwanted requests
by providing the `trusted` proxy list when calling `get_client_ip(request, proxy_trusted_ips=['177.139.233.133'])`.
In the following example, your load balancer (LB) can be seen as a `trusted` proxy.

   ```
    `Real` Client  <public> <---> <public> LB (Server) <private> <--------> <private> Django Server
                                                                      ^
                                                                      |
    `Fake` Client  <private> <---> <private> LB (Server) <private> ---^
   ```


   ```python
   # In the above scenario, use your load balancer's IP address as a way to filter out unwanted requests.
   client_ip, is_routable = get_client_ip(request, proxy_trusted_ips=['177.139.233.133'])

   # If you have multiple proxies, simply add them to the list
   client_ip, is_routable = get_client_ip(request, proxy_trusted_ips=['177.139.233.133', '177.139.233.134'])

   # For proxy servers with fixed sub-domain and dynamic IP, use the following pattern.
   client_ip, is_routable = get_client_ip(request, proxy_trusted_ips=['177.139.', '177.140'])
   client_ip, is_routable = get_client_ip(request, proxy_trusted_ips=['177.139.233.', '177.139.240'])
   ```

- ### Proxy Count

If your Django server is behind a `known` number of proxy server(s), you can filter out unwanted requests
by providing the `number` of proxies when calling `get_client_ip(request, proxy_count=1)`.
In the following example, your load balancer (LB) can be seen as the `only` proxy.

   ```
    `Real` Client  <public> <---> <public> LB (Server) <private> <--------> <private> Django Server
                                                                      ^
                                                                      |
                                          `Fake` Client  <private> ---^
   ```

   ```python
   # In the above scenario, the total number of proxies can be used as a way to filter out unwanted requests.
   client_ip, is_routable = get_client_ip(request, proxy_count=1)

   # The above may be very useful in cases where your proxy server's IP address is assigned dynamically.
   # However, If you have the proxy IP address, you can use it in combination to the proxy count.
   client_ip, is_routable = get_client_ip(request, proxy_count=1, proxy_trusted_ips=['177.139.233.133'])
   ```

- ### Originating Request

If your proxy server is configured such that the right most IP address is that of the originating client, you
can indicate `right-most` as your `proxy_order` when calling `get_client_ip(request, proxy_order="right-most")`.
Please note that the [de-facto](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) standard
for the originating client IP address is  the `left-most` as per `<client>, <proxy1>, <proxy2>`.

Running the tests
====================

To run the tests against the current environment:

    python manage.py test


License
====================

Released under a ([MIT](LICENSE)) license.


Version
====================
X.Y.Z Version

    `MAJOR` version -- when you make incompatible API changes,
    `MINOR` version -- when you add functionality in a backwards-compatible manner, and
    `PATCH` version -- when you make backwards-compatible bug fixes.

[status-image]: https://secure.travis-ci.org/un33k/django-ipware.png?branch=master
[status-link]: http://travis-ci.org/un33k/django-ipware?branch=master

[version-image]: https://img.shields.io/pypi/v/django-ipware.svg
[version-link]: https://pypi.python.org/pypi/django-ipware

[coverage-image]: https://coveralls.io/repos/un33k/django-ipware/badge.svg
[coverage-link]: https://coveralls.io/r/un33k/django-ipware

[download-image]: https://img.shields.io/pypi/dm/django-ipware.svg
[download-link]: https://pypi.python.org/pypi/django-ipware
