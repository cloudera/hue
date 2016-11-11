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
  from desktop import conf
  from desktop.views import _ko
  from django.utils.translation import ugettext as _
  from desktop.lib.i18n import smart_unicode
  from desktop.views import login_modal
%>

<%namespace name="assist" file="/assist.mako" />
<%namespace name="hueIcons" file="/hue_icons.mako" />

<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta charset="utf-8">
  <title>Hue</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="icon" type="image/x-icon" href="${ static('desktop/art/favicon.ico') }"/>
  <meta name="description" content="">
  <meta name="author" content="">

  <link href="${ static('desktop/ext/css/bootplus.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/font-awesome.min.css') }" rel="stylesheet">
  <link href="${ static('desktop/css/responsive.css') }" rel="stylesheet">

  <!--[if lt IE 9]>
  <script type="text/javascript">
    if (document.documentMode && document.documentMode < 9) {
      location.href = "${ url('desktop.views.unsupported') }";
    }
  </script>
  <![endif]-->

  <script type="text/javascript" charset="utf-8">
    // check if it's a Firefox < 7
    var _UA = navigator.userAgent.toLowerCase();
    for (var i = 1; i < 7; i++) {
      if (_UA.indexOf("firefox/" + i + ".") > -1) {
        location.href = "${ url('desktop.views.unsupported') }";
      }
    }

    // check for IE document modes
    if (document.documentMode && document.documentMode < 9) {
      location.href = "${ url('desktop.views.unsupported') }";
    }


    var LOGGED_USERNAME = '${ user.username }';
    var IS_S3_ENABLED = '${ is_s3_enabled }' === 'True';


    ApiHelperGlobals = {
      i18n: {
        errorLoadingDatabases: '${ _('There was a problem loading the databases') }',
        errorLoadingTablePreview: '${ _('There was a problem loading the preview') }'
      },
      user: '${ user.username }'
    }
  </script>
</head>

<body>

${ hueIcons.symbols() }

