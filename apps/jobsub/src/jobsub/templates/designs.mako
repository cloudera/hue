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
import cgi
import urllib
import time
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_('Job Designer'), "jobsub", user, "60px") | n,unicode }

<link rel="stylesheet" href="/jobsub/static/css/jobsub.css">

<script src="/static/ext/js/mustache.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/oozie/static/js/workflow.models.js" type="text/javascript" charset="utf-8"></script>
<script src="/oozie/static/js/workflow.node-fields.js" type="text/javascript" charset="utf-8"></script>
<script src="/jobsub/static/js/jobsub.templates.js" type="text/javascript" charset="utf-8"></script>
<script src="/jobsub/static/js/jobsub.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/jobsub/static/js/jobsub.js" type="text/javascript" charset="utf-8"></script>

<div class="container-fluid">
  <h1>${_('Job Designs')}</h1>

  <%actionbar:render>
    <%def name="actions()">
      <button id="home" class="btn" title="${_('Home')}"><i class="icon-share"></i> ${_('Home')}</button>
      &nbsp;
      <button id="submit-design" class="btn" title="${_('Submit')}" data-bind="enable: selectedDesignObjects().length == 1"><i class="icon-play"></i> ${_('Submit')}</button>
      <button id="edit-design" class="btn" title="${_('Edit')}" data-bind="enable: selectedDesignObjects().length == 1 && window.location.hash.substring(0,12) != '#edit-design'"><i class="icon-pencil"></i> ${_('Edit')}</button>
      <button id="delete-designs" class="btn" title="${_('Delete')}" data-bind="enable: selectedDesignObjects().length > 0"><i class="icon-trash"></i> ${_('Delete')}</button>
      <button id="copy-designs" class="btn" title="${_('Copy')}" data-bind="enable: selectedDesignObjects().length > 0"><i class="icon-retweet"></i> ${_('Copy')}</button>
    </%def>

    <%def name="creation()">
        <div id="new-action-dropdown" class="btn-group" style="display: inline">
          <a href="#" class="btn new-action-link dropdown-toggle" title="${_('New Action')}" data-toggle="dropdown">
            <i class="icon-plus-sign"></i> ${_('New Action')}
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu" style="top: auto">
            <li>
              <a href="#new-design/mapreduce" class="new-node-link" title="${_('Create MapReduce Design')}" rel="tooltip"><i class="icon-plus-sign"></i> MapReduce</a>
            </li>
            <li>
              <a href="#new-design/java" class="new-node-link" title="${_('Create Java Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Java</a>
            </li>
            <li>
              <a href="#new-design/streaming" class="new-node-link" title="${_('Create Streaming Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Streaming</a>
            </li>
            <li>
              <a href="#new-design/hive" class="new-node-link" title="${_('Create Hive Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Hive</a>
            </li>
            <li>
              <a href="#new-design/pig" class="new-node-link" title="${_('Create Pig Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Pig</a>
            </li>
            <li>
              <a href="#new-design/sqoop" class="new-node-link" title="${_('Create Sqoop Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Sqoop</a>
            </li>
            <li>
              <a href="#new-design/fs" class="new-node-link" title="${_('Create Fs Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Fs</a>
            </li>
            <li>
              <a href="#new-design/ssh" class="new-node-link" title="${_('Create Ssh Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Ssh</a>
            </li>
            <li>
              <a href="#new-design/shell" class="new-node-link" title="${_('Create Shell Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Shell</a>
            </li>
            <li>
              <a href="#new-design/email" class="new-node-link" title="${_('Create Email Design')}" rel="tooltip"><i class="icon-plus-sign"></i> Email</a>
            </li>
            <li>
              <a href="#new-design/distcp" class="new-node-link" title="${_('Create DistCp Design')}" rel="tooltip"><i class="icon-plus-sign"></i> DistCp</a>
            </li>
          </ul>
        </div>
    </%def>
  </%actionbar:render>

  <div id="design" class="section" data-bind="template: {name: temporary().template(), data: temporary().design(), if: temporary().design()}"></div>

  <div id="list-designs" class="section">
    <table id="designTable" class="table table-condensed datatables">
      <thead>
        <tr>
          <th width="1%">
            <div id="selectAll" data-bind="click: toggleSelectAll, css: {hueCheckbox: true, 'icon-ok': selectedDesignObjects().length == designs().length}"></div>
          </th>
          <th>${_('Name')}</th>
          <th>${_('Description')}</th>
          <th>${_('Owner')}</th>
          <th>${_('Type')}</th>
          <th>${_('Status')}</th>
          <th>${_('Last modified')}</th>
        </tr>
      </thead>
      <tbody id="designs" data-bind="template: {name: 'designTemplate', foreach: designs}">

      </tbody>
    </table>
  </div>

