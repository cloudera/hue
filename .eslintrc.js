const normalGlobals = [];

const hueGlobals = [
  // global_js_constants.mako
  'AUTOCOMPLETE_TIMEOUT',
  'CACHEABLE_TTL',
  'CSRF_TOKEN',
  'DOCUMENT_TYPES',
  'DROPZONE_HOME_DIR',
  'ENABLE_SQL_SYNTAX_CHECK',
  'HAS_MULTI_CLUSTER',
  'HAS_CATALOG',
  'HAS_OPTIMIZER',
  'HAS_WORKLOAD_ANALYTICS',
  'HUE_I18n',
  'HUE_VERSION',
  'IS_K8S_ONLY',
  'IS_NEW_INDEXER_ENABLED',
  'IS_S3_ENABLED',
  'isIE11',
  'KO_DATERANGEPICKER_LABELS',
  'LOGGED_USERGROUPS',
  'LOGGED_USERNAME',
  'METASTORE_PARTITION_LIMIT',
  'USER_HOME_DIR',
  'WorkerGlobalScope',

  // other misc
  'ace',
  'CodeMirror',
  'impalaDagre',
  'less',
  'MediumEditor',
  'moment',
  'Role',
  'trackOnGA',
  '__webpack_public_path__',

  // jest
  'afterAll',
  'afterEach',
  'beforeAll',
  'beforeEach',
  'describe',
  'expect',
  'fail',
  'fdescribe',
  'fit',
  'it',
  'jest',
  'spyOn',
  'xdescribe',
  'xit'
];

const globals = normalGlobals.concat(hueGlobals).reduce((acc, key) => {
  acc[key] = true;
  return acc;
}, {});

module.exports = {
  env: {
    browser: true,
    node: true,
    es6: true,
    jasmine: true
  },
  overrides: [
    {
      files: ['*.vue'],
      extends: [
        'plugin:prettier/recommended',
        'plugin:vue/vue3-recommended',
        'plugin:@typescript-eslint/recommended'
      ],
      parser: 'vue-eslint-parser',
      parserOptions: {
        parser: "@typescript-eslint/parser"
      },
      plugins: ['vue', '@typescript-eslint'],
      rules: {
        'vue/max-attributes-per-line': [
          'error',
          {
            singleline: 10,
            multiline: {
              max: 1,
              allowFirstLine: false
            }
          }
        ],
        'vue/html-self-closing': [
          "error",
          {
            "html": {
              "void": "any"
            }
          }
        ],
        'vue/singleline-html-element-content-newline': 0, // Conflicts with prettier
      }
    },
    {
      files: ['*.ts'],
      extends: ['plugin:@typescript-eslint/recommended'],
      parser: '@typescript-eslint/parser',
      plugins: ['jest', '@typescript-eslint']
    }
  ],
  extends: ['plugin:prettier/recommended'],
  globals: globals,
  parser: 'babel-eslint',
  parserOptions: {
    parser: 'babel-eslint',
    ecmaVersion: 2017,
    sourceType: 'module',
    ecmaFeatures: {
      legacyDecorators: true
    }
  },
  plugins: ['jest'],
  rules: {
    'jest/no-focused-tests': 'error',
    'jest/valid-expect': 'error',
    'new-cap': 0,
    'no-console': 0,
    'no-restricted-syntax': [
      'error',
      {
        selector:
          'CallExpression[callee.object.name="console"][callee.property.name!=/^(warn|error|info|trace)$/]',
        message: 'Unexpected property on console object was called'
      }
    ],
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
  settings: {}
};
