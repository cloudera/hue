// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/navbar
 * @description
 * <cui-navbar> is a wrapper component that contains nav components and html.
 * You mainly want to use cui-navbar so you can get the css styling.
 * Your context is not altered using cui-navbar, so $parent inside cui-navbar references $parent outside cui-navbar.
 * @example
 * <cui-navbar>
 *  <div>Anything you want</div>
 *  <ko-some-other-component></ko-some-other-component>
 * </cui-navbar>
 */
var componentUtils = require('cloudera-ui/ko/components/componentUtils');

/**
 * @constructor
 * @alias module:ko/components/navbar
 * @param {object} params The component params, not used.
 * @param {object} componentInfo contains extra knockout node info.
 * @param {Node[]} componentInfo.templateNodes A list of the nodes that were in the component before injecting the component template html.
 */
function NavbarWrapper(params, componentInfo) {
  this.content = componentInfo.templateNodes;
}

componentUtils.addComponent(NavbarWrapper, 'cui-navbar', `
<div class="cui-navbar">
<!-- ko componentContextEscaper -->
<!-- ko template: { nodes: $component.content, data: $data } -->
<!-- /ko -->
<!-- /ko -->
</div>
`);

module.exports = NavbarWrapper;
