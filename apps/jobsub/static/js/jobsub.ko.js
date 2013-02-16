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
 * Design representation
 */
var Design = (function($, ko, NodeFields) {
  var module = function(options) {
    var self = this;

    self.options = {};
    self.model = {};

    self.initialize(options);
  };

  // NodeFields is defined in oozie/static/js/workflow.node-fields.js.
  // It provides the more advanced field manipulation for the fields
  // that hava JSON representation.
  $.extend(module.prototype, NodeFields, {
    initialize: function(options) {
      var self = this;

      self.options = $.extend(self.options, options);
      self.model = options.model;

      self.model.errors = self.model.errors || {};
      for(var key in self.model) {
        switch(key) {
          case 'initialize':
          case 'toString':
          case 'errors':
          break;
          default:
            if (!(key in self.model.errors)) {
              self.model.errors[key] = [];
            }
          break;
        }
      }

      // @see http://knockoutjs.com/documentation/plugins-mapping.html
      // MAPPING_OPTIONS comes from /oozie/static/js/models.js
      // We don't update the observed object using ko.mapping because
      // the plugin does not work with mixed objects.
      ko.mapping.fromJS(self.model, MAPPING_OPTIONS, self);

      // hack on '<key>ErrorClass' and '<key>Condition'.
      $.each(self.__ko_mapping__, function(key, enabled) {
        if (ko.isObservable(self[key])) {
          self[key+'_condition'] = ko.computed(function() {
            return self[key]().length > 0;
          });
          self[key+'_error_class'] = ko.computed(function() {
            return ( self.errors[key]().length > 0 ) ? 'control-group error' : 'control-group';
          });
        }
      });

      if (!('is_dirty' in self)) {
        self.is_dirty = ko.observable(true);
      }

      if (!('new' in self)) {
        self.new = ko.computed(function() {
          return !self.id();
        });
      }

      $(document).trigger('initialize.design', [options, self]);
    },
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
      var options = $.extend({
        success: function(data) {
          self.is_dirty(false);
          $(document).trigger('load.design', [options, data]);
        }
      }, options);
      this.request('/jobsub/designs/' + self.id(), options);
    },
    save: function(options) {
      // First try to save, then update error list if fail.
      // Response should be json object. IE: {data: {errors: {files: ['example', ...], ... }}}
      var self = this;
      var model_dict = {};
      $.each(ko.mapping.toJS(self), function(key, value) {
        if (key != 'errors') {
          model_dict[key] = ko.utils.unwrapObservable(value);
        }
      });
      var data = normalize_model_fields($.parseJSON(JSON.stringify(model_dict)));
      var options = $.extend({
        type: 'POST',
        data: data,
        error: function(xhr) {
          var response = $.parseJSON(xhr.responseText);
          if (response) {
            var model = ko.mapping.toJS(self);
            $.extend(model.errors, response.data.errors);
            ko.mapping.fromJS(model, self);
            $(document).trigger('error.design', [options, data]);
          }
        },
        success: function(data) {
          $(document).trigger('save.design', [options, data]);
        }
      }, options);
      self.request((self.new()) ? '/jobsub/designs/'+self.node_type()+'/new' : '/jobsub/designs/'+self.id()+'/save', options);
    },
    clone: function(options) {
      var self = this;
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          $(document).trigger('clone.design', [options, data]);
        }
      }, options);
      this.request('/jobsub/designs/' + self.id() + '/clone', options);
    },
    delete: function(options) {
      var self = this;
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          $(document).trigger('delete.design', [options, data]);
        }
      }, options);
      this.request('/jobsub/designs/' + self.id() + '/delete', options);
    }
  });

  return module;
})($, ko, NodeFields);

/**
 * List of designs
 */
