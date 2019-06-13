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

    self.options = options || {
      model: {}
    };
    self.model = self.options.model;

    self.initialize(options);
  };

  // NodeFields is defined in oozie/static/js/workflow.node-fields.js.
  // It provides the more advanced field manipulation for the fields
  // that hava JSON representation.
  $.extend(module.prototype, NodeFields, {
    initialize: function(options) {
      var self = this;

      $(document).trigger('initialize.design', [options, self]);

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
      // MAPPING_OPTIONS comes from /oozie/static/js/workflow.models.js
      // We don't update the observed object using ko.mapping because
      // the plugin does not work with mixed objects.
      ko.mapping.fromJS(self.model, $.extend({
        is_shared: {
          create: function(options) {
            return ko.observable(($.type(options.data) == "string") ? value.toLowerCase() == "true" : new Boolean(options.data).valueOf());
          },
          update: function(options) {
            return ($.type(options.data) == "string") ? value.toLowerCase() == "true" : new Boolean(options.data);
          }
        },
        parameters: {
          // Will receive individual objects to subscribe.
          // Containing array is mapped automagically
          create: function(options) {
            var parent = options.parent;
            var subscribe = function(mapping) {
              mapping.name.subscribe(function(value) {
                parent.parameters.valueHasMutated();
              });
              mapping.value.subscribe(function(value) {
                parent.parameters.valueHasMutated();
              });
            };

            return map_params(options, subscribe);
          },
          update: function(options) {
            var parent = options.parent;
            var subscribe = function(mapping) {
              mapping.name.subscribe(function(value) {
                parent.parameters.valueHasMutated();
              });
              mapping.value.subscribe(function(value) {
                parent.parameters.valueHasMutated();
              });
            };

            return map_params(options, subscribe);
          }
        }
      }, MAPPING_OPTIONS), self);

      if ('files' in self) {
        var files = self.files();
        self.files = ko.observableArray([]);

        // ['file', ...] => [{'name': 'file', 'dummy': ''}, ...].
        $.each(files, function(index, filename) {
          var prop = { name: ko.observable(filename), dummy: ko.observable("") };
          prop.name.subscribe(function(value) {
            self.files.valueHasMutated();
          });
          prop.dummy.subscribe(function(value) {
            self.files.valueHasMutated();
          });
          self.files.push(prop);
        });
      }

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
        self['new'] = ko.computed(function() {
          return !self.id();
        });
      }

      if (!('editable' in self)) {
        self.editable = ko.observable(false);
      }

      $(document).trigger('initialized.design', [options, self]);
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
          $(document).trigger('load.design', [options, data, self]);
          self.is_dirty(false);
          self.initialize({model: data});
          $(document).trigger('loaded.design', [options, data, self]);
        }
      }, options);
      this.request('/jobsub/designs/' + self.id(), options);
    },
    save: function(options) {
      // First try to save, then update error list if fail.
      // Response should be json object. IE: {data: {errors: {files: ['example', ...], ... }}}
      var self = this;
      $(document).trigger('save.design', [options]);
      var model_dict = {};
      $.each(ko.mapping.toJS(self), function(key, value) {
        if (key != 'errors') {
          if (key == 'files') {
            // [{'name': 'file', 'dummy': ''}, ...] => ['file', ...].
            var files = ko.utils.unwrapObservable(value);
            model_dict[key] = [];
            $.each(files, function(i, value) {
              model_dict[key].push(value.name);
            });
          } else {
            model_dict[key] = ko.utils.unwrapObservable(value);
          }
        }
      });
      var data = normalize_model_fields(JSON.parse(JSON.stringify(model_dict)));
      var options = $.extend({
        type: 'POST',
        data: data,
        error: function(xhr) {
          var response = JSON.parse(xhr.responseText);
          if (response) {
            var model = ko.mapping.toJS(self);
            $.extend(model.errors, response.data.errors);
            ko.mapping.fromJS(model, self);
            $(document).trigger('error.design', [options, data]);
          }
        },
        success: function(data) {
          $(document).trigger('saved.design', [options, data]);
          $(document).trigger('reload.designs');
        }
      }, options);
      self.request((self['new']()) ? '/jobsub/designs/'+self.node_type()+'/new' : '/jobsub/designs/'+self.id()+'/save', options);
    },
    clone: function(options) {
      var self = this;
      $(document).trigger('clone.design', [options]);
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          $(document).trigger('cloned.design', [options, data]);
          $(document).trigger('reload.designs');
        }
      }, options);
      this.request('/jobsub/designs/' + self.id() + '/clone', options);
    },
    'delete': function(skip_trash, options) {
      var self = this;
      $(document).trigger('delete.design', [options]);
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          $(document).trigger('deleted.design', [options, data]);
          $(document).trigger('reload.designs');
        }
      }, options);
      if (skip_trash) {
        this.request('/jobsub/designs/' + self.id() + '/delete?skip_trash=true', options);
      } else {
        this.request('/jobsub/designs/' + self.id() + '/delete', options);
      }
    },
    restore: function(options) {
      var self = this;
      $(document).trigger('restore.design', [options]);
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          $(document).trigger('restored.design', [options, data]);
          $(document).trigger('reload.designs');
        }
      }, options);
      this.request('/jobsub/designs/' + self.id() + '/restore', options);
    },

    // More node field methods
    addParameter: function(data) {
      var self = this;
      var prop = { name: ko.observable(""), value: ko.observable("") };
      prop.name.subscribe(function(value) {
        self.parameters.valueHasMutated();
      });
      prop.value.subscribe(function(value) {
        self.parameters.valueHasMutated();
      });
      self.parameters.push(prop);
      $(document).trigger('add.parameter.workflow', [data]);
    },
    removeParameter: function(data) {
      var self = this;
      self.parameters.remove(data);
      $(document).trigger('remove.parameter.workflow', [data]);
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
    self.inTrash = ko.observable(false);
    self.isEditing = ko.observable(false);
    self.isLoading = ko.observable(false);
    self.designs = ko.observableArray([]);
    self.trashedDesignObjects = ko.computed(function() {
      var selected = [];
      $.each(self.designs(), function(index, designObject) {
        if (designObject.design().is_trashed()) {
          selected.push(designObject);
        }
      });
      return selected;
    });
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
      return self.selectedDesignObjects().length == self.designs().length && self.selectedDesignObjects().length > 0;
    });

    self.initialize(options);
  };

  $.extend(module.prototype, {
    initialize: function(options) {
      var self = this;
      $(document).trigger('initialize.designs', [options, self]);

      self.options = $.extend(self.options, options);

      self.designs.removeAll();
      self.designs(self.createDesigns(self.options.models));
      self.temporary({
        design: ko.observable(null),
        selected: ko.observable(false),
        template: ko.observable(null)
      })
      self.deselectAll();

      $(document).trigger('initialized.designs', [options, self]);
    },
    load: function(options) {
      // Fetch designs from backend.
      var self = this;
      var request = $.extend({
        url: '/jobsub/designs',
        dataType: 'json',
        type: 'GET',
        success: function(data) {
          // data = { designs: designs: [ {'is_trashed': ..., ...}, ... ] }
          $(document).trigger('load.designs', [options, data]);
          self.initialize({models: data.designs});
          $(document).trigger('loaded.designs', [options, data]);
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
      var designs = [];
      $.each(models, function(index, model) {
        designs.push({
          design: ko.observable(self.createDesign(model)),
          selected: ko.observable(false),
          template: ko.observable(model.node_type)
        });
      });
      return designs;
    },
    toggleSelect: function(index) {
      var self = this;
      self.designs()[index].selected(!self.designs()[index].selected());
    },
    selectByIndex: function(index) {
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
    getDesignObjectById: function(id) {
      var self = this;
      var designObjects = ko.utils.arrayFilter(self.designs(), function(value) {
        return value.design().id() == id;
      });
      return (designObjects.length > 0) ? designObjects[0] : null;
    },

    //// Design delegation
    newDesign: function(node_type) {
      var self = this;
      $(document).trigger('create.design', [design]);
      var design = self.createDesign({
        id: null,
        node_type: node_type,
        is_shared: true,
        parameters: '[{"name":"oozie.use.system.libpath","value":"true"}]'
      });
      // Reversing the order of the next two statements may cause KO to break.
      self.temporary().template(node_type);
      self.temporary().design(design);
      // Do not do any thing with any other design.
      self.deselectAll();
      $(document).trigger('created.design', [design]);
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
    trashDesigns: function() {
      var self = this;
      $.each(self.selectedDesignObjects(), function(index, designObject) {
        designObject.design()['delete']();
      });
    },
    destroyDesigns: function() {
      var self = this;
      $.each(self.selectedDesignObjects(), function(index, designObject) {
        designObject.design()['delete'](true);
      });
    },
    destroyAllTrashedDesigns: function() {
      var self = this;
      $.each(self.trashedDesignObjects(), function(index, designObject) {
        designObject.design()['delete'](true);
      });
    },
    restoreDesigns: function() {
      var self = this;
      $.each(self.selectedDesignObjects(), function(index, designObject) {
        designObject.design().restore(true);
      });
    },
    editDesign: function(index) {
      var self = this;
      $(document).trigger('edit.design', [design]);
      if (self.selectedDesignObject()) {
        var design = self.selectedDesignObject().design();
        if (design.is_dirty()) {
          $(document).one('loaded.design', function(e, options, data, design) {
            self.temporary().design(design);
            self.temporary().template(self.selectedDesignObject().template());
            $(document).trigger('edited.design', [design]);
          });
          design.load();
        } else {
          self.temporary().design(design);
          self.temporary().template(self.selectedDesignObject().template());
          $(document).trigger('edited.design', [design]);
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
