import axios from 'axios';
import AceEditor from './AceEditor.vue';
import { wrap } from 'vue/webComponentWrapper';

wrap('query-editor', AceEditor, {
  connectedCallback() {
    const element = <HTMLElement>this;
    const hueBaseUrl = element.getAttribute('hue-base-url');
    if (hueBaseUrl) {
      axios.defaults.baseURL = hueBaseUrl;
    }
  }
});