</div>

<script id="designTemplate" type="text/html">
  <tr style="cursor: pointer" data-bind="with: design">
    <td data-row-selector-exclude="true" data-bind="click: function(data, event) {$root.toggleSelect.call($root, $index());}" class="center" style="cursor: default">
      <div class="hueCheckbox savedCheck" data-row-selector-exclude="true" data-bind="css: {hueCheckbox: name != '..', 'icon-ok': $parent.selected()}"></div>
    </td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + $index() }, text: name"></td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + $index() }, text: description"></td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + $index() }, text: owner"></td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + $index() }, text: node_type"></td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + $index() }">
      <!-- ko if: is_shared -->
        <span class="label label-info">shared</span>
      <!-- /ko -->
      <!-- ko ifnot: is_shared -->
        <span class="label label-info">personal</span>
      <!-- /ko -->
    </td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + $index() }, text: new Date(last_modified() * 1000).format('%B %d, %Y %I:%M %p'), attr: { 'data-sort-value': last_modified() }"></td>
  </tr>
</script>

<div id="submitWf" class="modal hide fade"></div>

<div id="deleteWf" class="modal hide fade">
  <form id="deleteWfForm" action="#" method="POST" style="margin:0">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteWfMessage">${_('Delete the selected designs?')}</h3>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
      <input type="submit" class="btn btn-danger" value="${_('Yes')}" data-dismiss="modal" data-bind="click: deleteDesigns" />
    </div>
  </form>
</div>

<div id="chooseFile" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Choose a file')}</h3>
  </div>
  <div class="modal-body">
    <div id="fileChooserModal">
    </div>
  </div>
  <div class="modal-footer">
  </div>
</div>

<script type="text/javascript" charset="utf-8">
var AUTOCOMPLETE_PROPERTIES;

$(document).bind('initialize.designs', function() {
  var designTable, viewModel;

  $("#filterInput").keyup(function() {
      if (designTable != null){
          designTable.fnFilter($(this).val());
      }
  });

  designTable = $('#designTable').dataTable( {
    "sPaginationType": "bootstrap",
    "bLengthChange": false,
    "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
    "bDestroy": true,
    "aoColumns": [
      { "bSortable": false },
      null,
      null,
      null,
      null,
      { "sSortDataType": "dom-sort-value", "sType": "numeric" }
    ],
    "aaSorting": [[ 5, "desc" ]],
    "fnPreDrawCallback": function( oSettings ) {
      if (designs.allSelected()) {
        designs.selectAll();
      }
    },
    "oLanguage": {
      "sEmptyTable":     "${_('No data available')}",
      "sInfo":           "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
      "sInfoEmpty":      "${_('Showing 0 to 0 of 0 entries')}",
      "sInfoFiltered":   "${_('(filtered from _MAX_ total entries)')}",
      "sZeroRecords":    "${_('No matching records')}",
      "oPaginate": {
        "sFirst":    "${_('First')}",
        "sLast":     "${_('Last')}",
        "sNext":     "${_('Next')}",
        "sPrevious": "${_('Previous')}"
      }
    }
  });

  $(document).one('load.designs', function() {
    designTable.fnDestroy();
  });
});
designs.load();

/**
 * Using Mustache templating system: http://mustache.github.com/
 * Templates and partials are loaded in jobsub.templates.js
 * Context is matched up with templates and partials.
 * Global context is extended to provide any uniqueness.
 * Routie is used to provide hash routing: http://projects.jga.me/routie/.
 */
