---
title: "Components"
draft: false
weight: 4
---

Some of the UI elements in Hue are available as generic [Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components). They are library/framework agnostic, and can be used in any web project irrespective of what its built upon - React, Angular, Ember or something else. They can be [imported](#using-hue-ui-components-in-your-project) as classic JavaScript modules for your own development needs.

## Generic Components

Following are the generic components in Hue. Doc for each component must give you a sound idea on the attributes/props that the components accept, and events they generate.

* [SQL Parsers](/developer/components/parsers)
* [ER-diagram](/developer/components/er-diagram)
* [SQL Scratchpad](/developer/components/scratchpad)

## Using UI components in your project

All the Generic Hue components are published as [GetHue](/developer/gethue/) NPM package. Following will install the latest from https://www.npmjs.com/package/gethue.

    npm install --save gethue

Here is an example on how to use the er-diagram component once installed:

### Import

er-diagram can be imported into an html file using a simple script tag as follows.

    <script type = "text/javascript" src="node_modules/gethue/web/er-diagram.js"></script>

If you are using a bundler like webpack. They can be imported using a normal import statement.

    import 'gethue/web/er-diagram';

### Usage

Once imported they can be used like a native HTML tag.

    <er-diagram id="erd-id"/>

Please refer these [demo apps](https://github.com/cloudera/hue/tree/master/tools/examples/components) for examples on how the components can be used. You must be able to directly pass attributes, and listen to custom and native events.

### Use as Vue Components

Internally these components are created using Vue.js & TypeScript. So you can even use them as plain Vue component, and take advantage of Vue features. Vue version of the components are under `gethue/components`.

    import ERDiagram from 'gethue/components/er-diagram/index.vue';
