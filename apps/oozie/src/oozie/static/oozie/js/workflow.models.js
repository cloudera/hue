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

// Since knockout maps arrays without calling "update" nor "create"
// Provide a JSON string that will be parsed in custom 'create' and 'update' functions.
// These serialized values are also stored in the backend.
var MODEL_FIELDS_JSON = ['parameters', 'job_properties', 'files', 'archives', 'prepares', 'params',
                   'deletes', 'mkdirs', 'moves', 'chmods', 'touchzs'];
var DEFAULT_SLA = [
    {'key': 'enabled', 'value': false},
    {'key': 'nominal-time', 'value': ''},
    {'key': 'should-start', 'value': ''},
    {'key': 'should-end', 'value': ''},
    {'key': 'max-duration', 'value': ''},
    {'key': 'alert-events', 'value': ''},
    {'key': 'alert-contact', 'value': ''},
    {'key': 'notification-msg', 'value': ''},
    {'key': 'upstream-apps', 'value': ''}
];

function getDefaultData() {
  return {
    'sla': DEFAULT_SLA.slice(0),
    'credentials': []
  };
}

function normalize_model_fields(node_model) {
  $.each(MODEL_FIELDS_JSON, function(index, field) {
    if (field in node_model && $.isArray(node_model[field])) {
      node_model[field] = JSON.stringify(node_model[field]);
    }
  });
  return node_model;
}

// Parse JSON if it is JSON and appropriately map.
// Apply subscriber to each mapping.
var map_params = function(options, subscribe) {
  options.data = ($.type(options.data) == "string") ? JSON.parse(options.data) : options.data;
  if ($.isArray(options.data)) {
    var mapping =  ko.mapping.fromJS(options.data);
    $.each(mapping(), function(index, value) {
      subscribe(value);
    });
    return mapping;
  } else {
    var mapping = ko.mapping.fromJS(options.data, {});
    subscribe(mapping);
    return mapping;
  }
};

// Find all members of the data and apply appropriate mapping.
// Arrays might contain literals or plain objects.
// Plain objects should have their members mapped and literals should
// be replaced with observables.
// Plain object members will notify their containing arrays when they update.
// Literals will notify their containing arrays when they've changed.
var map_data = function(options) {
  var data = {};
  options.data = ($.type(options.data) == "string") ? JSON.parse(options.data) : options.data;
  $.each(options.data, function(member, value) {
    // @TODO: Should we support unstructureed data as children?
    if ($.isArray(value)) {
      // @TODO: Support more than {'member': 'value',...} and 'value'.
      data[member] = ko.observableArray();
      $.each(value, function(index, object_or_literal) {
        if ($.isPlainObject(object_or_literal)) {
          var obj = {};
          $.each(object_or_literal, function(key, literal) {
            obj[key] = ko.mapping.fromJS(literal);
            obj[key].subscribe(function() {
              data[member].valueHasMutated();
            });
          });
          data[member].push(obj);
        } else {
          var literal = ko.mapping.fromJS(object_or_literal);
          data[member].push(literal);
          literal.subscribe(function() {
            data[member].valueHasMutated();
          });
        }
      });
    } else {
      data[member] = ko.mapping.fromJS(value);
    }
  });
  return data;
};