$(document).ready(function() {
  //// Binding
  ko.applyBindings(designs);

  //// Routes
  // Context matches up with jobsub.templates.js and various templates defined there.
  // If there is an update to any of the templates,
  // This global context may need to be updated.
  var global_action_context = {
    alert: "${_('You can parameterize the values, using')} <code>$myVar</code> ${_('or')} <code>${"${"}myVar}</code>. ${_('When the design is submitted, you will be prompted for the actual value of ')}<code>myVar</code>.",
    paths_alert: "${_('All the paths are relative to the deployment directory. They can be absolute but this is not recommended.')}",
    smtp_alert: "${_('Requires some SMTP server configuration to be present (in oozie-site.xml).')}",
    ssh_alert: "${_('The ssh server requires passwordless login.')}",
    save: {
      name: "${_('Save')}",
      func: "function(data, event) {$root.saveDesign.call($root, data, event);}"
    },
    cancel: {
      name: "${_('Cancel')}",
      func: "function(data, event) {$root.closeDesign.call($parent, {}); designs.load();}"
    },
    name: {
      name: "${ _('Name') }",
      popover: "${ _('Name of the design.') }",
      js: {
        name: 'name'
      }
    },
    description: {
      name: "${ _('Description') }",
      popover: "${ _('Description of the design.') }",
      js: {
        name: 'description'
      }
    },
    is_shared: {
      name: "${ _('Is shared') }",
      popover: "${ _('Enable other users to have access to this job.') }",
      js: {
        name: 'is_shared'
      }
    },
    parameters: {
      title: "${ _('Oozie parameters') }",
      name: "${ _('Name') }",
      value: "${ _('Value') }",
      delete: {
        name: "${ _('Delete') }",
        func: 'function(data, event) { $parent.removeParameter.call($parent, data, event) }'
      },
      add: {
        name: "${ _('Add') }",
        func: 'addParameter'
      },
      ko: {
        items: "parameters",
        error_class: "parameters_error_class",
        condition: "parameters_condition"
      }
    },
    user: {
      name: "${ _('User') }",
      popover: "${ _('User to authenticate with.') }"
    },
    host: {
      name: "${ _('Host') }",
      popover: "${ _('Host to execute command on.') }"
    },
    command: {
      name: "${ _('Command') }",
      popover: "${ _('Command to execute.') }"
    },
    script_path: {
      name: "${ _('Script name') }",
      popover: "${ _('Path to the script to execute.') }"
    },
    jar_path: {
      name: "${ _('Jar path') }",
      popover: "${ _('Path to jar files on HDFS.') }"
    },
    main_class: {
      name: "${ _('Main class') }",
      popover: "${ _('Main class') }"
    },
    args: {
      name: "${ _('Args') }",
      popover: "${ _('Args') }"
    },
    java_opts: {
      name: "${ _('Java opts') }",
      popover: "${ _('Java opts') }"
    },
    mapper: {
      name: "${ _('Mapper') }",
      popover: "${ _('Mapper') }"
    },
    reducer: {
      name: "${ _('Reducer') }",
      popover: "${ _('Reducer') }"
    },
    to: {
      name: "${ _('TO addresses') }",
      popover: "${ _('TO addresses') }"
    },
    cc: {
      name: "${ _('CC addresses (optional)') }",
      popover: "${ _('CC addresses (optional)') }"
    },
    subject: {
      name: "${ _('Subject') }",
      popover: "${ _('Subject') }"
    },
    body: {
      name: "${ _('Body') }",
      popover: "${ _('Body') }"
    },
    job_properties: {
      title: "${ _('Job Properties') }",
      name: "${ _('Property name') }",
      value: "${ _('Value') }",
      delete: {
        name: "${ _('Delete') }",
        func: 'function(data, event) { $parent.removeProperty.call($parent, data, event) }'
      },
      add: {
        name: "${ _('Add Property') }",
        func: 'addProperty'
      },
      ko: {
        items: "job_properties",
        error_class: "job_properties_error_class",
        condition: "job_properties_condition"
      }
    },
    prepares: {
      title: "${ _('Prepare') }",
      name: "${ _('Type') }",
      value: "${ _('Value') }",
      delete: {
        name: "${ _('Delete') }",
        func: 'function(data, event) { $parent.removePrepare.call($parent, data, event) }'
      },
      add: {
        delete: {
          name: "${ _('Add delete') }",
          func: 'addPrepareDelete'
        },
        mkdir: {
          name: "${ _('Add mkdir') }",
          func: 'addPrepareMkdir'
        }
      },
      ko: {
        items: "prepares",
        error_class: "prepares_error_class",
        condition: "prepares_condition"
      }
    },
    params: {
      title: "${ _('Params') }",
      name: "${ _('Type') }",
      value: "${ _('Value') }",
      delete: {
        name: "${ _('Delete') }",
        func: 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
      },
      add: [{
        name: "${ _('Add param') }",
        func: 'addParam'
      }],
      ko: {
        items: "params",
        error_class: "params_error_class",
        condition: "params_condition"
      }
    },
    files: {
      title: "${ _('Files') }",
      delete: {
        name: "${ _('Delete') }",
        func: 'function(data, event) { $parent.removeFile.call($parent, data, event) }'
      },
      add: {
        name: "${ _('Add File') }",
        func: 'addFile'
      },
      ko: {
        items: "files",
        error_class: "files_error_class",
        condition: "files_condition"
      }
    },
    archives: {
      title: "${ _('Archives') }",
      delete: {
        name: "${ _('Delete') }",
        func: 'function(data, event) { $parent.removeArchive.call($parent, data, event) }'
      },
      add: {
        name: "${ _('Add Archive') }",
        func: 'addArchive'
      },
      ko: {
        items: "archives",
        error_class: "archives_error_class",
        condition: "archives_condition"
      }
    }
  };

  var contexts = {
    mapreduce: {
      title: "${ _('Job Design (mapreduce type)') }"
    },
    java: {
      title: "${ _('Job Design (java type)') }"
    },
    streaming: {
      title: "${ _('Job Design (streaming type)') }"
    },
    hive: {
      title: "${ _('Job Design (hive type)') }"
    },
    pig: {
      title: "${ _('Job Design (pig type)') }",
      params: {
        title: "${ _('Params') }",
        name: "${ _('Type') }",
        value: "${ _('Value') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
        },
        add: [{
          name: "${ _('Add param') }",
          func: 'addParam'
        },{
          name: "${ _('Add argument') }",
          func: 'addArgument'
        }],
        ko: {
          items: "params",
          error_class: "params_error_class",
          condition: "params_condition"
        }
      },
    },
    sqoop: {
      title: "${ _('Job Design (sqoop type)') }",
      script_path: {
        name: "${ _('Command') }",
        popover: "${ _('Command to execute.') }"
      },
      params: {
        title: "${ _('Params') }",
        name: "${ _('Type') }",
        value: "${ _('Value') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
        },
        add: [{
          name: "${ _('Add arg') }",
          func: 'addArg'
        }],
        ko: {
          items: "params",
          error_class: "params_error_class",
          condition: "params_condition"
        }
      }
    },
    fs: {
      title: "${ _('Job Design (fs type)') }",
      deletes: {
        title: "${ _('Delete path') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeDelete.call($parent, data, event) }'
        },
        add: {
          name: "${ _('Add Path') }",
          func: 'addDelete'
        },
        ko: {
          items: "deletes",
          error_class: "deletes_error_class",
          condition: "deletes_condition"
        }
      },
      mkdirs: {
        title: "${ _('Create directory') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeMkdir.call($parent, data, event) }'
        },
        add: {
          name: "${ _('Add Path') }",
          func: 'addMkdir'
        },
        ko: {
          items: "mkdirs",
          error_class: "mkdirs_error_class",
          condition: "mkdirs_condition"
        }
      },
      touchzs: {
        title: "${ _('Create or touch file') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeTouchz.call($parent, data, event) }'
        },
        add: {
          name: "${ _('Add Path') }",
          func: 'addTouchz'
        },
        ko: {
          items: "touchzs",
          error_class: "touchzs_error_class",
          condition: "touchzs_condition"
        }
      },
      chmods: {
        title: "${ _('Change permissions') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeChmod.call($parent, data, event) }'
        },
        add: {
          name: "${ _('Add chmod') }",
          func: 'addChmod'
        },
        ko: {
          items: "chmods",
          error_class: "chmods_error_class",
          condition: "chmods_condition"
        }
      },
      moves: {
        title: "${ _('Move file') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeMove.call($parent, data, event) }'
        },
        add: {
          name: "${ _('Add move') }",
          func: 'addMove'
        },
        ko: {
          items: "moves",
          error_class: "moves_error_class",
          condition: "moves_condition"
        }
      }
    },
    ssh: {
      title: "${ _('Job Design (ssh type)') }",
      params: {
        title: "${ _('Params') }",
        name: "${ _('Type') }",
        value: "${ _('Value') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
        },
        add: [{
          name: "${ _('Add arg') }",
          func: 'addArg'
        }],
        ko: {
          items: "params",
          error_class: "params_error_class",
          condition: "params_condition"
        }
      },
    },
    shell: {
      title: "${ _('Job Design (shell type)') }",
      params: {
        title: "${ _('Params') }",
        name: "${ _('Type') }",
        value: "${ _('Value') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
        },
        add: [{
          name: "${ _('Add argument') }",
          func: 'addArgument'
        },{
          name: "${ _('Add Env-Var') }",
          func: 'addEnvVar'
        }],
        ko: {
          items: "params",
          error_class: "params_error_class",
          condition: "params_condition"
        }
      },
    },
    email: {
      title: "${ _('Job Design (email type)') }"
    },
    distcp: {
      title: "${ _('Job Design (distcp type)') }",
      params: {
        title: "${ _('Params') }",
        name: "${ _('Type') }",
        value: "${ _('Value') }",
        delete: {
          name: "${ _('Delete') }",
          func: 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
        },
        add: [{
          name: "${ _('Add Argument') }",
          func: 'addArgument'
        }],
        ko: {
          items: "params",
          error_class: "params_error_class",
          condition: "params_condition"
        }
      },
    }
  }

  routie({
    'new-design/:node_type': function(node_type) {
      /**
       * Update context with correct title.
       * Create empty design to fill.
       * Create template by calling `getActionTemplate`.
       */
      // Show section only after we've finished the new design process.
      $(document).one('new.design', function() {
        showSection('design');
      });

      designs.closeDesign();

      var context = $.extend(true, {}, global_action_context, contexts[node_type]);
      templates.getActionTemplate(node_type, context);
      designs.newDesign(node_type);
    },
    'edit-design/:index': function(index) {
      /**
       * Update context with correct title.
       * Design is selected through 'list-designs'.
       */
      designs.closeDesign();

      var designObject = designs.designs()[index];
      if (!designObject) {
        routie('list-designs');
        return;
      }

      // Show section only after we've finished the edit design process.
      $(document).one('edit.design', function() {
        if (designObject.design().editable()) {
          $('#design input').removeAttr('disabled');
          $('#design textarea').removeAttr('disabled');
          $('#design button').removeAttr('disabled');
        } else {
          $('#design input').attr('disabled', 'disabled');
          $('#design textarea').attr('disabled', 'disabled');
          $('#design button').attr('disabled', 'disabled');
        }
        showSection('design');
      });

      var node_type = designObject.design().node_type();
      var context = $.extend(true, {}, global_action_context, contexts[node_type]);
      templates.getActionTemplate(node_type, context);
      designs.deselectAll();
      designs.select(index);
      designs.editDesign();
    },
    'list-designs': function() {
      showSection('list-designs');
    }
  });
  routie('list-designs');

  //// Row selector, buttons, and various features.
  $(".btn[rel='tooltip']").tooltip({placement:'bottom'});
  $("a[data-row-selector='true']").jHueRowSelector();
  $('#submit-design').click(function() {
    var url = '/oozie/submit_workflow/' + designs.selectedDesign().id();
    $.get(url, function (response) {
        $('#submitWf').html(response);
        $('#submitWf').modal('show');
      }
    );
  });
  $('#edit-design').click(function() {
    routie('edit-design/' + designs.selectedIndex());
  });
  $('#delete-designs').click(function() {
    $('#deleteWf').modal('show');
  });
  $('#copy-designs').click(function() {
    designs.cloneDesigns();
  });
  $('#home').click(function() {
    routie('list-designs');
  });
  // load the autocomplete properties
  $.getJSON("${ url('oozie:autocomplete_properties') }", function (properties) {
    AUTOCOMPLETE_PROPERTIES = properties;
  });
});
</script>

${ commonfooter(messages) | n,unicode }
