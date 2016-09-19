Changelog
=========

0.3.x
~~~~~

Version 0.3.9
-------------

Released on August 26, 2016.

- add support for timeout and ssl in `make_server` / `make_client` helper
  funcs, via `#204`_, `#205`_ and `#229`_.
- add support for `thrift_file` path in http protocol, via `#225`_. 

- preserve traceback when re-raise undeclared exception, via `#206`_.
- performance improvement by dynamically compile spec'd `__init__`
  functions, via `#210`_ and `#227`_.
- performance improvement by refine cython encoding/decoding,
  via `#211`_ and `#212`_.

- bugfix for type error in `cast_byte` parser and improve include dirs
  function, via `#214`_.
- bugfix for parse error when field begin with true/false keyword,
  via `#215`_ and `#218`_.
- bugfix for `is_open` not return false when socket closed after open,
  via `#230`_.

.. _`#204`: https://github.com/eleme/thriftpy/pull/204
.. _`#205`: https://github.com/eleme/thriftpy/pull/205
.. _`#206`: https://github.com/eleme/thriftpy/pull/206
.. _`#210`: https://github.com/eleme/thriftpy/pull/210
.. _`#211`: https://github.com/eleme/thriftpy/pull/211
.. _`#212`: https://github.com/eleme/thriftpy/pull/212
.. _`#214`: https://github.com/eleme/thriftpy/pull/214
.. _`#215`: https://github.com/eleme/thriftpy/pull/215
.. _`#218`: https://github.com/eleme/thriftpy/pull/218
.. _`#225`: https://github.com/eleme/thriftpy/pull/225
.. _`#227`: https://github.com/eleme/thriftpy/pull/227
.. _`#229`: https://github.com/eleme/thriftpy/pull/229
.. _`#230`: https://github.com/eleme/thriftpy/pull/230


Version 0.3.8
-------------

Released on May 3, 2016.

- add propagate decode_response to nested structs, via `#194`_.
- add support for tornado ssl, via `#196`_.

.. _`#194`: https://github.com/eleme/thriftpy/pull/194
.. _`#196`: https://github.com/eleme/thriftpy/pull/196


Version 0.3.7
-------------

Released on Mar 24, 2016.

- bugfix for a possible unicode decode error in cybin.
- use a better unhashable implementation for payload.


Version 0.3.6
-------------

Released on Mar 24, 2016.

- add compact protocol support, via `#159`_.
- add option to force return bytes on response, via `#190`_.

- bugfix for ssl socket can't be init without certfile and keyfile,
  and add additional `capath` argument for SSLContext.  via `#186`_.
- bugfix for set_timeout only works before socket open, via `#188`_.

.. _`#159`: https://github.com/eleme/thriftpy/pull/159
.. _`#186`: https://github.com/eleme/thriftpy/pull/186
.. _`#188`: https://github.com/eleme/thriftpy/pull/188
.. _`#190`: https://github.com/eleme/thriftpy/pull/190


Version 0.3.5
-------------

Released on Feb 16, 2016.

- fix another set_timeout backward compat issue introduced in last version.
- make thrift container struct unhashable, via `#184`_.

.. _`#184`: https://github.com/eleme/thriftpy/pull/184


Version 0.3.4
-------------

Released on Feb 3, 2016.

- fix backward compat issue introduced in last version, add back
  `set_timeout` api in socket.


Version 0.3.3
-------------

Released on Jan 21, 2016.

- add support for ssl transport.
- add named loggers, via `#169`_.

- refine socket and serversocket implementation with more configure options.

- bugfix for parser failure on windows under python3.2 caused by samefile
  method, via `#172`_.

.. _`#169`: https://github.com/eleme/thriftpy/pull/169
.. _`#172`: https://github.com/eleme/thriftpy/pull/172


Version 0.3.2
-------------

Released on Oct 12, 2015.

