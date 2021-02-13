// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Port of https://github.com/vuejs/vue-web-component-wrapper/blob/master/src/index.js for Vue 3 support
 * Mustb be removed once @vuejs/vue-web-component-wrapper starts supporting Vue 3
*/

import { Component, h, createApp, App, ComponentPublicInstance, VNode, ComponentOptionsWithObjectProps } from 'vue';

import { toHandlerKey } from '@vue/shared';

import {
  KeyHash,
  toVNodes,
  camelize,
  hyphenate,
  callHooks,
  setInitialProps,
  createCustomEvent,
  convertAttributeValue
} from './utils'

/**
 * Vue 3 wrapper to convert a Vue component into Web Component. Supports reactive attributes, events & slots.
 * @param component: Component - Component object created using Vue's defineComponent function
 * @param eventNames: string[] - Event names to be fired in kabab case. Events must be added using addEventListener, inline events doesnt work as of now.
*/
export default function wrap (component: Component, eventNames: string[] = []) {

  const componentObj: ComponentOptionsWithObjectProps = <ComponentOptionsWithObjectProps>component;

  let isInitialized = false;

  let hyphenatedPropsList: string[];
  let camelizedPropsList: string [];
  let camelizedPropsMap: KeyHash;

  function initialize () {
    if (isInitialized) return;

    // extract props info
    const propsList: string[] = Array.isArray(componentObj.props)
      ? componentObj.props
      : Object.keys(componentObj.props || {})
    hyphenatedPropsList = propsList.map(hyphenate)
    camelizedPropsList = propsList.map(camelize)

    const originalPropsAsObject = Array.isArray(componentObj.props) ? {} : componentObj.props || {}
    camelizedPropsMap = camelizedPropsList.reduce((map: KeyHash, key, i) => {
      map[key] = originalPropsAsObject[propsList[i]]
      return map
    }, {})

    isInitialized = true;
  }

  class CustomElement extends HTMLElement {
    _wrapper: App;
    _component?: ComponentPublicInstance;

    _props!: KeyHash;
    _slotChildren!: (VNode | null)[];
    _emit!: Function;
    _mounted: boolean = false;

    constructor () {
      super()

      const eventProxies = this.createEventProxies(eventNames);

      this._props = {};
      this._slotChildren = [];

      const self = this;
      this._wrapper = createApp({
        render () {
          return h(componentObj, Object.assign({}, self._props, eventProxies), () => self._slotChildren);
        },
        mounted() {
          self._mounted = true;
        },
        unmounted() {
          self._mounted = false;
        }
      });

      // Use MutationObserver to react to future attribute & slot content change
      const observer = new MutationObserver(mutations => {
        let hasChildrenChange = false;

        for (let i = 0; i < mutations.length; i++) {
          const m = mutations[i]

          if (isInitialized && m.type === 'attributes' && m.target === this) {
            if(m.attributeName) {
              this.syncAttribute(m.attributeName);
            }
          } else {
            hasChildrenChange = true;
          }
        }

        if (hasChildrenChange) {
          //this.syncSlots(); Commenting as this is causing an infinit $forceUpdate loop, will fix if required!
        }
      });

      observer.observe(this, {
        childList: true,
        subtree: true,
        characterData: true,
        attributes: true
      });
    }

    createEventProxies(eventNames: string[]): { [name: string]: Function } {
      const eventProxies: { [name: string]: Function } = {};

      eventNames.forEach(name => {
        let handlerName = toHandlerKey(camelize(name))
        eventProxies[handlerName] = (...args: any[]): void => {
          this.dispatchEvent(createCustomEvent(name, args));
        };
      });

      return eventProxies;
    }

    syncAttribute(key: string): void {
      const camelized = camelize(key);
      const value = this.hasAttribute(key) ? this.getAttribute(key) : undefined;

      this._props[camelized] = convertAttributeValue(
        value,
        key,
        camelizedPropsMap[camelized]
      );

      this._component?.$forceUpdate();
    }

    syncSlots(): void {
      this._slotChildren = toVNodes(this.childNodes);
      this._component?.$forceUpdate();
    }

    syncInitialAttributes(): void {
      this._props = setInitialProps(camelizedPropsList);

      hyphenatedPropsList.forEach(key => {
        this.syncAttribute(key);
      })
    }

    connectedCallback () {
      if (!this._component || !this._mounted) {

        if (isInitialized) {
          // initialize attributes
          this.syncInitialAttributes();
        }

        // initialize children
        this.syncSlots();

        // Mount the component
        this._component = this._wrapper.mount(this);

      } else {
        // Call mounted on re-insert
        callHooks(this._component, 'mounted')
      }
    }

    disconnectedCallback () {
      callHooks(this._component, 'unmounted');
    }
  }

  initialize();

  return CustomElement
}
