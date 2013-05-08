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
  options.data = ($.type(options.data) == "string") ? $.parseJSON(options.data) : options.data;
  if ($.isArray(options.data)) {
    var mapping =  ko.mapping.fromJS(options.data);
    $.each(mapping(), function(index, value) {
      subscribe(value);
    });
    return mapping;
  } else {
    var mapping =  ko.mapping.fromJS(options.data, {});
    subscribe(mapping);
    return mapping;
  }
};

// Maps JSON strings to fields in the view model.
var MAPPING_OPTIONS = {
  ignore: ['initialize', 'toString', 'copy'],
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
      return map_params(options, function() {});
    },
    update: function(options) {
      return map_params(options, function() {});
    },
  },
  mkdirs: {
    create: function(options) {
      return map_params(options, function() {});
    },
    update: function(options) {
      return map_params(options, function() {});
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
       return map_params(options, function() {});
     },
     update: function(options) {
       return map_params(options, function() {});
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
  job_xml: ''
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
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
  child_links: []
});

var GenericModel = ModelModule($);
$.extend(GenericModel.prototype, {
  id: 0,
  name: '',
  description: '',
  node_type: 'generic',
  workflow: 0,
  xml: '',
  child_links: []
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