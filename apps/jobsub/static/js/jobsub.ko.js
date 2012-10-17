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


var Design = function (design) {
    return {
        id:design.id,
        owner:design.owner,
        name:design.name,
        description:design.description,
        type:design.type,
        lastModifiedMillis:design.last_modified,
        lastModified:moment.unix(design.last_modified).format("MMMM DD, YYYY hh:mm a"),
        paramsUrl:design.url_params,
        submitUrl:design.url_submit,
        editUrl:design.url_edit,
        deleteUrl:design.url_delete,
        cloneUrl:design.url_clone,
        canSubmit:design.can_submit,
        canDelete:design.can_delete,
        selected:ko.observable(false),
        handleSelect:function (row, e) {
            this.selected(!this.selected());
        }
    }
}


var JobSubModel = function (designs) {

    var self = this;

    self.designs = ko.observableArray(ko.utils.arrayMap(designs, function (design) {
        return new Design(design);
    }));

    self.isLoading = ko.observable(true);

    self.allSelected = ko.observable(false);

    self.selectedDesigns = ko.computed(function () {
        return ko.utils.arrayFilter(self.designs(), function (design) {
            return design.selected();
        });
    }, self);

    self.selectedDesign = ko.computed(function () {
        return self.selectedDesigns()[0];
    }, self);

    self.selectAll = function () {
        self.allSelected(!self.allSelected());
        ko.utils.arrayForEach(self.designs(), function (design) {
            design.selected(self.allSelected());
        });
        return true;
    };

    self.cloneDesign = function () {
        location.href = self.selectedDesign().cloneUrl;
    };

    self.editDesign = function (design) {
        if (design.editUrl == null) {
            design = self.selectedDesign();
        }
        if (design != null && design.canSubmit) {
            location.href = design.editUrl;
        }
    };

    self.deleteDesign = function () {
        $("#deleteWfForm").attr("action", self.selectedDesign().deleteUrl);
        $("#deleteWfMessage").text(deleteMessage.replace("##PLACEHOLDER##", self.selectedDesign().name));
        $("#deleteWf").modal("show");
    };

    self.submitDesign = function () {
        $("#submitWfForm").attr("action", self.selectedDesign().submitUrl);
        $("#submitWfMessage").text(submitMessage.replace("##PLACEHOLDER##", self.selectedDesign().name));
        // We will show the model form, but disable the submit button
        // until we've finish loading the parameters via ajax.
        $("#submitBtn").attr("disabled", "disabled");
        $("#submitWf").modal("show");

        $.get(self.selectedDesign().paramsUrl, function (data) {
            var params = data["params"]
            var container = $("#param-container");
            container.empty();
            for (key in params) {
                if (!params.hasOwnProperty(key)) {
                    continue;
                }
                container.append(
                    $("<div/>").addClass("clearfix")
                        .append($("<label/>").text(params[key]))
                        .append(
                        $("<div/>").addClass("input")
                            .append($("<input/>").attr("name", key).attr("type", "text"))
                    )
                )
            }
            // Good. We can submit now.
            $("#submitBtn").removeAttr("disabled");
        }, "json");
    };
};
