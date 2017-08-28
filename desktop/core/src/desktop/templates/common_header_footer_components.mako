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
from django.template.defaultfilters import escape, escapejs

from desktop import conf
from desktop.lib.i18n import smart_unicode

from beeswax.conf import LIST_PARTITIONS_LIMIT

from metadata.conf import has_optimizer, OPTIMIZER
%>

<%def name="header_i18n_redirection(user, is_s3_enabled, apps)">
  <script type="text/javascript">

    var LOGGED_USERNAME = '${ user.username }';
    var IS_S3_ENABLED = '${ is_s3_enabled }' === 'True';
    var HAS_OPTIMIZER = '${ has_optimizer() }' === 'True';

    %if request and request.COOKIES and request.COOKIES.get('csrftoken','')!='':
    window.CSRF_TOKEN = '${request.COOKIES.get('csrftoken')}';
    %else:
    window.CSRF_TOKEN = '';
    %endif

    var BOOTSTRAP_RATIOS = {
      SPAN3: function () {
        var _w = $(window).width();
        if (_w >= 1200) {
          return 23.07692308;
        }
        else if (_w >= 768 && _w <= 979) {
          return 22.9281768;
        }
        else {
          return 23.17073171;
        }
      },
      SPAN9: function () {
        var _w = $(window).width();
        if (_w >= 1200) {
          return 74.35897436;
        }
        else if (_w >= 768 && _w <= 979) {
          return 74.30939227;
        }
        else {
          return 74.3902439;
        }
      },
      MARGIN: function () {
        return 2.56410256;
      }
    };

    var CACHEABLE_TTL = {
      default: ${ conf.CUSTOM.CACHEABLE_TTL.get() },
      optimizer: ${ OPTIMIZER.CACHEABLE_TTL.get() }
    };

    var AUTOCOMPLETE_TIMEOUT = ${ conf.EDITOR_AUTOCOMPLETE_TIMEOUT.get() };

    var ENABLE_SQL_SYNTAX_CHECK = '${ conf.ENABLE_SQL_SYNTAX_CHECK.get() }' === 'True';

    var DocumentTypeGlobals = {
      'all': '${_('All')}',
      'directory': '${ _('Directory') }',
      'link-pigscript': '${_('Pig Design')}',
      'link-workflow': '${_('Job Design')}',
      'notebook': '${_('Notebook')}',
      'oozie-bundle2': '${_('Oozie Bundle')}',
      'oozie-coordinator2': (IS_HUE_4 ? '${_('Oozie Schedule')}' : '${_('Oozie Coordinator')}'),
      'oozie-workflow2': '${_('Oozie Workflow')}',
      'query-hive': '${_('Hive Query')}',
      'query-impala': '${_('Impala Query')}',
      'search-dashboard': '${_('Search Dashboard')}',
      'query-mapreduce': '${_('MapReduce Job')}',
      'query-sqoop1': '${_('Import Job')}',
      'query-spark2': '${_('Spark Job')}',
      'query-java': '${_('Java Job')}',
      'query-pig': '${_('Pig Script')}',
      'query-shell': '${_('Shell Script')}',
      'query-distcp': '${_('DistCp Job')}'
    };

    var SyntaxCheckerGlobals = {
      i18n: {
        didYouMean: '${_('Did you mean')}',
        expectedStatementEnd: '${_('Expected end of statement')}',
        suppressError: '${_('Ignore this type of error')}',
        couldNotFind: '${_('Could not find')}'
      }
    };

    // jHue plugins global configuration
    var jHueFileChooserGlobals = {
      labels: {
        BACK: "${_('Back')}",
        SELECT_FOLDER: "${_('Select this folder')}",
        CREATE_FOLDER: "${_('Create folder')}",
        FOLDER_NAME: "${_('Folder name')}",
        CANCEL: "${_('Cancel')}",
        FILE_NOT_FOUND: "${_('The file has not been found')}",
        UPLOAD_FILE: "${_('Upload a file')}",
        FAILED: "${_('Failed')}"
      },
      user: "${ user.username }"
    };

    var jHueHdfsTreeGlobals = {
      labels: {
        CREATE_FOLDER: "${_('Create folder')}",
        FOLDER_NAME: "${_('Folder name')}",
        CANCEL: "${_('Cancel')}"
      }
    };

    var jHueTableExtenderGlobals = {
      labels: {
        GO_TO_COLUMN: "${_('Go to column:')}",
        PLACEHOLDER: "${_('column name...')}",
        LOCK: "${_('Lock this row')}",
        UNLOCK: "${_('Unlock this row')}",
        ROW_DETAILS: "${_('Show row details')}"
      }
    };

    var LeafletGlobals = {
      layer: '${ leaflet['layer'] |n,unicode }',
      attribution: '${ leaflet['attribution'] |n,unicode }'
    };

    var ApiHelperGlobals = {
      i18n: {
        errorLoadingDatabases: '${ _('There was a problem loading the databases') }',
        errorLoadingTablePreview: '${ _('There was a problem loading the preview') }'
      },
      user: '${ user.username }'
    };

    var DropzoneGlobals = {
      homeDir: '${ user.get_home_directory() if not user.is_anonymous() else "" }',
      i18n: {
        cancelUpload: '${ _('Cancel upload') }',
        uploadCanceled: '${ _('The upload has been canceled') }',
        uploadSucceeded: '${ _('uploaded successfully') }'
      }
    };

    var MetastoreGlobals = {
      partitionsLimit: ${ hasattr(LIST_PARTITIONS_LIMIT, 'get') and LIST_PARTITIONS_LIMIT.get() or 1000 },
      i18n: {
        errorRefreshingTableStats: '${_('An error occurred refreshing the table stats. Please try again.')}',
        errorLoadingDatabases: '${ _('There was a problem loading the databases. Please try again.') }',
        errorLoadingTablePreview: '${ _('There was a problem loading the table preview. Please try again.') }'
      }
    };

    var AutocompleterGlobals = {
      i18n: {
        category: {
          all: '${ _('All') }',
          column: '${ _('Columns') }',
          cte: '${ _('CTEs') }',
          database: '${ _('Databases') }',
          identifier: '${ _('Identifiers') }',
          keyword: '${ _('Keywords') }',
          popular: '${ _('Popular') }',
          sample: '${ _('Samples') }',
          table: '${ _('Tables') }',
          udf: '${ _('UDFs') }',
          variable: '${ _('Variables') }'
        },
        meta: {
          aggregateFunction: '${ _('aggregate') }',
          alias: '${ _('alias') }',
          commonTableExpression: '${ _('cte') }',
          database: '${ _('database') }',
          filter: '${ _('filter') }',
          groupBy: '${ _('group by') }',
          join: '${ _('join') }',
          joinCondition: '${ _('condition') }',
          keyword: '${ _('keyword') }',
          orderBy: '${ _('order by') }',
          table: '${ _('table') }',
          sample: '${ _('sample') }',
          variable: '${ _('variable') }',
          view: '${ _('view') }',
          virtual: '${ _('virtual') }'
        }
      }
    };

    var QueryBuilderGlobals = {
      i18n: {
        INSERT_VALUE_HERE: "${ _('Insert value here') }",
        QUERY_REQUIRE: "${ _('Query requires a select or aggregate.') }"
      }
    }

    var CopyToClipboardGlobals = {
      i18n: {
        ERROR: "${ _('Error while copying results.') }",
        SUCCESS: "${ _('Results copied successfully to the clipboard') }",
      }
    }

    var SelectizeGlobals = {
      i18n: {
        CHOOSE: "${ _('Choose...') }"
      }
    }
  </script>

  <!--[if lt IE 9]>
  <script type="text/javascript">
    if (document.documentMode && document.documentMode < 9){
      location.href = "${ url('desktop.views.unsupported') }";
    }
  </script>
  <![endif]-->


  <script type="text/javascript">
    // check if it's a Firefox < 7
    var _UA = navigator.userAgent.toLowerCase();
    for (var i = 1; i < 7; i++) {
      if (_UA.indexOf("firefox/" + i + ".") > -1) {
        location.href = "${ url('desktop.views.unsupported') }";
      }
    }

    // check for IE document modes
    if (document.documentMode && document.documentMode < 9){
      location.href = "${ url('desktop.views.unsupported') }";
    }

    // sets a global variable to see if it's IE11 or not
    var isIE11 = !!window.MSInputMethodContext && !!document.documentMode;
  </script>