<div class="main-page">
  <div class="top-nav">
    <a class="hamburger hamburger--squeeze pull-left" type="button">
      <span class="hamburger-box">
        <span class="hamburger-inner"></span>
      </span>
    </a>
    <a class="brand nav-tooltip pull-left" title="${_('Homepage')}" rel="navigator-tooltip" href="/home"><img src="${ static('desktop/art/hue-logo-mini-white.png') }" data-orig="${ static('desktop/art/hue-logo-mini-white.png') }" data-hover="${ static('desktop/art/hue-logo-mini-white-hover.png') }"/></a>
    <span style="color:white">

      <span style="font-size: 130%">
       <div class="btn-group" style="vertical-align: middle">
          <a href="${ url('notebook:new') }" title="${ _( 'New Notebook') }">
            <button class="btn btn-primary">
              <i class="fa fa-pencil-square-o"></i> ${ _('Compose') }
            </button>
          </a>
          <button id="trash-btn-caret" class="btn toolbarBtn dropdown-toggle" data-toggle="dropdown" title="${ _( 'Compose query or job') }">
            <span class="caret"></span>
          </button>
          <ul role="menu" class="dropdown-menu" title="${ _( 'Compose query or job') }">
           % if 'beeswax' in apps:
             <li><a href="${ url('notebook:editor') }?type=hive"><img src="${ static(apps['beeswax'].icon_path) }" class="app-icon"/> ${_('Hive')}</a></li>
           % endif
           % if 'impala' in apps: ## impala requires beeswax anyway
             <li><a href="${ url('notebook:editor') }?type=impala"><img src="${ static(apps['impala'].icon_path) }" class="app-icon"/> ${_('Impala')}</a></li>
           % endif
           % if 'search' in apps:
           <li>
             <a href="${ url('search:new_search') }" style="height: 24px; line-height: 24px!important;">
               <img src="${ static('search/art/icon_search_48.png') }" class="app-icon"/> ${ _('Dashboard') }</a>
           </li>
           % endif
           % if 'oozie' in apps:
           <li class="dropdown oozie">
             <img src="${ static('oozie/art/icon_oozie_editor_48.png') }" class="app-icon" /> <a title="${_('Schedule with Oozie')}" rel="navigator-tooltip" href="#" data-toggle="dropdown" class="dropdown-toggle">${ _('Workflows') }</span> <b class="caret"></b></a>
             <ul role="menu" class="dropdown-menu">
               % if not user.has_hue_permission(action="disable_editor_access", app="oozie") or user.is_superuser:
               <li class="dropdown-submenu">
                 <a href="${ url('oozie:list_editor_workflows') }"><img src="${ static('oozie/art/icon_oozie_editor_48.png') }" class="app-icon" /> ${_('Editors')}</a>
                 <ul class="dropdown-menu">
                   <li><a href="${url('oozie:list_editor_workflows')}"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon"/> ${_('Workflows')}</a></li>
                   <li><a href="${url('oozie:list_editor_coordinators')}"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" /> ${_('Coordinators')}</a></li>
                   <li><a href="${url('oozie:list_editor_bundles')}"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" /> ${_('Bundles')}</a></li>
                 </ul>
               </li>
               % endif
             </ul>
           </li>
           % endif
         <li>
            <a href="/${apps['jobsub'].display_name}">
              ${ _('More >>') }
            </a>
         </li>
         % for interpreter in interpreters:
          <li>
             <a href="${ url('notebook:editor') }?type=${ interpreter['type'] }">
               ${ interpreter['name'] }
             </a>
           </li>
         % endfor
         % if user.is_superuser:
         <li>
            <a href="gethue.com">
              ${ _('Add more...') }
            </a>
         </li>
         % endif
        </ul>
      </div>

      </span>

      <input class="input-xxlarge" placeholder="${ _('Search all data and saved documents...') }"></input> <i class="fa fa-search"></i>

      <div class="pull-right">

        % if user.is_authenticated() and section != 'login':
        <ul class="nav nav-pills">

        <li>
          <div class="btn-group" style="vertical-align: middle">
            <a href="${ url('notebook:new') }">
              <button class="btn btn-primary">
                ${ _('research queue') }
              </button>
            </a>
            <button id="trash-btn-caret" class="btn toolbarBtn dropdown-toggle" data-toggle="dropdown">
              <span class="caret"></span>
            </button>
            <ul role="menu" class="dropdown-menu">
              <li>
                <a href='#' class="ignore-btn confirmationModal">
                  ${ _('Production') }
                </a>
              </li>
              <li>
                <a href='#' class="ignore-btn confirmationModal">
                  ${ _('ETL analytics') }
                </a>
              </li>
              <li>
                <a href='#' class="ignore-btn confirmationModal">
                  <i class="fa fa-plus"></i> ${ _('Create') }
                </a>
              </li>
            </ul>
          </div>
        </li>

        <li>
          <span title="Running jobs and workflows">
            <a title="${_('Manage jobs')}" rel="navigator-tooltip" href="/jobbrowser/apps" style="color:white">
              <i class="fa fa-circle-o"></i> ${ _('Jobs') }
            </a>
            <span class="badge badge-warning">20</span>
            ## Batches
            ## Schedules
          </span>
        </li>

        % if 'oozie' in apps: # Merged with Jobs eventually
        <li>
          <span title="Running workflows">
            <a title="${_('Manage jobs')}" rel="navigator-tooltip" href="${ url('oozie:index') }" style="color:white">
              <i class="fa fa-circle-o"></i> ${ _('Workflows') }
            </a>
            <span class="badge badge-warning">10</span>
          </span>
            ## Coordinators
            ## Bundles
        </li>
        % endif

        <li>
          <span title="Notifications"><i class="fa fa-bell-o"></i> <span class="badge badge-success">10</span></span>
        </li>

        <li>
          <i class="fa fa-question-circle"></i>
        </li>

        <%
          view_profile = user.has_hue_permission(action="access_view:useradmin:edit_user", app="useradmin") or user.is_superuser
        %>
        <li class="dropdown">
          <a title="${ _('Administration') if view_profile else '' }" href="index.html#" rel="navigator-tooltip" data-toggle="dropdown" class="dropdown-toggle" style="color:white">
            <i class="fa fa-cogs"></i>&nbsp;${user.username}&nbsp;
            % if view_profile:
              <b class="caret"></b>
            % endif
          </a>
          % if view_profile:
          <ul class="dropdown-menu pull-right">
            <li>
              <a href="${ url('useradmin.views.edit_user', username=user.username) }"><i class="fa fa-user-circle"></i>&nbsp;&nbsp;
                % if is_ldap_setup:
                  ${_('View Profile')}
                % else:
                  ${_('Edit Profile')}
                % endif
              </a>
            </li>
            % if user.is_superuser:
              <li><a href="${ url('useradmin.views.list_users') }"><i class="fa fa-group"></i> ${_('Manage Users')}</a></li>
              <li><a href="${ url('useradmin.views.list_permissions') }"><i class="fa fa-key"></i> ${_('Set Permissions')}</a></li>
              <li><a href="/about"><img src="${ static('desktop/art/hue-logo-mini-white.png') }" data-orig="${ static('desktop/art/hue-logo-mini-white.png') }" data-hover="${ static('desktop/art/hue-logo-mini-white-hover.png') }" /> ${_('About Hue')}</a></li>
            % endif
            <li>
              <a title="${_('Sign out')}" href="/accounts/logout/"><i class="fa fa-sign-out"></i> ${ _('Sign out') }</a>
            </li>
          </ul>
        % endif
        </li>
      </ul>
    </div>
    % endif
  </div>

  <div class="content-wrapper">
    <div class="left-nav">
      <a href="javascript:void(0);" data-bind="click: function () { huePubSub.publish('switch.app', 'editor'); }">Query</a><br/>
      <br/>
      [Hive, Impala, Pig, PySpark, Solr, MapReduce...]<br/>

      <br/>

      Search Dashboards<br/>

      <br/>

      <a href="javascript:void(0);" data-bind="click: function () { huePubSub.publish('switch.app', 'metastore'); }">Browse</a><br/>
      [Tables]<br/>
      [Files]<br/>
      [Indexes]<br/>
      [HBase]<br/>

      <br/>

      Jobs<br/>
      [YARN, MR, Hive, Impala, Spark, Sqoop, Pig]<br/>
      Batch<br/>
      Schedules<br/>
      <br/>

      Oozie<br/>
      Workflows<br/>
      Coordinators<br/>
      Bundles<br/>
      <br/>
      
      Security<br/>
      Hive Tables<br/>
      Solr Collections<br/>
      HDFS Acls<br/>
      <br/>

      [Custom App 1]<br/>
      [Custom App 2]<br/>


      <span style="position: fixed; bottom: 0">
      Create Table<br/>
      Import File<br/>
      Import Queries<br/>
      [+]
      <br/>&nbsp
      </span>
    </div>

    <div id="assist-container" class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable()">
      <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
        <i class="fa fa-chevron-left"></i>
      </a>

      <div class="assist" data-bind="component: {
          name: 'assist-panel',
          params: {
            user: '${user.username}',
            sql: {
              sourceTypes: [{
                name: 'hive',
                type: 'hive'
              }],
              navigationSettings: {
                openItem: false,
                showStats: true
              }
            },
            visibleAssistPanels: ['sql']
          }
        }"></div>
    </div>

    <div class="resizer" data-bind="splitDraggable : { appName: 'notebook', leftPanelVisible: isAssistVisible, onPosition: function(){ huePubSub.publish('split.draggable.position') } }"><div class="resize-bar">&nbsp;</div></div>

    <div class="page-content">
      <a href="javascript: void(0);" title="${_('Toggle Assist')}" class="pointer show-assist" style="display:none;">
        <i class="fa fa-chevron-right"></i>
      </a>
      ##<div data-bind='component: currentApp'></div>
      <div data-bind='text: currentApp'></div>
    </div>
  </div>
