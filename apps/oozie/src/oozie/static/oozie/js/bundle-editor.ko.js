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


var Bundle = function (vm, bundle) {

  var self = this;

  self.id = ko.observable(typeof bundle.id != "undefined" && bundle.id != null ? bundle.id : null);
  self.uuid = ko.observable(typeof bundle.uuid != "undefined" && bundle.uuid != null ? bundle.uuid : hueUtils.UUID());
  self.name = ko.observable(typeof bundle.name != "undefined" && bundle.name != null ? bundle.name : "");

  self.coordinators = ko.mapping.fromJS(typeof bundle.coordinators != "undefined" && bundle.coordinators != null ? bundle.coordinators : []);
  self.properties = ko.mapping.fromJS(typeof bundle.properties != "undefined" && bundle.properties != null ? bundle.properties : {});

  self.tracker = new ChangeTracker(self, ko);  // from ko.common-dashboard.js

  self.isDirty = ko.computed(function () {
    return self.tracker().somethingHasChanged();
  });

  self.addCoordinator = function (coordinator_uuid) {
    self.getCoordinatorParameters(coordinator_uuid);
  };

  self.getCoordinatorParameters = function (uuid) {
    $.get("/oozie/editor/coordinator/parameters/", {
      "uuid": uuid,
    }, function (data) {
      var _var = {
        'coordinator': uuid,
        'properties': data.parameters
      };

      self.coordinators.push(ko.mapping.fromJS(_var));
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
}


var BundleEditorViewModel = function (bundle_json, coordinators_json, can_edit_json) {
  var self = this;

  self.canEdit = ko.mapping.fromJS(can_edit_json);
  self.isEditing = ko.observable(bundle_json.id == null);
  self.isEditing.subscribe(function (newVal) {
    $(document).trigger("editingToggled");
  });
  self.toggleEditing = function () {
    self.isEditing(!self.isEditing());
  };
  self.isSaving = ko.observable(false);

  self.bundle = new Bundle(self, bundle_json);

  self.coordinators = ko.mapping.fromJS(coordinators_json);

  self.coordinatorModalFilter = ko.observable("");
  self.filteredModalCoordinators = ko.computed(function () {
    var _filter = self.coordinatorModalFilter().toLowerCase();
    if (!_filter) {
      return self.coordinators();
    }
    else {
      return ko.utils.arrayFilter(self.coordinators(), function (coord) {
        return coord.name().toLowerCase().indexOf(_filter.toLowerCase()) > -1;
      });
    }
  }, self);

  self.getCoordinatorById = function (uuid) {
    var _coords = ko.utils.arrayFilter(self.coordinators(), function (coord) {
      return coord.uuid() == uuid;
    });
    if (_coords.length > 0) {
      return _coords[0];
    }
    return null;
  }

  self.addBundledCoordinator = function (uuid) {
    self.bundle.addCoordinator(uuid);
  };


  self.save = function () {
    if (!self.isSaving()) {
      self.isSaving(true);
      $.post("/oozie/editor/bundle/save/", {
        "bundle": ko.mapping.toJSON(self.bundle)
      }, function (data) {
        if (data.status == 0) {
          if (self.bundle.id() == null) {
            shareViewModel.setDocUuid(data.uuid);
          }
          self.bundle.id(data.id);
          self.bundle.tracker().markCurrentStateAsClean();
          $(document).trigger("info", data.message);
          hueUtils.changeURL('/hue/oozie/editor/bundle/edit/?bundle=' + data.id);
        }
        else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      }).always(function () {
        self.isSaving(false);
      });
    }
  };

  self.showSubmitPopup = function () {
    // If self.bundle.id() == null, need to save wf for now
    $(".jHueNotify").remove();
    if (!self.bundle.isDirty()) {
      hueAnalytics.log('oozie/editor/bundle', 'submit');
      $.get("/oozie/editor/bundle/submit/" + self.bundle.id(), {
        format: 'json'
      }, function (data) {
        $(document).trigger("showSubmitPopup", data);
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
  };
};
