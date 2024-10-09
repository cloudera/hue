  window.EDITOR_BINDABLE_ELEMENT = '#editorComponents';

  window.EDITOR_SUFFIX = 'editor';

  var HUE_PUB_SUB_EDITOR_ID = (window.location.pathname.indexOf('notebook') > -1) ? 'notebook' : 'editor';

  window.EDITOR_VIEW_MODEL_OPTIONS = $.extend({"languages": [{"name": "Hive", "displayName": "Hive", "type": "hive", "interface": "hiveserver2", "options": {}, "dialect": "hive", "dialect_properties": {}, "category": "editor", "is_sql": true, "is_catalog": false}, {"name": "Impala", "displayName": "Impala", "type": "impala", "interface": "hiveserver2", "options": {}, "dialect": "impala", "dialect_properties": {}, "category": "editor", "is_sql": true, "is_catalog": false}, {"name": "Pig", "displayName": "Pig", "type": "pig", "interface": "oozie", "options": {}, "dialect": "pig", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Java", "displayName": "Java", "type": "java", "interface": "oozie", "options": {}, "dialect": "java", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Spark", "displayName": "Spark", "type": "spark2", "interface": "oozie", "options": {}, "dialect": "spark2", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "MapReduce", "displayName": "MapReduce", "type": "mapreduce", "interface": "oozie", "options": {}, "dialect": "mapreduce", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Shell", "displayName": "Shell", "type": "shell", "interface": "oozie", "options": {}, "dialect": "shell", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Sqoop 1", "displayName": "Sqoop 1", "type": "sqoop1", "interface": "oozie", "options": {}, "dialect": "sqoop1", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Distcp", "displayName": "Distcp", "type": "distcp", "interface": "oozie", "options": {}, "dialect": "distcp", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Solr SQL", "displayName": "Solr SQL", "type": "solr", "interface": "solr", "options": {}, "dialect": "solr", "dialect_properties": {}, "category": "editor", "is_sql": true, "is_catalog": false}, {"name": "Scala", "displayName": "Scala", "type": "spark", "interface": "livy", "options": {}, "dialect": "spark", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "PySpark", "displayName": "PySpark", "type": "pyspark", "interface": "livy", "options": {}, "dialect": "pyspark", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "R", "displayName": "R", "type": "r", "interface": "livy", "options": {}, "dialect": "r", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Spark Submit Jar", "displayName": "Spark Submit Jar", "type": "jar", "interface": "livy-batch", "options": {}, "dialect": "jar", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Spark Submit Python", "displayName": "Spark Submit Python", "type": "py", "interface": "livy-batch", "options": {}, "dialect": "py", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Text", "displayName": "Text", "type": "text", "interface": "text", "options": {}, "dialect": "text", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}, {"name": "Markdown", "displayName": "Markdown", "type": "markdown", "interface": "text", "options": {}, "dialect": "markdown", "dialect_properties": {}, "category": "editor", "is_sql": false, "is_catalog": false}], "mode": "editor", "is_optimizer_enabled": false, "is_wa_enabled": false, "is_navigator_enabled": false, "editor_type": "hive", "mobile": false}, {
    huePubSubId: HUE_PUB_SUB_EDITOR_ID,
    user: 'admin',
    userId: 1100714,
    suffix: 'editor',
    assistAvailable: true,
    snippetViewSettings: {
      default: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/sql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      code: {
        placeHolder: 'Example: 1 + 1, or press CTRL + space',
        snippetIcon: 'fa-code'
      },
      hive: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/hive',
        snippetImage: '/static/beeswax/art/icon_beeswax_48.png',
        sqlDialect: true
      },
      hplsql: {
        placeHolder: 'Example: CREATE PROCEDURE name AS SELECT * FROM tablename limit 10 GO',
        aceMode: 'ace/mode/hplsql',
        snippetImage: '/static/beeswax/art/icon_beeswax_48.png',
        sqlDialect: true
      },
      impala: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/impala',
        snippetImage: '/static/impala/art/icon_impala_48.png',
        sqlDialect: true
      },
      presto: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/presto',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      dasksql: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/dasksql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      elasticsearch: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/elasticsearch',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      druid: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/druid',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      bigquery: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/bigquery',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      phoenix: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/phoenix',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      ksql: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/ksql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      flink: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/flink',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      jar : {
        snippetIcon: 'fa-file-archive-o '
      },
      mysql: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/mysql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      mysqljdbc: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/mysql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      oracle: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/oracle',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      pig: {
        placeHolder: 'Example: 1 + 1, or press CTRL + space',
        aceMode: 'ace/mode/pig',
        snippetImage: '/static/pig/art/icon_pig_48.png'
      },
      postgresql: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/pgsql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      solr: {
        placeHolder: 'Example: SELECT fieldA, FieldB FROM collectionname, or press CTRL + space',
        aceMode: 'ace/mode/mysql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      kafkasql: {
        placeHolder: 'Example: SELECT fieldA, FieldB FROM collectionname, or press CTRL + space',
        aceMode: 'ace/mode/mysql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      java : {
        snippetIcon: 'fa-file-code-o'
      },
      py : {
        snippetIcon: 'fa-file-code-o'
      },
      pyspark: {
        placeHolder: 'Example: 1 + 1, or press CTRL + space',
        aceMode: 'ace/mode/python',
        snippetImage: '/static/spark/art/icon_spark_48.png'
      },
      r: {
        placeHolder: 'Example: 1 + 1, or press CTRL + space',
        aceMode: 'ace/mode/r',
        snippetImage: '/static/spark/art/icon_spark_48.png'
      },
      scala: {
        placeHolder: 'Example: 1 + 1, or press CTRL + space',
        aceMode: 'ace/mode/scala',
        snippetImage: '/static/spark/art/icon_spark_48.png'
      },
      spark: {
        placeHolder: 'Example: 1 + 1, or press CTRL + space',
        aceMode: 'ace/mode/scala',
        snippetImage: '/static/spark/art/icon_spark_48.png'
      },
      spark2: {
        snippetImage: '/static/spark/art/icon_spark_48.png'
      },
      sparksql: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/sparksql',
        snippetImage: '/static/spark/art/icon_spark_48.png',
        sqlDialect: true
      },
      mapreduce: {
        snippetIcon: 'fa-file-archive-o'
      },
      shell: {
        snippetIcon: 'fa-terminal'
      },
      sqoop1: {
        placeHolder: 'Example: import  --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir hdfs://localhost:8020/user/foo -m 1',
        snippetImage: '/static/sqoop/art/icon_sqoop_48.png'
      },
      distcp: {
        snippetIcon: 'fa-files-o'
      },
      sqlite: {
        placeHolder: 'Example: SELECT * FROM tablename, or press CTRL + space',
        aceMode: 'ace/mode/sql',
        snippetIcon: 'fa-database',
        sqlDialect: true
      },
      text: {
        placeHolder: 'Type your text here',
        aceMode: 'ace/mode/text',
        snippetIcon: 'fa-header'
      },
      markdown: {
        placeHolder: 'Type your markdown here',
        aceMode: 'ace/mode/markdown',
        snippetIcon: 'fa-header'
      }
    }
  });

  window.EDITOR_ENABLE_QUERY_SCHEDULING = 'False' === 'True';

  window.SQL_ANALYZER_AUTO_UPLOAD_QUERIES = 'True' === 'True';

  window.SQL_ANALYZER_AUTO_UPLOAD_DDL = 'True' === 'True';

  window.SQL_ANALYZER_QUERY_HISTORY_UPLOAD_LIMIT = 10000;