</div>

<script src="${ static('desktop/ext/js/jquery/jquery-2.2.3.min.js') }"></script>
<script src="${ static('desktop/js/hue.utils.js') }"></script>
<script src="${ static('desktop/ext/js/bootstrap.min.js') }"></script>
<script src="${ static('desktop/ext/js/moment-with-locales.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.total-storage.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery.cookie.js') }"></script>


<script src="${ static('desktop/ext/js/jquery/plugins/jquery.basictable.min.js') }"></script>
<script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }"></script>
<script src="${ static('desktop/ext/js/knockout.min.js') }"></script>
<script src="${ static('desktop/js/apiHelper.js') }"></script>
<script src="${ static('desktop/js/ko.charts.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }"></script>
<script src="${ static('desktop/ext/js/knockout-sortable.min.js') }"></script>
<script src="${ static('desktop/js/ko.editable.js') }"></script>
<script src="${ static('desktop/js/ko.hue-bindings.js') }"></script>

${ assist.assistJSModels() }

## Dynamic loading of apps
##<script src="${ static('desktop/ext/js/text.js') }"></script>
##<script src="${ static('desktop/js/ko.editor.js') }"></script>
##<script src="${ static('desktop/js/ko.metastore.js') }"></script>


${ assist.assistPanel() }

