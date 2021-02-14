import { ComponentPublicInstance, h, VNode } from 'vue';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type KeyHash = { [key: string]: any };

const camelizeRE = /-(\w)/g;
export const camelize = (str: string): string => {
  return str.replace(camelizeRE, (_, c) => (c ? c.toUpperCase() : ''));
};

const hyphenateRE = /\B([A-Z])/g;
export const hyphenate = (str: string): string => {
  return str.replace(hyphenateRE, '-$1').toLowerCase();
};

export function setInitialProps(propsList: string[]): KeyHash {
  const res: KeyHash = {};
  propsList.forEach(key => {
    res[key] = undefined;
  });
  return res;
}

export function callHooks(vm: ComponentPublicInstance | undefined, hook: string): void {
  if (vm) {
    let hooks = vm.$options[hook] || [];
    if (!Array.isArray(hooks)) {
      hooks = [hooks];
    }
    hooks.forEach((hook: () => void): void => {
      hook.call(vm);
    });
  }
}

export function createCustomEvent(name: string, args: unknown): CustomEvent {
  return new CustomEvent(name, {
    bubbles: false,
    cancelable: false,
    detail: args
  });
}

const isBoolean = (val: unknown) => /function Boolean/.test(String(val));
const isNumber = (val: unknown) => /function Number/.test(String(val));

export function convertAttributeValue(
  value: unknown,
  name: string,
  { type }: { type?: unknown } = {}
): unknown {
  if (isBoolean(type)) {
    if (value === 'true' || value === 'false') {
      return value === 'true';
    }
    if (value === '' || value === name) {
      return true;
    }
    return value != null;
  } else if (isNumber(type)) {
    const parsed = parseFloat(<string>value);
    return isNaN(parsed) ? value : parsed;
  } else {
    return value;
  }
}

export function toVNodes(children: NodeListOf<ChildNode>): (VNode | null)[] {
  const res: (VNode | null)[] = [];

  for (let i = 0, l = children.length; i < l; i++) {
    res.push(toVNode(children[i]));
  }

  return res;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function toVNode(node: any): VNode | null {
  if (node.nodeType === 3) {
    return node.data.trim() ? node.data : null;
  } else if (node.nodeType === 1) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const data: { attrs: any; domProps: any; slot?: any } = {
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
    return null;
  }
}

function getAttributes(node: { attributes: { nodeName: string; nodeValue: unknown }[] }): KeyHash {
  const res: KeyHash = {};
  for (let i = 0, l = node.attributes.length; i < l; i++) {
    const attr = node.attributes[i];
    res[attr.nodeName] = attr.nodeValue;
  }
  return res;
}
