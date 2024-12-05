(function initializeEditorComponent() {
    // Fetches data as text content from a document inserted by onePageViewModel.
    // This approach supports 'unsafe-inline' by embedding the content in the <head>,
    // as specified in editor_component.mako.
    const editorOptionsElement = document.getElementById('editorOptionsJson');
    let options;
    try {
        const optionsJson = editorOptionsElement.textContent;
        options = JSON.parse(optionsJson);
    } catch (error) {
        console.error('Failed to parse editor options JSON:', error);
        return;
    }
    const user = {
        username: window.LOGGED_USERNAME,
        id: window.LOGGED_USER_ID
    };
    
    var ENABLE_QUERY_SCHEDULING = window.ENABLE_QUERY_SCHEDULING || false;
    var OPTIMIZER = {
        AUTO_UPLOAD_QUERIES: window.AUTO_UPLOAD_SQL_ANALYZER_STATS || false,
        AUTO_UPLOAD_DDL: window.AUTO_UPLOAD_SQL_ANALYZER_STATS || false,
        QUERY_HISTORY_UPLOAD_LIMIT: window.QUERY_HISTORY_UPLOAD_LIMIT
    };

    window.EDITOR_BINDABLE_ELEMENT = '#editorComponents';

    window.EDITOR_SUFFIX = 'editor';

    var HUE_PUB_SUB_EDITOR_ID = (window.location.pathname.indexOf('notebook') > -1) ? 'notebook' : 'editor';

    window.EDITOR_VIEW_MODEL_OPTIONS = $.extend(options, {
        huePubSubId: HUE_PUB_SUB_EDITOR_ID,
        user: user.username,
        userId: user.id,
        suffix: window.EDITOR_SUFFIX,
        assistAvailable: true,
        snippetViewSettings: {
            default: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/sql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            code: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                snippetIcon: 'fa-code'
            },
            hive: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/hive',
                snippetImage: '${ static("beeswax/art/icon_beeswax_48.png") }',
                sqlDialect: true
            },
            hplsql: {
                placeHolder: I18n("Example: CREATE PROCEDURE name AS SELECT * FROM tablename limit 10 GO"),
                aceMode: 'ace/mode/hplsql',
                snippetImage: '${ static("beeswax/art/icon_beeswax_48.png") }',
                sqlDialect: true
            },
            impala: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/impala',
                snippetImage: '${ static("impala/art/icon_impala_48.png") }',
                sqlDialect: true
            },
            presto: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/presto',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            dasksql: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/dasksql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            elasticsearch: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/elasticsearch',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            druid: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/druid',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            bigquery: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/bigquery',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            phoenix: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/phoenix',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            ksql: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/ksql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            flink: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/flink',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            jar: {
                snippetIcon: 'fa-file-archive-o '
            },
            mysql: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/mysql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            mysqljdbc: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/mysql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            oracle: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/oracle',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            pig: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                aceMode: 'ace/mode/pig',
                snippetImage: '${ static("pig/art/icon_pig_48.png") }'
            },
            postgresql: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/pgsql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            solr: {
                placeHolder: I18n("Example: SELECT fieldA, FieldB FROM collectionname, or press CTRL + space"),
                aceMode: 'ace/mode/mysql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            kafkasql: {
                placeHolder: I18n("Example: SELECT fieldA, FieldB FROM collectionname, or press CTRL + space"),
                aceMode: 'ace/mode/mysql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            java: {
                snippetIcon: 'fa-file-code-o'
            },
            py: {
                snippetIcon: 'fa-file-code-o'
            },
            pyspark: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                aceMode: 'ace/mode/python',
                snippetImage: '${ static("spark/art/icon_spark_48.png") }'
            },
            r: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                aceMode: 'ace/mode/r',
                snippetImage: '${ static("spark/art/icon_spark_48.png") }'
            },
            scala: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                aceMode: 'ace/mode/scala',
                snippetImage: '${ static("spark/art/icon_spark_48.png") }'
            },
            spark: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                aceMode: 'ace/mode/scala',
                snippetImage: '${ static("spark/art/icon_spark_48.png") }'
            },
            spark2: {
                snippetImage: '${ static("spark/art/icon_spark_48.png") }'
            },
            sparksql: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/sparksql',
                snippetImage: '${ static("spark/art/icon_spark_48.png") }',
                sqlDialect: true
            },
            mapreduce: {
                snippetIcon: 'fa-file-archive-o'
            },
            shell: {
                snippetIcon: 'fa-terminal'
            },
            sqoop1: {
                placeHolder: I18n("Example: import  --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir hdfs://localhost:8020/user/foo -m 1"),
                snippetImage: '${ static("sqoop/art/icon_sqoop_48.png") }'
            },
            distcp: {
                snippetIcon: 'fa-files-o'
            },
            sqlite: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/sql',
                snippetIcon: 'fa-database',
                sqlDialect: true
            },
            text: {
                placeHolder: I18n('Type your text here'),
                aceMode: 'ace/mode/text',
                snippetIcon: 'fa-header'
            },
            markdown: {
                placeHolder: I18n('Type your markdown here'),
                aceMode: 'ace/mode/markdown',
                snippetIcon: 'fa-header'
            }
        }
    });

    window.EDITOR_ENABLE_QUERY_SCHEDULING = ENABLE_QUERY_SCHEDULING;

    window.SQL_ANALYZER_AUTO_UPLOAD_QUERIES = OPTIMIZER.AUTO_UPLOAD_QUERIES;

    window.SQL_ANALYZER_AUTO_UPLOAD_DDL = OPTIMIZER.AUTO_UPLOAD_DDL;

    window.SQL_ANALYZER_QUERY_HISTORY_UPLOAD_LIMIT = OPTIMIZER.QUERY_HISTORY_UPLOAD_LIMIT;
})();
