## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
  from django.utils.translation import ugettext as _
%>

<%namespace name="properties" file="coordinator_properties.mako" />
<%namespace name="utils" file="../utils.inc.mako" />


<div class="alert alert-info">
  <h3>${ _('Edit bundled coordinator') }</h3>
</div>
<div>
  ${ utils.render_field_no_popover(bundled_coordinator_form['coordinator']) }
  ${ bundled_coordinator_form['parameters'] | n,unicode }
  ${ properties.print_key_value(bundled_coordinator_form['parameters'], 'edit_bundled_coordinator_parameters') }

  <div class="form-actions" style="padding-left:10px">
    <a id="editBundledCoordinatorFormBtn" class="btn btn-primary">${ _('Save') }</a>
  </div>
</div>


<script type="text/javascript">
$(document).ready(function () {

  var ViewModel = function() {
    var self = this;

    self.edit_bundled_coordinator_parameters = ko.observableArray(${ bundled_coordinator_instance.parameters | n,unicode });
    self.add_edit_bundled_coordinator_parameters = function() {
      self.edit_bundled_coordinator_parameters.push({name: "", value: ""});
    };
    self.remove_edit_bundled_coordinator_parameters = function(val) {
      self.edit_bundled_coordinator_parameters.remove(val);
    };
  };

  window.viewModel = new ViewModel();
  ko.applyBindings(window.viewModel, document.getElementById('editBundledCoordinator'));

  $('#editBundledCoordinatorFormBtn').click(function () {
     $("#id_edit-bundled-coordinator-parameters").val(ko.utils.stringifyJson(window.viewModel.edit_bundled_coordinator_parameters));

     $.post("${ url('oozie:edit_bundled_coordinator', bundle=bundle.id, bundled_coordinator=bundled_coordinator_form.instance.id) }",
       $("#jobForm").serialize(), function(response) {
         if (response['status'] != 0) {
           $('#editBundledCoordinator').html(response['data']);
         } else {
           window.location.replace(response['data']);
           window.location.reload();
         }
     });
  });
});
</script>