<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
  <i class="fa fa-chevron-right"></i>
</a>


<script type="text/javascript" charset="utf-8">
    var OnePageViewModel = function () {
      var self = this;

      self.currentApp = ko.observable('editor');

      huePubSub.subscribe('switch.app', function (name) {
        console.log(name);
        self.currentApp(name);
      })
    }

    var AssistViewModel = function (options) {
      var self = this;

      self.apiHelper = ApiHelper.getInstance(options);
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable();
      self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);
    };

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        i18n: {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
        }
      };

      ko.applyBindings(new OnePageViewModel(), $('.page-content')[0]);

      //ko.applyBindings({}, $('.left-nav')[0])
      ko.applyBindings(new AssistViewModel(options), $('#assist-container')[0])

      var isAssistVisible = ko.observable(true);
      isAssistVisible.subscribe(function (newValue) {
        if (!newValue) {
          $('.show-assist').show();
        }
      });
  });

  $('.show-assist').click(function () {
    isAssistVisible(true);
    $('.show-assist').hide();
  })

  $(".hamburger").click(function () {
    $(this).toggleClass("is-active");
    $(".left-nav").toggleClass("left-nav-visible");
  })

  moment.locale(window.navigator.userLanguage || window.navigator.language);
  localeFormat = function (time) {
    var mTime = time;
    if (typeof ko !== 'undefined' && ko.isObservable(time)) {
      mTime = time();
    }
    try {
      mTime = new Date(mTime);
      if (moment(mTime).isValid()) {
        return moment.utc(mTime).format("L LT");
      }
    }
    catch (e) {
      return mTime;
    }
    return mTime;
  }

  // Add CSRF Token to all XHR Requests
  var xrhsend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function (data) {
    % if request and request.COOKIES and request.COOKIES.get('csrftoken'):
      this.setRequestHeader('X-CSRFToken', "${ request.COOKIES.get('csrftoken') }");
    % else:
      this.setRequestHeader('X-CSRFToken', "");
    % endif

    return xrhsend.apply(this, arguments);
  }

  // Set global assistHelper TTL
  $.totalStorage('hue.cacheable.ttl', ${conf.CUSTOM.CACHEABLE_TTL.get()});

  $(document).ready(function () {
##       // forces IE's ajax calls not to cache
##       if ($.browser.msie) {
##         $.ajaxSetup({ cache: false });
##       }

    // prevents framebusting and clickjacking
    if (self == top) {
      $("body").css({
        'display': 'block',
        'visibility': 'visible'
      });
    } else {
      top.location = self.location;
    }

    %if conf.AUTH.IDLE_SESSION_TIMEOUT.get() > -1 and not skip_idle_timeout:
      var idleTimer;

      function resetIdleTimer() {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(function () {
          // Check if logged out
          $.get('/desktop/debug/is_idle');
        }, ${conf.AUTH.IDLE_SESSION_TIMEOUT.get()} * 1000 + 1000
        );
      }

      $(document).on('mousemove', resetIdleTimer);
      $(document).on('keydown', resetIdleTimer);
      $(document).on('click', resetIdleTimer);
      resetIdleTimer();
    %endif

    % if 'jobbrowser' in apps:
      var JB_CHECK_INTERVAL_IN_MILLIS = 30000;
      var checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, 10);

      function checkJobBrowserStatus(){
        $.post("/jobbrowser/jobs/", {
            "format": "json",
            "state": "running",
            "user": "${user.username}"
          },
          function(data) {
            if (data != null && data.jobs != null) {
              huePubSub.publish('jobbrowser.data', data.jobs);
              if (data.jobs.length > 0){
                $("#jobBrowserCount").removeClass("hide").text(data.jobs.length);
              }
              else {
                $("#jobBrowserCount").addClass("hide");
              }
            }
          checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);
        }).fail(function () {
          window.clearTimeout(checkJobBrowserStatusIdx);
        });
      }
      huePubSub.subscribe('check.job.browser', checkJobBrowserStatus);
    % endif
  });
