<%namespace name="listDesigns" file="designs.mako" />
<%inherit file="common_jasmine.mako"/>

<%block name="specs">
    <script src="/static/ext/js/mustache.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
    <script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
    <script src="/oozie/static/js/workflow.models.js" type="text/javascript" charset="utf-8"></script>
    <script src="/oozie/static/js/workflow.node-fields.js" type="text/javascript" charset="utf-8"></script>
    <script src="/jobsub/static/js/jobsub.templates.js" type="text/javascript" charset="utf-8"></script>
    <script src="/jobsub/static/js/jobsub.ko.js" type="text/javascript" charset="utf-8"></script>
    <script src="/jobsub/static/js/jobsub.js" type="text/javascript" charset="utf-8"></script>
    <script src="static/jasmine/jobsubSpec.js"></script>
</%block>


<%block name="fixtures">
  <div style="display:none">
  </div>
</%block>