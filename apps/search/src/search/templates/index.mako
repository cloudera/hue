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
from itertools import izip
%>



<%
def pairwise(iterable):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)
%>

${ commonheader(_('Search'), "search", user) }


##<div class="subnav subnav-fixed">
##  <div class="container-fluid">
##    <ul class="nav nav-pills">
##	  <li><a href="">${_('Configuration')}</a></li>
##    </ul>
##  </div>
##</div>

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            <div class="well" style="padding: 8px 0;">
            <ul class="nav nav-list">
                % if response and response['facet_counts']:
                    % if response['facet_counts']['facet_fields']:
                        <h4>Field Facets</h4>
                        % for cat in response['facet_counts']['facet_fields']:
                            % if response['facet_counts']['facet_fields'][cat]:
                            <li class="nav-header">${cat}</li>
                            % for subcat, count in pairwise(response['facet_counts']['facet_fields'][cat]):
                                <li><a href="#">${subcat} (${count})</a></li>
                            % endfor
                            % endif
                        % endfor
                    %endif
                    % if response['facet_counts']['facet_queries']:
                        <h4>Query Facets</h4>
                        % for cat in response['facet_counts']['facet_queries']:
                            % if response['facet_counts']['facet_queries'][cat]:
                                <li><a href="#">${cat} (${response['facet_counts']['facet_queries'][cat]})</a></li>
                            % endif
                        % endfor
                    %endif
                %endif
            </ul>
            </div>
        </div>
        <div class="span9">
            <form class="form-search well">
                ${ search_form }
                <button class="btn" type="submit">Search</button>
            </form>

            % if response:
                <table class="table table-striped table-hover" style="table-layout: fixed;">
                <tbody>
                % for result in response['response']['docs']:
                <tr>
                    <td style="word-wrap: break-word;">
                        <a rel="nofollow" href="#"><b>${ result.get('name', '') }</b></a>
                        <p>Price: ${ result.get('price_c', '') }</p>
                        <p>
                        % if result.get('features'):
                            <ul>
                            % for feature in result.get('features', ''):
                                <li>${ feature }</li>
                            % endfor
                            </ul>
                        % endif
                        </p>
                        <div style="color: #46a546;">
                            Id: ${ result.get('id', '') }
                        </div>
                    </td>
                </tr>
                % endfor
                </tbody>
                </table>
                <div class="row-fluid">
                    Result founds: ${ response['response']['numFound'] }
                </div>
            % endif
        </div>
    </div>

</div>

${ commonfooter(messages) }
