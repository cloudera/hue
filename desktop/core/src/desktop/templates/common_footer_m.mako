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
from django.http import HttpRequest
from django.utils.translation import ugettext as _
from django.template.defaultfilters import escape, escapejs
from desktop.lib.i18n import smart_unicode
%>



<script type="text/javascript">
  $(document).ready(function () {
    $(document).on("info", function (e, msg) {
      $.jHueNotify.info(msg);
    });
    $(document).on("warn", function (e, msg) {
      $.jHueNotify.warn(msg);
    });
    $(document).on("error", function (e, msg) {
      $.jHueNotify.error(msg);
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
  });

  if (typeof nv != "undefined"){
    // hides all the nvd3 logs
    nv.log = function() {};
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
      'page': '/remote/${ version }/' + _pathName
    });

    function trackOnGA(path) {
      if (typeof ga != "undefined" && ga != null) {
        ga('set', 'referrer', 'http://gethue.com'); // we force the referrer to prevent leaking sensitive information
        ga('send', 'pageview', {
          'page': '/remote/${ version }/' + path
        });
      }
    }

  %endif

</script>
  </body>
</html>
