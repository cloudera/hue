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

<%def name="import_templates(itemClick=None, iconClick=None, itemDblClick=None, itemSelected=None, iconModifier=None, styleModifier=None, styleModifierPullRight=None, showMore=None, anchorProperty=None, strikedProperty=None, itemChecked=None, component='')">

  <script src="${ static('desktop/js/ko.tree.js') }" type="text/javascript" charset="utf-8"></script>

  <script type="text/html" id="tree-template${ component }">
    <!-- ko if: nodes != null -->
    <ul class="tree" data-bind="foreach: nodes">
      <li>
        <span data-bind="template: { name: 'node-name-template${ component }', data: $data }"></span>
        <div data-bind="template: { name: 'folder-template${ component }', data: $data }, visible: isExpanded"></div>
      </li>
    </ul>
    <!-- /ko -->
  </script>

  <script type="text/html" id="folder-template${ component }">
    <ul>
      <!-- ko foreach: nodes -->
      <li>
        <div data-bind="template: { name: 'node-template${ component }', data: $data }"></div>
      </li>
      <!-- /ko -->
      %if showMore:
      <!-- ko if: page().number != page().num_pages() -->
      <li>
        <a href="javascript: void(0)" data-bind="click: ${showMore}" style="padding-left: 8px">
          <i class="fa fa-plus"></i> ${_('Show more...')}
        </a>
      </li>
      <!-- /ko -->
      %endif
    </ul>
  </script>

  <script type="text/html" id="node-template${ component }">
    <!-- ko if: nodes != null -->
    <span data-bind="
          template: { name: 'node-name-template${ component }', data: $data },
          css: { 'pointer-icon': nodes().length > 0 }"></span>
    <!-- /ko -->

    <!-- ko if: nodes().length !== 0 -->
    <div data-bind="template: { name: 'folder-template${ component }', data: $data }, visible: isExpanded"></div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="node-name-template${ component }">
    <div class="node-row" data-bind="
    %if itemSelected:
     css: { selected: ${itemSelected}}
    %endif
    ">
      <table style="width: 100%">
        <tr>
          %if itemChecked:
          <td style="width: 16px">
            <i data-bind="css: {'fa': true, 'fa-fw': true, 'fa-square-o': ! ${itemChecked}(), 'fa-check-square-o': ${itemChecked}()}, click: $root.assist.checkPath, style: { color: '#999999'}"></i>
          </td>
          %endif
          <td style="width: 16px">
            <i data-bind="
              %if iconClick:
                click: ${iconClick},
              %endif
              css: {
                  'fa fa-fw': true,
                  %if iconModifier:
                  ${iconModifier()}
                  %else:
                  'fa-file-o': true
                  %endif
              },
              %if styleModifier:
                style: { color: ${styleModifier}() ? '#0B7FAD': '#999999'}
              %else:
                style: { color: '#999999'}
              %endif
              "></i>
          </td>
          <td class="pointer" data-bind="
          %if itemClick:
              click: ${itemClick},
            %endif
            %if itemDblClick:
              event : { dblclick: ${itemDblClick} },
            %endif
          visible: true">
            %if anchorProperty:
              <a href="#" class="anchor" data-bind="attr: {href: ${anchorProperty}}"></a>
            %endif
            <strong><a style="display: inline-block" data-bind="text:name,
            %if strikedProperty:
            css:{'striked': striked},
            %endif
            visible: true"></a></strong>

            %if styleModifierPullRight:
            ${styleModifierPullRight()}
            %endif
          </td>
        </tr>
      </table>
    </div>
  </script>

</%def>

<%def name="render(id=None, data=None, afterRender='void(0)', component='')">
  <div id="${id}" class="hue-tree" data-bind="template: { name: 'tree-template${ component }', data: ${data}, afterRender: ${afterRender} }"></div>
</%def>

