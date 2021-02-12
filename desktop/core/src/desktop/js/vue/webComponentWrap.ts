import { ComponentOptions, Component } from 'vue';
import wrapper from './wrapper/index';

export interface HueComponentOptions<T extends Component> extends ComponentOptions<T> {
  hueBaseUrl?: string;
}

const isRegistered = function(tag: string): boolean {
  return document.createElement(tag).constructor !== HTMLElement;
}

export const wrap = <T extends Component>(
  tag: string,
  component: { new (): T },
  options?: ElementDefinitionOptions
): void => {
  if(!isRegistered(tag)) {
    const customElement: CustomElementConstructor = wrapper(component);
    window.customElements.define(tag, customElement, options);
  }
};