var Designs = (function($, ko, NodeModelChooser) {
  var module = function(options) {
    var self = this;

    self.options = options || {
      models: []
    };

    self.temporary = ko.observable();

    self.designs = ko.observableArray([]);
    self.selectedDesignObjects = ko.computed(function() {
      var selected = [];
      $.each(self.designs(), function(index, designObject) {
        if (designObject.selected()) {
          selected.push(designObject);
        }
      });
      return selected;
    });
    self.selectedDesignObject = ko.computed(function () {
      return self.selectedDesignObjects()[0];
    });
    self.selectedDesign = ko.computed(function() {
      if (self.selectedDesignObject()) {
        return self.selectedDesignObject().design();
      } else {
        return null;
      }
    });
    self.selectedIndex = ko.computed(function() {
      var selected = -1;
      $.each(self.designs(), function(index, designObject) {
        if (selected == -1 && designObject.selected()) {
          selected = index;
        }
      });
      return selected;
    });
    self.allSelected = ko.computed(function() {
      return self.selectedDesignObjects().length == self.designs().length;
    });

    self.initialize(options);
  };

  $.extend(module.prototype, {
    initialize: function(options) {
      var self = this;

      self.options = $.extend(self.options, options);

      self.designs.removeAll();
      self.createDesigns(self.options.models);
      self.temporary({
        design: ko.observable(null),
        selected: ko.observable(false),
        template: ko.observable(null)
      })
      self.deselectAll();

      $(document).trigger('initialize.designs', [options, self]);
    },
    load: function(options) {
      // Fetch designs from backend.
      var self = this;
      var request = $.extend({
        url: '/jobsub/designs',
        dataType: 'json',
        type: 'GET',
        success: function(data) {
          $(document).trigger('load.designs', [options, data]);
          self.initialize({models: data});
        },
        error: $.noop
      }, options || {});
      $.ajax(request);
    },
    ensureListFields: function(model) {
      if (!('name' in model)) {
        model.name = '';
      }
      if (!('description' in model)) {
        model.description = '';
      }
      if (!('owner' in model)) {
        model.owner = '';
      }
      if (!('last_modified' in model)) {
        model.last_modified = 0;
      }
      return model;
    },
    createDesign: function(model) {
      var self = this;
      var NodeModel = NodeModelChooser(model.node_type);
      var node_model = new NodeModel(self.ensureListFields(model));
      var design = new Design({model: node_model});
      return design;
    },
    createDesigns: function(models) {
      var self = this;
      $.each(models, function(index, model) {
        self.designs.push({
          design: ko.observable(self.createDesign(model)),
          selected: ko.observable(false),
          template: ko.observable(model.node_type)
        });
      });
    },
    toggleSelect: function(index) {
      var self = this;
      self.designs()[index].selected(!self.designs()[index].selected());
    },
    select: function(index) {
      var self = this;
      self.designs()[index].selected(true);
    },
    toggleSelectAll: function() {
      var self = this;
      if (self.allSelected()) {
        self.deselectAll();
      } else {
        self.selectAll();
      }
    },
    selectAll: function() {
      var self = this;
      $.each(self.designs(), function(index, value) {
        value.selected(true);
      });
    },
    deselectAll: function() {
      var self = this;
      $.each(self.designs(), function(index, value) {
        value.selected(false);
      });
    },

    //// Design delegation
    newDesign: function(node_type) {
      var self = this;
      var design = self.createDesign({
        id: null,
        node_type: node_type
      });
      // Reversing the order of the next two statements may cause KO to break.
      self.temporary().template(node_type);
      self.temporary().design(design);
      $(document).trigger('new.design', [design]);
    },
    saveDesign: function(data, event) {
      var self = this;
      self.temporary().design().save();
    },
    cloneDesigns: function() {
      var self = this;
      $.each(self.selectedDesignObjects(), function(index, designObject) {
        designObject.design().clone();
      });
    },
    deleteDesigns: function() {
      var self = this;
      $.each(self.selectedDesignObjects(), function(index, designObject) {
        designObject.design().delete();
      });
    },
    editDesign: function(index) {
      var self = this;
      if (self.selectedDesignObject()) {
        var design = self.selectedDesignObject().design();
        if (design.is_dirty()) {
          $(document).one('load.design', function(e, options, data) {
            design.initialize({model: data});
            self.temporary().design(design);
            self.temporary().template(self.selectedDesignObject().template());
            $(document).trigger('edit.design', [design, data]);
          });
          design.load();
        } else {
          self.temporary().design(design);
          self.temporary().template(self.selectedDesignObject().template());
          $(document).trigger('edit.design', [design, data]);
        }
      }
    },
    closeDesign: function() {
      var self = this;
      self.temporary().design(null);
      self.temporary().template(null);
    }
  });

  return module;
})($, ko, nodeModelChooser);

var designs = new Designs({models: []});