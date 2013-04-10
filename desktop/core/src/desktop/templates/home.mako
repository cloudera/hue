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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

${ commonheader(_('Home'), "home", user) | n,unicode }


<style type="text/css">
  .widget-box {
    background: none repeat scroll 0 0 #F9F9F9;
    border-top: 1px solid #CDCDCD;
    border-left: 1px solid #CDCDCD;
    border-right: 1px solid #CDCDCD;
    clear: both;
    margin-top: 10px;
    margin-bottom: 16px;
    position: relative;
  }

  .widget-title {
    background-color: #efefef;
    background-image: -webkit-gradient(linear, 0 0%, 0 100%, from(#fdfdfd), to(#eaeaea));
    background-image: -webkit-linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    background-image: -moz-linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    background-image: -ms-linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    background-image: -o-linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    background-image: -linear-gradient(top, #fdfdfd 0%, #eaeaea 100%);
    filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#fdfdfd', endColorstr='#eaeaea', GradientType=0); /* IE6-9 */
    border-bottom: 1px solid #CDCDCD;
    height: 36px;
  }

  .widget-title span.icon {
    border-right: 1px solid #cdcdcd;
    padding: 9px 10px 7px 11px;
    float: left;
    opacity: .7;
  }

  .widget-title h5 {
    color: #666666;
    text-shadow: 0 1px 0 #ffffff;
    float: left;
    font-size: 16px;
    font-weight: bold;
    padding: 10px;
    line-height: 16px;
    margin: 0;
  }

  .widget-content {
    padding-top: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #cdcdcd;
  }

  .widget-content ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .widget-content ul li {
    margin: 0;
    padding: 0;
  }

  .widget-content a {
    padding: 5px 15px;
    display: block;
    font-size: 14px;
    font-weight: bold;
  }

  .widget-content a i {
    color: #999999;
  }

  .widget-content a:hover {
    background-color: #EEEEEE;
    text-decoration: none;
  }

  .widget-content a:hover i {
    color: #333333;
  }

</style>

<%def name="app_link(current_app, label, extra_path = '')">
  %for app in apps:
    %if app == current_app:
      <li><a href="/${app}${extra_path}"><i class="icon-double-angle-right"></i> ${label}</a></li>
    %endif
  %endfor
</%def>


<div class="container-fluid">
  <h1>${_('Welcome Home.')}</h1>

  <div class="row-fluid">
    <div class="span12">
      <p>
        ${ _('Hue is a Web UI for Apache Hadoop. Please select an application below.') }
      </p>
    </div>
  </div>

  <div class="row-fluid" style="margin-top: 30px">

    <div class="span4">
      <div class="widget-box">
        <div class="widget-title">
          <span class="icon">
            <i class="icon-th-list"></i>
          </span>
          <h5>${_('Query')}</h5>
        </div>
        <div class="widget-content">
          <ul>
            ${ app_link("beeswax", _('Hive')) }
            ${ app_link("impala", _('Impala')) }
            ${ app_link("pig", _('Pig')) }
            ${ app_link("shell", _('Shell')) }
          </ul>
        </div>
      </div>
    </div>

    <div class="span4">
      <div class="widget-box">
        <div class="widget-title">
          <span class="icon">
            <i class="icon-th-list"></i>
          </span>
          <h5>${_('Hadoop')}</h5>
        </div>
        <div class="widget-content">
          <ul>
            ${ app_link("filebrowser", _('Files')) }
            ${ app_link("jobbrowser", _('Jobs')) }
            ${ app_link("catalog", _('Tables')) }
            ${ app_link("jobsub", _('Designs')) }
          </ul>
        </div>
      </div>
    </div>

    <div class="span4">
      <div class="widget-box">
        <div class="widget-title">
          <span class="icon">
            <i class="icon-th-list"></i>
          </span>
          <h5>${_('Workflow')}</h5>
        </div>
        <div class="widget-content">
          <ul>
            ${ app_link("oozie", _('Dashboard')) }
            ${ app_link("oozie", _('Editor'), "/list_workflows/") }
          </ul>
        </div>
      </div>
    </div>
  </div>

</div>

${ commonfooter(messages) | n,unicode }