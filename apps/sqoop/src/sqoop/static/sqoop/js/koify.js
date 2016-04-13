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


var koify = (function($, undefined) {
  function KOClass(fn, attrs) {
    var _cclass = cclass.create(fn, attrs);

    function reset_extends(fn, cclass) {
      cclass._extend = cclass.extend;
      cclass.extend = function() {
        var args = [fn];
        args.push.apply(args, arguments);
        var _fn = reset_extends(fn, cclass._extend.apply(cclass, args));
        return _fn;
      }
      return cclass;
    }

    return reset_extends(fn, _cclass);
  }

  var Model = KOClass(function(attrs) {
    var self = this;
    var attrs = attrs || {};
    $.extend(self, self.initialize(attrs));
    $.extend(self, self);  // Add attributes in prototype chain
  }, {
    initialize: function(attrs) {
      return attrs;
    }
  });


  var MinimalNode = KOClass(function(options) {
    var self = this;
    var options = options || {};

    self.options = options;
    self.initialize(options);
  }, {
    model_class: undefined,

    initialize: function(options) {
      var self = this;

      if (options.modelDict) {
        self.model = new self.model_class(options.modelDict);
      } else {
        self.model = $.extend(true, {}, options.model);
      }

      self.map();
    },
    map: function() {
      var self = this;
      var mapping_options = {
        'ignore': ['parent', 'initialize']
      };
      if ('__ko_mapping__' in self) {
        ko.mapping.fromJS(self.model, mapping_options, self);
      } else {
        var mapped = ko.mapping.fromJS(self.model, mapping_options);
        $.extend(self, mapped);
      }
    }
  });


  var Node = MinimalNode.extend({
    persist: true,
    identifier: undefined,

    request: function(url, options) {
      var self = this;
      var request = $.extend({
        url: url,
        dataType: 'json',
        type: 'GET',
        success: $.noop,
        error: $.noop
      }, options || {});
      $.ajax(request);
    },
    load: function(options) {
      var self = this;
      $(document).trigger('load.' + self.identifier, [self, options]);
      var options = $.extend({
        success: function(data) {
          switch(data.status) {
            case 0:
              self.initialize({modelDict: data[self.identifier]});
              $(document).trigger('loaded.' + self.identifier, [self, options]);
            break;
            default:
            case 1:
              $(document).trigger('load_fail.'  + self.identifier, [self, options, data]);
            break;
          }
        }
      }, options);
      self.request(self.loadUrl(), options);
    },
    save: function(options) {
      if (!this.persist) {
        return;
      }

      var self = this;
      $(document).trigger('save.' + self.identifier, [self, options]);
      var options = $.extend({
        type: 'POST',
        data: self.getData(),
        success: function(data) {
          switch(data.status) {
            case 0:
              $(document).trigger('saved.' + self.identifier, [self, options, data]);
            break;
            default:
            case 1:
              $(document).trigger('save_fail.' + self.identifier, [self, options, data]);
            break;
          }
        }
      }, options);
      self.request(self.saveUrl(), options);
    },
    clone: function(options) {
      if (!this.persist) {
        return;
      }

      var self = this;
      $(document).trigger('clone.' + self.identifier, [self, options]);
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          switch(data.status) {
            case 0:
              $(document).trigger('cloned.' + self.identifier, [self, options, data]);
            break;
            default:
            case 1:
              $(document).trigger('clone_fail.' + self.identifier, [self, options, data]);
            break;
          }
        }
      }, options);
      self.request(self.cloneUrl(), options);
    },
    delete: function(options) {
      if (!this.persist) {
        return;
      }

      var self = this;
      $(document).trigger('delete.' + self.identifier, [self, options]);
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          switch(data.status) {
            case 0:
              $(document).trigger('deleted.' + self.identifier, [self, options, data]);
            break;
            default:
            case 1:
              $(document).trigger('delete_fail.' + self.identifier, [self, options, data]);
            break;
          }
        }
      }, options);
      self.request(self.deleteUrl(), options);
    },
    getData: function() {
      var self = this;
      var model = ko.sqoop.fixModel(self);
      var data = {};
      data[self.identifier] = ko.utils.stringifyJson(model);
      return data;
    },
    loadUrl: function(persist) {
      var self = this;
      return self.base_url + ((persist) ? self.id() : '');
    },
    saveUrl: function() {
      var self = this;
      if (self.id() > -1) {
        return self.base_url +  self.id();
      } else {
        return self.base_url;
      }
    },
    cloneUrl: function() {
      var self = this;
      return self.base_url +  self.id() + '/clone';
    },
    deleteUrl: function() {
      var self = this;
      return self.base_url +  self.id() + '/delete';
    }
  });

  return {
    'KOClass': KOClass,
    'MinimalNode': MinimalNode,
    'Node': Node,
    'Model': Model
  }
})($, undefined);
