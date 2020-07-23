---
title: "Hue in Your Project"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 20
---

Some modules of Hue like the [SQL parsers](/developer/parsers/#using-hue-parsers-in-your-project) or [UI Components](/developer/components/#using-ui-components-in-your-project) can be imported independently as dependencies into your own apps. There are two ways to get them:

- [npm registry](#npm-registry)
- [Local dependency](#local-dependency)

## npm registry

    npm install gethue

Will install the latest from https://www.npmjs.com/package/gethue. Then import the module you need with something like below:

    import sqlAutocompleteParser from 'gethue/parse/sql/hive/hiveAutocompleteParser';

UI components can be imported in a similar way.

    import 'gethue/web/er-diagram';

## Local dependency

Checkout Hue and cd to the [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep). Steps are similar if you would like to use your own app instead of the demo app (hue_dep).

    cd tools/examples/api/hue_dep

    npm install
    npm run webpack
    npm run app

In hue_dep `package.json` add a dependency on Hue:

    "dependencies": {
      "hue": "file:../../.."
    },

Now let's import the Hive parser:

    import sqlAutocompleteParser from 'hue/desktop/core/src/desktop/js/parse/sql/hive/hiveAutocompleteParser';
