import Vue from 'vue';
import vueCustomElement from 'vue-custom-element';

Vue.use(vueCustomElement);

export const wrap = <T extends Vue>(tag: string, component: { new (): T }): void => {
  Vue.customElement(tag, new component().$options);
};
