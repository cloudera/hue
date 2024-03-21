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
    <h1 class="card-heading simple">Task List</h1>

    <script type="text/javascript">
      (function () {
        window.createReactComponents('#some-container');
      })();
    </script>

    <script type="text/javascript">
      (function () {
        const container = document.getElementById('some-container');

        ReactDOM.render(
          React.createElement(FallbackComponent, null),
          container
        );
      })();
    </script>

    <div id="some-container">
      <MyComponent data-reactcomponent='MyComponent' data-props='{"myObj": {"id": 1}, "children": "mako template only", "version" : "${sys.version_info[0]}"}' ></MyComponent>
    </div>
  </div>
</div>
</div>

<!--      <script type=“text/javascript”>-->
<!--        (function () {-->
<!--            window.createReactComponents(‘#testroot’);-->
<!--        })();-->
<!--      </script>-->

<!--      <p id=“testroot” style=“position: absolute; z-index: 99999; top: 50px”>-->
<!--        <ReactExampleGlobal data-reactcomponent=‘ReactExampleGlobal’ data-props=‘{“myObj”: {“id”: 1}, “children”: “mako template only”, “version” : “${sys.version_info[0]}“}’></ReactExampleGlobal>-->
<!--      </p>-->


<!--    <%actionbar:render>-->
<!--      <%def name="search()">-->
<!--        <input type="text" class="input-xlarge search-query filter-input" placeholder="${_('Search for tasks...')}">-->
<!--      </%def>-->
<!--    </%actionbar:render>-->

<!--    <table class="table table-condensed datatables">-->
<!--      <thead>-->
<!--        <tr>-->
<!--          <th>${_('Tasks')}</th>-->
<!--          <th>${_('Parameters')}</th>-->
<!--          <th>${_('Schedule interval')}</th>-->
<!--          <th>${_('Triggered by')}</th>-->
<!--          <th width="5%">${_('Is active')}</th>-->
<!--          <th width="15%">${_('Last triggered')}</th>-->
<!--        </tr>-->
<!--      </thead>-->


<!--      <tbody>-->

<!--          <tr class="tableRow">-->
<!--            <td><strong>Task 1</strong></td>-->
<!--            <td>Parameter for Task 1</td>-->
<!--            <td>Interval for Task 1</td>-->
<!--            <td>Triggered by for Task 1</td>-->
<!--            <td><i class="fa fa-check"></i></td>-->
<!--            <td>Last triggered time for Task 1</td>-->
<!--            <td>-->
<!--              <button onclick="triggerTask('Task 1')" class="btn btn-primary">Trigger Task</button>-->
<!--            </td>-->

<!--          </tr>-->

<!--          <tr class="tableRow">-->
<!--            <td><strong>Document clean up</strong></td>-->
<!--            <td>Parameter for Task 2</td>-->
<!--            <td>Interval for Task 2</td>-->
<!--            <td>Triggered by: </td>-->
<!--            <td><i class="fa fa-check"></i></td>-->
<!--            <td>Last triggered time for </td>-->
<!--            <td>-->
<!--              <button onclick="triggerTask('Task 2')" class="btn btn-primary">Trigger Task</button>-->
<!--            </td>-->

<!--          </tr>-->

<!--          <tr class="tableRow">-->
<!--            <td><strong>tmp clean up</strong></td>-->
<!--            <td>Parameter for Task 3</td>-->
<!--            <td>Interval for Task 3</td>-->
<!--            <td>Triggered by: </td>-->
<!--            <td><i class="fa fa-check"></i></td>-->
<!--            <td>Last triggered time for </td>-->
<!--            <td>-->
<!--              <button onclick="triggerTask('Task 3')" class="btn btn-primary">Trigger Task</button>-->
<!--            </td>-->

<!--          </tr>-->

<!--      </tbody>-->
<!--      <tfoot class="hide">-->
<!--      <tr>-->
<!--        <td colspan="8">-->
<!--          <div class="alert">-->
<!--            ${_('There are no users matching the search criteria.')}-->
<!--          </div>-->
<!--        </td>-->
<!--      </tr>-->
<!--      </tfoot>-->
<!--    </table>-->
<!--  </div>-->
<!--  </div>-->
<!--</div>-->

<!--<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>-->


%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif