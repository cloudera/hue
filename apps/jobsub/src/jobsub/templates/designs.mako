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

${ commonheader(None, "jobsub", user, request) | n,unicode }

<link rel="stylesheet" href="${ static('jobsub/css/jobsub.css') }">

<script src="${ static('desktop/ext/js/mustache.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/js/hue.routie.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('oozie/js/workflow.models.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('oozie/js/workflow.node-fields.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('jobsub/js/jobsub.templates.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('jobsub/js/jobsub.ko.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('jobsub/js/jobsub.js') }" type="text/javascript" charset="utf-8"></script>


<div class="navbar hue-title-bar nokids">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="app-header">
              <a href="/${app_name}">
                <img src="${ static('jobsub/art/icon_jobsub_48.png') }" class="app-icon" alt="${ _('Job Designer icon') }" />
                ${ _('Job Designer') }
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
</div>


<div class="container-fluid">
  <div class="card card-small">
    <div class="alert">
      ${ _('This is the old Job Editor, it is recommended to instead use the new ') }
        <a href="${ url('notebook:editor') }" target="_blank">${_('Editor')}</a>
    </div>

  <h1 class="card-heading simple">${_('Designs')}</h1>

  <%actionbar:render>
    <%def name="search()">
      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for design name')}">
    </%def>

    <%def name="actions()">
      <div class="btn-toolbar" style="display: inline; vertical-align: middle">
      <!-- ko ifnot: inTrash -->
        <button id="submit-design" class="btn" title="${_('Submit')}" data-bind="enable: selectedDesignObjects().length == 1"><i class="fa fa-play"></i> ${_('Submit')}</button>
        <button id="edit-design" class="btn" title="${_('Edit')}" data-bind="enable: selectedDesignObjects().length == 1"><i class="fa fa-pencil"></i> ${_('Edit')}</button>
        <button id="copy-designs" class="btn" title="${_('Copy')}" data-bind="enable: selectedDesignObjects().length > 0"><i class="fa fa-files-o"></i> ${_('Copy')}</button>
        <div id="delete-dropdown" class="btn-group" style="vertical-align: middle">
          <button id="trash-designs" class="btn" data-bind="enable: selectedDesignObjects().length > 0"><i class="fa fa-times"></i> ${_('Move to trash')}</button>
          <button class="btn dropdown-toggle" data-toggle="dropdown" data-bind="enable: selectedDesignObjects().length > 0">
            <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            <li><a href="javascript:void(0);" id="destroy-designs" title="${_('Delete forever')}"><i class="fa fa-bolt"></i> ${_('Delete forever')}</a></li>
          </ul>
        </div>
      <!-- /ko -->
      <!-- ko if: inTrash -->
        <button id="restore-designs" disabled="disabled" class="btn" title="${_('Restore')}" data-bind="enable: selectedDesignObjects().length > 0"><i class="fa fa-cloud-upload"></i> ${_('Restore')}</button>
        <button id="destroy-designs" disabled="disabled" class="btn" title="${_('Delete forever')}" data-bind="enable: selectedDesignObjects().length > 0"><i class="fa fa-bolt"></i> ${_('Delete forever')}</button>
      <!-- /ko -->
      </div>
    </%def>

    <%def name="creation()">
      <div class="btn-toolbar" style="display: inline; vertical-align: middle">
      <!-- ko if: inTrash -->
        <button disabled="disabled" type="button" id="purge-trashed-designs" class="btn" title="${ _('Delete all the designs') }"><i class="fa fa-fire"></i> ${ _('Empty trash') }</button>
        &nbsp;&nbsp;
      <!-- /ko -->
      <button id="home" class="btn" title="${_('Home')}" data-bind="visible: isEditing"><i class="fa fa-home"></i> ${_('View designs')}</button>
      <!-- ko ifnot: inTrash -->
        <div id="new-action-dropdown" class="btn-group" style="vertical-align: middle">
          <a href="#" class="btn new-action-link dropdown-toggle" title="${_('New action')}" data-toggle="dropdown">
            <i class="fa fa-plus-circle"></i> ${_('New action')}
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu" style="top: auto">
            <li>
              <a href="#new-design/mapreduce" class="new-node-link" title="${_('Create MapReduce design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> MapReduce</a>
            </li>
            <li>
              <a href="#new-design/java" class="new-node-link" title="${_('Create Java design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Java</a>
            </li>
            <li>
              <a href="#new-design/streaming" class="new-node-link" title="${_('Create Streaming design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Streaming</a>
            </li>
            <li>
              <a href="#new-design/hive" class="new-node-link" title="${_('Create Hive design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Hive</a>
            </li>
            % if 'pig' in apps:
            <li>
              <a href="#new-design/pig" class="new-node-link" title="${_('Create Pig design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Pig</a>
            </li>
            % endif
            <li>
              <a href="#new-design/sqoop" class="new-node-link" title="${_('Create Sqoop design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Sqoop</a>
            </li>
            <li>
              <a href="#new-design/fs" class="new-node-link" title="${_('Create Fs design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Fs</a>
            </li>
            <li>
              <a href="#new-design/ssh" class="new-node-link" title="${_('Create SSH design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Ssh</a>
            </li>
            <li>
              <a href="#new-design/shell" class="new-node-link" title="${_('Create Shell design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Shell</a>
            </li>
            <li>
              <a href="#new-design/email" class="new-node-link" title="${_('Create Email design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> Email</a>
            </li>
            <li>
              <a href="#new-design/distcp" class="new-node-link" title="${_('Create DistCp design')}" rel="tooltip"><i class="fa fa-plus-circle"></i> DistCp</a>
            </li>
          </ul>
        </div>
        &nbsp;&nbsp;
        <a href="#trashed-designs" class="btn"><i class="fa fa-trash-o"></i> ${ _('View trash') }</a>
      <!-- /ko -->

      </div>
    </%def>
  </%actionbar:render>

  <div id="design" class="section" data-bind="template: {'name': temporary().template(), 'data': temporary().design(), 'if': temporary().design()}"></div>

  <div id="list-designs" class="section">
    <table id="designTable" class="table table-condensed datatables">
      <thead>
        <tr>
          <th width="1%">
            <div id="selectAll" data-bind="click: toggleSelectAll, css: { 'hue-checkbox': true, 'fa': true, 'fa-check': allSelected}"></div>
          </th>
          <th>${_('Name')}</th>
          <th>${_('Description')}</th>
          <th>${_('Owner')}</th>
          <th>${_('Type')}</th>
          <th>${_('Status')}</th>
          <th>${_('Last modified')}</th>
          <th>${_('Trashed')}</th>
        </tr>
      </thead>
      <tbody id="designs" data-bind="template: {'name': 'designTemplate', 'foreach': designs}">

      </tbody>
    </table>
  </div>

  </div>

</div>

<div class="hueOverlay" data-bind="visible: isLoading">
  <i class="fa fa-spinner fa-spin big-spinner"></i>
</div>

<script id="designTemplate" type="text/html">
  <tr style="cursor: pointer" data-bind="with: design">
    <td data-row-selector-exclude="true" data-bind="click: function(data, event) {$root.toggleSelect.call($root, $index());}" class="center" style="cursor: default">
      <div class="hue-checkbox savedCheck" data-row-selector-exclude="true" data-bind="css: {'hue-checkbox': name != '..', 'fa': name != '..', 'fa-check': $parent.selected()}"></div>
    </td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + id() }, text: name"></td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + id() }, text: description"></td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + id() }, text: owner"></td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + id() }, text: node_type"></td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + id() }">
      <!-- ko if: is_shared -->
        <span class="label label-info">shared</span>
      <!-- /ko -->
      <!-- ko ifnot: is_shared -->
        <span class="label label-info">personal</span>
      <!-- /ko -->
    </td>
    <td data-bind="click: function(data, event) { window.location = '#edit-design/' + id() }, text: new Date(last_modified() * 1000).format('%B %d, %Y %I:%M %p'), attr: { 'data-sort-value': last_modified() }"></td>
    <td data-bind="text: is_trashed"></td>
  </tr>
