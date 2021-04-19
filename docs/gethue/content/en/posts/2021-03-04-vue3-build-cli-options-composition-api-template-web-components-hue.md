---
title: Introducing Vue 3 & Web Components in Hue Query Editor
author: Hue Team
type: post
date: 2021-03-04T00:00:00+00:00
url: /blog/vue3-build-cli-options-composition-api-template-web-components-hue
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4.10
  - Development

---

The Hue project has a longevity of more than 10 years. Over these years some of the technologies we use have become rather old fashioned. So while discussing the improvements to be made in Hue, upgrading UI technology was among the top.

Hue uses a combination of [Mako](https://www.makotemplates.org/) and [Knockout JS](https://knockoutjs.com/) libraries to create all the UI magic. As newer libraries bring more productivity at this point, we decided to start a hunt for the latest best. Following were our goals:
- Introduce a modern UI library that over time will replace Knockout JS
- Package the [component](https://docs.gethue.com/developer/components/) to be shared across various projects
- Move from partial Server-side Rendering to full Client-side Rendering
- Introduce Typescript for stronger code quality

[React](https://reactjs.org/) and [Vue](https://vuejs.org/) were the top candidates. [Angular](https://angularjs.org) and [Svelte](https://svelte.dev) were also on the table. After a few brainstorming sessions we decided to go with Vue.js. Even though all the top frameworks provide a productive way to write dynamic interfaces, Vue was chosen as it was not intrusive, very fast, small and most importantly did fit well with our current [componentization](https://docs.gethue.com/developer/components) effort. We started with Vue 2, but as Vue 3 was released soon after we decided to use to Vue 3 instead. Few questions had to be answered before migrating:
- How to set up the Vue build process?
- What is the best component syntax?
- How to package as web components?

## Build process

Hue had been using webpack to build the UI. As the plan was to gradually upgrade the components, we needed the setup to work with both old and new UI code. Luckily the boilerplate project created by Vue CLI turned out to be using webpack internally. Hence we decided to create a dummy project using CLI and copy the dependencies and configurations.

Creating a dummy project was pretty straightforward. Install CLI using `npm install -g @vue/cli`, and create a project using `vue create hue-dummy`. While creating, instead of going with a project preset, we decided to manually select project features and opted for Vue Version, Babel, Typescript, CSS Preprocessor, Linter & Unit Tests as in the following.

    Vue CLI v4.5.11
    ? Please pick a preset: Manually select features
    ? Check the features needed for your project:
    ◉ Choose Vue version
    ◉ Babel
    ◉ TypeScript
    ◯ Progressive Web App (PWA) Support
    ◯ Router
    ◯ Vuex
    ◉ CSS Pre-processors
    ◉ Linter / Formatter
    ❯◉ Unit Testing
    ◯ E2E Testing

In the subsequent page we chose Vue 3, Typescript, SASS, Prettier, Lint, Jest and the CLI started creating the dummy project.

    Vue CLI v4.5.11
    ? Please pick a preset: Manually select features
    ? Check the features needed for your project: Choose Vue version, Babel, TS, CSS Pre-processors, Linter, Unit
    ? Choose a version of Vue.js that you want to start the project with 3.x (Preview)
    ? Use class-style component syntax? No
    ? Use Babel alongside TypeScript (required for modern mode, auto-detected polyfills, transpiling JSX)? Yes
    ? Pick a CSS pre-processor (PostCSS, Autoprefixer and CSS Modules are supported by default): Sass/SCSS (with node-sass)
    ? Pick a linter / formatter config: Prettier
    ? Pick additional lint features: Lint on save
    ? Pick a unit testing solution: Jest
    ? Where do you prefer placing config for Babel, ESLint, etc.? In dedicated config files
    ? Save this as a preset for future projects? (y/N) N

Once the project was created, we took a diff of `package.json` and configuration files of Babel, ESLint etc and the changes were copied and dependencies were updated. In `webpack.config.js`, `vue-loader` and `babel-loader` rules were put in place for .vue & .ts files respectively, and the build started working.

_Note: One configuration from the demo project that caused problems for us was `"jsx": "preserve"` in `tsconfig.json`. It was conflicting with `<>` style type casting. If you want to use JSX instead of Vue template, make sure to use the `as` keyword for typecasting._

## Component syntax, APIs & template

Now that the project started building with Vue & Typescript features, the next challenge was to figure out the writing style, and in turn how a component would look. Vue supports various ways to write a component.

### Class-style syntax

In class-style you define components as ES6 classes. Data, methods and other properties of the components can be annotated with decorators. It also facilitates the use of OOPs features like inheritance, mixins etc. **Vue Class Component** is a library that lets you make your Vue components in class-style syntax. Along with Typescript this looked like the most Object Oriented approach. But as it **adds dependency on an extra library**, we decided to look elsewhere. Moreover it's just a syntactic sugar over the Options API that’s discussed in the next section.

Following is how a component would look in class-style.

    import Vue from 'vue'
    import Component from 'vue-class-component'

    @Component
    export default class Counter extends Vue {
      // Class definition
    }

### Object-style Syntax & Options API

In object-style we define a component as an `options object`. Data, methods and properties of a component are defined as children of the options object. Also we can add functions that would be called in each stage of the component lifecycle. Vue calls them lifecycle hooks. Format of these objects, and signatures of the hooks are defined by the Vue Options API. Along with native Typescript support provided by Vue 3, object style looked good. But Vue 3 had more in store!

Following is how a component is defined in object style.

    import { defineComponent } from 'vue';

    export default defineComponent({
      // Options object definition
    });

### Composition API

[Composition API](https://v3.vuejs.org/guide/composition-api-introduction.html) is a new way provided by Vue 3 to create a component. In this the complete component is composed using a `setup function`. Methods are defined as nested closure functions, and reactive data members can be returned as children of the object returned. Special functions like onMounted are provided for defining the lifecycle hooks.

Following is how a component is defined in object style

    import { defineComponent, onMounted } from 'vue';

    defineComponent(() => {
      return {
        data: 1
      };
    });

### Our component template

At the end we decided to go with object-style syntax, and a combination of Options & Composition API where setup hook acts as the setup function. **We decided to mix and match as defining static items like props or components is easy with Options API and dynamic items like reactive provide & inject is easy with Composition API. Moreover, many of the Vue 3 documentation uses this style.** After going through various sources we created the following template for a component. It provides various options (i.e, components, directives, props etc ) that can be used to define a component, the order they could be used, and how each part interacts. This acts as a base for all our components.

    <template>
      <Comp1 @click="onClick">Click Me!</Comp1>
    </template>

    <script lang="ts">
      import { defineComponent, PropType, inject, provide } from 'vue';

      import Comp1 from './Comp1.vue';
      import AnotherComp2 from './Comp2.vue';

      export default <T, K>() => defineComponent({
        components: {
          Comp1,
          AnotherComp2
        },

        directives: {
          'overflow-on-hover': overflowOnHover
        },

        provide(): {
          hideDrawer: () => void;
        } {
          return {
            hideDrawer: (): void => {
              this.$emit('close');
            }
          };
        },

        props: {
          propA: Boolean,
          propB: {
            type: String,
            default: 'Abc'
          },
          items: {
            type: Object as PropType<SidebarNavigationItem[]>,
            required: true
          }
        },

        emits: ['emitted-event-name'],

        setup(props): { // Setup function for composition
          const injectedReactiveValue: Type = inject('injectedReactiveValue');

          return {
            dataMember: false,
            processedProp: !props.propA,
            injectedReactiveValue
          }
        },

        data(): {
          return {
              genericMember: null as <T | null>
          };
        },

        computed: {
          isActive(): Boolean { // Computed getter
            // Statements
          }
        },

        mounted(): void {
          // Statements
        },
        unmounted(): void {
          // Statements
        },

        methods: {
          onClick(event: Event): void {
            console.log(this.processedProp);
          }
        },

        watch: {
          items(): void { // Watches items prop
            // Statements to be executed
          }
        },
        created() {
          this.$watch(
            ():K => this.foo.bar, // Watch nested property bar of type K
            (val:K, prevVal:K): void => {
              // Statements to be executed
            }
          )
        }
      })
    </script>

## Web components

Our next goal was packaging the component to be shared across various projects. As modern Web UIs are built using various technologies we needed a method that's framework agnostic. Enter the web component! Web Components allows you to create reusable custom elements with their functionality encapsulated away from the rest of your code.

But to our surprise the official Vue package for converting a component to a web component did not support Vue 3. And as per [this issue](https://github.com/vuejs/vue-web-component-wrapper/issues/93) it's going to be a while before the support is added. So we had to find an alternative. We created a port of the Vue 2 web component wrapper that works with Vue 3. It's named `vue3-webcomponent-wrapper`. The code is [here](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/vue/wrapper) and npm package is available [here](https://www.npmjs.com/package/vue3-webcomponent-wrapper). Our port supports reactive attributes, events & slots.

_Note: One main blocker preventing the official wrapper for upgrading was the lack of shadow-root CSS injection in Vue 3 build tooling. As we could live without shadow in Hue this was not an issue and port took hardly a day._

Using our component wrapper is pretty easy. It can be installed using `npm i --save vue3-webcomponent-wrapper`. Once installed following snippets show how to create a custom tag named `my-component`.

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

Please find more information about the wrapper in this [demo app](https://github.com/sreenaths/vue3-webcomponent-wrapper-demo). And [this](https://github.com/cloudera/hue/blob/master/apps/metastore/src/metastore/templates/metastore.mako#L825) er-diagram tag is a sample use of the wrapper in Hue project.

### Using official Vue 3 web component wrapper

The official wrapper must be very similar to our implementation. That said, the exact function signature of the official wrapper is unknown at this point. Keep a check on [this page](https://www.npmjs.com/package/vue3-webcomponent-wrapper) for future updates.

## And that's it!

Hue moved from using pretty old technologies to the forefront of Web interface development with Vue 3 and the component wrapper. We strongly believe component programming is a very effective development paradigm with its isolation and easy sharing. In the next episode we will demo how it all integrates with the new Hue 5 API.

~ Sreenath from the Hue Team
