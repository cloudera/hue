
const normalGlobals = [];

const hueGlobals = [
  // global_js_constants.mako
  'AUTOCOMPLETE_TIMEOUT', 'CACHEABLE_TTL', 'CSRF_TOKEN', 'DOCUMENT_TYPES', 'DROPZONE_HOME_DIR',
  'ENABLE_SQL_SYNTAX_CHECK', 'HAS_MULTI_CLUSTER', 'HAS_CATALOG', 'HAS_OPTIMIZER', 'HAS_WORKLOAD_ANALYTICS',
  'HUE_CONTAINER', 'HUE_I18n', 'HUE_VERSION', 'IS_EMBEDDED', 'IS_K8S_ONLY', 'IS_NEW_INDEXER_ENABLED', 'IS_S3_ENABLED',
  'isIE11', 'KO_DATERANGEPICKER_LABELS', 'LOGGED_USERGROUPS', 'LOGGED_USERNAME', 'METASTORE_PARTITION_LIMIT',
  'USER_HOME_DIR', 'WorkerGlobalScope',

  // other misc
  'ace', 'CodeMirror', 'impalaDagre', 'less', 'MediumEditor', 'moment', 'Role', 'trackOnGA',

  // jasmine
  'afterAll', 'afterEach', 'beforeAll', 'beforeEach', 'describe', 'expect', 'fail', 'fdescribe', 'fit', 'it', 'jasmine',
  'spyOn', 'xdescribe', 'xit'
];

const globals = normalGlobals.concat(hueGlobals).reduce((acc, key) => {
  acc[key] = true;
  return acc;
}, {});


module.exports = {
  env: {
    browser: true,
    node: true,
    es6: true
  },
  extends: [
    'plugin:prettier/recommended'
  ],
  globals: globals,
  parser: 'babel-eslint',
  parserOptions: {
    ecmaVersion: 2017,
    sourceType: 'module',
    ecmaFeatures: {
    }
  },
  plugins: [],
  rules: {
    'new-cap': 0,
    'no-console': 0,
    'no-extra-boolean-cast': 0,
    'no-invalid-this': 0,
    'no-lonely-if': 2,
    'no-throw-literal': 0,
    'no-unused-vars': [
      'error',
      {
        vars: 'all',
        args: 'none',
        ignoreRestSiblings: true,
        varsIgnorePattern: '_[a-zA-Z0-9_]+'
      }
    ],
    'no-useless-constructor': 2,
    'no-var': 1,
    'no-undef': 2,
    'one-var': 0,
    'prefer-arrow-callback': 2,
    'prefer-const': ['warn', { destructuring: 'all' }],
    'require-jsdoc': 0,
    strict: 0,
    'valid-jsdoc': 0,
    curly: [2, 'all']
  },
  settings: {
  }
};
