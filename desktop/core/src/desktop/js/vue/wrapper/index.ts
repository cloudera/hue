import { Component, h, createApp, App, ComponentPublicInstance } from 'vue';

import {
  toVNodes,
  camelize,
  hyphenate,
  callHooks,
  injectHook,
  getInitialProps,
  createCustomEvent,
  convertAttributeValue
} from './utils'

type ComponentInternal  = Partial<Component> &  {
  props: { [key: string]: any }
}

type KeyHash = { [key: string]: any };

export default function wrap (comp: Component) {

  const component: ComponentInternal = <ComponentInternal><unknown>comp;

  let isInitialized = false;

  let hyphenatedPropsList: string[];
  let camelizedPropsList: string [];
  let camelizedPropsMap: KeyHash;

  function initialize (component: ComponentInternal) {
    if (isInitialized) return;

    // extract props info
    const propsList: string[] = Array.isArray(component.props)
      ? component.props
      : Object.keys(component.props || {})
    hyphenatedPropsList = propsList.map(hyphenate)
    camelizedPropsList = propsList.map(camelize)

    const originalPropsAsObject = Array.isArray(component.props) ? {} : component.props || {}
    camelizedPropsMap = camelizedPropsList.reduce((map: KeyHash, key, i) => {
      map[key] = originalPropsAsObject[propsList[i]]
      return map
    }, {})

    // In Vue3 beforeCreate and created are replaced by the setup method

    // // proxy $emit to native DOM events
    // injectHook(component, 'setup', function () {
    //   const emit = this.$emit
    //   this.$emit = (name, ...args) => {
    //     this.$root.$options.customElement.dispatchEvent(createCustomEvent(name, args))
    //     return emit.call(this, name, ...args)
    //   }
    // })

    // injectHook(component, 'created', function () {
    //   // sync default props values to wrapper on created
    //   camelizedPropsList.forEach(key => {
    //     this.$root.props[key] = this[key]
    //   })
    // })

    // proxy props as Element properties
    camelizedPropsList.forEach(key => {
      Object.defineProperty(CustomElement.prototype, key, {
        get () {
          return this._wrapper.props[key]
        },
        set (newVal) {
          this._wrapper.props[key] = newVal
        },
        enumerable: false,
        configurable: true
      })
    })

    isInitialized = true
  }

  // function syncAttribute (el: CustomElement, key: string): void {
  //   const camelized = camelize(key)
  //   const value = el.hasAttribute(key) ? el.getAttribute(key) : undefined
  //   el._wrapper.props[camelized] = convertAttributeValue(
  //     value,
  //     key,
  //     camelizedPropsMap[camelized]
  //   )
  // }

  class CustomElement extends HTMLElement {
    _wrapper: App;
    _component?: ComponentPublicInstance;

    constructor () {
      const self = super()

      //this.attachShadow({ mode: 'open' })

      const wrapper: App = this._wrapper = createApp({
        name: 'shadow-root',
        data () {
          return {
            props: {},
            slotChildren: []
          }
        },
        render () {
          return h(component, {
            // ref: 'inner',
            props: this.props
          }, this.slotChildren)
        }
      })

      // // Use MutationObserver to react to future attribute & slot content change
      // const observer = new MutationObserver(mutations => {
      //   let hasChildrenChange = false
      //   for (let i = 0; i < mutations.length; i++) {
      //     const m = mutations[i]
      //     if (isInitialized && m.type === 'attributes' && m.target === this) {
      //       syncAttribute(this, m.attributeName)
      //     } else {
      //       hasChildrenChange = true
      //     }
      //   }

      //   if (hasChildrenChange) {
      //     // TODO: Make this working
      //     // wrapper.slotChildren = Object.freeze(toVNodes(
      //     //   h,
      //     //   this.childNodes
      //     // ))
      //   }
      // })

      // observer.observe(this, {
      //   childList: true,
      //   subtree: true,
      //   characterData: true,
      //   attributes: true
      // })
    }

    get vueComponent (): ComponentPublicInstance | undefined {
        return this._component;
    }

    connectedCallback () {
      this._component = this._wrapper.mount(this);
      callHooks(this._component, 'activated');
    }

    // connectedCallback () {
    //   const wrapper = this._wrapper
    //   if (!wrapper._isMounted) {
    //     // initialize attributes
    //     const syncInitialAttributes = () => {
    //       wrapper.props = getInitialProps(camelizedPropsList)
    //       hyphenatedPropsList.forEach(key => {
    //         syncAttribute(this, key)
    //       })
    //     }

    //     if (isInitialized) {
    //       syncInitialAttributes()
    //     } else {
    //       // async & unresolved
    //       component().then(resolved => {
    //         if (resolved.__esModule || resolved[Symbol.toStringTag] === 'Module') {
    //           resolved = resolved.default
    //         }
    //         initialize(resolved)
    //         syncInitialAttributes()
    //       })
    //     }

    //     // initialize children
    //     wrapper.slotChildren = Object.freeze(toVNodes(
    //       h,
    //       this.childNodes
    //     ))
    //     //wrapper.mount(this.shadowRoot)
    //   } else {
    //     callHooks(this.vueComponent, 'activated')
    //   }
    // }

    disconnectedCallback () {
      callHooks(this.vueComponent, 'deactivated')
    }
  }

  initialize(component)

  return CustomElement
}
