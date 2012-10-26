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

<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user) }

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            <div class="well" style="padding: 8px 0;">
            <ul class="nav nav-list">
                % if response and response['facet_counts']:
                    % if response['facet_counts']['facet_fields']:
                        <h4>Fields</h4>
                        % for cat in response['facet_counts']['facet_fields']:
                            % if response['facet_counts']['facet_fields'][cat]:
                            <li class="nav-header">${cat}</li>
                            % for subcat, count in macros.pairwise(response['facet_counts']['facet_fields'][cat]):
                                <li><a href="?query=${ solr_query['q'] }&fq=${ cat }:${ subcat }">${ subcat } (${ count })</a></li>
                            % endfor
                            % endif
                        % endfor
                    %endif

                    % if response['facet_counts']['facet_queries']:
                        ## Not used in demo
                        <h4>Queries</h4>
                        % for cat in response['facet_counts']['facet_queries']:
                            % if response['facet_counts']['facet_queries'][cat]:
                                <li><a href="#">${cat} (${response['facet_counts']['facet_queries'][cat]})</a></li>
                            % endif
                        % endfor
                    %endif

                    % if response['facet_counts']['facet_ranges']:
                        <h4>Ranges</h4>
                        % for cat in response['facet_counts']['facet_ranges']:
                            % if response['facet_counts']['facet_ranges'][cat]:
                            <li class="nav-header">${cat}</li>
                            % for range, count in macros.pairwise(response['facet_counts']['facet_ranges'][cat]['counts']):
                                <li><a href="?query=${ solr_query['q'] }&fq=${ cat }:${ range }">${ range } (${ count })</a></li>
                            % endfor
                            % endif
                        % endfor
                    %endif

                    % if response['facet_counts']['facet_dates']:
                        <h4>Dates</h4>
                        % for cat in response['facet_counts']['facet_dates']:
                            % if response['facet_counts']['facet_dates'][cat]:
                            <li class="nav-header">${cat}</li>
                            % for date, count in response['facet_counts']['facet_dates'][cat].iteritems():
                              % if date not in ('start', 'end', 'gap'):
                                <li><a href="?query=${ solr_query['q'] }&fq=${ cat }:${ date }">${ date } (${ count })</a></li>
                              % endif
                            % endfor
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
                    ${ macros.tweet_result(result) }
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

<div class="hide">
    ${ rr }
</div>

${ commonfooter(messages) }
