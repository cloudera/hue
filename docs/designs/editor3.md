
# Editor v3

* Component with sub components
* More than one query running at same time in same editor
* Reusable in popup like in Dashboard
* Result popup explorer
* Preso/Notebook mode
* Buttons on middle line

 ## March update

Summary: [connectors](docs/designs/connectors.md) are becoming the source of truth (both for API and UI)

* Standardize how to use the dialect names (cf. from notebook type, snippet connector, snippet type)
* Connectors are replacing Computes? [agreed]
* Namespace: utility still to browse DB without a compute. One idea would be to use connectors as well. So independent (bit like File connectors, but a HMS connector could be linked to a Hive connector and we transparently handle both or more. Could be HMS, or Atlas data catalog,..) and good timing when working on the specific left panels like 'catalogs', 'schemas', 'ksql streams', 'ksql topics'. etc..
* Could add optional FK to Connector (to handle more than one dialect instance) e.g. list all mysql queries as by default we should list only hive queries of hive connector X when opening it in the editor


So overall moving everything to connectors, handy for storing their custom properties there too and removing all the hardcoding. Then last step would be to add SQL properties like schema left assist panel, has UDF doc, has query browser, has language references so that it is truly refactored.

### API

Editor document type:

* if a 'query': 'query-[dialect name]'
* else 'notebook'

It still assumes we get the dialect type. Also easier and backward compatible automatically (if no connector id, or no connector for the id found, use the dialect filter. Using connector id in addition of dialect:

    /notebook/api/get_history?connector=9&type=query-mysql&...

    /desktop/api2/docs/?connector=9&type=query-mysql&...

    /notebook/api/execute/hive/9

Document model gets an optional foreign key on the connectors:

    type: query-impala
    connector: FK to connector 'x' for dialect 'impala'


### Examples

**Document types**

    directory
    gist
    oozie-bundle2
    oozie-coordinator2
    oozie-workflow2
    query-athena
    query-bigquery
    query-es
    query-flink
    query-hive
    query-impala
    query-ksql
    query-mysql
    query-phoenix
    query-postgresql
    query-presto
    query-sparksql
    query-sql
    search-dashboard


**Saved Query**

* "compute" is removed
* "namespace" is still there
* "connector" is "duplicated" (as also present soon as FK in Document object)
* notebook["type"] == "query-" + "notebook["snippets"][0]["connector"]["dialect"]

<pre>
    {
      "description": "",
      "directoryUuid": "",
      "executingAllIndex": 0,
      "id": null,
      "isExecutingAll": false,
      "isHidingCode": false,
      "isHistory": false,
      "isManaged": false,
      "isPresentationModeDefault": false,
      "isSaved": false,
      "name": "Hello World",
      "parentSavedQueryUuid": null,
      "presentationSnippets": {},
      "result": {},
      "sessions": [
        {
          "type": "9",
          "id": null,
          "properties": []
        }
      ],
      "snippets": [
        {
          "aceCursorPosition": null,
          "aceSize": 100,
          "executor": {
            "executables": [
              {
                "executeEnded": 0,
                "executeStarted": 0,
                "handle": {
                  "statement_id": 0
                },
                "id": "d9c7ef6e-3d11-3b1d-ca0d-019a1ddb5257",
                "logs": {
                  "jobs": [],
                  "errors": []
                },
                "lost": false,
                "observerState": {
                  "result-chart": {
                    "chartYMulti": []
                  }
                },
                "progress": 0,
                "status": "ready",
                "type": "sqlExecutable",
                "database": "default",
                "parsedStatement": {
                  "type": "statement",
                  "statement": "SHOW TABLES",
                  "location": {
                    "first_line": 1,
                    "last_line": 1,
                    "first_column": 0,
                    "last_column": 3
                  },
                  "firstToken": "SHOW"
                }
              }
            ]
          },
          "connector": {
            "name": "MySql",
            "type": "9",
            "displayName": "MySql",
            "buttonName": "Query",
            "tooltip": "9 Query",
            "page": "/editor/?type=9",
            "is_sql": true,
            "dialect": "mysql",
            "dialect_properties": {
              "is_sql": true,
              "sql_identifier_quote": "`",
              "sql_identifier_comment_single": "--",
              "has_catalog": true,
              "has_database": true,
              "has_table": true,
              "has_live_queries": false,
              "has_optimizer_risks": false,
              "has_optimizer_values": false,
              "has_auto_limit": false
            }
          },
          "currentQueryTab": "queryHistory",
          "database": "default",
          "id": "d2132c2b-b7f6-2696-265e-4ebaa576ff17",
          "is_redacted": false,
          "lastAceSelectionRowOffset": 0,
          "lastExecuted": 0,
          "name": "",
          "namespace": {
            "id": "default",
            "name": "default",
            "status": "CREATED",
            "computes": [
              {
                "id": "default",
                "name": "default",
                "type": "direct",
                "credentials": {}
              }
            ]
          },
          "pinnedContextTabs": [],
          "properties": {},
          "settingsVisible": false,
          "showLogs": true,
          "statement_raw": "sss",
          "statementPath": "",
          "statementType": "text",
          "status": "ready",
          "type": "mysql",
          "variables": [],
          "wasBatchExecuted": false
        }
      ],
      "type": "query-9",
      "uuid": "51eac6cf-6df8-ecab-5089-927c0287718a",
      "viewSchedulerId": ""
    }
<pre>
