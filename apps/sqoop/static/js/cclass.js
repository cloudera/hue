// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * cclass is a javascript Class inheritance implementation
 *
 * Example Usage:
 * var A = cclass.create(function() {
 *   this.instance_member = 'foo';
 * }, {
 *  test: function() {;
 *    // do something!!!
 *  }});
 *
 * var B = A.extend(function() {
 *   this.__proto__.constructor();
 * }, {
 *   static_member: 'bob',
 *   test: function(){
 *     this.parent.test();
 *   }
 * });
 *
 * var a = new B();
 * a.test();
 *
 */
var cclass = (function($, undefined) {
  function extend(ext_fn, attrs) {
    function parent() {};
    function fn() {
      ext_fn.apply(this, arguments);
    };
    parent.prototype = this.prototype;
    fn.prototype = new parent();
    fn.prototype.constructor = fn;
    fn.extend = extend;
    $.extend(fn.prototype, attrs || {}, {
        parent: parent.prototype
    });
    return fn;
  }

  return {
    create: function(fn, attrs) {
      $.extend(fn.prototype, attrs || {});
      fn.extend = extend;
      fn.parent = undefined;
      return fn;
    },
    extend: extend
  };
})($, undefined);
