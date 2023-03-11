-- (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

/*
 * Table definition for the query search functionality
 */
CREATE TABLE hive_query (
  id                    bigint unsigned PRIMARY KEY AUTO_INCREMENT,
  query_id              VARCHAR(512) UNIQUE,
  query                 LONGTEXT,
  start_time            BIGINT,
  end_time              BIGINT,
  elapsed_time          BIGINT,
  status                VARCHAR(32),
  queue_name            VARCHAR(767),
  user_id               VARCHAR(256),
  request_user          VARCHAR(256),
  cpu_time              BIGINT,
  physical_memory       BIGINT,
  virtual_memory        BIGINT,
  data_read             BIGINT,
  data_written          BIGINT,
  operation_id          VARCHAR(512),
  client_ip_address     VARCHAR(64),
  hive_instance_address VARCHAR(512),
  hive_instance_type    VARCHAR(512),
  session_id            VARCHAR(512),
  log_id                VARCHAR(512),
  thread_id             VARCHAR(512),
  execution_mode        VARCHAR(16),
  databases_used        JSON,
  tables_read           JSON,
  tables_written        JSON,
  domain_id             VARCHAR(512),
  llap_app_id           VARCHAR(512),
  used_cbo              tinyint(1),
  first_task_started_time BIGINT,
  waiting_time          BIGINT,
  resource_utilization  BIGINT,
  version               SMALLINT,
  created_at            TIMESTAMP(0) NOT NULL
);

CREATE INDEX idx_hq_query_id
  ON hive_query (query_id);
CREATE INDEX idx_hq_llap_app_id
  ON hive_query (llap_app_id);
CREATE INDEX idx_hq_start_time
  ON hive_query (start_time);
CREATE INDEX idx_hq_end_time
  ON hive_query (end_time);
CREATE INDEX idx_hq_elapsed_time
  ON hive_query (elapsed_time);
CREATE INDEX idx_hq_status
  ON hive_query (status);
CREATE INDEX idx_hq_query_name
  ON hive_query (queue_name);
CREATE INDEX idx_hq_request_user
  ON hive_query (request_user);
CREATE INDEX idx_hq_client_ip
  ON hive_query (client_ip_address);
/*
*CREATE INDEX idx_hq_tables_read
*  ON hive_query USING GIN (tables_read);
*CREATE INDEX idx_hq_tables_written
*  ON hive_query USING GIN (tables_written);
*/
CREATE INDEX idx_hq_created_at
  ON hive_query (created_at);
CREATE INDEX idx_hq_cpu_time
  ON hive_query (cpu_time);
CREATE INDEX idx_hq_physical_memory
  ON hive_query (physical_memory);
CREATE INDEX idx_hq_virtual_memory
  ON hive_query (virtual_memory);
CREATE INDEX idx_hq_data_read
  ON hive_query (data_read);
CREATE INDEX idx_hq_data_written
  ON hive_query (data_written);

CREATE TABLE dag_info (
  id                bigint unsigned PRIMARY KEY AUTO_INCREMENT,
  dag_id            VARCHAR(512) UNIQUE,
  dag_name          VARCHAR(512),
  application_id    VARCHAR(512),
  init_time         BIGINT,
  start_time        BIGINT,
  end_time          BIGINT,
  time_taken        BIGINT,
  status            VARCHAR(64),
  am_webservice_ver VARCHAR(16),
  am_log_url        VARCHAR(512),
  queue_name        VARCHAR(64),
  caller_id         VARCHAR(512),
  caller_type       VARCHAR(128),
  hive_query_id     bigint unsigned,
  created_at        TIMESTAMP(0) NOT NULL,
  source_file       TEXT,
  FOREIGN KEY (hive_query_id) REFERENCES hive_query (id) ON DELETE CASCADE
);


CREATE INDEX idx_di_dag_id
  ON dag_info (dag_id);
CREATE INDEX idx_di_dag_name
  ON dag_info (dag_name);
CREATE INDEX idx_di_init_time
  ON dag_info (init_time);
CREATE INDEX idx_di_start_time
  ON dag_info (start_time);
CREATE INDEX idx_di_end_time
  ON dag_info (end_time);
CREATE INDEX idx_di_time_taken
  ON dag_info (time_taken);
CREATE INDEX idx_di_status
  ON dag_info (status);
CREATE INDEX idx_di_queue_name
  ON dag_info (queue_name);
CREATE INDEX idx_di_application_id
  ON dag_info (application_id);
CREATE INDEX idx_di_hive_query_id
  ON dag_info (hive_query_id);
CREATE INDEX idx_di_created_at
  ON dag_info (created_at);

CREATE TABLE query_details (
  id                     bigint unsigned PRIMARY KEY AUTO_INCREMENT,
  hive_query_id          bigint unsigned,
  explain_plan_compressed LONGBLOB,
  configuration_compressed LONGBLOB,
  perf                   JSON,
  created_at             TIMESTAMP(0) NOT NULL,
  FOREIGN KEY (hive_query_id) REFERENCES hive_query (id) ON DELETE CASCADE
);

CREATE TABLE dag_details (
  id                     bigint unsigned PRIMARY KEY AUTO_INCREMENT,
  dag_info_id            bigint unsigned UNIQUE,
  hive_query_id          bigint unsigned,
  dag_plan_compressed    LONGBLOB,
  vertex_name_id_mapping_compressed LONGBLOB,
  diagnostics            LONGTEXT,
  counters_compressed    LONGBLOB,
  created_at             TIMESTAMP(0) NOT NULL,
  FOREIGN KEY (dag_info_id) REFERENCES dag_info (id) ON DELETE CASCADE,
  FOREIGN KEY (hive_query_id) REFERENCES hive_query (id) ON DELETE CASCADE
);

CREATE INDEX idx_dd_hive_query_id
  ON dag_details (hive_query_id);

CREATE TABLE vertex_info (
  id                        bigint unsigned PRIMARY KEY AUTO_INCREMENT,
  vertex_id                 VARCHAR(512) UNIQUE,
  name                      VARCHAR(256),
  domain_id                 VARCHAR(512),
  task_count                INT,
  completed_task_count      INT,
  succeeded_task_count      INT,
  failed_task_count         INT,
  killed_task_count         INT,
  failed_task_attempt_count INT,
  killed_task_attempt_count INT,
  class_name                VARCHAR(512),
  start_time                BIGINT,
  end_time                  BIGINT,
  init_requested_time       BIGINT,
  start_requested_time      BIGINT,
  status                    VARCHAR(64),
  counters_compressed       LONGBLOB,
  stats_compressed          LONGBLOB,
  events_compressed         LONGBLOB,
  dag_id                    bigint unsigned,
  created_at                TIMESTAMP(0) NOT NULL,
  FOREIGN KEY (dag_id) REFERENCES dag_info (id) ON DELETE CASCADE
);

CREATE INDEX idx_vi_vertex_id
  ON vertex_info (vertex_id);
CREATE INDEX idx_vi_dag_id
  ON vertex_info (dag_id);

CREATE TABLE tez_app_info (
  id            bigint unsigned PRIMARY KEY AUTO_INCREMENT,
  app_id        VARCHAR(512) UNIQUE,
  submit_time   BIGINT,
  config_compressed LONGBLOB
);

/*
 * Table definition for the event file read tracker functionality
 */
CREATE TABLE file_status (
  id                bigint unsigned PRIMARY KEY AUTO_INCREMENT,
  file_type         VARCHAR(10),
  date              DATE,
  file_name         VARCHAR(512),
  position          BIGINT,
  last_event_time   BIGINT,
  finished          tinyint(1),
  UNIQUE (file_type, date, file_name)
);
