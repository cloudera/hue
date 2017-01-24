// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module utils/guid
 * @description GUID related code.
 */

module.exports = {
  /**
   * Generates a new guid.
   * @return {string}
   * @see http://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid-in-javascript
   * @example
   * var id = guid.generate();
   */
  generate: function() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      /*jshint bitwise: false */
      /*jslint bitwise: true */
      var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      /*jslint bitwise: false */
      /*jshint bitwise: true */
      return v.toString(16);
    });
  }
};
