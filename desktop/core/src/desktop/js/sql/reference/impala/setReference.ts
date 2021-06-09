// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { SetOptions } from 'sql/reference/types';

export const SET_OPTIONS: SetOptions = {
  ALLOW_ERASURE_CODED_FILES: {
    description:
      'Use the ALLOW_ERASURE_CODED_FILES query option to enable or disable the support of erasure coded files in Impala. Until Impala is fully tested and certified with erasure coded files, this query option is set to FALSE by default.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  APPX_COUNT_DISTINCT: {
    description:
      'Allows multiple COUNT(DISTINCT) operations within a single query, by internally rewriting each COUNT(DISTINCT) to use the NDV() function. The resulting count is approximate rather than precise.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  BATCH_SIZE: {
    description:
      'Number of rows evaluated at a time by SQL operators. Unspecified or a size of 0 uses a predefined default size. Using a large number improves responsiveness, especially for scan operations, at the cost of a higher memory footprint.',
    type: 'Numeric',
    default: '0 (meaning the predefined default of 1024)'
  },
  BUFFER_POOL_LIMIT: {
    description:
      'Defines a limit on the amount of memory that a query can allocate from the internal buffer pool. The value for this limit applies to the memory on each host, not the aggregate memory across the cluster. Typically not changed by users, except during diagnosis of out-of-memory errors during queries.',
    type: 'Integer',
    default:
      'The default setting for this option is the lower of 80% of the MEM_LIMIT setting, or the MEM_LIMIT setting minus 100 MB.'
  },
  COMPRESSION_CODEC: {
    description:
      'When Impala writes Parquet data files using the INSERT statement, the underlying compression is controlled by the COMPRESSION_CODEC query option.',
    type: 'String; SNAPPY, GZIP or NONE',
    default: 'SNAPPY'
  },
  COMPUTE_STATS_MIN_SAMPLE_SIZE: {
    description:
      'The COMPUTE_STATS_MIN_SAMPLE_SIZE query option specifies the minimum number of bytes that will be scanned in COMPUTE STATS TABLESAMPLE, regardless of the user-supplied sampling percent. This query option prevents sampling for very small tables where accurate stats can be obtained cheaply without sampling because the minimum sample size is required to get meaningful stats.',
    type: 'Integer',
    default: '1073741824 (1GB)'
  },
  DEFAULT_JOIN_DISTRIBUTION_MODE: {
    description:
      'This option determines the join distribution that Impala uses when any of the tables involved in a join query is missing statistics.\n\nThe setting DEFAULT_JOIN_DISTRIBUTION_MODE=SHUFFLE is recommended when setting up and deploying new clusters, because it is less likely to result in serious consequences such as spilling or out-of-memory errors if the query plan is based on incomplete information.',
    type: 'Integer; The allowed values are BROADCAST (equivalent to 0) or SHUFFLE (equivalent to 1).',
    default: '0'
  },
  DEFAULT_SPILLABLE_BUFFER_SIZE: {
    description:
      'Specifies the default size for a memory buffer used when the spill-to-disk mechanism is activated, for example for queries against a large table with no statistics, or large join operations.\n\nAccepts a numeric value that represents a size in bytes; you can also use a suffix of m or mb for megabytes, or g or gb for gigabytes. If you specify a value with unrecognized formats, subsequent queries fail with an error.',
    type: 'Integer',
    default: '2097152 (2 MB)'
  },
  DISABLE_CODEGEN: {
    description:
      'This is a debug option, intended for diagnosing and working around issues that cause crashes. If a query fails with an "illegal instruction" or other hardware-specific message, try setting DISABLE_CODEGEN=true and running the query again. If the query succeeds only when the DISABLE_CODEGEN option is turned on, submit the problem to Cloudera Support and include that detail in the problem report. Do not otherwise run with this setting turned on, because it results in lower overall performance.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  DISABLE_ROW_RUNTIME_FILTERING: {
    description:
      'The DISABLE_ROW_RUNTIME_FILTERING query option reduces the scope of the runtime filtering feature. Queries still dynamically prune partitions, but do not apply the filtering logic to individual rows within partitions.\n\nOnly applies to queries against Parquet tables. For other file formats, Impala only prunes at the level of partitions, not individual rows.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  DISABLE_STREAMING_PREAGGREGATIONS: {
    description:
      'Turns off the "streaming preaggregation" optimization that is available in CDH 5.7 / Impala 2.5 and higher. This optimization reduces unnecessary work performed by queries that perform aggregation operations on columns with few or no duplicate values, for example DISTINCT id_column or GROUP BY unique_column. If the optimization causes regressions in existing queries that use aggregation functions, you can turn it off as needed by setting this query option.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  DISABLE_UNSAFE_SPILLS: {
    description:
      'Enable this option if you prefer to have queries fail when they exceed the Impala memory limit, rather than write temporary data to disk.\n\nQueries that "spill" to disk typically complete successfully, when in earlier Impala releases they would have failed. However, queries with exorbitant memory requirements due to missing statistics or inefficient join clauses could become so slow as a result that you would rather have them cancelled automatically and reduce the memory usage through standard Impala tuning techniques.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  EXEC_SINGLE_NODE_ROWS_THRESHOLD: {
    description:
      'This setting controls the cutoff point (in terms of number of rows scanned) below which Impala treats a query as a "small" query, turning off optimizations such as parallel execution and native code generation. The overhead for these optimizations is applicable for queries involving substantial amounts of data, but it makes sense to skip them for queries involving tiny amounts of data. Reducing the overhead for small queries allows Impala to complete them more quickly, keeping YARN resources, admission control slots, and so on available for data-intensive queries.',
    type: 'Numeric',
    default: '100'
  },
  EXEC_TIME_LIMIT_S: {
    description:
      'The EXEC_TIME_LIMIT_S query option sets a time limit on query execution. If a query is still executing when time limit expires, it is automatically canceled. The option is intended to prevent runaway queries that execute for much longer than intended.',
    type: 'Numeric',
    default: '0 (no time limit)'
  },
  EXPLAIN_LEVEL: {
    description:
      'Controls the amount of detail provided in the output of the EXPLAIN statement. The basic output can help you identify high-level performance issues such as scanning a higher volume of data or more partitions than you expect. The higher levels of detail show how intermediate results flow between nodes and how different SQL operations such as ORDER BY, GROUP BY, joins, and WHERE clauses are implemented within a distributed query.',
    type: 'String or Int; 0 - MINIMAL, 1 - STANDARD, 2 - EXTENDED or 3 - VERBOSE',
    default: '1'
  },
  HBASE_CACHE_BLOCKS: {
    description:
      'Setting this option is equivalent to calling the setCacheBlocks method of the class org.apache.hadoop.hbase.client.Scan, in an HBase Java application. Helps to control the memory pressure on the HBase RegionServer, in conjunction with the HBASE_CACHING query option.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  HBASE_CACHING: {
    description:
      'Setting this option is equivalent to calling the setCaching method of the class org.apache.hadoop.hbase.client.Scan, in an HBase Java application. Helps to control the memory pressure on the HBase RegionServer, in conjunction with the HBASE_CACHE_BLOCKS query option.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  MAX_ERRORS: {
    description:
      'Maximum number of non-fatal errors for any particular query that are recorded in the Impala log file. For example, if a billion-row table had a non-fatal data error in every row, you could diagnose the problem without all billion errors being logged. Unspecified or 0 indicates the built-in default value of 1000.\n\nThis option only controls how many errors are reported. To specify whether Impala continues or halts when it encounters such errors, use the ABORT_ON_ERROR option.',
    type: 'Numeric',
    default: '0 (meaning 1000 errors)'
  },
  MAX_MEM_ESTIMATE_FOR_ADMISSION: {
    description:
      'Use the MAX_MEM_ESTIMATE_FOR_ADMISSION query option to set an upper limit on the memory estimates of a query as a workaround for over-estimates precluding a query from being admitted.',
    type: 'Numeric',
    default: ''
  },
  MAX_NUM_RUNTIME_FILTERS: {
    description:
      'The MAX_NUM_RUNTIME_FILTERS query option sets an upper limit on the number of runtime filters that can be produced for each query.',
    type: 'Integer',
    default: '10'
  },
  MAX_ROW_SIZE: {
    description:
      'Ensures that Impala can process rows of at least the specified size. (Larger rows might be successfully processed, but that is not guaranteed.) Applies when constructing intermediate or final rows in the result set. This setting prevents out-of-control memory use when accessing columns containing huge strings.\n\nAccepts a numeric value that represents a size in bytes; you can also use a suffix of m or mb for megabytes, or g or gb for gigabytes. If you specify a value with unrecognized formats, subsequent queries fail with an error.',
    type: 'Integer',
    default: '524288 (512 KB)'
  },
  MAX_SCAN_RANGE_LENGTH: {
    description:
      'Maximum length of the scan range. Interacts with the number of HDFS blocks in the table to determine how many CPU cores across the cluster are involved with the processing for a query. (Each core processes one scan range.)\n\nLowering the value can sometimes increase parallelism if you have unused CPU capacity, but a too-small value can limit query performance because each scan range involves extra overhead.\n\nOnly applicable to HDFS tables. Has no effect on Parquet tables. Unspecified or 0 indicates backend default, which is the same as the HDFS block size for each table.',
    type: 'Numeric',
    default: '0'
  },
  MEM_LIMIT: {
    description:
      'When resource management is not enabled, defines the maximum amount of memory a query can allocate on each node. Therefore, the total memory that can be used by a query is the MEM_LIMIT times the number of nodes.\n\nAccepts a numeric value that represents a size in bytes; you can also use a suffix of m or mb for megabytes, or g or gb for gigabytes. If you specify a value with unrecognized formats, subsequent queries fail with an error.',
    type: 'Numeric',
    default: '0 (unlimited)'
  },
  MIN_SPILLABLE_BUFFER_SIZE: {
    description:
      'Specifies the minimum size for a memory buffer used when the spill-to-disk mechanism is activated, for example for queries against a large table with no statistics, or large join operations.\n\nAccepts a numeric value that represents a size in bytes; you can also use a suffix of m or mb for megabytes, or g or gb for gigabytes. If you specify a value with unrecognized formats, subsequent queries fail with an error.',
    type: 'Integer',
    default: '65536 (64 KB)'
  },
  MT_DOP: {
    description:
      'Sets the degree of parallelism used for certain operations that can benefit from multithreaded execution. You can specify values higher than zero to find the ideal balance of response time, memory usage, and CPU usage during statement processing.',
    type: 'Integer; Range from 0 to 64',
    default: '0'
  },
  NUM_NODES: {
    description: 'Limit the number of nodes that process a query, typically during debugging.',
    type: 'Numeric; Only accepts the values 0 (meaning all nodes) or 1 (meaning all work is done on the coordinator node).',
    default: '0'
  },
  NUM_SCANNER_THREADS: {
    description:
      'Maximum number of scanner threads (on each node) used for each query. By default, Impala uses as many cores as are available (one thread per core). You might lower this value if queries are using excessive resources on a busy cluster. Impala imposes a maximum value automatically, so a high value has no practical',
    type: 'Numeric',
    default: '0'
  },
  OPTIMIZE_PARTITION_KEY_SCANS: {
    description:
      'Enables a fast code path for queries that apply simple aggregate functions to partition key columns: MIN(key_column), MAX(key_column), or COUNT(DISTINCT key_column).',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  PARQUET_ANNOTATE_STRINGS_UTF8: {
    description:
      'Causes Impala INSERT and CREATE TABLE AS SELECT statements to write Parquet files that use the UTF-8 annotation for STRING columns.\n\nBy default, Impala represents a STRING column in Parquet as an unannotated binary field.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  PARQUET_FALLBACK_SCHEMA_RESOLUTION: {
    description:
      'Allows Impala to look up columns within Parquet files by column name, rather than column order, when necessary.',
    type: 'integer or string. Allowed values are 0 for POSITION and 1 for NAME.',
    default: '0'
  },
  PARQUET_FILE_SIZE: {
    description:
      'Specifies the maximum size of each Parquet data file produced by Impala INSERT statements.',
    type: 'Numeric, with optional unit specifier.',
    default:
      '0 (produces files with a target size of 256 MB; files might be larger for very wide tables)'
  },
  PREFETCH_MODE: {
    description:
      'Determines whether the prefetching optimization is applied during join query processing.',
    type: 'Numeric (0, 1) or corresponding mnemonic strings (NONE, HT_BUCKET).',
    default: '1 (equivalent to HT_BUCKET)'
  },
  QUERY_TIMEOUT_S: {
    description:
      'Sets the idle query timeout value for the session, in seconds. Queries that sit idle for longer than the timeout value are automatically cancelled. If the system administrator specified the --idle_query_timeout startup option, QUERY_TIMEOUT_S must be smaller than or equal to the --idle_query_timeout value.',
    type: 'Numeric',
    default:
      '0 (no timeout if --idle_query_timeout not in effect; otherwise, use --idle_query_timeout value)'
  },
  REQUEST_POOL: {
    description:
      'The pool or queue name that queries should be submitted to. Only applies when you enable the Impala admission control feature. Specifies the name of the pool used by requests from Impala to the resource manager.',
    type: 'String',
    default:
      'empty (use the user-to-pool mapping defined by an impalad startup option in the Impala configuration file)'
  },
  REPLICA_PREFERENCE: {
    description:
      'The REPLICA_PREFERENCE query option lets you distribute the work more evenly if hotspots and bottlenecks persist. It causes the access cost of all replicas of a data block to be considered equal to or worse than the configured value. This allows Impala to schedule reads to suboptimal replicas (e.g. local in the presence of cached ones) in order to distribute the work across more executor nodes.',
    type: 'Numeric (0, 2, 4) or corresponding mnemonic strings (CACHE_LOCAL, DISK_LOCAL, REMOTE). The gaps in the numeric sequence are to accomodate other intermediate values that might be added in the future.',
    default: '0 (equivalent to CACHE_LOCAL)'
  },
  RUNTIME_BLOOM_FILTER_SIZE: {
    description:
      'Size (in bytes) of Bloom filter data structure used by the runtime filtering feature.',
    type: 'Integer; Maximum 16 MB.',
    default: '1048576 (1 MB)'
  },
  RUNTIME_FILTER_MAX_SIZE: {
    description:
      'The RUNTIME_FILTER_MAX_SIZE query option adjusts the settings for the runtime filtering feature. This option defines the maximum size for a filter, no matter what the estimates produced by the planner are. This value also overrides any lower number specified for the RUNTIME_BLOOM_FILTER_SIZE query option. Filter sizes are rounded up to the nearest power of two.',
    type: 'Integer',
    default: '0 (meaning use the value from the corresponding impalad startup option)'
  },
  RUNTIME_FILTER_MIN_SIZE: {
    description:
      'The RUNTIME_FILTER_MIN_SIZE query option adjusts the settings for the runtime filtering feature. This option defines the minimum size for a filter, no matter what the estimates produced by the planner are. This value also overrides any lower number specified for the RUNTIME_BLOOM_FILTER_SIZE query option. Filter sizes are rounded up to the nearest power of two.',
    type: 'Integer',
    default: '0 (meaning use the value from the corresponding impalad startup option)'
  },
  RUNTIME_FILTER_MODE: {
    description:
      'The RUNTIME_FILTER_MODE query option adjusts the settings for the runtime filtering feature. It turns this feature on and off, and controls how extensively the filters are transmitted between hosts.',
    type: 'Numeric (0, 1, 2) or corresponding mnemonic strings (OFF, LOCAL, GLOBAL).',
    default: '2 (equivalent to GLOBAL); formerly was 1 / LOCAL, in CDH 5.7 / Impala 2.5'
  },
  RUNTIME_FILTER_WAIT_TIME_MS: {
    description:
      'The RUNTIME_FILTER_WAIT_TIME_MS query option adjusts the settings for the runtime filtering feature. It specifies a time in milliseconds that each scan node waits for runtime filters to be produced by other plan fragments.',
    type: 'Integer',
    default: '0 (meaning use the value from the corresponding impalad startup option)'
  },
  S3_SKIP_INSERT_STAGING: {
    description:
      'Speeds up INSERT operations on tables or partitions residing on the Amazon S3 filesystem. The tradeoff is the possibility of inconsistent data left behind if an error occurs partway through the operation.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'true (shown as 1 in output of SET statement)'
  },
  SCHEDULE_RANDOM_REPLICA: {
    description:
      'The SCHEDULE_RANDOM_REPLICA query option fine-tunes the algorithm for deciding which host processes each HDFS data block. It only applies to tables and partitions that are not enabled for the HDFS caching feature.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  SCRATCH_LIMIT: {
    description:
      'Specifies the maximum amount of disk storage, in bytes, that any Impala query can consume on any host using the "spill to disk" mechanism that handles queries that exceed the memory limit.',
    type: 'Numeric, with optional unit specifier',
    default: '-1 (amount of spill space is unlimited)'
  },
  SHUFFLE_DISTINCT_EXPRS: {
    description:
      'The SHUFFLE_DISTINCT_EXPRS query option controls the shuffling behavior when a query has both grouping and distinct expressions. Impala can optionally include the distinct expressions in the hash exchange to spread the data among more nodes. However, this plan requires one more hash exchange phase. It is recommended that you turn off this option if the NDVs of the grouping expressions are high.',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  SYNC_DDL: {
    description:
      'When enabled, causes any DDL operation such as CREATE TABLE or ALTER TABLE to return only when the changes have been propagated to all other Impala nodes in the cluster by the Impala catalog service. That way, if you issue a subsequent CONNECT statement in impala-shell to connect to a different node in the cluster, you can be sure that other node will already recognize any added or changed tables. (The catalog service automatically broadcasts the DDL changes to all nodes automatically, but without this option there could be a period of inconsistency if you quickly switched to another node, such as by issuing a subsequent query through a load-balancing proxy.)',
    type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
    default: 'false (shown as 0 in output of SET statement)'
  },
  TIMEZONE: {
    description:
      'The TIMEZONE query option defines the timezone used for conversions between UTC and the local time. If not set, Impala uses the system time zone where the Coordinator Impalad runs. As query options are not sent to the Coordinator immediately, the timezones are validated only when the query runs.',
    type: 'String, can be a canonical code or a time zone name defined in the IANA Time Zone Database. The value is case-sensitive.',
    default: 'Coordinator Impalad system time zone.'
  },
  TOPN_BYTES_LIMIT: {
    description:
      'The TOPN_BYTES_LIMIT query option places a limit on the amount of estimated memory that Impala can process for top-N queries.',
    type: 'Numeric',
    default: '536870912 (512 MB)'
  }
};
