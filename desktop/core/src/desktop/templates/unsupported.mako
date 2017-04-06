## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.    See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##       http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
  from django.utils.translation import ugettext as _
%>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>${_('Hue - Unsupported browser')}</title>

  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="">
  <meta name="author" content="">

  <style type="text/css">
    body {
      padding-top: 80px;
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 13px;
      line-height: 20px;
      color: #444444;
      text-align: center;
    }

    #logo {
      display: block;
      margin-left: auto;
      margin-right: auto;
      margin-bottom: 10px;
      background: #FFF url("${ static('desktop/art/hue-login-logo-ellie.png') }") 50% 14px no-repeat;
      width: 130px;
      height: 130px;
    }

    .header {
      background-color: #0B7FAD;
      position: fixed;
      top: 0;
      width: 100%;
      text-align: left;
      padding: 4px;
    }

    .footer {
      position: fixed;
      bottom: 0;
      background-color: #0B7FAD;
      color: #FFF;
      font-size: 10px;
      width: 100%;
      text-align: center;
      height: 6px;
    }

    a {
      color: #0B7FAD;
      text-decoration: none;
      font-weight: bold;
    }

    a:hover {
      text-decoration: underline;
    }
  </style>
</head>

<body>
<div class="header">
  <img src="${ static('desktop/art/hue-logo-mini-white.png') }" alt="${ _('Hue logo') }"/>
</div>

<div class="footer"></div>

<div id="logo"></div>

<h3>${_('It looks like you are running an older browser. What about upgrading to the latest')}</h3>

<a href="http://www.google.com/chrome/">Google Chrome</a> |
<a href="http://www.mozilla.org/firefox/">Mozilla Firefox</a> |
<a href="http://windows.microsoft.com/en-us/internet-explorer/browser-ie">Microsoft Internet Explorer</a>

</body>
</html>
