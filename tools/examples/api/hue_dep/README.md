
 Using Parser in [src/app.js](src/app.js) app

    cd hue_dep
    npm install       // Install dependencies
    npm run webpack   // Build demo app
    npm run app       // Run demo app

In package.json there’s a dependency on Hue git project:

    "dependencies": {
      "hue": "file:../../../.."
    },

Note that it can also be a GitHub link but takes a bit longer to do `npm install`.

    "hue": "git://github.com/cloudera/hue.git"

## GetHue

You need not have a dependency on the complete Hue project, the parsers are available as [gethue npm package](https://www.npmjs.com/package/gethue). To run the demo app with gethue please making the following changes:

1. Install gethue NPM package

       npm install --save gethue

2. In `hue_dep/package.json`, remove `"hue": "file:../../../.."` without touching the newly added gethue dependency.
3. In `hue_dep/src/app.js`, change the import line to.

       import sqlAutocompleteParser from 'gethue/parse/sql/hive/hiveAutocompleteParser';

4. In `hue_dep/webpack.config.js`:
   - Change `'js'` to `'node_modules/gethue'` under `resolve.modules`.
   - Remove `exclude: /node_modules/,` from `babel-loader`.

## Output

You should get the following JSON as output on running the app.

    {
      "locations": [
        {
          "type": "statement",
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 1,
            "last_column": 38
          }
        },
        {
          "type": "statementType",
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 1,
            "last_column": 7
          },
          "identifier": "SELECT"
        },
        {
          "type": "selectList",
          "missing": false,
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 8,
            "last_column": 29
          }
        },
        {
          "type": "column",
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 8,
            "last_column": 12
          },
          "identifierChain": [
            {
              "name": "col1"
            }
          ],
          "qualified": false,
          "tables": [
            {
              "identifierChain": [
                {
                  "name": "tbl"
                }
              ]
            }
          ]
        },
        {
          "type": "column",
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 14,
            "last_column": 18
          },
          "identifierChain": [
            {
              "name": "col2"
            }
          ],
          "qualified": false,
          "tables": [
            {
              "identifierChain": [
                {
                  "name": "tbl"
                }
              ]
            }
          ]
        },
        {
          "type": "column",
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 20,
            "last_column": 24
          },
          "identifierChain": [
            {
              "name": "tbl2"
            }
          ],
          "qualified": false,
          "tables": [
            {
              "identifierChain": [
                {
                  "name": "tbl"
                }
              ]
            }
          ]
        },
        {
          "type": "complex",
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 25,
            "last_column": 29
          },
          "identifierChain": [
            {
              "name": "tbl2"
            },
            {
              "name": "col3"
            }
          ],
          "qualified": true,
          "tables": [
            {
              "identifierChain": [
                {
                  "name": "tbl"
                }
              ]
            }
          ]
        },
        {
          "type": "table",
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 35,
            "last_column": 38
          },
          "identifierChain": [
            {
              "name": "tbl"
            }
          ]
        },
        {
          "type": "whereClause",
          "missing": true,
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 38,
            "last_column": 38
          }
        },
        {
          "type": "limitClause",
          "missing": true,
          "location": {
            "first_line": 1,
            "last_line": 1,
            "first_column": 38,
            "last_column": 38
          }
        }
      ],
      "lowerCase": false,
      "suggestKeywords": [
        {
          "value": "ABORT",
          "weight": -1
        },
        {
          "value": "ALTER",
          "weight": -1
        },
        {
          "value": "ANALYZE TABLE",
          "weight": -1
        },
        {
          "value": "CREATE",
          "weight": -1
        },
        {
          "value": "DELETE",
          "weight": -1
        },
        {
          "value": "DESCRIBE",
          "weight": -1
        },
        {
          "value": "DROP",
          "weight": -1
        },
        {
          "value": "EXPLAIN",
          "weight": -1
        },
        {
          "value": "EXPORT",
          "weight": -1
        },
        {
          "value": "FROM",
          "weight": -1
        },
        {
          "value": "GRANT",
          "weight": -1
        },
        {
          "value": "IMPORT",
          "weight": -1
        },
        {
          "value": "INSERT",
          "weight": -1
        },
        {
          "value": "LOAD",
          "weight": -1
        },
        {
          "value": "MERGE",
          "weight": -1
        },
        {
          "value": "MSCK",
          "weight": -1
        },
        {
          "value": "RELOAD FUNCTION",
          "weight": -1
        },
        {
          "value": "RESET",
          "weight": -1
        },
        {
          "value": "REVOKE",
          "weight": -1
        },
        {
          "value": "SELECT",
          "weight": -1
        },
        {
          "value": "SET",
          "weight": -1
        },
        {
          "value": "SHOW",
          "weight": -1
        },
        {
          "value": "TRUNCATE",
          "weight": -1
        },
        {
          "value": "UPDATE",
          "weight": -1
        },
        {
          "value": "USE",
          "weight": -1
        },
        {
          "value": "WITH",
          "weight": -1
        }
      ],
      "definitions": []
    }