- add `__thrift_meta__` attribute to loaded module, via `#138`_.
- add type validation before write data to transport, via `#149`_ and `#150`_.
- add load_fp api to load thrift from file like object, via `#154`_.
- add support for recursive struct definition, via `#155`_.
- add support for integer boolean constants, via `#161`_.

- simplify the read_i08() bool result cast, via `#162`_.
- performance improvements on payload `init()` func, via `#163`_.

- bugfix for parsing of duplicate field name or id, now will raise error
  when duplicates detected, via `#139`_.
- bugfix for server side transport not connected error when closing socket,
  via `#143`_.
- bugfix for a typo error in `default_spec` generation, via `#145`_.
- bugfix for i16 byte swap bug in OS X, via `#148`_.

.. _`#138`: https://github.com/eleme/thriftpy/pull/138
.. _`#139`: https://github.com/eleme/thriftpy/pull/139
.. _`#143`: https://github.com/eleme/thriftpy/pull/143
.. _`#145`: https://github.com/eleme/thriftpy/pull/145
.. _`#148`: https://github.com/eleme/thriftpy/pull/148
.. _`#149`: https://github.com/eleme/thriftpy/pull/149
.. _`#150`: https://github.com/eleme/thriftpy/pull/150
.. _`#154`: https://github.com/eleme/thriftpy/pull/154
.. _`#155`: https://github.com/eleme/thriftpy/pull/155
.. _`#161`: https://github.com/eleme/thriftpy/pull/161
.. _`#162`: https://github.com/eleme/thriftpy/pull/162
.. _`#163`: https://github.com/eleme/thriftpy/pull/163


Version 0.3.1
-------------

Released on May 29, 2015.

- lock down to use pure python only in windows env. (this avoid the cython
  stuffs on windows totally)
- enable multiple include dirs, via `#131`_.
- bugfix for parsing of constants with separators, via `#134`_.

.. _`#131`: https://github.com/eleme/thriftpy/pull/131
.. _`#134`: https://github.com/eleme/thriftpy/pull/134


Version 0.3.0
-------------

Released on April 15, 2015.

Non-Backward Compatible changes:

- migrate multiplexed protocol implementation to the same with upstream,
  via `#117`_.

.. _`#117`: https://github.com/eleme/thriftpy/pull/117


0.2.x
~~~~~

Version 0.2.1
-------------

Released on April 15, 2015.

- add an experimental tracking feature in `thriftpy.contrib`, via `#96`_.
- add limitation on thrift reserved keyword for compatible with upstream, via
  `#115`_.
- bugfix EOF grammar error, via `#103`_.
- bugfix for mis-mach transport in client caused server crash, via `#119`_.
- bugfix for typedef on included thrift files, via `#121`_.

.. _`#96`: https://github.com/eleme/thriftpy/pull/96
.. _`#103`: https://github.com/eleme/thriftpy/pull/103
.. _`#115`: https://github.com/eleme/thriftpy/pull/115
.. _`#119`: https://github.com/eleme/thriftpy/pull/119
.. _`#121`: https://github.com/eleme/thriftpy/pull/121


Version 0.2.0
-------------

Released on March 3, 2015.

- support for default enum values that reference the original enum, via
  `#69`_.
- support for `require` keyword, via `#72`_.
- support for allow use and definition of types in the same file, via
  `#77`_.
- support for multiplexing for services, via `#88`_.
- support for cython accelerated memory transport and framed transport,
  via `#93`
- bugfix for transport clean in read_struct in cybin, via `#70`_.
- bugfix for large reading size in framed transport, via `#73`_.
- bugfix for cython build failed in older CentOS, via `#92`_.
- bugfix for thrift file version mis-match caused message corrupt in
  `read_struct`, via `#95`_.

Non-Backward Compatible changes:

- refined new parser, the parser now behaves very similar to Apache Thrift,
  and supports a lot more features than the old one, via `#80`_. Refer to the
  pull request for more detailed changes.
