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

import ko from 'knockout';

const PigFunctions = (function() {
  const EVAL_FUNCTIONS = {
    avg: { signature: 'AVG(%VAR%)', draggable: 'AVG()' },
    concat: { signature: 'CONCAT(%VAR1%, %VAR2%)', draggable: 'CONCAT()' },
    count: { signature: 'COUNT(%VAR%)', draggable: 'COUNT()' },
    count_start: { signature: 'COUNT_START(%VAR%)', draggable: 'COUNT_START()' },
    is_empty: { signature: 'IsEmpty(%VAR%)', draggable: 'IsEmpty()' },
    diff: { signature: 'DIFF(%VAR1%, %VAR2%)', draggable: 'DIFF()' },
    max: { signature: 'MAX(%VAR%)', draggable: 'MAX()' },
    min: { signature: 'MIN(%VAR%)', draggable: 'MIN()' },
    size: { signature: 'SIZE(%VAR%)', draggable: 'SIZE()' },
    sum: { signature: 'SUM(%VAR%)', draggable: 'SUM()' },
    tokenize: { signature: 'TOKENIZE(%VAR%, %DELIM%)', draggable: 'TOKENIZE()' }
  };

  const RELATIONAL_OPERATORS = {
    cogroup: { signature: 'COGROUP %VAR% BY %VAR%', draggable: 'COGROUP %VAR% BY %VAR%' },
    cross: { signature: 'CROSS %VAR1%, %VAR2%;', draggable: 'CROSS %VAR1%, %VAR2%;' },
    distinct: { signature: 'DISTINCT %VAR%;', draggable: 'DISTINCT %VAR%;' },
    filter: { signature: 'FILTER %VAR% BY %COND%', draggable: 'FILTER %VAR% BY %COND%' },
    flatten: { signature: 'FLATTEN(%VAR%)', draggable: 'FLATTEN()' },
    foreach_generate: {
      signature: 'FOREACH %DATA% GENERATE %NEW_DATA%;',
      draggable: 'FOREACH %DATA% GENERATE %NEW_DATA%;'
    },
    foreach: {
      signature: 'FOREACH %DATA% {%NESTED_BLOCK%};',
      draggable: 'FOREACH %DATA% {%NESTED_BLOCK%};'
    },
    group_by: { signature: 'GROUP %VAR% BY %VAR%', draggable: 'GROUP %VAR% BY %VAR%' },
    group_all: { signature: 'GROUP %VAR% ALL', draggable: 'GROUP %VAR% ALL' },
    join: { signature: 'JOIN %VAR% BY ', draggable: 'JOIN %VAR% BY ' },
    limit: { signature: 'LIMIT %VAR% %N%', draggable: 'LIMIT %VAR% %N%' },
    order: { signature: 'ORDER %VAR% BY %FIELD%', draggable: 'ORDER %VAR% BY %FIELD%' },
    sample: { signature: 'SAMPLE %VAR% %SIZE%', draggable: 'SAMPLE %VAR% %SIZE%' },
    split: {
      signature: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%',
      draggable: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%'
    },
    union: { signature: 'UNION %VAR1%, %VAR2%', draggable: 'UNION %VAR1%, %VAR2%' }
  };

  const INPUT_OUTPUT = {
    load: { signature: "LOAD '%FILE%';", draggable: "LOAD '%FILE%';" },
    dump: { signature: 'DUMP %VAR%;', draggable: 'DUMP %VAR%;' },
    store: { signature: 'STORE %VAR% INTO %PATH%;', draggable: 'STORE %VAR% INTO %PATH%;' }
  };

  const DEBUG = {
    explain: { signature: 'EXPLAIN %VAR%;', draggable: 'EXPLAIN %VAR%;' },
    illustrate: { signature: 'ILLUSTRATE %VAR%;', draggable: 'ILLUSTRATE %VAR%;' },
    describe: { signature: 'DESCRIBE %VAR%;', draggable: 'DESCRIBE %VAR%;' }
  };

  const HCATALOG = {
    LOAD: {
      signature: "LOAD '%TABLE%' USING org.apache.hcatalog.pig.HCatLoader();",
      draggable: "LOAD '%TABLE%' USING org.apache.hcatalog.pig.HCatLoader();"
    }
  };

  const MATH_FUNCTIONS = {
    abs: { signature: 'ABS(%VAR%)', draggable: 'ABS()' },
    acos: { signature: 'ACOS(%VAR%)', draggable: 'ACOS()' },
    asin: { signature: 'ASIN(%VAR%)', draggable: 'ASIN()' },
    atan: { signature: 'ATAN(%VAR%)', draggable: 'ATAN()' },
    cbrt: { signature: 'CBRT(%VAR%)', draggable: 'CBRT()' },
    ceil: { signature: 'CEIL(%VAR%)', draggable: 'CEIL()' },
    cos: { signature: 'COS(%VAR%)', draggable: 'COS()' },
    cosh: { signature: 'COSH(%VAR%)', draggable: 'COSH()' },
    exp: { signature: 'EXP(%VAR%)', draggable: 'EXP()' },
    floor: { signature: 'FLOOR(%VAR%)', draggable: 'FLOOR()' },
    log: { signature: 'LOG(%VAR%)', draggable: 'LOG()' },
    log10: { signature: 'LOG10(%VAR%)', draggable: 'LOG10()' },
    random: { signature: 'RANDOM(%VAR%)', draggable: 'RANDOM()' },
    round: { signature: 'ROUND(%VAR%)', draggable: 'ROUND()' },
    sin: { signature: 'SIN(%VAR%)', draggable: 'SIN()' },
    sinh: { signature: 'SINH(%VAR%)', draggable: 'SINH()' },
    sqrt: { signature: 'SQRT(%VAR%)', draggable: 'SQRT()' },
    tan: { signature: 'TAN(%VAR%)', draggable: 'TAN()' },
    tanh: { signature: 'TANH(%VAR%)', draggable: 'TANH()' }
  };

  const TUPLE_BAG_MAP = {
    totuple: { signature: 'TOTUPLE(%VAR%)', draggable: 'TOTUPLE()' },
    tobag: { signature: 'TOBAG(%VAR%)', draggable: 'TOBAG()' },
    tomap: { signature: 'TOMAP(%KEY%, %VALUE%)', draggable: 'TOMAP()' },
    top: { signature: 'TOP(%topN%, %COLUMN%, %RELATION%)', draggable: 'TOP()' }
  };

  const STRING_FUNCTIONS = {
    indexof: {
      signature: "INDEXOF(%STRING%, '%CHARACTER%', %STARTINDEX%)",
      draggable: 'INDEXOF()'
    },
    last_index_of: {
      signature: "LAST_INDEX_OF(%STRING%, '%CHARACTER%', %STARTINDEX%)",
      draggable: 'LAST_INDEX_OF()'
    },
    lower: { signature: 'LOWER(%STRING%)', draggable: 'LOWER()' },
    regex_extract: {
      signature: 'REGEX_EXTRACT(%STRING%, %REGEX%, %INDEX%)',
      draggable: 'REGEX_EXTRACT()'
    },
    regex_extract_all: {
      signature: 'REGEX_EXTRACT_ALL(%STRING%, %REGEX%)',
      draggable: 'REGEX_EXTRACT_ALL()'
    },
    replace: { signature: "REPLACE(%STRING%, '%oldChar%', '%newChar%')", draggable: 'REPLACE()' },
    strsplit: { signature: 'STRSPLIT(%STRING%, %REGEX%, %LIMIT%)', draggable: 'STRSPLIT()' },
    substring: {
      signature: 'SUBSTRING(%STRING%, %STARTINDEX%, %STOPINDEX%)',
      draggable: 'SUBSTRING()'
    },
    trim: { signature: 'TRIM(%STRING%)', draggable: 'TRIM()' },
    ucfirst: { signature: 'UCFIRST(%STRING%)', draggable: 'UCFIRST()' },
    upper: { signature: 'UPPER(%STRING%)', draggable: 'UPPER()' }
  };

  const MACROS = {
    import: { signature: "IMPORT '%PATH_TO_MACRO%';", draggable: "IMPORT '%PATH_TO_MACRO%';" }
  };

  const HBASE = {
    load: {
      signature:
        "LOAD 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')",
      draggable:
        "LOAD 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')"
    },
    store: {
      signature:
        "STORE %VAR% INTO 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')",
      draggable:
        "STORE %VAR% INTO 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')"
    }
  };

  const PYTHON_UDF = {
    register: {
      signature: "REGISTER 'python_udf.py' USING jython AS myfuncs;",
      draggable: "REGISTER 'python_udf.py' USING jython AS myfuncs;"
    }
  };

  const CATEGORIZED_FUNCTIONS = [
    { name: 'Eval', functions: EVAL_FUNCTIONS },
    { name: 'Relational Operators', functions: RELATIONAL_OPERATORS },
    { name: 'Input and Output', functions: INPUT_OUTPUT },
    { name: 'Debug', functions: DEBUG },
    { name: 'HCatalog', functions: HCATALOG },
    { name: 'Math', functions: MATH_FUNCTIONS },
    { name: 'Tuple, Bag and Map', functions: TUPLE_BAG_MAP },
    { name: 'String', functions: STRING_FUNCTIONS },
    { name: 'Macros', functions: MACROS },
    { name: 'HBase', functions: HBASE },
    { name: 'Python UDF', functions: PYTHON_UDF }
  ];

  return {
    CATEGORIZED_FUNCTIONS: CATEGORIZED_FUNCTIONS
  };
})();

