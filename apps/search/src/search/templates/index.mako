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

<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user) | n,unicode }


<div class="container-fluid">

  <div class="row-fluid">
    <div class="span12">
      <form class="form-search well">
        <i class="twitter-logo"></i>
        ${ search_form | n,unicode }
        <button class="btn" type="submit">${_('Search')}</button>
        % if response:
        <div class="btn-group pull-right">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
            ${_('Sort by')}
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            <li><a href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=created_at+desc&rows=${solr_query["rows"]}&start=${solr_query["start"]}">${_('Date')}</a></li>
            <li><a href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=retweet_count+desc&rows=${solr_query["rows"]}&start=${solr_query["start"]}">${_('Retweets count')}</a></li>
            <li class="divider"></li>
            <li><a href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&rows=${solr_query["rows"]}&start=${solr_query["start"]}">${_('Reset sorting')}</a></li>
          </ul>
          % endif
          % if user.is_superuser:
            <a class="btn" href="${ url('search:admin') }">${ _('Admin') }</a>
          % endif
        </div>
      </form>
    </div>
  </div>

  % if response and solr_query['facets'] == 1:
  <div class="row-fluid">
    <div class="span3">
      <div class="well" style="padding: 8px 0;">
      <ul class="nav nav-list">
        % if solr_query['fq']:
          <li class="nav-header">${_('Current filter')}</li>
          % for fq in solr_query['fq'].split('|'):
            % if fq:
              <%
                removeList = solr_query['fq'].split('|')
                removeList.remove(fq)
              %>
              <li><a href="?query=${ solr_query['q'] }&fq=${'|'.join(removeList)}&sort=${solr_query["sort"]}">${fq} <i class="icon-trash"></i></a></li>
            % endif
          % endfor
          <li style="margin-bottom: 20px"></li>
        % endif

        % if response and response['facet_counts']:
          % if response['facet_counts']['facet_fields']:
            <h4>${_('Fields')}</h4>
            % for cat in response['facet_counts']['facet_fields']:
                % if response['facet_counts']['facet_fields'][cat]:
                <li class="nav-header">${cat}</li>
                % for subcat, count in macros.pairwise(response['facet_counts']['facet_fields'][cat]):
                  %if count > 0 and subcat != "":
                    <li><a href="?query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ cat }:${ subcat }&sort=${solr_query["sort"]}">${subcat} (${ count })</a></li>
                  %endif
                % endfor
                % endif
            % endfor
          %endif

          % if response['facet_counts']['facet_ranges']:
            <h4>${_('Ranges')}</h4>
            % for cat in response['facet_counts']['facet_ranges']:
                % if response['facet_counts']['facet_ranges'][cat]:
                <li class="nav-header">${cat}</li>
                % for range, count in macros.pairwise(response['facet_counts']['facet_ranges'][cat]['counts']):
                 % if count > 0:
                   <li><a href="?query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ cat }:${ range }&sort=${solr_query["sort"]}">${ range } (${ count })</a></li>
                  %endif
                % endfor
              % endif
            % endfor
          % endif

          % if response['facet_counts']['facet_dates']:
            <h4>${_('Dates')}</h4>
            % for cat in response['facet_counts']['facet_dates']:
                % if response['facet_counts']['facet_dates'][cat]:
                <li class="nav-header">${cat}</li>
                % for date, count in response['facet_counts']['facet_dates'][cat].iteritems():
                  % if date not in ('start', 'end', 'gap') and count > 0:
                    <li><a href="?query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ cat }:${ date }&sort=${solr_query["sort"]}">${ date } (${ count })</a></li>
                  % endif
                % endfor
                % endif
            % endfor
          %endif
         %endif
      </ul>
      </div>
    </div>
    % endif

    <div class="span9">
    % if response:
      <table class="table table-striped table-hover" style="table-layout: fixed;">
        <tbody>
          % for result in response['response']['docs']:
            ${ hue_core.result.render_result(result) | n,unicode }
          % endfor
        </tbody>
      </table>

      <div class="pagination">
        <ul class="pull-right">
          <%
            beginning = 0
            previous = int(solr_query["start"]) - int(solr_query["rows"])
            next = int(solr_query["start"]) + int(solr_query["rows"])
          %>
          % if int(solr_query["start"]) > 0:
            <li><a title="${_('Beginning of List')}" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=${solr_query["sort"]}&rows=${solr_query["rows"]}&start=${beginning}">&larr; ${_('Beginning of List')}</a></li>
            <li><a title="Previous Page" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=${solr_query["sort"]}&rows=${solr_query["rows"]}&start=${previous}">${_('Previous Page')}</a></li>
          % endif
          <li><a title="Next page" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=${solr_query["sort"]}&rows=${solr_query["rows"]}&start=${next}">${_('Next Page')}</a></li>
        </ul>
        <p>
          ${_('Showing %s to %s of %s tweets') % (int(solr_query["start"])+1, int(solr_query["start"])+int(solr_query["rows"]), response['response']['numFound'])}
          ##${_('Show')}
          ##<select id="recordsPerPage" class="input-mini"><option value="15">15</option><option value="30">30</option><option value="45">45</option><option value="60">60</option><option value="100">100</option></select>
          ##${_('tweets per page.')}
        </p>
      </div>
    % endif
    </div>
  </div>
</div>

<div class="hide">
  ${ rr | n,unicode }
</div>

<link rel="stylesheet" href="/search/static/css/search.css">

<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>

<script>
  $(document).ready(function(){
    $("a[data-dt]").each(function(){
      $(this).text(moment($(this).data("dt")).add("hours", 8).fromNow());
    });
    $(".text").click(function(e){
      if ($(e.target).is("div")){
        window.open($(this).data("link"))
      }
      if ($(e.target).is("a")){
        e.stopImmediatePropagation();
        e.stopPropagation();
      }
    });
    $("[rel='tooltip']").tooltip();
    $("[rel='popover']").popover();
    $("#recordsPerPage").change(function(){
      $("input[name='rows']").val($(this).val());
      $("input[name='rows']").closest("form").submit();
    });
    $("#recordsPerPage").val($("input[name='rows']").val());
  });
</script>

${ commonfooter(messages) | n,unicode }