</script>

<div id="submitWf" class="modal hide fade"></div>

<div id="trashWf" class="modal hide fade">
  <form id="trashWfForm" action="#" method="POST" style="margin:0">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="trashWfMessage" class="modal-title">${_('Move the selected designs to trash?')}</h2>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
      <input type="submit" class="btn btn-danger" value="${_('Yes')}" data-dismiss="modal" data-bind="click: trashDesigns" />
    </div>
  </form>
</div>

<div id="destroyWf" class="modal hide fade">
  <form id="destroyWfForm" action="#" method="POST" style="margin:0">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="destroyWfMessage" class="modal-title">${_('Delete selected designs?')}</h2>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
      <input type="submit" class="btn btn-danger" value="${_('Yes')}" data-dismiss="modal" data-bind="click: destroyDesigns" />
    </div>
  </form>
</div>

<div id="purgeWf" class="modal hide fade">
  <form id="purgeWfForm" action="#" method="POST" style="margin:0">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="purgeWfMessage" class="modal-title">${_('Delete all trashed designs?')}</h2>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
      <input type="submit" class="btn btn-danger" value="${_('Yes')}" data-dismiss="modal" data-bind="click: destroyAllTrashedDesigns" />
    </div>
  </form>
</div>

<div id="restoreWf" class="modal hide fade">
  <form id="restoreWfForm" action="#" method="POST" style="margin:0">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="restoreWfMessage" class="modal-title">${_('Restore selected designs?')}</h2>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${_('No')}</a>
      <input type="submit" class="btn btn-danger" value="${_('Yes')}" data-dismiss="modal" data-bind="click: restoreDesigns" />
    </div>
  </form>
</div>

<div id="chooseFile" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Choose a file')}</h2>
  </div>
  <div class="modal-body">
    <div class="chooser">
    </div>
  </div>
  <div class="modal-footer">
  </div>
</div>

<div id="chooseDirectory" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Choose a directory')}</h2>
  </div>
  <div class="modal-body">
    <div class="chooser">
    </div>
  </div>
  <div class="modal-footer">
  </div>
</div>

<div id="choosePath" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Choose a path')}</h2>
  </div>
  <div class="modal-body">
    <div class="chooser">
    </div>
  </div>
  <div class="modal-footer">
  </div>
</div>

