var locale = 'en-US';

import $ from 'jquery';
import ko from 'knockout';
import komapping from 'komapping';
//import singletonLoader from 'ko/components/singletonLoader';
//import commonMessages from 'ko/components/commonMessages';
//import commonModals from 'ko/components/commonModals';
//import i18n         from 'utils/i18n';

//var cuiResources = require('cloudera-ui/locales/' + locale);

//i18n.extend(cuiResources);

// This is only need for apps that don't do applyBindings at the body level.
//singletonLoader.applyBindings();

window.$ = $;
window.ko = ko;
window.ko.mapping = komapping;
//window.commonMessages = commonMessages;
//window.commonModals = commonModals;
