---
title: "Components"
draft: false
weight: 3
---

Some core UI elements are available as generic [Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components). They are library/framework agnostic, and can be used in any Web project irrespective of what its built upon - React, Angular, Ember or something else.

They can be simply imported as classic JavaScript modules for your own development needs or just reused as is.

## Importing

There are two ways to get them:

### NPM registry

Published as a NPM package in https://www.npmjs.com/package/gethue.

The recommended way. Versioned, published on the stabdard public JavaSCript module registry NPM, without any dependency on a local Hue project.

To run the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep) make the following changes:

1. Install gethue NPM package

       npm install --save gethue

2. In [package.json](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/package.json), remove `"hue": "file:../../../.."` without touching the newly added gethue dependency
3. In [src/app.js](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/src/app.js), change the import line to:

       import sqlAutocompleteParser from 'gethue/lib/parsers/hiveAutocompleteParser';

4. In [webpack.config.js](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/webpack.config.js):
   - Change `'js'` to `'node_modules/gethue'` under `resolve.modules`
   - Remove `exclude: /node_modules/,` from `babel-loader`

### Local repository

Checkout Hue and cd to the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep). Steps are similar if you would like to use your own app instead of the demo app.

    cd tools/examples/api/hue_dep

    npm install
    npm run webpack
    npm run app

In hue_dep `package.json` there is a dependency on Hue:

    "dependencies": {
      "hue": "file:../../.."
    },

Now let's import the Hive parser:

    import sqlAutocompleteParser from 'hue/desktop/core/src/desktop/js/parse/sql/hive/hiveAutocompleteParser';