<script type="text/javascript">
//// Contexts
// Context matches up with jobsub.templates.js and various templates defined there.
// If there is an update to any of the templates,
// This global context may need to be updated.
// Global context is extended to provide any uniqueness.
var global_action_context = {
  'alert': "${_('You can parameterize the values, using')} <code>$myVar</code> ${_('or')} <code>${"${"}myVar}</code>. ${_('When the design is submitted, you will be prompted for the actual value of ')}<code>myVar</code>.",
  'paths_alert': "${_('All the paths are relative to the deployment directory. They can be absolute but this is not recommended.')}",
  'smtp_alert': "${_('Requires some SMTP server configuration to be present (in oozie-site.xml).')}",
  'ssh_alert': "${_('The ssh server requires passwordless login.')}",
  'save': {
    'name': "${_('Save')}",
    'func': "function(data, event) {$root.saveDesign.call($root, data, event);}"
  },
  'cancel': {
    'name': "${_('Cancel')}",
    'func': "function(data, event) {$root.closeDesign.call($parent, {}); reload();}"
  },
  'name': {
    'name': "${ _('Name') }",
    'popover': "${ _('Name of the design.') }",
    'js': {
      'name': 'name'
    }
  },
  'description': {
    'name': "${ _('Description') }",
    'popover': "${ _('Description of the design.') }",
    'js': {
      'name': 'description'
    }
  },
  'is_shared': {
    'name': "${ _('Is shared') }",
    'popover': "${ _('Enable other users to have access to this job.') }",
    'js': {
      'name': 'is_shared'
    }
  },
  'capture_output': {
    'name': "${ _('Capture output') }",
    'popover': "${ _('Capture the output of this job.') }",
    'js': {
      'name': 'capture_output'
    }
  },
  'parameters': {
    'title': "${ _('Oozie parameters') }",
    'name': "${ _('Name') }",
    'value': "${ _('Value') }",
    'delete': {
      'name': "${ _('Delete') }",
      'func': 'function(data, event) { $parent.removeParameter.call($parent, data, event) }'
    },
    'add': {
      'name': "${ _('Add') }",
      'func': 'addParameter'
    },
    'ko': {
      'items': "parameters",
      'error_class': "parameters_error_class",
      'condition': "parameters_condition"
    }
  },
  'user': {
    'name': "${ _('User') }",
    'popover': "${ _('User to authenticate with.') }"
  },
  'host': {
    'name': "${ _('Host') }",
    'popover': "${ _('Host to execute command on.') }"
  },
  'command': {
    'name': "${ _('Command') }",
    'popover': "${ _('Command to execute.') }"
  },
  'script_path': {
    'name': "${ _('Script name') }",
    'popover': "${ _('Path to the script to execute.') }"
  },
  'jar_path': {
    'name': "${ _('Jar path') }",
    'popover': "${ _('Path to jar files on HDFS.') }"
  },
  'main_class': {
    'name': "${ _('Main class') }",
    'popover': "${ _('Main class') }"
  },
  'args': {
    'name': "${ _('Args') }",
    'popover': "${ _('Args') }"
  },
  'java_opts': {
    'name': "${ _('Java opts') }",
    'popover': "${ _('Java opts') }"
  },
  'mapper': {
    'name': "${ _('Mapper') }",
    'popover': "${ _('Mapper') }"
  },
  'reducer': {
    'name': "${ _('Reducer') }",
    'popover': "${ _('Reducer') }"
  },
  'to': {
    'name': "${ _('TO addresses') }",
    'popover': "${ _('TO addresses') }"
  },
  'cc': {
    'name': "${ _('CC addresses (optional)') }",
    'popover': "${ _('CC addresses (optional)') }"
  },
  'subject': {
    'name': "${ _('Subject') }",
    'popover': "${ _('Subject') }"
  },
  'body': {
    'name': "${ _('Body') }",
    'popover': "${ _('Body') }"
  },
  'job_properties': {
    'title': "${ _('Hadoop job properties') }",
    'name': "${ _('Property name') }",
    'value': "${ _('Value') }",
    'delete': {
      'name': "${ _('Delete') }",
      'func': 'function(data, event) { $parent.removeProperty.call($parent, data, event) }'
    },
    'add': {
      'name': "${ _('Add property') }",
      'func': 'addProperty'
    },
    'ko': {
      'items': "job_properties",
      'error_class': "job_properties_error_class",
      'condition': "job_properties_condition"
    }
  },
  'prepares': {
    'title': "${ _('Prepare') }",
    'name': "${ _('Type') }",
    'value': "${ _('Value') }",
    'delete': {
      'name': "${ _('Delete') }",
      'func': 'function(data, event) { $parent.removePrepare.call($parent, data, event) }'
    },
    'add': {
      'delete': {
        'name': "${ _('Add delete') }",
        'func': 'addPrepareDelete'
      },
      'mkdir': {
        'name': "${ _('Add mkdir') }",
        'func': 'addPrepareMkdir'
      }
    },
    'ko': {
      'items': "prepares",
      'error_class': "prepares_error_class",
      'condition': "prepares_condition"
    }
  },
  'params': {
    'title': "${ _('Params') }",
    'name': "${ _('Type') }",
    'value': "${ _('Value') }",
    'delete': {
      'name': "${ _('Delete') }",
      'func': 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
    },
    'add': [{
      'name': "${ _('Add param') }",
      'func': 'addParam'
    }],
    'ko': {
      'items': "params",
      'error_class': "params_error_class",
      'condition': "params_condition"
    }
  },
  'files': {
    'title': "${ _('Files') }",
    'delete': {
      'name': "${ _('Delete') }",
      'func': 'function(data, event) { $parent.removeFile.call($parent, data, event) }'
    },
    'add': {
      'name': "${ _('Add file') }",
      'func': 'addFile'
    },
    'ko': {
      'items': "files",
      'error_class': "files_error_class",
      'condition': "files_condition"
    }
  },
  'archives': {
    'title': "${ _('Archives') }",
    'delete': {
      'name': "${ _('Delete') }",
      'func': 'function(data, event) { $parent.removeArchive.call($parent, data, event) }'
    },
    'add': {
      'name': "${ _('Add archive') }",
      'func': 'addArchive'
    },
    'ko': {
      'items': "archives",
      'error_class': "archives_error_class",
      'condition': "archives_condition"
    }
  }
};

var contexts = {
  'mapreduce': {
    'title': "${ _('Job Design (mapreduce type)') }"
  },
  'java': {
    'title': "${ _('Job Design (java type)') }"
  },
  'streaming': {
    'title': "${ _('Job Design (streaming type)') }"
  },
  'hive': {
    'title': "${ _('Job Design (hive type)') }"
  },
  'pig': {
    'title': "${ _('Job Design (pig type)') }",
    'params': {
      'title': "${ _('Params') }",
      'name': "${ _('Type') }",
      'value': "${ _('Value') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
      },
      'add': [{
        'name': "${ _('Add param') }",
        'func': 'addParam'
      },{
        'name': "${ _('Add argument') }",
        'func': 'addArgument'
      }],
      'ko': {
        'items': "params",
        'error_class': "params_error_class",
        'condition': "params_condition"
      }
    },
  },
  'sqoop': {
    'title': "${ _('Job Design (sqoop type)') }",
    'script_path': {
      'name': "${ _('Command') }",
      'popover': "${ _('Command to execute.') }"
    },
    'params': {
      'title': "${ _('Params') }",
      'name': "${ _('Type') }",
      'value': "${ _('Value') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
      },
      'add': [{
        'name': "${ _('Add arg') }",
        'func': 'addArg'
      }],
      'ko': {
        'items': "params",
        'error_class': "params_error_class",
        'condition': "params_condition"
      }
    }
  },
  'fs': {
    'title': "${ _('Job Design (fs type)') }",
    'deletes': {
      'title': "${ _('Delete path') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeDelete.call($parent, data, event) }'
      },
      'add': {
        'name': "${ _('Add path') }",
        'func': 'addDelete'
      },
      'ko': {
        'items': "deletes",
        'error_class': "deletes_error_class",
        'condition': "deletes_condition"
      }
    },
    'mkdirs': {
      'title': "${ _('Create directory') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeMkdir.call($parent, data, event) }'
      },
      'add': {
        'name': "${ _('Add path') }",
        'func': 'addMkdir'
      },
      'ko': {
        'items': "mkdirs",
        'error_class': "mkdirs_error_class",
        'condition': "mkdirs_condition"
      }
    },
    'touchzs': {
      'title': "${ _('Create or touch file') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeTouchz.call($parent, data, event) }'
      },
      'add': {
        'name': "${ _('Add path') }",
        'func': 'addTouchz'
      },
      'ko': {
        'items': "touchzs",
        'error_class': "touchzs_error_class",
        'condition': "touchzs_condition"
      }
    },
    'chmods': {
      'title': "${ _('Change permissions') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeChmod.call($parent, data, event) }'
      },
      'add': {
        'name': "${ _('Add chmod') }",
        'func': 'addChmod'
      },
      'ko': {
        'items': "chmods",
        'error_class': "chmods_error_class",
        'condition': "chmods_condition"
      }
    },
    'moves': {
      'title': "${ _('Move file') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeMove.call($parent, data, event) }'
      },
      'add': {
        'name': "${ _('Add move') }",
        'func': 'addMove'
      },
      'ko': {
        'items': "moves",
        'error_class': "moves_error_class",
        'condition': "moves_condition"
      }
    }
  },
  'ssh': {
    'title': "${ _('Job Design (ssh type)') }",
    'params': {
      'title': "${ _('Params') }",
      'name': "${ _('Type') }",
      'value': "${ _('Value') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
      },
      'add': [{
        'name': "${ _('Add arg') }",
        'func': 'addArg'
      }],
      'ko': {
        'items': "params",
        'error_class': "params_error_class",
        'condition': "params_condition"
      }
    },
  },
  'shell': {
    'title': "${ _('Job Design (shell type)') }",
    'params': {
      'title': "${ _('Params') }",
      'name': "${ _('Type') }",
      'value': "${ _('Value') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
      },
      'add': [{
        'name': "${ _('Add argument') }",
        'func': 'addArgument'
      },{
        'name': "${ _('Add env-var') }",
        'func': 'addEnvVar'
      }],
      'ko': {
        'items': "params",
        'error_class': "params_error_class",
        'condition': "params_condition"
      }
    },
  },
  'email': {
    'title': "${ _('Job Design (email type)') }"
  },
  'distcp': {
    'title': "${ _('Job Design (distcp type)') }",
    'params': {
      'title': "${ _('Params') }",
      'name': "${ _('Type') }",
      'value': "${ _('Value') }",
      'delete': {
        'name': "${ _('Delete') }",
        'func': 'function(data, event) { $parent.removeParam.call($parent, data, event) }'
      },
      'add': [{
        'name': "${ _('Add argument') }",
        'func': 'addArgument'
      }],
      'ko': {
        'items': "params",
        'error_class': "params_error_class",
        'condition': "params_condition"
      }
    },
  }
}

