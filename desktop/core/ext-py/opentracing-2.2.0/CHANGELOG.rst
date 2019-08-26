.. :changelog:

History
=======

2.2.0 (2019-05-10)
------------------

- Fix __exit__ method of Scope class (#120) <Aliaksei Urbanski>
- Add support for Python 3.5/3.7 and fix tests (#121) <Aliaksei Urbanski>


2.1.0 (2019-04-27)
------------------

- Add support for indicating if a global tracer has been registered (#109) <Mike Goldsmith>
- Use pytest-cov==2.6.0 as 2.6.1 depends on pytest>=3.6.0 (#113) <Carlos Alberto Cortez>
- Better error handling in context managers for Span/Scope. (#101) <Carlos Alberto Cortez>
- Add log fields constants to opentracing.logs. (#99) <Carlos Alberto Cortez>
- Move opentracing.ext.tags to opentracing.tags. (#103) <Carlos Alberto Cortez>
- Add SERVICE tag (#100) <Carlos Alberto Cortez>
- Fix unclosed active scope in tests (#97) <Michał Szymański>
- Initial implementation of a global Tracer. (#95) <Carlos Alberto Cortez>


2.0.0 (2018-07-10)
------------------

- Implement ScopeManager for in-process propagation.
- Added a set of default ScopeManager implementations.
- Added testbed/ for testing API changes.
- Added MockTracer for instrumentation testing.


1.3.0 (2018-01-14)
------------------

- Added sphinx-generated documentation.
- Remove 'futures' from install_requires (#62)
- Add a harness check for unicode keys and vals (#40)
- Have the harness try all tag value types (#39)


1.2.2 (2016-10-03)
------------------

- Fix KeyError when checking kwargs for optional values


1.2.1 (2016-09-22)
------------------

- Make Span.log(self, \**kwargs) smarter


1.2.0 (2016-09-21)
------------------

- Add Span.log_kv and deprecate older logging methods


1.1.0 (2016-08-06)
------------------

- Move set/get_baggage back to Span; add SpanContext.baggage
- Raise exception on unknown format


2.0.0.dev3 (2016-07-26)
-----------------------

- Support SpanContext


2.0.0.dev1 (2016-07-12)
-----------------------

- Rename ChildOf/FollowsFrom to child_of/follows_from
- Rename span_context to referee in Reference
- Document expected behavior when referee=None


2.0.0.dev0 (2016-07-11)
-----------------------

- Support SpanContext (and real semvers)


1.0rc4 (2016-05-21)
-------------------

- Add standard tags per http://opentracing.io/data-semantics/


1.0rc3 (2016-03-22)
-------------------

- No changes yet


1.0rc3 (2016-03-22)
-------------------

- Move to simpler carrier formats


1.0rc2 (2016-03-11)
-------------------

- Remove the Injector/Extractor layer


1.0rc1 (2016-02-24)
-------------------

- Upgrade to 1.0 RC specification


0.6.3 (2016-01-16)
------------------

- Rename repository back to opentracing-python


0.6.2 (2016-01-15)
------------------

- Validate chaining of logging calls


0.6.1 (2016-01-09)
------------------

- Fix typo in the attributes API test


0.6.0 (2016-01-09)
------------------

- Change inheritance to match api-go: TraceContextSource extends codecs,
  Tracer extends TraceContextSource
- Create API harness


0.5.2 (2016-01-08)
------------------

- Update README and meta.


0.5.1 (2016-01-08)
------------------

- Prepare for PYPI publishing.


0.5.0 (2016-01-07)
------------------

- Remove debug flag
- Allow passing tags to start methods
- Add Span.add_tags() method


0.4.2 (2016-01-07)
------------------

- Add SPAN_KIND tag


0.4.0 (2016-01-06)
------------------

- Rename marshal -> encode


0.3.1 (2015-12-30)
------------------

- Fix std context implementation to refer to Trace Attributes instead of metadata


0.3.0 (2015-12-29)
------------------

- Rename trace tags to Trace Attributes. Rename RPC tags to PEER. Add README.


0.2.0 (2015-12-28)
------------------

- Export global `tracer` variable.


0.1.4 (2015-12-28)
------------------

- Rename RPC_SERVICE tag to make it symmetric


0.1.3 (2015-12-27)
------------------

- Allow repeated keys for span tags; add standard tag names for RPC


0.1.2 (2015-12-27)
------------------

- Move creation of child context to TraceContextSource


0.1.1 (2015-12-27)
------------------

- Add log methods


0.1.0 (2015-12-27)
------------------

- Initial public API