</%def>

<%def name="header_pollers(user, is_s3_enabled, apps)">
  <script type="text/javascript">
    Dropzone.autoDiscover = false;
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
    };

    // Catches HTTP 502 errors
    function xhrOnreadystatechange() {
      if (this.readyState === 4 && this.status === 502) {
        $.jHueNotify.error($('<span>').html(this.responseText).text());
      }
      if (this._onreadystatechange) {
        return this._onreadystatechange.apply(this, arguments);
      }
    }

    var xhrSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function (data) {
      // Add CSRF Token to all XHR Requests
      this.setRequestHeader('X-CSRFToken', window.CSRF_TOKEN);

      if (this.onreadystatechange) {
        this._onreadystatechange = this.onreadystatechange;
      }
      this.onreadystatechange = xhrOnreadystatechange;
      return xhrSend.apply(this, arguments);
    };
    XMLHttpRequest.prototype.isAugmented = true;

    $.fn.dataTableExt.sErrMode = "throw";

    var IDLE_SESSION_TIMEOUT = -1;

    $(document).ready(function () {
      // forces IE's ajax calls not to cache
      if ($.browser.msie) {
        $.ajaxSetup({ cache: false });
      }

      // prevents framebusting and clickjacking
      if (self == top){
        $("body").css({
          'display': 'block',
          'visibility': 'visible'
        });
      }
      else {
        top.location = self.location;
      }

      %if conf.AUTH.IDLE_SESSION_TIMEOUT.get() > -1 and not skip_idle_timeout:
      IDLE_SESSION_TIMEOUT = ${conf.AUTH.IDLE_SESSION_TIMEOUT.get()};
      var idleTimer;
      function resetIdleTimer() {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(function () {
          // Check if logged out
          $.get('/desktop/debug/is_idle');
        }, (IDLE_SESSION_TIMEOUT * 1000) + 1000);
      }

      $(document).on('mousemove', resetIdleTimer);
      $(document).on('keydown', resetIdleTimer);
      $(document).on('click', resetIdleTimer);
      resetIdleTimer();
      %endif

      $(".submitter").keydown(function (e) {
        if (e.keyCode == 13) {
          $(this).closest("form").submit();
        }
      }).change(function () {
          $(this).closest("form").submit();
      });

      $(".navbar .nav-tooltip").tooltip({
        delay: 0,
        placement: "bottom"
      });

      $("[rel='tooltip']").tooltip({
        delay: 0,
        placement: "bottom"
      });

      $("[data-rel='navigator-tooltip']").tooltip({
        delay: 0,
        placement: "bottom"
      });

      % if 'jobbrowser' in apps:
      if (!IS_HUE_4) {
        var JB_CHECK_INTERVAL_IN_MILLIS = 30000;
        var checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, 10);
        var lastJobBrowserRequest = null;

        function checkJobBrowserStatus() {
          if (lastJobBrowserRequest !== null && lastJobBrowserRequest.readyState < 4) {
            return;
          }
          window.clearTimeout(checkJobBrowserStatusIdx);
          lastJobBrowserRequest = $.post("/jobbrowser/jobs/", {
                "format": "json",
                "state": "running",
                "user": "${user.username}"
              },
              function (data) {
                if (data != null && data.jobs != null) {
                  huePubSub.publish('jobbrowser.data', data.jobs);
                  if (data.jobs.length > 0) {
                    $("#jobBrowserCount").show().text(data.jobs.length);
                  } else {
                    $("#jobBrowserCount").hide();
                  }
                }
                checkJobBrowserStatusIdx = window.setTimeout(checkJobBrowserStatus, JB_CHECK_INTERVAL_IN_MILLIS);
              }).fail(function () {
            window.clearTimeout(checkJobBrowserStatusIdx);
          });
        }

        huePubSub.subscribe('check.job.browser', checkJobBrowserStatus);
      }
      % endif

      function openDropdown(which, timeout){
        var _this = which;
        var _timeout = timeout!=null?timeout:800;
        if ($(".navigator").find("ul.dropdown-menu:visible").length > 0) {
          _timeout = 10;
        }
        window.clearTimeout(closeTimeout);
        openTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator .nav-pills li.dropdown > ul.dropdown-menu").hide();
          $("[data-rel='navigator-tooltip']").tooltip("hide");
          _this.find("ul.dropdown-menu:eq(0)").show();
        }, _timeout);
      }

      var openTimeout, closeTimeout;
      $(".navigator ul.nav li.dropdown").on("click", function(){
        openDropdown($(this), 10);
      });
      $(".navigator ul.nav li.dropdown").hover(function () {
        openDropdown($(this));
      },
      function () {
        window.clearTimeout(openTimeout);
        closeTimeout = window.setTimeout(function () {
          $(".navigator li.open").removeClass("open");
          $(".navigator li a:focus").blur();
          $(".navigator").find("ul.dropdown-menu").hide();
        }, 1000);
      });

      function showSubmenu(menuElement) {
        $(".tooltip").remove();
        menuElement.data("lastShown", (new Date()).getTime())
        menuElement.show();
      }

      $(".navigator ul.nav li.dropdown-submenu a").on("mouseenter", function () {
        showSubmenu($(this).siblings(".dropdown-menu"));
      });

      $(".navigator ul.nav li.dropdown-submenu a img").on("mouseenter", function () {
        showSubmenu($(this).parent().siblings(".dropdown-menu"));
      });

      $(".navigator ul.nav li.dropdown-submenu").on("mouseenter", function () {
        $(this).siblings().find(".dropdown-menu").hide();
        showSubmenu($(this).find(".dropdown-menu"));
      });

      $(".navigator ul.nav li.dropdown-submenu").on("mouseleave", function () {
        var _lastShown = $(this).find(".dropdown-menu").data("lastShown");
        if (_lastShown == null || (new Date()).getTime() - _lastShown > 300) {
          var _el = $(this);
          _el.hideTimeout = window.setTimeout(function () {
            window.clearTimeout(_el.hideTimeout);
            _el.find(".dropdown-menu").hide();
          }, 50);
        }
      });

      window.hueDebug = {
        viewModel: function (element) {
          if (typeof element !== 'undefined' && typeof element === 'string') {
            element = $(element)[0];
          }
          return ko.dataFor(element || document.body);
        }
      }
    });
  </script>

