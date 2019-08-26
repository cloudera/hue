.. :changelog:

History
-------

4.0.0 (2019-04-27)
------------------

- (Support OpenTracing API v2.0 (#206) <Michał Szymański>
- Add support for references (#241) <Bhavin Gandhi>
- Add info on configuring Jaeger agent location. (#245) <Carlos Nunez>
- Add 128bit trace_id support (#230) <Bhavin Gandhi>
- Enable linting of tests (#227) <pravarag>
- Enable windows support by isolating ioctl calls (#233) <CARRIERE Etienne>
- Unpin flake8 to allow v3 (#231) <Yuri Shkuro>
- Fix pycurl install advice <Yuri Shkuro>
- Fix handling of missing headers in the b3 codec (#215) <cshowe>
- Fix typo in the link name <Yuri Shkuro>
- Add supported python version to README (#226) <Won Jun Jang>


3.13.0 (2018-12-04)
-------------------

- Mark reporter_queue_size Config option as valid (#209) <Tim Joseph Dumol>
- Allow setting of the Jaeger Agent Host via environment variable (#218) <Tim Stoop>
- Wrap parsing of throttling response in try block to avoid errors (#219) <Isaac Hier>


3.12.0 (2018-11-02)
-------------------

- Support deleting key from baggage (#216) <TianYi ZHU>
- Preserve datatype of tag values (#213) <Trond Hindenes>
- Support `jaeger-baggage` header for ad-hoc baggage (#207) <Yuri Shkuro>


3.11.0 (2018-08-02)
-------------------

- Fix parsing remote sampling strategy on Python 3.5 (#180) <Niels Pardon>
- Fix handling of missing ParentSpanId for B3 codec (#182) <Gabriel Gravel>
- Implement throttler (#188) <Isaac Hier>
- Improve handling of config values and default arguments (#192) <Isaac Hier>
- Add ability to update rate limitier (#196) <Won Jun Jang>
- Fix incorrect default agent reporting port (#200) <Ryan Fitzpatrick>
- Correct sampled and debug B3 headers (#203) <Ryan Fitzpatrick>


3.10.0 (2018-05-09)
------------------

- Allow specifying hostname and ip via tags (#167) <Jeff Schroeder>
- Use String strategyType instead of int (#172)


3.9.0 (2018-04-20)
------------------

Python 3.6 is now officially supported!

- Remove support for non-ascii baggage keys; enable testing with Py 3.6  (#154) <Yuri Shkuro>
- Add IP tag to tracer tags; rename `jaeger.hostname` tag to `hostname` (#160) <Won Jun Jang>
- Remove `tchannel;<py3` restriction in tests/extras_require (#159) <Won Jun Jang>
- Replace `concurrent.futures.Future` with `tornado.concurrent.Future` (#155) <Yuri Shkuro>
- Better support for creating multiple tracers (#150) <nziebart>
- Add PrometheusMetricsFactory (#142) <Eundoo Song>
- Add ability to validate configuration (#124) <Gregory Reshetniak>
- Make Metrics consistent with Go client (#129) <Eundoo Song>


3.8.0 (2018-03-06)
------------------

- Replace zipkin.thrift out-of-band span format with jaeger.thrift (#111)
- Use only `six` for py2/py3 compatibility, drop `future` (#130, #134, #135)
- Add codec for B3 trace context headers (#112) - thanks @gravelg
- Increase max tag value length to 1024 and make it configurable (#110)
- A number of fixes for Python 3.x compatibility
  - Fix span and sampler tests to work under Py3 (#117)
  - Fix dependencies for Py3 compatibility (#116)
  - Fix xrange for Py3 in thrift generated files (#115)
  - Add python3 compat, hasattr iteritems->itemx (#113) - thanks @kbroughton


3.7.1 (2017-12-14)
------------------

- Encode unicode baggage keys/values to UTF-8 (#109)


3.7.0 (2017-12-12)
------------------

- Change default for one_span_per_rpc to False (#105)


3.6.1 (2017-09-26)
------------------

- Fix bug when creating tracer with tags. (#80)


3.6.0 (2017-09-26)
------------------

- Allow tracer constructor to accept optional tags argument.
- Support `JAEGER_TAGS` environment variable and config for tracer tags.


3.5.0 (2017-07-10)
------------------

- Add metrics factory and allow tags for metrics [#45]
- Save baggage in span [#54]
- Allow to override hostname for jaeger agent [#51]


3.4.0 (2017-03-20)
------------------

- Add adaptive sampler
- Allow overriding one-span-per-rpc behavior
- Allow overriding codecs in tracer initialization


3.3.1 (2016-10-14)
------------------

- Replace 0 parentID with None


3.3.0 (2016-10-04)
------------------

- Upgrade to opentracing 1.2 with KV logging.


3.2.0 (2016-09-20)
------------------

- Support debug traces via HTTP header jaeger-debug-id.


3.1.0 (2016-09-06)
------------------

- Report sampling strategy as root span tags `sampler.type` and `sampler.param`. In case of probabilistic sampling (most frequently used strategy), the values would be `probabilistic` and the sampling probability [0 .. 1], respectively.
- Record host name as `jaeger.hostname` tag on the first-in-process spans (i.e. root spans and rpc-server spans)
- Record the version of the Jaeger library as `jaeger.version` tag


3.0.2 (2016-08-18)
------------------

- Do not create SpanContext from Zipkin span if trace_id is empty/zero


3.0.1 (2016-08-09)
------------------

- Do not publish crossdock module


3.0.0 (2016-08-07)
------------------

- Upgrade to OpenTracing 1.1


2.2.0 (2016-08-02)
------------------

- Implement Zipkin codec for interop with TChannel


2.1.0 (2016-07-19)
------------------

- Allow passing external IOLoop


2.0.0 (2016-07-19)
------------------

- Remove TChannel dependency
- Remove dependency on opentracing_instrumentation


1.0.1 (2016-07-11)
------------------

- Downgrade TChannel dependency to >= 0.24


1.0.0 (2016-07-10)
------------------

- Initial open source release.
