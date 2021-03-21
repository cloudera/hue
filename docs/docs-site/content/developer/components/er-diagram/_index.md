---
title: "ER-diagram"
draft: false
---

The [Entity-relationship model](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model) (ERD) provides an illustration of various SQL entities, and the relationship between them. Entity types supported by the ERD diagram are currently `Table` & `Literal`. It has a very generic architecture, and more types of entities can be supported in the future.

{{< webcomp name="er-diagram"
    src="/js/gethue/components/er-diagram.js"
    attrSrc="demo/attrs.json"
    events="entity-clicked:name"
/>}}

## Import

Please refer [here](/developer/components/#using-ui-components-in-your-project) for importing the component in your own project. Also [er-diagram-demo](https://github.com/cloudera/hue/tree/master/tools/examples/components/er-diagram-demo) app have working examples.

Once imported `er-diagram` can be used like a native HTML tag.

    <er-diagram id="erd-element-id"/>

## Attributes

- entities: Array &lt;[IEntity](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/components/er-diagram/lib/interfaces.ts#L21)&gt; - An array of entity objects. Each entity will be a box in the UI.
- relations: Array &lt;[IRelation](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/components/er-diagram/lib/interfaces.ts#L26)&gt; - An array of relation objects. Each relation will connect two of the above entities.

Please refer the [interfaces](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/components/er-diagram/lib/interfaces.ts) for an idea on the structure of these objects.

## Events

- entity-clicked: Function([IEntity](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/components/er-diagram/lib/interfaces.ts#L21)) - Will be triggered when an entity is clicked.

## Resource Files

- Hue
  - **Web Component:** gethue/web/er-diagram.js
  - **Vue Component:** gethue/components/er-diagram/index.vue
- GetHue
  - **Web Component:** desktop/core/src/desktop/js/components/er-diagram/webcomp.ts
  - **Vue Component:** desktop/core/src/desktop/js/components/er-diagram/index.vue
