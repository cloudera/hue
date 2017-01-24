// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/navlogo
 *
 * @description
 * <cui-nav-logo> is to be used in conjunction with <cui-navbar>
 * It generates a hyperlink around an image tag with your logo url.
 * @example
 * <cui-navbar>
 *   <div class="navbar-header">
 *     <cui-nav-logo params="logoUrl: logoUrl"></cui-nav-logo>
 *   </div>
 *   <div class="collapse navbar-collapse">
 *   </div>
 * </cui-navbar>
 */
var componentUtils = require('cloudera-ui/ko/components/componentUtils');

/**
 * @constructor
 * @alias module:ko/components/navlogo
 * @param {object} params The component params.
 * @param {string} params.logoUrl The logo url to fetch.
 * @param {string} params.navUrl The url you want to navigate to.
 * @param {string} [params.title] The title for your navbar logo.
 */
function NavLogoComponent(params) {
  /**
   * Attributes to bind to the inner <a> tag.
   * @type {object}
   */
  this.anchorAttrs = {
    href: params.navUrl || '#'
  };
  if (params.title) {
    this.anchorAttrs.title = params.title;
  }

  /**
   * Attributes to bind to the inner <img> tag.
   * @type {object}
   */
  this.imgAttrs = {
    src: params.logoUrl
  };
}

componentUtils.addComponent(NavLogoComponent, 'cui-nav-logo', `
 <a class="cui-nav-logo" data-bind="attr: anchorAttrs">
  <img data-bind="attr: imgAttrs">
 </a>
`);

module.exports = NavLogoComponent;