const SqlSetOptions = (function() {
  const SET_OPTIONS = {
    hive: {},
    impala: {
      ALLOW_ERASURE_CODED_FILES: {
        description:
          'Use the ALLOW_ERASURE_CODED_FILES query option to enable or disable the support of erasure coded files in Impala. Until Impala is fully tested and certified with erasure coded files, this query option is set to FALSE by default.',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      APPX_COUNT_DISTINCT: {
        description:
          'Allows multiple COUNT(DISTINCT) operations within a single query, by internally rewriting each COUNT(DISTINCT) to use the NDV() function. The resulting count is approximate rather than precise.',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
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
        type:
          'Integer; The allowed values are BROADCAST (equivalent to 0) or SHUFFLE (equivalent to 1).',
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
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      DISABLE_ROW_RUNTIME_FILTERING: {
        description:
          'The DISABLE_ROW_RUNTIME_FILTERING query option reduces the scope of the runtime filtering feature. Queries still dynamically prune partitions, but do not apply the filtering logic to individual rows within partitions.\n\nOnly applies to queries against Parquet tables. For other file formats, Impala only prunes at the level of partitions, not individual rows.',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      DISABLE_STREAMING_PREAGGREGATIONS: {
        description:
          'Turns off the "streaming preaggregation" optimization that is available in CDH 5.7 / Impala 2.5 and higher. This optimization reduces unnecessary work performed by queries that perform aggregation operations on columns with few or no duplicate values, for example DISTINCT id_column or GROUP BY unique_column. If the optimization causes regressions in existing queries that use aggregation functions, you can turn it off as needed by setting this query option.',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      DISABLE_UNSAFE_SPILLS: {
        description:
          'Enable this option if you prefer to have queries fail when they exceed the Impala memory limit, rather than write temporary data to disk.\n\nQueries that "spill" to disk typically complete successfully, when in earlier Impala releases they would have failed. However, queries with exorbitant memory requirements due to missing statistics or inefficient join clauses could become so slow as a result that you would rather have them cancelled automatically and reduce the memory usage through standard Impala tuning techniques.',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
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
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      HBASE_CACHING: {
        description:
          'Setting this option is equivalent to calling the setCaching method of the class org.apache.hadoop.hbase.client.Scan, in an HBase Java application. Helps to control the memory pressure on the HBase RegionServer, in conjunction with the HBASE_CACHE_BLOCKS query option.',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
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
        type:
          'Numeric; Only accepts the values 0 (meaning all nodes) or 1 (meaning all work is done on the coordinator node).',
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
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      PARQUET_ANNOTATE_STRINGS_UTF8: {
        description:
          'Causes Impala INSERT and CREATE TABLE AS SELECT statements to write Parquet files that use the UTF-8 annotation for STRING columns.\n\nBy default, Impala represents a STRING column in Parquet as an unannotated binary field.',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
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
        type:
          'Numeric (0, 2, 4) or corresponding mnemonic strings (CACHE_LOCAL, DISK_LOCAL, REMOTE). The gaps in the numeric sequence are to accomodate other intermediate values that might be added in the future.',
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
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'true (shown as 1 in output of SET statement)'
      },
      SCHEDULE_RANDOM_REPLICA: {
        description:
          'The SCHEDULE_RANDOM_REPLICA query option fine-tunes the algorithm for deciding which host processes each HDFS data block. It only applies to tables and partitions that are not enabled for the HDFS caching feature.',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
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
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      SYNC_DDL: {
        description:
          'When enabled, causes any DDL operation such as CREATE TABLE or ALTER TABLE to return only when the changes have been propagated to all other Impala nodes in the cluster by the Impala catalog service. That way, if you issue a subsequent CONNECT statement in impala-shell to connect to a different node in the cluster, you can be sure that other node will already recognize any added or changed tables. (The catalog service automatically broadcasts the DDL changes to all nodes automatically, but without this option there could be a period of inconsistency if you quickly switched to another node, such as by issuing a subsequent query through a load-balancing proxy.)',
        type:
          'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      TIMEZONE: {
        description:
          'The TIMEZONE query option defines the timezone used for conversions between UTC and the local time. If not set, Impala uses the system time zone where the Coordinator Impalad runs. As query options are not sent to the Coordinator immediately, the timezones are validated only when the query runs.',
        type:
          'String, can be a canonical code or a time zone name defined in the IANA Time Zone Database. The value is case-sensitive.',
        default: 'Coordinator Impalad system time zone.'
      },
      TOPN_BYTES_LIMIT: {
        description:
          'The TOPN_BYTES_LIMIT query option places a limit on the amount of estimated memory that Impala can process for top-N queries.',
        type: 'Numeric',
        default: '536870912 (512 MB)'
      }
    }
  };

  const suggestOptions = function(dialect, completions, category) {
    if (dialect === 'hive' || dialect === 'impala') {
      Object.keys(SET_OPTIONS[dialect]).forEach(name => {
        completions.push({
          category: category,
          value: name,
          meta: '',
          popular: ko.observable(false),
          weightAdjust: 0,
          details: SET_OPTIONS[dialect][name]
        });
      });
    }
  };

  return {
    suggestOptions: suggestOptions
  };
})();

const SqlFunctions = (function() {
  const MATHEMATICAL_FUNCTIONS = {
    hive: {
      abs: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'abs(DOUBLE a)',
        draggable: 'abs()',
        description: 'Returns the absolute value.'
      },
      acos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'acos(DECIMAL|DOUBLE a)',
        draggable: 'acos()',
        description: 'Returns the arccosine of a if -1<=a<=1 or NULL otherwise.'
      },
      asin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'asin(DECIMAL|DOUBLE a)',
        draggable: 'asin()',
        description: 'Returns the arc sin of a if -1<=a<=1 or NULL otherwise.'
      },
      atan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'atan(DECIMAL|DOUBLE a)',
        draggable: 'atan()',
        description: 'Returns the arctangent of a.'
      },
      bin: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'BIGINT' }]],
        signature: 'bin(BIGINT a)',
        draggable: 'bin()',
        description: 'Returns the number in binary format'
      },
      bround: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'INT', optional: true }]],
        signature: 'bround(DOUBLE a [, INT decimals])',
        draggable: 'bround()',
        description:
          'Returns the rounded BIGINT value of a using HALF_EVEN rounding mode with optional decimal places d.'
      },
      cbrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'cbft(DOUBLE a)',
        draggable: 'cbft()',
        description: 'Returns the cube root of a double value.'
      },
      ceil: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'ceil(DOUBLE a)',
        draggable: 'ceil()',
        description: 'Returns the minimum BIGINT value that is equal to or greater than a.'
      },
      ceiling: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'ceiling(DOUBLE a)',
        draggable: 'ceiling()',
        description: 'Returns the minimum BIGINT value that is equal to or greater than a.'
      },
      conv: {
        returnTypes: ['T'],
        arguments: [[{ type: 'BIGINT' }, { type: 'STRING' }], [{ type: 'INT' }], [{ type: 'INT' }]],
        signature: 'conv(BIGINT|STRING a, INT from_base, INT to_base)',
        draggable: 'conv()',
        description: 'Converts a number from a given base to another'
      },
      cos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'cos(DECIMAL|DOUBLE a)',
        draggable: 'cos()',
        description: 'Returns the cosine of a (a is in radians).'
      },
      degrees: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'degrees(DECIMAL|DOUBLE a)',
        draggable: 'degrees()',
        description: 'Converts value of a from radians to degrees.'
      },
      e: {
        returnTypes: ['DOUBLE'],
        arguments: [[]],
        signature: 'e()',
        draggable: 'e()',
        description: 'Returns the value of e.'
      },
      exp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'exp(DECIMAL|DOUBLE a)',
        draggable: 'exp()',
        description: 'Returns e^a where e is the base of the natural logarithm.'
      },
      factorial: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'INT' }]],
        signature: 'factorial(INT a)',
        draggable: 'factorial()',
        description: 'Returns the factorial of a. Valid a is [0..20].'
      },
      floor: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'floor(DOUBLE a)',
        draggable: 'floor()',
        description: 'Returns the maximum BIGINT value that is equal to or less than a.'
      },
      greatest: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'greatest(T a1, T a2, ...)',
        draggable: 'greatest()',
        description:
          'Returns the greatest value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with ">" operator.'
      },
      hex: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'BIGINT' }, { type: 'BINARY' }, { type: 'STRING' }]],
        signature: 'hex(BIGINT|BINARY|STRING a)',
        draggable: 'hex()',
        description:
          'If the argument is an INT or binary, hex returns the number as a STRING in hexadecimal format. Otherwise if the number is a STRING, it converts each character into its hexadecimal representation and returns the resulting STRING.'
      },
      least: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'least(T a1, T a2, ...)',
        draggable: 'least()',
        description:
          'Returns the least value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with "<" operator.'
      },
      ln: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'ln(DECIMAL|DOUBLE a)',
        draggable: 'ln()',
        description: 'Returns the natural logarithm of the argument a'
      },
      log: {
        returnTypes: ['DOUBLE'],
        arguments: [
          [{ type: 'DECIMAL' }, { type: 'DOUBLE' }],
          [{ type: 'DECIMAL' }, { type: 'DOUBLE' }]
        ],
        signature: 'log(DECIMAL|DOUBLE base, DECIMAL|DOUBLE a)',
        draggable: 'log()',
        description: 'Returns the base-base logarithm of the argument a.'
      },
      log10: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'log10(DECIMAL|DOUBLE a)',
        draggable: 'log10()',
        description: 'Returns the base-10 logarithm of the argument a.'
      },
      log2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'log2(DECIMAL|DOUBLE a)',
        draggable: 'log2()',
        description: 'Returns the base-2 logarithm of the argument a.'
      },
      negative: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }]],
        signature: 'negative(T<DOUBLE|INT> a)',
        draggable: 'negative()',
        description: 'Returns -a.'
      },
      pi: {
        returnTypes: ['DOUBLE'],
        arguments: [],
        signature: 'pi()',
        draggable: 'pi()',
        description: 'Returns the value of pi.'
      },
      pmod: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }], [{ type: 'T' }]],
        signature: 'pmod(T<DOUBLE|INT> a, T b)',
        draggable: 'pmod()',
        description: 'Returns the positive value of a mod b'
      },
      positive: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }]],
        signature: 'positive(T<DOUBLE|INT> a)',
        draggable: 'positive()',
        description: 'Returns a.'
      },
      pow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
        signature: 'pow(DOUBLE a, DOUBLE p)',
        draggable: 'pow()',
        description: 'Returns a^p'
      },
      power: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
        signature: 'power(DOUBLE a, DOUBLE p)',
        draggable: 'power()',
        description: 'Returns a^p'
      },
      radians: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'radians(DECIMAL|DOUBLE a)',
        draggable: 'radians()',
        description: 'Converts value of a from degrees to radians.'
      },
      rand: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'INT', optional: true }]],
        signature: 'rand([INT seed])',
        draggable: 'rand()',
        description:
          'Returns a random number (that changes from row to row) that is distributed uniformly from 0 to 1. Specifying the seed will make sure the generated random number sequence is deterministic.'
      },
      round: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'INT', optional: true }]],
        signature: 'round(DOUBLE a [, INT d])',
        draggable: 'round()',
        description: 'Returns the rounded BIGINT value of a or a rounded to d decimal places.'
      },
      shiftleft: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'BIGINT' }, { type: 'INT' }, { type: 'SMALLINT' }, { type: 'TINYINT' }],
          [{ type: 'INT' }]
        ],
        signature: 'shiftleft(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        draggable: 'shiftleft()',
        description:
          'Bitwise left shift. Shifts a b positions to the left. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      shiftright: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'BIGINT' }, { type: 'INT' }, { type: 'SMALLINT' }, { type: 'TINYINT' }],
          [{ type: 'INT' }]
        ],
        signature: 'shiftright(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        draggable: 'shiftright()',
        description:
          'Bitwise right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      shiftrightunsigned: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'BIGINT' }, { type: 'INT' }, { type: 'SMALLINT' }, { type: 'TINYINT' }],
          [{ type: 'INT' }]
        ],
        signature: 'shiftrightunsigned(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        draggable: 'shiftrightunsigned()',
        description:
          'Bitwise unsigned right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      sign: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }]],
        signature: 'sign(T<DOUBLE|INT> a)',
        draggable: 'sign()',
        description:
          "Returns the sign of a as '1.0' (if a is positive) or '-1.0' (if a is negative), '0.0' otherwise. The decimal version returns INT instead of DOUBLE."
      },
      sin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'sin(DECIMAL|DOUBLE a)',
        draggable: 'sin()',
        description: 'Returns the sine of a (a is in radians).'
      },
      sqrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'sqrt(DECIMAL|DOUBLE a)',
        draggable: 'sqrt()',
        description: 'Returns the square root of a'
      },
      tan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
        signature: 'tan(DECIMAL|DOUBLE a)',
        draggable: 'tan()',
        description: 'Returns the tangent of a (a is in radians).'
      },
      unhex: {
        returnTypes: ['BINARY'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'unhex(STRING a)',
        draggable: 'unhex()',
        description:
          'Inverse of hex. Interprets each pair of characters as a hexadecimal number and converts to the byte representation of the number.'
      },
      width_bucket: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'NUMBER' }, { type: 'NUMBER' }, { type: 'NUMBER' }, { type: 'INT' }]],
        signature: 'width_bucket(NUMBER expr, NUMBER min_value, NUMBER max_value, INT num_buckets)',
        draggable: 'width_bucket()',
        description:
          'Returns an integer between 0 and num_buckets+1 by mapping expr into the ith equally sized bucket. Buckets are made by dividing [min_value, max_value] into equally sized regions. If expr < min_value, return 1, if expr > max_value return num_buckets+1. (as of Hive 3.0.0)'
      }
    },
    impala: {
      abs: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'abs(T a)',
        draggable: 'abs()',
        description:
          'Returns the absolute value of the argument. Use this function to ensure all return values are positive. This is different than the positive() function, which returns its argument unchanged (even if the argument was negative).'
      },
      acos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'acos(DOUBLE a)',
        draggable: 'acos()',
        description: 'Returns the arccosine of the argument.'
      },
      asin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'asin(DOUBLE a)',
        draggable: 'asin()',
        description: 'Returns the arcsine of the argument.'
      },
      atan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'atan(DOUBLE a)',
        draggable: 'atan()',
        description: 'Returns the arctangent of the argument.'
      },
      atan2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
        signature: 'atan2(DOUBLE a, DOUBLE b)',
        draggable: 'atan2()',
        description:
          'Returns the arctangent of the two arguments, with the signs of the arguments used to determine the quadrant of the result.'
      },
      bin: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'BIGINT' }]],
        signature: 'bin(BIGINT a)',
        draggable: 'bin()',
        description:
          'Returns the binary representation of an integer value, that is, a string of 0 and 1 digits.'
      },
      ceil: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
        signature: 'ceil(T<DOUBLE|DECIMAL> a)',
        draggable: 'ceil()',
        description: 'Returns the smallest integer that is greater than or equal to the argument.'
      },
      ceiling: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
        signature: 'ceiling(T<DOUBLE|DECIMAL> a)',
        draggable: 'ceiling()',
        description: 'Returns the smallest integer that is greater than or equal to the argument.'
      },
      conv: {
        returnTypes: ['T'],
        arguments: [[{ type: 'BIGINT' }, { type: 'STRING' }], [{ type: 'INT' }], [{ type: 'INT' }]],
        signature: 'conv(T<BIGINT|STRING> a, INT from_base, INT to_base)',
        draggable: 'conv()',
        description:
          'Returns a string representation of an integer value in a particular base. The input value can be a string, for example to convert a hexadecimal number such as fce2 to decimal. To use the return value as a number (for example, when converting to base 10), use CAST() to convert to the appropriate type.'
      },
      cos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'cos(DOUBLE a)',
        draggable: 'cos()',
        description: 'Returns the cosine of the argument.'
      },
      cosh: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'cosh(DOUBLE a)',
        draggable: 'cosh()',
        description: 'Returns the hyperbolic cosine of the argument.'
      },
      cot: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'cot(DOUBLE a)',
        draggable: 'cot()',
        description: 'Returns the cotangent of the argument.'
      },
      dceil: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
        signature: 'dceil(T<DOUBLE|DECIMAL> a)',
        draggable: 'dceil()',
        description: 'Returns the smallest integer that is greater than or equal to the argument.'
      },
      degrees: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'degrees(DOUBLE a)',
        draggable: 'degrees()',
        description: 'Converts argument value from radians to degrees.'
      },
      dexp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'dexp(DOUBLE a)',
        draggable: 'dexp()',
        description: 'Returns the mathematical constant e raised to the power of the argument.'
      },
      dfloor: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
        signature: 'dfloor(T<DOUBLE|DECIMAL> a)',
        draggable: 'dfloor()',
        description: 'Returns the largest integer that is less than or equal to the argument.'
      },
      dlog1: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'dlog1(DOUBLE a)',
        draggable: 'dlog1()',
        description: 'Returns the natural logarithm of the argument.'
      },
      dpow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
        signature: 'dpow(DOUBLE a, DOUBLE p)',
        draggable: 'dpow()',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      dround: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }], [{ type: 'INT', optional: true }]],
        signature: 'dround(DOUBLE a [, INT d]), round(DECIMAL val, INT d)',
        draggable: 'dround()',
        description:
          'Rounds a floating-point value. By default (with a single argument), rounds to the nearest integer. Values ending in .5 are rounded up for positive numbers, down for negative numbers (that is, away from zero). The optional second argument specifies how many digits to leave after the decimal point; values greater than zero produce a floating-point return value rounded to the requested number of digits to the right of the decimal point.'
      },
      dsqrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'dsqrt(DOUBLE a)',
        draggable: 'dsqrt()',
        description: 'Returns the square root of the argument.'
      },
      dtrunc: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
          [{ type: 'NUMBER', optional: true }]
        ],
        signature: 'dtrunc(T<DOUBLE|DECIMAL> a, [NUMBER b])',
        draggable: 'dtrunc()',
        description:
          'Removes some or all fractional digits from a numeric value. With no argument, removes all fractional digits, leaving an integer value. The optional argument specifies the number of fractional digits to include in the return value, and only applies with the argument type is DECIMAL. truncate(), trunc() and dtrunc() are aliases for the same function.'
      },
      e: {
        returnTypes: ['DOUBLE'],
        arguments: [],
        signature: 'e()',
        draggable: 'e()',
        description: 'Returns the mathematical constant e.'
      },
      exp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'exp(DOUBLE a)',
        draggable: 'exp()',
        description: 'Returns the mathematical constant e raised to the power of the argument.'
      },
      factorial: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'T' }]],
        signature: 'factorial(T a)',
        draggable: 'factorial()',
        description:
          'Computes the factorial of an integer value. It works with any integer type. You can use either the factorial() function or the ! operator. The factorial of 0 is 1. Likewise, the factorial() function returns 1 for any negative value. The maximum positive value for the input argument is 20; a value of 21 or greater overflows the range for a BIGINT and causes an error.'
      },
      floor: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
        signature: 'floor(T<DOUBLE|DECIMAL> a)',
        draggable: 'floor()',
        description: 'Returns the largest integer that is less than or equal to the argument.'
      },
      fmod: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'DOUBLE' }, { type: 'DOUBLE' }],
          [{ type: 'FLOAT' }, { type: 'FLOAT' }]
        ],
        signature: 'fmod(DOUBLE a, DOUBLE b), fmod(FLOAT a, FLOAT b)',
        draggable: 'fmod()',
        description: 'Returns the modulus of a floating-point number'
      },
      fpow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
        signature: 'fpow(DOUBLE a, DOUBLE p)',
        draggable: 'fpow()',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      fnv_hash: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'T' }]],
        signature: 'fnv_hash(T a)',
        draggable: 'fnv_hash()',
        description:
          'Returns a consistent 64-bit value derived from the input argument, for convenience of implementing hashing logic in an application.'
      },
      greatest: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'greatest(T a1, T a2, ...)',
        draggable: 'greatest()',
        description: 'Returns the largest value from a list of expressions.'
      },
      hex: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'BIGINT' }, { type: 'STRING' }]],
        signature: 'hex(T<BIGINT|STRING> a)',
        draggable: 'hex()',
        description:
          'Returns the hexadecimal representation of an integer value, or of the characters in a string.'
      },
      is_inf: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'is_inf(DOUBLE a)',
        draggable: 'is_inf()',
        description:
          'Tests whether a value is equal to the special value "inf", signifying infinity.'
      },
      is_nan: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'is_nan(DOUBLE A)',
        draggable: 'is_nan()',
        description:
          'Tests whether a value is equal to the special value "NaN", signifying "not a number".'
      },
      least: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'least(T a1, T a2, ...)',
        draggable: 'least()',
        description: 'Returns the smallest value from a list of expressions.'
      },
      ln: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'ln(DOUBLE a)',
        draggable: 'ln()',
        description: 'Returns the natural logarithm of the argument.'
      },
      log: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
        signature: 'log(DOUBLE base, DOUBLE a)',
        draggable: 'log()',
        description: 'Returns the logarithm of the second argument to the specified base.'
      },
      log10: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'log10(DOUBLE a)',
        draggable: 'log10()',
        description: 'Returns the logarithm of the argument to the base 10.'
      },
      log2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'log2(DOUBLE a)',
        draggable: 'log2()',
        description: 'Returns the logarithm of the argument to the base 2.'
      },
      max_bigint: {
        returnTypes: ['BIGINT'],
        arguments: [],
        signature: 'max_bigint()',
        draggable: 'max_bigint()',
        description: 'Returns the largest value of the associated integral type.'
      },
      max_int: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'max_int()',
        draggable: 'max_int()',
        description: 'Returns the largest value of the associated integral type.'
      },
      max_smallint: {
        returnTypes: ['SMALLINT'],
        arguments: [],
        signature: 'max_smallint()',
        draggable: 'max_smallint()',
        description: 'Returns the largest value of the associated integral type.'
      },
      max_tinyint: {
        returnTypes: ['TINYINT'],
        arguments: [],
        signature: 'max_tinyint()',
        draggable: 'max_tinyint()',
        description: 'Returns the largest value of the associated integral type.'
      },
      min_bigint: {
        returnTypes: ['BIGINT'],
        arguments: [],
        signature: 'min_bigint()',
        draggable: 'min_bigint()',
        description:
          'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_int: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'min_int()',
        draggable: 'min_int()',
        description:
          'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_smallint: {
        returnTypes: ['SMALLINT'],
        arguments: [],
        signature: 'min_smallint()',
        draggable: 'min_smallint()',
        description:
          'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_tinyint: {
        returnTypes: ['TINYINT'],
        arguments: [],
        signature: 'min_tinyint()',
        draggable: 'min_tinyint()',
        description:
          'Returns the smallest value of the associated integral type (a negative number).'
      },
      mod: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'mod(T a, T b)',
        draggable: 'mod()',
        description:
          'Returns the modulus of a number. Equivalent to the % arithmetic operator. Works with any size integer type, any size floating-point type, and DECIMAL with any precision and scale.'
      },
      murmur_hash: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'T' }]],
        signature: 'murmur_hash(T a)',
        draggable: 'murmur_hash()',
        description:
          'Returns a consistent 64-bit value derived from the input argument, for convenience of implementing MurmurHash2 non-cryptographic hash function.'
      },
      negative: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'negative(T a)',
        draggable: 'negative()',
        description:
          'Returns the argument with the sign reversed; returns a positive value if the argument was already negative.'
      },
      pi: {
        returnTypes: ['DOUBLE'],
        arguments: [],
        signature: 'pi()',
        draggable: 'pi()',
        description: 'Returns the constant pi.'
      },
      pmod: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }], [{ type: 'T' }]],
        signature: 'pmod(T<DOUBLE|INT> a, T b)',
        draggable: 'pmod()',
        description: 'Returns the positive modulus of a number.'
      },
      positive: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'positive(T a)',
        draggable: 'positive()',
        description: 'Returns the original argument unchanged (even if the argument is negative).'
      },
      pow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
        signature: 'pow(DOUBLE a, DOUBLE p)',
        draggable: 'pow()',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      power: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
        signature: 'power(DOUBLE a, DOUBLE p)',
        draggable: 'power()',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      precision: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'NUMBER' }]],
        signature: 'precision(numeric_expression)',
        draggable: 'precision()',
        description:
          'Computes the precision (number of decimal digits) needed to represent the type of the argument expression as a DECIMAL value.'
      },
      quotient: {
        returnTypes: ['INT'],
        arguments: [
          [{ type: 'BIGINT' }, { type: 'DOUBLE' }],
          [{ type: 'BIGINT' }, { type: 'DOUBLE' }]
        ],
        signature:
          'quotient(BIGINT numerator, BIGINT denominator), quotient(DOUBLE numerator, DOUBLE denominator)',
        draggable: 'quotient()',
        description:
          'Returns the first argument divided by the second argument, discarding any fractional part. Avoids promoting arguments to DOUBLE as happens with the / SQL operator.'
      },
      radians: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'radians(DOUBLE a)',
        draggable: 'radians()',
        description: 'Converts argument value from degrees to radians.'
      },
      rand: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'INT', optional: true }]],
        signature: 'rand([INT seed])',
        draggable: 'rand()',
        description:
          'Returns a random value between 0 and 1. After rand() is called with a seed argument, it produces a consistent random sequence based on the seed value.'
      },
      random: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'INT', optional: true }]],
        signature: 'random([INT seed])',
        draggable: 'random()',
        description:
          'Returns a random value between 0 and 1. After rand() is called with a seed argument, it produces a consistent random sequence based on the seed value.'
      },
      round: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }], [{ type: 'INT', optional: true }]],
        signature: 'round(DOUBLE a [, INT d]), round(DECIMAL val, INT d)',
        draggable: 'round()',
        description:
          'Rounds a floating-point value. By default (with a single argument), rounds to the nearest integer. Values ending in .5 are rounded up for positive numbers, down for negative numbers (that is, away from zero). The optional second argument specifies how many digits to leave after the decimal point; values greater than zero produce a floating-point return value rounded to the requested number of digits to the right of the decimal point.'
      },
      scale: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'NUMBER' }]],
        signature: 'scale(numeric_expression)',
        draggable: 'scale()',
        description:
          'Computes the scale (number of decimal digits to the right of the decimal point) needed to represent the type of the argument expression as a DECIMAL value.'
      },
      sign: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'sign(DOUBLE a)',
        draggable: 'sign()',
        description: 'Returns -1, 0, or 1 to indicate the signedness of the argument value.'
      },
      sin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'sin(DOUBLE a)',
        draggable: 'sin()',
        description: 'Returns the sine of the argument.'
      },
      sinh: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'sinh(DOUBLE a)',
        draggable: 'sinh()',
        description: 'Returns the hyperbolic sine of the argument.'
      },
      sqrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'sqrt(DOUBLE a)',
        draggable: 'sqrt()',
        description: 'Returns the square root of the argument.'
      },
      tan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'tan(DOUBLE a)',
        draggable: 'tan()',
        description: 'Returns the tangent of the argument.'
      },
      tanh: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'DOUBLE' }]],
        signature: 'tanh(DOUBLE a)',
        draggable: 'tanh()',
        description: 'Returns the tangent of the argument.'
      },
      trunc: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
          [{ type: 'NUMBER', optional: true }]
        ],
        signature: 'trunc(T<DOUBLE|DECIMAL> a, [NUMBER b])',
        draggable: 'trunc()',
        description:
          'Removes some or all fractional digits from a numeric value. With no argument, removes all fractional digits, leaving an integer value. The optional argument specifies the number of fractional digits to include in the return value, and only applies with the argument type is DECIMAL. truncate(), trunc() and dtrunc() are aliases for the same function.'
      },
      truncate: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
          [{ type: 'NUMBER', optional: true }]
        ],
        signature: 'truncate(T<DOUBLE|DECIMAL> a, [NUMBER b])',
        draggable: 'truncate()',
        description:
          'Removes some or all fractional digits from a numeric value. With no argument, removes all fractional digits, leaving an integer value. The optional argument specifies the number of fractional digits to include in the return value, and only applies with the argument type is DECIMAL. truncate(), trunc() and dtrunc() are aliases for the same function.'
      },
      unhex: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'unhex(STRING a)',
        draggable: 'unhex()',
        description:
          'Returns a string of characters with ASCII values corresponding to pairs of hexadecimal digits in the argument.'
      },
      width_bucket: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
          [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
          [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
          [{ type: 'INT' }]
        ],
        signature:
          'width_bucket(DECIMAL expr, DECIMAL min_value, DECIMAL max_value, INT num_buckets)',
        draggable: 'width_bucket()',
        description:
          'Returns the bucket number in which the expr value would fall in the histogram where its range between min_value and max_value is divided into num_buckets buckets of identical sizes.'
      }
    }
  };

  const COMPLEX_TYPE_CONSTRUCTS = {
    hive: {
      array: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'array(val1, val2, ...)',
        draggable: 'array()',
        description: 'Creates an array with the given elements.'
      },
      create_union: {
        returnTypes: ['UNION'],
        arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true }]],
        signature: 'create_union(tag, val1, val2, ...)',
        draggable: 'create_union()',
        description:
          'Creates a union type with the value that is being pointed to by the tag parameter.'
      },
      map: {
        returnTypes: ['MAP'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'map(key1, value1, ...)',
        draggable: 'map()',
        description: 'Creates a map with the given key/value pairs.'
      },
      named_struct: {
        returnTypes: ['STRUCT'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'named_struct(name1, val1, ...)',
        draggable: 'named_struct()',
        description: 'Creates a struct with the given field names and values.'
      },
      struct: {
        returnTypes: ['STRUCT'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'struct(val1, val2, ...)',
        draggable: 'struct()',
        description:
          'Creates a struct with the given field values. Struct field names will be col1, col2, ....'
      }
    },
    impala: {}
  };

  const AGGREGATE_FUNCTIONS = {
    generic: {
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'T' }]],
        signature: 'count(col)',
        draggable: 'count()',
        description:
          'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL.'
      },
      sum: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'sum(col)',
        draggable: 'sum()',
        description:
          'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'
      },
      max: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'max(col)',
        draggable: 'max()',
        description: 'Returns the maximum value of the column in the group.'
      },
      min: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'min(col)',
        draggable: 'min()',
        description: 'Returns the minimum of the column in the group.'
      }
    },
    hive: {
      avg: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'avg(col)',
        draggable: 'avg()',
        description:
          'Returns the average of the elements in the group or the average of the distinct values of the column in the group.'
      },
      collect_set: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'T' }]],
        signature: 'collect_set(col)',
        draggable: 'collect_set()',
        description: 'Returns a set of objects with duplicate elements eliminated.'
      },
      collect_list: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'T' }]],
        signature: 'collect_list(col)',
        draggable: 'collect_list()',
        description: 'Returns a list of objects with duplicates. (As of Hive 0.13.0.)'
      },
      corr: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'corr(col1, col2)',
        draggable: 'corr()',
        description:
          'Returns the Pearson coefficient of correlation of a pair of a numeric columns in the group.'
      },
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'T' }]],
        signature: 'count([DISTINCT] col)',
        draggable: 'count()',
        description:
          'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL. count(DISTINCT expr[, expr]) - Returns the number of rows for which the supplied expression(s) are unique and non-NULL. Execution of this can be optimized with hive.optimize.distinct.rewrite.'
      },
      covar_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'covar_pop(col1, col2)',
        draggable: 'covar_pop()',
        description: 'Returns the population covariance of a pair of numeric columns in the group.'
      },
      covar_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'covar_samp(col1, col2)',
        draggable: 'covar_samp()',
        description: 'Returns the sample covariance of a pair of a numeric columns in the group.'
      },
      histogram_numeric: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'histogram_numeric(col, b)',
        draggable: 'histogram_numeric()',
        description:
          'Computes a histogram of a numeric column in the group using b non-uniformly spaced bins. The output is an array of size b of double-valued (x,y) coordinates that represent the bin centers and heights.'
      },
      max: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'max(col)',
        draggable: 'max()',
        description: 'Returns the maximum value of the column in the group.'
      },
      min: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'min(col)',
        draggable: 'min()',
        description: 'Returns the minimum of the column in the group.'
      },
      ntile: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'INT' }]],
        signature: 'ntile(INT x)',
        draggable: 'ntile()',
        description:
          'Divides an ordered partition into x groups called buckets and assigns a bucket number to each row in the partition. This allows easy calculation of tertiles, quartiles, deciles, percentiles and other common summary statistics. (As of Hive 0.11.0.)'
      },
      percentile: {
        returnTypes: ['DOUBLE', 'ARRAY'],
        arguments: [[{ type: 'BIGINT' }], [{ type: 'ARRAY' }, { type: 'DOUBLE' }]],
        signature:
          'percentile(BIGINT col, p), array<DOUBLE> percentile(BIGINT col, array(p1 [, p2]...))',
        draggable: 'percentile()',
        description:
          'Returns the exact pth percentile (or percentiles p1, p2, ..) of a column in the group (does not work with floating point types). p must be between 0 and 1. NOTE: A true percentile can only be computed for integer values. Use PERCENTILE_APPROX if your input is non-integral.'
      },
      percentile_approx: {
        returnTypes: ['DOUBLE', 'ARRAY'],
        arguments: [
          [{ type: 'DOUBLE' }],
          [{ type: 'DOUBLE' }, { type: 'ARRAY' }],
          [{ type: 'BIGINT', optional: true }]
        ],
        signature:
          'percentile_approx(DOUBLE col, p, [, B]), array<DOUBLE> percentile_approx(DOUBLE col, array(p1 [, p2]...), [, B])',
        draggable: 'percentile_approx()',
        description:
          'Returns an approximate pth percentile (or percentiles p1, p2, ..) of a numeric column (including floating point types) in the group. The B parameter controls approximation accuracy at the cost of memory. Higher values yield better approximations, and the default is 10,000. When the number of distinct values in col is smaller than B, this gives an exact percentile value.'
      },
      regr_avgx: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_avgx(T independent, T dependent)',
        draggable: 'regr_avgx()',
        description: 'Equivalent to avg(dependent). As of Hive 2.2.0.'
      },
      regr_avgy: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_avgy(T independent, T dependent)',
        draggable: 'regr_avgy()',
        description: 'Equivalent to avg(dependent). As of Hive 2.2.0.'
      },
      regr_count: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_count(T independent, T dependent)',
        draggable: 'regr_count()',
        description:
          'Returns the number of non-null pairs used to fit the linear regression line. As of Hive 2.2.0.'
      },
      regr_intercept: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_intercept(T independent, T dependent)',
        draggable: 'regr_intercept()',
        description:
          'Returns the y-intercept of the linear regression line, i.e. the value of b in the equation dependent = a * independent + b. As of Hive 2.2.0.'
      },
      regr_r2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_r2(T independent, T dependent)',
        draggable: 'regr_r2()',
        description:
          'Returns the coefficient of determination for the regression. As of Hive 2.2.0.'
      },
      regr_slope: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_slope(T independent, T dependent)',
        draggable: 'regr_slope()',
        description:
          'Returns the slope of the linear regression line, i.e. the value of a in the equation dependent = a * independent + b. As of Hive 2.2.0.'
      },
      regr_sxx: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_sxx(T independent, T dependent)',
        draggable: 'regr_sxx()',
        description:
          'Equivalent to regr_count(independent, dependent) * var_pop(dependent). As of Hive 2.2.0.'
      },
      regr_sxy: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_sxy(T independent, T dependent)',
        draggable: 'regr_sxy()',
        description:
          'Equivalent to regr_count(independent, dependent) * covar_pop(independent, dependent). As of Hive 2.2.0.'
      },
      regr_syy: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'regr_syy(T independent, T dependent)',
        draggable: 'regr_syy()',
        description:
          'Equivalent to regr_count(independent, dependent) * var_pop(independent). As of Hive 2.2.0.'
      },
      stddev_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'stddev_pop(col)',
        draggable: 'stddev_pop()',
        description: 'Returns the standard deviation of a numeric column in the group.'
      },
      stddev_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'stddev_samp(col)',
        draggable: 'stddev_samp()',
        description:
          'Returns the unbiased sample standard deviation of a numeric column in the group.'
      },
      sum: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'sum(col)',
        draggable: 'sum()',
        description:
          'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'
      },
      variance: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'variance(col)',
        draggable: 'variance()',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'var_pop(col)',
        draggable: 'var_pop()',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'var_samp(col)',
        draggable: 'var_samp()',
        description: 'Returns the unbiased sample variance of a numeric column in the group.'
      }
    },
    impala: {
      appx_median: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'appx_median([DISTINCT|ALL] T col)',
        draggable: 'appx_median()',
        description:
          'An aggregate function that returns a value that is approximately the median (midpoint) of values in the set of input values.'
      },
      avg: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'NUMBER' }]],
        signature: 'avg([DISTINCT|ALL] col)',
        draggable: 'avg()',
        description:
          'An aggregate function that returns the average value from a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to AVG are NULL, AVG returns NULL.'
      },
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'T' }]],
        signature: 'count([DISTINCT|ALL] col)',
        draggable: 'count()',
        description:
          'An aggregate function that returns the number of rows, or the number of non-NULL rows.'
      },
      group_concat: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'T' }], [{ type: 'STRING', optional: true }]],
        signature: 'group_concat([ALL] col [, separator])',
        draggable: 'group_concat()',
        description:
          'An aggregate function that returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values. The default separator is a comma followed by a space.'
      },
      max: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'max([DISTINCT | ALL] T col)',
        draggable: 'max()',
        description:
          'An aggregate function that returns the maximum value from a set of numbers. Opposite of the MIN function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MAX are NULL, MAX returns NULL.'
      },
      min: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'min([DISTINCT | ALL] T col)',
        draggable: 'min()',
        description:
          'An aggregate function that returns the minimum value from a set of numbers. Opposite of the MAX function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, MIN returns NULL.'
      },
      ndv: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'ndv([DISTINCT | ALL] col)',
        draggable: 'ndv()',
        description:
          'An aggregate function that returns an approximate value similar to the result of COUNT(DISTINCT col), the "number of distinct values". It is much faster than the combination of COUNT and DISTINCT, and uses a constant amount of memory and thus is less memory-intensive for columns with high cardinality.'
      },
      stddev: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'stddev([DISTINCT | ALL] col)',
        draggable: 'stddev()',
        description: 'Returns the standard deviation of a numeric column in the group.'
      },
      stddev_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'stddev_pop([DISTINCT | ALL] col)',
        draggable: 'stddev_pop()',
        description: 'Returns the population standard deviation of a numeric column in the group.'
      },
      stddev_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'stddev_samp([DISTINCT | ALL] col)',
        draggable: 'stddev_samp()',
        description:
          'Returns the unbiased sample standard deviation of a numeric column in the group.'
      },
      sum: {
        returnTypes: ['BIGINT', 'DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'sum([DISTINCT | ALL] col)',
        draggable: 'sum()',
        description:
          'An aggregate function that returns the sum of a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, SUM returns NULL.'
      },
      variance: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'variance([DISTINCT | ALL] col)',
        draggable: 'variance()',
        description:
          'An aggregate function that returns the variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      variance_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'variance_pop([DISTINCT | ALL] col)',
        draggable: 'variance_pop()',
        description:
          'An aggregate function that returns the population variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      variance_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'variance_samp([DISTINCT | ALL] col)',
        draggable: 'variance_samp()',
        description:
          'An aggregate function that returns the sample variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      var_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'var_pop(col)',
        draggable: 'var_pop()',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'T' }]],
        signature: 'var_samp(col)',
        draggable: 'var_samp()',
        description: 'Returns the unbiased sample variance of a numeric column in the group.'
      }
    }
  };

  const COLLECTION_FUNCTIONS = {
    hive: {
      array_contains: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'ARRAY' }], [{ type: 'T' }]],
        signature: 'array_contains(Array<T> a, val)',
        draggable: 'array_contains()',
        description: 'Returns TRUE if the array contains value.'
      },
      map_keys: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'MAP' }]],
        signature: 'array<K.V> map_keys(Map<K.V> a)',
        draggable: 'array<K.V> map_keys()',
        description: 'Returns an unordered array containing the keys of the input map.'
      },
      map_values: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'MAP' }]],
        signature: 'array<K.V> map_values(Map<K.V> a)',
        draggable: 'array<K.V> map_values()',
        description: 'Returns an unordered array containing the values of the input map.'
      },
      size: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'ARRAY' }, { type: 'MAP' }]],
        signature: 'size(Map<K.V>|Array<T> a)',
        draggable: 'size()',
        description: 'Returns the number of elements in the map or array type.'
      },
      sort_array: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'ARRAY' }]],
        signature: 'sort_array(Array<T> a)',
        draggable: 'sort_array()',
        description:
          'Sorts the input array in ascending order according to the natural ordering of the array elements and returns it.'
      }
    },
    impala: {}
  };

  const TYPE_CONVERSION_FUNCTIONS = {
    hive: {
      binary: {
        returnTypes: ['BINARY'],
        arguments: [[{ type: 'BINARY' }, { type: 'STRING' }]],
        signature: 'binary(BINARY|STRING a)',
        draggable: 'binary()',
        description: 'Casts the parameter into a binary.'
      },
      cast: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'cast(a as T)',
        draggable: 'cast()',
        description:
          "Converts the results of the expression expr to type T. For example, cast('1' as BIGINT) will convert the string '1' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string."
      }
    },
    impala: {
      cast: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'cast(a as T)',
        draggable: 'cast()',
        description:
          "Converts the results of the expression expr to type T. For example, cast('1' as BIGINT) will convert the string '1' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string."
      },
      typeof: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'T' }]],
        signature: 'typeof(T a)',
        draggable: 'typeof()',
        description:
          'Returns the name of the data type corresponding to an expression. For types with extra attributes, such as length for CHAR and VARCHAR, or precision and scale for DECIMAL, includes the full specification of the type.'
      }
    }
  };

  const DATE_FUNCTIONS = {
    hive: {
      add_months: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }],
          [{ type: 'INT' }]
        ],
        signature: 'add_months(DATE|STRING|TIMESTAMP start_date, INT num_months)',
        draggable: 'add_months()',
        description:
          'Returns the date that is num_months after start_date (as of Hive 1.1.0). start_date is a string, date or timestamp. num_months is an integer. The time part of start_date is ignored. If start_date is the last day of the month or if the resulting month has fewer days than the day component of start_date, then the result is the last day of the resulting month. Otherwise, the result has the same day component as start_date.'
      },
      current_date: {
        returnTypes: ['DATE'],
        arguments: [],
        signature: 'current_date',
        draggable: 'current_date',
        description:
          'Returns the current date at the start of query evaluation (as of Hive 1.2.0). All calls of current_date within the same query return the same value.'
      },
      current_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'current_timestamp()',
        draggable: 'current_timestamp()',
        description:
          'Returns the current timestamp at the start of query evaluation (as of Hive 1.2.0). All calls of current_timestamp within the same query return the same value.'
      },
      datediff: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'datediff(STRING enddate, STRING startdate)',
        draggable: 'datediff()',
        description:
          "Returns the number of days from startdate to enddate: datediff('2009-03-01', '2009-02-27') = 2."
      },
      date_add: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DATE' }, { type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'date_add(DATE startdate, INT days)',
        draggable: 'date_add()',
        description:
          "Adds a number of days to startdate: date_add('2008-12-31', 1) = '2009-01-01'. T = pre 2.1.0: STRING, 2.1.0 on: DATE"
      },
      date_format: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }],
          [{ type: 'STRING' }]
        ],
        signature: 'date_format(DATE|TIMESTAMP|STRING ts, STRING fmt)',
        draggable: 'date_format()',
        description:
          "Converts a date/timestamp/string to a value of string in the format specified by the date format fmt (as of Hive 1.2.0). Supported formats are Java SimpleDateFormat formats – https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html. The second argument fmt should be constant. Example: date_format('2015-04-08', 'y') = '2015'."
      },
      date_sub: {
        returnTypes: ['T'],
        arguments: [[{ type: 'DATE' }, { type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'date_sub(DATE startdate, INT days)',
        draggable: 'date_sub()',
        description:
          "Subtracts a number of days to startdate: date_sub('2008-12-31', 1) = '2008-12-30'. T = pre 2.1.0: STRING, 2.1.0 on: DATE"
      },
      day: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'day(STRING date)',
        draggable: 'day()',
        description:
          "Returns the day part of a date or a timestamp string: day('1970-11-01 00:00:00') = 1, day('1970-11-01') = 1."
      },
      dayofmonth: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'dayofmonth(STRING date)',
        draggable: 'dayofmonth()',
        description:
          "Returns the day part of a date or a timestamp string: dayofmonth('1970-11-01 00:00:00') = 1, dayofmonth('1970-11-01') = 1."
      },
      extract: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'extract(field FROM source)',
        draggable: 'extract()',
        description:
          'Retrieve fields such as days or hours from source (as of Hive 2.2.0). Source must be a date, timestamp, interval or a string that can be converted into either a date or timestamp. Supported fields include: day, dayofweek, hour, minute, month, quarter, second, week and year.'
      },
      from_unixtime: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'BIGINT' }], [{ type: 'STRING', optional: true }]],
        signature: 'from_unixtime(BIGINT unixtime [, STRING format])',
        draggable: 'from_unixtime()',
        description:
          "Converts time string in format yyyy-MM-dd HH:mm:ss to Unix timestamp (in seconds), using the default timezone and the default locale, return 0 if fail: unix_timestamp('2009-03-20 11:30:01') = 1237573801"
      },
      from_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'T' }], [{ type: 'STRING' }]],
        signature: 'from_utc_timestamp(T a, STRING timezone)',
        draggable: 'from_utc_timestamp()',
        description:
          "Assumes given timestamp is UTC and converts to given timezone (as of Hive 0.8.0). For example, from_utc_timestamp('1970-01-01 08:00:00','PST') returns 1970-01-01 00:00:00"
      },
      hour: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'hour(STRING date)',
        draggable: 'hour()',
        description:
          "Returns the hour of the timestamp: hour('2009-07-30 12:58:59') = 12, hour('12:58:59') = 12."
      },
      last_day: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'last_day(STRING date)',
        draggable: 'last_day()',
        description:
          "Returns the last day of the month which the date belongs to (as of Hive 1.1.0). date is a string in the format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-dd'. The time part of date is ignored."
      },
      minute: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'minute(STRING date)',
        draggable: 'minute()',
        description: 'Returns the minute of the timestamp.'
      },
      month: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'month(STRING date)',
        draggable: 'month()',
        description:
          "Returns the month part of a date or a timestamp string: month('1970-11-01 00:00:00') = 11, month('1970-11-01') = 11."
      },
      months_between: {
        returnTypes: ['DOUBLE'],
        arguments: [
          [{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }],
          [{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }]
        ],
        signature: 'months_between(DATE|TIMESTAMP|STRING date1, DATE|TIMESTAMP|STRING date2)',
        draggable: 'months_between()',
        description:
          "Returns number of months between dates date1 and date2 (as of Hive 1.2.0). If date1 is later than date2, then the result is positive. If date1 is earlier than date2, then the result is negative. If date1 and date2 are either the same days of the month or both last days of months, then the result is always an integer. Otherwise the UDF calculates the fractional portion of the result based on a 31-day month and considers the difference in time components date1 and date2. date1 and date2 type can be date, timestamp or string in the format 'yyyy-MM-dd' or 'yyyy-MM-dd HH:mm:ss'. The result is rounded to 8 decimal places. Example: months_between('1997-02-28 10:30:00', '1996-10-30') = 3.94959677"
      },
      next_day: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'next_day(STRING start_date, STRING day_of_week)',
        draggable: 'next_day()',
        description:
          "Returns the first date which is later than start_date and named as day_of_week (as of Hive 1.2.0). start_date is a string/date/timestamp. day_of_week is 2 letters, 3 letters or full name of the day of the week (e.g. Mo, tue, FRIDAY). The time part of start_date is ignored. Example: next_day('2015-01-14', 'TU') = 2015-01-20."
      },
      quarter: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }]],
        signature: 'quarter(DATE|TIMESTAMP|STRING a)',
        draggable: 'quarter()',
        description:
          "Returns the quarter of the year for a date, timestamp, or string in the range 1 to 4. Example: quarter('2015-04-08') = 2."
      },
      second: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'second(STRING date)',
        draggable: 'second()',
        description: 'Returns the second of the timestamp.'
      },
      to_date: {
        returnTypes: ['T'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'to_date(STRING timestamp)',
        draggable: 'to_date()',
        description:
          "Returns the date part of a timestamp string, example to_date('1970-01-01 00:00:00'). T = pre 2.1.0: STRING 2.1.0 on: DATE"
      },
      to_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'T' }], [{ type: 'STRING' }]],
        signature: 'to_utc_timestamp(T a, STRING timezone)',
        draggable: 'to_utc_timestamp()',
        description:
          "Assumes given timestamp is in given timezone and converts to UTC (as of Hive 0.8.0). For example, to_utc_timestamp('1970-01-01 00:00:00','PST') returns 1970-01-01 08:00:00."
      },
      trunc: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'trunc(STRING date, STRING format)',
        draggable: 'trunc()',
        description:
          "Returns date truncated to the unit specified by the format (as of Hive 1.2.0). Supported formats: MONTH/MON/MM, YEAR/YYYY/YY. Example: trunc('2015-03-17', 'MM') = 2015-03-01."
      },
      unix_timestamp: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'STRING', optional: true }], [{ type: 'STRING', optional: true }]],
        signature: 'unix_timestamp([STRING date [, STRING pattern]])',
        draggable: 'unix_timestamp()',
        description:
          "Convert time string with given pattern to Unix time stamp (in seconds), return 0 if fail: unix_timestamp('2009-03-20', 'yyyy-MM-dd') = 1237532400."
      },
      weekofyear: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'weekofyear(STRING date)',
        draggable: 'weekofyear()',
        description:
          "Returns the week number of a timestamp string: weekofyear('1970-11-01 00:00:00') = 44, weekofyear('1970-11-01') = 44."
      },
      year: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'year(STRING date)',
        draggable: 'year()',
        description:
          "Returns the year part of a date or a timestamp string: year('1970-01-01 00:00:00') = 1970, year('1970-01-01') = 1970"
      }
    },
    impala: {
      add_months: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'add_months(TIMESTAMP date, BIGINT|INT months)',
        draggable: 'add_months()',
        description: 'Returns the specified date and time plus some number of months.'
      },
      adddate: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'adddate(TIMESTAMP startdate, BIGINT|INT days)',
        draggable: 'adddate()',
        description:
          'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      current_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'current_timestamp()',
        draggable: 'current_timestamp()',
        description: 'Alias for the now() function.'
      },
      date_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'INT' }]],
        signature:
          'date_add(TIMESTAMP startdate, INT days), date_add(TIMESTAMP startdate, interval_expression)',
        draggable: 'date_add()',
        description:
          'Adds a specified number of days to a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.'
      },
      date_part: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'STRING' }], [{ type: 'TIMESTAMP' }]],
        signature: 'date_part(STRING unit, TIMESTAMP timestamp)',
        draggable: 'date_part()',
        description:
          'Similar to EXTRACT(), with the argument order reversed. Supports the same date and time units as EXTRACT(). For compatibility with SQL code containing vendor extensions.'
      },
      date_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'INT' }]],
        signature:
          'date_sub(TIMESTAMP startdate, INT days), date_sub(TIMESTAMP startdate, interval_expression)',
        draggable: 'date_sub()',
        description:
          'Subtracts a specified number of days from a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.'
      },
      date_trunc: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'STRING' }], [{ type: 'TIMESTAMP' }]],
        signature: 'date_trunc(STRING unit, TIMESTAMP timestamp)',
        draggable: 'date_trunc()',
        description:
          "Truncates a TIMESTAMP value to the specified precision. The unit argument value for truncating TIMESTAMP values is not case-sensitive. This argument string can be one of: 'microseconds', 'milliseconds', 'second', 'minute', 'hour', 'day', 'week', 'month', 'year', 'decade', 'century' or 'millennium'."
      },
      datediff: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'TIMESTAMP' }]],
        signature: 'datediff(TIMESTAMP enddate, TIMESTAMP startdate)',
        draggable: 'datediff()',
        description: 'Returns the number of days between two TIMESTAMP values.'
      },
      day: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'day(TIMESTAMP date)',
        draggable: 'day()',
        description:
          'Returns the day field from the date portion of a TIMESTAMP. The value represents the day of the month, therefore is in the range 1-31, or less for months without 31 days.'
      },
      dayname: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'dayname(TIMESTAMP date)',
        draggable: 'dayname()',
        description:
          "Returns the day field from a TIMESTAMP value, converted to the string corresponding to that day name. The range of return values is 'Sunday' to 'Saturday'. Used in report-generating queries, as an alternative to calling dayofweek() and turning that numeric return value into a string using a CASE expression."
      },
      dayofmonth: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'dayofmonth(TIMESTAMP date)',
        draggable: 'dayofmonth()',
        description:
          'Returns the day field from the date portion of a TIMESTAMP. The value represents the day of the month, therefore is in the range 1-31, or less for months without 31 days.'
      },
      dayofweek: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'dayofweek(TIMESTAMP date)',
        draggable: 'dayofweek()',
        description:
          'Returns the day field from the date portion of a TIMESTAMP, corresponding to the day of the week. The range of return values is 1 (Sunday) to 7 (Saturday).'
      },
      dayofyear: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'dayofyear(TIMESTAMP date)',
        draggable: 'dayofyear()',
        description:
          'Returns the day field from a TIMESTAMP value, corresponding to the day of the year. The range of return values is 1 (January 1) to 366 (December 31 of a leap year).'
      },
      days_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'days_add(TIMESTAMP startdate, BIGINT|INT days)',
        draggable: 'days_add()',
        description:
          'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      days_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'days_sub(TIMESTAMP startdate, BIGINT|INT days)',
        draggable: 'days_sub()',
        description:
          'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      extract: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
        signature: 'extract(TIMESTAMP date, STRING unit), extract(STRING unit FROM TIMESTAMP date)',
        draggable: 'extract()',
        description: 'Returns one of the numeric date or time fields from a TIMESTAMP value.'
      },
      from_timestamp: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
        signature: 'from_timestamp(TIMESTAMP val, STRING format)',
        draggable: 'from_timestamp()',
        description:
          "Converts a specified timestamp to a string with the given format. Example: from_timestamp(cast('1999-01-01 10:10:10' as timestamp), 'yyyy-MM-dd')\" results in \"1999-01-01\""
      },
      from_unixtime: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'BIGINT' }], [{ type: 'STRING', optional: true }]],
        signature: 'from_unixtime(BIGINT unixtime [, STRING format])',
        draggable: 'from_unixtime()',
        description:
          'Converts the number of seconds from the Unix epoch to the specified time into a string in the local time zone.'
      },
      from_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
        signature: 'from_utc_timestamp(TIMESTAMP date, STRING timezone)',
        draggable: 'from_utc_timestamp()',
        description:
          'Converts a specified UTC timestamp value into the appropriate value for a specified time zone.'
      },
      hour: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'hour(TIMESTAMP date)',
        draggable: 'hour()',
        description: 'Returns the hour field from a TIMESTAMP field.'
      },
      hours_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'hours_add(TIMESTAMP date, BIGINT|INT hours)',
        draggable: 'hours_add()',
        description: 'Returns the specified date and time plus some number of hours.'
      },
      hours_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'hours_sub(TIMESTAMP date, BIGINT|INT hours)',
        draggable: 'hours_sub()',
        description: 'Returns the specified date and time minus some number of hours.'
      },
      int_months_between: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'TIMESTAMP' }]],
        signature: 'int_months_between(TIMESTAMP newer, TIMESTAMP older)',
        draggable: 'int_months_between()',
        description:
          'Returns the number of months between the date portions of two TIMESTAMP values, as an INT representing only the full months that passed.'
      },
      last_day: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'last_day(TIMESTAMP t)',
        draggable: 'last_day()',
        description:
          'Returns a TIMESTAMP corresponding to the beginning of the last calendar day in the same month as the TIMESTAMP argument.'
      },
      microseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'microseconds_add(TIMESTAMP date, BIGINT|INT microseconds)',
        draggable: 'microseconds_add()',
        description: 'Returns the specified date and time plus some number of microseconds.'
      },
      microseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'microseconds_sub(TIMESTAMP date, BIGINT|INT microseconds)',
        draggable: 'microseconds_sub()',
        description: 'Returns the specified date and time minus some number of microseconds.'
      },
      millisecond: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'millisecond(TIMESTAMP date)',
        draggable: 'millisecond()',
        description: 'Returns the millisecond portion of a TIMESTAMP value.'
      },
      milliseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'milliseconds_add(TIMESTAMP date, BIGINT|INT milliseconds)',
        draggable: 'milliseconds_add()',
        description: 'Returns the specified date and time plus some number of milliseconds.'
      },
      milliseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'milliseconds_sub(TIMESTAMP date, BIGINT|INT milliseconds)',
        draggable: 'milliseconds_sub()',
        description: 'Returns the specified date and time minus some number of milliseconds.'
      },
      minute: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'minute(TIMESTAMP date)',
        draggable: 'minute()',
        description: 'Returns the minute field from a TIMESTAMP value.'
      },
      minutes_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'minutes_add(TIMESTAMP date, BIGINT|INT minutes)',
        draggable: 'minutes_add()',
        description: 'Returns the specified date and time plus some number of minutes.'
      },
      minutes_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'minutes_sub(TIMESTAMP date, BIGINT|INT minutes)',
        draggable: 'minutes_sub()',
        description: 'Returns the specified date and time minus some number of minutes.'
      },
      month: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'month(TIMESTAMP date)',
        draggable: 'month()',
        description:
          'Returns the month field, represented as an integer, from the date portion of a TIMESTAMP.'
      },
      monthname: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'monthname(TIMESTAMP date)',
        draggable: 'monthname()',
        description:
          'Returns the month field from TIMESTAMP value, converted to the string corresponding to that month name.'
      },
      months_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'months_add(TIMESTAMP date, BIGINT|INT months)',
        draggable: 'months_add()',
        description: 'Returns the specified date and time plus some number of months.'
      },
      months_between: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'TIMESTAMP' }]],
        signature: 'months_between(TIMESTAMP newer, TIMESTAMP older)',
        draggable: 'months_between()',
        description:
          'Returns the number of months between the date portions of two TIMESTAMP values. Can include a fractional part representing extra days in addition to the full months between the dates. The fractional component is computed by dividing the difference in days by 31 (regardless of the month).'
      },
      months_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'months_sub(TIMESTAMP date, BIGINT|INT months)',
        draggable: 'months_sub()',
        description: 'Returns the specified date and time minus some number of months.'
      },
      nanoseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'nanoseconds_add(TIMESTAMP date, BIGINT|INT nanoseconds)',
        draggable: 'nanoseconds_add()',
        description: 'Returns the specified date and time plus some number of nanoseconds.'
      },
      nanoseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'nanoseconds_sub(TIMESTAMP date, BIGINT|INT nanoseconds)',
        draggable: 'nanoseconds_sub()',
        description: 'Returns the specified date and time minus some number of nanoseconds.'
      },
      next_day: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
        signature: 'next_day(TIMESTAMP date, STRING weekday)',
        draggable: 'next_day()',
        description:
          'Returns the date of the weekday that follows the specified date. The weekday parameter is case-insensitive. The following values are accepted for weekday: "Sunday"/"Sun", "Monday"/"Mon", "Tuesday"/"Tue", "Wednesday"/"Wed", "Thursday"/"Thu", "Friday"/"Fri", "Saturday"/"Sat".'
      },
      now: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'now()',
        draggable: 'now()',
        description:
          'Returns the current date and time (in the local time zone) as a timestamp value.'
      },
      quarter: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'quarter(TIMESTAMP date)',
        draggable: 'quarter()',
        description:
          'Returns the quarter in the input TIMESTAMP expression as an integer value, 1, 2, 3, or 4, where 1 represents January 1 through March 31.'
      },
      second: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'second(TIMESTAMP date)',
        draggable: 'second()',
        description: 'Returns the second field from a TIMESTAMP value.'
      },
      seconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'seconds_add(TIMESTAMP date, BIGINT|INT seconds)',
        draggable: 'seconds_add()',
        description: 'Returns the specified date and time plus some number of seconds.'
      },
      seconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'seconds_sub(TIMESTAMP date, BIGINT|INT seconds)',
        draggable: 'seconds_sub()',
        description: 'Returns the specified date and time minus some number of seconds.'
      },
      subdate: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'subdate(TIMESTAMP startdate, BIGINT|INT days)',
        draggable: 'subdate()',
        description:
          'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      timeofday: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'timeofday()',
        draggable: 'timeofday()',
        description:
          'Returns a string representation of the current date and time, according to the time of the local system, including any time zone designation.'
      },
      timestamp_cmp: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'TIMESTAMP' }]],
        signature: 'timestamp_cmp(TIMESTAMP t1, TIMESTAMP t2)',
        draggable: 'timestamp_cmp()',
        description:
          'Tests if one TIMESTAMP value is newer than, older than, or identical to another TIMESTAMP. Returns either -1, 0, 1 or NULL.'
      },
      to_date: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'to_date(TIMESTAMP date)',
        draggable: 'to_date()',
        description: 'Returns a string representation of the date field from a timestamp value.'
      },
      to_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        altArguments: [[{ type: 'BIGINT' }]],
        signature: 'to_timestamp([STRING val, STRING format]|[BIGINT val])',
        draggable: 'to_timestamp()',
        description:
          "Converts a bigint (delta from the Unix epoch) or a string with the specified format to a timestamp. Example: to_timestamp('1970-01-01 00:00:00', 'yyyy-MM-dd HH:mm:ss')."
      },
      to_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
        signature: 'to_utc_timestamp(TIMESTAMP date, STRING timezone)',
        draggable: 'to_utc_timestamp()',
        description:
          'Converts a specified timestamp value in a specified time zone into the corresponding value for the UTC time zone.'
      },
      trunc: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
        signature: 'trunc(TIMESTAMP date, STRING unit)',
        draggable: 'trunc()',
        description:
          'Strips off fields and optionally rounds a TIMESTAMP value. The unit argument value is case-sensitive. This argument string can be one of: SYYYY, YYYY, YEAR, SYEAR, YYY, YY, Y: Year. Q: Quarter. MONTH, MON, MM, RM: Month. WW, W: Same day of the week as the first day of the month. DDD, DD, J: Day. DAY, DY, D: Starting day of the week. (Not necessarily the current day.) HH, HH12, HH24: Hour. A TIMESTAMP value truncated to the hour is always represented in 24-hour notation, even for the HH12 argument string. MI: Minute.'
      },
      unix_timestamp: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING', optional: true }], [{ type: 'STRING', optional: true }]],
        altArguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'unix_timestamp([STRING datetime [, STRING format]]|[TIMESTAMP datetime])',
        draggable: 'unix_timestamp()',
        description:
          'Returns an integer value representing the current date and time as a delta from the Unix epoch, or converts from a specified date and time value represented as a TIMESTAMP or STRING.'
      },
      utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'utc_timestamp()',
        draggable: 'utc_timestamp()',
        description:
          'Returns a TIMESTAMP corresponding to the current date and time in the UTC time zone.'
      },
      weekofyear: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'weekofyear(TIMESTAMP date)',
        draggable: 'weekofyear()',
        description: 'Returns the corresponding week (1-53) from the date portion of a TIMESTAMP.'
      },
      weeks_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'weeks_add(TIMESTAMP date, BIGINT|INT weeks)',
        draggable: 'weeks_add()',
        description: 'Returns the specified date and time plus some number of weeks.'
      },
      weeks_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'weeks_sub(TIMESTAMP date, BIGINT|INT weeks)',
        draggable: 'weeks_sub()',
        description: 'Returns the specified date and time minus some number of weeks.'
      },
      year: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'TIMESTAMP' }]],
        signature: 'year(TIMESTAMP date)',
        draggable: 'year()',
        description: 'Returns the year field from the date portion of a TIMESTAMP.'
      },
      years_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'years_add(TIMESTAMP date, BIGINT|INT years)',
        draggable: 'years_add()',
        description: 'Returns the specified date and time plus some number of years.'
      },
      years_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
        signature: 'years_sub(TIMESTAMP date, BIGINT|INT years)',
        draggable: 'years_sub()',
        description: 'Returns the specified date and time minus some number of years.'
      }
    }
  };

  const CONDITIONAL_FUNCTIONS = {
    hive: {
      assert_true: {
        returnTypes: ['T'],
        arguments: [[{ type: 'BOOLEAN' }]],
        signature: 'assert_true(BOOLEAN condition)',
        draggable: 'assert_true()',
        description:
          "Throw an exception if 'condition' is not true, otherwise return null (as of Hive 0.8.0). For example, select assert_true (2<1)."
      },
      coalesce: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'coalesce(T v1, T v2, ...)',
        draggable: 'coalesce()',
        description: "Returns the first v that is not NULL, or NULL if all v's are NULL."
      },
      if: {
        returnTypes: ['T'],
        arguments: [[{ type: 'BOOLEAN' }], [{ type: 'T' }], [{ type: 'T' }]],
        signature: 'if(BOOLEAN testCondition, T valueTrue, T valueFalseOrNull)',
        draggable: 'if()',
        description:
          'Returns valueTrue when testCondition is true, returns valueFalseOrNull otherwise.'
      },
      isnotnull: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'T' }]],
        signature: 'isnotnull(a)',
        draggable: 'isnotnull()',
        description: 'Returns true if a is not NULL and false otherwise.'
      },
      isnull: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'T' }]],
        signature: 'isnull(a)',
        draggable: 'isnull()',
        description: 'Returns true if a is NULL and false otherwise.'
      },
      nullif: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'nullif(a, b)',
        draggable: 'nullif()',
        description: 'Returns NULL if a=b; otherwise returns a (as of Hive 2.2.0).'
      },
      nvl: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'nvl(T value, T default_value)',
        draggable: 'nvl()',
        description: 'Returns default value if value is null else returns value (as of Hive 0.11).'
      }
    },
    impala: {
      coalesce: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'coalesce(T v1, T v2, ...)',
        draggable: 'coalesce()',
        description:
          'Returns the first specified argument that is not NULL, or NULL if all arguments are NULL.'
      },
      decode: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', multiple: true }]],
        signature:
          'decode(T expression, T search1, T result1 [, T search2, T result2 ...] [, T default] )',
        draggable: 'decode()',
        description:
          'Compares an expression to one or more possible values, and returns a corresponding result when a match is found.'
      },
      if: {
        returnTypes: ['T'],
        arguments: [[{ type: 'BOOLEAN' }], [{ type: 'T' }], [{ type: 'T' }]],
        signature: 'if(BOOLEAN condition, T ifTrue, T ifFalseOrNull)',
        draggable: 'if()',
        description:
          'Tests an expression and returns a corresponding result depending on whether the result is true, false, or NULL.'
      },
      ifnull: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'ifnull(T a, T ifNotNull)',
        draggable: 'ifnull()',
        description:
          'Alias for the isnull() function, with the same behavior. To simplify porting SQL with vendor extensions to Impala.'
      },
      isfalse: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'BOOLEAN' }]],
        signature: 'isfalse(BOOLEAN condition)',
        draggable: 'isfalse()',
        description:
          'Tests if a Boolean expression is false or not. Returns true if so. If the argument is NULL, returns false. Identical to isnottrue(), except it returns the opposite value for a NULL argument.'
      },
      isnotfalse: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'BOOLEAN' }]],
        signature: 'isnotfalse(BOOLEAN condition)',
        draggable: 'isnotfalse()',
        description:
          'Tests if a Boolean expression is not false (that is, either true or NULL). Returns true if so. If the argument is NULL, returns true. Identical to istrue(), except it returns the opposite value for a NULL argument.'
      },
      isnottrue: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'BOOLEAN' }]],
        signature: 'isnottrue(BOOLEAN condition)',
        draggable: 'isnottrue()',
        description:
          'Tests if a Boolean expression is not true (that is, either false or NULL). Returns true if so. If the argument is NULL, returns true. Identical to isfalse(), except it returns the opposite value for a NULL argument.'
      },
      isnull: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'isnull(T a, T ifNotNull)',
        draggable: 'isnull()',
        description:
          'Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument.'
      },
      istrue: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'BOOLEAN' }]],
        signature: 'istrue(BOOLEAN condition)',
        draggable: 'istrue()',
        description:
          'Tests if a Boolean expression is true or not. Returns true if so. If the argument is NULL, returns false. Identical to isnotfalse(), except it returns the opposite value for a NULL argument.'
      },
      nonnullvalue: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'T' }]],
        signature: 'nonnullvalue(T expression)',
        draggable: 'nonnullvalue()',
        description:
          'Tests if an expression (of any type) is NULL or not. Returns false if so. The converse of nullvalue().'
      },
      nullif: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'nullif(T expr1, T expr2)',
        draggable: 'nullif()',
        description:
          'Returns NULL if the two specified arguments are equal. If the specified arguments are not equal, returns the value of expr1. The data types of the expressions must be compatible. You cannot use an expression that evaluates to NULL for expr1; that way, you can distinguish a return value of NULL from an argument value of NULL, which would never match expr2.'
      },
      nullifzero: {
        returnTypes: ['T'],
        arguments: [[{ type: 'NUMBER' }]],
        signature: 'nullifzero(T numeric_expr)',
        draggable: 'nullifzero()',
        description:
          'Returns NULL if the numeric expression evaluates to 0, otherwise returns the result of the expression.'
      },
      nullvalue: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'T' }]],
        signature: 'nullvalue(T expression)',
        draggable: 'nullvalue()',
        description:
          'Tests if an expression (of any type) is NULL or not. Returns true if so. The converse of nonnullvalue().'
      },
      nvl: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'nvl(T a, T ifNotNull)',
        draggable: 'nvl()',
        description:
          'Alias for the isnull() function. Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument. Equivalent to the nvl() function from Oracle Database or ifnull() from MySQL.'
      },
      nvl2: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
        signature: 'nvl2(T a, T ifNull, T ifNotNull)',
        draggable: 'nvl2()',
        description:
          'Enhanced variant of the nvl() function. Tests an expression and returns different result values depending on whether it is NULL or not. If the first argument is NULL, returns the second argument. If the first argument is not NULL, returns the third argument. Equivalent to the nvl2() function from Oracle.'
      },
      zeroifnull: {
        returnTypes: ['T'],
        arguments: [[{ type: 'NUMBER' }]],
        signature: 'zeroifnull(T numeric_expr)',
        draggable: 'zeroifnull()',
        description:
          'Returns 0 if the numeric expression evaluates to NULL, otherwise returns the result of the expression.'
      }
    }
  };

  const STRING_FUNCTIONS = {
    hive: {
      ascii: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'ascii(STRING str)',
        draggable: 'ascii()',
        description: 'Returns the numeric value of the first character of str.'
      },
      base64: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'BINARY' }]],
        signature: 'base64(BINARY bin)',
        draggable: 'base64()',
        description: 'Converts the argument from binary to a base 64 string (as of Hive 0.12.0).'
      },
      chr: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'BIGINT' }, { type: 'DOUBLE' }]],
        signature: 'chr(BIGINT|DOUBLE a)',
        draggable: 'chr()',
        description:
          'Returns the ASCII character having the binary equivalent to a (as of Hive 1.3.0 and 2.1.0). If a is larger than 256 the result is equivalent to chr(a % 256). Example: select chr(88); returns "X".'
      },
      char_length: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'char_length(STRING a)',
        draggable: 'char_length()',
        description:
          'Returns the number of UTF-8 characters contained in str (as of Hive 2.2.0). This is shorthand for character_length.'
      },
      character_length: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'character_length(STRING a)',
        draggable: 'character_length()',
        description:
          'Returns the number of UTF-8 characters contained in str (as of Hive 2.2.0). The function char_length is shorthand for this function.'
      },
      concat: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING', multiple: true }, { type: 'BINARY', multiple: true }]],
        signature: 'concat(STRING|BINARY a, STRING|BINARY b...)',
        draggable: 'concat()',
        description:
          "Returns the string or bytes resulting from concatenating the strings or bytes passed in as parameters in order. For example, concat('foo', 'bar') results in 'foobar'. Note that this function can take any number of input strings."
      },
      concat_ws: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING' }],
          [{ type: 'STRING', multiple: true }]
        ],
        altArguments: [[{ type: 'STRING' }], [{ type: 'ARRAY' }]],
        signature:
          'concat_ws(STRING sep, STRING a, STRING b...), concat_ws(STRING sep, Array<STRING>)',
        draggable: 'concat_ws()',
        description: 'Like concat(), but with custom separator SEP.'
      },
      context_ngrams: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'ARRAY' }], [{ type: 'ARRAY' }], [{ type: 'INT' }], [{ type: 'INT' }]],
        signature:
          'array<struct<STRING,DOUBLE>> context_ngrams(Array<Array<STRING>>, Array<STRING>, INT k, INT pf)',
        draggable: 'array<struct<STRING,DOUBLE>> context_ngrams()',
        description:
          'Returns the top-k contextual N-grams from a set of tokenized sentences, given a string of "context".'
      },
      decode: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'BINARY' }], [{ type: 'STRING' }]],
        signature: 'decode(BINARY bin, STRING charset)',
        draggable: 'decode()',
        description:
          "Decodes the first argument into a String using the provided character set (one of 'US-ASCII', 'ISO-8859-1', 'UTF-8', 'UTF-16BE', 'UTF-16LE', 'UTF-16'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)"
      },
      elt: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'INT' }], [{ type: 'STRING', multiple: true }]],
        signature: 'elt(INT n, STRING str, STRING str1, ...])',
        draggable: 'elt()',
        description:
          "Return string at index number. For example elt(2,'hello','world') returns 'world'. Returns NULL if N is less than 1 or greater than the number of arguments."
      },
      encode: {
        returnTypes: ['BINARY'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'encode(STRING src, STRING charset)',
        draggable: 'encode()',
        description:
          "Encodes the first argument into a BINARY using the provided character set (one of 'US-ASCII', 'ISO-8859-1', 'UTF-8', 'UTF-16BE', 'UTF-16LE', 'UTF-16'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)"
      },
      field: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'field(T val, T val1, ...])',
        draggable: 'field()',
        description:
          "Returns the index of val in the val1,val2,val3,... list or 0 if not found. For example field('world','say','hello','world') returns 3. All primitive types are supported, arguments are compared using str.equals(x). If val is NULL, the return value is 0."
      },
      find_in_set: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'find_in_set(STRING str, STRING strList)',
        draggable: 'find_in_set()',
        description:
          "Returns the first occurance of str in strList where strList is a comma-delimited string. Returns null if either argument is null. Returns 0 if the first argument contains any commas. For example, find_in_set('ab', 'abc,b,ab,c,def') returns 3."
      },
      format_number: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'NUMBER' }], [{ type: 'INT' }]],
        signature: 'format_number(NUMBER x, INT d)',
        draggable: 'format_number()',
        description:
          "Formats the number X to a format like '#,###,###.##', rounded to D decimal places, and returns the result as a string. If D is 0, the result has no decimal point or fractional part. (As of Hive 0.10.0; bug with float types fixed in Hive 0.14.0, decimal type support added in Hive 0.14.0)"
      },
      get_json_object: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'get_json_object(STRING json_string, STRING path)',
        draggable: 'get_json_object()',
        description:
          'Extracts json object from a json string based on json path specified, and returns json string of the extracted json object. It will return null if the input json string is invalid. NOTE: The json path can only have the characters [0-9a-z_], i.e., no upper-case or special characters. Also, the keys *cannot start with numbers.* This is due to restrictions on Hive column names.'
      },
      initcap: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'initcap(STRING a)',
        draggable: 'initcap()',
        description:
          'Returns string, with the first letter of each word in uppercase, all other letters in lowercase. Words are delimited by whitespace. (As of Hive 1.1.0.)'
      },
      instr: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'instr(STRING str, STRING substr)',
        draggable: 'instr()',
        description:
          'Returns the position of the first occurrence of substr in str. Returns null if either of the arguments are null and returns 0 if substr could not be found in str. Be aware that this is not zero based. The first character in str has index 1.'
      },
      in_file: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'in_file(STRING str, STRING filename)',
        draggable: 'in_file()',
        description: 'Returns true if the string str appears as an entire line in filename.'
      },
      length: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'length(STRING a)',
        draggable: 'length()',
        description: 'Returns the length of the string.'
      },
      levenshtein: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'levenshtein(STRING a, STRING b)',
        draggable: 'levenshtein()',
        description:
          "Returns the Levenshtein distance between two strings (as of Hive 1.2.0). For example, levenshtein('kitten', 'sitting') results in 3."
      },
      lcase: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'lcase(STRING a)',
        draggable: 'lcase()',
        description:
          "Returns the string resulting from converting all characters of B to lower case. For example, lcase('fOoBaR') results in 'foobar'."
      },
      locate: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
        signature: 'locate(STRING substr, STRING str [, INT pos])',
        draggable: 'locate()',
        description:
          'Returns the position of the first occurrence of substr in str after position pos.'
      },
      lower: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'lower(STRING a)',
        draggable: 'lower()',
        description:
          "Returns the string resulting from converting all characters of B to lower case. For example, lower('fOoBaR') results in 'foobar'."
      },
      lpad: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'STRING' }]],
        signature: 'lpad(STRING str, INT len, STRING pad)',
        draggable: 'lpad()',
        description: 'Returns str, left-padded with pad to a length of len.'
      },
      ltrim: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'ltrim(STRING a)',
        draggable: 'ltrim()',
        description:
          "Returns the string resulting from trimming spaces from the beginning(left hand side) of A. For example, ltrim(' foobar ') results in 'foobar '."
      },
      ngrams: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'ARRAY' }], [{ type: 'INT' }], [{ type: 'INT' }], [{ type: 'INT' }]],
        signature:
          'array<struct<STRING, DOUBLE>> ngrams(Array<Array<STRING>> a, INT n, INT k, INT pf)',
        draggable: 'array<struct<STRING, DOUBLE>> ngrams()',
        description:
          'Returns the top-k N-grams from a set of tokenized sentences, such as those returned by the sentences() UDAF.'
      },
      octet_length: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'octet_length(STRING a)',
        draggable: 'octet_length()',
        description:
          'Returns the number of octets required to hold the string str in UTF-8 encoding (since Hive 2.2.0). Note that octet_length(str) can be larger than character_length(str).'
      },
      parse_url: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING' }],
          [{ type: 'STRING', optional: true }]
        ],
        signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])',
        draggable: 'parse_url()',
        description:
          "Returns the specified part from the URL. Valid values for partToExtract include HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, and USERINFO. For example, parse_url('http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1', 'HOST') returns 'facebook.com'. Also a value of a particular key in QUERY can be extracted by providing the key as the third argument, for example, parse_url('http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1', 'QUERY', 'k1') returns 'v1'."
      },
      printf: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'T', multiple: true }]],
        signature: 'printf(STRING format, Obj... args)',
        draggable: 'printf()',
        description:
          'Returns the input formatted according do printf-style format strings (as of Hive 0.9.0).'
      },
      regexp_extract: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'regexp_extract(STRING subject, STRING pattern, INT index)',
        draggable: 'regexp_extract()',
        description:
          "Returns the string extracted using the pattern. For example, regexp_extract('foothebar', 'foo(.*?)(bar)', 2) returns 'bar.' Note that some care is necessary in using predefined character classes: using '\\s' as the second argument will match the letter s; '\\\\s' is necessary to match whitespace, etc. The 'index' parameter is the Java regex Matcher group() method index."
      },
      regexp_replace: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'regexp_replace(STRING initial_string, STRING pattern, STRING replacement)',
        draggable: 'regexp_replace()',
        description:
          'Returns the string resulting from replacing all substrings in INITIAL_STRING that match the java regular expression syntax defined in PATTERN with instances of REPLACEMENT. For example, regexp_replace("foobar", "oo|ar", "") returns \'fb.\' Note that some care is necessary in using predefined character classes: using \'\\s\' as the second argument will match the letter s; \'\\\\s\' is necessary to match whitespace, etc.'
      },
      repeat: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'repeat(STRING str, INT n)',
        draggable: 'repeat()',
        description: 'Repeats str n times.'
      },
      replace: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'replace(STRING a, STRING old, STRING new)',
        draggable: 'replace()',
        description:
          'Returns the string a with all non-overlapping occurrences of old replaced with new (as of Hive 1.3.0 and 2.1.0). Example: select replace("ababab", "abab", "Z"); returns "Zab".'
      },
      reverse: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'reverse(STRING a)',
        draggable: 'reverse()',
        description: 'Returns the reversed string.'
      },
      rpad: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'STRING' }]],
        signature: 'rpad(STRING str, INT len, STRING pad)',
        draggable: 'rpad()',
        description: 'Returns str, right-padded with pad to a length of len.'
      },
      rtrim: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'rtrim(STRING a)',
        draggable: 'rtrim()',
        description:
          "Returns the string resulting from trimming spaces from the end(right hand side) of A. For example, rtrim(' foobar ') results in ' foobar'."
      },
      sentences: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'array<array<STRING>> sentences(STRING str, STRING lang, STRING locale)',
        draggable: 'array<array<STRING>> sentences()',
        description:
          'Tokenizes a string of natural language text into words and sentences, where each sentence is broken at the appropriate sentence boundary and returned as an array of words. The \'lang\' and \'locale\' are optional arguments. For example, sentences(\'Hello there! How are you?\') returns ( ("Hello", "there"), ("How", "are", "you") ).'
      },
      soundex: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'soundex(STRING a)',
        draggable: 'soundex()',
        description:
          "Returns soundex code of the string (as of Hive 1.2.0). For example, soundex('Miller') results in M460."
      },
      space: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'INT' }]],
        signature: 'space(INT n)',
        draggable: 'space()',
        description: 'Returns a string of n spaces.'
      },
      split: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'array<STRING> split(STRING str, STRING pat)',
        draggable: 'array<STRING> split()',
        description: 'Splits str around pat (pat is a regular expression).'
      },
      str_to_map: {
        returnTypes: ['MAP'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING', optional: true }],
          [{ type: 'STRING', optional: true }]
        ],
        signature: 'map<STRING,STRING> str_to_map(STRING [, STRING delimiter1, STRING delimiter2])',
        draggable: 'map<STRING,STRING> str_to_map()',
        description:
          "Splits text into key-value pairs using two delimiters. Delimiter1 separates text into K-V pairs, and Delimiter2 splits each K-V pair. Default delimiters are ',' for delimiter1 and '=' for delimiter2."
      },
      substr: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'STRING' }, { type: 'BINARY' }],
          [{ type: 'INT' }],
          [{ type: 'INT', optional: true }]
        ],
        signature: 'substr(STRING|BINARY A, INT start [, INT len]) ',
        draggable: 'substr()',
        description:
          "Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr('foobar', 4) results in 'bar'"
      },
      substring: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'STRING' }, { type: 'BINARY' }],
          [{ type: 'INT' }],
          [{ type: 'INT', optional: true }]
        ],
        signature: 'substring(STRING|BINARY a, INT start [, INT len])',
        draggable: 'substring()',
        description:
          "Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr('foobar', 4) results in 'bar'"
      },
      substring_index: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'substring_index(STRING a, STRING delim, INT count)',
        draggable: 'substring_index()',
        description:
          "Returns the substring from string A before count occurrences of the delimiter delim (as of Hive 1.3.0). If count is positive, everything to the left of the final delimiter (counting from the left) is returned. If count is negative, everything to the right of the final delimiter (counting from the right) is returned. Substring_index performs a case-sensitive match when searching for delim. Example: substring_index('www.apache.org', '.', 2) = 'www.apache'."
      },
      translate: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'STRING' }, { type: 'CHAR' }, { type: 'VARCHAR' }],
          [{ type: 'STRING' }, { type: 'CHAR' }, { type: 'VARCHAR' }],
          [{ type: 'STRING' }, { type: 'CHAR' }, { type: 'VARCHAR' }]
        ],
        signature:
          'translate(STRING|CHAR|VARCHAR input, STRING|CHAR|VARCHAR from, STRING|CHAR|VARCHAR to)',
        draggable: 'translate()',
        description:
          'Translates the input string by replacing the characters present in the from string with the corresponding characters in the to string. This is similar to the translate function in PostgreSQL. If any of the parameters to this UDF are NULL, the result is NULL as well. (Available as of Hive 0.10.0, for string types) Char/varchar support added as of Hive 0.14.0.'
      },
      trim: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'trim(STRING a)',
        draggable: 'trim()',
        description:
          "Returns the string resulting from trimming spaces from both ends of A. For example, trim(' foobar ') results in 'foobar'"
      },
      ucase: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'ucase(STRING a)',
        draggable: 'ucase()',
        description:
          "Returns the string resulting from converting all characters of A to upper case. For example, ucase('fOoBaR') results in 'FOOBAR'."
      },
      unbase64: {
        returnTypes: ['BINARY'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'unbase64(STRING a)',
        draggable: 'unbase64()',
        description: 'Converts the argument from a base 64 string to BINARY. (As of Hive 0.12.0.)'
      },
      upper: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'upper(STRING a)',
        draggable: 'upper()',
        description:
          "Returns the string resulting from converting all characters of A to upper case. For example, upper('fOoBaR') results in 'FOOBAR'."
      }
    },
    impala: {
      ascii: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'ascii(STRING str)',
        draggable: 'ascii()',
        description: 'Returns the numeric ASCII code of the first character of the argument.'
      },
      base64decode: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'base64decode(STRING str)',
        draggable: 'base64decode()',
        description:
          "Decodes the given string from Base64, an ACSII string format. It's typically used in combination with base64encode(), to store data in an Impala table string that is problematic to store or transmit"
      },
      base64encode: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'base64encode(STRING str)',
        draggable: 'base64encode()',
        description:
          "Encodes the given string to Base64, an ACSII string format. It's typically used in combination with base64decode(), to store data in an Impala table string that is problematic to store or transmit"
      },
      btrim: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
        signature: 'btrim(STRING str [, STRING chars_to_trim])',
        draggable: 'btrim()',
        description:
          'Removes all instances of one or more characters from the start and end of a STRING value. By default, removes only spaces. If a non-NULL optional second argument is specified, the function removes all occurrences of characters in that second argument from the beginning and end of the string.'
      },
      char_length: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'char_length(STRING a)',
        draggable: 'char_length()',
        description:
          'Returns the length in characters of the argument string. Aliases for the length() function.'
      },
      character_length: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'character_length(STRING a)',
        draggable: 'character_length()',
        description:
          'Returns the length in characters of the argument string. Aliases for the length() function.'
      },
      chr: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'INT' }]],
        signature: 'chr(INT character_code)',
        draggable: 'chr()',
        description:
          'Returns a character specified by a decimal code point value. The interpretation and display of the resulting character depends on your system locale. Because consistent processing of Impala string values is only guaranteed for values within the ASCII range, only use this function for values corresponding to ASCII characters. In particular, parameter values greater than 255 return an empty string.'
      },
      concat: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
        signature: 'concat(STRING a, STRING b...)',
        draggable: 'concat()',
        description: 'Returns a single string representing all the argument values joined together.'
      },
      concat_ws: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING' }],
          [{ type: 'STRING', multiple: true }]
        ],
        signature: 'concat_ws(STRING sep, STRING a, STRING b...)',
        draggable: 'concat_ws()',
        description:
          'Returns a single string representing the second and following argument values joined together, delimited by a specified separator.'
      },
      find_in_set: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'find_in_set(STRING str, STRING strList)',
        draggable: 'find_in_set()',
        description:
          'Returns the position (starting from 1) of the first occurrence of a specified string within a comma-separated string. Returns NULL if either argument is NULL, 0 if the search string is not found, or 0 if the search string contains a comma.'
      },
      group_concat: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
        signature: 'group_concat(STRING s [, STRING sep])',
        draggable: 'group_concat()',
        description:
          'Returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values.'
      },
      initcap: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'initcap(STRING str)',
        draggable: 'initcap()',
        description: 'Returns the input string with the first letter capitalized.'
      },
      instr: {
        returnTypes: ['INT'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING' }],
          [{ type: 'BIGINT', optional: true }],
          [{ type: 'BIGINT', optional: true }]
        ],
        signature: 'instr(STRING str, STRING substr [, BIGINT position [, BIGINT occurrence]])',
        draggable: 'instr()',
        description:
          'Returns the position (starting from 1) of the first occurrence of a substring within a longer string. The optional third and fourth arguments let you find instances of the substring other than the first instance starting from the left.'
      },
      left: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'left(STRING a, INT num_chars)',
        draggable: 'left()',
        description: 'Returns the leftmost characters of the string. Same as strleft().'
      },
      length: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'length(STRING a)',
        draggable: 'length()',
        description: 'Returns the length in characters of the argument string.'
      },
      levenshtein: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'levenshtein(STRING a, STRING b)',
        draggable: 'levenshtein()',
        description:
          "Returns the Levenshtein distance between two strings. For example, levenshtein('kitten', 'sitting') results in 3."
      },
      locate: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
        signature: 'locate(STRING substr, STRING str[, INT pos])',
        draggable: 'locate()',
        description:
          'Returns the position (starting from 1) of the first occurrence of a substring within a longer string, optionally after a particular position.'
      },
      lower: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'lower(STRING a)',
        draggable: 'lower()',
        description: 'Returns the argument string converted to all-lowercase.'
      },
      lcase: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'lcase(STRING a)',
        draggable: 'lcase()',
        description: 'Returns the argument string converted to all-lowercase.'
      },
      lpad: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'STRING' }]],
        signature: 'lpad(STRING str, INT len, STRING pad)',
        draggable: 'lpad()',
        description:
          'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the left with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.'
      },
      ltrim: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
        signature: 'ltrim(STRING a [, STRING charsToTrim])',
        draggable: 'ltrim()',
        description:
          'Returns the argument string with all occurrences of characters specified by the second argument removed from the left side. Removes spaces if the second argument is not specified.'
      },
      parse_url: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING' }],
          [{ type: 'STRING', optional: true }]
        ],
        signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])',
        draggable: 'parse_url()',
        description:
          "Returns the portion of a URL corresponding to a specified part. The part argument can be 'PROTOCOL', 'HOST', 'PATH', 'REF', 'AUTHORITY', 'FILE', 'USERINFO', or 'QUERY'. Uppercase is required for these literal values. When requesting the QUERY portion of the URL, you can optionally specify a key to retrieve just the associated value from the key-value pairs in the query string."
      },
      regexp_escape: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'regexp_escape(STRING source)',
        draggable: 'regexp_escape()',
        description:
          'The regexp_escape function returns a string escaped for the special character in RE2 library so that the special characters are interpreted literally rather than as special characters. The following special characters are escaped by the function: .\\+*?[^]$(){}=!<>|:-'
      },
      regexp_extract: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'regexp_extract(STRING subject, STRING pattern, INT index)',
        draggable: 'regexp_extract()',
        description:
          'Returns the specified () group from a string based on a regular expression pattern. Group 0 refers to the entire extracted string, while group 1, 2, and so on refers to the first, second, and so on (...) portion.'
      },
      regexp_like: {
        returnTypes: ['BOOLEAN'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING' }],
          [{ type: 'STRING', optional: true }]
        ],
        signature: 'regexp_like(STRING source, STRING pattern [, STRING options])',
        draggable: 'regexp_like()',
        description:
          'Returns true or false to indicate whether the source string contains anywhere inside it the regular expression given by the pattern. The optional third argument consists of letter flags that change how the match is performed, such as i for case-insensitive matching.'
      },
      regexp_replace: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'regexp_replace(STRING initial, STRING pattern, STRING replacement)',
        draggable: 'regexp_replace()',
        description:
          'Returns the initial argument with the regular expression pattern replaced by the final argument string.'
      },
      repeat: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'repeat(STRING str, INT n)',
        draggable: 'repeat()',
        description: 'Returns the argument string repeated a specified number of times.'
      },
      replace: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'replace(STRING initial, STRING target, STRING replacement)',
        draggable: 'replace()',
        description:
          'Returns the initial argument with all occurrences of the target string replaced by the replacement string.'
      },
      reverse: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'reverse(STRING a)',
        draggable: 'reverse()',
        description: 'Returns the argument string with characters in reversed order.'
      },
      right: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'right(STRING a, INT num_chars)',
        draggable: 'right()',
        description: 'Returns the rightmost characters of the string. Same as strright().'
      },
      rpad: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'STRING' }]],
        signature: 'rpad(STRING str, INT len, STRING pad)',
        draggable: 'rpad()',
        description:
          'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the right with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.'
      },
      rtrim: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
        signature: 'rtrim(STRING a [, STRING charsToTrim])',
        draggable: 'rtrim()',
        description:
          'Returns the argument string with all occurrences of characters specified by the second argument removed from the right side. Removes spaces if the second argument is not specified.'
      },
      space: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'INT' }]],
        signature: 'space(INT n)',
        draggable: 'space()',
        description:
          "Returns a concatenated string of the specified number of spaces. Shorthand for repeat(' ', n)."
      },
      split_part: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'BIGINT' }]],
        signature: 'split_part(STRING source, STRING delimiter, BIGINT n)',
        draggable: 'split_part()',
        description:
          'Returns the nth field within a delimited string. The fields are numbered starting from 1. The delimiter can consist of multiple characters, not just a single character. All matching of the delimiter is done exactly, not using any regular expression patterns.'
      },
      strleft: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'strleft(STRING a, INT num_chars)',
        draggable: 'strleft()',
        description:
          'Returns the leftmost characters of the string. Shorthand for a call to substr() with 2 arguments.'
      },
      strright: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
        signature: 'strright(STRING a, INT num_chars)',
        draggable: 'strright()',
        description:
          'Returns the rightmost characters of the string. Shorthand for a call to substr() with 2 arguments.'
      },
      substr: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'INT', optional: true }]],
        signature: 'substr(STRING a, INT start [, INT len])',
        draggable: 'substr()',
        description:
          'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.'
      },
      substring: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'INT', optional: true }]],
        signature: 'substring(STRING a, INT start [, INT len])',
        draggable: 'substring()',
        description:
          'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.'
      },
      translate: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'translate(STRING input, STRING from, STRING to)',
        draggable: 'translate()',
        description:
          'Returns the input string with a set of characters replaced by another set of characters.'
      },
      trim: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'trim(STRING a)',
        draggable: 'trim()',
        description:
          'Returns the input string with both leading and trailing spaces removed. The same as passing the string through both ltrim() and rtrim().'
      },
      upper: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'upper(STRING a)',
        draggable: 'upper()',
        description: 'Returns the argument string converted to all-uppercase.'
      },
      ucase: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }]],
        signature: 'ucase(STRING a)',
        draggable: 'ucase()',
        description: 'Returns the argument string converted to all-uppercase.'
      }
    }
  };

  const DATA_MASKING_FUNCTIONS = {
    hive: {
      mask: {
        returnTypes: ['STRING'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING', optional: true }],
          [{ type: 'STRING', optional: true }],
          [{ type: 'STRING', optional: true }]
        ],
        signature: 'mask(STRING str [, STRING upper [, STRING lower [, STRING number]]])',
        draggable: 'mask()',
        description:
          'Returns a masked version of str (as of Hive 2.1.0). By default, upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example mask("abcd-EFGH-8765-4321") results in xxxx-XXXX-nnnn-nnnn. You can override the characters used in the mask by supplying additional arguments: the second argument controls the mask character for upper case letters, the third argument for lower case letters and the fourth argument for numbers. For example, mask("abcd-EFGH-8765-4321", "U", "l", "#") results in llll-UUUU-####-####.'
      },
      mask_first_n: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
        signature: 'mask_first_n(STRING str [, INT n])',
        draggable: 'mask_first_n()',
        description:
          'Returns a masked version of str with the first n values masked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_first_n("1234-5678-8765-4321", 4) results in nnnn-5678-8765-4321.'
      },
      mask_last_n: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
        signature: 'mask_last_n(STRING str [, INT n])',
        draggable: 'mask_last_n()',
        description:
          'Returns a masked version of str with the last n values masked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_last_n("1234-5678-8765-4321", 4) results in 1234-5678-8765-nnnn.'
      },
      mask_show_first_n: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
        signature: 'mask_show_first_n(STRING str [, INT n])',
        draggable: 'mask_show_first_n()',
        description:
          'Returns a masked version of str, showing the first n characters unmasked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_show_first_n("1234-5678-8765-4321", 4) results in 1234-nnnn-nnnn-nnnn.'
      },
      mask_show_last_n: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
        signature: 'mask_show_last_n(STRING str [, INT n])',
        draggable: 'mask_show_last_n()',
        description:
          'Returns a masked version of str, showing the last n characters unmasked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_show_last_n("1234-5678-8765-4321", 4) results in nnnn-nnnn-nnnn-4321.'
      },
      mask_hash: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }, { type: 'CHAR' }, { type: 'VARCHAR' }]],
        signature: 'mask_hash(STRING|CHAR|VARCHAR str)',
        draggable: 'mask_hash()',
        description:
          'Returns a hashed value based on str (as of Hive 2.1.0). The hash is consistent and can be used to join masked values together across tables. This function returns null for non-string types.'
      }
    },
    impala: {}
  };

  const TABLE_GENERATING_FUNCTIONS = {
    hive: {
      explode: {
        returnTypes: ['table'],
        arguments: [[{ type: 'ARRAY' }, { type: 'MAP' }]],
        signature: 'explode(Array|Array<T>|Map a)',
        draggable: 'explode()',
        description: ''
      },
      inline: {
        returnTypes: ['table'],
        arguments: [[{ type: 'ARRAY' }]],
        signature: 'inline(Array<Struct [, Struct]> a)',
        draggable: 'inline()',
        description: 'Explodes an array of structs into a table. (As of Hive 0.10.)'
      },
      json_tuple: {
        returnTypes: ['table'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
        signature: 'json_tuple(STRING jsonStr, STRING k1, STRING k2, ...)',
        draggable: 'json_tuple()',
        description:
          'A new json_tuple() UDTF is introduced in Hive 0.7. It takes a set of names (keys) and a JSON string, and returns a tuple of values using one function. This is much more efficient than calling GET_JSON_OBJECT to retrieve more than one key from a single JSON string.'
      },
      parse_url_tuple: {
        returnTypes: ['table'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
        signature: 'parse_url_tuple(STRING url, STRING p1, STRING p2, ...)',
        draggable: 'parse_url_tuple()',
        description:
          'The parse_url_tuple() UDTF is similar to parse_url(), but can extract multiple parts of a given URL, returning the data in a tuple. Values for a particular key in QUERY can be extracted by appending a colon and the key to the partToExtract argument.'
      },
      posexplode: {
        returnTypes: ['table'],
        arguments: [[{ type: 'ARRAY' }]],
        signature: 'posexplode(ARRAY)',
        draggable: 'posexplode()',
        description:
          'posexplode() is similar to explode but instead of just returning the elements of the array it returns the element as well as its position  in the original array.'
      },
      stack: {
        returnTypes: ['table'],
        arguments: [[{ type: 'INT' }], [{ type: 'T', multiple: true }]],
        signature: 'stack(INT n, v1, v2, ..., vk)',
        draggable: 'stack()',
        description:
          'Breaks up v1, v2, ..., vk into n rows. Each row will have k/n columns. n must be constant.'
      }
    },
    impala: {}
  };

  const MISC_FUNCTIONS = {
    hive: {
      crc32: {
        returnTypes: ['BIGINT'],
        arguments: [[{ type: 'STRING' }, { type: 'BINARY' }]],
        signature: 'crc32(STRING|BINARY a)',
        draggable: 'crc32()',
        description:
          "Computes a cyclic redundancy check value for string or binary argument and returns bigint value (as of Hive 1.3.0). Example: crc32('ABC') = 2743272264."
      },
      current_database: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'current_database()',
        draggable: 'current_database()',
        description: 'Returns current database name (as of Hive 0.13.0).'
      },
      current_user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'current_user()',
        draggable: 'current_user()',
        description: 'Returns current user name (as of Hive 1.2.0).'
      },
      get_json_object: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'get_json_object(STRING json, STRING jsonPath)',
        draggable: 'get_json_object()',
        description:
          'A limited version of JSONPath is supported ($ : Root object, . : Child operator, [] : Subscript operator for array, * : Wildcard for []'
      },
      hash: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'T', multiple: true }]],
        signature: 'hash(a1[, a2...])',
        draggable: 'hash()',
        description: 'Returns a hash value of the arguments. (As of Hive 0.4.)'
      },
      java_method: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING' }],
          [{ type: 'T', multiple: true, optional: true }]
        ],
        signature: 'java_method(class, method[, arg1[, arg2..]])',
        draggable: 'java_method()',
        description:
          'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.9.0.)'
      },
      logged_in_user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'logged_in_user()',
        draggable: 'logged_in_user()',
        description:
          'Returns current user name from the session state (as of Hive 2.2.0). This is the username provided when connecting to Hive.'
      },
      md5: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }, { type: 'BINARY' }]],
        signature: 'md5(STRING|BINARY a)',
        draggable: 'md5()',
        description:
          "Calculates an MD5 128-bit checksum for the string or binary (as of Hive 1.3.0). The value is returned as a string of 32 hex digits, or NULL if the argument was NULL. Example: md5('ABC') = '902fbdd2b1df0c4f70b4a5d23525e932'."
      },
      reflect: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'STRING' }],
          [{ type: 'STRING' }],
          [{ type: 'T', multiple: true, optional: true }]
        ],
        signature: 'reflect(class, method[, arg1[, arg2..]])',
        draggable: 'reflect()',
        description:
          'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.7.0.)'
      },
      sha: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }, { type: 'BINARY' }]],
        signature: 'sha(STRING|BINARY a)',
        draggable: 'sha()',
        description:
          "Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1('ABC') = '3c01bdbb26f358bab27f267924aa2c9a03fcfdb8'."
      },
      sha1: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }, { type: 'BINARY' }]],
        signature: 'sha1(STRING|BINARY a)',
        draggable: 'sha1()',
        description:
          "Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1('ABC') = '3c01bdbb26f358bab27f267924aa2c9a03fcfdb8'."
      },
      sha2: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }, { type: 'BINARY' }], [{ type: 'INT' }]],
        signature: 'sha2(STRING|BINARY a, INT b)',
        draggable: 'sha2()',
        description:
          "Calculates the SHA-2 family of hash functions (SHA-224, SHA-256, SHA-384, and SHA-512) (as of Hive 1.3.0). The first argument is the string or binary to be hashed. The second argument indicates the desired bit length of the result, which must have a value of 224, 256, 384, 512, or 0 (which is equivalent to 256). SHA-224 is supported starting from Java 8. If either argument is NULL or the hash length is not one of the permitted values, the return value is NULL. Example: sha2('ABC', 256) = 'b5d4045c3f466fa91fe2cc6abe79232a1a57cdf104f7a26e716e0a1e2789df78'."
      },
      version: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'version()',
        draggable: 'version()',
        description:
          'Returns the Hive version (as of Hive 2.1.0). The string contains 2 fields, the first being a build number and the second being a build hash. Example: "select version();" might return "2.1.0.2.5.0.0-1245 r027527b9c5ce1a3d7d0b6d2e6de2378fb0c39232". Actual results will depend on your build.'
      },
      xpath: {
        returnTypes: ['ARRAY'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'array<STRING> xpath(STRING xml, STRING xpath)',
        draggable: 'array<STRING> xpath()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_boolean: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'xpath_boolean(STRING xml, STRING xpath)',
        draggable: 'xpath_boolean()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_double: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'xpath_double(STRING xml, STRING xpath)',
        draggable: 'xpath_double()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_float: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'xpath_float(STRING xml, STRING xpath)',
        draggable: 'xpath_float()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_int: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'xpath_int(STRING xml, STRING xpath)',
        draggable: 'xpath_int()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_long: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'xpath_long(STRING xml, STRING xpath)',
        draggable: 'xpath_long()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_number: {
        returnTypes: ['DOUBLE'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'xpath_number(STRING xml, STRING xpath)',
        draggable: 'xpath_number()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_short: {
        returnTypes: ['INT'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'xpath_short(STRING xml, STRING xpath)',
        draggable: 'xpath_short()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_string: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
        signature: 'xpath_string(STRING xml, STRING xpath)',
        draggable: 'xpath_string()',
        description:
          'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      }
    },
    impala: {
      coordinator: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'coordinator()',
        draggable: 'coordinator()',
        description:
          'Returns the name of the host which is running the impalad daemon that is acting as the coordinator for the current query.'
      },
      current_database: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'current_database()',
        draggable: 'current_database()',
        description:
          'Returns the database that the session is currently using, either default if no database has been selected, or whatever database the session switched to through a USE statement or the impalad - d option'
      },
      effective_user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'effective_user()',
        draggable: 'effective_user()',
        description:
          'Typically returns the same value as user(), except if delegation is enabled, in which case it returns the ID of the delegated user.'
      },
      logged_in_user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'logged_in_user()',
        draggable: 'logged_in_user()',
        description:
          'Purpose: Typically returns the same value as USER(). If delegation is enabled, it returns the ID of the delegated user. LOGGED_IN_USER() is an alias of EFFECTIVE_USER().'
      },
      pid: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'pid()',
        draggable: 'pid()',
        description:
          'Returns the process ID of the impalad daemon that the session is connected to.You can use it during low - level debugging, to issue Linux commands that trace, show the arguments, and so on the impalad process.'
      },
      sleep: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'INT' }]],
        signature: 'sleep(INT ms)',
        draggable: 'sleep()',
        description:
          'Pauses the query for a specified number of milliseconds. For slowing down queries with small result sets enough to monitor runtime execution, memory usage, or other factors that otherwise would be difficult to capture during the brief interval of query execution.'
      },
      user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'user()',
        draggable: 'user()',
        description:
          'Returns the username of the Linux user who is connected to the impalad daemon.Typically called a single time, in a query without any FROM clause, to understand how authorization settings apply in a security context; once you know the logged - in user name, you can check which groups that user belongs to, and from the list of groups you can check which roles are available to those groups through the authorization policy file.In Impala 2.0 and later, user() returns the the full Kerberos principal string, such as user@example.com, in a Kerberized environment.'
      },
      uuid: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'uuid()',
        draggable: 'uuid()',
        description:
          'Returns a universal unique identifier, a 128-bit value encoded as a string with groups of hexadecimal digits separated by dashes.'
      },
      version: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'version()',
        draggable: 'version()',
        description:
          'Returns information such as the precise version number and build date for the impalad daemon that you are currently connected to.Typically used to confirm that you are connected to the expected level of Impala to use a particular feature, or to connect to several nodes and confirm they are all running the same level of impalad.'
      }
    }
  };

  const ANALYTIC_FUNCTIONS = {
    hive: {
      cume_dist: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true, optional: true }]],
        signature: 'cume_dist()',
        draggable: 'cume_dist()',
        description: ''
      },
      dense_rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'dense_rank() OVER([partition_by_clause] order_by_clause)',
        draggable: 'dense_rank() OVER()',
        description:
          'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions.'
      },
      first_value: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'first_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        draggable: 'first_value() OVER()',
        description:
          'Returns the expression value from the first row in the window. The return value is NULL if the input expression is NULL.'
      },
      lag: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'T' }],
          [{ type: 'INT', optional: true }],
          [{ type: 'T', optional: true }]
        ],
        signature: 'lag(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        draggable: 'lag() OVER()',
        description:
          'This function returns the value of an expression using column values from a preceding row. You specify an integer offset, which designates a row position some number of rows previous to the current row. Any column references in the expression argument refer to column values from that prior row.'
      },
      last_value: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'last_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        draggable: 'last_value() OVER()',
        description:
          'Returns the expression value from the last row in the window. The return value is NULL if the input expression is NULL.'
      },
      lead: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'T' }],
          [{ type: 'INT', optional: true }],
          [{ type: 'T', optional: true }]
        ],
        signature: 'lead(expr [, offset] [, default]) OVER([partition_by_clause] order_by_clause)',
        draggable: 'lead() OVER()',
        description:
          'This function returns the value of an expression using column values from a following row. You specify an integer offset, which designates a row position some number of rows after to the current row. Any column references in the expression argument refer to column values from that later row.'
      },
      ntile: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true, optional: true }]],
        signature: 'ntile()',
        draggable: 'ntile()',
        description: ''
      },
      percent_rank: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T', multiple: true, optional: true }]],
        signature: 'percent_rank()',
        draggable: 'percent_rank()',
        description: ''
      },
      rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'rank() OVER([partition_by_clause] order_by_clause)',
        draggable: 'rank() OVER()',
        description:
          'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions. After generating duplicate output values for the "tied" input values, the function increments the sequence by the number of tied values.'
      },
      row_number: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'row_number() OVER([partition_by_clause] order_by_clause)',
        draggable: 'row_number() OVER()',
        description:
          'Returns an ascending sequence of integers, starting with 1. Starts the sequence over for each group produced by the PARTITIONED BY clause. The output sequence includes different values for duplicate input values. Therefore, the sequence never contains any duplicates or gaps, regardless of duplicate input values.'
      }
    },
    impala: {
      cume_dist: {
        returnTypes: ['T'],
        arguments: [{ type: 'T' }],
        signature: 'cume_dist(T expr) OVER([partition_by_clause] order_by_clause)',
        draggable: 'cume_dist() OVER()',
        description:
          'Returns the cumulative distribution of a value. The value for each row in the result set is greater than 0 and less than or equal to 1.'
      },
      dense_rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'dense_rank() OVER([partition_by_clause] order_by_clause)',
        draggable: 'dense_rank() OVER()',
        description:
          'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions.'
      },
      first_value: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'first_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        draggable: 'first_value() OVER()',
        description:
          'Returns the expression value from the first row in the window. The return value is NULL if the input expression is NULL.'
      },
      lag: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'T' }],
          [{ type: 'INT', optional: true }],
          [{ type: 'T', optional: true }]
        ],
        signature: 'lag(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        draggable: 'lag() OVER()',
        description:
          'This function returns the value of an expression using column values from a preceding row. You specify an integer offset, which designates a row position some number of rows previous to the current row. Any column references in the expression argument refer to column values from that prior row.'
      },
      last_value: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'last_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        draggable: 'last_value() OVER()',
        description:
          'Returns the expression value from the last row in the window. The return value is NULL if the input expression is NULL.'
      },
      lead: {
        returnTypes: ['T'],
        arguments: [
          [{ type: 'T' }],
          [{ type: 'INT', optional: true }],
          [{ type: 'T', optional: true }]
        ],
        signature: 'lead(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        draggable: 'lead() OVER()',
        description:
          'This function returns the value of an expression using column values from a following row. You specify an integer offset, which designates a row position some number of rows after to the current row. Any column references in the expression argument refer to column values from that later row.'
      },
      ntile: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true, optional: true }]],
        signature: 'ntile(T expr [, T offset ...])',
        draggable: 'ntile()',
        description:
          'Returns the "bucket number" associated with each row, between 1 and the value of an expression. For example, creating 100 buckets puts the lowest 1% of values in the first bucket, while creating 10 buckets puts the lowest 10% of values in the first bucket. Each partition can have a different number of buckets.'
      },
      percent_rank: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'percent_rank(T expr) OVER ([partition_by_clause] order_by_clause)',
        draggable: 'percent_rank() OVER()',
        description:
          'Calculates the rank, expressed as a percentage, of each row within a group of rows. If rank is the value for that same row from the RANK() function (from 1 to the total number of rows in the partition group), then the PERCENT_RANK() value is calculated as (rank - 1) / (rows_in_group - 1) . If there is only a single item in the partition group, its PERCENT_RANK() value is 0. The ORDER BY clause is required. The PARTITION BY clause is optional. The window clause is not allowed.'
      },
      rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'rank() OVER([partition_by_clause] order_by_clause)',
        draggable: 'rank() OVER()',
        description:
          'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions. After generating duplicate output values for the "tied" input values, the function increments the sequence by the number of tied values.'
      },
      row_number: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'row_number() OVER([partition_by_clause] order_by_clause)',
        draggable: 'row_number() OVER()',
        description:
          'Returns an ascending sequence of integers, starting with 1. Starts the sequence over for each group produced by the PARTITIONED BY clause. The output sequence includes different values for duplicate input values. Therefore, the sequence never contains any duplicates or gaps, regardless of duplicate input values.'
      }
    }
  };

  const BIT_FUNCTIONS = {
    hive: {},
    impala: {
      bitand: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'bitand(T<integer_type> a, T<integer_type> b)',
        draggable: 'bitand()',
        description:
          'Returns an integer value representing the bits that are set to 1 in both of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
      },
      bitnot: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'bitnot(T<integer_type> a)',
        draggable: 'bitnot()',
        description: 'Inverts all the bits of the input argument.'
      },
      bitor: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'bitor(T<integer_type> a, T<integer_type> b)',
        draggable: 'bitor()',
        description:
          'Returns an integer value representing the bits that are set to 1 in either of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
      },
      bitxor: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'bitxor(T<integer_type> a, T<integer_type> b)',
        draggable: 'bitxor()',
        description:
          'Returns an integer value representing the bits that are set to 1 in one but not both of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
      },
      countset: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT', optional: true }]],
        signature: 'countset(T<integer_type> a [, INT b])',
        draggable: 'countset()',
        description:
          'By default, returns the number of 1 bits in the specified integer value. If the optional second argument is set to zero, it returns the number of 0 bits instead.'
      },
      getbit: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'getbit(T<integer_type> a, INT b)',
        draggable: 'getbit()',
        description:
          'Returns a 0 or 1 representing the bit at a specified position. The positions are numbered right to left, starting at zero. The position argument (b) cannot be negative.'
      },
      rotateleft: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'rotateleft(T<integer_type> a, INT b)',
        draggable: 'rotateleft()',
        description:
          'Rotates an integer value left by a specified number of bits. As the most significant bit is taken out of the original value, if it is a 1 bit, it is "rotated" back to the least significant bit. Therefore, the final value has the same number of 1 bits as the original value, just in different positions. In computer science terms, this operation is a "circular shift".'
      },
      rotateright: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'rotateright(T<integer_type> a, INT b)',
        draggable: 'rotateright()',
        description:
          'Rotates an integer value right by a specified number of bits. As the least significant bit is taken out of the original value, if it is a 1 bit, it is "rotated" back to the most significant bit. Therefore, the final value has the same number of 1 bits as the original value, just in different positions. In computer science terms, this operation is a "circular shift".'
      },
      setbit: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }], [{ type: 'INT', optional: true }]],
        signature: 'setbit(T<integer_type> a, INT b [, INT c])',
        draggable: 'setbit()',
        description:
          'By default, changes a bit at a specified position (b) to a 1, if it is not already. If the optional third argument is set to zero, the specified bit is set to 0 instead.'
      },
      shiftleft: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'shiftleft(T<integer_type> a, INT b)',
        draggable: 'shiftleft()',
        description:
          'Shifts an integer value left by a specified number of bits. As the most significant bit is taken out of the original value, it is discarded and the least significant bit becomes 0. In computer science terms, this operation is a "logical shift".'
      },
      shiftright: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'shiftright(T<integer_type> a, INT b)',
        draggable: 'shiftright()',
        description:
          'Shifts an integer value right by a specified number of bits. As the least significant bit is taken out of the original value, it is discarded and the most significant bit becomes 0. In computer science terms, this operation is a "logical shift".'
      }
    }
  };

  const CATEGORIZED_FUNCTIONS = {
    hive: [
      { name: 'Aggregate', functions: AGGREGATE_FUNCTIONS['hive'] },
      { name: 'Analytic', functions: ANALYTIC_FUNCTIONS['hive'] },
      { name: 'Collection', functions: COLLECTION_FUNCTIONS['hive'] },
      { name: 'Complex Type', functions: COMPLEX_TYPE_CONSTRUCTS['hive'] },
      { name: 'Conditional', functions: CONDITIONAL_FUNCTIONS['hive'] },
      { name: 'Date', functions: DATE_FUNCTIONS['hive'] },
      { name: 'Mathematical', functions: MATHEMATICAL_FUNCTIONS['hive'] },
      { name: 'Misc', functions: MISC_FUNCTIONS['hive'] },
      { name: 'String', functions: STRING_FUNCTIONS['hive'] },
      { name: 'Data Masking', functions: DATA_MASKING_FUNCTIONS['hive'] },
      { name: 'Table Generating', functions: TABLE_GENERATING_FUNCTIONS['hive'] },
      { name: 'Type Conversion', functions: TYPE_CONVERSION_FUNCTIONS['hive'] }
    ],
    impala: [
      { name: 'Aggregate', functions: AGGREGATE_FUNCTIONS['impala'] },
      { name: 'Analytic', functions: ANALYTIC_FUNCTIONS['impala'] },
      { name: 'Bit', functions: BIT_FUNCTIONS['impala'] },
      { name: 'Conditional', functions: CONDITIONAL_FUNCTIONS['impala'] },
      { name: 'Date', functions: DATE_FUNCTIONS['impala'] },
      { name: 'Mathematical', functions: MATHEMATICAL_FUNCTIONS['impala'] },
      { name: 'Misc', functions: MISC_FUNCTIONS['impala'] },
      { name: 'String', functions: STRING_FUNCTIONS['impala'] },
      { name: 'Type Conversion', functions: TYPE_CONVERSION_FUNCTIONS['impala'] }
    ]
  };

  const typeImplicitConversion = {
    hive: {
      BOOLEAN: {
        BOOLEAN: true,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        FLOAT: false,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: false,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      TIMESTAMP: {
        BOOLEAN: false,
        TIMESTAMP: true,
        DATE: false,
        BINARY: false,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        FLOAT: false,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: false,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      DATE: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: true,
        BINARY: false,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        FLOAT: false,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: false,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      BINARY: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: true,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        FLOAT: false,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: false,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      TINYINT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: true,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        FLOAT: false,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: true,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      SMALLINT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: false,
        BIGINT: false,
        FLOAT: false,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: true,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      INT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: false,
        FLOAT: false,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: true,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      BIGINT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: false,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: true,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      FLOAT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: true,
        DOUBLE: false,
        DECIMAL: false,
        NUMBER: true,
        STRING: false,
        CHAR: false,
        VARCHAR: false,
        T: true
      },
      DOUBLE: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: true,
        DOUBLE: true,
        DECIMAL: false,
        NUMBER: true,
        STRING: true,
        CHAR: true,
        VARCHAR: true,
        T: true
      },
      DECIMAL: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: true,
        DOUBLE: true,
        DECIMAL: true,
        NUMBER: true,
        STRING: true,
        CHAR: true,
        VARCHAR: true,
        T: true
      },
      NUMBER: {
        BOOLEAN: false,
        TIMESTAMP: false,
        DATE: false,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: true,
        DOUBLE: true,
        DECIMAL: true,
        NUMBER: true,
        STRING: true,
        CHAR: true,
        VARCHAR: true,
        T: true
      },
      STRING: {
        BOOLEAN: false,
        TIMESTAMP: true,
        DATE: true,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: true,
        DOUBLE: true,
        DECIMAL: true,
        NUMBER: true,
        STRING: true,
        CHAR: true,
        VARCHAR: true,
        T: true
      },
      CHAR: {
        BOOLEAN: false,
        TIMESTAMP: true,
        DATE: true,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: true,
        DOUBLE: true,
        DECIMAL: true,
        NUMBER: true,
        STRING: true,
        CHAR: true,
        VARCHAR: true,
        T: true
      },
      VARCHAR: {
        BOOLEAN: false,
        TIMESTAMP: true,
        DATE: true,
        BINARY: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: true,
        DOUBLE: true,
        DECIMAL: true,
        NUMBER: true,
        STRING: true,
        CHAR: true,
        VARCHAR: true,
        T: true
      },
      T: {
        BOOLEAN: true,
        TIMESTAMP: true,
        DATE: true,
        BINARY: true,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        FLOAT: true,
        DOUBLE: true,
        DECIMAL: true,
        NUMBER: true,
        STRING: true,
        CHAR: true,
        VARCHAR: true,
        T: true
      }
    },
    impala: {
      BOOLEAN: {
        BOOLEAN: true,
        TIMESTAMP: false,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: false,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      TIMESTAMP: {
        BOOLEAN: false,
        TIMESTAMP: true,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: false,
        CHAR: false,
        VARCHAR: false,
        STRING: true,
        T: true
      },
      TINYINT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      SMALLINT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: true,
        INT: false,
        BIGINT: false,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      INT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: false,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      BIGINT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      DOUBLE: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        DOUBLE: true,
        REAL: true,
        DECIMAL: false,
        FLOAT: true,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      REAL: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        DOUBLE: true,
        REAL: true,
        DECIMAL: false,
        FLOAT: true,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      DECIMAL: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        DOUBLE: true,
        REAL: true,
        DECIMAL: true,
        FLOAT: true,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      FLOAT: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: true,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      NUMBER: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        DOUBLE: true,
        REAL: true,
        DECIMAL: true,
        FLOAT: true,
        NUMBER: true,
        CHAR: false,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      CHAR: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: false,
        CHAR: true,
        VARCHAR: false,
        STRING: false,
        T: true
      },
      VARCHAR: {
        BOOLEAN: false,
        TIMESTAMP: false,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: false,
        CHAR: true,
        VARCHAR: true,
        STRING: false,
        T: true
      },
      STRING: {
        BOOLEAN: false,
        TIMESTAMP: true,
        TINYINT: false,
        SMALLINT: false,
        INT: false,
        BIGINT: false,
        DOUBLE: false,
        REAL: false,
        DECIMAL: false,
        FLOAT: false,
        NUMBER: false,
        CHAR: true,
        VARCHAR: false,
        STRING: true,
        T: true
      },
      T: {
        BOOLEAN: true,
        TIMESTAMP: true,
        TINYINT: true,
        SMALLINT: true,
        INT: true,
        BIGINT: true,
        DOUBLE: true,
        REAL: true,
        DECIMAL: true,
        FLOAT: true,
        NUMBER: true,
        CHAR: true,
        VARCHAR: true,
        STRING: true,
        T: true
      }
    }
  };

  const createDocHtml = function(funcDesc) {
    let html =
      '<div class="fn-details"><p><span class="fn-sig">' + funcDesc.signature + '</span></p>';
    if (funcDesc.description) {
      html += '<p>' + funcDesc.description.replace(/[<]/g, '&lt;').replace(/[>]/g, '&gt;') + '</p>';
    }
    html += '<div>';
    return html;
  };

  const stripPrecision = function(types) {
    const result = [];
    types.forEach(type => {
      if (type.indexOf('(') > -1) {
        result.push(type.substring(0, type.indexOf('(')));
      } else {
        result.push(type);
      }
    });
    return result;
  };

  /**
   * Matches types based on implicit conversion i.e. if you expect a BIGINT then INT is ok but not BOOLEAN etc.
   *
   * @param dialect
   * @param expectedTypes
   * @param actualRawTypes
   * @returns {boolean}
   */
  const matchesType = function(dialect, expectedTypes, actualRawTypes) {
    if (dialect !== 'hive') {
      dialect = 'impala';
    }
    if (expectedTypes.length === 1 && expectedTypes[0] === 'T') {
      return true;
    }
    const actualTypes = stripPrecision(actualRawTypes);
    if (
      actualTypes.indexOf('ARRAY') !== -1 ||
      actualTypes.indexOf('MAP') !== -1 ||
      actualTypes.indexOf('STRUCT') !== -1
    ) {
      return true;
    }
    for (let i = 0; i < expectedTypes.length; i++) {
      for (let j = 0; j < actualTypes.length; j++) {
        // To support future unknown types
        if (
          typeof typeImplicitConversion[dialect][expectedTypes[i]] === 'undefined' ||
          typeof typeImplicitConversion[dialect][expectedTypes[i]][actualTypes[j]] == 'undefined'
        ) {
          return true;
        }
        if (
          typeImplicitConversion[dialect][expectedTypes[i]] &&
          typeImplicitConversion[dialect][expectedTypes[i]][actualTypes[j]]
        ) {
          return true;
        }
      }
    }
    return false;
  };

  const addFunctions = function(functionIndex, dialect, returnTypes, result) {
    const indexForDialect = functionIndex[dialect || 'generic'];
    if (indexForDialect) {
      Object.keys(indexForDialect).forEach(funcName => {
        const func = indexForDialect[funcName];
        if (
          typeof returnTypes === 'undefined' ||
          matchesType(dialect, returnTypes, func.returnTypes)
        ) {
          result[funcName] = func;
        }
      });
    }
    if (functionIndex.shared) {
      Object.keys(functionIndex.shared).forEach(funcName => {
        const func = functionIndex.shared[funcName];
        if (
          typeof returnTypes === 'undefined' ||
          matchesType(dialect, returnTypes, func.returnTypes)
        ) {
          result[funcName] = func;
        }
      });
    }
  };

  const getFunctionsWithReturnTypes = function(
    dialect,
    returnTypes,
    includeAggregate,
    includeAnalytic
  ) {
    const result = {};
    addFunctions(BIT_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(COLLECTION_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(CONDITIONAL_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(COMPLEX_TYPE_CONSTRUCTS, dialect, returnTypes, result);
    addFunctions(DATE_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(MATHEMATICAL_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(TYPE_CONVERSION_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(STRING_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(DATA_MASKING_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(MISC_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(TABLE_GENERATING_FUNCTIONS, dialect, returnTypes, result);
    if (includeAggregate) {
      addFunctions(AGGREGATE_FUNCTIONS, dialect, returnTypes, result);
    }
    if (includeAnalytic) {
      addFunctions(ANALYTIC_FUNCTIONS, dialect, returnTypes, result);
    }
    return result;
  };

  const suggestFunctions = function(
    dialect,
    returnTypes,
    includeAggregate,
    includeAnalytic,
    completions,
    weight
  ) {
    const functionsToSuggest = getFunctionsWithReturnTypes(
      dialect,
      returnTypes,
      includeAggregate,
      includeAnalytic
    );
    Object.keys(functionsToSuggest).forEach(name => {
      completions.push({
        value: name + '()',
        meta: functionsToSuggest[name].returnTypes.join('|'),
        weight:
          returnTypes.filter(type => {
            return (
              functionsToSuggest[name].returnTypes.filter(otherType => {
                return otherType === type;
              }).length > 0
            );
          }).length > 0
            ? weight + 1
            : weight,
        docHTML: createDocHtml(functionsToSuggest[name])
      });
    });
  };

  const findFunction = function(dialect, functionName) {
    return (
      BIT_FUNCTIONS[dialect][functionName] ||
      COLLECTION_FUNCTIONS[dialect][functionName] ||
      CONDITIONAL_FUNCTIONS[dialect][functionName] ||
      COMPLEX_TYPE_CONSTRUCTS[dialect][functionName] ||
      DATE_FUNCTIONS[dialect][functionName] ||
      MATHEMATICAL_FUNCTIONS[dialect][functionName] ||
      TYPE_CONVERSION_FUNCTIONS[dialect][functionName] ||
      STRING_FUNCTIONS[dialect][functionName] ||
      DATA_MASKING_FUNCTIONS[dialect][functionName] ||
      MISC_FUNCTIONS[dialect][functionName] ||
      TABLE_GENERATING_FUNCTIONS[dialect][functionName] ||
      AGGREGATE_FUNCTIONS[dialect][functionName] ||
      ANALYTIC_FUNCTIONS[dialect][functionName]
    );
  };

  const getArgumentTypes = function(dialect, functionName, argumentPosition) {
    if (dialect !== 'hive' && dialect !== 'impala') {
      return ['T'];
    }
    const foundFunction = findFunction(dialect, functionName);
    if (!foundFunction) {
      return ['T'];
    }
    const args = foundFunction.arguments;
    if (argumentPosition > args.length) {
      const multiples = args[args.length - 1].filter(type => {
        return type.multiple;
      });
      if (multiples.length > 0) {
        return multiples
          .map(argument => {
            return argument.type;
          })
          .sort();
      }
      return [];
    }
    return args[argumentPosition - 1]
      .map(argument => {
        return argument.type;
      })
      .sort();
  };

  const getReturnTypes = function(dialect, functionName) {
    if (dialect !== 'hive' && dialect !== 'impala') {
      return ['T'];
    }
    const foundFunction = findFunction(dialect, functionName);
    if (!foundFunction) {
      return ['T'];
    }
    return foundFunction.returnTypes;
  };

  return {
    suggestFunctions: suggestFunctions,
    getArgumentTypes: getArgumentTypes,
    CATEGORIZED_FUNCTIONS: CATEGORIZED_FUNCTIONS,
    getFunctionsWithReturnTypes: getFunctionsWithReturnTypes,
    getReturnTypes: getReturnTypes,
    matchesType: matchesType,
    findFunction: findFunction
  };
})();

export { PigFunctions, SqlSetOptions, SqlFunctions };
