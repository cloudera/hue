const normalGlobals = [];

const hueGlobals = [
  // global_js_constants.mako
  'CACHEABLE_TTL',
  'CSRF_TOKEN',
  'DOCUMENT_TYPES',
  'DROPZONE_HOME_DIR',
  'ENABLE_SQL_SYNTAX_CHECK',
  'HAS_MULTI_CLUSTER',
  'HAS_CATALOG',
  'HAS_SQL_ANALYZER',
  'HAS_WORKLOAD_ANALYTICS',
  'HUE_I18n',
  'HUE_VERSION',
  'IS_K8S_ONLY',
  'IS_NEW_INDEXER_ENABLED',
  'IS_S3_ENABLED',
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

const jsTsVueRules = {
  'no-useless-constructor': 'off',
  '@typescript-eslint/no-non-null-assertion': 'off',
  '@typescript-eslint/no-explicit-any': 'error',
  '@typescript-eslint/no-this-alias': 'error',
  '@typescript-eslint/no-unused-vars': [
    'error',
    {
      varsIgnorePattern: '__webpack.*'
    }
  ],
  '@typescript-eslint/explicit-module-boundary-types': 'error',
  'vue/max-attributes-per-line': [
    'error',
    {
      singleline: 10,
      multiline: {
        max: 1
      }
    }
  ],
  'vue/html-self-closing': [
    'error',
    {
      html: {
        void: 'any'
      }
    }
  ],
  'vue/multi-word-component-names': 'off',
  'vue/require-toggle-inside-transition': 'off',
  'vue/singleline-html-element-content-newline': 'off' // Conflicts with prettier
};

const jestRules = {
  'jest/no-focused-tests': 'error',
  'jest/valid-expect': 'error',
  'new-cap': 'off',
  'no-console': 'off',
  'no-restricted-syntax': [
    'error',
    {
      selector:
        'CallExpression[callee.object.name="console"][callee.property.name!=/^(warn|error|info|trace)$/]',
      message: 'Unexpected property on console object was called'
    }
  ],
  'no-extra-boolean-cast': 'off',
  'no-invalid-this': 'off',
  'no-lonely-if': 'error',
  'no-throw-literal': 'off',
  'no-unused-vars': [
    'error',
    {
      vars: 'all',
      args: 'none',
      ignoreRestSiblings: true,
      varsIgnorePattern: '_[a-zA-Z0-9_]+'
    }
  ],
  'no-useless-constructor': 'error',
  'no-var': 'error',
  'no-undef': 'error',
  'one-var': 'off',
  'prefer-arrow-callback': 'error',
  'prefer-const': ['warn', { destructuring: 'all' }],
  'require-jsdoc': 'off',
  strict: 'off',
  'valid-jsdoc': 'off',
  curly: ['error', 'all']
};

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
        parser: '@typescript-eslint/parser'
      },
      plugins: ['vue', '@typescript-eslint'],
      rules: jsTsVueRules
    },
    {
      files: ['*.d.ts'],
      extends: ['plugin:@typescript-eslint/recommended'],
      parser: '@typescript-eslint/parser',
      plugins: ['jest', '@typescript-eslint'],
      rules: jsTsVueRules
    },
    {
      files: ['*.ts', '*.tsx'],
      extends: ['plugin:@typescript-eslint/recommended'],
      parser: '@typescript-eslint/parser',
      plugins: ['jest', '@typescript-eslint'],
      rules: jsTsVueRules
    }
  ],
  extends: ['plugin:prettier/recommended'],
  globals: globals,
  parser: '@babel/eslint-parser',
  parserOptions: {
    parser: '@babel/eslint-parser',
    ecmaVersion: 2017,
    sourceType: 'module',
    ecmaFeatures: {
      legacyDecorators: true
    }
  },
  plugins: ['jest'],
  rules: jestRules,
  settings: {}
};
