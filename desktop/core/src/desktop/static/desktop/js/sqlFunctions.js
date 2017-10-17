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

var PigFunctions = (function () {
  var EVAL_FUNCTIONS = {
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

  var RELATIONAL_OPERATORS = {
    cogroup: { signature: 'COGROUP %VAR% BY %VAR%', draggable: 'COGROUP %VAR% BY %VAR%' },
    cross: { signature: 'CROSS %VAR1%, %VAR2%;', draggable: 'CROSS %VAR1%, %VAR2%;' },
    distinct: { signature: 'DISTINCT %VAR%;', draggable: 'DISTINCT %VAR%;' },
    filter: { signature: 'FILTER %VAR% BY %COND%', draggable: 'FILTER %VAR% BY %COND%' },
    flatten: { signature: 'FLATTEN(%VAR%)', draggable: 'FLATTEN()' },
    foreach_generate: { signature: 'FOREACH %DATA% GENERATE %NEW_DATA%;', draggable: 'FOREACH %DATA% GENERATE %NEW_DATA%;' },
    foreach: { signature: 'FOREACH %DATA% {%NESTED_BLOCK%};', draggable: 'FOREACH %DATA% {%NESTED_BLOCK%};' },
    group_by: { signature: 'GROUP %VAR% BY %VAR%', draggable: 'GROUP %VAR% BY %VAR%' },
    group_all: { signature: 'GROUP %VAR% ALL', draggable: 'GROUP %VAR% ALL' },
    join: { signature: 'JOIN %VAR% BY ', draggable: 'JOIN %VAR% BY ' },
    limit: { signature: 'LIMIT %VAR% %N%', draggable: 'LIMIT %VAR% %N%' },
    order: { signature: 'ORDER %VAR% BY %FIELD%', draggable: 'ORDER %VAR% BY %FIELD%' },
    sample: { signature: 'SAMPLE %VAR% %SIZE%', draggable: 'SAMPLE %VAR% %SIZE%' },
    split: { signature: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%', draggable: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%' },
    union: { signature: 'UNION %VAR1%, %VAR2%', draggable: 'UNION %VAR1%, %VAR2%' }
  };

  var INPUT_OUTPUT = {
    load: { signature: 'LOAD \'%FILE%\';',  draggable: 'LOAD \'%FILE%\';' },
    dump: { signature: 'DUMP %VAR%;', draggable: 'DUMP %VAR%;' },
    store: { signature: 'STORE %VAR% INTO %PATH%;', draggable: 'STORE %VAR% INTO %PATH%;' }
  };

  var DEBUG = {
    explain: { signature: 'EXPLAIN %VAR%;', draggable: 'EXPLAIN %VAR%;' },
    illustrate: { signature: 'ILLUSTRATE %VAR%;' , draggable: 'ILLUSTRATE %VAR%;' },
    describe: { signature: 'DESCRIBE %VAR%;', draggable: 'DESCRIBE %VAR%;' }
  };

  var HCATALOG = {
    LOAD: { signature: 'LOAD \'%TABLE%\' USING org.apache.hcatalog.pig.HCatLoader();', draggable: 'LOAD \'%TABLE%\' USING org.apache.hcatalog.pig.HCatLoader();' }
  };

  var MATH_FUNCTIONS = {
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

  var TUPLE_BAG_MAP = {
    totuple: { signature: 'TOTUPLE(%VAR%)',draggable: 'TOTUPLE()' },
    tobag: { signature: 'TOBAG(%VAR%)',draggable: 'TOBAG()' },
    tomap: { signature: 'TOMAP(%KEY%, %VALUE%)',draggable: 'TOMAP()' },
    top: { signature: 'TOP(%topN%, %COLUMN%, %RELATION%)',draggable: 'TOP()' }
  };

  var STRING_FUNCTIONS = {
    indexof: { signature: 'INDEXOF(%STRING%, \'%CHARACTER%\', %STARTINDEX%)',draggable: 'INDEXOF()' },
    last_index_of: { signature: 'LAST_INDEX_OF(%STRING%, \'%CHARACTER%\', %STARTINDEX%)',draggable: 'LAST_INDEX_OF()' },
    lower: { signature: 'LOWER(%STRING%)',draggable: 'LOWER()' },
    regex_extract: { signature: 'REGEX_EXTRACT(%STRING%, %REGEX%, %INDEX%)',draggable: 'REGEX_EXTRACT()' },
    regex_extract_all: { signature: 'REGEX_EXTRACT_ALL(%STRING%, %REGEX%)',draggable: 'REGEX_EXTRACT_ALL()' },
    replace: { signature: 'REPLACE(%STRING%, \'%oldChar%\', \'%newChar%\')',draggable: 'REPLACE()' },
    strsplit: { signature: 'STRSPLIT(%STRING%, %REGEX%, %LIMIT%)',draggable: 'STRSPLIT()' },
    substring: { signature: 'SUBSTRING(%STRING%, %STARTINDEX%, %STOPINDEX%)',draggable: 'SUBSTRING()' },
    trim: { signature: 'TRIM(%STRING%)',draggable: 'TRIM()' },
    ucfirst: { signature: 'UCFIRST(%STRING%)',draggable: 'UCFIRST()' },
    upper: { signature: 'UPPER(%STRING%)',draggable: 'UPPER()' }
  };

  var MACROS = {
    import: { signature: 'IMPORT \'%PATH_TO_MACRO%\';', draggable: 'IMPORT \'%PATH_TO_MACRO%\';' }
  };

  var HBASE = {
    load: { signature: 'LOAD \'hbase://%TABLE%\' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage(\'%columnList%\')', draggable: 'LOAD \'hbase://%TABLE%\' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage(\'%columnList%\')' },
    store: { signature: 'STORE %VAR% INTO \'hbase://%TABLE%\' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage(\'%columnList%\')', draggable: 'STORE %VAR% INTO \'hbase://%TABLE%\' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage(\'%columnList%\')' }
  };

  var PYTHON_UDF = {
    register: { signature: 'REGISTER \'python_udf.py\' USING jython AS myfuncs;', draggable: 'REGISTER \'python_udf.py\' USING jython AS myfuncs;' }
  };

  var CATEGORIZED_FUNCTIONS = [
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
  }
})();

var SqlSetOptions = (function () {
  var SET_OPTIONS = {
    hive: {
      'hive.execution.engine': {
        description: 'Chooses execution engine.',
        type: 'String; Options are: mr (Map reduce, default), tez (Tez execution, for Hadoop 2 only), or spark (Spark execution, for Hive 1.1.0 onward).',
        default: 'mr'
      },
      'mapred.reduce.tasks': {
        description: 'The default number of reduce tasks per job. Typically set to a prime close to the number of available hosts. Ignored when mapred.job.tracker is "local". Hadoop set this to 1 by default, whereas Hive uses -1 as its default value. By setting this property to -1, Hive will automatically figure out what should be the number of reducers.',
        type: 'Numeric',
        default: '-1'
      },
      'hive.exec.reducers.bytes.per.reducer': {
        description: 'Size per reducer. The default in Hive 0.14.0 and earlier is 1 GB, that is, if the input size is 10 GB then 10 reducers will be used. In Hive 0.14.0 and later the default is 256 MB, that is, if the input size is 1 GB then 4 reducers will be used.',
        type: 'Numeric',
        default: '1,000,000,000 prior to Hive 0.14.0; 256 MB (256,000,000) in Hive 0.14.0 and later'
      },
      'hive.exec.reducers.max': {
        description: 'Maximum number of reducers that will be used. If the one specified in the configuration property mapred.reduce.tasks is negative, Hive will use this as the maximum number of reducers when automatically determining the number of reducers.',
        type: 'Numeric',
        default: '999 prior to Hive 0.14.0; 1009 in Hive 0.14.0 and later'
      },
      'hive.jar.path': {
        description: 'The location of hive_cli.jar that is used when submitting jobs in a separate jvm.',
        type: 'String',
        default: '(empty)'
      },
      'hive.aux.jars.path': {
        description: 'The location of the plugin jars that contain implementations of user defined functions (UDFs) and SerDes.',
        type: 'String',
        default: '(empty)'
      },
      'hive.reloadable.aux.jars.path': {
        description: 'The locations of the plugin jars, which can be comma-separated folders or jars. They can be renewed (added, removed, or updated) by executing the Beeline reload command without having to restart HiveServer2. These jars can be used just like the auxiliary classes in hive.aux.jars.path for creating UDFs or SerDes.',
        type: 'String',
        default: '(empty)'
      },
      'hive.exec.scratchdir': {
        description: 'Scratch space for Hive jobs. This directory is used by Hive to store the plans for different map/reduce stages for the query as well as to stored the intermediate outputs of these stages. Hive 0.14.0 and later:  HDFS root scratch directory for Hive jobs, which gets created with write all (733) permission. For each connecting user, an HDFS scratch directory ${hive.exec.scratchdir}/<username> is created with ${hive.scratch.dir.permission}. Also see hive.start.cleanup.scratchdir and hive.scratchdir.lock.',
        type: 'String',
        default: '/tmp/${user.name} in Hive 0.2.0 through 0.8.0; /tmp/hive-${user.name} in Hive 0.8.1 through 0.14.0; or /tmp/hive in Hive 0.14.0 and later'
      },
      'hive.scratch.dir.permission': {
        description: 'The permission for the user-specific scratch directories that get created in the root scratch directory. (See hive.exec.scratchdir.)',
        type: 'Numeric',
        default: '700'
      },
      'hive.map.aggr': {
        description: 'Whether to use map-side aggregation in Hive Group By queries.',
        type: 'Boolean',
        default: 'true in Hive 0.3 and later; false in Hive 0.2'
      },
      'hive.groupby.skewindata': {
        description: 'Whether there is skew in data to optimize group by queries.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.groupby.mapaggr.checkinterval': {
        description: 'Number of rows after which size of the grouping keys/aggregation classes is performed.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.new.job.grouping.set.cardinality': {
        description: 'Whether a new map-reduce job should be launched for grouping sets/rollups/cubes.\n\nFor a query like "select a, b, c, count(1) from T group by a, b, c with rollup;" four rows are created per row: (a, b, c), (a, b, null), (a, null, null), (null, null, null). This can lead to explosion across the map-reduce boundary if the cardinality of T is very high, and map-side aggregation does not do a very good job.\n\nThis parameter decides if Hive should add an additional map-reduce job. If the grouping set cardinality (4 in the example above) is more than this value, a new MR job is added under the assumption that the orginal "group by" will reduce the data size.',
        type: 'Numeric',
        default: '30'
      },
      'hive.mapred.local.mem': {
        description: 'For local mode, memory of the mappers/reducers.',
        type: 'Numeric',
        default: '0'
      },
      'hive.map.aggr.hash.force.flush.memory.threshold': {
        description: 'The maximum memory to be used by map-side group aggregation hash table. If the memory usage is higher than this number, force to flush data.',
        type: 'Numeric',
        default: '0.9'
      },
      'hive.map.aggr.hash.percentmemory': {
        description: 'Portion of total memory to be used by map-side group aggregation hash table.',
        type: 'Numeric',
        default: '0.5'
      },
      'hive.map.aggr.hash.min.reduction': {
        description: 'Hash aggregation will be turned off if the ratio between hash table size and input rows is bigger than this number. Set to 1 to make sure hash aggregation is never turned off.',
        type: 'Numeric',
        default: '0.5'
      },
      'hive.optimize.groupby': {
        description: 'Whether to enable the bucketed group by from bucketed partitions/tables.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.countdistinct': {
        description: 'Whether to rewrite count distinct into 2 stages, i.e., the first stage uses multiple reducers with the count distinct key and the second stage uses a single reducer without key.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.remove.sq_count_check': {
        description: 'Whether to remove an extra join with sq_count_check UDF for scalar subqueries with constant group by keys. ',
        type: 'Boolean',
        default: 'false'
      },
      'hive.multigroupby.singlereducer': {
        description: 'Whether to optimize multi group by query to generate a single M/R  job plan. If the multi group by query has common group by keys, it will be optimized to generate a single M/R job.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.index.filter': {
        description: 'Whether to enable automatic use of indexes.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.ppd': {
        description: 'Whether to enable predicate pushdown (PPD). Note: Turn on hive.optimize.index.filter as well to use file format specific indexes with PPD.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.ppd.storage': {
        description: 'Whether to push predicates down into storage handlers. Ignored when hive.optimize.ppd is false.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.ppd.remove.duplicatefilters': {
        description: 'During query optimization, filters may be pushed down in the operator tree. If this config is true, only pushed down filters remain in the operator tree, and the original filter is removed. If this config is false, the original filter is also left in the operator tree at the original place.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.ppd.recognizetransivity': {
        description: 'Whether to transitively replicate predicate filters over equijoin conditions.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.join.emit.interval': {
        description: 'How many rows in the right-most join operand Hive should buffer before emitting the join result.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.join.cache.size': {
        description: 'How many rows in the joining tables (except the streaming table) should be cached in memory.',
        type: 'Numeric',
        default: '25000'
      },
      'hive.mapjoin.followby.map.aggr.hash.percentmemory': {
        description: 'Portion of total memory to be used by map-side group aggregation hash table, when this group by is followed by map join.',
        type: 'Numeric',
        default: '0.3'
      },
      'hive.smalltable.filesize': {
        description: 'The threshold (in bytes) for the input file size of the small tables; if the file size is smaller than this threshold, it will try to convert the common join into map join.',
        type: 'Numeric',
        default: '25000000'
      },
      'hive.mapjoin.localtask.max.memory.usage': {
        description: 'This number means how much memory the local task can take to hold the key/value into an in-memory hash table. If the local task\'s memory usage is more than this number, the local task will be aborted. It means the data of small table is too large to be held in memory.',
        type: 'Numeric',
        default: '0.90'
      },
      'hive.mapjoin.followby.gby.localtask.max.memory.usage': {
        description: 'This number means how much memory the local task can take to hold the key/value into an in-memory hash table when this map join is followed by a group by. If the local task\'s memory usage is more than this number, the local task will abort by itself. It means the data of the small table is too large to be held in memory.',
        type: 'Numeric',
        default: '0.55'
      },
      'hive.mapjoin.check.memory.rows': {
        description: 'The number means after how many rows processed it needs to check the memory usage.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.ignore.mapjoin.hint': {
        description: 'Whether Hive ignores the mapjoin hint.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.smbjoin.cache.rows': {
        description: 'How many rows with the same key value should be cached in memory per sort-merge-bucket joined table.',
        type: 'Numeric',
        default: '10000'
      },
      'hive.mapjoin.optimized.hashtable': {
        description: 'Whether Hive should use a memory-optimized hash table for MapJoin. Only works on Tez and Spark, because memory-optimized hash table cannot be serialized. (Spark is supported starting from Hive 1.3.0, with HIVE-11180.)',
        type: 'Boolean',
        default: 'true'
      },
      'hive.mapjoin.optimized.hashtable.wbsize': {
        description: 'Optimized hashtable (see hive.mapjoin.optimized.hashtable) uses a chain of buffers to store data. This is one buffer size. Hashtable may be slightly faster if this is larger, but for small joins unnecessary memory will be allocated and then trimmed.',
        type: 'Numeric',
        default: '10485760 (10 * 1024 * 1024)'
      },
      'hive.hashtable.initialCapacity': {
        description: 'Initial capacity of mapjoin hashtable if statistics are absent, or if hive.hashtable.key.count.adjustment is set to 0.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.hashtable.key.count.adjustment': {
        description: 'Adjustment to mapjoin hashtable size derived from table and column statistics; the estimate of the number of keys is divided by this value. If the value is 0, statistics are not used and hive.hashtable.initialCapacity is used instead.',
        type: 'Numeric',
        default: '1.0'
      },
      'hive.hashtable.loadfactor': {
        description: 'In the process of Mapjoin, the key/value will be held in the hashtable. This value means the load factor for the in-memory hashtable.',
        type: 'Numeric',
        default: '0.75'
      },
      'hive.debug.localtask': {
        description: '',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.skewjoin': {
        description: 'Whether to enable skew join optimization.  (Also see hive.optimize.skewjoin.compiletime.)',
        type: 'Boolean',
        default: 'false'
      },
      'hive.skewjoin.key': {
        description: 'Determine if we get a skew key in join. If we see more than the specified number of rows with the same key in join operator, we think the key as a skew join key.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.skewjoin.mapjoin.map.tasks': {
        description: 'Determine the number of map task used in the follow up map join job for a skew join. It should be used together with hive.skewjoin.mapjoin.min.split to perform a fine grained control.',
        type: 'Numeric',
        default: '10000'
      },
      'hive.skewjoin.mapjoin.min.split': {
        description: 'Determine the number of map task at most used in the follow up map join job for a skew join by specifying the minimum split size. It should be used together with hive.skewjoin.mapjoin.map.tasks to perform a fine grained control.',
        type: 'Numeric',
        default: '33554432'
      },
      'hive.optimize.skewjoin.compiletime': {
        description: 'Whether to create a separate plan for skewed keys for the tables in the join. This is based on the skewed keys stored in the metadata. At compile time, the plan is broken into different joins: one for the skewed keys, and the other for the remaining keys. And then, a union is performed for the two joins generated above. So unless the same skewed key is present in both the joined tables, the join for the skewed key will be performed as a map-side join.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.union.remove': {
        description: 'Whether to remove the union and push the operators between union and the filesink above union. This avoids an extra scan of the output by union. This is independently useful for union queries, and especially useful when hive.optimize.skewjoin.compiletime is set to true, since an extra union is inserted.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.mapred.supports.subdirectories': {
        description: 'Whether the version of Hadoop which is running supports sub-directories for tables/partitions. Many Hive optimizations can be applied if the Hadoop version supports sub-directories for tables/partitions. This support was added by MAPREDUCE-1501.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.mapred.mode': {
        description: 'The mode in which the Hive operations are being performed. In strict mode, some risky queries are not allowed to run. For example, full table scans are prevented (see HIVE-10454) and ORDER BY requires a LIMIT clause.',
        type: 'String',
        default: 'Hive 1.x: nonstrict, Hive 2.x: strict'
      },
      'hive.exec.script.maxerrsize': {
        description: 'Maximum number of bytes a script is allowed to emit to standard error (per map-reduce task). This prevents runaway scripts from filling logs partitions to capacity.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.script.auto.progress': {
        description: 'Whether Hive Tranform/Map/Reduce Clause should automatically send progress information to TaskTracker to avoid the task getting killed because of inactivity. Hive sends progress information when the script is outputting to stderr. This option removes the need of periodically producing stderr messages, but users should be cautious because this may prevent infinite loops in the scripts to be killed by TaskTracker.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exec.script.allow.partial.consumption': {
        description: 'When enabled, this option allows a user script to exit successfully without consuming all the data from the standard input.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.script.operator.id.env.var': {
        description: 'Name of the environment variable that holds the unique script operator ID in the user\'s transform function (the custom mapper/reducer that the user has specified in the query).',
        type: 'String',
        default: 'HIVE_SCRIPT_OPERATOR_ID'
      },
      'hive.script.operator.env.blacklist': {
        description: 'By default all values in the HiveConf object are converted to environment variables of the same name as the key (with \'.\' (dot) converted to \'_\' (underscore)) and set as part of the script operator\'s environment.  However, some values can grow large or are not amenable to translation to environment variables.  This value gives a comma separated list of configuration values that will not be set in the environment when calling a script operator.  By default the valid transaction list is excluded, as it can grow large and is sometimes compressed, which does not translate well to an environment variable.',
        type: 'String',
        default: 'hive.txn.valid.txns,hive.script.operator.env.blacklist'
      },
      'hive.exec.compress.output': {
        description: 'This controls whether the final outputs of a query (to a local/hdfs file or a Hive table) is compressed. The compression codec and other options are determined from Hadoop configuration variables mapred.output.compress* .',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exec.compress.intermediate': {
        description: 'This controls whether intermediate files produced by Hive between multiple map-reduce jobs are compressed. The compression codec and other options are determined from Hadoop configuration variables mapred.output.compress*.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exec.parallel': {
        description: 'Whether to execute jobs in parallel.  Applies to MapReduce jobs that can run in parallel, for example jobs processing different source tables before a join.  As of Hive 0.14, also applies to move tasks that can run in parallel, for example moving files to insert targets during multi-insert.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exec.parallel.thread.number': {
        description: 'How many jobs at most can be executed in parallel.',
        type: 'Numeric',
        default: '8'
      },
      'hive.exec.rowoffset': {
        description: 'Whether to provide the row offset virtual column.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.counters.group.name': {
        description: 'Counter group name for counters used during query execution. The counter group is used for internal Hive variables (CREATED_FILE, FATAL_ERROR, and so on).',
        type: 'String',
        default: 'HIVE'
      },
      'hive.exec.pre.hooks': {
        description: 'Comma-separated list of pre-execution hooks to be invoked for each statement. A pre-execution hook is specified as the name of a Java class which implements the org.apache.hadoop.hive.ql.hooks.ExecuteWithHookContext interface.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.exec.post.hooks': {
        description: 'Comma-separated list of post-execution hooks to be invoked for each statement. A post-execution hook is specified as the name of a Java class which implements the org.apache.hadoop.hive.ql.hooks.ExecuteWithHookContext interface.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.exec.failure.hooks': {
        description: 'Comma-separated list of on-failure hooks to be invoked for each statement. An on-failure hook is specified as the name of Java class which implements the org.apache.hadoop.hive.ql.hooks.ExecuteWithHookContext interface.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.merge.mapfiles': {
        description: 'Merge small files at the end of a map-only job.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.merge.mapredfiles': {
        description: 'Merge small files at the end of a map-reduce job.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.merge.size.per.task': {
        description: 'Size of merged files at the end of the job.',
        type: 'Numeric',
        default: '256000000'
      },
      'hive.merge.smallfiles.avgsize': {
        description: 'When the average output file size of a job is less than this number, Hive will start an additional map-reduce job to merge the output files into bigger files. This is only done for map-only jobs if hive.merge.mapfiles is true, and for map-reduce jobs if hive.merge.mapredfiles is true.',
        type: 'Numeric',
        default: '16000000'
      },
      'hive.heartbeat.interval': {
        description: 'Send a heartbeat after this interval – used by mapjoin and filter operators.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.auto.convert.join': {
        description: 'Whether Hive enables the optimization about converting common join into mapjoin based on the input file size. (Note that hive-default.xml.template incorrectly gives the default as false in Hive 0.11.0 through 0.13.1.)',
        type: 'Boolean',
        default: 'false in 0.7.0 to 0.10.0; true in 0.11.0 and later (HIVE-3297)  '
      },
      'hive.auto.convert.join.noconditionaltask': {
        description: 'Whether Hive enables the optimization about converting common join into mapjoin based on the input file size. If this parameter is on, and the sum of size for n-1 of the tables/partitions for an n-way join is smaller than the size specified by hive.auto.convert.join.noconditionaltask.size, the join is directly converted to a mapjoin (there is no conditional task).',
        type: 'Boolean',
        default: 'true'
      },
      'hive.auto.convert.join.noconditionaltask.size': {
        description: 'If hive.auto.convert.join.noconditionaltask is off, this parameter does not take effect. However, if it is on, and the sum of size for n-1 of the tables/partitions for an n-way join is smaller than this size, the join is directly converted to a mapjoin (there is no conditional task). The default is 10MB.',
        type: 'Numeric',
        default: '10000000'
      },
      'hive.auto.convert.join.use.nonstaged': {
        description: 'For conditional joins, if input stream from a small alias can be directly applied to the join operator without filtering or projection, the alias need not be pre-staged in the distributed cache via a mapred local task. Currently, this is not working with vectorization or Tez execution engine.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.merge.nway.joins': {
        description: 'For multiple joins on the same condition, merge joins together into a single join operator. This is useful in the case of large shuffle joins to avoid a reshuffle phase. Disabling this in Tez will often provide a faster join algorithm in case of left outer joins or a general Snowflake schema.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.udtf.auto.progress': {
        description: 'Whether Hive should automatically send progress information to TaskTracker when using UDTF\'s to prevent the task getting killed because of inactivity. Users should be cautious because this may prevent TaskTracker from killing tasks with infinite loops.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.mapred.reduce.tasks.speculative.execution': {
        description: 'Whether speculative execution for reducers should be turned on.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.exec.counters.pull.interval': {
        description: 'The interval with which to poll the JobTracker for the counters the running job. The smaller it is the more load there will be on the jobtracker, the higher it is the less granular the caught will be.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.optimize.bucketingsorting': {
        description: 'If hive.enforce.bucketing or hive.enforce.sorting is true, don\'t create a reducer for enforcing bucketing/sorting for queries of the form: insert overwrite table T2 select * from T1; where T1 and T2 are bucketed/sorted by the same keys into the same number of buckets. (In Hive 2.0.0 and later, this parameter does not depend on hive.enforce.bucketing or hive.enforce.sorting.)',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.reducededuplication': {
        description: 'Remove extra map-reduce jobs if the data is already clustered by the same key which needs to be used again. This should always be set to true. Since it is a new feature, it has been made configurable.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.reducededuplication.min.reducer': {
        description: 'Reduce deduplication merges two RSs (reduce sink operators) by moving key/parts/reducer-num of the child RS to parent RS. That means if reducer-num of the child RS is fixed (order by or forced bucketing) and small, it can make very slow, single MR. The optimization will be disabled if number of reducers is less than specified value.',
        type: 'Numeric',
        default: '4'
      },
      'hive.optimize.correlation': {
        description: 'Exploit intra-query correlations. For details see the Correlation Optimizer design document.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.limittranspose': {
        description: 'Whether to push a limit through left/right outer join or union. If the value is true and the size of the outer input is reduced enough (as specified in hive.optimize.limittranspose.reductionpercentage and hive.optimize.limittranspose.reductiontuples), the limit is pushed to the outer input or union; to remain semantically correct, the limit is kept on top of the join or the union too.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.limittranspose.reductionpercentage': {
        description: 'When hive.optimize.limittranspose is true, this variable specifies the minimal percentage (fractional) reduction of the size of the outer input of the join or input of the union that the optimizer should get in order to apply the rule.',
        type: 'Numeric',
        default: '1.0'
      },
      'hive.optimize.limittranspose.reductiontuples': {
        description: 'When hive.optimize.limittranspose is true, this variable specifies the minimal reduction in the number of tuples of the outer input of the join or input of the union that the optimizer should get in order to apply the rule.',
        type: 'Numeric',
        default: '0'
      },
      'hive.optimize.filter.stats.reduction': {
        description: 'Whether to simplify comparison expressions in filter operators using column stats.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.sort.dynamic.partition': {
        description: 'When enabled, dynamic partitioning column will be globally sorted. This way we can keep only one record writer open for each partition value in the reducer thereby reducing the memory pressure on reducers.',
        type: 'Boolean',
        default: 'true in Hive 0.13.0 and 0.13.1; false in Hive 0.14.0 and later (HIVE-8151)'
      },
      'hive.cbo.enable': {
        description: 'When true, the cost based optimizer, which uses the Calcite framework, will be enabled.',
        type: 'Boolean',
        default: 'false in Hive 0.14.*; true in Hive 1.1.0 and later (HIVE-8395)'
      },
      'hive.cbo.returnpath.hiveop': {
        description: 'When true, this optimization to CBO Logical plan will add rule to introduce not null filtering on join keys.  Controls Calcite plan to Hive operator conversion.  Overrides hive.optimize.remove.identity.project when set to false.',
        type: 'String',
        default: 'false '
      },
      'hive.cbo.cnf.maxnodes': {
        description: 'When converting to conjunctive normal form (CNF), fail if the expression exceeds the specified threshold; the threshold is expressed in terms of the number of nodes (leaves and interior nodes). The default, -1, does not set up a threshold.',
        type: 'Numeric',
        default: '-1 '
      },
      'hive.optimize.null.scan': {
        description: 'When true, this optimization will try to not scan any rows from tables which can be determined at query compile time to not generate any rows (e.g., where 1 = 2, where false, limit 0 etc.).',
        type: 'Boolean',
        default: 'true'
      },
      'hive.exec.dynamic.partition': {
        description: 'Whether or not to allow dynamic partitions in DML/DDL.',
        type: 'Boolean',
        default: 'false prior to Hive 0.9.0; true in Hive 0.9.0 and later (HIVE-2835)'
      },
      'hive.exec.dynamic.partition.mode': {
        description: 'In strict mode, the user must specify at least one static partition in case the user accidentally overwrites all partitions. In nonstrict mode all partitions are allowed to be dynamic. Set to nonstrict to support INSERT ... VALUES, UPDATE, and DELETE transactions (Hive 0.14.0 and later). For a complete list of parameters required for turning on Hive transactions, see hive.txn.manager.',
        type: 'String',
        default: 'strict'
      },
      'hive.exec.max.dynamic.partitions': {
        description: 'Maximum number of dynamic partitions allowed to be created in total.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.exec.max.dynamic.partitions.pernode': {
        description: 'Maximum number of dynamic partitions allowed to be created in each mapper/reducer node.',
        type: 'Numeric',
        default: '100'
      },
      'hive.exec.max.created.files': {
        description: 'Maximum number of HDFS files created by all mappers/reducers in a MapReduce job.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.exec.default.partition.name': {
        description: 'The default partition name in case the dynamic partition column value is null/empty string or any other values that cannot be escaped. This value must not contain any special character used in HDFS URI (e.g., \':\', \'%\', \'/\' etc). The user has to be aware that the dynamic partition value should not contain this value to avoid confusions.',
        type: 'String',
        default: '_HIVE_DEFAULT_PARTITION_'
      },
      'hive.fetch.output.serde': {
        description: 'The SerDe used by FetchTask to serialize the fetch output.',
        type: 'String',
        default: 'org.apache.hadoop.hive.serde2.DelimitedJSONSerDe'
      },
      'hive.exec.mode.local.auto': {
        description: 'Lets Hive determine whether to run in local mode automatically.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exec.mode.local.auto.inputbytes.max': {
        description: 'When hive.exec.mode.local.auto is true, input bytes should be less than this for local mode.',
        type: 'Numeric',
        default: '134217728'
      },
      'hive.exec.mode.local.auto.input.files.max': {
        description: 'When hive.exec.mode.local.auto is true, the number of tasks should be less than this for local mode.',
        type: 'Numeric',
        default: '4'
      },
      'hive.exec.drop.ignorenonexistent': {
        description: 'Do not report an error if DROP TABLE/VIEW/PARTITION/INDEX/TEMPORARY FUNCTION specifies a non-existent table/view. Also applies to permanent functions as of Hive 0.13.0.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.exec.show.job.failure.debug.info': {
        description: 'If a job fails, whether to provide a link in the CLI to the task with the most failures, along with debugging hints if applicable.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.auto.progress.timeout': {
        description: 'How long to run autoprogressor for the script/UDTF operators (in seconds). Set to 0 for forever.',
        type: 'Numeric',
        default: '0'
      },
      'hive.table.parameters.default': {
        description: 'Default property values for newly created tables.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.error.on.empty.partition': {
        description: 'Whether to throw an exception if dynamic partition insert generates empty results.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exim.uri.scheme.whitelist': {
        description: 'A comma separated list of acceptable URI schemes for import and export.',
        type: 'Strings',
        default: 'hdfs,pfile prior to Hive 2.2.0; hdfs,pfile,file in Hive 2.2.0 and later'
      },
      'hive.limit.row.max.size': {
        description: 'When trying a smaller subset of data for simple LIMIT, how much size we need to guarantee each row to have at least.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.limit.optimize.limit.file': {
        description: 'When trying a smaller subset of data for simple LIMIT, maximum number of files we can sample.',
        type: 'Numeric',
        default: '10'
      },
      'hive.limit.optimize.enable': {
        description: 'Whether to enable to optimization to trying a smaller subset of data for simple LIMIT first.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.limit.optimize.fetch.max': {
        description: 'Maximum number of rows allowed for a smaller subset of data for simple LIMIT, if it is a fetch query. Insert queries are not restricted by this limit.',
        type: 'Numeric',
        default: '50000'
      },
      'hive.rework.mapredwork': {
        description: 'Should rework the mapred work or not. This is first introduced by SymlinkTextInputFormat to replace symlink files with real paths at compile time.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.sample.seednumber': {
        description: 'A number used to percentage sampling. By changing this number, user will change the subsets of data sampled.',
        type: 'Numeric',
        default: '0'
      },
      'hive.autogen.columnalias.prefix.label': {
        description: 'String used as a prefix when auto generating column alias. By default the prefix label will be appended with a column position number to form the column alias. Auto generation would happen if an aggregate function is used in a select clause without an explicit alias.',
        type: 'String',
        default: '_c'
      },
      'hive.autogen.columnalias.prefix.includefuncname': {
        description: 'Whether to include function name in the column alias auto generated by Hive.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exec.perf.logger': {
        description: 'The class responsible logging client side performance metrics. Must be a subclass of org.apache.hadoop.hive.ql.log.PerfLogger.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.log.PerfLogger'
      },
      'hive.start.cleanup.scratchdir': {
        description: 'To clean up the Hive scratch directory while starting the Hive server (or HiveServer2). This is not an option for a multi-user environment since it will accidentally remove the scratch directory in use.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.scratchdir.lock': {
        description: 'When true, holds a lock file in the scratch directory. If a Hive process dies and accidentally leaves a dangling scratchdir behind, the cleardanglingscratchdir tool will remove it. When false, does not create a lock file and therefore the cleardanglingscratchdir tool cannot remove any dangling scratch directories.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.output.file.extension': {
        description: 'String used as a file extension for output files. If not set, defaults to the codec extension for text files (e.g. ".gz"), or no extension otherwise.',
        type: 'String',
        default: '(empty)'
      },
      'hive.insert.into.multilevel.dirs': {
        description: 'Whether to insert into multilevel nested directories like "insert directory \'/HIVEFT25686/chinna/\' from table".',
        type: 'Boolean',
        default: 'false'
      },
      'hive.conf.validation': {
        description: 'Enables type checking for registered Hive configurations.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.fetch.task.conversion': {
        description: 'Some select queries can be converted to a single FETCH task, minimizing latency. Currently the query should be single sourced not having any subquery and should not have any aggregations or distincts (which incur RS – ReduceSinkOperator, requiring a MapReduce task), lateral views and joins.',
        type: 'String',
        default: 'minimal in Hive 0.10.0 through 0.13.1, more in Hive 0.14.0 and later'
      },
      'hive.map.groupby.sorted': {
        description: 'If the bucketing/sorting properties of the table exactly match the grouping key, whether to perform the group by in the mapper by using BucketizedHiveInputFormat. The only downside to this is that it limits the number of mappers to the number of files.',
        type: 'Boolean',
        default: 'Hive 0.x and 1.x: false, Hive 2.0 and later: true'
      },
      'hive.groupby.position.alias': {
        description: 'Whether to enable using Column Position Alias in GROUP BY.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.orderby.position.alias': {
        description: 'Whether to enable using Column Position Alias in ORDER BY.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.fetch.task.aggr': {
        description: 'Aggregation queries with no group-by clause (for example, select count(*) from src) execute final aggregations in a single reduce task. If this parameter is set to true, Hive delegates the final aggregation stage to a fetch task, possibly decreasing the query time.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.fetch.task.conversion.threshold': {
        description: 'Input threshold (in bytes) for applying hive.fetch.task.conversion. If target table is native, input length is calculated by summation of file lengths. If it\'s not native, the storage handler for the table can optionally implement the org.apache.hadoop.hive.ql.metadata.InputEstimator interface. A negative threshold means hive.fetch.task.conversion is applied without any input length threshold.',
        type: 'Numeric',
        default: '-1 in Hive 0.13.0 and 0.13.1, 1073741824 (1 GB) in Hive 0.14.0 and later '
      },
      'hive.limit.pushdown.memory.usage': {
        description: 'The maximum memory to be used for hash in RS operator for top K selection. The default value "-1" means no limit.',
        type: 'Numeric',
        default: '-1'
      },
      'hive.cache.expr.evaluation': {
        description: 'If true, the evaluation result of a deterministic expression referenced twice or more will be cached. For example, in a filter condition like "... where key + 10 > 10 or key + 10 = 0" the expression "key + 10" will be evaluated/cached once and reused for the following expression ("key + 10 = 0"). Currently, this is applied only to expressions in select or filter operators.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.resultset.use.unique.column.names': {
        description: 'Make column names unique in the result set by qualifying column names with table alias if needed. Table alias will be added to column names for queries of type "select *" or if query explicitly uses table alias "select r1.x..".',
        type: 'Boolean',
        default: 'true'
      },
      'hive.support.quoted.identifiers': {
        description: 'Whether to use quoted identifiers.  Value can be "none" or "column".',
        type: 'String',
        default: 'column'
      },
      'hive.plan.serialization.format': {
        description: 'Query plan format serialization between client and task nodes. Two supported values are kryo and javaXML. Kryo is the default.',
        type: 'String',
        default: 'kryo'
      },
      'hive.exec.check.crossproducts': {
        description: 'Check if a query plan contains a cross product. If there is one, output a warning to the session\'s console.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.display.partition.cols.separately': {
        description: 'In older Hive versions (0.10 and earlier) no distinction was made between partition columns or non-partition columns while displaying columns in DESCRIBE TABLE. From version 0.12 onwards, they are displayed separately. This flag will let you get the old behavior, if desired. See test-case in patch for HIVE-6689.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.sampling.orderby': {
        description: 'Uses sampling on order-by clause for parallel execution.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.sampling.orderby.number': {
        description: 'With hive.optimize.sampling.orderby=true, total number of samples to be obtained to calculate partition keys.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.optimize.sampling.orderby.percent': {
        description: 'With hive.optimize.sampling.orderby=true, probability with which a row will be chosen.',
        type: 'Numeric',
        default: '0.1'
      },
      'hive.compat': {
        description: 'Enable (configurable) deprecated behaviors of arithmetic operations by setting the desired level of backward compatibility. The default value gives backward-compatible return types for numeric operations. Other supported release numbers give newer behavior for numeric operations, for example 0.13 gives the more SQL compliant return types introduced in HIVE-5356. The value "latest" specifies the latest supported level.',
        type: 'Numeric',
        default: '0.12'
      },
      'hive.optimize.constant.propagation': {
        description: 'Whether to enable the constant propagation optimizer.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.entity.capture.transform': {
        description: 'Enable capturing compiler read entity of transform URI which can be introspected in the semantic and exec hooks.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.support.sql11.reserved.keywords': {
        description: 'Whether to enable support for SQL2011 reserved keywords. When enabled, will support (part of) SQL2011 reserved keywords.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.log.explain.output': {
        description: 'When enabled, will log EXPLAIN EXTENDED output for the query at log4j INFO level and in WebUI / Drilldown / Query Plan.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.explain.user': {
        description: 'Whether to show explain result at user level. When enabled, will log EXPLAIN output for the query at user level. (Tez only.  For Spark, see hive.spark.explain.user.)',
        type: 'Boolean',
        default: 'false'
      },
      'hive.typecheck.on.insert': {
        description: 'Extended In: Hive 1.2 with HIVE-10307 for alter, describe partition, etc. Whether to check, convert, and normalize partition value specified in partition specification to conform to the partition column type.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.exec.temporary.table.storage': {
        description: 'Expects one of [memory, ssd, default]. Define the storage policy for temporary tables. Choices between memory, ssd and default. See HDFS Storage Types and Storage Policies.',
        type: 'String',
        default: 'default'
      },
      'hive.optimize.distinct.rewrite': {
        description: 'When applicable, this optimization rewrites distinct aggregates from a single-stage to multi-stage aggregation. This may not be optimal in all cases. Ideally, whether to trigger it or not should be a cost-based decision. Until Hive formalizes the cost model for this, this is config driven.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.point.lookup': {
        description: 'Whether to transform OR clauses in Filter operators into IN clauses.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.point.lookup.min': {
        description: 'Minimum number of OR clauses needed to transform into IN clauses.',
        type: 'Numeric',
        default: '31'
      },
      'hive.allow.udf.load.on.demand': {
        description: 'Whether enable loading UDFs from metastore on demand; this is mostly relevant for HS2 and was the default behavior before Hive 1.2.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.async.log.enabled': {
        description: 'Whether to enable Log4j2\'s asynchronous logging. Asynchronous logging can give significant performance improvement as logging will be handled in a separate thread that uses the LMAX disruptor queue for buffering log messages. Refer to https://logging.apache.org/log4j/2.x/manual/async.html for benefits and drawbacks.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.msck.repair.batch.size': {
        description: 'To run the MSCK REPAIR TABLE command batch-wise. If there is a large number of untracked partitions, by configuring a value to the property it will execute in batches internally. The default value of the property is zero, which means it will execute all the partitions at once.',
        type: 'Numeric',
        default: '0'
      },
      'hive.exec.copyfile.maxnumfiles': {
        description: 'Maximum number of files Hive uses to do sequential HDFS copies between directories. Distributed copies (distcp) will be used instead for larger numbers of files so that copies can be done faster.',
        type: 'Numeric',
        default: '1'
      },
      'hive.exec.copyfile.maxsize': {
        description: 'Maximum file size (in bytes) that Hive uses to do single HDFS copies between directories. Distributed copies (distcp) will be used instead for bigger files so that copies can be done faster.',
        type: 'Numeric',
        default: '32 megabytes'
      },
      'hive.exec.stagingdir': {
        description: 'Directory name that will be created inside table locations in order to support HDFS encryption. This is replaces hive.exec.scratchdir for query results with the exception of read-only tables. In all cases hive.exec.scratchdir is still used for other temporary files, such as job plans.',
        type: 'String',
        default: '.hive-staging'
      },
      'hive.query.lifetime.hooks': {
        description: 'A comma separated list of hooks which implement QueryLifeTimeHook. These will be triggered before/after query compilation and before/after query execution, in the order specified. As of Hive 3.0.0 (HIVE-16363), this config can be used to specify implementations of QueryLifeTimeHookWithParseHooks. If they are specified then they will be invoked in the same places as QueryLifeTimeHooks and will be invoked during pre and post query parsing.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.remove.orderby.in.subquery': {
        description: 'If set to true, order/sort by without limit in subqueries and views will be removed.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.script.serde': {
        description: 'The default SerDe for transmitting input data to and reading output data from the user scripts.',
        type: 'String',
        default: 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
      },
      'hive.script.recordreader': {
        description: 'The default record reader for reading data from the user scripts.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.exec.TextRecordReader'
      },
      'hive.script.recordwriter': {
        description: 'The default record writer for writing data to the user scripts.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.exec.TextRecordWriter'
      },
      'hive.default.serde': {
        description: 'The default SerDe Hive will use for storage formats that do not specify a SerDe.  Storage formats that currently do not specify a SerDe include "TextFile, RcFile".',
        type: 'String',
        default: 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
      },
      'hive.lazysimple.extended_boolean_literal': {
        description: 'LazySimpleSerDe uses this property to determine if it treats \'T\', \'t\', \'F\', \'f\', \'1\', and \'0\' as extended, legal boolean literals, in addition to \'TRUE\' and \'FALSE\'. The default is false, which means only \'TRUE\' and \'FALSE\' are treated as legal boolean literals. I/O',
        type: 'Boolean',
        default: 'false'
      },
      'hive.io.exception.handlers': {
        description: 'A list of I/O exception handler class names. This is used to construct a list of exception handlers to handle exceptions thrown by record readers.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.input.format': {
        description: 'The default input format. Set this to HiveInputFormat if you encounter problems with CombineHiveInputFormat.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.io.CombineHiveInputFormat'
      },
      'hive.default.fileformat': {
        description: 'Default file format for CREATE TABLE statement. Options are TextFile, SequenceFile, RCfile, ORC, and Parquet. Users can explicitly say CREATE TABLE ... STORED AS TEXTFILE|SEQUENCEFILE|RCFILE|ORC|AVRO|INPUTFORMAT...OUTPUTFORMAT... to override.',
        type: 'String',
        default: 'TextFile'
      },
      'hive.default.fileformat.managed': {
        description: 'Default file format for CREATE TABLE statement applied to managed tables only. External tables will be created with format specified by hive.default.fileformat. Options are none, TextFile, SequenceFile, RCfile, ORC, and Parquet (as of Hive 2.3.0). Leaving this null will result in using hive.default.fileformat for all native tables. For non-native tables the file format is determined by the storage handler, as shown below (see the StorageHandlers section for more information on managed/external and native/non-native terminology).',
        type: 'String',
        default: 'none'
      },
      'hive.fileformat.check': {
        description: 'Whether to check file format or not when loading data files.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.query.result.fileformat': {
        description: 'File format to use for a query\'s intermediate results. Options are TextFile, SequenceFile, and RCfile. Default value is changed to SequenceFile since Hive 2.1.0 (HIVE-1608).',
        type: 'String',
        default: 'Hive 0.x, 1.x, and 2.0: TextFile, Hive 2.1 onward: SequenceFile'
      },
      'hive.io.rcfile.record.interval': {
        description: '',
        type: 'Numeric',
        default: '2147483647'
      },
      'hive.io.rcfile.column.number.conf': {
        description: '',
        type: 'Numeric',
        default: '0'
      },
      'hive.io.rcfile.tolerate.corruptions': {
        description: '',
        type: 'Boolean',
        default: 'false'
      },
      'hive.io.rcfile.record.buffer.size': {
        description: 'ORC File Format.',
        type: 'Numeric',
        default: '4194304'
      },
      'hive.exec.orc.memory.pool': {
        description: 'Maximum fraction of heap that can be used by ORC file writers.',
        type: 'Numeric',
        default: '0.5'
      },
      'hive.exec.orc.write.format': {
        description: 'Define the version of the file to write. Possible values are 0.11 and 0.12. If this parameter is not defined, ORC will use the run length encoding (RLE) introduced in Hive 0.12. Any value other than 0.11 results in the 0.12 encoding.',
        type: 'Numeric',
        default: '(empty)'
      },
      'hive.exec.orc.base.delta.ratio': {
        description: 'Define the ratio of base writer and delta writer in terms of STRIPE_SIZE and BUFFER_SIZE.',
        type: 'Numeric',
        default: '8'
      },
      'hive.exec.orc.default.stripe.size': {
        description: 'Define the default ORC stripe size, in bytes.',
        type: 'Numeric',
        default: '64*1024*1024 (67,108,864) in 0.14.0, 256*1024*1024 (268,435,456) in 0.13.0;'
      },
      'hive.exec.orc.default.block.size': {
        description: 'Define the default file system block size for ORC files.',
        type: 'Numeric',
        default: '256*1024*1024 (268,435,456)'
      },
      'hive.exec.orc.dictionary.key.size.threshold': {
        description: 'If the number of keys in a dictionary is greater than this fraction of the total number of non-null rows, turn off dictionary encoding.  Use 1 to always use dictionary encoding.',
        type: 'Numeric',
        default: '0.8'
      },
      'hive.exec.orc.default.row.index.stride': {
        description: 'Define the default ORC index stride in number of rows. (Stride is the number of rows an index entry represents.)',
        type: 'Numeric',
        default: '10000'
      },
      'hive.exec.orc.default.buffer.size': {
        description: 'Define the default ORC buffer size, in bytes.',
        type: 'Numeric',
        default: '256*1024 (262,144)'
      },
      'hive.exec.orc.default.block.padding': {
        description: 'Define the default block padding. Block padding was',
        type: 'Boolean',
        default: 'true'
      },
      'hive.exec.orc.block.padding.tolerance': {
        description: 'Define the tolerance for block padding as a decimal fraction of stripe size (for example, the default value 0.05 is 5% of the stripe size). For the defaults of 64Mb ORC stripe and 256Mb HDFS blocks, a maximum of 3.2Mb will be reserved for padding within the 256Mb block with the default hive.exec.orc.block.padding.tolerance. In that case, if the available size within the block is more than 3.2Mb, a new smaller stripe will be inserted to fit within that space. This will make sure that no stripe written will cross block boundaries and cause remote reads within a node local task.',
        type: 'Numeric',
        default: '0.05'
      },
      'hive.exec.orc.default.compress': {
        description: 'Define the default compression codec for ORC file.',
        type: 'String',
        default: 'ZLIB'
      },
      'hive.exec.orc.encoding.strategy': {
        description: 'Define the encoding strategy to use while writing data. Changing this will only affect the light weight encoding for integers. This flag will not change the compression level of higher level compression codec (like ZLIB). Possible options are SPEED and COMPRESSION.',
        type: 'String',
        default: 'SPEED'
      },
      'hive.orc.splits.include.file.footer': {
        description: 'If turned on, splits generated by ORC will include metadata about the stripes in the file. This data is read remotely (from the client or HiveServer2 machine) and sent to all the tasks.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.orc.cache.stripe.details.size': {
        description: 'Cache size for keeping meta information about ORC splits cached in the client.',
        type: 'Numeric',
        default: '10000'
      },
      'hive.orc.cache.use.soft.references': {
        description: 'By default, the cache that ORC input format uses to store the ORC file footer uses hard references for the cached object. Setting this to true can help avoid out-of-memory issues under memory pressure (in some cases) at the cost of slight unpredictability in overall query performance.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.io.sarg.cache.max.weight.mb': {
        description: 'The maximum weight allowed for the SearchArgument Cache, in megabytes. By default, the cache allows a max-weight of 10MB, after which entries will be evicted. Set to 0, to disable SearchArgument caching entirely.',
        type: 'Numeric',
        default: '10'
      },
      'hive.orc.compute.splits.num.threads': {
        description: 'How many threads ORC should use to create splits in parallel.',
        type: 'Numeric',
        default: '10'
      },
      'hive.exec.orc.split.strategy': {
        description: 'What strategy ORC should use to create splits for execution. The available options are "BI", "ETL" and "HYBRID".',
        type: 'String',
        default: 'HYBRID'
      },
      'hive.exec.orc.skip.corrupt.data': {
        description: 'If ORC reader encounters corrupt data, this value will be used to determine whether to skip the corrupt data or throw an exception. The default behavior is to throw an exception.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exec.orc.zerocopy': {
        description: 'Use zerocopy reads with ORC. (This requires Hadoop 2.3 or later.)',
        type: 'Boolean',
        default: 'false'
      },
      'hive.merge.orcfile.stripe.level': {
        description: 'When hive.merge.mapfiles, hive.merge.mapredfiles or hive.merge.tezfiles is enabled while writing a table with ORC file format, enabling this configuration property will do stripe-level fast merge for small ORC files. Note that enabling this configuration property will not honor the padding tolerance configuration (hive.exec.orc.block.padding.tolerance).',
        type: 'Boolean',
        default: 'true'
      },
      'hive.orc.row.index.stride.dictionary.check': {
        description: 'If enabled dictionary check will happen after first row index stride (default 10000 rows) else dictionary check will happen before writing first stripe. In both cases, the decision to use dictionary or not will be retained thereafter.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.exec.orc.compression.strategy': {
        description: 'Define the compression strategy to use while writing data. This changes the compression level of higher level compression codec (like ZLIB). Value can be SPEED or COMPRESSION.',
        type: 'String',
        default: 'SPEED'
      },
      'hive.parquet.timestamp.skip.conversion': {
        description: 'Current Hive implementation of Parquet stores timestamps in UTC on-file, this flag allows skipping of the conversion on reading Parquet files created from other tools that may not have done so.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.vectorized.execution.enabled': {
        description: 'This flag should be set to true to enable vectorized mode of query execution. The default value is false.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.vectorized.execution.reduce.enabled': {
        description: 'This flag should be set to true to enable vectorized mode of the reduce-side of query execution. The default value is true.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.vectorized.execution.reduce.groupby.enabled': {
        description: 'This flag should be set to true to enable vectorized mode of the reduce-side GROUP BY query execution. The default value is true.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.vectorized.execution.reducesink.new.enabled': {
        description: 'This flag should be set to true to enable the new vectorization of queries using ReduceSink.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.vectorized.execution.mapjoin.native.enabled': {
        description: 'This flag should be set to true to enable native (i.e. non-pass through) vectorization of queries using MapJoin.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.vectorized.execution.mapjoin.native.multikey.only.enabled': {
        description: 'This flag should be set to true to restrict use of native vector map join hash tables to the MultiKey in queries using MapJoin.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.vectorized.execution.mapjoin.minmax.enabled': {
        description: 'This flag should be set to true to enable vector map join hash tables to use max / max filtering for integer join queries using MapJoin.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.vectorized.execution.mapjoin.overflow.repeated.threshold': {
        description: 'The number of small table rows for a match in vector map join hash tables where we use the repeated field optimization in overflow vectorized row batch for join queries using MapJoin. A value of -1 means do use the join result optimization. Otherwise, threshold value can be 0 to maximum integer.',
        type: 'Numeric',
        default: '-1'
      },
      'hive.vectorized.execution.mapjoin.native.fast.hashtable.enabled': {
        description: 'This flag should be set to true to enable use of native fast vector map join hash tables in queries using MapJoin.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.vectorized.groupby.checkinterval': {
        description: 'Number of entries added to the GROUP BY aggregation hash before a recomputation of average entry size is performed.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.vectorized.groupby.maxentries': {
        description: 'Maximum number of entries in the vector GROUP BY aggregation hashtables. Exceeding this will trigger a flush regardless of memory pressure condition.',
        type: 'Numeric',
        default: '1000000'
      },
      'hive.vectorized.use.vectorized.input.format': {
        description: 'This flag should be set to true to allow Hive to take advantage of input formats that support vectorization. The default value is true.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.vectorized.use.vector.serde.deserialize': {
        description: 'This flag should be set to true to enable vectorizing rows using vector deserialize. The default value is false.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.vectorized.use.row.serde.deserialize': {
        description: 'This flag should be set to true to enable vectorizing using row deserialize. The default value is false.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.vectorized.input.format.excludes': {
        description: 'This flag should be used to provide a comma separated list of fully qualified classnames to exclude certain FileInputFormats from vectorized execution using the vectorized file inputformat. Note that vectorized execution could still occur for that input format based on whether hive.vectorized.use.vector.serde.deserialize or hive.vectorized.use.row.serde.deserialize is enabled or not.',
        type: 'Strings',
        default: '(empty)'
      },
      'javax.jdo.option.ConnectionURL': {
        description: 'JDBC connect string for a JDBC metastore.',
        type: 'String',
        default: 'jdbc:derby:;databaseName=metastore_db;create=true'
      },
      'javax.jdo.option.ConnectionDriverName': {
        description: 'Driver class name for a JDBC metastore.',
        type: 'String',
        default: 'org.apache.derby.jdbc.EmbeddedDriver'
      },
      'javax.jdo.PersistenceManagerFactoryClass': {
        description: 'Class implementing the JDO PersistenceManagerFactory.',
        type: 'String',
        default: 'org.datanucleus.jdo.JDOPersistenceManagerFactory'
      },
      'javax.jdo.option.DetachAllOnCommit': {
        description: 'Detaches all objects from session so that they can be used after transaction is committed.',
        type: 'Boolean',
        default: 'true'
      },
      'javax.jdo.option.NonTransactionalRead': {
        description: 'Reads outside of transactions.',
        type: 'Boolean',
        default: 'true'
      },
      'javax.jdo.option.ConnectionUserName': {
        description: 'Username to use against metastore database.',
        type: 'String',
        default: 'APP'
      },
      'javax.jdo.option.ConnectionPassword': {
        description: 'Password to use against metastore database.',
        type: 'String',
        default: 'mine'
      },
      'javax.jdo.option.Multithreaded': {
        description: 'Set this to true if multiple threads access metastore through JDO concurrently.',
        type: 'Boolean',
        default: 'true'
      },
      'datanucleus.connectionPoolingType': {
        description: 'Uses a HikariCP connection pool for JDBC metastore from 3.0 release onwards (HIVE-16383). Uses a BoneCP connection pool for JDBC metastore in release 0.12 to 2.3 (HIVE-4807), or a DBCP connection pool in releases 0.7 to 0.11. As of Hive 2.2.0 (HIVE-13159), this parameter can also be set to none.',
        type: 'String',
        default: 'DBCP in Hive 0.7 to 0.11; BoneCP in 0.12 to 2.3; HikariCP in 3.0 and later'
      },
      'datanucleus.connectionPool.maxPoolSize': {
        description: 'Specify the maximum number of connections in the connection pool. Note: The configured size will be used by 2 connection pools (TxnHandler and ObjectStore).',
        type: 'Numeric',
        default: '10'
      },
      'datanucleus.schema.validateTables': {
        description: 'Validates existing schema against code. Turn this on if you want to verify existing schema.',
        type: 'Boolean',
        default: 'false'
      },
      'datanucleus.schema.validateColumns': {
        description: 'Validates existing schema against code. Turn this on if you want to verify existing schema.',
        type: 'Boolean',
        default: 'false'
      },
      'datanucleus.schema.validateConstraints': {
        description: 'Validates existing schema against code. Turn this on if you want to verify existing schema.',
        type: 'Boolean',
        default: 'false'
      },
      'datanucleus.storeManagerType': {
        description: 'Metadata store type.',
        type: 'String',
        default: 'rdbms'
      },
      'datanucleus.schema.autoCreateAll': {
        description: 'Creates necessary schema on a startup if one does not exist. Reset this to false, after creating it once.',
        type: 'Boolean',
        default: 'false'
      },
      'datanucleus.autoStartMechanismMode': {
        description: 'Throw exception if metadata tables are incorrect.',
        type: 'String',
        default: 'checked'
      },
      'datanucleus.transactionIsolation': {
        description: 'Default transaction isolation level for identity generation.',
        type: 'String',
        default: 'read-committed'
      },
      'datanucleus.cache.level2.type': {
        description: 'NONE = disable the datanucleus level 2 cache, SOFT = soft reference based cache, WEAK = weak reference based cache. Warning note: For most Hive installations, enabling the datanucleus cache can lead to correctness issues, and is dangerous. This should be left as "none".',
        type: 'String',
        default: 'none in Hive 0.9 and later; SOFT in Hive 0.7 to 0.8.1'
      },
      'datanucleus.identifierFactory': {
        description: 'Name of the identifier factory to use when generating table/column names etc. \'datanucleus\' is used for backward compatibility.',
        type: 'String',
        default: 'datanucleus'
      },
      'datanucleus.plugin.pluginRegistryBundleCheck': {
        description: 'Defines what happens when plugin bundles are found and are duplicated: EXCEPTION, LOG, or NONE.',
        type: 'String',
        default: 'LOG'
      },
      'hive.metastore.warehouse.dir': {
        description: 'Location of default database for the warehouse.',
        type: 'String',
        default: '/user/hive/warehouse'
      },
      'hive.metastore.execute.setugi': {
        description: 'In unsecure mode, true will cause the metastore to execute DFS operations using the client\'s reported user and group permissions. Note that this property must be set on both the client and server sides. Further note that it\'s best effort. If client sets it to true and server sets it to false, the client setting will be ignored.',
        type: 'String',
        default: 'false in Hive 0.8.1 through 0.13.0, true starting in Hive 0.14.0'
      },
      'hive.metastore.event.listeners': {
        description: 'List of comma-separated listeners for metastore events.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.metastore.partition.inherit.table.properties': {
        description: 'List of comma-separated keys occurring in table properties which will get inherited to newly created partitions. * implies all the keys will get inherited.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.metastore.end.function.listeners': {
        description: 'List of comma-separated listeners for the end of metastore functions.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.metastore.event.expiry.duration': {
        description: 'Duration after which events expire from events table (in seconds).',
        type: 'Numeric',
        default: '0'
      },
      'hive.metastore.event.clean.freq': {
        description: 'Frequency at which timer task runs to purge expired events in metastore(in seconds).',
        type: 'Numeric',
        default: '0'
      },
      'hive.metastore.connect.retries': {
        description: 'Number of retries while opening a connection to metastore.',
        type: 'Numeric',
        default: '3'
      },
      'hive.metastore.client.connect.retry.delay': {
        description: 'Number of seconds for the client to wait between consecutive connection attempts.',
        type: 'Numeric',
        default: '1'
      },
      'hive.metastore.client.socket.timeout': {
        description: 'MetaStore Client socket timeout in seconds.',
        type: 'Numeric',
        default: '20 in Hive 0.7 through 0.13.1; 600 in Hive 0.14.0 and later'
      },
      'hive.metastore.rawstore.impl': {
        description: 'Name of the class that implements org.apache.hadoop.hive.metastore.rawstore interface. This class is used to store and retrieval of raw metadata objects such as table, database.',
        type: 'String',
        default: 'org.apache.hadoop.hive.metastore.ObjectStore'
      },
      'hive.metastore.batch.retrieve.max': {
        description: 'Maximum number of objects (tables/partitions) can be retrieved from metastore in one batch. The higher the number, the less the number of round trips is needed to the Hive metastore server, but it may also cause higher memory requirement at the client side.',
        type: 'Numeric',
        default: '300'
      },
      'hive.metastore.ds.connection.url.hook': {
        description: 'Name of the hook to use for retriving the JDO connection URL. If empty, the value in javax.jdo.option.ConnectionURL is used.',
        type: 'String',
        default: '(empty)'
      },
      'hive.metastore.ds.retry.attempts': {
        description: 'The number of times to retry a metastore call if there were a connection error.',
        type: 'Numeric',
        default: '1'
      },
      'hive.metastore.ds.retry.interval': {
        description: 'The number of milliseconds between metastore retry attempts.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.metastore.server.min.threads': {
        description: 'Minimum number of worker threads in the Thrift server\'s pool.',
        type: 'Numeric',
        default: '200'
      },
      'hive.metastore.server.max.threads': {
        description: 'Maximum number of worker threads in the Thrift server\'s pool.',
        type: 'Numeric',
        default: 'Hive 0.x and 1.0.x: 100000, Hive 1.1.0 and later: 1000'
      },
      'hive.metastore.server.max.message.size': {
        description: 'Maximum message size in bytes a Hive metastore will accept.',
        type: 'Numeric',
        default: '100*1024*1024'
      },
      'hive.metastore.server.tcp.keepalive': {
        description: 'Whether to enable TCP keepalive for the metastore server. Keepalive will prevent accumulation of half-open connections.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.metastore.sasl.enabled': {
        description: 'If true, the metastore thrift interface will be secured with SASL. Clients must authenticate with Kerberos.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.metastore.kerberos.keytab.file': {
        description: 'The path to the Kerberos Keytab file containing the metastore thrift server\'s service principal.',
        type: 'String',
        default: '(empty)'
      },
      'hive.metastore.kerberos.principal': {
        description: 'The service principal for the metastore thrift server. The special string _HOST will be replaced automatically with the correct host name.',
        type: 'String',
        default: 'hive-metastore/_HOST@EXAMPLE.COM'
      },
      'hive.metastore.client.kerberos.principal': {
        description: 'The client-facing kerberos service principal for the Hive metastore. If unset, it defaults to the value set for hive.metatore.kerberos.principal, for backward compatibility.',
        type: 'String',
        default: '"" (Empty)'
      },
      'hive.metastore.cache.pinobjtypes': {
        description: 'List of comma-separated metastore object types that should be pinned in the cache.',
        type: 'String',
        default: 'Table,StorageDescriptor,SerDeInfo,Partition,Database,Type,FieldSchema,Order'
      },
      'hive.metastore.authorization.storage.checks': {
        description: 'Should the metastore do authorization checks against the underlying storage for operations like drop-partition (disallow the drop-partition if the user in question doesn\'t have permissions to delete the corresponding directory on the storage).',
        type: 'Boolean',
        default: 'false'
      },
      'hive.metastore.thrift.framed.transport.enabled': {
        description: 'If true, the metastore Thrift interface will use TFramedTransport. When false (default) a standard TTransport is used.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.metastore.schema.verification': {
        description: 'Enforce metastore schema version consistency.',
        type: 'String',
        default: 'false '
      },
      'hive.metastore.integral.jdo.pushdown': {
        description: 'Allow JDO query pushdown for integral partition columns in metastore. Off by default. This improves metastore performance for integral columns, especially if there\'s a large number of partitions. However, it doesn\'t work correctly with integral values that are not normalized (for example, if they have leading zeroes like 0012). If metastore direct SQL is enabled and works (hive.metastore.try.direct.sql), this optimization is also irrelevant.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.metastore.try.direct.sql': {
        description: 'Whether the Hive metastore should try to use direct SQL queries instead of the DataNucleus for certain read paths. This can improve metastore performance when fetching many partitions or column statistics by orders of magnitude; however, it is not guaranteed to work on all RDBMS-es and all versions. In case of SQL failures, the metastore will fall back to the DataNucleus, so it\'s safe even if SQL doesn\'t work for all queries on your datastore. If all SQL queries fail (for example, your metastore is backed by MongoDB), you might want to disable this to save the try-and-fall-back cost.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.metastore.try.direct.sql.ddl': {
        description: 'Same as hive.metastore.try.direct.sql, for read statements within a transaction that modifies metastore data. Due to non-standard behavior in Postgres, if a direct SQL select query has incorrect syntax or something similar inside a transaction, the entire transaction will fail and fall-back to DataNucleus will not be possible. You should disable the usage of direct SQL inside transactions if that happens in your case.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.metastore.orm.retrieveMapNullsAsEmptyStrings': {
        description: 'Thrift does not support nulls in maps, so any nulls present in maps retrieved from object-relational mapping (ORM) must be either pruned or converted to empty strings. Some backing databases such as Oracle persist empty strings as nulls, and therefore will need to have this parameter set to true in order to reverse that behavior. For others, the default pruning behavior is correct.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.direct.sql.max.query.length': {
        description: 'The maximum size of a query string (in KB) as generated by direct SQL.',
        type: 'Numeric',
        default: '100'
      },
      'hive.direct.sql.max.elements.in.clause': {
        description: 'The maximum number of values in an IN clause as generated by direct SQL. Once exceeded, it will be broken into multiple OR separated IN clauses.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.direct.sql.max.elements.values.clause': {
        description: 'The maximum number of values in a VALUES clause for an INSERT statement as generated by direct SQL.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.metastore.port': {
        description: 'Hive metastore listener port.',
        type: 'Numeric',
        default: '9083'
      },
      'hive.metastore.initial.metadata.count.enabled': {
        description: 'Enable a metadata count at metastore startup for metrics.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.metastore.limit.partition.request': {
        description: 'This limits the number of partitions that can be requested from the Metastore for a given table. A query will not be executed if it attempts to fetch more partitions per table than the limit configured. A value of "-1" means unlimited. This parameter is preferred over hive.limit.query.max.table.partition (deprecated).',
        type: 'Numeric',
        default: '-1'
      },
      'hive.metastore.fastpath': {
        description: 'Used to avoid all of the proxies and object copies in the metastore. Note, if this is set, you MUST use a local metastore (hive.metastore.uris must be empty) otherwise undefined and most likely undesired behavior will result.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.metastore.hbase.file.metadata.threads': {
        description: 'Number of threads to use to read file metadata in background to cache it.',
        type: 'Numeric',
        default: '1'
      },
      'hive.server\'2.thrift.port': {
        description: 'Port number of HiveServer2 Thrift interface. Can be overridden by setting $HIVE_SERVER2_THRIFT_PORT.',
        type: 'Numeric',
        default: '10000'
      },
      'hive.server2.thrift.bind.host': {
        description: 'Bind host on which to run the HiveServer2 Thrift interface. Can be overridden by setting $HIVE_SERVER2_THRIFT_BIND_HOST.',
        type: 'String',
        default: 'localhost'
      },
      'hive.server2.thrift.min.worker.threads': {
        description: 'Minimum number of Thrift worker threads.',
        type: 'Numeric',
        default: '5'
      },
      'hive.server2.thrift.max.worker.threads': {
        description: 'Maximum number of Thrift worker threads.',
        type: 'Numeric',
        default: '100 in Hive 0.11.0, 500 in Hive 0.12.0 and later'
      },
      'hive.server2.thrift.worker.keepalive.time': {
        description: 'Keepalive time (in seconds) for an idle worker thread. When number of workers > min workers, excess threads are killed after this time interval.',
        type: 'Numeric',
        default: '60'
      },
      'hive.server2.thrift.max.message.size': {
        description: 'Maximum message size in bytes a HiveServer2 server will accept.',
        type: 'Numeric',
        default: '100*1024*1024'
      },
      'hive.server2.authentication': {
        description: 'Client authentication types. NONE: no authentication check – plain SASL transport LDAP: LDAP/AD based authentication KERBEROS: Kerberos/GSSAPI authentication CUSTOM: Custom authentication provider (use with property hive.server2.custom.authentication.class) PAM: Pluggable authentication module',
        type: 'String',
        default: 'NONE'
      },
      'hive.server2.authentication.kerberos.keytab': {
        description: 'Kerberos keytab file for server principal.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.authentication.kerberos.principal': {
        description: 'Kerberos server principal.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.custom.authentication.class': {
        description: 'Custom authentication class. Used when property hive.server2.authentication is set to \'CUSTOM\'. Provided class must be a proper implementation of the interface org.apache.hive.service.auth.PasswdAuthenticationProvider. HiveServer2 will call its Authenticate(user, passed) method to authenticate requests. The implementation may optionally extend Hadoop\'s org.apache.hadoop.conf.Configured class to grab Hive\'s Configuration object.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.enable.doAs': {
        description: 'Setting this property to true will have HiveServer2 execute Hive operations as the user making the calls to it.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.server2.authentication.ldap.url': {
        description: 'LDAP connection URL(s), value could be a SPACE separated list of URLs to multiple LDAP servers for resiliency. URLs are tried in the order specified until the connection is successful.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.authentication.ldap.baseDN': {
        description: 'LDAP base DN (distinguished name).',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.authentication.ldap.guidKey': {
        description: 'This property is to indicate what prefix to use when building the bindDN for LDAP connection (when using just baseDN). So bindDN will be "<guidKey>=<user/group>,<baseDN>". If userDNPattern and/or groupDNPattern is used in the configuration, the guidKey is not needed. Primarily required when just baseDN is being used.',
        type: 'String',
        default: 'uid'
      },
      'hive.server2.authentication.ldap.Domain': {
        description: 'LDAP domain.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.authentication.ldap.groupDNPattern': {
        description: 'A COLON-separated list of string patterns to represent the base DNs for LDAP Groups. Use "%s" where the actual group name is to be plugged in. Example of one string pattern: uid=%s,OU=Groups,DC=apache,DC=org',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.server2.authentication.ldap.groupFilter': {
        description: 'A COMMA-separated list of group names that the users should belong to (at least one of the groups) for authentication to succeed. See Group Membership for details.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.server2.authentication.ldap.groupMembershipKey': {
        description: 'LDAP attribute name on the group object that contains the list of distinguished names for the user, group, and contact objects that are members of the group. For example: member, uniqueMember, or memberUid.',
        type: 'String',
        default: 'member'
      },
      'hive.server2.authentication.ldap.userMembershipKey': {
        description: 'LDAP attribute name on the user object that contains groups of which the user is a direct member, except for the primary group, which is represented by the primaryGroupId. For example: memberOf.',
        type: 'String',
        default: 'null'
      },
      'hive.server2.authentication.ldap.groupClassKey': {
        description: 'This property is used in LDAP search queries for finding LDAP group names a user belongs to. The value of this property is used to construct LDAP group search query and is used to indicate what a group\'s objectClass is. Every LDAP group has certain objectClass. For example: group, groupOfNames, groupOfUniqueNames etc.',
        type: 'String',
        default: 'groupOfNames'
      },
      'hive.server2.authentication.ldap.userDNPattern': {
        description: 'A COLON-separated list of string patterns to represent the base DNs for LDAP Users. Use "%s" where the actual username is to be plugged in. See User Search List for details. Example of one string pattern: uid=%s,OU=Users,DC=apache,DC=org',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.server2.authentication.ldap.userFilter': {
        description: 'A COMMA-separated list of usernames for whom authentication will succeed if the user is found in LDAP. See User Search List for details.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.server2.authentication.ldap.customLDAPQuery': {
        description: 'A user-specified custom LDAP query that will be used to grant/deny an authentication request. If the user is part of the query\'s result set, authentication succeeds. See Custom Query String for details.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.global.init.file.location': {
        description: 'Either the location of a HiveServer2 global init file or a directory containing a .hiverc file. If the property is set, the value must be a valid path to an init file or directory where the init file is located.',
        type: 'String',
        default: '$HIVE_CONF_DIR  (typically <hive_root>/conf)'
      },
      'hive.server2.thrift.http.port': {
        description: 'Port number when in HTTP mode.',
        type: 'Numeric',
        default: '10001'
      },
      'hive.server2.thrift.http.min.worker.threads': {
        description: 'Minimum number of worker threads when in HTTP mode.',
        type: 'Numeric',
        default: '5'
      },
      'hive.server2.thrift.http.max.worker.threads': {
        description: 'Maximum number of worker threads when in HTTP mode.',
        type: 'Numeric',
        default: '500'
      },
      'hive.server2.thrift.http.max.idle.time': {
        description: 'Maximum idle time for a connection on the server when in HTTP mode.',
        type: 'Numeric',
        default: '1800s (ie, 1800 seconds)'
      },
      'hive.server2.thrift.http.worker.keepalive.time': {
        description: 'Keepalive time (in seconds) for an idle http worker thread. When number of workers > min workers, excess threads are killed after this time interval.',
        type: 'Numeric',
        default: '60'
      },
      'hive.server2.thrift.sasl.qop': {
        description: 'Sasl QOP value; set it to one of the following values to enable higher levels of protection for HiveServer2 communication with clients. "auth" – authentication only (default), "auth-int" – authentication plus integrity protection or  "auth-conf" – authentication plus integrity and confidentiality protection',
        type: 'String',
        default: 'auth'
      },
      'hive.server2.async.exec.threads': {
        description: 'Number of threads in the async thread pool for HiveServer2.',
        type: 'Numeric',
        default: '50 in Hive 0.12.0, 100 in Hive 0.13.0 and later'
      },
      'hive.server2.async.exec.shutdown.timeout': {
        description: 'Time (in seconds) for which HiveServer2 shutdown will wait for async threads to terminate.',
        type: 'Numeric',
        default: '10'
      },
      'hive.server2.table.type.mapping': {
        description: 'This setting reflects how HiveServer2 will report the table types for JDBC and other client implementations that retrieve the available tables and supported table types. HIVE: Exposes Hive\'s native table types like MANAGED_TABLE, EXTERNAL_TABLE, VIRTUAL_VIEW CLASSIC: More generic types like TABLE and VIEW',
        type: 'String',
        default: 'CLASSIC'
      },
      'hive.server2.session.hook': {
        description: 'Session-level hook for HiveServer2.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.max.start.attempts': {
        description: 'The number of times HiveServer2 will attempt to start before exiting, sleeping 60 seconds between retries. The default of 30 will keep trying for 30 minutes.',
        type: 'Numeric',
        default: '30'
      },
      'hive.server2.async.exec.wait.queue.size': {
        description: 'Size of the wait queue for async thread pool in HiveServer2. After hitting this limit, the async thread pool will reject new requests.',
        type: 'Numeric',
        default: '100'
      },
      'hive.server2.async.exec.keepalive.time': {
        description: 'Time (in seconds) that an idle HiveServer2 async thread (from the thread pool) will wait for a new task to arrive before terminating.',
        type: 'Numeric',
        default: '10'
      },
      'hive.server2.long.polling.timeout': {
        description: 'Time in milliseconds that HiveServer2 will wait, before responding to asynchronous calls that use long polling.',
        type: 'Numeric',
        default: '5000L'
      },
      'hive.server2.allow.user.substitution': {
        description: 'Allow alternate user to be specified as part of HiveServer2 open connection request.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.server2.authentication.spnego.keytab': {
        description: 'Keytab file for SPNEGO principal, optional. A typical value would look like /etc/security/keytabs/spnego.service.keytab. This keytab would be used by HiveServer2 when Kerberos security is enabled and HTTP transport mode is used. This needs to be set only if SPNEGO is to be used in authentication. SPNEGO authentication would be honored only if valid hive.server2.authentication.spnego.principal and hive.server2.authentication.spnego.keytab are specified.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.authentication.spnego.principal': {
        description: 'SPNEGO service principal, optional. A typical value would look like HTTP/_HOST@EXAMPLE.COM. The SPNEGO service principal would be used by HiveServer2 when Kerberos security is enabled and HTTP transport mode is used. This needs to be set only if SPNEGO is to be used in authentication.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.authentication.pam.services': {
        description: 'List of the underlying PAM services that should be used when hive.server2.authentication type is PAM. A file with the same name must exist in /etc/pam.d.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.server2.use.SSL': {
        description: 'Set this to true for using SSL encryption in HiveServer2.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.server2.keystore.path': {
        description: 'SSL certificate keystore location.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.keystore.password': {
        description: 'SSL certificate keystore password.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.tez.default.queues': {
        description: 'A list of comma separated values corresponding to YARN queues of the same name. When HiveServer2 is launched in Tez mode, this configuration needs to be set for multiple Tez sessions to run in parallel on the cluster.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.server2.tez.sessions.per.default.queue': {
        description: 'A positive integer that determines the number of Tez sessions that should be launched on each of the queues specified by hive.server2.tez.default.queues. Determines the parallelism on each queue.',
        type: 'Numeric',
        default: '1'
      },
      'hive.server2.tez.initialize.default.sessions': {
        description: 'This flag is used in HiveServer 2 to enable a user to use HiveServer 2 without turning on Tez for HiveServer 2. The user could potentially want to run queries over Tez without the pool of sessions.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.server2.session.check.interval': {
        description: 'The check interval for session/operation timeout, which can be disabled by setting to zero or negative value.',
        type: 'Numeric',
        default: 'Hive 0.x, 1.0.x, 1.1.x, 1.2.0: 0ms, Hive 1.2.1+, 1.3+, 2.x+: 6h'
      },
      'hive.server2.idle.session.timeout': {
        description: 'With hive.server2.session.check.interval set to a positive time value, session will be closed when it\'s not accessed for this duration of time, which can be disabled by setting to zero or negative value.',
        type: 'Numeric',
        default: 'Hive 0.x, 1.0.x, 1.1.x, 1.2.0: 0ms, Hive 1.2.1+, 1.3+, 2.x+: 7d'
      },
      'hive.server2.idle.operation.timeout': {
        description: 'With hive.server2.session.check.interval set to a positive time value, operation will be closed when it\'s not accessed for this duration of time, which can be disabled by setting to zero value. With positive value, it\'s checked for operations in terminal state only (FINISHED, CANCELED, CLOSED, ERROR). With negative value, it\'s checked for all of the operations regardless of state.',
        type: 'Numeric',
        default: '0ms'
      },
      'hive.server2.logging.operation.enabled': {
        description: 'When true, HiveServer2 will save operation logs and make them available for clients.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.server2.logging.operation.log.location': {
        description: 'Top level directory where operation logs are stored if logging functionality is enabled.',
        type: 'String',
        default: '${java.io.tmpdir}/${user.name}/operation_logs'
      },
      'hive.server2.logging.operation.level': {
        description: 'HiveServer2 operation logging mode available to clients to be set at session level. For this to work, hive.server2.logging.operation.enabled should be set to true. The allowed values are: NONE: Ignore any logging. EXECUTION: Log completion of tasks. PERFORMANCE: Execution + Performance logs. VERBOSE: All logs.',
        type: 'String',
        default: 'EXECUTION'
      },
      'hive.server2.thrift.http.cookie.auth.enabled': {
        description: 'When true, HiveServer2 in HTTP transport mode will use cookie based authentication mechanism.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.server2.thrift.http.cookie.max.age': {
        description: 'Maximum age in seconds for server side cookie used by HiveServer2 in HTTP mode.',
        type: 'Numeric',
        default: '86400s (1 day)'
      },
      'hive.server2.thrift.http.cookie.path': {
        description: 'Path for the HiveServer2 generated cookies.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.thrift.http.cookie.domain': {
        description: 'Domain for the HiveServer2 generated cookies.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.thrift.http.cookie.is.secure': {
        description: 'Secure attribute of the HiveServer2 generated cookie.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.server2.thrift.http.cookie.is.httponly': {
        description: 'HttpOnly attribute of the HiveServer2 generated cookie.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.server2.close.session.on.disconnect': {
        description: 'Session will be closed when connection is closed. Set this to false to have session outlive its parent connection.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.server2.xsrf.filter.enabled': {
        description: 'If enabled, HiveServer2 will block any requests made to it over HTTP if an X-XSRF-HEADER header is not present.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.server2.job.credential.provider.path': {
        description: 'This configuration property enables the user to provide a comma-separated list of URLs which provide the type and location of Hadoop credential providers. These credential providers are used by HiveServer2 for providing job-specific credentials launched using MR or Spark execution engines. This functionality has not been tested against Tez.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.server2.in.place.progress': {
        description: 'Allows HiveServer2 to send progress bar update information. This is currently available only if the execution engine is tez.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.hadoop.classpath': {
        description: 'For the Windows operating system, Hive needs to pass the HIVE_HADOOP_CLASSPATH Java parameter while starting HiveServer2 using "-hiveconf hive.hadoop.classpath=%HIVE_LIB%". Users can set this parameter in hiveserver2.xml. HiveServer2 Web UI A web interface for HiveServer2 is introduced in release 2.0.0 (see Web UI for HiveServer2).',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.webui.host': {
        description: 'The host address the HiveServer2 Web UI will listen on. The Web UI can be used to access the HiveServer2 configuration, local logs, and metrics. It can also be used to check some information about active sessions and queries being executed.',
        type: 'String',
        default: '0.0.0.0'
      },
      'hive.server2.webui.port': {
        description: 'The port the HiveServer2 Web UI will listen on. Set to 0 or a negative number to disable the HiveServer2 Web UI feature.',
        type: 'Numeric',
        default: '10002'
      },
      'hive.server2.webui.max.threads': {
        description: 'The maximum number of HiveServer2 Web UI threads.',
        type: 'Numeric',
        default: '50'
      },
      'hive.server2.webui.max.historic.queries': {
        description: 'The maximum number of past queries to show in HiveServer2 Web UI.',
        type: 'Numeric',
        default: '25'
      },
      'hive.server2.webui.use.ssl': {
        description: 'Set this to true for using SSL encryption for HiveServer2 WebUI.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.server2.webui.keystore.path': {
        description: 'SSL certificate keystore location for HiveServer2 WebUI.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.webui.keystore.password': {
        description: 'SSL certificate keystore password for HiveServer2 WebUI.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.webui.use.spenego': {
        description: 'SSL certificate keystore password for HiveServer2 WebUI.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.server2.webui.spnego.keytab': {
        description: 'The path to the Kerberos Keytab file containing the HiveServer2 WebUI SPNEGO service principal.',
        type: 'String',
        default: '(empty)'
      },
      'hive.server2.webui.spnego.principal': {
        description: 'The HiveServer2 WebUI SPNEGO service principal. The special string _HOST will be replaced automatically with the value of hive.server2.webui.host or the correct host name.',
        type: 'String',
        default: 'HTTP/_HOST@EXAMPLE.COM'
      },
      'hive.spark.job.monitor.timeout': {
        description: 'Timeout for job monitor to get Spark job state.',
        type: 'Numeric',
        default: '60 seconds'
      },
      'hive.spark.dynamic.partition.pruning': {
        description: 'When true, this turns on dynamic partition pruning for the Spark engine, so that joins on partition keys will be processed by writing to a temporary HDFS file, and read later for removing unnecessary partitions.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.spark.dynamic.partition.pruning.max.data.size': {
        description: 'The maximum data size for the dimension table that generates partition pruning information. If reaches this limit, the optimization will be turned off.',
        type: 'Numeric',
        default: '100MB'
      },
      'hive.spark.exec.inplace.progress': {
        description: 'Updates Spark job execution progress in-place in the terminal.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.spark.use.ts.stats.for.mapjoin': {
        description: 'If this is set to true, mapjoin optimization in Hive/Spark will use statistics from TableScan operators at the root of the operator tree, instead of parent ReduceSink operators of the Join operator.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.spark.explain.user': {
        description: 'Whether to show explain result at user level for Hive-on-Spark queries. When enabled, will log EXPLAIN output for the query at user level.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.prewarm.spark.timeout': {
        description: 'Time to wait to finish prewarming Spark executors when hive.prewarm.enabled is true. ',
        type: 'Numeric',
        default: '5000ms'
      },
      'hive.spark.client.future.timeout': {
        description: 'Timeout for requests from Hive client to remote Spark driver.',
        type: 'Numeric',
        default: '60 seconds'
      },
      'hive.spark.client.connect.timeout': {
        description: 'Timeout for remote Spark driver in connecting back to Hive client.',
        type: 'Numeric',
        default: '1000 miliseconds'
      },
      'hive.spark.client.server.connect.timeout': {
        description: 'Timeout for handshake between Hive client and remote Spark driver. Checked by both processes.',
        type: 'Numeric',
        default: '90000 miliseconds'
      },
      'hive.spark.client.secret.bits': {
        description: 'Number of bits of randomness in the generated secret for communication between Hive client and remote Spark driver. Rounded down to nearest multiple of 8.',
        type: 'Numeric',
        default: '256'
      },
      'hive.spark.client.rpc.server.address': {
        description: 'The server address of HiverServer2 host to be used for communication between Hive client and remote Spark driver.',
        type: 'String',
        default: 'hive.spark.client.rpc.server.address, localhost if unavailable.'
      },
      'hive.spark.client.rpc.threads': {
        description: 'Maximum number of threads for remote Spark driver\'s RPC event loop.',
        type: 'Numeric',
        default: '8'
      },
      'hive.spark.client.rpc.max.size': {
        description: 'Maximum message size in bytes for communication between Hive client and remote Spark driver. Default is 50 MB.',
        type: 'Numeric',
        default: '52,428,800 (50 * 1024 * 1024, or 50 MB)'
      },
      'hive.spark.client.channel.log.level': {
        description: 'Channel logging level for remote Spark driver. One of DEBUG, ERROR, INFO, TRACE, WARN. If unset, TRACE is chosen.',
        type: 'String',
        default: '(empty)'
      },
      'hive.jar.directory': {
        description: 'This is the location that Hive in Tez mode will look for to find a site-wide installed Hive instance.  See hive.user.install.directory for the default behavior.',
        type: 'String',
        default: 'null'
      },
      'hive.user.install.directory': {
        description: 'If Hive (in Tez mode only) cannot find a usable Hive jar in hive.jar.directory, it will upload the Hive jar to <hive.user.install.directory>/<user_name> and use it to run queries.',
        type: 'String',
        default: 'hdfs:///user/'
      },
      'hive.compute.splits.in.am': {
        description: 'Whether to generate the splits locally or in the ApplicationMaster (Tez only).',
        type: 'Boolean',
        default: 'true'
      },
      'hive.rpc.query.plan': {
        description: 'Whether to send the query plan via local resource or RPC.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.prewarm.enabled': {
        description: 'Enables container prewarm for Tez (0.13.0 to 1.2.x) or Tez/Spark (1.3.0+). This is for Hadoop 2 only.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.prewarm.numcontainers': {
        description: 'Controls the number of containers to prewarm for Tez (0.13.0 to 1.2.x) or Tez/Spark (1.3.0+). This is for Hadoop 2 only.',
        type: 'Numeric',
        default: '10'
      },
      'hive.merge.tezfiles': {
        description: 'Merge small files at the end of a Tez DAG.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.tez.input.format': {
        description: 'The default input format for Tez. Tez groups splits in the AM (ApplicationMaster).',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.io.HiveInputFormat'
      },
      'hive.tez.input.generate.consistent.splits': {
        description: 'Whether to generate consistent split locations when generating splits in the AM. Setting to false randomizes the location and order of splits depending on how threads generate. Relates to LLAP.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.tez.container.size': {
        description: 'By default Tez will spawn containers of the size of a mapper. This can be used to overwrite the default.',
        type: 'Numeric',
        default: '-1'
      },
      'hive.tez.java.opts': {
        description: 'By default Tez will use the Java options from map tasks. This can be used to overwrite the default.',
        type: 'String',
        default: '(empty)'
      },
      'hive.convert.join.bucket.mapjoin.tez': {
        description: 'Whether joins can be automatically converted to bucket map joins in Hive when Tez is used as the execution engine (hive.execution.engine is set to "tez").',
        type: 'Boolean',
        default: 'false'
      },
      'hive.tez.log.level': {
        description: 'The log level to use for tasks executing as part of the DAG. Used only if hive.tez.java.opts is used to configure Java options.',
        type: 'String',
        default: 'INFO'
      },
      'hive.localize.resource.wait.interval': {
        description: 'Time in milliseconds to wait for another thread to localize the same resource for Hive-Tez.',
        type: 'Numeric',
        default: '5000'
      },
      'hive.localize.resource.num.wait.attempts': {
        description: 'The number of attempts waiting for localizing a resource in Hive-Tez.',
        type: 'Numeric',
        default: '5'
      },
      'hive.tez.smb.number.waves': {
        description: 'The number of waves in which to run the SMB (sort-merge-bucket) join. Account for cluster being occupied. Ideally should be 1 wave.',
        type: 'Numeric',
        default: '0.5'
      },
      'hive.tez.cpu.vcores': {
        description: 'By default Tez will ask for however many CPUs MapReduce is configured to use per container. This can be used to overwrite the default.',
        type: 'Numeric',
        default: '-1'
      },
      'hive.tez.auto.reducer.parallelism': {
        description: 'Turn on Tez\' auto reducer parallelism feature. When enabled, Hive will still estimate data sizes and set parallelism estimates. Tez will sample source vertices\' output sizes and adjust the estimates at runtime as necessary.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.tez.max.partition.factor': {
        description: 'When auto reducer parallelism is enabled this factor will be used to over-partition data in shuffle edges.',
        type: 'Numeric',
        default: '2'
      },
      'hive.tez.min.partition.factor': {
        description: 'When auto reducer parallelism is enabled this factor will be used to put a lower limit to the number of reducers that Tez specifies.',
        type: 'Numeric',
        default: '0.25'
      },
      'hive.tez.exec.print.summary': {
        description: 'If true, displays breakdown of execution steps for every query executed on Hive CLI or Beeline client.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.tez.exec.inplace.progress': {
        description: 'Updates Tez job execution progress in-place in the terminal when Hive CLI is used.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.execution.mode': {
        description: 'Possible Values: auto, none, all, map; also only (as of 2.2.0 with HIVE-15135) Chooses whether query fragments will run in a container or in LLAP. When set to "all" everything runs in LLAP if possible; "only" is like "all" but disables fallback to containers, so that the query fails if it cannot run in LLAP.',
        type: 'String',
        default: 'none'
      },
      'hive.server2.llap.concurrent.queries': {
        description: 'The number of queries allowed in parallel via llap. Negative number implies \'infinite\'.',
        type: 'Numeric',
        default: '-1'
      },
      'hive.llap.client.consistent.splits': {
        description: 'Whether to setup split locations to match nodes on which LLAP daemons are running, instead of using the locations provided by the split itself.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.llap.daemon.web.port': {
        description: 'LLAP daemon web UI port.',
        type: 'Numeric',
        default: '15002'
      },
      'hive.llap.daemon.web.ssl': {
        description: 'Whether LLAP daemon web UI should use SSL',
        type: 'Boolean',
        default: 'false'
      },
      'hive.llap.auto.auth': {
        description: 'Whether or not to set Hadoop configs to enable auth in LLAP web app.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.daemon.service.principal': {
        description: 'The name of the LLAP daemon\'s service principal.',
        type: 'String',
        default: '(empty)'
      },
      'hive.llap.daemon.service.hosts': {
        description: 'Explicitly specified hosts to use for LLAP scheduling. Useful for testing. By default, YARN registry is used.',
        type: 'String',
        default: 'null'
      },
      'hive.llap.daemon.task.preemption.metrics.intervals': {
        description: 'Comma-delimited set of integers denoting the desired rollover intervals (in seconds) for percentile latency metrics.',
        type: 'Integers',
        default:  '30,60,300'
      },
      'hive.llap.object.cache.enabled': {
        description: 'Cache objects (plans, hashtables, etc) in LLAP',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.io.use.lrfu': {
        description: 'Whether ORC low-level cache should use Least Frequently / Frequently Used (LRFU) cache policy instead of default First-In-First-Out (FIFO).',
        type: 'Boolean',
        default: 'false'
      },
      'hive.llap.io.lrfu.lambda': {
        description: 'Possible Values: Between 0 and 1 Lambda for ORC low-level cache LRFU cache policy. Must be in [0, 1]. 0 makes LRFU behave like LFU, 1 makes it behave like LRU, values in between balance accordingly.',
        type: 'Numeric',
        default: '0.01f'
      },
      'hive.llap.io.enabled': {
        description: 'Whether the LLAP I/O layer is enabled.  Remove property or set to false to disable LLAP I/O.',
        type: 'String',
        default: 'null'
      },
      'hive.llap.io.cache.orc.size': {
        description: 'Maximum size for IO allocator or ORC low-level cache.',
        type: 'Numeric',
        default: '1Gb'
      },
      'hive.llap.io.threadpool.size': {
        description: 'Specify the number of threads to use for low-level IO thread pool.',
        type: 'Numeric',
        default: '10'
      },
      'hive.llap.io.orc.time.counters': {
        description: 'Whether to enable time counters for LLAP IO layer (time spent in HDFS, etc.)',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.io.memory.mode': {
        description: 'Possible Values: cache, allocator, none \'cache\' (the default) uses data and metadata cache with a custom off-heap allocator, \'allocator\' uses the custom allocator without the caches, \'none\' doesn\'t use either (this mode may result in significant performance degradation)',
        type: 'String',
        default: 'cache'
      },
      'hive.llap.io.allocator.alloc.min': {
        description: 'Minimum allocation possible from LLAP buddy allocator. Allocations below that are padded to minimum allocation. For ORC, should generally be the same as the expected compression buffer size, or next lowest power of 2. Must be a power of 2.',
        type: 'Numeric',
        default: '128Kb'
      },
      'hive.llap.io.allocator.alloc.max': {
        description: 'Maximum allocation possible from LLAP buddy allocator. For ORC, should be as large as the largest expected ORC compression buffer size. Must be a power of 2.',
        type: 'Numeric',
        default: '16Mb'
      },
      'hive.llap.io.allocator.arena.count': {
        description: 'Arena count for LLAP low-level cache; cache will be allocated in the steps of (size/arena_count) bytes. This size must be <= 1Gb and >= max allocation; if it is not the case, an adjusted size will be used. Using powers of 2 is recommended.',
        type: 'Numeric',
        default: '8'
      },
      'hive.llap.io.memory.size': {
        description: 'Maximum size for IO allocator or ORC low-level cache.',
        type: 'Numeric',
        default: '1Gb'
      },
      'hive.llap.io.allocator.direct': {
        description: 'Whether ORC low-level cache should use direct allocation.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.io.allocator.nmap': {
        description: 'Whether ORC low-level cache should use memory mapped allocation (direct I/O)',
        type: 'Boolean',
        default: 'false'
      },
      'hive.llap.io.allocator.nmap.path': {
        description: 'The directory location for mapping NVDIMM/NVMe flash storage into the ORC low-level cache.',
        type: 'String',
        default: '/tmp'
      },
      'hive.llap.auto.allow.uber': {
        description: 'Whether or not to allow the planner to run vertices in the AM.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.auto.enforce.tree': {
        description: 'Enforce that all parents are in llap, before considering vertex',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.auto.enforce.vectorized': {
        description: 'Enforce that inputs are vectorized, before considering vertex',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.auto.enforce.stats': {
        description: 'Enforce that column stats are available, before considering vertex.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.auto.max.input.size': {
        description: 'Check input size, before considering vertex (-1 disables check)',
        type: 'Numeric',
        default: '10*1024*1024*1024L'
      },
      'hive.llap.auto.max.output.size': {
        description: 'Check output size, before considering vertex (-1 disables check)',
        type: 'Numeric',
        default: '1*1024*1024*1024L'
      },
      'hive.llap.queue.metrics.percentiles.intervals': {
        description: 'Comma-delimited set of integers denoting the desired rollover intervals (in seconds) for percentile latency metrics on the LLAP daemon producer-consumer queue. By default, percentile latency metrics are disabled.',
        type: 'String',
        default: 'blank'
      },
      'hive.llap.management.rpc.port': {
        description: 'RPC port for LLAP daemon management service.',
        type: 'Numeric',
        default: '15004'
      },
      'hive.llap.allow.permanent.fns': {
        description: 'Whether LLAP decider should allow permanent UDFs.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.llap.daemon.download.permanent.fns': {
        description: 'Whether LLAP daemon should localize the resources for permanent UDFs.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.llap.daemon.keytab.file': {
        description: 'The path to the Kerberos Keytab file containing the LLAP daemon\'s service principal.',
        type: 'String',
        default: '(empty)'
      },
      'hive.llap.zk.sm.principal': {
        description: 'The name of the principal to use to talk to ZooKeeper for ZooKeeper SecretManager.',
        type: 'String',
        default: '(empty)'
      },
      'hive.llap.zk.sm.keytab.file': {
        description: 'The path to the Kerberos Keytab file containing the principal to use to talk to ZooKeeper for ZooKeeper SecretManager.',
        type: 'String',
        default: '(empty)'
      },
      'hive.llap.zk.sm.connectionString': {
        description: 'ZooKeeper connection string for ZooKeeper SecretManager.',
        type: 'String',
        default: '(empty)'
      },
      'hive.llap.daemon.acl': {
        description: 'The ACL for LLAP daemon.',
        type: 'String',
        default: '*'
      },
      'hive.llap.management.acl': {
        description: 'The ACL for LLAP daemon management.',
        type: 'String',
        default: '*'
      },
      'hive.llap.daemon.delegation.token.lifetime': {
        description: 'LLAP delegation token lifetime, in seconds if specified without a unit.',
        type: 'Numeric',
        default: '14d'
      },
      'hive.txn.manager': {
        description: 'Hive Transactions Value: org.apache.hadoop.hive.ql.lockmgr.DbTxnManager Set this to org.apache.hadoop.hive.ql.lockmgr.DbTxnManager as part of turning on Hive transactions. The default DummyTxnManager replicates pre-Hive-0.13 behavior and provides no transactions. Turning on Hive transactions also requires appropriate settings for hive.compactor.initiator.on, hive.compactor.worker.threads, hive.support.concurrency, hive.enforce.bucketing (Hive 0.x and 1.x only), and hive.exec.dynamic.partition.mode.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.lockmgr.DummyTxnManager'
      },
      'hive.txn.strict.locking.mode': {
        description: 'In strict mode non-ACID resources use standard R/W lock semantics, e.g. INSERT will acquire exclusive lock. In non-strict mode, for non-ACID resources, INSERT will only acquire shared lock, which allows two concurrent writes to the same partition but still lets lock manager prevent DROP TABLE etc. when the table is being written to.  Only apples when hive.txn.manager=org.apache.hadoop.hive.ql.lockmgr.DbTxnManager.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.txn.timeout': {
        description: 'Time after which transactions are declared aborted if the client has not sent a heartbeat, in seconds.',
        type: 'Numeric',
        default: '300'
      },
      'hive.txn.heartbeat.threadpool.size': {
        description: 'The number of threads to use for heartbeating. For the Hive CLI one thread is enough, but HiveServer2 needs a few threads.',
        type: 'Numeric',
        default: '5'
      },
      'hive.timedout.txn.reaper.start': {
        description: 'Time delay of first reaper (the process which aborts timed-out transactions) run after the metastore start.',
        type: 'Numeric',
        default: '100s'
      },
      'hive.timedout.txn.reaper.interval': {
        description: 'Time interval describing how often the reaper (the process which aborts timed-out transactions) runs.',
        type: 'Numeric',
        default: '180s'
      },
      'hive.writeset.reaper.interval': {
        description: 'Frequency of WriteSet reaper runs.',
        type: 'Numeric',
        default: '60s'
      },
      'hive.txn.max.open.batch': {
        description: 'Maximum number of transactions that can be fetched in one call to open_txns(). This controls how many transactions streaming agents such as Flume or Storm open simultaneously. The streaming agent then writes that number of entries into a single file (per Flume agent or Storm bolt). Thus increasing this value decreases the number of delta files created by streaming agents. But it also increases the number of open transactions that Hive has to track at any given time, which may negatively affect read performance.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.max.open.txns': {
        description: 'Maximum number of open transactions. If current open transactions reach this limit, future open transaction requests will be rejected, until the number goes below the limit.',
        type: 'Numeric',
        default: '100000'
      },
      'hive.count.open.txns.interval': {
        description: 'Time in seconds between checks to count open transactions.',
        type: 'Numeric',
        default: '1s'
      },
      'hive.txn.retryable.sqlex.regex': {
        description: 'Comma separated list of regular expression patterns for SQL state, error code, and error message of retryable SQLExceptions, that\'s suitable for the Hive metastore database. For example: Can\'t serialize.*,40001$,^Deadlock,.*ORA-08176.*',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.compactor.initiator.on': {
        description: 'Hive Transactions Value: true (for exactly one instance of the Thrift metastore service) Whether to run the initiator and cleaner threads on this metastore instance. Set this to true on one instance of the Thrift metastore service as part of turning on Hive transactions. For a complete list of parameters required for turning on transactions, see hive.txn.manager.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.compactor.worker.threads': {
        description: 'Hive Transactions Value: greater than 0 on at least one instance of the Thrift metastore service. How many compactor worker threads to run on this metastore instance. Set this to a positive number on one or more instances of the Thrift metastore service as part of turning on Hive transactions. For a complete list of parameters required for turning on transactions, see hive.txn.manager.',
        type: 'Numeric',
        default: '0'
      },
      'hive.compactor.worker.timeout': {
        description: 'Time in seconds after which a compaction job will be declared failed and the compaction re-queued.',
        type: 'Numeric',
        default: '86400'
      },
      'hive.compactor.check.interval': {
        description: 'Time in seconds between checks to see if any tables or partitions need to be compacted. This should be kept high because each check for compaction requires many calls against the NameNode.',
        type: 'Numeric',
        default: '300'
      },
      'hive.compactor.cleaner.run.interval': {
        description: 'Time in milliseconds between runs of the cleaner thread.  Increasing this value will lengthen the time it takes to clean up old, no longer used versions of data and lower the load on the metastore server.  Decreasing this value will shorten the time it takes to clean up old, no longer used versions of the data and increase the load on the metastore server.',
        type: 'Numeric',
        default: '5000'
      },
      'hive.compactor.delta.num.threshold': {
        description: 'Number of delta directories in a table or partition that will trigger a minor compaction.',
        type: 'Numeric',
        default: '10'
      },
      'hive.compactor.delta.pct.threshold': {
        description: 'Percentage (fractional) size of the delta files relative to the base that will trigger a major compaction. (1.0 = 100%, so the default 0.1 = 10%.)',
        type: 'Numeric',
        default: '0.1'
      },
      'hive.compactor.abortedtxn.threshold': {
        description: 'Number of aborted transactions involving a given table or partition that will trigger a major compaction.',
        type: 'Numeric',
        default: '1000'
      },
      'hive.compactor.history.retention.succeeded': {
        description: 'Number of successful compaction entries to retain in history (per partition).',
        type: 'Numeric',
        default: '3'
      },
      'hive.compactor.history.retention.failed': {
        description: 'Number of failed compaction entries to retain in history (per partition).',
        type: 'Numeric',
        default: '3'
      },
      'hive.compactor.history.retention.attempted': {
        description: 'Number of attempted compaction entries to retain in history (per partition).',
        type: 'Numeric',
        default: '2'
      },
      'hive.compactor.history.reaper.interval': {
        description: 'Controls how often the process to purge historical record of compactions runs.',
        type: 'Numeric',
        default: '2m'
      },
      'hive.compactor.initiator.failed.compacts.threshold': {
        description: 'Number of consecutive failed compactions for a given partition after which the Initiator will stop attempting to schedule compactions automatically. It is still possible to use ALTER TABLE to initiate compaction. Once a manually-initiated compaction succeeds, auto-initiated compactions will resume. Note that this must be less than hive.compactor.history.retention.failed.',
        type: 'Numeric',
        default: '2'
      },
      'hive.index.compact.file.ignore.hdfs': {
        description: 'When true the HDFS location stored in the index file will be ignored at runtime. If the data got moved or the name of the cluster got changed, the index data should still be usable.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.index.filter.compact.minsize': {
        description: 'Minimum size (in bytes) of the inputs on which a compact index is automatically used.',
        type: 'Numeric',
        default: '5368709120'
      },
      'hive.optimize.index.filter.compact.maxsize': {
        description: 'Maximum size (in bytes) of the inputs on which a compact index is automatically used. A negative number is equivalent to infinity.',
        type: 'Numeric',
        default: '-1'
      },
      'hive.index.compact.query.max.size': {
        description: 'The maximum number of bytes that a query using the compact index can read. Negative value is equivalent to infinity.',
        type: 'Numeric',
        default: '10737418240'
      },
      'hive.index.compact.query.max.entries': {
        description: 'The maximum number of index entries to read during a query that uses the compact index. Negative value is equivalent to infinity.',
        type: 'Numeric',
        default: '10000000'
      },
      'hive.exec.concatenate.check.index': {
        description: 'If this sets to true, Hive will throw error when doing ALTER TABLE tbl_name [partSpec] CONCATENATE on a table/partition that has indexes on it. The reason the user want to set this to true is because it can help user to avoid handling all index drop, recreation, rebuild work. This is very helpful for tables with thousands of partitions.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.optimize.index.autoupdate': {
        description: 'Whether or not to enable automatic rebuilding of indexes when they go stale.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.optimize.index.groupby': {
        description: '',
        type: 'Boolean',
        default: 'false'
      },
      'hive.index.compact.binary.search': {
        description: 'Whether or not to use a binary search to find the entries in an index table that match the filter, where possible.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.stats.dbclass': {
        description: 'New Values: counter and custom Hive 0.7 to 0.12:  The default database that stores temporary Hive statistics.  Options are jdbc:derby, jdbc:mysql, and hbase as defined in StatsSetupConst.java. Hive 0.13 and later:  The storage that stores temporary Hive statistics. In filesystem based statistics collection ("fs"), each task writes statistics it has collected in a file on the filesystem, which will be aggregated after the job has finished. Supported values are fs (filesystem), jdbc:<database> (where <database> can be derby, mysql, etc.), hbase, counter, and custom as defined in StatsSetupConst.java.',
        type: 'String',
        default: 'jdbc:derby (Hive 0.7 to 0.12) or fs (Hive 0.13 and later)'
      },
      'hive.stats.autogather': {
        description: 'A flag to gather statistics automatically during the INSERT OVERWRITE command.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.stats.jdbcdriver': {
        description: 'The JDBC driver for the database that stores temporary Hive statistics.',
        type: 'String',
        default: 'org.apache.derby.jdbc.EmbeddedDriver'
      },
      'hive.stats.dbconnectionstring': {
        description: 'The default connection string for the database that stores temporary Hive statistics.',
        type: 'String',
        default: 'jdbc:derby:;databaseName=TempStatsStore;create=true'
      },
      'hive.stats.default.publisher': {
        description: 'The Java class (implementing the StatsPublisher interface) that is used by default if hive.stats.dbclass is not JDBC or HBase (Hive 0.12.0 and earlier), or if hive.stats.dbclass is a custom type (Hive 0.13.0 and later:  HIVE-4632).',
        type: 'String',
        default: '(empty)'
      },
      'hive.stats.default.aggregator': {
        description: 'The Java class (implementing the StatsAggregator interface) that is used by default if hive.stats.dbclass is not JDBC or HBase (Hive 0.12.0 and earlier), or if hive.stats.dbclass is a custom type (Hive 0.13.0 and later:  HIVE-4632).',
        type: 'String',
        default: '(empty)'
      },
      'hive.stats.jdbc.timeout': {
        description: 'Timeout value (number of seconds) used by JDBC connection and statements.',
        type: 'Numeric',
        default: '30'
      },
      'hive.stats.atomic': {
        description: 'If this is set to true then the metastore statistics will be updated only if all types of statistics (number of rows, number of files, number of bytes, etc.) are available. Otherwise metastore statistics are updated in a best effort fashion with whatever are available.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.stats.retries.max': {
        description: 'Maximum number of retries when stats publisher/aggregator got an exception updating intermediate database. Default is no tries on failures.',
        type: 'Numeric',
        default: '0'
      },
      'hive.stats.retries.wait': {
        description: 'The base waiting window (in milliseconds) before the next retry. The actual wait time is calculated by baseWindow * failures + baseWindow * (failure + 1) * (random number between 0.0,1.0).',
        type: 'Numeric',
        default: '3000'
      },
      'hive.stats.collect.rawdatasize': {
        description: 'If true, the raw data size is collected when analyzing tables.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.client.stats.publishers': {
        description: 'Comma-separated list of statistics publishers to be invoked on counters on each job. A client stats publisher is specified as the name of a Java class which implements the org.apache.hadoop.hive.ql.stats.ClientStatsPublisher interface.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.client.stats.counters': {
        description: 'Subset of counters that should be of interest for hive.client.stats.publishers (when one wants to limit their publishing). Non-display names should be used.',
        type: 'String',
        default: '(empty)'
      },
      'hive.stats.reliable': {
        description: 'Whether queries will fail because statistics cannot be collected completely accurately. If this is set to true, reading/writing from/into a partition or unpartitioned table may fail because the statistics could not be computed accurately. If it is set to false, the operation will succeed. In Hive 0.13.0 and later, if hive.stats.reliable is false and statistics could not be computed correctly, the operation can still succeed and update the statistics but it sets a partition property "areStatsAccurate" to false. If the application needs accurate statistics, they can then be obtained in the background.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.stats.ndv.error': {
        description: 'Standard error allowed for NDV estimates, expressed in percentage. This provides a tradeoff between accuracy and compute cost. A lower value for the error indicates higher accuracy and a higher compute cost. (NDV means number of distinct values.)',
        type: 'Numeric',
        default: '20.0'
      },
      'hive.stats.collect.tablekeys': {
        description: 'Whether join and group by keys on tables are derived and maintained in the QueryPlan. This is useful to identify how tables are accessed and to determine if they should be bucketed.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.stats.collect.scancols': {
        description: 'Whether column accesses are tracked in the QueryPlan. This is useful to identify how tables are accessed and to determine if there are wasted columns that can be trimmed.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.stats.key.prefix.max.length': {
        description: 'Determines if, when the prefix of the key used for intermediate statistics collection exceeds a certain length, a hash of the key is used instead. If the value < 0 then hashing is never used, if the value >= 0 then hashing is used only when the key prefixes\' length exceeds that value. The key prefix is defined as everything preceding the task ID in the key. For counter type statistics, it\'s maxed by mapreduce.job.counters.group.name.max, which is by default 128.',
        type: 'Numeric',
        default: '200 (Hive 0.11 and 0.12) or 150 (Hive 0.13 and later)'
      },
      'hive.stats.key.prefix.reserve.length': {
        description: 'Reserved length for postfix of statistics key. Currently only meaningful for counter type statistics which should keep the length of the full statistics key smaller than the maximum length configured by hive.stats.key.prefix.max.length. For counter type statistics, it should be bigger than the length of LB spec if exists.',
        type: 'Numeric',
        default: '24'
      },
      'hive.stats.max.variable.length': {
        description: 'To estimate the size of data flowing through operators in Hive/Tez (for reducer estimation etc.), average row size is multiplied with the total number of rows coming out of each operator. Average row size is computed from average column size of all columns in the row. In the absence of column statistics, for variable length columns (like string, bytes, etc.) this value will be used. For fixed length columns their corresponding Java equivalent sizes are used (float – 4 bytes, double – 8 bytes, etc.).',
        type: 'Numeric',
        default: '100'
      },
      'hive.analyze.stmt.collect.partlevel.stats': {
        description: 'Prior to 0.14, on partitioned table, analyze statement used to collect table level statistics when no partition is specified. That behavior has changed beginning 0.14 to instead collect partition level statistics for all partitions. If old behavior of collecting aggregated table level statistics is desired, change the value of this config to false. This impacts only column statistics. Basic statistics are not impacted by this config.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.stats.list.num.entries': {
        description: 'To estimate the size of data flowing through operators in Hive/Tez (for reducer estimation etc.), average row size is multiplied with the total number of rows coming out of each operator. Average row size is computed from average column size of all columns in the row. In the absence of column statistics and for variable length complex columns like list, the average number of entries/values can be specified using this configuration property.',
        type: 'Numeric',
        default: '10'
      },
      'hive.stats.map.num.entries': {
        description: 'To estimate the size of data flowing through operators in Hive/Tez (for reducer estimation etc.), average row size is multiplied with the total number of rows coming out of each operator. Average row size is computed from average column size of all columns in the row. In the absence of column statistics and for variable length complex columns like map, the average number of entries/values can be specified using this configuration property.',
        type: 'Numeric',
        default: '10'
      },
      'hive.stats.fetch.partition.stats': {
        description: 'Annotation of the operator tree with statistics information requires partition level basic statistics like number of rows, data size and file size. Partition statistics are fetched from the metastore. Fetching partition statistics for each needed partition can be expensive when the number of partitions is high. This flag can be used to disable fetching of partition statistics from the metastore. When this flag is disabled, Hive will make calls to the filesystem to get file sizes and will estimate the number of rows from the row schema.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.stats.fetch.column.stats': {
        description: 'Annotation of the operator tree with statistics information requires column statistics. Column statistics are fetched from the metastore. Fetching column statistics for each needed column can be expensive when the number of columns is high. This flag can be used to disable fetching of column statistics from the metastore.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.stats.join.factor': {
        description: 'The Hive/Tez optimizer estimates the data size flowing through each of the operators. The JOIN operator uses column statistics to estimate the number of rows flowing out of it and hence the data size. In the absence of column statistics, this factor determines the amount of rows flowing out of the JOIN operator.',
        type: 'Numeric',
        default: '(float) 1.1'
      },
      'hive.stats.deserialization.factor': {
        description: 'The Hive/Tez optimizer estimates the data size flowing through each of the operators. In the absence of basic statistics like number of rows and data size, file size is used to estimate the number of rows and data size. Since files in tables/partitions are serialized (and optionally compressed) the estimates of number of rows and data size cannot be reliably determined. This factor is multiplied with the file size to account for serialization and compression.',
        type: 'Numeric',
        default: '(float) 1.0'
      },
      'hive.stats.avg.row.size': {
        description: 'In the absence of table/partition statistics, average row size will be used to estimate the number of rows/data size.',
        type: 'Numeric',
        default: '10000'
      },
      'hive.compute.query.using.stats': {
        description: 'When set to true Hive will answer a few queries like min, max, and count(1) purely using statistics stored in the metastore. For basic statistics collection, set the configuration property hive.stats.autogather to true. For more advanced statistics collection, run ANALYZE TABLE queries.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.stats.gather.num.threads': {
        description: 'Number of threads used by partialscan/noscan analyze command for partitioned tables. This is applicable only for file formats that implement the StatsProvidingRecordReader interface (like ORC).',
        type: 'Numeric',
        default: '10'
      },
      'hive.tez.dynamic.semijoin.reduction': {
        description: '',
        type: 'Boolean',
        default: 'true'
      },
      'hive.tez.min.bloom.filter.entries': {
        description: '',
        type: 'Numeric',
        default: '1000000'
      },
      'hive.tez.max.bloom.filter.entries': {
        description: '',
        type: 'Numeric',
        default: '100000000'
      },
      'hive.tez.bloom.filter.factor': {
        description: '',
        type: 'Numeric',
        default: '2.0'
      },
      'hive.tez.bigtable.minsize.semijoin.reduction': {
        description: '',
        type: 'Numeric',
        default: '1000000'
      },
      'hive.conf.restricted.list': {
        description: 'Comma separated list of configuration properties which are immutable at runtime. For example, if hive.security.authorization.enabled is set to true, it should be included in this list to prevent a client from changing it to false at runtime.',
        type: 'Strings',
        default: ''
      },
      'hive.conf.hidden.list': {
        description: 'Comma separated list of configuration options which should not be read by normal user, such as passwords.',
        type: 'String',
        default: 'javax.jdo.option.ConnectionPassword,hive.server2.keystore.password'
      },
      'hive.conf.internal.variable.list': {
        description: 'Comma separated list of configuration options which are internally used and should not be settable via set command.',
        type: 'String',
        default: 'hive.added.files.path,hive.added.jars.path,hive.added.archives.path'
      },
      'hive.security.command.whitelist': {
        description: 'Comma separated list of non-SQL Hive commands that users are authorized to execute. This can be used to restrict the set of authorized commands. The supported command list is "set,reset,dfs,add,delete,compile" in Hive 0.13.0 or "set,reset,dfs,add,list,delete,reload,compile" starting in Hive 0.14.0 and by default all these commands are authorized. To restrict any of these commands, set hive.security.command.whitelist to a value that does not have the command in it.',
        type: 'Strings',
        default: 'set,reset,dfs,add,delete,compile[,list,reload]'
      },
      'hive.security.authorization.enabled': {
        description: 'Enable or disable the Hive client authorization.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.security.authorization.manager': {
        description: 'The Hive client authorization manager class name. The user defined authorization class should implement interface org.apache.hadoop.hive.ql.security.authorization.HiveAuthorizationProvider.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.security.authorization.DefaultHiveAuthorizationProvider'
      },
      'hive.security.authenticator.manager': {
        description: 'Hive client authenticator manager class name. The user-defined authenticator should implement interface org.apache.hadoop.hive.ql.security.HiveAuthenticationProvider.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.security.HadoopDefaultAuthenticator'
      },
      'hive.security.authorization.createtable.user.grants': {
        description: 'The privileges automatically granted to some users whenever a table gets created. An example like "userX,userY:select;userZ:create" will grant select privilege to userX and userY, and grant create privilege to userZ whenever a new table created.',
        type: 'String',
        default: '(empty)'
      },
      'hive.security.authorization.createtable.group.grants': {
        description: 'The privileges automatically granted to some groups whenever a table gets created. An example like "groupX,groupY:select;groupZ:create" will grant select privilege to groupX and groupY, and grant create privilege to groupZ whenever a new table created.',
        type: 'String',
        default: '(empty)'
      },
      'hive.security.authorization.createtable.role.grants': {
        description: 'The privileges automatically granted to some roles whenever a table gets created. An example like "roleX,roleY:select;roleZ:create" will grant select privilege to roleX and roleY, and grant create privilege to roleZ whenever a new table created.',
        type: 'String',
        default: '(empty)'
      },
      'hive.security.authorization.createtable.owner.grants': {
        description: 'The privileges automatically granted to the owner whenever a table gets created. An example like "select,drop" will grant select and drop privilege to the owner of the table. Note that the default gives the creator of a table no access to the table.',
        type: 'String',
        default: '(empty)'
      },
      'hive.metastore.pre.event.listeners': {
        description: 'The pre-event listener classes to be loaded on the metastore side to run code whenever databases, tables, and partitions are created, altered, or dropped. Set this configuration property to org.apache.hadoop.hive.ql.security.authorization.AuthorizationPreEventListener in hive-site.xml to turn on Hive metastore-side security.',
        type: 'String',
        default: '(empty)'
      },
      'hive.security.metastore.authorization.manager': {
        description: 'Hive 0.13 and earlier:  The authorization manager class name to be used in the metastore for authorization. The user-defined authorization class should implement interface org.apache.hadoop.hive.ql.security.authorization.HiveMetastoreAuthorizationProvider. Hive 0.14 and later:  Names of authorization manager classes (comma separated) to be used in the metastore for authorization. User-defined authorization classes should implement interface org.apache.hadoop.hive.ql.security.authorization.HiveMetastoreAuthorizationProvider. All authorization manager classes have to successfully authorize the metastore API call for the command execution to be allowed.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.security.authorization.DefaultHiveMetastoreAuthorizationProvider'
      },
      'hive.security.metastore.authenticator.manager': {
        description: 'The authenticator manager class name to be used in the metastore for authentication. The user-defined authenticator class should implement interface org.apache.hadoop.hive.ql.security.HiveAuthenticationProvider.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.security.HadoopDefaultMetastoreAuthenticator'
      },
      'hive.security.metastore.authorization.auth.reads': {
        description: 'If this is true, the metastore authorizer authorizes read actions on database and table. See Storage Based Authorization.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.metastore.token.signature': {
        description: 'The delegation token service name to match when selecting a token from the current user\'s tokens.',
        type: 'String',
        default: '"" (empty string)'
      },
      'hive.users.in.admin.role': {
        description: 'A comma separated list of users which will be added to the ADMIN role when the metastore starts up. More users can still be added later on.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.security.authorization.sqlstd.confwhitelist': {
        description: 'A comma separated list of configuration properties that users are authorized to set when SQL standard base authorization is used.',
        type: 'Strings',
        default: '(empty, but includes list shown below implicitly)'
      },
      'hive.server2.builtin.udf.whitelist': {
        description: 'A comma separated list of builtin UDFs that are allowed to be executed. A UDF that is not included in the list will return an error if invoked from a query. If set to empty, then treated as wildcard character – all UDFs will be allowed. Note that this configuration is read at the startup time by HiveServer2 and changing this using a \'set\' command in a session won\'t change the behavior.',
        type: 'Strings',
        default: 'Empty (treated as not set – all UDFs allowed)'
      },
      'hive.server2.builtin.udf.blacklist': {
        description: 'A comma separated list of builtin UDFs that are not allowed to be executed. A UDF that is included in the list will return an error if invoked from a query.  Note that this configuration is read at the startup time by HiveServer2 and changing this using a \'set\' command in a session won\'t change the behavior.',
        type: 'String',
        default: 'Empty'
      },
      'hive.security.authorization.task.factory': {
        description: 'To override the default authorization DDL handling, set hive.security.authorization.task.factory to a class that implements the org.apache.hadoop.hive.ql.parse.authorization.HiveAuthorizationTaskFactory interface.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.parse.authorization.HiveAuthorizationTaskFactoryImpl'
      },
      'fs.har.impl': {
        description: 'The implementation for accessing Hadoop Archives. Note that this won\'t be applicable to Hadoop versions less than 0.20.',
        type: 'String',
        default: 'org.apache.hadoop.hive.shims.HiveHarFileSystem'
      },
      'hive.archive.enabled': {
        description: 'Whether archiving operations are permitted.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.support.concurrency': {
        description: 'Whether Hive supports concurrency or not. A ZooKeeper instance must be up and running for the default Hive lock manager to support read-write locks.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.lock.manager': {
        description: 'The lock manager to use when hive.support.concurrency is set to true.',
        type: 'String',
        default: 'org.apache.hadoop.hive.ql.lockmgr.zookeeper.ZooKeeperHiveLockManager'
      },
      'hive.lock.mapred.only.operation': {
        description: 'This configuration property is to control whether or not only do lock on queries that need to execute at least one mapred job.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.lock.query.string.max.length': {
        description: 'The maximum length of the query string to store in the lock. The default value is 1000000, since the data limit of a znode is 1MB',
        type: 'Numeric',
        default: '1000000'
      },
      'hive.lock.numretries': {
        description: 'The number of times you want to try to get all the locks.',
        type: 'Numeric',
        default: '100'
      },
      'hive.unlock.numretries': {
        description: 'The number of times you want to retry to do one unlock.',
        type: 'Numeric',
        default: '10'
      },
      'hive.lock.sleep.between.retries': {
        description: 'The sleep time (in seconds) between various retries.',
        type: 'Numeric',
        default: '60'
      },
      'hive.zookeeper.quorum': {
        description: 'The list of ZooKeeper servers to talk to. This is only needed for read/write locks.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.zookeeper.namespace': {
        description: 'The parent node under which all ZooKeeper nodes are created.',
        type: 'String',
        default: 'hive_zookeeper_namespace'
      },
      'hive.zookeeper.clean.extra.nodes': {
        description: 'Clean extra nodes at the end of the session.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.lockmgr.zookeeper.default.partition.name': {
        description: 'The default partition name when ZooKeeperHiveLockManager is the hive lock manager.',
        type: 'String',
        default: '__HIVE_DEFAULT_ZOOKEEPER_PARTITION__'
      },
      'hive.metastore.metrics.enabled': {
        description: 'Enable metrics on the Hive Metastore Service. (For other metastore configuration properties, see the Metastore and Hive Metastore Security sections.)',
        type: 'Boolean',
        default: 'false'
      },
      'hive.server2.metrics.enabled': {
        description: 'Enable metrics on HiveServer2. (For other HiveServer2 configuration properties, see the HiveServer2 section.)',
        type: 'Boolean',
        default: 'false'
      },
      'hive.service.metrics.class': {
        description: 'Hive metrics subsystem implementation class.  "org.apache.hadoop.hive.common.metrics.metrics2.CodahaleMetrics" is the new implementation. To revert back to the old implementation before Hive 1.3 and 2.0 along with its built-in JMX reporting capabilities, choose "org.apache.hadoop.hive.common.metrics.LegacyMetrics".',
        type: 'String',
        default: 'org.apache.hadoop.hive.common.metrics.metrics2.CodahaleMetrics'
      },
      'hive.service.metrics.codahale.reporter.classes': {
        description: 'Comma separated list of reporter implementation classes for metric class org.apache.hadoop.hive.common.metrics.metrics2.CodahaleMetrics. Overrides hive.service.metrics.reporter conf if present.',
        type: 'String',
        default: '"org.apache.hadoop.hive.common.metrics.metrics2.JsonFileMetricsReporter, org.apache.hadoop.hive.common.metrics.metrics2.JmxMetricsReporter"'
      },
      'hive.service.metrics.file.location': {
        description: 'For hive.service.metrics.class org.apache.hadoop.hive.common.metrics.metrics2.CodahaleMetrics and hive.service.metrics.reporter JSON_FILE, this is the location of the local JSON metrics file dump. This file will get overwritten at every interval of hive.service.metrics.file.frequency.',
        type: 'String',
        default: '"/tmp/report.json"'
      },
      'hive.service.metrics.file.frequency': {
        description: 'For hive.service.metrics.class org.apache.hadoop.hive.common.metrics.metrics2.CodahaleMetrics and hive.service.metrics.reporter JSON_FILE, this is the frequency of updating the JSON metrics file.',
        type: 'Numeric',
        default: '5 seconds'
      },
      'hive.service.metrics.hadoop2.component': {
        description: 'For hive.service.metrics.class org.apache.hadoop.hive.common.metrics.metrics2.CodahaleMetrics and hive.service.metrics.reporter HADOOP2, this is the component name to provide to the HADOOP2 metrics system. Ideally \'hivemetastore\' for the MetaStore and \'hiveserver2\' for HiveServer2. The metrics will be updated at every interval of hive.service.metrics.hadoop2.frequency.',
        type: 'String',
        default: '"hive"'
      },
      'hive.service.metrics.hadoop2.frequency': {
        description: 'For hive.service.metrics.class org.apache.hadoop.hive.common.metrics.metrics2.CodahaleMetrics and hive.service.metrics.reporter HADOOP2, this is the frequency of updating the HADOOP2 metrics system.',
        type: 'Numeric',
        default: '30 seconds'
      },
      'hive.cluster.delegation.token.store.class': {
        description: 'The delegation token store implementation. Set to org.apache.hadoop.hive.thrift.ZooKeeperTokenStore for load-balanced cluster.',
        type: 'String',
        default: 'org.apache.hadoop.hive.thrift.MemoryTokenStore'
      },
      'hive.cluster.delegation.token.store.zookeeper.connectString': {
        description: 'The ZooKeeper token store connect string.',
        type: 'String',
        default: 'localhost:2181'
      },
      'hive.cluster.delegation.token.store.zookeeper.znode': {
        description: 'The root path for token store data.',
        type: 'String',
        default: '/hive/cluster/delegation'
      },
      'hive.cluster.delegation.token.store.zookeeper.acl': {
        description: 'ACL for token store entries. List comma separated all server principals for the cluster.',
        type: 'String',
        default: 'sasl:hive/host1@EXAMPLE.COM:cdrwa,sasl:hive/host2@EXAMPLE.COM:cdrwa'
      },
      'hive.cli.print.header': {
        description: 'Whether to print the names of the columns in query output.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.cli.print.current.db': {
        description: 'Whether to include the current database in the Hive prompt. HBase StorageHandler',
        type: 'Boolean',
        default: 'false'
      },
      'hive.hbase.wal.enabled': {
        description: 'Whether writes to HBase should be forced to the write-ahead log. Disabling this improves HBase write performance at the risk of lost writes in case of a crash.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.hbase.generatehfiles': {
        description: 'True when HBaseStorageHandler should generate hfiles instead of operate against the online table. Hive Web Interface (HWI) (component removed as of Hive 2.2.0)',
        type: 'Boolean',
        default: 'false'
      },
      'hive.repl.rootdir': {
        description: 'This is an HDFS root directory under which Hive\'s REPL DUMP command will operate, creating dumps to replicate along to other warehouses. ',
        type: 'String',
        default: '/usr/hive/repl/'
      },
      'hive.repl.replica.functions.root.dir': {
        description: 'Root directory on the replica warehouse where the repl sub-system will store jars from the primary warehouse.',
        type: 'String',
        default: '/usr/hive/repl/functions'
      },
      'hive.repl.partitions.dump.parallelism': {
        description: 'Number of threads that will be used to dump partition data information during REPL DUMP.',
        type: 'Numeric',
        default: '100'
      },
      'hive.repl.approx.max.load.tasks': {
        description: 'Provide an approximation of the maximum number of tasks that should be executed before dynamically generating the next set of tasks. The number is approximate as Hive will stop at a slightly higher number, the reason being some events might lead to a task increment that would cross the specified limit. Blobstore (i.e. Amazon S3) Starting in release 2.2.0, a set of configurations was added to enable read/write performance improvements when working with tables stored on blobstore systems, such as Amazon S3.',
        type: 'Numeric',
        default: '10000'
      },
      'hive.blobstore.supported.schemes': {
        description: 'List of supported blobstore schemes that Hive uses to apply special read/write performance improvements.',
        type: 'String',
        default: 's3,s3a,s3n'
      },
      'hive.blobstore.optimizations.enabled': {
        description: 'This parameter is a global variable that enables a number of optimizations when running on blobstores. Some of the optimizations, such as hive.blobstore.use.blobstore.as.scratchdir, won\'t be used if this variable is set to false.',
        type: 'Boolean',
        default: 'true'
      },
      'hive.blobstore.use.blobstore.as.scratchdir': {
        description: 'Set this to true to enable the use of scratch directories directly on blob storage systems (it may cause performance penalties).',
        type: 'Boolean',
        default: 'false'
      },
      'hive.exec.input.listing.max.threads': {
        description: 'Set this to a maximum number of threads that Hive will use to list file information from file systems, such as file size and number of files per table (recommended > 1 for blobstore).',
        type: 'Numeric',
        default: '0 (disabled)'
      },
      'hive.test.mode': {
        description: 'Whether Hive is running in test mode. If yes, it turns on sampling and prefixes the output tablename.',
        type: 'Boolean',
        default: 'false'
      },
      'hive.test.mode.prefix': {
        description: 'If Hive is running in test mode, prefixes the output table by this string.',
        type: 'String',
        default: 'test_'
      },
      'hive.test.mode.samplefreq': {
        description: 'If Hive is running in test mode and table is not bucketed, sampling frequency.',
        type: 'Numeric',
        default: '32'
      },
      'hive.test.mode.nosamplelist': {
        description: 'If Hive is running in test mode, don\'t sample the above comma separated list of tables.',
        type: 'Strings',
        default: '(empty)'
      },
      'hive.exec.submit.local.task.via.child': {
        description: '',
        type: 'Boolean',
        default: 'true'
      }
    },
    impala: {
      'ABORT_ON_DEFAULT_LIMIT_EXCEEDED': {
        description: 'When this option is enabled, Impala cancels a query immediately when any of the nodes encounters an error, rather than continuing and possibly returning incomplete results. This option is disabled by default, to help gather maximum diagnostic information when an error occurs, for example, whether the same problem occurred on all nodes or only a single node. Currently, the errors that Impala can skip over involve data corruption, such as a column that contains a string value when expected to contain an integer value.\n\nTo control how much logging Impala does for non-fatal errors when ABORT_ON_ERROR is turned off, use the MAX_ERRORS option.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'APPX_COUNT_DISTINCT': {
        description: 'Allows multiple COUNT(DISTINCT) operations within a single query, by internally rewriting each COUNT(DISTINCT) to use the NDV() function. The resulting count is approximate rather than precise.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'BATCH_SIZE': {
        description: 'Number of rows evaluated at a time by SQL operators. Unspecified or a size of 0 uses a predefined default size. Using a large number improves responsiveness, especially for scan operations, at the cost of a higher memory footprint.',
        type: 'Numeric',
        default: '0 (meaning the predefined default of 1024)'
      },
      'BUFFER_POOL_LIMIT': {
        description: 'Defines a limit on the amount of memory that a query can allocate from the internal buffer pool. The value for this limit applies to the memory on each host, not the aggregate memory across the cluster. Typically not changed by users, except during diagnosis of out-of-memory errors during queries.',
        type: 'Integer',
        default: 'The default setting for this option is the lower of 80% of the MEM_LIMIT setting, or the MEM_LIMIT setting minus 100 MB.'
      },
      'COMPRESSION_CODEC': {
        description: 'When Impala writes Parquet data files using the INSERT statement, the underlying compression is controlled by the COMPRESSION_CODEC query option.',
        type: 'String; SNAPPY, GZIP or NONE',
        default: 'SNAPPY'
      },
      'DEFAULT_JOIN_DISTRIBUTION_MODE': {
        description: 'This option determines the join distribution that Impala uses when any of the tables involved in a join query is missing statistics.\n\nThe setting DEFAULT_JOIN_DISTRIBUTION_MODE=SHUFFLE is recommended when setting up and deploying new clusters, because it is less likely to result in serious consequences such as spilling or out-of-memory errors if the query plan is based on incomplete information.',
        type: 'Integer; The allowed values are BROADCAST (equivalent to 0) or SHUFFLE (equivalent to 1).',
        default: '0'
      },
      'DEFAULT_SPILLABLE_BUFFER_SIZE': {
        description: 'Specifies the default size for a memory buffer used when the spill-to-disk mechanism is activated, for example for queries against a large table with no statistics, or large join operations.\n\nAccepts a numeric value that represents a size in bytes; you can also use a suffix of m or mb for megabytes, or g or gb for gigabytes. If you specify a value with unrecognized formats, subsequent queries fail with an error.',
        type: 'Integer',
        default: '2097152 (2 MB)'
      },
      'DISABLE_CODEGEN': {
        description: 'This is a debug option, intended for diagnosing and working around issues that cause crashes. If a query fails with an "illegal instruction" or other hardware-specific message, try setting DISABLE_CODEGEN=true and running the query again. If the query succeeds only when the DISABLE_CODEGEN option is turned on, submit the problem to Cloudera Support and include that detail in the problem report. Do not otherwise run with this setting turned on, because it results in lower overall performance.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'DISABLE_ROW_RUNTIME_FILTERING': {
        description: 'The DISABLE_ROW_RUNTIME_FILTERING query option reduces the scope of the runtime filtering feature. Queries still dynamically prune partitions, but do not apply the filtering logic to individual rows within partitions.\n\nOnly applies to queries against Parquet tables. For other file formats, Impala only prunes at the level of partitions, not individual rows.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'DISABLE_STREAMING_PREAGGREGATIONS': {
        description: 'Turns off the "streaming preaggregation" optimization that is available in CDH 5.7 / Impala 2.5 and higher. This optimization reduces unnecessary work performed by queries that perform aggregation operations on columns with few or no duplicate values, for example DISTINCT id_column or GROUP BY unique_column. If the optimization causes regressions in existing queries that use aggregation functions, you can turn it off as needed by setting this query option.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'DISABLE_UNSAFE_SPILLS': {
        description: 'Enable this option if you prefer to have queries fail when they exceed the Impala memory limit, rather than write temporary data to disk.\n\nQueries that "spill" to disk typically complete successfully, when in earlier Impala releases they would have failed. However, queries with exorbitant memory requirements due to missing statistics or inefficient join clauses could become so slow as a result that you would rather have them cancelled automatically and reduce the memory usage through standard Impala tuning techniques.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'EXEC_SINGLE_NODE_ROWS_THRESHOLD': {
        description: 'This setting controls the cutoff point (in terms of number of rows scanned) below which Impala treats a query as a "small" query, turning off optimizations such as parallel execution and native code generation. The overhead for these optimizations is applicable for queries involving substantial amounts of data, but it makes sense to skip them for queries involving tiny amounts of data. Reducing the overhead for small queries allows Impala to complete them more quickly, keeping YARN resources, admission control slots, and so on available for data-intensive queries.',
        type: 'Numeric',
        default: '100'
      },
      'EXPLAIN_LEVEL': {
        description: 'Controls the amount of detail provided in the output of the EXPLAIN statement. The basic output can help you identify high-level performance issues such as scanning a higher volume of data or more partitions than you expect. The higher levels of detail show how intermediate results flow between nodes and how different SQL operations such as ORDER BY, GROUP BY, joins, and WHERE clauses are implemented within a distributed query.',
        type: 'String or Int; 0 - MINIMAL, 1 - STANDARD, 2 - EXTENDED or 3 - VERBOSE',
        default: '1'
      },
      'HBASE_CACHE_BLOCKS': {
        description: 'Setting this option is equivalent to calling the setCacheBlocks method of the class org.apache.hadoop.hbase.client.Scan, in an HBase Java application. Helps to control the memory pressure on the HBase RegionServer, in conjunction with the HBASE_CACHING query option.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'HBASE_CACHING': {
        description: 'Setting this option is equivalent to calling the setCaching method of the class org.apache.hadoop.hbase.client.Scan, in an HBase Java application. Helps to control the memory pressure on the HBase RegionServer, in conjunction with the HBASE_CACHE_BLOCKS query option.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'MAX_ERRORS': {
        description: 'Maximum number of non-fatal errors for any particular query that are recorded in the Impala log file. For example, if a billion-row table had a non-fatal data error in every row, you could diagnose the problem without all billion errors being logged. Unspecified or 0 indicates the built-in default value of 1000.\n\nThis option only controls how many errors are reported. To specify whether Impala continues or halts when it encounters such errors, use the ABORT_ON_ERROR option.',
        type: 'Numeric',
        default: '0 (meaning 1000 errors)'
      },
      'MAX_NUM_RUNTIME_FILTERS': {
        description: 'The MAX_NUM_RUNTIME_FILTERS query option sets an upper limit on the number of runtime filters that can be produced for each query.',
        type: 'Integer',
        default: '10'
      },
      'MAX_ROW_SIZE': {
        description: 'Ensures that Impala can process rows of at least the specified size. (Larger rows might be successfully processed, but that is not guaranteed.) Applies when constructing intermediate or final rows in the result set. This setting prevents out-of-control memory use when accessing columns containing huge strings.\n\nAccepts a numeric value that represents a size in bytes; you can also use a suffix of m or mb for megabytes, or g or gb for gigabytes. If you specify a value with unrecognized formats, subsequent queries fail with an error.',
        type: 'Integer',
        default: '524288 (512 KB)'
      },
      'MAX_SCAN_RANGE_LENGTH': {
        description: 'Maximum length of the scan range. Interacts with the number of HDFS blocks in the table to determine how many CPU cores across the cluster are involved with the processing for a query. (Each core processes one scan range.)\n\nLowering the value can sometimes increase parallelism if you have unused CPU capacity, but a too-small value can limit query performance because each scan range involves extra overhead.\n\nOnly applicable to HDFS tables. Has no effect on Parquet tables. Unspecified or 0 indicates backend default, which is the same as the HDFS block size for each table.',
        type: 'Numeric',
        default: '0'
      },
      'MEM_LIMIT': {
        description: 'When resource management is not enabled, defines the maximum amount of memory a query can allocate on each node. Therefore, the total memory that can be used by a query is the MEM_LIMIT times the number of nodes.\n\nAccepts a numeric value that represents a size in bytes; you can also use a suffix of m or mb for megabytes, or g or gb for gigabytes. If you specify a value with unrecognized formats, subsequent queries fail with an error.',
        type: 'Numeric',
        default: '0 (unlimited)'
      },
      'MIN_SPILLABLE_BUFFER_SIZE': {
        description: 'Specifies the minimum size for a memory buffer used when the spill-to-disk mechanism is activated, for example for queries against a large table with no statistics, or large join operations.\n\nAccepts a numeric value that represents a size in bytes; you can also use a suffix of m or mb for megabytes, or g or gb for gigabytes. If you specify a value with unrecognized formats, subsequent queries fail with an error.',
        type: 'Integer',
        default: '65536 (64 KB)'
      },
      'MT_DOP': {
        description: 'Sets the degree of parallelism used for certain operations that can benefit from multithreaded execution. You can specify values higher than zero to find the ideal balance of response time, memory usage, and CPU usage during statement processing.',
        type: 'Integer; Range from 0 to 64',
        default: '0'
      },
      'NUM_NODES': {
        description: 'Limit the number of nodes that process a query, typically during debugging.',
        type: 'Numeric; Only accepts the values 0 (meaning all nodes) or 1 (meaning all work is done on the coordinator node).',
        default: '0'
      },
      'NUM_SCANNER_THREADS': {
        description: 'Maximum number of scanner threads (on each node) used for each query. By default, Impala uses as many cores as are available (one thread per core). You might lower this value if queries are using excessive resources on a busy cluster. Impala imposes a maximum value automatically, so a high value has no practical',
        type: 'Numeric',
        default: '0'
      },
      'OPTIMIZE_PARTITION_KEY_SCANS': {
        description: 'Enables a fast code path for queries that apply simple aggregate functions to partition key columns: MIN(key_column), MAX(key_column), or COUNT(DISTINCT key_column).',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'PARQUET_ANNOTATE_STRINGS_UTF8': {
        description: 'Causes Impala INSERT and CREATE TABLE AS SELECT statements to write Parquet files that use the UTF-8 annotation for STRING columns.\n\nBy default, Impala represents a STRING column in Parquet as an unannotated binary field.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'PARQUET_FALLBACK_SCHEMA_RESOLUTION': {
        description: 'Allows Impala to look up columns within Parquet files by column name, rather than column order, when necessary.',
        type: 'integer or string. Allowed values are 0 or position, 1 or name.',
        default: '0'
      },
      'PARQUET_FILE_SIZE': {
        description: 'Specifies the maximum size of each Parquet data file produced by Impala INSERT statements.',
        type: 'Numeric, with optional unit specifier.',
        default: '0 (produces files with a target size of 256 MB; files might be larger for very wide tables)'
      },
      'PREFETCH_MODE': {
        description: 'Determines whether the prefetching optimization is applied during join query processing.',
        type: 'Numeric (0, 1) or corresponding mnemonic strings (NONE, HT_BUCKET).',
        default: '1 (equivalent to HT_BUCKET)'
      },
      'QUERY_TIMEOUT_S': {
        description: 'Sets the idle query timeout value for the session, in seconds. Queries that sit idle for longer than the timeout value are automatically cancelled. If the system administrator specified the --idle_query_timeout startup option, QUERY_TIMEOUT_S must be smaller than or equal to the --idle_query_timeout value.',
        type: 'Numeric',
        default: '0 (no timeout if --idle_query_timeout not in effect; otherwise, use --idle_query_timeout value)'
      },
      'REQUEST_POOL': {
        description: 'The pool or queue name that queries should be submitted to. Only applies when you enable the Impala admission control feature. Specifies the name of the pool used by requests from Impala to the resource manager.',
        type: 'String',
        default: 'empty (use the user-to-pool mapping defined by an impalad startup option in the Impala configuration file)'
      },
      'REPLICA_PREFERENCE': {
        description: 'The REPLICA_PREFERENCE query option lets you spread the load more evenly if hotspots and bottlenecks persist, by allowing hosts to do local reads, or even remote reads, to retrieve the data for cached blocks if Impala can determine that it would be too expensive to do all such processing on a particular host.',
        type: 'Numeric (0, 3, 5) or corresponding mnemonic strings (CACHE_LOCAL, DISK_LOCAL, REMOTE). The gaps in the numeric sequence are to accomodate other intermediate values that might be added in the future.',
        default: '0 (equivalent to CACHE_LOCAL)'
      },
      'RUNTIME_BLOOM_FILTER_SIZE': {
        description: 'Size (in bytes) of Bloom filter data structure used by the runtime filtering feature.',
        type: 'Integer; Maximum 16 MB.',
        default: '1048576 (1 MB)'
      },
      'RUNTIME_FILTER_MAX_SIZE': {
        description: 'The RUNTIME_FILTER_MAX_SIZE query option adjusts the settings for the runtime filtering feature. This option defines the maximum size for a filter, no matter what the estimates produced by the planner are. This value also overrides any lower number specified for the RUNTIME_BLOOM_FILTER_SIZE query option. Filter sizes are rounded up to the nearest power of two.',
        type: 'Integer',
        default: '0 (meaning use the value from the corresponding impalad startup option)'
      },
      'RUNTIME_FILTER_MIN_SIZE': {
        description: 'The RUNTIME_FILTER_MIN_SIZE query option adjusts the settings for the runtime filtering feature. This option defines the minimum size for a filter, no matter what the estimates produced by the planner are. This value also overrides any lower number specified for the RUNTIME_BLOOM_FILTER_SIZE query option. Filter sizes are rounded up to the nearest power of two.',
        type: 'Integer',
        default: '0 (meaning use the value from the corresponding impalad startup option)'
      },
      'RUNTIME_FILTER_MODE': {
        description: 'The RUNTIME_FILTER_MODE query option adjusts the settings for the runtime filtering feature. It turns this feature on and off, and controls how extensively the filters are transmitted between hosts.',
        type: 'Numeric (0, 1, 2) or corresponding mnemonic strings (OFF, LOCAL, GLOBAL).',
        default: '2 (equivalent to GLOBAL); formerly was 1 / LOCAL, in CDH 5.7 / Impala 2.5'
      },
      'RUNTIME_FILTER_WAIT_TIME_MS': {
        description: 'The RUNTIME_FILTER_WAIT_TIME_MS query option adjusts the settings for the runtime filtering feature. It specifies a time in milliseconds that each scan node waits for runtime filters to be produced by other plan fragments.',
        type: 'Integer',
        default: '0 (meaning use the value from the corresponding impalad startup option)'
      },
      'S3_SKIP_INSERT_STAGING': {
        description: 'Speeds up INSERT operations on tables or partitions residing on the Amazon S3 filesystem. The tradeoff is the possibility of inconsistent data left behind if an error occurs partway through the operation.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'true (shown as 1 in output of SET statement)'
      },
      'SCAN_NODE_CODEGEN_THRESHOLD': {
        description: 'The SCAN_NODE_CODEGEN_THRESHOLD query option adjusts the aggressiveness of the code generation optimization process when performing I/O read operations. It can help to work around performance problems for queries where the table is small and the WHERE clause is complicated.',
        type: 'Integer',
        default: '1800000 (1.8 million)'
      },
      'SCHEDULE_RANDOM_REPLICA': {
        description: 'The SCHEDULE_RANDOM_REPLICA query option fine-tunes the algorithm for deciding which host processes each HDFS data block. It only applies to tables and partitions that are not enabled for the HDFS caching feature.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'SCRATCH_LIMIT': {
        description: 'Specifies the maximum amount of disk storage, in bytes, that any Impala query can consume on any host using the "spill to disk" mechanism that handles queries that exceed the memory limit.',
        type: 'Numeric, with optional unit specifier',
        default: '-1 (amount of spill space is unlimited)'
      },
      'SUPPORT_START_OVER': {
        description: 'Leave this setting at its default value. It is a read-only setting, tested by some client applications such as Hue.\n\nIf you accidentally change it through impala-shell, subsequent queries encounter errors until you undo the change by issuing UNSET support_start_over.',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      },
      'SYNC_DDL': {
        description: 'When enabled, causes any DDL operation such as CREATE TABLE or ALTER TABLE to return only when the changes have been propagated to all other Impala nodes in the cluster by the Impala catalog service. That way, if you issue a subsequent CONNECT statement in impala-shell to connect to a different node in the cluster, you can be sure that other node will already recognize any added or changed tables. (The catalog service automatically broadcasts the DDL changes to all nodes automatically, but without this option there could be a period of inconsistency if you quickly switched to another node, such as by issuing a subsequent query through a load-balancing proxy.)',
        type: 'Boolean; recognized values are 1 and 0, or true and false; any other value interpreted as false',
        default: 'false (shown as 0 in output of SET statement)'
      }
    }
  };

  var createOptionHtml = function (funcDesc) {
    var html = '<div class="fn-details">';
    if (funcDesc.description) {
      html += '<p><span style="white-space: pre; font-family: monospace;">' + funcDesc.description + '</span></p>';
    }
    if (funcDesc.type) {
      html += '<p>Type:' + funcDesc.type + '</p>';
    }
    if (funcDesc.default) {
      html += '<p>Default:' + funcDesc.default + '</p>';
    }
    html += '<div>';
    return html;
  };

  var suggestOptions = function (dialect, completions, category) {
    if (dialect === 'hive' || dialect === 'impala') {
      Object.keys(SET_OPTIONS[dialect]).forEach(function (name) {
        completions.push({
          category: category,
          value: name,
          meta: '',
          popular: ko.observable(false),
          weightAdjust: 0,
          details: SET_OPTIONS[dialect][name]
        })
      });
    }
  };

  return {
    suggestOptions : suggestOptions
  };
})();

var SqlFunctions = (function () {

  var MATHEMATICAL_FUNCTIONS = {
    hive: {
      abs: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'abs(DOUBLE a)',
        draggable: 'abs()',
        description: 'Returns the absolute value.'
      },
      acos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'acos(DECIMAL|DOUBLE a)',
        draggable: 'acos()',
        description: 'Returns the arccosine of a if -1<=a<=1 or NULL otherwise.'
      },
      asin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'asin(DECIMAL|DOUBLE a)',
        draggable: 'asin()',
        description: 'Returns the arc sin of a if -1<=a<=1 or NULL otherwise.'
      },
      atan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'atan(DECIMAL|DOUBLE a)',
        draggable: 'atan()',
        description: 'Returns the arctangent of a.'
      },
      bin: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}]],
        signature: 'bin(BIGINT a)',
        draggable: 'bin()',
        description: 'Returns the number in binary format'
      },
      bround: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'INT', optional: true}]],
        signature: 'bround(DOUBLE a [, INT decimals])',
        draggable: 'bround()',
        description: 'Returns the rounded BIGINT value of a using HALF_EVEN rounding mode with optional decimal places d.'
      },
      cbrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'cbft(DOUBLE a)',
        draggable: 'cbft()',
        description: 'Returns the cube root of a double value.'
      },
      ceil: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'ceil(DOUBLE a)',
        draggable: 'ceil()',
        description: 'Returns the minimum BIGINT value that is equal to or greater than a.'
      },
      ceiling: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'ceiling(DOUBLE a)',
        draggable: 'ceiling()',
        description: 'Returns the minimum BIGINT value that is equal to or greater than a.'
      },
      conv: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'STRING'}], [{type: 'INT'}], [{type: 'INT'}]],
        signature: 'conv(BIGINT|STRING a, INT from_base, INT to_base)',
        draggable: 'conv()',
        description: 'Converts a number from a given base to another'
      },
      cos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'cos(DECIMAL|DOUBLE a)',
        draggable: 'cos()',
        description: 'Returns the cosine of a (a is in radians).'
      },
      degrees: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
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
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'exp(DECIMAL|DOUBLE a)',
        draggable: 'exp()',
        description: 'Returns e^a where e is the base of the natural logarithm.'
      },
      factorial: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'INT'}]],
        signature: 'factorial(INT a)',
        draggable: 'factorial()',
        description: 'Returns the factorial of a. Valid a is [0..20].'
      },
      floor: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'floor(DOUBLE a)',
        draggable: 'floor()',
        description: 'Returns the maximum BIGINT value that is equal to or less than a.'
      },
      greatest: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'greatest(T a1, T a2, ...)',
        draggable: 'greatest()',
        description: 'Returns the greatest value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with ">" operator.'
      },
      hex: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}, {type: 'BINARY'}, {type: 'STRING'}]],
        signature: 'hex(BIGINT|BINARY|STRING a)',
        draggable: 'hex()',
        description: 'If the argument is an INT or binary, hex returns the number as a STRING in hexadecimal format. Otherwise if the number is a STRING, it converts each character into its hexadecimal representation and returns the resulting STRING.'
      },
      least: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'least(T a1, T a2, ...)',
        draggable: 'least()',
        description: 'Returns the least value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with "<" operator.'
      },
      ln: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'ln(DECIMAL|DOUBLE a)',
        draggable: 'ln()',
        description: 'Returns the natural logarithm of the argument a'
      },
      log: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}], [{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'log(DECIMAL|DOUBLE base, DECIMAL|DOUBLE a)',
        draggable: 'log()',
        description: 'Returns the base-base logarithm of the argument a.'
      },
      log10: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'log10(DECIMAL|DOUBLE a)',
        draggable: 'log10()',
        description: 'Returns the base-10 logarithm of the argument a.'
      },
      log2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'log2(DECIMAL|DOUBLE a)',
        draggable: 'log2()',
        description: 'Returns the base-2 logarithm of the argument a.'
      },
      negative: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}]],
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
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}], [{type: 'T'}]],
        signature: 'pmod(T<DOUBLE|INT> a, T b)',
        draggable: 'pmod()',
        description: 'Returns the positive value of a mod b'
      },
      positive: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}]],
        signature: 'positive(T<DOUBLE|INT> a)',
        draggable: 'positive()',
        description: 'Returns a.'
      },
      pow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'pow(DOUBLE a, DOUBLE p)',
        draggable: 'pow()',
        description: 'Returns a^p'
      },
      power: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'power(DOUBLE a, DOUBLE p)',
        draggable: 'power()',
        description: 'Returns a^p'
      },
      radians: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'radians(DECIMAL|DOUBLE a)',
        draggable: 'radians()',
        description: 'Converts value of a from degrees to radians.'
      },
      rand: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'INT', optional: true}]],
        signature: 'rand([INT seed])',
        draggable: 'rand()',
        description: 'Returns a random number (that changes from row to row) that is distributed uniformly from 0 to 1. Specifying the seed will make sure the generated random number sequence is deterministic.'
      },
      round: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'INT', optional: true}]],
        signature: 'round(DOUBLE a [, INT d])',
        draggable: 'round()',
        description: 'Returns the rounded BIGINT value of a or a rounded to d decimal places.'
      },
      shiftleft: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'INT'}, {type: 'SMALLINT'}, {type: 'TINYINT'}], [{type: 'INT'}]],
        signature: 'shiftleft(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        draggable: 'shiftleft()',
        description: 'Bitwise left shift. Shifts a b positions to the left. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      shiftright: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'INT'}, {type: 'SMALLINT'}, {type: 'TINYINT'}], [{type: 'INT'}]],
        signature: 'shiftright(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        draggable: 'shiftright()',
        description: 'Bitwise right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      shiftrightunsigned: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'INT'}, {type: 'SMALLINT'}, {type: 'TINYINT'}], [{type: 'INT'}]],
        signature: 'shiftrightunsigned(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        draggable: 'shiftrightunsigned()',
        description: 'Bitwise unsigned right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      sign: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}]],
        signature: 'sign(T<DOUBLE|INT> a)',
        draggable: 'sign()',
        description: 'Returns the sign of a as \'1.0\' (if a is positive) or \'-1.0\' (if a is negative), \'0.0\' otherwise. The decimal version returns INT instead of DOUBLE.'
      },
      sin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'sin(DECIMAL|DOUBLE a)',
        draggable: 'sin()',
        description: 'Returns the sine of a (a is in radians).'
      },
      sqrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'sqrt(DECIMAL|DOUBLE a)',
        draggable: 'sqrt()',
        description: 'Returns the square root of a'
      },
      tan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'tan(DECIMAL|DOUBLE a)',
        draggable: 'tan()',
        description: 'Returns the tangent of a (a is in radians).'
      },
      unhex: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'STRING'}]],
        signature: 'unhex(STRING a)',
        draggable: 'unhex()',
        description: 'Inverse of hex. Interprets each pair of characters as a hexadecimal number and converts to the byte representation of the number.'
      },
      width_bucket: {
        returnTypes: ['INT'],
        arguments: [[{type: 'NUMBER'}, {type: 'NUMBER'}, {type: 'NUMBER'}, {type: 'INT'}]],
        signature: 'width_bucket(NUMBER expr, NUMBER min_value, NUMBER max_value, INT num_buckets)',
        draggable: 'width_bucket()',
        description: 'Returns an integer between 0 and num_buckets+1 by mapping expr into the ith equally sized bucket. Buckets are made by dividing [min_value, max_value] into equally sized regions. If expr < min_value, return 1, if expr > max_value return num_buckets+1. (as of Hive 3.0.0)'
      }
    },
    impala: {
      abs: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'abs(T a)',
        draggable: 'abs()',
        description: 'Returns the absolute value of the argument. Use this function to ensure all return values are positive. This is different than the positive() function, which returns its argument unchanged (even if the argument was negative).'
      },
      acos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'acos(DOUBLE a)',
        draggable: 'acos()',
        description: 'Returns the arccosine of the argument.'
      },
      asin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'asin(DOUBLE a)',
        draggable: 'asin()',
        description: 'Returns the arcsine of the argument.'
      },
      atan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'atan(DOUBLE a)',
        draggable: 'atan()',
        description: 'Returns the arctangent of the argument.'
      },
      atan2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'atan2(DOUBLE a, DOUBLE b)',
        draggable: 'atan2()',
        description: 'Returns the arctangent of the two arguments, with the signs of the arguments used to determine the quadrant of the result.'
      },
      bin: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}]],
        signature: 'bin(BIGINT a)',
        draggable: 'bin()',
        description: 'Returns the binary representation of an integer value, that is, a string of 0 and 1 digits.'
      },
      ceil: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}]],
        signature: 'ceil(T<DOUBLE|DECIMAL> a)',
        draggable: 'ceil()',
        description: 'Returns the smallest integer that is greater than or equal to the argument.'
      },
      ceiling: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}]],
        signature: 'ceiling(T<DOUBLE|DECIMAL> a)',
        draggable: 'ceiling()',
        description: 'Returns the smallest integer that is greater than or equal to the argument.'
      },
      conv: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'STRING'}], [{type: 'INT'}], [{type: 'INT'}]],
        signature: 'conv(T<BIGINT|STRING> a, INT from_base, INT to_base)',
        draggable: 'conv()',
        description: 'Returns a string representation of an integer value in a particular base. The input value can be a string, for example to convert a hexadecimal number such as fce2 to decimal. To use the return value as a number (for example, when converting to base 10), use CAST() to convert to the appropriate type.'
      },
      cos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'cos(DOUBLE a)',
        draggable: 'cos()',
        description: 'Returns the cosine of the argument.'
      },
      cosh: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'cosh(DOUBLE a)',
        draggable: 'cosh()',
        description: 'Returns the hyperbolic cosine of the argument.'
      },
      cot: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'cot(DOUBLE a)',
        draggable: 'cot()',
        description: 'Returns the cotangent of the argument.'
      },
      dceil: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}]],
        signature: 'dceil(T<DOUBLE|DECIMAL> a)',
        draggable: 'dceil()',
        description: 'Returns the smallest integer that is greater than or equal to the argument.'
      },
      degrees: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'degrees(DOUBLE a)',
        draggable: 'degrees()',
        description: 'Converts argument value from radians to degrees.'
      },
      dexp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'dexp(DOUBLE a)',
        draggable: 'dexp()',
        description: 'Returns the mathematical constant e raised to the power of the argument.'
      },
      dfloor: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}]],
        signature: 'dfloor(T<DOUBLE|DECIMAL> a)',
        draggable: 'dfloor()',
        description: 'Returns the largest integer that is less than or equal to the argument.'
      },
      dlog1: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'dlog1(DOUBLE a)',
        draggable: 'dlog1()',
        description: 'Returns the natural logarithm of the argument.'
      },
      dpow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'dpow(DOUBLE a, DOUBLE p)',
        draggable: 'dpow()',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      dround: {
        returnTypes: ['T'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}], [{type: 'INT', optional: true}]],
        signature: 'dround(DOUBLE a [, INT d]), round(DECIMAL val, INT d)',
        draggable: 'dround()',
        description: 'Rounds a floating-point value. By default (with a single argument), rounds to the nearest integer. Values ending in .5 are rounded up for positive numbers, down for negative numbers (that is, away from zero). The optional second argument specifies how many digits to leave after the decimal point; values greater than zero produce a floating-point return value rounded to the requested number of digits to the right of the decimal point.'
      },
      dsqrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'dsqrt(DOUBLE a)',
        draggable: 'dsqrt()',
        description: 'Returns the square root of the argument.'
      },
      dtrunc: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}], [{ type: 'NUMBER', optional: true }]],
        signature: 'dtrunc(T<DOUBLE|DECIMAL> a, [NUMBER b])',
        draggable: 'dtrunc()',
        description: 'Removes some or all fractional digits from a numeric value. With no argument, removes all fractional digits, leaving an integer value. The optional argument specifies the number of fractional digits to include in the return value, and only applies with the argument type is DECIMAL. truncate() and dtrunc() are aliases for the same function.'
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
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'exp(DOUBLE a)',
        draggable: 'exp()',
        description: 'Returns the mathematical constant e raised to the power of the argument.'
      },
      factorial: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'factorial(T a)',
        draggable: 'factorial()',
        description: 'Computes the factorial of an integer value. It works with any integer type. You can use either the factorial() function or the ! operator. The factorial of 0 is 1. Likewise, the factorial() function returns 1 for any negative value. The maximum positive value for the input argument is 20; a value of 21 or greater overflows the range for a BIGINT and causes an error.'
      },
      floor: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}]],
        signature: 'floor(T<DOUBLE|DECIMAL> a)',
        draggable: 'floor()',
        description: 'Returns the largest integer that is less than or equal to the argument.'
      },
      fmod: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DOUBLE'}], [{type: 'FLOAT'}, {type: 'FLOAT'}]],
        signature: 'fmod(DOUBLE a, DOUBLE b), fmod(FLOAT a, FLOAT b)',
        draggable: 'fmod()',
        description: 'Returns the modulus of a number.'
      },
      fpow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'fpow(DOUBLE a, DOUBLE p)',
        draggable: 'fpow()',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      fnv_hash: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'fnv_hash(T a)',
        draggable: 'fnv_hash()',
        description: 'Returns a consistent 64-bit value derived from the input argument, for convenience of implementing hashing logic in an application.'
      },
      greatest: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'greatest(T a1, T a2, ...)',
        draggable: 'greatest()',
        description: 'Returns the largest value from a list of expressions.'
      },
      hex: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}, {type: 'STRING'}]],
        signature: 'hex(T<BIGINT|STRING> a)',
        draggable: 'hex()',
        description: 'Returns the hexadecimal representation of an integer value, or of the characters in a string.'
      },
      is_inf: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'is_inf(DOUBLE a)',
        draggable: 'is_inf()',
        description: 'Tests whether a value is equal to the special value "inf", signifying infinity.'
      },
      is_nan: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'is_nan(DOUBLE A)',
        draggable: 'is_nan()',
        description: 'Tests whether a value is equal to the special value "NaN", signifying "not a number".'
      },
      least: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'least(T a1, T a2, ...)',
        draggable: 'least()',
        description: 'Returns the smallest value from a list of expressions.'
      },
      ln: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'ln(DOUBLE a)',
        draggable: 'ln()',
        description: 'Returns the natural logarithm of the argument.'
      },
      log: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'log(DOUBLE base, DOUBLE a)',
        draggable: 'log()',
        description: 'Returns the logarithm of the second argument to the specified base.'
      },
      log10: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'log10(DOUBLE a)',
        draggable: 'log10()',
        description: 'Returns the logarithm of the argument to the base 10.'
      },
      log2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
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
        description: 'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_int: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'min_int()',
        draggable: 'min_int()',
        description: 'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_smallint: {
        returnTypes: ['SMALLINT'],
        arguments: [],
        signature: 'min_smallint()',
        draggable: 'min_smallint()',
        description: 'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_tinyint: {
        returnTypes: ['TINYINT'],
        arguments: [],
        signature: 'min_tinyint()',
        draggable: 'min_tinyint()',
        description: 'Returns the smallest value of the associated integral type (a negative number).'
      },
      mod: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'mod(T a, T b)',
        draggable: 'mod()',
        description: 'Returns the modulus of a number. Equivalent to the % arithmetic operator. Works with any size integer type, any size floating-point type, and DECIMAL with any precision and scale.'
      },
      negative: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'negative(T a)',
        draggable: 'negative()',
        description: 'Returns the argument with the sign reversed; returns a positive value if the argument was already negative.'
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
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}], [{type: 'T'}]],
        signature: 'pmod(T<DOUBLE|INT> a, T b)',
        draggable: 'pmod()',
        description: 'Returns the positive modulus of a number.'
      },
      positive: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'positive(T a)',
        draggable: 'positive()',
        description: 'Returns the original argument unchanged (even if the argument is negative).'
      },
      pow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'pow(DOUBLE a, DOUBLE p)',
        draggable: 'pow()',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      power: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'power(DOUBLE a, DOUBLE p)',
        draggable: 'power()',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      precision: {
        returnTypes: ['INT'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'precision(numeric_expression)',
        draggable: 'precision()',
        description: 'Computes the precision (number of decimal digits) needed to represent the type of the argument expression as a DECIMAL value.'
      },
      quotient: {
        returnTypes: ['INT'],
        arguments: [[{type: 'BIGINT'}, {type: 'DOUBLE'}], [{type: 'BIGINT'}, {type: 'DOUBLE'}]],
        signature: 'quotient(BIGINT numerator, BIGINT denominator), quotient(DOUBLE numerator, DOUBLE denominator)',
        draggable: 'quotient()',
        description: 'Returns the first argument divided by the second argument, discarding any fractional part. Avoids promoting arguments to DOUBLE as happens with the / SQL operator.'
      },
      radians: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'radians(DOUBLE a)',
        draggable: 'radians()',
        description: 'Converts argument value from degrees to radians.'
      },
      rand: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'INT', optional: true}]],
        signature: 'rand([INT seed])',
        draggable: 'rand()',
        description: 'Returns a random value between 0 and 1. After rand() is called with a seed argument, it produces a consistent random sequence based on the seed value.'
      },
      random: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'INT', optional: true}]],
        signature: 'random([INT seed])',
        draggable: 'random()',
        description: 'Returns a random value between 0 and 1. After rand() is called with a seed argument, it produces a consistent random sequence based on the seed value.'
      },
      round: {
        returnTypes: ['T'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}], [{type: 'INT', optional: true}]],
        signature: 'round(DOUBLE a [, INT d]), round(DECIMAL val, INT d)',
        draggable: 'round()',
        description: 'Rounds a floating-point value. By default (with a single argument), rounds to the nearest integer. Values ending in .5 are rounded up for positive numbers, down for negative numbers (that is, away from zero). The optional second argument specifies how many digits to leave after the decimal point; values greater than zero produce a floating-point return value rounded to the requested number of digits to the right of the decimal point.'
      },
      scale: {
        returnTypes: ['INT'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'scale(numeric_expression)',
        draggable: 'scale()',
        description: 'Computes the scale (number of decimal digits to the right of the decimal point) needed to represent the type of the argument expression as a DECIMAL value.'
      },
      sign: {
        returnTypes: ['INT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'sign(DOUBLE a)',
        draggable: 'sign()',
        description: 'Returns -1, 0, or 1 to indicate the signedness of the argument value.'
      },
      sin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'sin(DOUBLE a)',
        draggable: 'sin()',
        description: 'Returns the sine of the argument.'
      },
      sinh: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'sinh(DOUBLE a)',
        draggable: 'sinh()',
        description: 'Returns the hyperbolic sine of the argument.'
      },
      sqrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'sqrt(DOUBLE a)',
        draggable: 'sqrt()',
        description: 'Returns the square root of the argument.'
      },
      tan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'tan(DOUBLE a)',
        draggable: 'tan()',
        description: 'Returns the tangent of the argument.'
      },
      tanh: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'tanh(DOUBLE a)',
        draggable: 'tanh()',
        description: 'Returns the tangent of the argument.'
      },
      truncate: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}], [{ type: 'NUMBER', optional: true }]],
        signature: 'truncate(T<DOUBLE|DECIMAL> a, [NUMBER b])',
        draggable: 'truncate()',
        description: 'Removes some or all fractional digits from a numeric value. With no argument, removes all fractional digits, leaving an integer value. The optional argument specifies the number of fractional digits to include in the return value, and only applies with the argument type is DECIMAL. truncate() and dtrunc() are aliases for the same function.'
      },
      unhex: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'unhex(STRING a)',
        draggable: 'unhex()',
        description: 'Returns a string of characters with ASCII values corresponding to pairs of hexadecimal digits in the argument.'
      }
    }
  };

  var COMPLEX_TYPE_CONSTRUCTS = {
    hive: {
      array: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'array(val1, val2, ...)',
        draggable: 'array()',
        description: 'Creates an array with the given elements.'
      },
      create_union: {
        returnTypes: ['UNION'],
        arguments: [[{type: 'T'}], [{type: 'T', multiple: true}]],
        signature: 'create_union(tag, val1, val2, ...)',
        draggable: 'create_union()',
        description: 'Creates a union type with the value that is being pointed to by the tag parameter.'
      },
      map: {
        returnTypes: ['MAP'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'map(key1, value1, ...)',
        draggable: 'map()',
        description: 'Creates a map with the given key/value pairs.'
      },
      named_struct: {
        returnTypes: ['STRUCT'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'named_struct(name1, val1, ...)',
        draggable: 'named_struct()',
        description: 'Creates a struct with the given field names and values.'
      },
      struct: {
        returnTypes: ['STRUCT'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'struct(val1, val2, ...)',
        draggable: 'struct()',
        description: 'Creates a struct with the given field values. Struct field names will be col1, col2, ....'
      }
    },
    impala: {}
  };

  var AGGREGATE_FUNCTIONS = {
    generic: {
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'count(col)',
        draggable: 'count()',
        description: 'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL.'
      },
      sum: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'sum(col)',
        draggable: 'sum()',
        description: 'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'
      },
      max: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'max(col)',
        draggable: 'max()',
        description: 'Returns the maximum value of the column in the group.'
      },
      min: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'min(col)',
        draggable: 'min()',
        description: 'Returns the minimum of the column in the group.'
      }
    },
    hive: {
      avg: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'avg(col)',
        draggable: 'avg()',
        description: 'Returns the average of the elements in the group or the average of the distinct values of the column in the group.'
      },
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'count([DISTINCT] col)',
        draggable: 'count()',
        description: 'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL. count(DISTINCT expr[, expr]) - Returns the number of rows for which the supplied expression(s) are unique and non-NULL. Execution of this can be optimized with hive.optimize.distinct.rewrite.'
      },
      stddev_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev_pop(col)',
        draggable: 'stddev_pop()',
        description: 'Returns the standard deviation of a numeric column in the group.'
      },
      stddev_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev_samp(col)',
        draggable: 'stddev_samp()',
        description: 'Returns the unbiased sample standard deviation of a numeric column in the group.'
      },
      sum: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'sum(col)',
        draggable: 'sum()',
        description: 'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'
      },
      max: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'max(col)',
        draggable: 'max()',
        description: 'Returns the maximum value of the column in the group.'
      },
      min: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'min(col)',
        draggable: 'min()',
        description: 'Returns the minimum of the column in the group.'
      },
      corr: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'corr(col1, col2)',
        draggable: 'corr()',
        description: 'Returns the Pearson coefficient of correlation of a pair of a numeric columns in the group.'
      },
      covar_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'covar_pop(col1, col2)',
        draggable: 'covar_pop()',
        description: 'Returns the population covariance of a pair of numeric columns in the group.'
      },
      covar_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'covar_samp(col1, col2)',
        draggable: 'covar_samp()',
        description: 'Returns the sample covariance of a pair of a numeric columns in the group.'
      },
      collect_set: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'T'}]],
        signature: 'collect_set(col)',
        draggable: 'collect_set()',
        description: 'Returns a set of objects with duplicate elements eliminated.'
      },
      collect_list: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'T'}]],
        signature: 'collect_list(col)',
        draggable: 'collect_list()',
        description: 'Returns a list of objects with duplicates. (As of Hive 0.13.0.)'
      },
      histogram_numeric: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'T'}], [{type: 'INT'}]],
        signature: 'array<struct {\'x\', \'y\'}> histogram_numeric(col, b)',
        draggable: 'array<struct {\'x\', \'y\'}> histogram_numeric()',
        description: 'Computes a histogram of a numeric column in the group using b non-uniformly spaced bins. The output is an array of size b of double-valued (x,y) coordinates that represent the bin centers and heights'
      },
      ntile: {
        returnTypes: ['INT'],
        arguments: [[{type: 'INT'}]],
        signature: 'ntile(INT x)',
        draggable: 'ntile()',
        description: 'Divides an ordered partition into x groups called buckets and assigns a bucket number to each row in the partition. This allows easy calculation of tertiles, quartiles, deciles, percentiles and other common summary statistics. (As of Hive 0.11.0.)'
      },
      percentile: {
        returnTypes: ['DOUBLE', 'ARRAY'],
        arguments: [[{type: 'BIGINT'}], [{type: 'ARRAY'}, {type: 'DOUBLE'}]],
        signature: 'percentile(BIGINT col, p), array<DOUBLE> percentile(BIGINT col, array(p1 [, p2]...))',
        draggable: 'percentile()',
        description: 'Returns the exact pth percentile (or percentiles p1, p2, ..) of a column in the group (does not work with floating point types). p must be between 0 and 1. NOTE: A true percentile can only be computed for integer values. Use PERCENTILE_APPROX if your input is non-integral.'
      },
      percentile_approx: {
        returnTypes: ['DOUBLE', 'ARRAY'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}, {type: 'ARRAY'}], [{type: 'BIGINT', optional: true}]],
        signature: 'percentile_approx(DOUBLE col, p, [, B]), array<DOUBLE> percentile_approx(DOUBLE col, array(p1 [, p2]...), [, B])',
        draggable: 'percentile_approx()',
        description: 'Returns an approximate pth percentile (or percentiles p1, p2, ..) of a numeric column (including floating point types) in the group. The B parameter controls approximation accuracy at the cost of memory. Higher values yield better approximations, and the default is 10,000. When the number of distinct values in col is smaller than B, this gives an exact percentile value.'
      },
      variance: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'variance(col)',
        draggable: 'variance()',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'var_pop(col)',
        draggable: 'var_pop()',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'var_samp(col)',
        draggable: 'var_samp()',
        description: 'Returns the unbiased sample variance of a numeric column in the group.'
      },
      regr_avgx: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_avgx(T independent, T dependent)',
        draggable: 'regr_avgx()',
        description: 'Equivalent to avg(dependent). As of Hive 2.2.0.'
      },
      regr_avgy: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_avgy(T independent, T dependent)',
        draggable: 'regr_avgy()',
        description: 'Equivalent to avg(dependent). As of Hive 2.2.0.'
      },
      regr_count: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_count(T independent, T dependent)',
        draggable: 'regr_count()',
        description: 'Returns the number of non-null pairs used to fit the linear regression line. As of Hive 2.2.0.'
      },
      regr_intercept: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_intercept(T independent, T dependent)',
        draggable: 'regr_intercept()',
        description: 'Returns the y-intercept of the linear regression line, i.e. the value of b in the equation dependent = a * independent + b. As of Hive 2.2.0.'
      },
      regr_r2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_r2(T independent, T dependent)',
        draggable: 'regr_r2()',
        description: 'Returns the coefficient of determination for the regression. As of Hive 2.2.0.'
      },
      regr_slope: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_slope(T independent, T dependent)',
        draggable: 'regr_slope()',
        description: 'Returns the slope of the linear regression line, i.e. the value of a in the equation dependent = a * independent + b. As of Hive 2.2.0.'
      },
      regr_sxx: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_sxx(T independent, T dependent)',
        draggable: 'regr_sxx()',
        description: 'Equivalent to regr_count(independent, dependent) * var_pop(dependent). As of Hive 2.2.0.'
      },
      regr_sxy: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_sxy(T independent, T dependent)',
        draggable: 'regr_sxy()',
        description: 'Equivalent to regr_count(independent, dependent) * covar_pop(independent, dependent). As of Hive 2.2.0.'
      },
      regr_syy: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'regr_syy(T independent, T dependent)',
        draggable: 'regr_syy()',
        description: 'Equivalent to regr_count(independent, dependent) * var_pop(independent). As of Hive 2.2.0.'
      }
    },
    impala: {
      appx_median: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'appx_median([DISTINCT|ALL] T col)',
        draggable: 'appx_median()',
        description: 'An aggregate function that returns a value that is approximately the median (midpoint) of values in the set of input values.'
      },
      avg: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'avg([DISTINCT|ALL] col)',
        draggable: 'avg()',
        description: 'An aggregate function that returns the average value from a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to AVG are NULL, AVG returns NULL.'
      },
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'count([DISTINCT|ALL] col)',
        draggable: 'count()',
        description: 'An aggregate function that returns the number of rows, or the number of non-NULL rows.'
      },
      max: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'max([DISTINCT | ALL] T col)',
        draggable: 'max()',
        description: 'An aggregate function that returns the maximum value from a set of numbers. Opposite of the MIN function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MAX are NULL, MAX returns NULL.'
      },
      min: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'min([DISTINCT | ALL] T col)',
        draggable: 'min()',
        description: 'An aggregate function that returns the minimum value from a set of numbers. Opposite of the MAX function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, MIN returns NULL.'
      },
      sum: {
        returnTypes: ['BIGINT', 'DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'sum([DISTINCT | ALL] col)',
        draggable: 'sum()',
        description: 'An aggregate function that returns the sum of a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, SUM returns NULL.'
      },
      group_concat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'T'}], [{type: 'STRING', optional: true}]],
        signature: 'group_concat([ALL] col [, separator])',
        draggable: 'group_concat()',
        description: 'An aggregate function that returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values. The default separator is a comma followed by a space.'
      },
      ndv: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'ndv([DISTINCT | ALL] col)',
        draggable: 'ndv()',
        description: 'An aggregate function that returns an approximate value similar to the result of COUNT(DISTINCT col), the "number of distinct values". It is much faster than the combination of COUNT and DISTINCT, and uses a constant amount of memory and thus is less memory-intensive for columns with high cardinality.'
      },
      stddev: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev([DISTINCT | ALL] col)',
        draggable: 'stddev()',
        description: 'Returns the standard deviation of a numeric column in the group.'
      },
      stddev_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev_pop([DISTINCT | ALL] col)',
        draggable: 'stddev_pop()',
        description: 'Returns the population standard deviation of a numeric column in the group.'
      },
      stddev_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev_samp([DISTINCT | ALL] col)',
				draggable: 'stddev_samp()',
        description: 'Returns the unbiased sample standard deviation of a numeric column in the group.'
      },
      variance: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'variance([DISTINCT | ALL] col)',
				draggable: 'variance()',
        description: 'An aggregate function that returns the variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      variance_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'variance_pop([DISTINCT | ALL] col)',
				draggable: 'variance_pop()',
        description: 'An aggregate function that returns the population variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      variance_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'variance_samp([DISTINCT | ALL] col)',
				draggable: 'variance_samp()',
        description: 'An aggregate function that returns the sample variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      var_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'var_pop(col)',
				draggable: 'var_pop()',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'var_samp(col)',
				draggable: 'var_samp()',
        description: 'Returns the unbiased sample variance of a numeric column in the group.'
      }
    }
  };

  var COLLECTION_FUNCTIONS = {
    hive: {
      array_contains: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'ARRAY'}], [{type: 'T'}]],
        signature: 'array_contains(Array<T> a, val)',
				draggable: 'array_contains()',
        description: 'Returns TRUE if the array contains value.'
      },
      map_keys: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'MAP'}]],
        signature: 'array<K.V> map_keys(Map<K.V> a)',
				draggable: 'array<K.V> map_keys()',
        description: 'Returns an unordered array containing the keys of the input map.'
      },
      map_values: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'MAP'}]],
        signature: 'array<K.V> map_values(Map<K.V> a)',
				draggable: 'array<K.V> map_values()',
        description: 'Returns an unordered array containing the values of the input map.'
      },
      size: {
        returnTypes: ['INT'],
        arguments: [[{type: 'ARRAY'}, {type: 'MAP'}]],
        signature: 'size(Map<K.V>|Array<T> a)',
				draggable: 'size()',
        description: 'Returns the number of elements in the map or array type.'
      },
      sort_array: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'ARRAY'}]],
        signature: 'sort_array(Array<T> a)',
				draggable: 'sort_array()',
        description: 'Sorts the input array in ascending order according to the natural ordering of the array elements and returns it.'
      }
    },
    impala: {}
  };

  var TYPE_CONVERSION_FUNCTIONS = {
    hive: {
      binary: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'BINARY'}, {type: 'STRING'}]],
        signature: 'binary(BINARY|STRING a)',
				draggable: 'binary()',
        description: 'Casts the parameter into a binary.'
      },
      cast: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'cast(a as T)',
				draggable: 'cast()',
        description: 'Converts the results of the expression expr to type T. For example, cast(\'1\' as BIGINT) will convert the string \'1\' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string.'
      }
    },
    impala: {
      cast: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }]],
        signature: 'cast(a as T)',
				draggable: 'cast()',
        description: 'Converts the results of the expression expr to type T. For example, cast(\'1\' as BIGINT) will convert the string \'1\' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string.'
      },
      typeof: {
        returnTypes: ['STRING'],
        arguments: [[{ type: 'T' }]],
        signature: 'typeof(T a)',
        draggable: 'typeof()',
        description: 'Returns the name of the data type corresponding to an expression. For types with extra attributes, such as length for CHAR and VARCHAR, or precision and scale for DECIMAL, includes the full specification of the type.'
      }
    }
  };

  var DATE_FUNCTIONS = {
    hive: {
      add_months: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}], [{type: 'INT'}]],
        signature: 'add_months(DATE|STRING|TIMESTAMP start_date, INT num_months)',
				draggable: 'add_months()',
        description: 'Returns the date that is num_months after start_date (as of Hive 1.1.0). start_date is a string, date or timestamp. num_months is an integer. The time part of start_date is ignored. If start_date is the last day of the month or if the resulting month has fewer days than the day component of start_date, then the result is the last day of the resulting month. Otherwise, the result has the same day component as start_date.'
      },
      current_date: {
        returnTypes: ['DATE'],
        arguments: [],
        signature: 'current_date',
        draggable: 'current_date',
        description: 'Returns the current date at the start of query evaluation (as of Hive 1.2.0). All calls of current_date within the same query return the same value.'
      },
      current_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'current_timestamp()',
				draggable: 'current_timestamp()',
        description: 'Returns the current timestamp at the start of query evaluation (as of Hive 1.2.0). All calls of current_timestamp within the same query return the same value.'
      },
      datediff: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'datediff(STRING enddate, STRING startdate)',
				draggable: 'datediff()',
        description: 'Returns the number of days from startdate to enddate: datediff(\'2009-03-01\', \'2009-02-27\') = 2.'
      },
      date_add: {
        returnTypes: ['T'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}], [{type: 'INT'}]],
        signature: 'date_add(DATE startdate, INT days)',
				draggable: 'date_add()',
        description: 'Adds a number of days to startdate: date_add(\'2008-12-31\', 1) = \'2009-01-01\'. T = pre 2.1.0: STRING, 2.1.0 on: DATE'
      },
      date_format: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'date_format(DATE|TIMESTAMP|STRING ts, STRING fmt)',
				draggable: 'date_format()',
        description: 'Converts a date/timestamp/string to a value of string in the format specified by the date format fmt (as of Hive 1.2.0). Supported formats are Java SimpleDateFormat formats – https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html. The second argument fmt should be constant. Example: date_format(\'2015-04-08\', \'y\') = \'2015\'.'
      },
      date_sub: {
        returnTypes: ['T'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}], [{type: 'INT'}]],
        signature: 'date_sub(DATE startdate, INT days)',
				draggable: 'date_sub()',
        description: 'Subtracts a number of days to startdate: date_sub(\'2008-12-31\', 1) = \'2008-12-30\'. T = pre 2.1.0: STRING, 2.1.0 on: DATE'
      },
      day: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'day(STRING date)',
				draggable: 'day()',
        description: 'Returns the day part of a date or a timestamp string: day(\'1970-11-01 00:00:00\') = 1, day(\'1970-11-01\') = 1.'
      },
      dayofmonth: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'dayofmonth(STRING date)',
				draggable: 'dayofmonth()',
        description: 'Returns the day part of a date or a timestamp string: dayofmonth(\'1970-11-01 00:00:00\') = 1, dayofmonth(\'1970-11-01\') = 1.'
      },
      extract: {
        returnTypes: ['INT'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'extract(field FROM source)',
        draggable: 'extract()',
        description: 'Retrieve fields such as days or hours from source (as of Hive 2.2.0). Source must be a date, timestamp, interval or a string that can be converted into either a date or timestamp. Supported fields include: day, dayofweek, hour, minute, month, quarter, second, week and year.'
      },
      from_unixtime: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'BIGINT'}], [{type: 'STRING', optional: true}]],
        signature: 'from_unixtime(BIGINT unixtime [, STRING format])',
				draggable: 'from_unixtime()',
        description: 'Converts time string in format yyyy-MM-dd HH:mm:ss to Unix timestamp (in seconds), using the default timezone and the default locale, return 0 if fail: unix_timestamp(\'2009-03-20 11:30:01\') = 1237573801'
      },
      from_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'T'}], [{type: 'STRING'}]],
        signature: 'from_utc_timestamp(T a, STRING timezone)',
				draggable: 'from_utc_timestamp()',
        description: 'Assumes given timestamp is UTC and converts to given timezone (as of Hive 0.8.0). For example, from_utc_timestamp(\'1970-01-01 08:00:00\',\'PST\') returns 1970-01-01 00:00:00'
      },
      hour: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'hour(STRING date)',
				draggable: 'hour()',
        description: 'Returns the hour of the timestamp: hour(\'2009-07-30 12:58:59\') = 12, hour(\'12:58:59\') = 12.'
      },
      last_day: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'last_day(STRING date)',
				draggable: 'last_day()',
        description: 'Returns the last day of the month which the date belongs to (as of Hive 1.1.0). date is a string in the format \'yyyy-MM-dd HH:mm:ss\' or \'yyyy-MM-dd\'. The time part of date is ignored.'
      },
      minute: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'minute(STRING date)',
				draggable: 'minute()',
        description: 'Returns the minute of the timestamp.'
      },
      month: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'month(STRING date)',
				draggable: 'month()',
        description: 'Returns the month part of a date or a timestamp string: month(\'1970-11-01 00:00:00\') = 11, month(\'1970-11-01\') = 11.'
      },
      months_between: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}], [{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}]],
        signature: 'months_between(DATE|TIMESTAMP|STRING date1, DATE|TIMESTAMP|STRING date2)',
				draggable: 'months_between()',
        description: 'Returns number of months between dates date1 and date2 (as of Hive 1.2.0). If date1 is later than date2, then the result is positive. If date1 is earlier than date2, then the result is negative. If date1 and date2 are either the same days of the month or both last days of months, then the result is always an integer. Otherwise the UDF calculates the fractional portion of the result based on a 31-day month and considers the difference in time components date1 and date2. date1 and date2 type can be date, timestamp or string in the format \'yyyy-MM-dd\' or \'yyyy-MM-dd HH:mm:ss\'. The result is rounded to 8 decimal places. Example: months_between(\'1997-02-28 10:30:00\', \'1996-10-30\') = 3.94959677'
      },
      next_day: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'next_day(STRING start_date, STRING day_of_week)',
				draggable: 'next_day()',
        description: 'Returns the first date which is later than start_date and named as day_of_week (as of Hive 1.2.0). start_date is a string/date/timestamp. day_of_week is 2 letters, 3 letters or full name of the day of the week (e.g. Mo, tue, FRIDAY). The time part of start_date is ignored. Example: next_day(\'2015-01-14\', \'TU\') = 2015-01-20.'
      },
      quarter: {
        returnTypes: ['INT'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}]],
        signature: 'quarter(DATE|TIMESTAMP|STRING a)',
        draggable: 'quarter()',
        description: 'Returns the quarter of the year for a date, timestamp, or string in the range 1 to 4. Example: quarter(\'2015-04-08\') = 2.'
      },
      second: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'second(STRING date)',
				draggable: 'second()',
        description: 'Returns the second of the timestamp.'
      },
      to_date: {
        returnTypes: ['T'],
        arguments: [[{type: 'STRING'}]],
        signature: 'to_date(STRING timestamp)',
				draggable: 'to_date()',
        description: 'Returns the date part of a timestamp string, example to_date(\'1970-01-01 00:00:00\'). T = pre 2.1.0: STRING 2.1.0 on: DATE'
      },
      to_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'T'}], [{type: 'STRING'}]],
        signature: 'to_utc_timestamp(T a, STRING timezone)',
				draggable: 'to_utc_timestamp()',
        description: 'Assumes given timestamp is in given timezone and converts to UTC (as of Hive 0.8.0). For example, to_utc_timestamp(\'1970-01-01 00:00:00\',\'PST\') returns 1970-01-01 08:00:00.'
      },
      trunc: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'trunc(STRING date, STRING format)',
				draggable: 'trunc()',
        description: 'Returns date truncated to the unit specified by the format (as of Hive 1.2.0). Supported formats: MONTH/MON/MM, YEAR/YYYY/YY. Example: trunc(\'2015-03-17\', \'MM\') = 2015-03-01.'
      },
      unix_timestamp: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'STRING', optional: true}], [{type: 'STRING', optional: true}]],
        signature: 'unix_timestamp([STRING date [, STRING pattern]])',
				draggable: 'unix_timestamp()',
        description: 'Convert time string with given pattern to Unix time stamp (in seconds), return 0 if fail: unix_timestamp(\'2009-03-20\', \'yyyy-MM-dd\') = 1237532400.'
      },
      weekofyear: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'weekofyear(STRING date)',
				draggable: 'weekofyear()',
        description: 'Returns the week number of a timestamp string: weekofyear(\'1970-11-01 00:00:00\') = 44, weekofyear(\'1970-11-01\') = 44.'
      },
      year: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'year(STRING date)',
				draggable: 'year()',
        description: 'Returns the year part of a date or a timestamp string: year(\'1970-01-01 00:00:00\') = 1970, year(\'1970-01-01\') = 1970'
      }
    },
    impala: {
      add_months: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'add_months(TIMESTAMP date, BIGINT|INT months)',
				draggable: 'add_months()',
        description: 'Returns the specified date and time plus some number of months.'
      },
      adddate: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'adddate(TIMESTAMP startdate, BIGINT|INT days)',
				draggable: 'adddate()',
        description: 'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
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
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'INT'}]],
        signature: 'date_add(TIMESTAMP startdate, INT days), date_add(TIMESTAMP startdate, interval_expression)',
        draggable: 'date_add()',
        description: 'Adds a specified number of days to a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.'
      },
      date_part: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'STRING'}], [{type: 'TIMESTAMP'}]],
        signature: 'date_part(STRING unit, TIMESTAMP timestamp)',
				draggable: 'date_part()',
        description: 'Similar to EXTRACT(), with the argument order reversed. Supports the same date and time units as EXTRACT(). For compatibility with SQL code containing vendor extensions.'
      },
      date_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'INT'}]],
        signature: 'date_sub(TIMESTAMP startdate, INT days), date_sub(TIMESTAMP startdate, interval_expression)',
        draggable: 'date_sub()',
        description: 'Subtracts a specified number of days from a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.'
      },
      datediff: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'TIMESTAMP'}]],
        signature: 'datediff(TIMESTAMP enddate, TIMESTAMP startdate)',
				draggable: 'datediff()',
        description: 'Returns the number of days between two TIMESTAMP values.'
      },
      day: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'day(TIMESTAMP date)',
				draggable: 'day()',
        description: 'Returns the day field from the date portion of a TIMESTAMP. The value represents the day of the month, therefore is in the range 1-31, or less for months without 31 days.'
      },
      dayname: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'dayname(TIMESTAMP date)',
				draggable: 'dayname()',
        description: 'Returns the day field from a TIMESTAMP value, converted to the string corresponding to that day name. The range of return values is \'Sunday\' to \'Saturday\'. Used in report-generating queries, as an alternative to calling dayofweek() and turning that numeric return value into a string using a CASE expression.'
      },
      dayofmonth: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'dayofmonth(TIMESTAMP date)',
				draggable: 'dayofmonth()',
        description: 'Returns the day field from the date portion of a TIMESTAMP. The value represents the day of the month, therefore is in the range 1-31, or less for months without 31 days.'
      },
      dayofweek: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'dayofweek(TIMESTAMP date)',
				draggable: 'dayofweek()',
        description: 'Returns the day field from the date portion of a TIMESTAMP, corresponding to the day of the week. The range of return values is 1 (Sunday) to 7 (Saturday).'
      },
      dayofyear: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'dayofyear(TIMESTAMP date)',
				draggable: 'dayofyear()',
        description: 'Returns the day field from a TIMESTAMP value, corresponding to the day of the year. The range of return values is 1 (January 1) to 366 (December 31 of a leap year).'
      },
      days_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'days_add(TIMESTAMP startdate, BIGINT|INT days)',
				draggable: 'days_add()',
        description: 'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      days_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'days_sub(TIMESTAMP startdate, BIGINT|INT days)',
				draggable: 'days_sub()',
        description: 'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      extract: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'extract(TIMESTAMP date, STRING unit), extract(STRING unit FROM TIMESTAMP date)',
        draggable: 'extract()',
        description: 'Returns one of the numeric date or time fields from a TIMESTAMP value.'
      },
      from_timestamp: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'from_timestamp(TIMESTAMP val, STRING format)',
        draggable: 'from_timestamp()',
        description: 'Converts a specified timestamp to a string with the given format. Example: from_timestamp(cast(\'1999-01-01 10:10:10\' as timestamp), \'yyyy-MM-dd\')" results in "1999-01-01"'
      },
      from_unixtime: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}], [{type: 'STRING', optional: true}]],
        signature: 'from_unixtime(BIGINT unixtime [, STRING format])',
				draggable: 'from_unixtime()',
        description: 'Converts the number of seconds from the Unix epoch to the specified time into a string in the local time zone.'
      },
      from_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'from_utc_timestamp(TIMESTAMP date, STRING timezone)',
				draggable: 'from_utc_timestamp()',
        description: 'Converts a specified UTC timestamp value into the appropriate value for a specified time zone.'
      },
      hour: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'hour(TIMESTAMP date)',
				draggable: 'hour()',
        description: 'Returns the hour field from a TIMESTAMP field.'
      },
      hours_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'hours_add(TIMESTAMP date, BIGINT|INT hours)',
				draggable: 'hours_add()',
        description: 'Returns the specified date and time plus some number of hours.'
      },
      hours_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'hours_sub(TIMESTAMP date, BIGINT|INT hours)',
				draggable: 'hours_sub()',
        description: 'Returns the specified date and time minus some number of hours.'
      },
      int_months_between: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'TIMESTAMP'}]],
        signature: 'int_months_between(TIMESTAMP newer, TIMESTAMP older)',
        draggable: 'int_months_between()',
        description: 'Returns the number of months between the date portions of two TIMESTAMP values, as an INT representing only the full months that passed.'
      },
      microseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'microseconds_add(TIMESTAMP date, BIGINT|INT microseconds)',
				draggable: 'microseconds_add()',
        description: 'Returns the specified date and time plus some number of microseconds.'
      },
      microseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'microseconds_sub(TIMESTAMP date, BIGINT|INT microseconds)',
				draggable: 'microseconds_sub()',
        description: 'Returns the specified date and time minus some number of microseconds.'
      },
      milliseconds: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'milliseconds(TIMESTAMP date)',
        draggable: 'milliseconds()',
        description: 'Returns the millisecond portion of a TIMESTAMP value.'
      },
      milliseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'milliseconds_add(TIMESTAMP date, BIGINT|INT milliseconds)',
				draggable: 'milliseconds_add()',
        description: 'Returns the specified date and time plus some number of milliseconds.'
      },
      milliseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'milliseconds_sub(TIMESTAMP date, BIGINT|INT milliseconds)',
				draggable: 'milliseconds_sub()',
        description: 'Returns the specified date and time minus some number of milliseconds.'
      },
      minute: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'minute(TIMESTAMP date)',
				draggable: 'minute()',
        description: 'Returns the minute field from a TIMESTAMP value.'
      },
      minutes_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'minutes_add(TIMESTAMP date, BIGINT|INT minutes)',
				draggable: 'minutes_add()',
        description: 'Returns the specified date and time plus some number of minutes.'
      },
      minutes_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'minutes_sub(TIMESTAMP date, BIGINT|INT minutes)',
				draggable: 'minutes_sub()',
        description: 'Returns the specified date and time minus some number of minutes.'
      },
      month: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'month(TIMESTAMP date)',
				draggable: 'month()',
        description: 'Returns the month field, represented as an integer, from the date portion of a TIMESTAMP.'
      },
      months_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'months_add(TIMESTAMP date, BIGINT|INT months)',
				draggable: 'months_add()',
        description: 'Returns the specified date and time plus some number of months.'
      },
      months_between: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'TIMESTAMP'}]],
        signature: 'months_between(TIMESTAMP newer, TIMESTAMP older)',
        draggable: 'months_between()',
        description: 'Returns the number of months between the date portions of two TIMESTAMP values. Can include a fractional part representing extra days in addition to the full months between the dates. The fractional component is computed by dividing the difference in days by 31 (regardless of the month).'
      },
      months_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'months_sub(TIMESTAMP date, BIGINT|INT months)',
				draggable: 'months_sub()',
        description: 'Returns the specified date and time minus some number of months.'
      },
      nanoseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'nanoseconds_add(TIMESTAMP date, BIGINT|INT nanoseconds)',
				draggable: 'nanoseconds_add()',
        description: 'Returns the specified date and time plus some number of nanoseconds.'
      },
      nanoseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'nanoseconds_sub(TIMESTAMP date, BIGINT|INT nanoseconds)',
				draggable: 'nanoseconds_sub()',
        description: 'Returns the specified date and time minus some number of nanoseconds.'
      },
      now: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'now()',
				draggable: 'now()',
        description: 'Returns the current date and time (in the local time zone) as a timestamp value.'
      },
      second: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'second(TIMESTAMP date)',
				draggable: 'second()',
        description: 'Returns the second field from a TIMESTAMP value.'
      },
      seconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'seconds_add(TIMESTAMP date, BIGINT|INT seconds)',
				draggable: 'seconds_add()',
        description: 'Returns the specified date and time plus some number of seconds.'
      },
      seconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'seconds_sub(TIMESTAMP date, BIGINT|INT seconds)',
				draggable: 'seconds_sub()',
        description: 'Returns the specified date and time minus some number of seconds.'
      },
      subdate: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'subdate(TIMESTAMP startdate, BIGINT|INT days)',
				draggable: 'subdate()',
        description: 'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      timeofday: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'timeofday()',
        draggable: 'timeofday()',
        description: 'Returns a string representation of the current date and time, according to the time of the local system, including any time zone designation.'
      },
      timestamp_cmp: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'TIMESTAMP'}]],
        signature: 'timestamp_cmp(TIMESTAMP t1, TIMESTAMP t2)',
        draggable: 'timestamp_cmp()',
        description: 'Tests if one TIMESTAMP value is newer than, older than, or identical to another TIMESTAMP. Returns either -1, 0, 1 or NULL.'
      },
      to_date: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'to_date(TIMESTAMP date)',
				draggable: 'to_date()',
        description: 'Returns a string representation of the date field from a timestamp value.'
      },
      to_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        altArguments: [[{type: 'BIGINT'}]],
        signature: 'to_timestamp([STRING val, STRING format]|[BIGINT val])',
        draggable: 'to_timestamp()',
        description: 'Converts a bigint (delta from the Unix epoch) or a string with the specified format to a timestamp. Example: to_timestamp(\'1970-01-01 00:00:00\', \'yyyy-MM-dd HH:mm:ss\').'
      },
      to_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'to_utc_timestamp(TIMESTAMP date, STRING timezone)',
				draggable: 'to_utc_timestamp()',
        description: 'Converts a specified timestamp value in a specified time zone into the corresponding value for the UTC time zone.'
      },
      trunc: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'trunc(TIMESTAMP date, STRING unit)',
				draggable: 'trunc()',
        description: 'Strips off fields and optionally rounds a TIMESTAMP value. The unit argument value is case-sensitive. This argument string can be one of: SYYYY, YYYY, YEAR, SYEAR, YYY, YY, Y: Year. Q: Quarter. MONTH, MON, MM, RM: Month. WW, W: Same day of the week as the first day of the month. DDD, DD, J: Day. DAY, DY, D: Starting day of the week. (Not necessarily the current day.) HH, HH12, HH24: Hour. A TIMESTAMP value truncated to the hour is always represented in 24-hour notation, even for the HH12 argument string. MI: Minute.'
      },
      unix_timestamp: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING', optional: true}], [{type: 'STRING', optional: true}]],
        altArguments: [[{type: 'TIMESTAMP'}]],
        signature: 'unix_timestamp([STRING datetime [, STRING format]]|[TIMESTAMP datetime])',
				draggable: 'unix_timestamp()',
        description: 'Returns an integer value representing the current date and time as a delta from the Unix epoch, or converts from a specified date and time value represented as a TIMESTAMP or STRING.'
      },
      weekofyear: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'weekofyear(TIMESTAMP date)',
				draggable: 'weekofyear()',
        description: 'Returns the corresponding week (1-53) from the date portion of a TIMESTAMP.'
      },
      weeks_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'weeks_add(TIMESTAMP date, BIGINT|INT weeks)',
				draggable: 'weeks_add()',
        description: 'Returns the specified date and time plus some number of weeks.'
      },
      weeks_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'weeks_sub(TIMESTAMP date, BIGINT|INT weeks)',
				draggable: 'weeks_sub()',
        description: 'Returns the specified date and time minus some number of weeks.'
      },
      year: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'year(TIMESTAMP date)',
				draggable: 'year()',
        description: 'Returns the year field from the date portion of a TIMESTAMP.'
      },
      years_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'years_add(TIMESTAMP date, BIGINT|INT years)',
				draggable: 'years_add()',
        description: 'Returns the specified date and time plus some number of years.'
      },
      years_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'years_sub(TIMESTAMP date, BIGINT|INT years)',
				draggable: 'years_sub()',
        description: 'Returns the specified date and time minus some number of years.'
      }
    }
  };

  var CONDITIONAL_FUNCTIONS = {
    hive: {
      assert_true: {
        returnTypes: ['T'],
        arguments: [[{type: 'BOOLEAN'}]],
        signature: 'assert_true(BOOLEAN condition)',
        draggable: 'assert_true()',
        description: 'Throw an exception if \'condition\' is not true, otherwise return null (as of Hive 0.8.0). For example, select assert_true (2<1).'
      },
      coalesce: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'coalesce(T v1, T v2, ...)',
				draggable: 'coalesce()',
        description: 'Returns the first v that is not NULL, or NULL if all v\'s are NULL.'
      },
      if: {
        returnTypes: ['T'],
        arguments: [[{type: 'BOOLEAN'}], [{type: 'T'}], [{type: 'T'}]],
        signature: 'if(BOOLEAN testCondition, T valueTrue, T valueFalseOrNull)',
				draggable: 'if()',
        description: 'Returns valueTrue when testCondition is true, returns valueFalseOrNull otherwise.'
      },
      isnotnull: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'T'}]],
        signature: 'isnotnull(a)',
				draggable: 'isnotnull()',
        description: 'Returns true if a is not NULL and false otherwise.'
      },
      isnull: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'T'}]],
        signature: 'isnull(a)',
				draggable: 'isnull()',
        description: 'Returns true if a is NULL and false otherwise.'
      },
      nullif: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'nullif(a, b)',
        draggable: 'nullif()',
        description: 'Returns NULL if a=b; otherwise returns a (as of Hive 2.2.0).'
      },
      nvl: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'nvl(T value, T default_value)',
				draggable: 'nvl()',
        description: 'Returns default value if value is null else returns value (as of Hive 0.11).'
      }
    },
    impala: {
      coalesce: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'coalesce(T v1, T v2, ...)',
				draggable: 'coalesce()',
        description: 'Returns the first specified argument that is not NULL, or NULL if all arguments are NULL.'
      },
      decode: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}], [{type: 'T', multiple: true}]],
        signature: 'decode(T expression, T search1, T result1 [, T search2, T result2 ...] [, T default] )',
				draggable: 'decode()',
        description: 'Compares an expression to one or more possible values, and returns a corresponding result when a match is found.'
      },
      if: {
        returnTypes: ['T'],
        arguments: [[{type: 'BOOLEAN'}], [{type: 'T'}], [{type: 'T'}]],
        signature: 'if(BOOLEAN condition, T ifTrue, T ifFalseOrNull)',
				draggable: 'if()',
        description: 'Tests an expression and returns a corresponding result depending on whether the result is true, false, or NULL.'
      },
      ifnull: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'ifnull(T a, T ifNotNull)',
				draggable: 'ifnull()',
        description: 'Alias for the isnull() function, with the same behavior. To simplify porting SQL with vendor extensions to Impala.'
      },
      isfalse: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'BOOLEAN'}]],
        signature: 'isfalse(BOOLEAN condition)',
        draggable: 'isfalse()',
        description: 'Tests if a Boolean expression is false or not. Returns true if so. If the argument is NULL, returns false. Identical to isnottrue(), except it returns the opposite value for a NULL argument.'
      },
      isnotfalse: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'BOOLEAN'}]],
        signature: 'isnotfalse(BOOLEAN condition)',
        draggable: 'isnotfalse()',
        description: 'Tests if a Boolean expression is not false (that is, either true or NULL). Returns true if so. If the argument is NULL, returns true. Identical to istrue(), except it returns the opposite value for a NULL argument.'
      },
      isnottrue: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'BOOLEAN'}]],
        signature: 'isnottrue(BOOLEAN condition)',
        draggable: 'isnottrue()',
        description: 'Tests if a Boolean expression is not true (that is, either false or NULL). Returns true if so. If the argument is NULL, returns true. Identical to isfalse(), except it returns the opposite value for a NULL argument.'
      },
      isnull: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'isnull(T a, T ifNotNull)',
				draggable: 'isnull()',
        description: 'Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument.'
      },
      istrue: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'BOOLEAN'}]],
        signature: 'istrue(BOOLEAN condition)',
        draggable: 'istrue()',
        description: 'Tests if a Boolean expression is true or not. Returns true if so. If the argument is NULL, returns false. Identical to isnotfalse(), except it returns the opposite value for a NULL argument.'
      },
      nonnullvalue: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'T'}]],
        signature: 'nonnullvalue(T expression)',
        draggable: 'nonnullvalue()',
        description: 'Tests if an expression (of any type) is NULL or not. Returns false if so. The converse of nullvalue().'
      },
      nullif: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'nullif(T expr1, T expr2)',
				draggable: 'nullif()',
        description: 'Returns NULL if the two specified arguments are equal. If the specified arguments are not equal, returns the value of expr1. The data types of the expressions must be compatible. You cannot use an expression that evaluates to NULL for expr1; that way, you can distinguish a return value of NULL from an argument value of NULL, which would never match expr2.'
      },
      nullifzero: {
        returnTypes: ['T'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'nullifzero(T numeric_expr)',
				draggable: 'nullifzero()',
        description: 'Returns NULL if the numeric expression evaluates to 0, otherwise returns the result of the expression.'
      },
      nullvalue: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'T'}]],
        signature: 'nullvalue(T expression)',
        draggable: 'nullvalue()',
        description: 'Tests if an expression (of any type) is NULL or not. Returns true if so. The converse of nonnullvalue().'
      },
      nvl: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'nvl(T a, T ifNotNull)',
				draggable: 'nvl()',
        description: 'Alias for the isnull() function. Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument. Equivalent to the nvl() function from Oracle Database or ifnull() from MySQL.'
      },
      nvl2: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}], [{type: 'T'}]],
        signature: 'nvl2(T a, T ifNull, T ifNotNull)',
        draggable: 'nvl2()',
        description: 'Enhanced variant of the nvl() function. Tests an expression and returns different result values depending on whether it is NULL or not. If the first argument is NULL, returns the second argument. If the first argument is not NULL, returns the third argument. Equivalent to the nvl2() function from Oracle.'
      },
      zeroifnull: {
        returnTypes: ['T'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'zeroifnull(T numeric_expr)',
				draggable: 'zeroifnull()',
        description: 'Returns 0 if the numeric expression evaluates to NULL, otherwise returns the result of the expression.'
      }
    }
  };

  var STRING_FUNCTIONS = {
    hive: {
      ascii: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ascii(STRING str)',
				draggable: 'ascii()',
        description: 'Returns the numeric value of the first character of str.'
      },
      base64: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BINARY'}]],
        signature: 'base64(BINARY bin)',
				draggable: 'base64()',
        description: 'Converts the argument from binary to a base 64 string (as of Hive 0.12.0).'
      },
      chr: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}, {type: 'DOUBLE'}]],
        signature: 'chr(BIGINT|DOUBLE a)',
        draggable: 'chr()',
        description: 'Returns the ASCII character having the binary equivalent to a (as of Hive 1.3.0 and 2.1.0). If a is larger than 256 the result is equivalent to chr(a % 256). Example: select chr(88); returns "X".'
      },
      char_length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'char_length(STRING a)',
        draggable: 'char_length()',
        description: 'Returns the number of UTF-8 characters contained in str (as of Hive 2.2.0). This is shorthand for character_length.'
      },
      character_length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'character_length(STRING a)',
        draggable: 'character_length()',
        description: 'Returns the number of UTF-8 characters contained in str (as of Hive 2.2.0). The function char_length is shorthand for this function.'
      },
      concat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING', multiple: true}, {type: 'BINARY', multiple: true}]],
        signature: 'concat(STRING|BINARY a, STRING|BINARY b...)',
				draggable: 'concat()',
        description: 'Returns the string or bytes resulting from concatenating the strings or bytes passed in as parameters in order. For example, concat(\'foo\', \'bar\') results in \'foobar\'. Note that this function can take any number of input strings.'
      },
      concat_ws: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        altArguments: [[{type: 'STRING'}], [{type: 'ARRAY'}]],
        signature: 'concat_ws(STRING sep, STRING a, STRING b...), concat_ws(STRING sep, Array<STRING>)',
        draggable: 'concat_ws()',
        description: 'Like concat(), but with custom separator SEP.'
      },
      context_ngrams: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'ARRAY'}], [{type: 'ARRAY'}], [{type: 'INT'}], [{type: 'INT'}]],
        signature: 'array<struct<STRING,DOUBLE>> context_ngrams(Array<Array<STRING>>, Array<STRING>, INT k, INT pf)',
				draggable: 'array<struct<STRING,DOUBLE>> context_ngrams()',
        description: 'Returns the top-k contextual N-grams from a set of tokenized sentences, given a string of "context".'
      },
      decode: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BINARY'}], [{type: 'STRING'}]],
        signature: 'decode(BINARY bin, STRING charset)',
				draggable: 'decode()',
        description: 'Decodes the first argument into a String using the provided character set (one of \'US-ASCII\', \'ISO-8859-1\', \'UTF-8\', \'UTF-16BE\', \'UTF-16LE\', \'UTF-16\'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)'
      },
      elt: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'INT'}], [{type: 'STRING' , multiple: true }]],
        signature: 'elt(INT n, STRING str, STRING str1, ...])',
        draggable: 'elt()',
        description: 'Return string at index number. For example elt(2,\'hello\',\'world\') returns \'world\'. Returns NULL if N is less than 1 or greater than the number of arguments.'
      },
      encode: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'encode(STRING src, STRING charset)',
				draggable: 'encode()',
        description: 'Encodes the first argument into a BINARY using the provided character set (one of \'US-ASCII\', \'ISO-8859-1\', \'UTF-8\', \'UTF-16BE\', \'UTF-16LE\', \'UTF-16\'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)'
      },
      field: {
        returnTypes: ['INT'],
        arguments: [[{type: 'T' , multiple: true }]],
        signature: 'field(T val, T val1, ...])',
        draggable: 'field()',
        description: 'Returns the index of val in the val1,val2,val3,... list or 0 if not found. For example field(\'world\',\'say\',\'hello\',\'world\') returns 3. All primitive types are supported, arguments are compared using str.equals(x). If val is NULL, the return value is 0.'
      },
      find_in_set: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'find_in_set(STRING str, STRING strList)',
				draggable: 'find_in_set()',
        description: 'Returns the first occurance of str in strList where strList is a comma-delimited string. Returns null if either argument is null. Returns 0 if the first argument contains any commas. For example, find_in_set(\'ab\', \'abc,b,ab,c,def\') returns 3.'
      },
      format_number: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'NUMBER'}], [{type: 'INT'}]],
        signature: 'format_number(NUMBER x, INT d)',
				draggable: 'format_number()',
        description: 'Formats the number X to a format like \'#,###,###.##\', rounded to D decimal places, and returns the result as a string. If D is 0, the result has no decimal point or fractional part. (As of Hive 0.10.0; bug with float types fixed in Hive 0.14.0, decimal type support added in Hive 0.14.0)'
      },
      get_json_object: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'get_json_object(STRING json_string, STRING path)',
				draggable: 'get_json_object()',
        description: 'Extracts json object from a json string based on json path specified, and returns json string of the extracted json object. It will return null if the input json string is invalid. NOTE: The json path can only have the characters [0-9a-z_], i.e., no upper-case or special characters. Also, the keys *cannot start with numbers.* This is due to restrictions on Hive column names.'
      },
      initcap: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'initcap(STRING a)',
				draggable: 'initcap()',
        description: 'Returns string, with the first letter of each word in uppercase, all other letters in lowercase. Words are delimited by whitespace. (As of Hive 1.1.0.)'
      },
      instr: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'instr(STRING str, STRING substr)',
				draggable: 'instr()',
        description: 'Returns the position of the first occurrence of substr in str. Returns null if either of the arguments are null and returns 0 if substr could not be found in str. Be aware that this is not zero based. The first character in str has index 1.'
      },
      in_file: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'in_file(STRING str, STRING filename)',
				draggable: 'in_file()',
        description: 'Returns true if the string str appears as an entire line in filename.'
      },
      length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'length(STRING a)',
				draggable: 'length()',
        description: 'Returns the length of the string.'
      },
      levenshtein: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'levenshtein(STRING a, STRING b)',
				draggable: 'levenshtein()',
        description: 'Returns the Levenshtein distance between two strings (as of Hive 1.2.0). For example, levenshtein(\'kitten\', \'sitting\') results in 3.'
      },
      lcase: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'lcase(STRING a)',
				draggable: 'lcase()',
        description: 'Returns the string resulting from converting all characters of B to lower case. For example, lcase(\'fOoBaR\') results in \'foobar\'.'
      },
      locate: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT', optional: true}]],
        signature: 'locate(STRING substr, STRING str [, INT pos])',
				draggable: 'locate()',
        description: 'Returns the position of the first occurrence of substr in str after position pos.'
      },
      lower: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'lower(STRING a)',
				draggable: 'lower()',
        description: 'Returns the string resulting from converting all characters of B to lower case. For example, lower(\'fOoBaR\') results in \'foobar\'.'
      },
      lpad: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'STRING'}]],
        signature: 'lpad(STRING str, INT len, STRING pad)',
				draggable: 'lpad()',
        description: 'Returns str, left-padded with pad to a length of len.'
      },
      ltrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ltrim(STRING a)',
				draggable: 'ltrim()',
        description: 'Returns the string resulting from trimming spaces from the beginning(left hand side) of A. For example, ltrim(\' foobar \') results in \'foobar \'.'
      },
      ngrams: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'ARRAY'}], [{type: 'INT'}], [{type: 'INT'}], [{type: 'INT'}]],
        signature: 'array<struct<STRING, DOUBLE>> ngrams(Array<Array<STRING>> a, INT n, INT k, INT pf)',
				draggable: 'array<struct<STRING, DOUBLE>> ngrams()',
        description: 'Returns the top-k N-grams from a set of tokenized sentences, such as those returned by the sentences() UDAF.'
      },
      octet_length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'octet_length(STRING a)',
        draggable: 'octet_length()',
        description: 'Returns the number of octets required to hold the string str in UTF-8 encoding (since Hive 2.2.0). Note that octet_length(str) can be larger than character_length(str).'
      },
      parse_url: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])',
				draggable: 'parse_url()',
        description: 'Returns the specified part from the URL. Valid values for partToExtract include HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, and USERINFO. For example, parse_url(\'http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1\', \'HOST\') returns \'facebook.com\'. Also a value of a particular key in QUERY can be extracted by providing the key as the third argument, for example, parse_url(\'http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1\', \'QUERY\', \'k1\') returns \'v1\'.'
      },
      printf: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'T', multiple: true}]],
        signature: 'printf(STRING format, Obj... args)',
				draggable: 'printf()',
        description: 'Returns the input formatted according do printf-style format strings (as of Hive 0.9.0).'
      },
      regexp_extract: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'regexp_extract(STRING subject, STRING pattern, INT index)',
				draggable: 'regexp_extract()',
        description: 'Returns the string extracted using the pattern. For example, regexp_extract(\'foothebar\', \'foo(.*?)(bar)\', 2) returns \'bar.\' Note that some care is necessary in using predefined character classes: using \'\\s\' as the second argument will match the letter s; \'\\\\s\' is necessary to match whitespace, etc. The \'index\' parameter is the Java regex Matcher group() method index.'
      },
      regexp_replace: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'regexp_replace(STRING initial_string, STRING pattern, STRING replacement)',
				draggable: 'regexp_replace()',
        description: 'Returns the string resulting from replacing all substrings in INITIAL_STRING that match the java regular expression syntax defined in PATTERN with instances of REPLACEMENT. For example, regexp_replace("foobar", "oo|ar", "") returns \'fb.\' Note that some care is necessary in using predefined character classes: using \'\\s\' as the second argument will match the letter s; \'\\\\s\' is necessary to match whitespace, etc.'
      },
      repeat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'repeat(STRING str, INT n)',
				draggable: 'repeat()',
        description: 'Repeats str n times.'
      },
      replace: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'replace(STRING a, STRING old, STRING new)',
        draggable: 'replace()',
        description: 'Returns the string a with all non-overlapping occurrences of old replaced with new (as of Hive 1.3.0 and 2.1.0). Example: select replace("ababab", "abab", "Z"); returns "Zab".'
      },
      reverse: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'reverse(STRING a)',
				draggable: 'reverse()',
        description: 'Returns the reversed string.'
      },
      rpad: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'STRING'}]],
        signature: 'rpad(STRING str, INT len, STRING pad)',
				draggable: 'rpad()',
        description: 'Returns str, right-padded with pad to a length of len.'
      },
      rtrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'rtrim(STRING a)',
				draggable: 'rtrim()',
        description: 'Returns the string resulting from trimming spaces from the end(right hand side) of A. For example, rtrim(\' foobar \') results in \' foobar\'.'
      },
      sentences: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'array<array<STRING>> sentences(STRING str, STRING lang, STRING locale)',
				draggable: 'array<array<STRING>> sentences()',
        description: 'Tokenizes a string of natural language text into words and sentences, where each sentence is broken at the appropriate sentence boundary and returned as an array of words. The \'lang\' and \'locale\' are optional arguments. For example, sentences(\'Hello there! How are you?\') returns ( ("Hello", "there"), ("How", "are", "you") ).'
      },
      soundex: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'soundex(STRING a)',
				draggable: 'soundex()',
        description: 'Returns soundex code of the string (as of Hive 1.2.0). For example, soundex(\'Miller\') results in M460.'
      },
      space: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'INT'}]],
        signature: 'space(INT n)',
				draggable: 'space()',
        description: 'Returns a string of n spaces.'
      },
      split: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'array<STRING> split(STRING str, STRING pat)',
				draggable: 'array<STRING> split()',
        description: 'Splits str around pat (pat is a regular expression).'
      },
      str_to_map: {
        returnTypes: ['MAP'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', optional: true}], [{type: 'STRING', optional: true}]],
        signature: 'map<STRING,STRING> str_to_map(STRING [, STRING delimiter1, STRING delimiter2])',
				draggable: 'map<STRING,STRING> str_to_map()',
        description: 'Splits text into key-value pairs using two delimiters. Delimiter1 separates text into K-V pairs, and Delimiter2 splits each K-V pair. Default delimiters are \',\' for delimiter1 and \'=\' for delimiter2.'
      },
      substr: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}], [{type: 'INT'}], [{type: 'INT', optional: true}]],
        signature: 'substr(STRING|BINARY A, INT start [, INT len]) ',
        draggable: 'substr()',
        description: 'Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr(\'foobar\', 4) results in \'bar\''
      },
      substring: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}], [{type: 'INT'}], [{type: 'INT', optional: true}]],
        signature: 'substring(STRING|BINARY a, INT start [, INT len])',
				draggable: 'substring()',
        description: 'Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr(\'foobar\', 4) results in \'bar\''
      },
      substring_index: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'substring_index(STRING a, STRING delim, INT count)',
				draggable: 'substring_index()',
        description: 'Returns the substring from string A before count occurrences of the delimiter delim (as of Hive 1.3.0). If count is positive, everything to the left of the final delimiter (counting from the left) is returned. If count is negative, everything to the right of the final delimiter (counting from the right) is returned. Substring_index performs a case-sensitive match when searching for delim. Example: substring_index(\'www.apache.org\', \'.\', 2) = \'www.apache\'.'
      },
      translate: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'CHAR'}, {type: 'VARCHAR'}], [{type: 'STRING'}, {type: 'CHAR'}, {type: 'VARCHAR'}], [{type: 'STRING'}, {type: 'CHAR'}, {type: 'VARCHAR'}]],
        signature: 'translate(STRING|CHAR|VARCHAR input, STRING|CHAR|VARCHAR from, STRING|CHAR|VARCHAR to)',
				draggable: 'translate()',
        description: 'Translates the input string by replacing the characters present in the from string with the corresponding characters in the to string. This is similar to the translate function in PostgreSQL. If any of the parameters to this UDF are NULL, the result is NULL as well. (Available as of Hive 0.10.0, for string types) Char/varchar support added as of Hive 0.14.0.'
      },
      trim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'trim(STRING a)',
				draggable: 'trim()',
        description: 'Returns the string resulting from trimming spaces from both ends of A. For example, trim(\' foobar \') results in \'foobar\''
      },
      ucase: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ucase(STRING a)',
				draggable: 'ucase()',
        description: 'Returns the string resulting from converting all characters of A to upper case. For example, ucase(\'fOoBaR\') results in \'FOOBAR\'.'
      },
      unbase64: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'STRING'}]],
        signature: 'unbase64(STRING a)',
				draggable: 'unbase64()',
        description: 'Converts the argument from a base 64 string to BINARY. (As of Hive 0.12.0.)'
      },
      upper: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'upper(STRING a)',
				draggable: 'upper()',
        description: 'Returns the string resulting from converting all characters of A to upper case. For example, upper(\'fOoBaR\') results in \'FOOBAR\'.'
      }
    },
    impala: {
      ascii: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ascii(STRING str)',
				draggable: 'ascii()',
        description: 'Returns the numeric ASCII code of the first character of the argument.'
      },
      btrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        signature: 'btrim(STRING str [, STRING chars_to_trim])',
        draggable: 'btrim()',
        description: 'Removes all instances of one or more characters from the start and end of a STRING value. By default, removes only spaces. If a non-NULL optional second argument is specified, the function removes all occurrences of characters in that second argument from the beginning and end of the string.'
      },
      char_length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'char_length(STRING a)',
				draggable: 'char_length()',
        description: 'Returns the length in characters of the argument string. Aliases for the length() function.'
      },
      character_length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'character_length(STRING a)',
				draggable: 'character_length()',
        description: 'Returns the length in characters of the argument string. Aliases for the length() function.'
      },
      chr: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'INT'}]],
        signature: 'chr(INT character_code)',
        draggable: 'chr()',
        description: 'Returns a character specified by a decimal code point value. The interpretation and display of the resulting character depends on your system locale. Because consistent processing of Impala string values is only guaranteed for values within the ASCII range, only use this function for values corresponding to ASCII characters. In particular, parameter values greater than 255 return an empty string.'
      },
      concat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        signature: 'concat(STRING a, STRING b...)',
				draggable: 'concat()',
        description: 'Returns a single string representing all the argument values joined together.'
      },
      concat_ws: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        signature: 'concat_ws(STRING sep, STRING a, STRING b...)',
				draggable: 'concat_ws()',
        description: 'Returns a single string representing the second and following argument values joined together, delimited by a specified separator.'
      },
      find_in_set: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'find_in_set(STRING str, STRING strList)',
				draggable: 'find_in_set()',
        description: 'Returns the position (starting from 1) of the first occurrence of a specified string within a comma-separated string. Returns NULL if either argument is NULL, 0 if the search string is not found, or 0 if the search string contains a comma.'
      },
      group_concat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        signature: 'group_concat(STRING s [, STRING sep])',
				draggable: 'group_concat()',
        description: 'Returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values.'
      },
      initcap: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'initcap(STRING str)',
				draggable: 'initcap()',
        description: 'Returns the input string with the first letter capitalized.'
      },
      instr: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{ type: 'BIGINT', optional: true}], [{ type: 'BIGINT', optional: true}]],
        signature: 'instr(STRING str, STRING substr [, BIGINT position [, BIGINT occurrence]])',
				draggable: 'instr()',
        description: 'Returns the position (starting from 1) of the first occurrence of a substring within a longer string. The optional third and fourth arguments let you find instances of the substring other than the first instance starting from the left.'
      },
      length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'length(STRING a)',
				draggable: 'length()',
        description: 'Returns the length in characters of the argument string.'
      },
      locate: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT', optional: true}]],
        signature: 'locate(STRING substr, STRING str[, INT pos])',
				draggable: 'locate()',
        description: 'Returns the position (starting from 1) of the first occurrence of a substring within a longer string, optionally after a particular position.'
      },
      lower: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'lower(STRING a)',
				draggable: 'lower()',
        description: 'Returns the argument string converted to all-lowercase.'
      },
      lcase: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'lcase(STRING a)',
				draggable: 'lcase()',
        description: 'Returns the argument string converted to all-lowercase.'
      },
      lpad: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'STRING'}]],
        signature: 'lpad(STRING str, INT len, STRING pad)',
				draggable: 'lpad()',
        description: 'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the left with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.'
      },
      ltrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ltrim(STRING a)',
				draggable: 'ltrim()',
        description: 'Returns the argument string with any leading spaces removed from the left side.'
      },
      parse_url: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])',
				draggable: 'parse_url()',
        description: 'Returns the portion of a URL corresponding to a specified part. The part argument can be \'PROTOCOL\', \'HOST\', \'PATH\', \'REF\', \'AUTHORITY\', \'FILE\', \'USERINFO\', or \'QUERY\'. Uppercase is required for these literal values. When requesting the QUERY portion of the URL, you can optionally specify a key to retrieve just the associated value from the key-value pairs in the query string.'
      },
      regexp_extract: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'regexp_extract(STRING subject, STRING pattern, INT index)',
				draggable: 'regexp_extract()',
        description: 'Returns the specified () group from a string based on a regular expression pattern. Group 0 refers to the entire extracted string, while group 1, 2, and so on refers to the first, second, and so on (...) portion.'
      },
      regexp_like: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        signature: 'regexp_like(STRING source, STRING pattern [, STRING options])',
        draggable: 'regexp_like()',
        description: 'Returns true or false to indicate whether the source string contains anywhere inside it the regular expression given by the pattern. The optional third argument consists of letter flags that change how the match is performed, such as i for case-insensitive matching.'
      },
      regexp_replace: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'regexp_replace(STRING initial, STRING pattern, STRING replacement)',
				draggable: 'regexp_replace()',
        description: 'Returns the initial argument with the regular expression pattern replaced by the final argument string.'
      },
      repeat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'repeat(STRING str, INT n)',
				draggable: 'repeat()',
        description: 'Returns the argument string repeated a specified number of times.'
      },
      replace: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'replace(STRING initial, STRING target, STRING replacement)',
        draggable: 'replace()',
        description: 'Returns the initial argument with all occurrences of the target string replaced by the replacement string.'
      },
      reverse: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'reverse(STRING a)',
				draggable: 'reverse()',
        description: 'Returns the argument string with characters in reversed order.'
      },
      rpad: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'STRING'}]],
        signature: 'rpad(STRING str, INT len, STRING pad)',
				draggable: 'rpad()',
        description: 'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the right with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.'
      },
      rtrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'rtrim(STRING a)',
				draggable: 'rtrim()',
        description: 'Returns the argument string with any trailing spaces removed from the right side.'
      },
      space: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'INT'}]],
        signature: 'space(INT n)',
				draggable: 'space()',
        description: 'Returns a concatenated string of the specified number of spaces. Shorthand for repeat(\' \', n).'
      },
      split_part: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'BIGINT'}]],
        signature: 'split_part(STRING source, STRING delimiter, BIGINT n)',
        draggable: 'split_part()',
        description: 'Returns the nth field within a delimited string. The fields are numbered starting from 1. The delimiter can consist of multiple characters, not just a single character. All matching of the delimiter is done exactly, not using any regular expression patterns.'
      },
      strleft: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'strleft(STRING a, INT num_chars)',
				draggable: 'strleft()',
        description: 'Returns the leftmost characters of the string. Shorthand for a call to substr() with 2 arguments.'
      },
      strright: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'strright(STRING a, INT num_chars)',
				draggable: 'strright()',
        description: 'Returns the rightmost characters of the string. Shorthand for a call to substr() with 2 arguments.'
      },
      substr: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'INT', optional: true}]],
        signature: 'substr(STRING a, INT start [, INT len])',
				draggable: 'substr()',
        description: 'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.'
      },
      substring: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'INT', optional: true}]],
        signature: 'substring(STRING a, INT start [, INT len])',
				draggable: 'substring()',
        description: 'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.'
      },
      translate: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'translate(STRING input, STRING from, STRING to)',
				draggable: 'translate()',
        description: 'Returns the input string with a set of characters replaced by another set of characters.'
      },
      trim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'trim(STRING a)',
				draggable: 'trim()',
        description: 'Returns the input string with both leading and trailing spaces removed. The same as passing the string through both ltrim() and rtrim().'
      },
      upper: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'upper(STRING a)',
				draggable: 'upper()',
        description: 'Returns the argument string converted to all-uppercase.'
      },
      ucase: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ucase(STRING a)',
				draggable: 'ucase()',
        description: 'Returns the argument string converted to all-uppercase.'
      }
    }
  };

  var DATA_MASKING_FUNCTIONS = {
    hive: {
      mask: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', optional: true}], [{type: 'STRING', optional: true}], [{type: 'STRING', optional: true}]],
        signature: 'mask(STRING str [, STRING upper [, STRING lower [, STRING number]]])',
        draggable: 'mask()',
        description: 'Returns a masked version of str (as of Hive 2.1.0). By default, upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example mask("abcd-EFGH-8765-4321") results in xxxx-XXXX-nnnn-nnnn. You can override the characters used in the mask by supplying additional arguments: the second argument controls the mask character for upper case letters, the third argument for lower case letters and the fourth argument for numbers. For example, mask("abcd-EFGH-8765-4321", "U", "l", "#") results in llll-UUUU-####-####.'
      },
      mask_first_n: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT', optional: true}]],
        signature: 'mask_first_n(STRING str [, INT n])',
        draggable: 'mask_first_n()',
        description: 'Returns a masked version of str with the first n values masked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_first_n("1234-5678-8765-4321", 4) results in nnnn-5678-8765-4321.'
      },
      mask_last_n: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT', optional: true}]],
        signature: 'mask_last_n(STRING str [, INT n])',
        draggable: 'mask_last_n()',
        description: 'Returns a masked version of str with the last n values masked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_last_n("1234-5678-8765-4321", 4) results in 1234-5678-8765-nnnn.'
      },
      mask_show_first_n: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT', optional: true}]],
        signature: 'mask_show_first_n(STRING str [, INT n])',
        draggable: 'mask_show_first_n()',
        description: 'Returns a masked version of str, showing the first n characters unmasked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_show_first_n("1234-5678-8765-4321", 4) results in 1234-nnnn-nnnn-nnnn.'
      },
      mask_show_last_n: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT', optional: true}]],
        signature: 'mask_show_last_n(STRING str [, INT n])',
        draggable: 'mask_show_last_n()',
        description: 'Returns a masked version of str, showing the last n characters unmasked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_show_last_n("1234-5678-8765-4321", 4) results in nnnn-nnnn-nnnn-4321.'
      },
      mask_hash: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'CHAR'}, {type: 'VARCHAR'}]],
        signature: 'mask_hash(STRING|CHAR|VARCHAR str)',
        draggable: 'mask_hash()',
        description: 'Returns a hashed value based on str (as of Hive 2.1.0). The hash is consistent and can be used to join masked values together across tables. This function returns null for non-string types.'
      },
    },
    impala: {}
  };

  var TABLE_GENERATING_FUNCTIONS = {
    hive: {
      explode: {
        returnTypes: ['table'],
        arguments: [[{type: 'ARRAY'}, {type: 'MAP'}]],
        signature: 'explode(Array|Array<T>|Map a)',
				draggable: 'explode()',
        description: ''
      },
      inline: {
        returnTypes: ['table'],
        arguments: [[{type: 'ARRAY'}]],
        signature: 'inline(Array<Struct [, Struct]> a)',
				draggable: 'inline()',
        description: 'Explodes an array of structs into a table. (As of Hive 0.10.)'
      },
      json_tuple: {
        returnTypes: ['table'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        signature: 'json_tuple(STRING jsonStr, STRING k1, STRING k2, ...)',
				draggable: 'json_tuple()',
        description: 'A new json_tuple() UDTF is introduced in Hive 0.7. It takes a set of names (keys) and a JSON string, and returns a tuple of values using one function. This is much more efficient than calling GET_JSON_OBJECT to retrieve more than one key from a single JSON string.'
      },
      parse_url_tuple: {
        returnTypes: ['table'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        signature: 'parse_url_tuple(STRING url, STRING p1, STRING p2, ...)',
				draggable: 'parse_url_tuple()',
        description: 'The parse_url_tuple() UDTF is similar to parse_url(), but can extract multiple parts of a given URL, returning the data in a tuple. Values for a particular key in QUERY can be extracted by appending a colon and the key to the partToExtract argument.'
      },
      posexplode: {
        returnTypes: ['table'],
        arguments: [[{type: 'ARRAY'}]],
        signature: 'posexplode(ARRAY)',
        draggable: 'posexplode()',
        description: 'posexplode() is similar to explode but instead of just returning the elements of the array it returns the element as well as its position  in the original array.'
      },
      stack: {
        returnTypes: ['table'],
        arguments: [[{type: 'INT'}], [{type: 'T', multiple: true}]],
        signature: 'stack(INT n, v1, v2, ..., vk)',
				draggable: 'stack()',
        description: 'Breaks up v1, v2, ..., vk into n rows. Each row will have k/n columns. n must be constant.'
      }
    },
    impala: {}
  };

  var MISC_FUNCTIONS = {
    hive: {
      aes_decrypt: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'BINARY'}], [{type: 'BINARY'}, {type: 'STRING'}]],
        signature: 'aes_decrypt(BINARY input, STRING|BINARY key)',
				draggable: 'aes_decrypt()',
        description: 'Decrypt input using AES (as of Hive 1.3.0). Key lengths of 128, 192 or 256 bits can be used. 192 and 256 bits keys can be used if Java Cryptography Extension (JCE) Unlimited Strength Jurisdiction Policy Files are installed. If either argument is NULL or the key length is not one of the permitted values, the return value is NULL. Example: aes_decrypt(unbase64(\'y6Ss+zCYObpCbgfWfyNWTw==\'), \'1234567890123456\') = \'ABC\'.'
      },
      aes_encrypt: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}], [{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'aes_encrypt(STRING|BINARY input, STRING|BINARY key)',
				draggable: 'aes_encrypt()',
        description: 'Encrypt input using AES (as of Hive 1.3.0). Key lengths of 128, 192 or 256 bits can be used. 192 and 256 bits keys can be used if Java Cryptography Extension (JCE) Unlimited Strength Jurisdiction Policy Files are installed. If either argument is NULL or the key length is not one of the permitted values, the return value is NULL. Example: base64(aes_encrypt(\'ABC\', \'1234567890123456\')) = \'y6Ss+zCYObpCbgfWfyNWTw==\'.'
      },
      crc32: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'crc32(STRING|BINARY a)',
				draggable: 'crc32()',
        description: 'Computes a cyclic redundancy check value for string or binary argument and returns bigint value (as of Hive 1.3.0). Example: crc32(\'ABC\') = 2743272264.'
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
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'get_json_object(STRING json, STRING jsonPath)',
				draggable: 'get_json_object()',
        description: 'A limited version of JSONPath is supported ($ : Root object, . : Child operator, [] : Subscript operator for array, * : Wildcard for []'
      },
      hash: {
        returnTypes: ['INT'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'hash(a1[, a2...])',
				draggable: 'hash()',
        description: 'Returns a hash value of the arguments. (As of Hive 0.4.)'
      },
      java_method: {
        returnTypes: ['T'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'T', multiple: true, optional: true}]],
        signature: 'java_method(class, method[, arg1[, arg2..]])',
				draggable: 'java_method()',
        description: 'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.9.0.)'
      },
      md5: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'md5(STRING|BINARY a)',
        draggable: 'md5()',
        description: 'Calculates an MD5 128-bit checksum for the string or binary (as of Hive 1.3.0). The value is returned as a string of 32 hex digits, or NULL if the argument was NULL. Example: md5(\'ABC\') = \'902fbdd2b1df0c4f70b4a5d23525e932\'.'
      },
      reflect: {
        returnTypes: ['T'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'T', multiple: true, optional: true}]],
        signature: 'reflect(class, method[, arg1[, arg2..]])',
				draggable: 'reflect()',
        description: 'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.7.0.)'
      },
      sha: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'sha(STRING|BINARY a)',
				draggable: 'sha()',
        description: 'Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1(\'ABC\') = \'3c01bdbb26f358bab27f267924aa2c9a03fcfdb8\'.'
      },
      sha1: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'sha1(STRING|BINARY a)',
				draggable: 'sha1()',
        description: 'Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1(\'ABC\') = \'3c01bdbb26f358bab27f267924aa2c9a03fcfdb8\'.'
      },
      sha2: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}], [{type: 'INT'}]],
        signature: 'sha2(STRING|BINARY a, INT b)',
				draggable: 'sha2()',
        description: 'Calculates the SHA-2 family of hash functions (SHA-224, SHA-256, SHA-384, and SHA-512) (as of Hive 1.3.0). The first argument is the string or binary to be hashed. The second argument indicates the desired bit length of the result, which must have a value of 224, 256, 384, 512, or 0 (which is equivalent to 256). SHA-224 is supported starting from Java 8. If either argument is NULL or the hash length is not one of the permitted values, the return value is NULL. Example: sha2(\'ABC\', 256) = \'b5d4045c3f466fa91fe2cc6abe79232a1a57cdf104f7a26e716e0a1e2789df78\'.'
      },
      version: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'version()',
        draggable: 'version()',
        description: 'Returns the Hive version (as of Hive 2.1.0). The string contains 2 fields, the first being a build number and the second being a build hash. Example: "select version();" might return "2.1.0.2.5.0.0-1245 r027527b9c5ce1a3d7d0b6d2e6de2378fb0c39232". Actual results will depend on your build.'
      },
      xpath: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'array<STRING> xpath(STRING xml, STRING xpath)',
				draggable: 'array<STRING> xpath()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_boolean: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_boolean(STRING xml, STRING xpath)',
				draggable: 'xpath_boolean()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_double: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_double(STRING xml, STRING xpath)',
				draggable: 'xpath_double()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_float: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_float(STRING xml, STRING xpath)',
				draggable: 'xpath_float()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_int: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_int(STRING xml, STRING xpath)',
				draggable: 'xpath_int()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_long: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_long(STRING xml, STRING xpath)',
				draggable: 'xpath_long()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_number: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_number(STRING xml, STRING xpath)',
				draggable: 'xpath_number()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_short: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_short(STRING xml, STRING xpath)',
				draggable: 'xpath_short()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_string: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_string(STRING xml, STRING xpath)',
				draggable: 'xpath_string()',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      }
    },
    impala: {
      current_database: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'current_database()',
				draggable: 'current_database()',
        description: 'Returns the database that the session is currently using, either default if no database has been selected, or whatever database the session switched to through a USE statement or the impalad - d option'
      },
      effective_user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'effective_user()',
        draggable: 'effective_user()',
        description: 'Typically returns the same value as user(), except if delegation is enabled, in which case it returns the ID of the delegated user.'
      },
      pid: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'pid()',
				draggable: 'pid()',
        description: 'Returns the process ID of the impalad daemon that the session is connected to.You can use it during low - level debugging, to issue Linux commands that trace, show the arguments, and so on the impalad process.'
      },
      user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'user()',
				draggable: 'user()',
        description: 'Returns the username of the Linux user who is connected to the impalad daemon.Typically called a single time, in a query without any FROM clause, to understand how authorization settings apply in a security context; once you know the logged - in user name, you can check which groups that user belongs to, and from the list of groups you can check which roles are available to those groups through the authorization policy file.In Impala 2.0 and later, user() returns the the full Kerberos principal string, such as user@example.com, in a Kerberized environment.'
      },
      uuid: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'uuid()',
        draggable: 'uuid()',
        description: 'Returns a universal unique identifier, a 128-bit value encoded as a string with groups of hexadecimal digits separated by dashes.'
      },
      version: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'version()',
				draggable: 'version()',
        description: 'Returns information such as the precise version number and build date for the impalad daemon that you are currently connected to.Typically used to confirm that you are connected to the expected level of Impala to use a particular feature, or to connect to several nodes and confirm they are all running the same level of impalad.'
      }
    }
  };

  var ANALYTIC_FUNCTIONS = {
    hive: {
      cume_dist: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true, optional: true }]],
        signature: 'cume_dist()',
				draggable: 'cume_dist()',
        description: ''
      },
      dense_rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'dense_rank() OVER([partition_by_clause] order_by_clause)',
        draggable: 'dense_rank() OVER()',
        description: 'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions.'
      },
      first_value: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'first_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        draggable: 'first_value() OVER()',
        description: 'Returns the expression value from the first row in the window. The return value is NULL if the input expression is NULL.'
      },
      lag: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'INT', optional: true}], [{type: 'T', optional: true}]],
        signature: 'lag(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        draggable: 'lag() OVER()',
        description: 'This function returns the value of an expression using column values from a preceding row. You specify an integer offset, which designates a row position some number of rows previous to the current row. Any column references in the expression argument refer to column values from that prior row.'
      },
      last_value: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'last_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        draggable: 'last_value() OVER()',
        description: 'Returns the expression value from the last row in the window. The return value is NULL if the input expression is NULL.'
      },
      lead: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'INT', optional: true}], [{type: 'T', optional: true}]],
        signature: 'lead(expr [, offset] [, default]) OVER([partition_by_clause] order_by_clause)',
        draggable: 'lead() OVER()',
        description: 'This function returns the value of an expression using column values from a following row. You specify an integer offset, which designates a row position some number of rows after to the current row. Any column references in the expression argument refer to column values from that later row.'
      },
      ntile: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true, optional: true }]],
        signature: 'ntile()',
				draggable: 'ntile()',
        description: ''
      },
      percent_rank: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true, optional: true }]],
        signature: 'percent_rank()',
				draggable: 'percent_rank()',
        description: ''
      },
      rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'rank() OVER([partition_by_clause] order_by_clause)',
        draggable: 'rank() OVER()',
        description: 'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions. After generating duplicate output values for the "tied" input values, the function increments the sequence by the number of tied values.'
      },
      row_number: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'row_number() OVER([partition_by_clause] order_by_clause)',
        draggable: 'row_number() OVER()',
        description: 'Returns an ascending sequence of integers, starting with 1. Starts the sequence over for each group produced by the PARTITIONED BY clause. The output sequence includes different values for duplicate input values. Therefore, the sequence never contains any duplicates or gaps, regardless of duplicate input values.'
      }
    },
    impala: {
      cume_dist: {
        returnTypes: ['T'],
        arguments: [{type: 'T'}],
        signature: 'cume_dist(T expr) OVER([partition_by_clause] order_by_clause)',
        draggable: 'cume_dist() OVER()',
        description: 'Returns the cumulative distribution of a value. The value for each row in the result set is greater than 0 and less than or equal to 1.'
      },
      dense_rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'dense_rank() OVER([partition_by_clause] order_by_clause)',
        draggable: 'dense_rank() OVER()',
        description: 'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions.'
      },
      first_value: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'first_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        draggable: 'first_value() OVER()',
        description: 'Returns the expression value from the first row in the window. The return value is NULL if the input expression is NULL.'
      },
      lag: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'INT', optional: true}], [{type: 'T', optional: true}]],
        signature: 'lag(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        draggable: 'lag() OVER()',
        description: 'This function returns the value of an expression using column values from a preceding row. You specify an integer offset, which designates a row position some number of rows previous to the current row. Any column references in the expression argument refer to column values from that prior row.'
      },
      last_value: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'last_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        draggable: 'last_value() OVER()',
        description: 'Returns the expression value from the last row in the window. The return value is NULL if the input expression is NULL.'
      },
      lead: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'INT', optional: true}], [{type: 'T', optional: true}]],
        signature: 'lead(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        draggable: 'lead() OVER()',
        description: 'This function returns the value of an expression using column values from a following row. You specify an integer offset, which designates a row position some number of rows after to the current row. Any column references in the expression argument refer to column values from that later row.'
      },
      ntile: {
        returnTypes: ['T'],
        arguments: [[{type: 'T' }], [{type: 'T', multiple: true, optional: true}]],
        signature: 'ntile(T expr [, T offset ...])',
        draggable: 'ntile()',
        description: 'Returns the "bucket number" associated with each row, between 1 and the value of an expression. For example, creating 100 buckets puts the lowest 1% of values in the first bucket, while creating 10 buckets puts the lowest 10% of values in the first bucket. Each partition can have a different number of buckets.'
      },
      percent_rank: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'percent_rank(T expr) OVER ([partition_by_clause] order_by_clause)',
        draggable: 'percent_rank() OVER()',
        description: 'Calculates the rank, expressed as a percentage, of each row within a group of rows. If rank is the value for that same row from the RANK() function (from 1 to the total number of rows in the partition group), then the PERCENT_RANK() value is calculated as (rank - 1) / (rows_in_group - 1) . If there is only a single item in the partition group, its PERCENT_RANK() value is 0. The ORDER BY clause is required. The PARTITION BY clause is optional. The window clause is not allowed.'
      },
      rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'rank() OVER([partition_by_clause] order_by_clause)',
        draggable: 'rank() OVER()',
        description: 'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions. After generating duplicate output values for the "tied" input values, the function increments the sequence by the number of tied values.'
      },
      row_number: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'row_number() OVER([partition_by_clause] order_by_clause)',
        draggable: 'row_number() OVER()',
        description: 'Returns an ascending sequence of integers, starting with 1. Starts the sequence over for each group produced by the PARTITIONED BY clause. The output sequence includes different values for duplicate input values. Therefore, the sequence never contains any duplicates or gaps, regardless of duplicate input values.'
      }
    }
  };

  var BIT_FUNCTIONS = {
    hive: {},
    impala: {
      bitand: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'bitand(T<integer_type> a, T<integer_type> b)',
        draggable: 'bitand()',
        description: 'Returns an integer value representing the bits that are set to 1 in both of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
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
        description: 'Returns an integer value representing the bits that are set to 1 in either of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
      },
      bitxor: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'T' }]],
        signature: 'bitxor(T<integer_type> a, T<integer_type> b)',
        draggable: 'bitxor()',
        description: 'Returns an integer value representing the bits that are set to 1 in one but not both of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
      },
      countset: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT', optional: true }]],
        signature: 'countset(T<integer_type> a [, INT b])',
        draggable: 'countset()',
        description: 'By default, returns the number of 1 bits in the specified integer value. If the optional second argument is set to zero, it returns the number of 0 bits instead.'
      },
      getbit: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'getbit(T<integer_type> a, INT b)',
        draggable: 'getbit()',
        description: 'Returns a 0 or 1 representing the bit at a specified position. The positions are numbered right to left, starting at zero. The position argument (b) cannot be negative.'
      },
      rotateleft: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'rotateleft(T<integer_type> a, INT b)',
        draggable: 'rotateleft()',
        description: 'Rotates an integer value left by a specified number of bits. As the most significant bit is taken out of the original value, if it is a 1 bit, it is "rotated" back to the least significant bit. Therefore, the final value has the same number of 1 bits as the original value, just in different positions. In computer science terms, this operation is a "circular shift".'
      },
      rotateright: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'rotateright(T<integer_type> a, INT b)',
        draggable: 'rotateright()',
        description: 'Rotates an integer value right by a specified number of bits. As the least significant bit is taken out of the original value, if it is a 1 bit, it is "rotated" back to the most significant bit. Therefore, the final value has the same number of 1 bits as the original value, just in different positions. In computer science terms, this operation is a "circular shift".'
      },
      setbit: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }], [{ type: 'INT', optional: true }]],
        signature: 'setbit(T<integer_type> a, INT b [, INT c])',
        draggable: 'setbit()',
        description: 'By default, changes a bit at a specified position (b) to a 1, if it is not already. If the optional third argument is set to zero, the specified bit is set to 0 instead.'
      },
      shiftleft: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'shiftleft(T<integer_type> a, INT b)',
        draggable: 'shiftleft()',
        description: 'Shifts an integer value left by a specified number of bits. As the most significant bit is taken out of the original value, it is discarded and the least significant bit becomes 0. In computer science terms, this operation is a "logical shift".'
      },
      shiftright: {
        returnTypes: ['T'],
        arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
        signature: 'shiftright(T<integer_type> a, INT b)',
        draggable: 'shiftright()',
        description: 'Shifts an integer value right by a specified number of bits. As the least significant bit is taken out of the original value, it is discarded and the most significant bit becomes 0. In computer science terms, this operation is a "logical shift".'
      }
    }
  };

  var CATEGORIZED_FUNCTIONS = {
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

  var typeImplicitConversion = {
    hive: {
      BOOLEAN: {
        BOOLEAN: true, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: false, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      TIMESTAMP: {
        BOOLEAN: false, TIMESTAMP: true, DATE: false, BINARY: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: false, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      DATE: {
        BOOLEAN: false, TIMESTAMP: false, DATE: true, BINARY: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: false, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      BINARY: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: true, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: false, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      TINYINT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      SMALLINT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      INT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      BIGINT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      FLOAT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      DOUBLE: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: false, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      DECIMAL: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      NUMBER: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      STRING: {
        BOOLEAN: false, TIMESTAMP: true, DATE: true, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      CHAR: {
        BOOLEAN: false, TIMESTAMP: true, DATE: true, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      VARCHAR: {
        BOOLEAN: false, TIMESTAMP: true, DATE: true, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      T: {
        BOOLEAN: true, TIMESTAMP: true, DATE: true, BINARY: true, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      }
    },
    impala: {
      BOOLEAN: {
        BOOLEAN: true, TIMESTAMP: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      TIMESTAMP :{
        BOOLEAN: false, TIMESTAMP: true, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: false, VARCHAR: false, STRING: true, T: true
      },
      TINYINT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      SMALLINT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      INT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      BIGINT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      DOUBLE: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: false, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      REAL: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: false, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      DECIMAL: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: true, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      FLOAT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      NUMBER: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: true, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      CHAR: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: true, VARCHAR: false, STRING: false, T: true
      },
      VARCHAR: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: true, VARCHAR: true, STRING: false, T: true
      },
      STRING: {
        BOOLEAN: false, TIMESTAMP: true, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: true, VARCHAR: false, STRING: true, T: true
      },
      T: {
        BOOLEAN: true, TIMESTAMP: true, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: true, FLOAT: true, NUMBER: true, CHAR: true, VARCHAR: true, STRING: true, T: true
      }
    }
  };

  var createDocHtml = function (funcDesc) {
    var html = '<div class="fn-details"><p><span class="fn-sig">' + funcDesc.signature + '</span></p>';
    if (funcDesc.description) {
      html += '<p>' + funcDesc.description.replace(/[<]/g, "&lt;").replace(/[>]/g, "&gt;") + '</p>';
    }
    html += '<div>';
    return html;
  };

  var stripPrecision = function (types) {
    var result = [];
    types.forEach(function (type) {
      if (type.indexOf('(') > -1) {
        result.push(type.substring(0, type.indexOf('(')))
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
   * @param actualTypes
   * @returns {boolean}
   */
  var matchesType = function (dialect, expectedTypes, actualRawTypes) {
    if (dialect !== 'hive') {
      dialect = 'impala';
    }
    var actualTypes = stripPrecision(actualRawTypes);
    if (actualTypes.indexOf('ARRAY') !== -1 || actualTypes.indexOf('MAP') !== -1 || actualTypes.indexOf('STRUCT') !== -1) {
      return true;
    }
    for (var i = 0; i < expectedTypes.length; i++) {
      for (var j = 0; j < actualTypes.length; j++) {
        // To support future unknown types
        if (typeof typeImplicitConversion[dialect][expectedTypes[i]] === 'undefined' || typeof typeImplicitConversion[dialect][expectedTypes[i]][actualTypes[j]] == 'undefined') {
          return true;
        }
        if (typeImplicitConversion[dialect][expectedTypes[i]] && typeImplicitConversion[dialect][expectedTypes[i]][actualTypes[j]]) {
          return true;
        }
      }
    }
    return false;
  };

  var addFunctions = function (functionIndex, dialect, returnTypes, result) {
    var indexForDialect = functionIndex[dialect || 'generic'];
    if (indexForDialect) {
      Object.keys(indexForDialect).forEach(function (funcName) {
        var func = indexForDialect[funcName];
        if (typeof returnTypes === 'undefined' || matchesType(dialect, returnTypes, func.returnTypes)) {
          result[funcName] = func;
        }
      });
    }
    if (functionIndex.shared) {
      Object.keys(functionIndex.shared).forEach(function (funcName) {
        var func = functionIndex.shared[funcName];
        if (typeof returnTypes === 'undefined' || matchesType(dialect, returnTypes, func.returnTypes)) {
          result[funcName] = func;
        }
      });
    }
  };

  var getFunctionsWithReturnTypes = function (dialect, returnTypes, includeAggregate, includeAnalytic) {
    var result = {};
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

  var suggestFunctions = function (dialect, returnTypes, includeAggregate, includeAnalytic, completions, weight) {
    var functionsToSuggest = getFunctionsWithReturnTypes(dialect, returnTypes, includeAggregate, includeAnalytic);
    Object.keys(functionsToSuggest).forEach(function (name) {
      completions.push({
        value: name + '()',
        meta: functionsToSuggest[name].returnTypes.join('|'),
        weight: returnTypes.filter(function (type) {
          return functionsToSuggest[name].returnTypes.filter(
              function (otherType) {
                return otherType === type;
              }).length > 0
        }).length > 0 ? weight + 1 : weight,
        docHTML: createDocHtml(functionsToSuggest[name])
      })
    });
  };

  var findFunction = function (dialect, functionName) {
    return BIT_FUNCTIONS[dialect][functionName] ||
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
      ANALYTIC_FUNCTIONS[dialect][functionName];
  };

  var getArgumentTypes = function (dialect, functionName, argumentPosition) {
    if (dialect !== 'hive' && dialect !== 'impala') {
      return ['T'];
    }
    var foundFunction = findFunction(dialect, functionName);
    if (!foundFunction) {
      return ['T'];
    }
    var arguments = foundFunction.arguments;
    if (argumentPosition > arguments.length) {
      var multiples = arguments[arguments.length - 1].filter(function (type) {
        return type.multiple;
      });
      if (multiples.length > 0) {
        return multiples.map(function (argument) {
          return argument.type;
        }).sort();
      }
      return [];
    }
    return arguments[argumentPosition - 1].map(function (argument) {
      return argument.type;
    }).sort();
  };

  var getReturnTypes = function (dialect, functionName) {
    if (dialect !== 'hive' && dialect !== 'impala') {
      return ['T'];
    }
    var foundFunction = findFunction(dialect, functionName);
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