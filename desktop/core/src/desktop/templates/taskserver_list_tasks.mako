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


<div id="tasksComponents" class="taskserver container-fluid">
<div class="container-fluid">
  <div class="card card-small">
    <h1>${message}</h1> <!-- Display the message passed from the view -->
    <h1 class="card-heading simple">Task Browser</h1>



    <script type="text/javascript">
      (function () {
        window.createReactComponents('#some-container');
      })();
    </script>

<!--    <script type="text/javascript">-->
<!--      (function () {-->
<!--        const container = document.getElementById('some-container');-->

<!--        ReactDOM.render(-->
<!--          React.createElement(TaskBrowserTable, null),-->
<!--          container-->
<!--        );-->
<!--      })();-->
<!--    </script>-->

    <div id="some-container">
      <MyComponent data-reactcomponent='TaskBrowser' data-props='{"myObj": {"id": 1}, "children": "mako template only", "version" : "${sys.version_info[0]}"}' ></MyComponent>
    </div>

  </div>
</div>
</div>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif