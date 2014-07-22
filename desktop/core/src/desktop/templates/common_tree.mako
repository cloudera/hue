## -*- coding: utf-8 -*-
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


#
# Include this in order to use the functions:
# <%namespace name="tree" file="common_tree.mako" />
#

<%!
  from django.utils.translation import ugettext as _
%>

<%def name="import_templates(itemClick=None, itemDblClick=None, itemSelected=None, iconModifier=None, styleModifier=None, styleModifierPullRight=None, limitCount=None, limitFunction=None)">

  <script src="/static/js/ko.tree.js" type="text/javascript" charset="utf-8"></script>

  <script type="text/html" id="tree-template">
    <!-- ko if: nodes != null -->
    <ul class="tree" data-bind="foreach: nodes">
      <li>
        <span data-bind="template: { name: 'node-name-template', data: $data }"></span>
        <div data-bind="template: { name: 'folder-template', data: $data }, visible: isExpanded"></div>
      </li>
    </ul>
    <!-- /ko -->
  </script>

  <script type="text/html" id="folder-template">
    <!-- ko if: nodes != null -->
    <ul data-bind="foreach: nodes">
      <li>
        <div data-bind="template: { name: 'node-template', data: $data }"></div>
      </li>
      <!-- ko if: $index() == 14 -->
      <li>
        <a href="javascript: void(0)">
          <i class="fa fa-plus"></i>
        </a>
      </li>
      <!-- /ko -->
    </ul>
    <!-- /ko -->
  </script>

  <script type="text/html" id="node-template">
    <!-- ko if: nodes != null -->
    <span data-bind="
          template: { name: 'node-name-template', data: $data },
          css: { 'pointer-icon': nodes().length > 0 }"></span>
    <!-- /ko -->

    <!-- ko if: nodes().length !== 0 -->
    <div data-bind="template: { name: 'folder-template', data: $data }, visible: isExpanded"></div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="node-name-template">
    <div class="node-row" data-bind="
    %if itemClick:
      click: ${itemClick},
    %endif
    %if itemDblClick:
      event : { dblclick: ${itemDblClick} },
    %endif
    %if styleModifier:
      style: { border: ${styleModifier}() ? '1px dashed #bce8f1': '',  background: ${styleModifier}() ? '#d9edf7': ''},
    %endif
    %if itemSelected:
     css:{selected: ${itemSelected}}">
    %else:
     css:{unselected: true">
    %endif
      <i data-bind="
        css: {
            'fa': true,
            %if iconModifier:
            ${iconModifier()}
            %else:
            'fa-file-o': true
            %endif
        },
        %if styleModifier:
          style: { color: ${styleModifier}() ? '#338bb8': '#999999'}
        %else:
          style: { color: '#999999'}
        %endif
        "></i>
      <strong><a style="display: inline-block" data-bind="text:name"></a></strong>

      %if styleModifierPullRight:
      ${styleModifierPullRight()}
      %endif
    </div>
  </script>

</%def>

<%def name="render(id=None, data=None)">
  <div id="${id}" data-bind="template: { name: 'tree-template', data: ${data} }"></div>
</%def>

