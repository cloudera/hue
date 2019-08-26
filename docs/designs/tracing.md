
# Open Tracing

Goal: understanding of where exactly the time is being spent when executing queries (e.g. in Hue database, in interpreter, RPC call to warehouse...)

* https://opentracing.io/guides/python/quickstart/
* https://github.com/opentracing-contrib/python-django
* https://medium.com/jaegertracing/grafana-labs-teams-observed-query-performance-improvements-up-to-10x-with-jaeger-cec84b0e3609
* https://github.com/census-instrumentation/opencensus-python

# Hue

Track:

* REST RPC
* Thrift RPC
* Celery tasks
* DB

Would need to inject:

## All the time

* user id
* operation ID (auto: trace id)

## SQL

When starting a new query or sessions:

* session id
* query id

and propagating by adding them to check_status, fetch_result, close_statement, close_sessions.

Notes:
* Not forwarding trace id span among query Hue API calls to see a "full query trace": manually filtering by query id instead. Maybe an option in the future.
* Ideally: distributed query tracing done with other components (Hive, Impala, HDFS...).

# TODO

* @trace() only a few individual calls
* Add spans to HS2 and SqlAlchemy APIs RPCs
* Trace DB & more via https://github.com/census-instrumentation/opencensus-python#extensions?
* Trace HTTP
* Tracer options for remote Jaeger?
* get active spans and set ids earlier
* Add session ids to tags
* Jaeger embedded UI with User / Session / Query input boxes
* Provide Trace ID to Task Worker
* Provide Trace ID to Impala
