
# Open Tracing

Goal: understanding of where exactly the time is being spent when executing queries (e.g. in Hue database, in interpreter, RPC call to warehouse...)

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
* not forwarding trace id span among query Hue API calls to see a "full query trace": manually filtering by query id instead
* Ideally: distributed query tracing done with other components (Hive, Impala, HDFS...).