// Maps JSON strings to fields in the view model.
var MAPPING_OPTIONS = {
  ignore: ['initialize', 'toString', 'copy'], // Do not support cancel edit on data
  job_properties: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.job_properties.valueHasMutated();
        });
        mapping.value.subscribe(function(value) {
          parent.job_properties.valueHasMutated();
        });
      };

      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.job_properties.valueHasMutated();
        });
        mapping.value.subscribe(function(value) {
          parent.job_properties.valueHasMutated();
        });
      };

      return map_params(options, subscribe);
    }
  },
  files: {
    create: function(options) {
      return map_params(options, function() {});
    },
    update: function(options) {
      return map_params(options, function() {});
    }
  },
  archives: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.archives.valueHasMutated();
        });
        mapping.dummy.subscribe(function(value) {
          parent.archives.valueHasMutated();
        });
      };

      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.archives.valueHasMutated();
        });
        mapping.dummy.subscribe(function(value) {
          parent.archives.valueHasMutated();
        });
      };

      return map_params(options, subscribe);
    }
  },
  params: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.value.subscribe(function(value) {
          parent.params.valueHasMutated();
        });
        mapping.type.subscribe(function(value) {
          parent.params.valueHasMutated();
        });
      };

      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.value.subscribe(function(value) {
          parent.params.valueHasMutated();
        });
        mapping.type.subscribe(function(value) {
          parent.params.valueHasMutated();
        });
      };

      return map_params(options, subscribe);
    }
  },
  prepares: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.value.subscribe(function(value) {
          parent.prepares.valueHasMutated();
        });
        mapping.type.subscribe(function(value) {
          parent.prepares.valueHasMutated();
        });
      };

      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.value.subscribe(function(value) {
          parent.prepares.valueHasMutated();
        });
        mapping.type.subscribe(function(value) {
          parent.prepares.valueHasMutated();
        });
      };

      return map_params(options, subscribe);
    }
  },
  deletes: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.deletes.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.deletes.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    },
  },
  mkdirs: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.mkdirs.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.mkdirs.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    },
  },
  moves: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.source.subscribe(function(value) {
          parent.moves.valueHasMutated();
        });
        mapping.destination.subscribe(function(value) {
          parent.moves.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.source.subscribe(function(value) {
          parent.moves.valueHasMutated();
        });
        mapping.destination.subscribe(function(value) {
          parent.moves.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    }
  },
  chmods: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.path.subscribe(function(value) {
          parent.chmods.valueHasMutated();
        });
        mapping.permissions.subscribe(function(value) {
          parent.chmods.valueHasMutated();
        });
        mapping.recursive.subscribe(function(value) {
          parent.chmods.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.path.subscribe(function(value) {
          parent.chmods.valueHasMutated();
        });
        mapping.permissions.subscribe(function(value) {
          parent.chmods.valueHasMutated();
        });
        mapping.recursive.subscribe(function(value) {
          parent.chmods.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    },
  },
  touchzs: {
    create: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.touchzs.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    },
    update: function(options) {
      var parent = options.parent;
      var subscribe = function(mapping) {
        mapping.name.subscribe(function(value) {
          parent.touchzs.valueHasMutated();
        });
      };
      return map_params(options, subscribe);
    }
  },
  data: {
    create: function(options) {
      return map_data(options);
    },
    update: function(options) {
      return map_data(options);
    }
  }
};

var ModelModule = function($) {
  var module = function(attrs) {
    var self = this;
    $.extend(self, attrs);

    module.prototype.initialize.apply(self, arguments);

    return self;
  };

  $.extend(module.prototype, {
    // Normal stuff
    initialize: function(){},

    toString: function() {
      var self = this;
      return JSON.stringify(self, null, '\t');
    },

    copy: function() {
      var self = this;
      var model = $.extend(true, {}, self);
      $.each(MODEL_FIELDS_JSON, function(i, field) {
        if (field in model && $.type(model[field]) != "string") {
          model[field] = JSON.stringify(model[field]);
        }
      });
      return model;
    }
  });

  return module;
};

function initializeWorkflowData() {
  var self = this;

  self.data = ($.type(self.data) == "string") ? JSON.parse(self.data) : self.data;

  if (! ('sla' in self.data)) {
    self.data['sla'] = DEFAULT_SLA.slice(0);
  }
}

function initializeNodeData() {
  var self = this;

  self.data = ($.type(self.data) == "string") ? JSON.parse(self.data) : self.data;

  if (! ('sla' in self.data)) {
    self.data['sla'] = DEFAULT_SLA.slice(0);
  }

  if (! ('credentials' in self.data)) {
	self.data['credentials'] = getDefaultData()['credentials'].slice(0);
  }
}

var WorkflowModel = ModelModule($);
$.extend(WorkflowModel.prototype, {
  id: 0,
  name: '',
  description: '',
  start: 0,
  end: 0,
  schema_version: 0.4,
  deployment_dir: '',
  is_shared: true,
  parameters: '[]',
  job_xml: '',
  data: getDefaultData(),
  initialize: initializeWorkflowData
});

var NodeModel = ModelModule($);
$.extend(NodeModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: '',
  workflow: 0,
  child_links: []
});

var ForkModel = ModelModule($);
$.extend(ForkModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'fork',
  workflow: 0,
  child_links: []
});

