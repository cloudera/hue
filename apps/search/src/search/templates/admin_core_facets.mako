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

<%namespace name="macros" file="macros.mako" />
<%namespace name="navigation" file="navigation_bar_admin.mako" />

${ commonheader(_('Search'), "search", user) | n,unicode }


<div class="container-fluid">
  ${ navigation.menubar('cores') }
  ${ navigation.sub_menubar(hue_core.name, 'facets') }

  Solr
  <p>
  ${ solr_core }
  </p>

  Hue
  <p>
  ${ hue_core }
  </p>

  <!--
  <div class="btn-group" style="display: inline">
    <a href="#" data-toggle="dropdown" class="btn dropdown-toggle">
      <i class="icon-plus-sign"></i> New
      <span class="caret"></span>
    </a>
    <ul class="dropdown-menu" style="top: auto">
      <li><a href="#" class="create-file-link" title="${ _('Field facet') }"><i class="icon-bookmark"></i> ${ _('Field') }</a></li>
      <li><a href="#" class="create-directory-link" title="${ _('Range') }"><i class="icon-resize-full"></i> ${ _('Range') }</a></li>
      <li><a href="#" class="create-directory-link" title="Directory"><i class="icon-calendar"></i> ${ _('Date') }</a></li>
    </ul>
  </div>
  -->

  <form method="POST" id="facets" data-bind="submit: submit">
    <ul data-bind="foreach: field_facets">
      <li>
        <span data-bind="text: $data"></span>
        <button data-bind="click: $parent.removeFieldFacets">${ _('Remove') }</button>
      </li>
    </ul>

    <button type="submit">${ _('Save') }</button>
  </form>


  <select data-bind="options: fields, selectedOptions: field_facets" size="5" multiple="true"></select>

  ${ hue_core.fields }

</div>

<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  $(document).ready(function(){
     function ViewModel() {
       var self = this;
       self.fields = ko.observableArray(${ hue_core.fields | n,unicode });
       self.field_facets = ko.observableArray(${ hue_core.facets.data | n,unicode }.fields);

       self.removeFieldFacets = function(facet) {
         self.field_facets.remove(facet);
       };

      self.submit = function() {
	    $.ajax("${ url('search:admin_core_facets', core=hue_core.name) }", {
		    data : {'fields': ko.utils.stringifyJson(self.field_facets)},
		    contentType : 'application/json',
		    type : 'POST'
	    }); // notif + refresh?
      };
    };

    ko.applyBindings(new ViewModel());
  });
</script>

${ commonfooter(messages) | n,unicode }
