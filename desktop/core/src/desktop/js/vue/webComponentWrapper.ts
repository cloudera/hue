import Vue, { ComponentOptions } from 'vue';
import VueCustomElement from 'vue-custom-element';
import vueCustomElement from 'vue-custom-element';

Vue.use(vueCustomElement);

export interface HueComponentOptions<T extends Vue> extends ComponentOptions<T> {
  hueBaseUrl?: string;
}

export const wrap = <T extends Vue>(
  tag: string,
  component: { new (): T },
  options?: VueCustomElement.options
): void => {
  Vue.customElement(tag, new component().$options, options);
};