</%def>

<%def name="footer(messages)">

<div id="progressStatus" class="uploadstatus well hide">
  <h4>${ _('Upload progress') }</h4>
  <div id="progressStatusBar" class="hide progress">
    <div class="bar bar-upload"></div>
  </div>
  <div id="progressStatusContent" class="scrollable-uploadstatus">
    <div class="updateStatus"> </div>
  </div>
</div>

<div id="chooseFile" class="modal hide fade" style="z-index: 10000;" tabindex="-1">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Choose a file')}</h2>
  </div>
  <div class="modal-body">
    <div id="filechooser"></div>
  </div>
  <div class="modal-footer"></div>
</div>

<div id="rowDetailsModal" class="modal transparent-modal hide" data-backdrop="true" style="width:980px;margin-left:-510px!important;z-index:1071">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${_('Row details')}</h2>
  </div>
  <div class="modal-body">
    <table class="table table-condensed">

    </table>
  </div>
</div>

<script type="text/javascript">

  huePubSub.subscribe('set.hue.version', function (version) {
    $.post("/desktop/api2/user_preferences/hue_version", {
      set: version
    }, function (data) {
      if (data && data.status == 0) {
        location.href = version === 3 ? window.location.pathname.substr(4) + window.location.search : '/hue' + window.location.pathname + window.location.search
      }
      else {
        $.jHueNotify.error("${ _('An error occurred while saving your default Hue preference. Please try again...') }");
      }
    });
  });


  $(document).ready(function () {

    huePubSub.subscribe('table.row.dblclick', function(data){
      var $el = $(data.table);
      var $t = $('#rowDetailsModal').find('table');
      $t.html('');
      var html = '';
      $el.find('thead th').each(function (colIdx, col) {
        if (colIdx > 0){
          html += '<tr><th width="10%">' + $(col).text() + '</th><td>' + $el.data('data')[data.idx][colIdx] + '</td></tr>';
        }
      });
      $t.html(html);
      $('#rowDetailsModal').modal('show');
    });

    $('#rowDetailsModal').on('shown', function () {
      $('.modal-backdrop').css('z-index', '1070');
    });

    if ($.fn.editableform) {
      $.fn.editableform.buttons =
          '<button type="submit" class="btn btn-primary editable-submit disable-feedback">' +
          '<i class="fa fa-fw fa-check"></i>' +
          '</button>' +
          '<button type="button" class="btn btn-default editable-cancel">' +
          '<i class="fa fa-fw fa-times"></i>' +
          '</button>';
    }

    $(document).on("info", function (e, msg) {
      $.jHueNotify.info(msg);
    });
    $(document).on("warn", function (e, msg) {
      $.jHueNotify.warn(msg);
    });
    $(document).on("error", function (e, msg) {
      $.jHueNotify.error(msg);
    });

    $($('#zoomDetectFrame')[0].contentWindow).resize(function () {
      $(window).trigger('zoom');
    });

    %if messages:
      %for message in messages:
        %if message.tags == 'error':
          $(document).trigger('error', '${ escapejs(escape(message)) }');
        %elif message.tags == 'warning':
          $(document).trigger('warn', '${ escapejs(escape(message)) }');
        %else:
          $(document).trigger('info', '${ escapejs(escape(message)) }');
        %endif
      %endfor
    %endif

    // global catch for ajax calls after the user has logged out
    var isLoginRequired = false;
    $(document).ajaxComplete(function (event, xhr, settings) {
      if (xhr.responseText === '/* login required */') {
        var isAutoLogout = settings.url == '/desktop/debug/is_idle';
        $('.blurred').removeClass('blurred');

        if ($('#login-modal').length > 0 && $('#login-modal').is(':hidden')) {
          $('#login-modal .link-message').hide();
          if (isAutoLogout) {
            $('body').children(':not(#login-modal)').addClass('blurred');
            $('#login-modal .auto-logged-out').show();
            $('#login-modal').modal({
              backdrop: 'static',
              keyboard: false
            });
          }
          else {
            $('#login-modal .logged-out').show();
            $('#login-modal').modal({
              backdrop: false,
              keyboard: true
            });
          }
          window.setTimeout(function () {
            $('.jHueNotify').remove();
          }, 200);
        }
      }
    });

    $('#login-modal').on('hidden', function () {
      isLoginRequired = false;
      $('.blurred').removeClass('blurred');
    });

    huePubSub.subscribe('hue.login.result', function (response) {
      if (response.auth) {
        if ($('#login-modal #id_username').val() !== LOGGED_USERNAME) { //LOGGED_USERNAME is in common_header
          location.reload();
        }
        else {
          $('#login-modal').modal('hide');
          $.jHueNotify.info('${ _('You have signed in successfully!') }');
          $('#login-modal .login-error').addClass('hide');
        }
      }
      else {
        $('#login-modal .login-error').removeClass('hide');
      }
    });

    $("div.navigator ul.dropdown-menu").css("maxHeight", $(window).height() - 50);
    var scrollableDropdownTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(scrollableDropdownTimeout);
      scrollableDropdownTimeout = window.setTimeout(function () {
        $("div.navigator ul.dropdown-menu").css("maxHeight", $(window).height() - 50);
      }, 500);
    });

    $(".dataTables_wrapper").jHueTableScroller();
    var resetTimeout = -1;
    var pendingRequestsInterval = -1;

    // sets feedback on every primary and danger action across Hue
    // can be disabled adding the class "disable-feedback" to the button
    $(document).on("click", ".btn-primary:not(.disable-feedback), .btn-danger:not(.disable-feedback)", function () {
      if (!$(this).hasClass('disabled')) {
        var text = ($(this).text() != "") ? $(this).text() : $(this).val();
        $(this).attr("data-loading-text", text + " ...");
        $(this).button("loading");
        startPendingRequestsPolling();
        resetTimeout = window.setTimeout(function () {
          resetPrimaryButtonsStatus();
        }, 200);
      }
    });

    $(document).on("hidden", ".modal", function () {
      resetPrimaryButtonsStatus();
    });

    $(window).unload(function () {
      window.clearInterval(pendingRequestsInterval);
      window.clearTimeout(resetTimeout);
    });

    $(document).on("submit", "form", function () {
      hasAjaxBeenSent = false;
      window.setInterval(function () {
        window.clearTimeout(resetTimeout);
      }, 10);
    });

    var hasAjaxBeenSent = false;
    $(document).ajaxSend(function () {
      hasAjaxBeenSent = true;
    });

    function startPendingRequestsPolling() {
      pendingRequestsInterval = window.setInterval(function () {
        if (hasAjaxBeenSent) {
          var activeRequests = 0;
          if (jQuery.ajax.active) {
            activeRequests = jQuery.ajax.active;
          }
          else {
            activeRequests = jQuery.active;
          }
          if (activeRequests == 0) {
            resetPrimaryButtonsStatus();
            window.clearInterval(pendingRequestsInterval);
          }
        }
        else {
          window.clearInterval(pendingRequestsInterval);
        }
      }, 200);
    }

    var pageWidth = $(window).width();
    if ($('.page-content').length > 0) {
      pageWidth = $('.page-content').width();
    }
    else if ($('.content-panel').length > 0) {
      pageWidth = $('.content-panel').width();
      document.styleSheets[0].addRule('.form-actions','margin-left: -11px !important');
    }

    document.styleSheets[0].addRule('.form-actions','width: ' + pageWidth + 'px');
  });

  function resetPrimaryButtonsStatus() {
    $(".btn-primary:not(.disable-feedback), .btn-danger:not(.disable-feedback)").button("reset");
  }

  var _catchEnterKeyOnModals = false;

  $(document).on("shown", ".modal", function () {
    _catchEnterKeyOnModals = true;
    // safe ux enhancement: focus on the first editable input
    $(".modal:visible").find('input:not(.disable-autofocus):visible:first').not($('.jHueFilechooserActions input')).focus();
  });

  $(document).on("hidden", ".modal", function () {
    _catchEnterKeyOnModals = false;
  });

  $(document).on("keyup", function (e) {
    var _code = (e.keyCode ? e.keyCode : e.which);
    if (_catchEnterKeyOnModals && $(".modal").is(":visible") && _code == 13) {
      var _currentModal = $(".modal:visible");
      if (!$('.jHueAutocompleteElement').is(':focus')) {
        if (_currentModal.find(".btn-primary:not(.disable-enter)").length > 0) {
          _currentModal.find(".btn-primary:not(.disable-enter)").click();
        }
        else if (_currentModal.find(".btn-danger:not(.disable-enter)").length > 0) {
          _currentModal.find(".btn-danger:not(.disable-enter)").click();
        }
      }
    }
  });

  if (typeof nv != "undefined") {
    // hides all the nvd3 logs
    nv.log = function () {
    };
  }


  %if collect_usage:

    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

    ga('create', 'UA-40351920-1', 'auto');
    ga('set', 'referrer', 'http://gethue.com'); // we force the referrer to prevent leaking sensitive information

    // We collect only 2 path levels: not hostname, no IDs, no anchors...
    var _pathName = location.pathname;
    var _splits = _pathName.substr(1).split("/");
    _pathName = _splits[0] + (_splits.length > 1 && $.trim(_splits[1]) != "" ? "/" + _splits[1] : "");

    ga('send', 'pageview', {
      'page': '/remote/${ version }/' + (IS_HUE_4 ? '4/' : '3/') + _pathName
    });

    function trackOnGA(path) {
      if (typeof ga != "undefined" && ga != null) {
        ga('set', 'referrer', 'http://gethue.com'); // we force the referrer to prevent leaking sensitive information
        ga('send', 'pageview', {
          'page': '/remote/${ version }/' + (IS_HUE_4 ? '4/' : '3/') + path
        });
      }
    }

  %endif

</script>
</%def>