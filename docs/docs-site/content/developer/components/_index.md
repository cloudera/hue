---
title: "Components"
draft: false
weight: 3
---

Some of the UI elements in Hue are available as generic [Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components). They are library/framework agnostic, and can be used in any web project irrespective of what its built upon - React, Angular, Ember or something else.

They can be imported as classic JavaScript modules for your own development needs.

## Component list

* [SQL Parsers](/developer/components/parsers)
* [ER-diagram](/developer/components/er-diagram)
* [SQL Scratchpad](/developer/components/scratchpad)

## Importing

There are two ways to get them:

### NPM registry

Published as a NPM package in https://www.npmjs.com/package/gethue. You do not need a dependency on a complete local Hue project.

To run the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep) make the following changes:

1. Install gethue NPM package

       npm install --save gethue

2. In [package.json](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/package.json), remove `"hue": "file:../../../.."` without touching the newly added gethue dependency
3. In [src/app.js](https://github.com/cloudera/hue/blob/master/tools/examples/api/hue_dep/src/app.js), change the import line to:

       import sqlAutocompleteParser from 'gethue/parse/sql/hive/hiveAutocompleteParser';

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


## Using

Here is an example on how to use the er-diagram component once installed:

### Import

er-diagram can be imported into an html file using a simple script tag as follows.

    <script type = "text/javascript" src="node_modules/gethue/web/er-diagram.js"></script>

If you are using a bundler like webpack. They can be imported using a normal import statement.

    import 'gethue/web/er-diagram';

### Instantiate

Once imported they can be used like a native HTML tag.

    <er-diagram id="erd-id"/>

Please refer these [demo apps](https://github.com/cloudera/hue/tree/master/tools/examples/components) for examples on how the components can be used. You must be able to directly pass attributes, and listen to custom and native events.

### Use as a Vue Component

Internally these components are created using Vue.js & TypeScript. So you can even use them as plain Vue component, and take advantage of Vue features. Vue version of the components are under `gethue/components`.

    import ERDiagram from 'gethue/components/er-diagram/index.vue';