- refined transport, all transports have cython accelerated version. The
  cython version of protocol and transport are enabled by default now.

.. _`#69`: https://github.com/eleme/thriftpy/pull/69
.. _`#70`: https://github.com/eleme/thriftpy/pull/70
.. _`#72`: https://github.com/eleme/thriftpy/pull/72
.. _`#73`: https://github.com/eleme/thriftpy/pull/73
.. _`#77`: https://github.com/eleme/thriftpy/pull/77
.. _`#80`: https://github.com/eleme/thriftpy/pull/80
.. _`#88`: https://github.com/eleme/thriftpy/pull/88
.. _`#91`: https://github.com/eleme/thriftpy/pull/91
.. _`#92`: https://github.com/eleme/thriftpy/pull/92
.. _`#93`: https://github.com/eleme/thriftpy/pull/93
.. _`#95`: https://github.com/eleme/thriftpy/pull/95


0.1.x
~~~~~

Version 0.1.15
--------------

Released on December 12, 2014.

- add MIT `LICENSE` file as requested.
- tests refines with tox and pytest fixtures.
- support for a mostly cythonized version of framed transport, via `#66`_.
- bugfix for unix socket param in rpc.
- bugfix for receiving 0-length strings & framed transport, via `#63`_.
- bugfix for json protocol unicode decode error, via `#65`_.
- bugfix for operator `__ne__` implementation error, via `#68`_.

.. _`#66`: https://github.com/eleme/thriftpy/pull/66
.. _`#63`: https://github.com/eleme/thriftpy/pull/63
.. _`#65`: https://github.com/eleme/thriftpy/pull/65
.. _`#68`: https://github.com/eleme/thriftpy/pull/68


Version 0.1.14
--------------

Released on November 8, 2014.

- support for python2.6.
- support for testing by tox.
- support for oneway keyword, via `#49`_.
- bugfix for wrong type args, via `#48`_.
- bugfix for thrift file include keyword, via `#53`_.
- bugfix for skip method not found in protocol, via `#55`_.
- bugfix for set type support, via `#59`_.
- bugfix for 'api' arg name collision in client.

.. _`#48`: https://github.com/eleme/thriftpy/pull/48
.. _`#49`: https://github.com/eleme/thriftpy/pull/49
.. _`#53`: https://github.com/eleme/thriftpy/pull/53
.. _`#55`: https://github.com/eleme/thriftpy/pull/55
.. _`#59`: https://github.com/eleme/thriftpy/pull/59


Version 0.1.13
--------------

Released on September 24, 2014.

- bugfix for TPayload not able to be hashed in py3, via `#44`_.
- bugfix for cython buffered transport read issue, via `#46`_.

.. _`#44`: https://github.com/eleme/thriftpy/pull/44
.. _`#46`: https://github.com/eleme/thriftpy/pull/46


Version 0.1.12
--------------

Released on September 18, 2014.

- bugfix for lack of `skip` func in cython binary protocol, via `#43`_.

.. _`#43`: https://github.com/eleme/thriftpy/pull/43


Version 0.1.11
--------------

Released on September 16, 2014.

- bugfix for init func generator for TStruct.
- bugfix for set constants in parser, via `#39`_.
- add support for "includes" and service "extends", via `#37`_.
- add close() to servers, via `#38`_.
- implement non-strict mode for binary protocol, via `#40`_.
- removed cython ext in pypy, and add pypy3 support.
- some args updates:
  * add `trans_factory` arg to `make_server`
  * rename `rbuf_size` in buffered transport to `buf_size`.
  * rename `isOpen` to `is_open`, `readFrame` to `read_frame`.

.. _`#37`: https://github.com/eleme/thriftpy/pull/37
.. _`#38`: https://github.com/eleme/thriftpy/pull/38
.. _`#39`: https://github.com/eleme/thriftpy/pull/39
.. _`#40`: https://github.com/eleme/thriftpy/pull/40


