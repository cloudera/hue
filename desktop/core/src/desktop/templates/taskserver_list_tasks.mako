<%!
import sys
from desktop.views import commonheader, commonfooter
from desktop.auth.backend import is_admin

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />

%if not is_embeddable:
${ commonheader(_('Task Server'), "about", user, request) | n,unicode }
%endif

${ layout.menubar(section='task_server') }


<div class="container-fluid">
  <div class="card card-small">

    <script type="text/javascript">
      (function () {
        window.createReactComponents('#taskbrowser-container');
      })();
    </script>

    <div id="taskbrowser-container">
      <MyComponent data-reactcomponent='TaskBrowser' data-props='{"myObj": {"id": 1}, "children": "mako template only", "version" : "${sys.version_info[0]}"}' ></MyComponent>
    </div>

  </div>
</div>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif