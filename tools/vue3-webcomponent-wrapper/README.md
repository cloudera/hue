# vue3-webcomponent-wrapper
[![npm version](https://badge.fury.io/js/vue3-webcomponent-wrapper.svg)](https://www.npmjs.com/package/vue3-webcomponent-wrapper)

Vue 3 wrapper to convert a Vue component into Web Component. It supports reactive attributes, events & slots.

This is a port of [@vuejs/vue-web-component-wrapper](https://github.com/vuejs/vue-web-component-wrapper) (Official Vue 2 web component wrapper package) to work with Vue 3. And could be deprecated once the official wrapper package  starts supporting Vue 3. Progress of Vue3 support is tracked in this [issue.](https://github.com/vuejs/vue-web-component-wrapper/issues/93)

One main blocker preventing the official wrapper from upgrading was the lack of shadow-root CSS injection in Vue 3 build tooling. As we could live without a shadow dom in Hue this was not an issue and this port was created.

## Usage

Before with Vue 2 and [@vuejs/vue-web-component-wrapper](https://github.com/vuejs/vue-web-component-wrapper).

    import Vue from 'vue'
    import wrapper from '@vue/web-component-wrapper'
    import MyComponent from "./components/MyComponent.vue";

    const CustomElement = wrapper(Vue, MyComponent)
    window.customElements.define('my-component', CustomElement)

Now with Vue 3 and vue3-webcomponent-wrapper.

    import { createApp, h } from "vue";
    import wrapper from "vue3-webcomponent-wrapper";
    import MyComponent from "./components/MyComponent.vue";

    const CustomElement = wrapper(MyComponent, createApp, h);
    window.customElements.define("my-component", CustomElement);


Please find more information in this [demo app](https://github.com/sreenaths/vue3-webcomponent-wrapper-demo).

## Build & Publish

vue3-webcomponent-wrapper is build as part of gethue npm build. Following are the steps to be followed under hue root to build and publish this package.

    npm run webpack-npm
    cd tools/vue3-webcomponent-wrapper
    npm publish