Version 0.1.10
--------------

Released on September 4, 2014.

- bugfix for memory free in cython buffered transport, via `#35`_.
- new thrift parser by PLY, removed cache since the performance is much more
  faster now, via `#36`_.

.. _`#35`: https://github.com/eleme/thriftpy/pull/35
.. _`#36`: https://github.com/eleme/thriftpy/pull/36


Version 0.1.9
-------------

Released on September 1, 2014.

- refine cython binary protocol, add cython buffered transport, via `#32`_.
- param name change, rename transport_factory to trans_factory in rpc.

.. _`#32`: https://github.com/eleme/thriftpy/pull/32


Version 0.1.8
-------------

Released on August 28, 2014.

- faster thrift file parse speed, via `#30`_.
- bugfix for cybin buffer read, via `#31`_.

.. _`#30`: https://github.com/eleme/thriftpy/pull/30
.. _`#31`: https://github.com/eleme/thriftpy/pull/31


Version 0.1.7
-------------

Released on August 19, 2014.

- use args instead of kwargs in api calling to match upstream behavior.
- cython binary protocol auto grow buffer size, via `#29`_.
- bugfix for void api exception handling in processor.
- bugfix for cybin protocol buffer overflow and memcpy, via `#27`_ and `#28`_.

.. _`#27`: https://github.com/eleme/thriftpy/pull/27
.. _`#28`: https://github.com/eleme/thriftpy/pull/28
.. _`#29`: https://github.com/eleme/thriftpy/pull/29


Version 0.1.6
-------------

Released on August 14, 2014.

- json protocol, via `#21`_.
- more standard module for loaded sdk, now generated TPayload objects can
  be pickled when module_name provided, via `#22`_.
- gunicorn_thrift integration pingpong example, via `#24`_.
- token cache now only checks python's major and minor version.
- bugfix for exception handling in void api in RPC request.
- bugfix for negative number value not recognized.
- bugfix for cybin protocol to allow None value in struct.
- bugfix for double free or corruption in cybin protocol, via `#26`_.

.. _`#21`: https://github.com/eleme/thriftpy/pull/21
.. _`#22`: https://github.com/eleme/thriftpy/pull/22
.. _`#24`: https://github.com/eleme/thriftpy/pull/24
.. _`#26`: https://github.com/eleme/thriftpy/pull/26


Version 0.1.5
-------------

Released on July 25, 2014.

- tornado client, server and framed transport support with tornado 4.0,
  via `#15`_.
- immediately read from TMemoryBuffer after writing to it, via `#20`_.
- cache `load` function to avoid duplicate module generation.
- support client with socket timeout
- enum struct now has VALUES_TO_NAMES and NAMES_TO_VALUES.

.. _`#15`: https://github.com/eleme/thriftpy/pull/15
.. _`#20`: https://github.com/eleme/thriftpy/pull/20


Version 0.1.4
-------------

Released on July 17, 2014.

- parser token cache, speed boost for thrift file parsing, via `#12`_.
- new cython binary protocol with speed very close to c ext, via `#16`_.

.. _`#12`: https://github.com/eleme/thriftpy/pull/14
.. _`#16`: https://github.com/eleme/thriftpy/pull/14


Version 0.1.3
-------------

Released on June 19, 2014.

- support for union, binary fields, support for empty structs,
  support for Apache Storm thrift file, via `#14`_.
- bugfix for import hook
- bugfix for skip function in binary protocols

.. _`#14`: https://github.com/eleme/thriftpy/pull/14


Version 0.1.2
-------------

Released on June 7, 2014.

- disabled the magic import hook by default. and add install/remove
  function to switch the hook on and off.
- reworked benchmark suit and add benchmark results.
- new `__init__` function code generator. get a noticable speed boost.
- bug fixes


Version 0.1.1
-------------

First public release.
