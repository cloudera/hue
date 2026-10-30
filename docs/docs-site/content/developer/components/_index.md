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

Published as an NPM package: [gethue](https://www.npmjs.com/package/gethue).

The recommended way. Versioned, published on the standard public JavaScript module registry NPM, without any dependency on a local Hue project.

To run the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep) make the following changes:

1. Install the `gethue` NPM package:

   ```bash
   npm install --save gethue
   ```

2. In [package.json](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/package.json), remove `"hue": "file:../../../.."` without touching the newly added gethue dependency
3. In [src/app.js](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/src/app.js), change the import line to:

   ```js
   import sqlAutocompleteParser from 'gethue/lib/parsers/hiveAutocompleteParser';
   ```

4. In [webpack.config.js](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/webpack.config.js):
   - Change `'js'` to `'node_modules/gethue'` under `resolve.modules`
   - Remove `exclude: /node_modules/,` from `babel-loader`

### Local repository

Check out Hue and go to the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep). The steps are similar if you would like to use your own app instead of the demo app.

```bash
cd tools/examples/api/hue_dep

npm install
npm run webpack
npm run app
```

In the `hue_dep` `package.json` there is a dependency on Hue:

```json
"dependencies": {
  "hue": "file:../../../.."
},
```

Now import the Hive parser:

```js
import sqlAutocompleteParser from 'hue/desktop/core/src/desktop/js/parse/sql/hive/hiveAutocompleteParser';
```
