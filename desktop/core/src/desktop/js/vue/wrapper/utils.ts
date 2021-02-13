import { ComponentPublicInstance, h, VNode } from "vue";

export type KeyHash = { [key: string]: any };

const camelizeRE = /-(\w)/g
export const camelize = (str: string): string => {
  return str.replace(camelizeRE, (_, c) => c ? c.toUpperCase() : '')
}

const hyphenateRE = /\B([A-Z])/g
export const hyphenate = (str: string): string => {
  return str.replace(hyphenateRE, '-$1').toLowerCase()
}

export function setInitialProps(propsList: string[]): KeyHash {
  const res: KeyHash = {}
  propsList.forEach(key => {
    res[key] = undefined
  })
  return res
}

export function injectHook (options: KeyHash, key: string, hook: Function) {
  options[key] = [].concat(options[key] || [])
  options[key].unshift(hook)
}

export function callHooks (vm: ComponentPublicInstance | undefined, hook: string) {
  if (vm) {
    const hooks = vm.$options[hook] || [];
    hooks.forEach((hook: Function) => {
      hook.call(vm)
    });
  }
}

export function createCustomEvent (name: string, args: any) {
  return new CustomEvent(name, {
    bubbles: false,
    cancelable: false,
    detail: args
  })
}

const isBoolean = (val: any) => /function Boolean/.test(String(val));
const isNumber = (val: any) => /function Number/.test(String(val));

export function convertAttributeValue (value: any, name: string, { type }: { type?: any } = {}) {
  if (isBoolean(type)) {
    if (value === 'true' || value === 'false') {
      return value === 'true';
    }
    if (value === '' || value === name) {
      return true;
    }
    return value != null;
  } else if (isNumber(type)) {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? value : parsed;
  } else {
    return value;
  }
}

export function toVNodes (children: NodeListOf<ChildNode>): (VNode | null)[] {
  const res: (VNode | null)[] = [];

  for (let i = 0, l = children.length; i < l; i++) {
    res.push(toVNode(children[i]));
  }

  return res;
}

function toVNode (node: any): VNode | null {
  if (node.nodeType === 3) {
    return node.data.trim() ? node.data : null;
  } else if (node.nodeType === 1) {
    const data = {
      attrs: getAttributes(node),
      domProps: {
        innerHTML: node.innerHTML
      }
    };

    if (data.attrs.slot) {
      data.slot = data.attrs.slot;
      delete data.attrs.slot;
    }

    return h(node.tagName, data);
  } else {
    return null
  }
}

function getAttributes (node: any): KeyHash {
  const res: KeyHash = {};
  for (let i = 0, l = node.attributes.length; i < l; i++) {
    const attr = node.attributes[i];
    res[attr.nodeName] = attr.nodeValue;
  }
  return res;
}
