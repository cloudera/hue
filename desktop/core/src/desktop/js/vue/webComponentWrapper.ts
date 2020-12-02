import axios from 'axios';
import Vue, { ComponentOptions } from 'vue';
import vueCustomElement from 'vue-custom-element';

Vue.use(vueCustomElement);

export interface HueComponentOptions<T extends Vue> extends ComponentOptions<T> {
  hueBaseUrl?: string;
}

export const wrap = <T extends Vue>(tag: string, component: { new (): T }): void => {
  Vue.customElement(tag, new component().$options, {
    connectedCallback() {
      const element = <HTMLElement>this;
      const hueBaseUrl = element.getAttribute('hue-base-url');
      if (hueBaseUrl) {
        axios.defaults.baseURL = hueBaseUrl;
      }
    }
  });
};
