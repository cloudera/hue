import { createApp, ComponentOptions, Component } from 'vue';
// import wrapper from './wrapper/index';

// Dummy till wrapper is fixed ---
import { CreateAppFunction } from '@vue/runtime-core';
function wrapper(createApp: CreateAppFunction<Element>, component: Component): CustomElementConstructor {
  return null;
}
// Dummy till wrapper is fixed ---

export interface HueComponentOptions<T extends Component> extends ComponentOptions<T> {
  hueBaseUrl?: string;
}

export const wrap = <T extends Component>(
  tag: string,
  component: { new (): T },
  options?: ElementDefinitionOptions
): void => {
  const customElement: CustomElementConstructor = wrapper(createApp, component);
  window.customElements.define(tag, customElement, options);
};
