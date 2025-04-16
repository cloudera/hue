<%!
import sys

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />

${ layout.menubar(section='task_server') }

<script src="${ static('desktop/js/task-browser-inline.js') }" type="text/javascript"></script>

<div id="taskbrowser-container" class="cuix antd" style="height: calc(100vh - 110px)">
  <MyComponent data-reactcomponent='TaskServer'/>
</div>