//// Binding
var designs = new Designs();
ko.applyBindings(designs);

// Design table and other variables.
var designTableOptions = {
  "bAutoWidth": false,
  "sPaginationType": "bootstrap",
  "bLengthChange": false,
  "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
  "bDestroy": true,
  "aoColumnDefs": [
    { "bSortable": false, "aTargets": [ 0 ] },
    { "sSortDataType": "dom-sort-value", "sType": "numeric", "aTargets": [6] },
    { "bVisible": false, "aTargets": [7] }
  ],
  "aaSorting": [[ 6, "desc" ]],
  "fnPreDrawCallback": function( oSettings ) {
    if (designs.allSelected()) {
      designs.selectAll();
    }
  },
  "iDisplayLength" : 25,
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
};
var designTable = $('#designTable').dataTable( designTableOptions );

/**
 * Redraw a table after the table has been dynamically updated.
 * This is necessary because KO and datatables don't play well together.
 * This is useful when datatables doesn't automatically update and no extra rows have been added.
 */
function redraw() {
  designs.isLoading(true);
  designTable.fnDestroy();
  designTable = $('#designTable').dataTable( designTableOptions );
  designTable.fnFilter(designs.inTrash().toString(), 7);
  designs.isLoading(false);
}

/**
 * Reload with datatables.
 * Remove datatables, reload, then reinitialize datatables.
 * Knockout doesn't work without this.
 * Clearing the table is necessary so multiple rows will not be added.
 */

