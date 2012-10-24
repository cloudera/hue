<%namespace name="listDesigns" file="list_designs.mako" />
<%inherit file="common_jasmine.mako"/>

<%block name="specs">
    <script src="/static/ext/js/moment.min.js"></script>
    <script src="static/js/jobsub.ko.js"></script>
    <script src="static/jasmine/jobsubSpec.js"></script>
</%block>


<%block name="fixtures">
  <div style="display:none">
    ${listDesigns.layout()}
  </div>
</%block>