var DecisionModel = ModelModule($);
$.extend(DecisionModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'decision',
  workflow: 0,
  child_links: []
});

var DistCPModel = ModelModule($);
$.extend(DistCPModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'distcp',
  workflow: 0,
  job_properties: '[]',
  prepares: '[]',
  job_xml: '',
  params: '[]',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var MapReduceModel = ModelModule($);
$.extend(MapReduceModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'mapreduce',
  workflow: 0,
  files: '[]',
  archives: '[]',
  job_properties: '[]',
  jar_path: '',
  prepares: '[]',
  job_xml: '',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var StreamingModel = ModelModule($);
$.extend(StreamingModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'streaming',
  workflow: 0,
  files: '[]',
  archives: '[]',
  job_properties: '[]',
  mapper: '',
  reducer: '',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var JavaModel = ModelModule($);
$.extend(JavaModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'java',
  workflow: 0,
  files: '[]',
  archives: '[]',
  job_properties: '[]',
  jar_path: '',
  prepares: '[]',
  job_xml: '',
  main_class: '',
  args: '',
  java_opts: '',
  capture_output: false,
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var PigModel = ModelModule($);
$.extend(PigModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'pig',
  workflow: 0,
  files: '[]',
  archives: '[]',
  job_properties: '[]',
  prepares: '[]',
  job_xml: '',
  params: '[]',
  script_path: '',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var HiveModel = ModelModule($);
$.extend(HiveModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'hive',
  workflow: 0,
  files: '[]',
  archives: '[]',
  job_properties: '[]',
  prepares: '[]',
  job_xml: '',
  params: '[]',
  script_path: '',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var SqoopModel = ModelModule($);
$.extend(SqoopModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'sqoop',
  workflow: 0,
  files: '[]',
  archives: '[]',
  job_properties: '[]',
  prepares: '[]',
  job_xml: '',
  params: '[]',
  script_path: '',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var ShellModel = ModelModule($);
$.extend(ShellModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'shell',
  workflow: 0,
  files: '[]',
  archives: '[]',
  job_properties: '[]',
  prepares: '[]',
  job_xml: '',
  params: '[]',
  command: '',
  capture_output: false,
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var SshModel = ModelModule($);
$.extend(SshModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'ssh',
  workflow: 0,
  user: '',
  host: '',
  params: '[]',
  command: '',
  capture_output: false,
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var FsModel = ModelModule($);
$.extend(FsModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'fs',
  workflow: 0,
  deletes: '[]',
  mkdirs: '[]',
  moves: '[]',
  chmods: '[]',
  touchzs: '[]',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var EmailModel = ModelModule($);
$.extend(EmailModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'email',
  workflow: 0,
  to: '',
  cc: '',
  subject: '',
  body: '',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var SubWorkflowModel = ModelModule($);
$.extend(SubWorkflowModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'subworkflow',
  workflow: 0,
  sub_workflow: 0,
  propagate_configuration: true,
  job_properties: '[]',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

var GenericModel = ModelModule($);
$.extend(GenericModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'generic',
  workflow: 0,
  xml: '',
  child_links: [],
  data: getDefaultData(),
  initialize: initializeNodeData
});

function nodeModelChooser(node_type) {
  switch(node_type) {
    case 'mapreduce':
      return MapReduceModel;
    case 'streaming':
      return StreamingModel;
    case 'java':
      return JavaModel;
    case 'pig':
      return PigModel;
    case 'hive':
      return HiveModel;
    case 'sqoop':
      return SqoopModel;
    case 'shell':
      return ShellModel;
    case 'ssh':
      return SshModel;
    case 'distcp':
      return DistCPModel;
    case 'fs':
        return FsModel;
    case 'email':
        return EmailModel;
    case 'subworkflow':
        return SubWorkflowModel;
    case 'generic':
        return GenericModel;
    case 'fork':
      return ForkModel;
    case 'decision':
      return DecisionModel;
    default:
      return NodeModel;
  }
}