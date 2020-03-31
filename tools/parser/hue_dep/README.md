
 Using Parser in [src/app.js](src/app.js) app

    cd hue_dep
    npm install
    npm run webpack
    npm run app

In package.json there’s a dependency on Hue git project:

    "dependencies": {
      "hue": "file:../../.."
    },

Note that it can also be a GitHub link: “hue”: "git://github.com/cloudera/hue.git” but takes a bit longer to do “npm install"

    { locations:
    [ { type: 'statement', location: [Object] },
      { type: 'statementType',
        location: [Object],
        identifier: 'SELECT' },
      { type: 'selectList', missing: false, location: [Object] },
      { type: 'column',
        location: [Object],
        identifierChain: [Array],
        qualified: false,
        tables: [Array] },
      { type: 'column',
        location: [Object],
        identifierChain: [Array],
        qualified: false,
        tables: [Array] },
      { type: 'column',
        location: [Object],
        identifierChain: [Array],
        qualified: false,
        tables: [Array] },
      { type: 'table', location: [Object], identifierChain: [Array] },
      { type: 'whereClause', missing: true, location: [Object] },
      { type: 'limitClause', missing: true, location: [Object] } ],
    lowerCase: false,
    suggestKeywords:
    [ { value: 'ABORT', weight: -1 },
      { value: 'ALTER', weight: -1 },
      { value: 'ANALYZE TABLE', weight: -1 },
      { value: 'CREATE', weight: -1 },
      { value: 'DELETE', weight: -1 },
      { value: 'DESCRIBE', weight: -1 },
      { value: 'DROP', weight: -1 },
      { value: 'EXPLAIN', weight: -1 },
      { value: 'EXPORT', weight: -1 },
      { value: 'FROM', weight: -1 },
      { value: 'GRANT', weight: -1 },
      { value: 'IMPORT', weight: -1 },
      { value: 'INSERT', weight: -1 },
      { value: 'LOAD', weight: -1 },
      { value: 'MERGE', weight: -1 },
      { value: 'MSCK', weight: -1 },
      { value: 'RELOAD FUNCTION', weight: -1 },
      { value: 'RESET', weight: -1 },
      { value: 'REVOKE', weight: -1 },
      { value: 'SELECT', weight: -1 },
      { value: 'SET', weight: -1 },
      { value: 'SHOW', weight: -1 },
      { value: 'TRUNCATE', weight: -1 },
      { value: 'UPDATE', weight: -1 },
      { value: 'USE', weight: -1 },
      { value: 'WITH', weight: -1 } ],
    definitions: [] }