function reload() {
  designs.isLoading(true);
  $(document).one('load.designs', function() {
    if (designTable != null){
      designTable.fnClearTable();
      designTable.fnDestroy();
    }
  });
  $(document).one('initialized.designs', function() {
    designTable = $('#designTable').dataTable( designTableOptions );
    designTable.fnFilter(designs.inTrash().toString(), 7);
    designs.isLoading(false);
    routie('list-designs');
  });
  designs.load();
}

$(document).bind('loaded.designs', function() {
  // Filter should be added again after datatable has been recreated.
  $("#filterInput").keyup(function() {
    if (designTable != null){
      designTable.fnFilter($(this).val());
    }
  });
});

$(document).bind('reload.designs', reload);

reload();

/**
 * Using Mustache templating system: http://mustache.github.com/
 * Templates and partials are loaded in jobsub.templates.js
 * Context is matched up with templates and partials.
 * Routie is used to provide hash routing: http://projects.jga.me/routie/.
 */
var setupRoutes = (function() {
  var eventCount = 0;

  return function(e) {
    if (++eventCount > 1) {
      //// Routes
      routie({
        'new-design/:node_type': function(node_type) {
          /**
           * Update context with correct title.
           * Create empty design to fill.
           * Create template by calling `getActionTemplate`.
           */
          // Show section only after we've finished the new design process.
          $(document).one('created.design', function() {
            showSection('design');
          });

          designs.closeDesign();
          designs.isEditing(true);

          var context = $.extend(true, {}, global_action_context, contexts[node_type]);
          templates.getActionTemplate(node_type, context);
          designs.newDesign(node_type);
        },
        'edit-design/:design_id': function(design_id) {
          /**
           * Update context with correct title.
           * Design is selected through 'list-designs'.
           */
          designs.closeDesign();

          var designObject = designs.getDesignObjectById(design_id);
          if (!designObject) {
            routie('list-designs');
            return;
          }

          // Show section only after we've finished the edit design process.
          $(document).one('edited.design', function() {
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

          designs.isEditing(true);

          var node_type = designObject.design().node_type();
          var context = $.extend(true, {}, global_action_context, contexts[node_type]);
          templates.getActionTemplate(node_type, context);
          designs.deselectAll();
          designObject.selected(true);
          designs.editDesign();
        },
        'trashed-designs': function() {
          $('#home').removeAttr('disabled');
          designs.inTrash(true);
          designs.isEditing(true);
          showSection('list-designs');
          redraw();
        },
        'list-designs': function() {
          $('#home').removeAttr('disabled');
          designs.inTrash(false);
          designs.isEditing(false);
          showSection('list-designs');
          redraw();
        }
      });
    }
  }
})();

$(document).ready(setupRoutes);
$(document).one('loaded.designs', setupRoutes);
$(document).ready(function(e) {
  //// Row selector, buttons, and various features.
  $(".btn[rel='tooltip']").tooltip({'placement':'bottom'});
  $("a[data-row-selector='true']").jHueRowSelector();
  $('#submit-design').click(function() {
    var url = '/oozie/submit_workflow/' + designs.selectedDesign().id();
    $.get(url, function (response) {
        $('#submitWf').html(response);
        $('#submitWf').modal('show');
      }
    );
  });
  $(HUE_CONTAINER).on('click', '#edit-design', function() {
    routie('edit-design/' + designs.selectedDesign().id());
  });
  $(HUE_CONTAINER).on('click', '#trash-designs', function() {
    $('#trashWf').modal('show');
  });
  $(HUE_CONTAINER).on('click', '#destroy-designs', function() {
    $('#destroyWf').modal('show');
  });
  $(HUE_CONTAINER).on('click', '#purge-trashed-designs', function() {
    $('#purgeWf').modal('show');
  });
  $(HUE_CONTAINER).on('click', '#restore-designs', function() {
    $('#restoreWf').modal('show');
  });
  $(HUE_CONTAINER).on('click', '#copy-designs', function() {
    designs.isLoading(true);
    designs.cloneDesigns();
  });
  $('#home').click(function() {
    routie('list-designs');
  });

  // load the autocomplete properties
  var AUTOCOMPLETE_PROPERTIES;
  $.getJSON("${ url('oozie:autocomplete_properties') }", function (data) {
    AUTOCOMPLETE_PROPERTIES = data.properties;
  });
});
</script>

${ commonfooter(request, messages) | n,unicode }
