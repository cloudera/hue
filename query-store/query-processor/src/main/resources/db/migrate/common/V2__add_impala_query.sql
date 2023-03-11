-- (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

/*
 * Table definition for the Impala query search functionality
 */
CREATE TABLE impala_query (
  id                    SERIAL PRIMARY KEY,

  query_id              VARCHAR(512) UNIQUE,
  query_text            TEXT,
  status                VARCHAR(16),
  query_type            VARCHAR(16),

  start_time            BIGINT,
  end_time              BIGINT,
  duration              BIGINT,

  user_name             VARCHAR(64),
  coordinator           VARCHAR(2048),

  cpu_time              BIGINT,
  rows_produced         BIGINT,
  peak_memory           BIGINT,
  hdfs_bytes_read       BIGINT,

  source                JSONB,
  version               SMALLINT
);

CREATE INDEX idx_iq_query_id
  ON impala_query (query_id);
CREATE INDEX idx_iq_query_text
  ON impala_query (query_text);
CREATE INDEX idx_iq_status
  ON impala_query (status);
CREATE INDEX idx_iq_query_type
  ON impala_query (query_type);

CREATE INDEX idx_iq_start_time
  ON impala_query (start_time);
CREATE INDEX idx_iq_end_time
  ON impala_query (end_time);
CREATE INDEX idx_iq_duration
  ON impala_query (duration);

CREATE INDEX idx_iq_user_name
  ON impala_query (user_name);
CREATE INDEX idx_iq_coordinator
  ON impala_query (coordinator);

CREATE INDEX idx_iq_cpu_time
  ON impala_query (cpu_time);
CREATE INDEX idx_iq_rows_produced
  ON impala_query (rows_produced);
CREATE INDEX idx_iq_peak_memory
  ON impala_query (peak_memory);
CREATE INDEX idx_iq_hdfs_bytes_read
  ON impala_query (hdfs_bytes_read);
