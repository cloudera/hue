(function initializeEditorComponent() {
    // The page specific settings are passed on the script URL because onePageViewModel only keeps
    // the src attribute when it re-injects the scripts of an embeddable page.
    const scriptParams = new URL(document.currentScript.src).searchParams;
    const bindableElement = '#' + scriptParams.get('bindableElement');
    const suffix = scriptParams.get('suffix') || '';

    // Fetches data as text content from a document inserted by onePageViewModel.
    // This approach supports 'unsafe-inline' by embedding the content in the <head>,
    // as specified in editor_component.mako. The editor and the notebook pages are kept side by
    // side in the DOM, so the lookup is scoped to the page that is currently being loaded.
    const bindableContainer = document.querySelector(bindableElement);
    const editorOptionsElement =
        (bindableContainer && bindableContainer.querySelector('#editorOptionsJson')) ||
        document.getElementById('editorOptionsJson');
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

    window.EDITOR_BINDABLE_ELEMENT = bindableElement;

    window.EDITOR_SUFFIX = suffix;

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
                snippetSvg: 'hi-hive',
                sqlDialect: true
            },
            hplsql: {
                placeHolder: I18n("Example: CREATE PROCEDURE name AS SELECT * FROM tablename limit 10 GO"),
                aceMode: 'ace/mode/hplsql',
                snippetSvg: 'hi-hive',
                sqlDialect: true
            },
            impala: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/impala',
                snippetSvg: 'hi-impala',
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
                snippetSvg: 'hi-pig'
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
                snippetSvg: 'hi-spark'
            },
            r: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                aceMode: 'ace/mode/r',
                snippetSvg: 'hi-spark'
            },
            scala: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                aceMode: 'ace/mode/scala',
                snippetSvg: 'hi-spark'
            },
            spark: {
                placeHolder: I18n("Example: 1 + 1, or press CTRL + space"),
                aceMode: 'ace/mode/scala',
                snippetSvg: 'hi-spark'
            },
            spark2: {
                snippetSvg: 'hi-spark'
            },
            sparksql: {
                placeHolder: I18n("Example: SELECT * FROM tablename, or press CTRL + space"),
                aceMode: 'ace/mode/sparksql',
                snippetSvg: 'hi-spark',
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
                snippetSvg: 'hi-sqoop'
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
