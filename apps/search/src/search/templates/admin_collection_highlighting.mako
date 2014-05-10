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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user, "29px") | n,unicode }

<%layout:skeleton>
  <%def name="title()">
    <h4>${ _('Highlighting for') } <strong>${ hue_collection.name }</strong></h4>
  </%def>

  <%def name="navigation()">
    ${ layout.sidebar(hue_collection, 'highlighting') }
  </%def>

  <%def name="content()">
    <form method="POST" class="form" data-bind="submit: submit">
      <div class="well">
      <div class="section">
        <div class="alert alert-info">
          <div class="pull-right" style="margin-top: 10px">
            <label>
              <input type='checkbox' data-bind="checked: isEnabled" style="margin-top: -2px; margin-right: 4px"/> ${_('Enabled') }
            </label>
          </div>
          <h3>${_('Highlighting')}</h3>
          ${_('Highlights the query keywords matching some of the fields below.')}
          <strong>
            <span data-bind="visible: ! isEnabled()">
            ${_('Highlighting is currently disabled.')}
            </span>
          </strong>
        </div>
        <div class="selector">
          <select data-bind="options: fields, selectedOptions: highlightedFields" size="20" multiple="true" class="hide"></select>
          <select id="fields" size="20" multiple="true"></select>
        </div>
      </div>

      <div class="form-actions" style="margin-top: 80px">
        <button type="submit" class="btn btn-primary" id="save-btn">${_('Save')}</button>
      </div>
      </div>
    </form>
  </%def>
</%layout:skeleton>

<style type="text/css">
  #fields {
    list-style-type: none;
    margin: 0;
    padding: 0;
    width: 100%;
  }

  #fields li {
    margin-bottom: 10px;
    padding: 10px;
    border: 1px solid #E3E3E3;
    height: 30px;
  }

  .placeholder {
    height: 30px;
    background-color: #F5F5F5;
    border: 1px solid #E3E3E3;
  }
</style>


<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js"></script>
## Duplication with desktop/core required because of packaging for now
<script src="/search/static/js/jquery.selector.js"></script>

<script type="text/javascript">
  function ViewModel() {
    var self = this;
    self.fields = ko.observableArray(${ hue_collection.fields(user) | n,unicode });

    var highlighting = ${ hue_collection.result.get_highlighting() | n,unicode };
    var properties = ${ hue_collection.result.get_properties() | n,unicode };

    self.highlightedFields = ko.observableArray(highlighting != null ? highlighting : []);
    self.isEnabled = ko.observable(properties.highlighting_enabled);

    self.submit = function () {
      $.ajax("${ url('search:admin_collection_highlighting', collection_id=hue_collection.id) }", {
        data: {
          'properties': ko.utils.stringifyJson({'highlighting_enabled': self.isEnabled()}),
          'highlighting': ko.utils.stringifyJson(self.highlightedFields)
        },
        contentType: 'application/json',
        type: 'POST',
        success: function () {
          $(document).trigger("info", "${_('Updated')}");
        },
        error: function (data) {
          $(document).trigger("error", "${_('Error: ')}" + data);
        },
        complete: function() {
          $("#save-btn").button('reset');
        }
      });
    };
  };

  var viewModel = new ViewModel();

  $(document).ready(function () {
    ko.applyBindings(viewModel);

    ko.utils.arrayForEach(viewModel.fields(), function(field) {
      $("<option>").attr("value", field).text(field).appendTo($("#fields"));
    });

    $("#fields").val(viewModel.highlightedFields());

    $("#fields").jHueSelector({
      selectAllLabel: "${_('Select all')}",
      searchPlaceholder: "${_('Search')}",
      noChoicesFound: "${_('No fields found.')}",
      width:$(".selector").width(),
      height:340,
      onChange: function(){
        viewModel.highlightedFields($("#fields").val());
        viewModel.isEnabled(viewModel.highlightedFields() != null);
      }
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
