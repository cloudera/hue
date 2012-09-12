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

${ commonheader(_('Search'), "search", "100px") }


##<div class="subnav subnav-fixed">
##  <div class="container-fluid">
##    <ul class="nav nav-pills">
##	  <li><a href="">${_('Configuration')}</a></li>
##    </ul>
##  </div>
##</div>

<div class="container-fluid">
  <h1>Search</h1>
  <div class="row-fluid">    
    <div class="span2"></div>
    <div class="span8">
      <form class="form-search">
         ${ search_form }
       <button class="btn" type="submit">Search</button>
      </form>
    </div>
    <div class="span2">(query example: solr)</div>
  </div>
</div>

% if response:
<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2"></div>
    <div class="span8">
      % for result in response['response']['docs']:
        <div class="row-fluid">
          <div class="span2">${ result.get('id', '') }</div>
          <div class="span6">${ result.get('name', '') }</div>
        </div>
      % endfor
    </div>
    <div class="span2"></div>
  </div>
  
  <div class="row-fluid">
    <div class="span2"></div>
    <div class="span8">  
      Result founds: ${ response['response']['numFound'] }
     </div>
    <div class="span2"></div>
  </div> 
  
  <div class="row-fluid"> 
      ${ response }
  </div>  
</div>
% endif

${ commonfooter(messages) }
