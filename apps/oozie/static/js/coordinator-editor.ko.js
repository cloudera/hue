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

var Dataset = function (vm, dataset) {
  var self = this;

}


var InputDataset = function (vm, input_dataset) {
  var self = this;
  
  
}


var OutputDataset = function (vm, output_dataset) {
  var self = this;
  
  
}

var Coordinator = function (vm, coordinator) {
  var self = this;

  self.id = ko.observable(typeof coordinator.id != "undefined" && coordinator.id != null ? coordinator.id : null);
  self.uuid = ko.observable(typeof coordinator.uuid != "undefined" && coordinator.uuid != null ? coordinator.uuid : UUID());
  self.name = ko.observable(typeof coordinator.name != "undefined" && coordinator.name != null ? coordinator.name : "");

  self.properties = ko.mapping.fromJS(typeof coordinator.properties != "undefined" && coordinator.properties != null ? coordinator.properties : {});
  self.variables = ko.mapping.fromJS(typeof coordinator.variables != "undefined" && coordinator.variables != null ? coordinator.variables : []);

  self.variablesUI = ko.observableArray(['parameter', 'input_path', 'output_path']);

  self.properties.workflow.subscribe(function(newVal) {
    if (newVal) {
	  $.get("/desktop/api2/doc/get", {
        "uuid": self.properties.workflow()
	   }, function (data) {
	    // set wf
	  }).fail(function (xhr, textStatus, errorThrown) {
	    $(document).trigger("error", xhr.responseText);
	  });
	}
  });
  
  self.addVariable = function() {
    var _var = {       
       'workflow_variable': '',
       
       'dataset_type': 'parameter',
       
       'uuid': UUID(),
       'dataset_variable': '',       
       'show_advanced': false,       
       'done_flag': '',
       'timezone': 'America/Los_Angeles',
       'instance_choice': 'default',
       'is_advanced_start_instance': false,
       'start_instance': '0',
       'advanced_start_instance': '${coord:current(0)}',
       'is_advanced_end_instance': false,
       'advanced_end_instance': '${coord:current(0)}',
       'end_instance': '0',
       'frequency_number': 1,
       'frequency_unit': 'DAYS',
       'start': new Date(),

       'shared_dataset_uuid': '' // If reusing a shared dataset
    };

	self.variables.push(ko.mapping.fromJS(_var));	  
  };
  
  self.init = function() {
    // load
  };
}


var CoordinatorEditorViewModel = function (coordinator_json, credentials_json, workflows_json) {
  var self = this;

  self.isEditing = ko.observable(true);
  self.isEditing.subscribe(function(newVal){
    $(document).trigger("editingToggled");
  });
  self.toggleEditing = function () {
    self.isEditing(! self.isEditing());
  };

  self.workflows = ko.mapping.fromJS(workflows_json);
  self.coordinator = new Coordinator(self, coordinator_json);
  self.credentials = ko.mapping.fromJS(credentials_json);
  
  
  self.save = function () {
    $.post("/oozie/editor/coordinator/save/", {
        "coordinator": ko.mapping.toJSON(self.coordinator)
    }, function (data) {
      if (data.status == 0) {
        self.coordinator.id(data.id);
        $(document).trigger("info", data.message);
        if (window.location.search.indexOf("coordinator") == -1) {
          window.location.hash = '#coordinator=' + data.id;
        }
      }
      else {
        $(document).trigger("error", data.message);
     }
   }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.gen_xml = function () {
	$(".jHueNotify").hide();
	logGA('gen_xml');

    $.post("/oozie/editor/coordinator/gen_xml/", {
        "coordinator": ko.mapping.toJSON(self.coordinator)
    }, function (data) {
      if (data.status == 0) {
        console.log(data.xml);
      }
      else {
        $(document).trigger("error", data.message);
     }
   }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.import_coordinators = function () {
    $.post("/oozie/editor/coordinator/import_coordinators/", {
    }, function (data) {
      if (data.status == 0) {
        console.log(data.json);
      }
      else {
        $(document).trigger("error", data.message);
     }
   }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
  
  self.showSubmitPopup = function () {
    // If self.coordinator.id() == null, need to save wf for now

    $.get("/oozie/editor/coordinator/submit/" + self.coordinator.id(), {
      }, function (data) {
        $(document).trigger("showSubmitPopup", data);
    }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
    });
  };
};


function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('oozie/editor/coordinator/' + page);
  }
}