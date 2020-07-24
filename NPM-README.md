# GetHue
GetHue is a collection of various Hue building blocks providing a smart SQL Cloud Editor. They can be classified into two groups, [SQL Parsers](#sql-parsers) and [UI Components](#ui-components). We have collated them into an NPM package for you to easily use in your own app.

# Install

    npm install --save gethue

# SQL Parsers

The parsers are the flagship part of Hue and power extremely advanced autocompletes and other [SQL functionalities](https://docs.gethue.com/user/querying/#autocomplete). They are running on the client side and comes with just a few megabytes of JavaScript that are cached by the browser. This provides a very reactive experience to the end user and allows to [import them](https://docs.gethue.com/developer/parsers#using-hue-parsers-in-your-project) as classic JavaScript modules for your own development needs.

Please refer the [SQL Parser Documentation](https://docs.gethue.com/developer/parsers/), or this [demo app](https://github.com/cloudera/hue/tree/master/tools/examples/api/hue_dep) for more information.

!["Parser Component"](https://cdn.gethue.com/uploads/2020/07/parser_component.png)

# UI Components

Some of the UI elements in Hue are available as generic [Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components). They are library/framework agnostic, and can be used in any web project irrespective of what it's built upon - React, Angular, Ember or something else. Internally these components are **created using Vue.js & TypeScript**. So you can even use them as plain Vue component, and take advantage of Vue features.

Please refer the [UI Components Documentation](https://docs.gethue.com/developer/components/) for more information. Page for each component must give you a sound idea on the attributes/props that the components accept, and events they generate. Please refer these [demo apps](https://github.com/cloudera/hue/tree/master/tools/examples/components) for examples on how the components can be used.

!["SQL Scratchpad Component"](https://cdn.gethue.com/uploads/2020/02/quick-query-component.jpg)
