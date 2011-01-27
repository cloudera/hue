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
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
  <head>
    <title>Forms with Dependencies</title>
  </head>
  <body>
    <p>
     The form below conditionally uses different inputs given the state of the select input. If you choose alpha, the "A" section is used.
     This is using the <i>DependencyAwareForm</i> Django form in the view. There's no UI component here; this test is verifying that Django form extension.
    </p>
    <form action="${url("jframegallery.views.forms_with_dependencies")}" method="post" class="dependency_form jframe_padded {'deps':${form.render_dep_metadata()|n}}">
      % if len(form.non_field_errors()):
        ${unicode(form.non_field_errors()) | n}
      % endif
      % for field in form:
        <dt>${field.label_tag() | n}</dt>
        <dd>${unicode(field) | n}
          % if len(field.errors):
            ${unicode(field.errors) | n}
          % endif
        </dd>
      % endfor
    <input type="submit">
    </form>

    <div class="jframe_padded">
      % if data:
        Succesful submission: ${data}
      % else:
        No submission.
      % endif
    </div>
  </body>
</html>
