FROM postgres:9.4

ENV DB_USER hueuser
ENV DB_PASSWORD huepasswd
ENV DB_NAME huedb
ENV DB_ENCODING UTF-8

RUN mkdir -p /tmp/psql_data/

COPY docker/huedb/db/huedb.dump /tmp/psql_data/
COPY docker/huedb/scripts/init_docker_postgres.sh /docker-entrypoint-initdb.d/
