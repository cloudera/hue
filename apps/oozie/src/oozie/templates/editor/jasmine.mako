<%inherit file="/common_jasmine.mako"/>

<%block name="specs">
  <script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="/static/ext/js/bootstrap.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="static/js/workflow.js" type="text/javascript" charset="utf-8"></script>
  <script src="static/jasmine/workflow.js" type="text/javascript" charset="utf-8"></script>
</%block>

<%block name="fixtures">
  <div style="display:none">
    <h1>Buongiorno, world!</h1>
    <div id="graph"></div>
  </div>
</%block>