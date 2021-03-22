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
  import sys

  from desktop import conf

  if sys.version_info[0] > 2:
    from django.utils.translation import gettext as _
  else:
    from django.utils.translation import ugettext as _
%>

<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta charset="utf-8">
  <title>Hue</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  % if conf.CUSTOM.LOGO_SVG.get():
    <link rel="icon" type="image/x-icon" href="${ static('desktop/art/custom-branding/favicon.ico') }"/>
  % else:
    <link rel="icon" type="image/x-icon" href="${ static('desktop/art/favicon.ico') }"/>
  % endif

  % if conf.ENABLE_GIST_PREVIEW.get():
    % if image_link:
      <meta name="twitter:image" content="${ static(image_link) }">
    % endif
    <meta name="twitter:card" content="summary">
    <meta property="og:site_name" content="Hue" />
    <meta property="og:title" content="${ title }" />
    <meta property="og:description" content="${ description }"/>
  % endif
</head>

<body>
</body>

</html>