</script>

<script type="text/javascript">

  $(document).ready(function () {
    // global catch for ajax calls after the user has logged out
    var isLoginRequired = false;
    $(document).ajaxComplete(function (event, xhr, settings) {
      if (xhr.responseText === '/* login required */' && !isLoginRequired) {
        isLoginRequired = true;
        $('body').children(':not(#login-modal)').addClass('blurred');
        if ($('#login-modal').length > 0) {
          $('#login-modal').modal('show');
          window.setTimeout(function () {
            $('.jHueNotify').remove();
          }, 200);
        }
        else {
          location.reload();
        }
      }
    });

    $('#login-modal').on('hidden', function () {
      isLoginRequired = false;
      $('.blurred').removeClass('blurred');
    });

    huePubSub.subscribe('hue.login.result', function (response) {
      if (response.auth) {
        $('#login-modal').modal('hide');
        $.jHueNotify.info('${ _('You have signed in successfully!') }');
        $('#login-modal .login-error').addClass('hide');
      } else {
        $('#login-modal .login-error').removeClass('hide');
      }
    });
  });

  $(".modal").on("shown", function () {
    // safe ux enhancement: focus on the first editable input
    $(".modal:visible").find("input:not(.disable-autofocus):visible:first").focus();
  });

    %if collect_usage:
      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', 'UA-40351920-1']);

      // We collect only 2 path levels: not hostname, no IDs, no anchors...
      var _pathName = location.pathname;
      var _splits = _pathName.substr(1).split("/");
      _pathName = _splits[0] + (_splits.length > 1 && $.trim(_splits[1]) != "" ? "/" + _splits[1] : "");

      _gaq.push(['_trackPageview', '/remote/${ version }/' + _pathName]);

      (function () {
        var ga = document.createElement('script');
        ga.type = 'text/javascript';
        ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(ga, s);
      })();

      function trackOnGA(path) {
        if (typeof _gaq != "undefined" && _gaq != null) {
          _gaq.push(['_trackPageview', '/remote/${ version }/' + path]);
        }
      }
    %endif
</script>
</body>
</html>