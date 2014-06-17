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


<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Hadoop Security'), "security", user) | n,unicode }
${ layout.menubar(section='hive') }


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav">
        <ul class="nav nav-list">
          <li class="nav-header">${ _('Properties') }</li>
          <li class="active"><a href="#properties"><i class="fa fa-eye"></i> ${ _('View') }</a></li>
          <li><a href="#listDataset"><i class="fa fa-group"></i> ${ _('Groups') }</a></li>
          <li><a href="#listDataset"><i class="fa fa-cubes"></i> ${ _('Roles') }</a></li>
        </ul>
      </div>
    </div>
    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${ _('View') }</h1>
        <div class="card-body">
          Assist: 
          ${ assist }        
        <div>
        <div class="card-body">     
          Hadoop Groups: 
          ${ hadoop_groups }
        <div>            
        <div class="card-body">     
          Roles: 
          ${ roles }
        <div>      
        <div class="form-actions" id="bottom-nav">
          <a id="backBtn" class="btn disabled">${ _('Back') }</a>
          <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>
        </div>

        </div>

        <div id="listDataset" class="section hide">
          <div class="alert alert-info"><h3>${ _('Existing datasets') }</h3></div>
        </div>

        <div id="listHistory" class="section hide">
          <div class="alert alert-info"><h3>${ _('History') }</h3></div>          
        </div>

      </form>

    </div>
    </div>

  </div>

</div>



${ commonfooter(messages) | n,unicode }
