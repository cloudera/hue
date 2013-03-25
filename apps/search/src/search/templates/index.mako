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

${ commonheader(_('Search'), "search", user, "40px") | n,unicode }

<div class="search-bar">
  % if user.is_superuser:
    <div class="pull-right" style="margin-top: 4px">
      <a class="change-settings btn" href="#"><i class="icon-edit"></i> ${ _('Customize result display') }</a>
    </div>
  % endif
  <form class="form-search" style="margin: 0">
    <div class="dropdown" style="display: inline">
      Search in <a href="#" data-toggle="dropdown"><strong class="current-core"></strong> <i class="icon-caret-down"></i></a>
      <ul class="dropdown-menu">
        % if user.is_superuser:
          % for core in hue_cores:
            <li><a class="dropdown-core" href="#" data-value="${ core.name }" data-settings-url="${ core.get_absolute_url() }">${ core.label }</a></li>
          % endfor
        % else:
          % for core in hue_cores:
            <li><a class="dropdown-core" href="#" data-value="${ core.name }">${ core.label }</a></li>
          % endfor
        % endif
      </ul>
    </div>
    <div class="input-append">
      ${ search_form | n,unicode }
      <button type="submit" class="btn">${ _('Go') }</button>
    </div>
  </form>
</div>

<div class="container-fluid">
  <div class="row-fluid">
    % if error:
    <div class="span12">
      <div class="alert">
        ${ error['message'] }
      </div>
    </div>
    %else:
    % if response and response['response']['docs'] and len(response['response']['docs']) > 0 and solr_query['facets'] == 1 and response.get('facet_counts'):
    <div class="span2">
      <ul class="facet-list">
        % if response and response.get('facet_counts'):
          % if response['facet_counts']['facet_fields']:
            % for cat in response['facet_counts']['facet_fields']:
                % if response['facet_counts']['facet_fields'][cat]:
                  <%
                    found_value = ""
                    for fq in solr_query['fq'].split('|'):
                      if fq and fq.split(':')[0] == cat:
                        found_value = fq.split(':')[1]
                        remove_list = solr_query['fq'].split('|')
                        remove_list.remove(fq)
                  %>
                <li class="nav-header">${cat}</li>
                % for subcat, count in macros.pairwise(response['facet_counts']['facet_fields'][cat]):
                  %if count > 0 and subcat != "" and found_value == "":
                    <li><a href="?query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ cat }:${ subcat }&sort=${solr_query["sort"]}">${subcat}</a> <span class="counter">(${ count })</span></li>
                  %endif
                  % if found_value != "":
                    <li><strong>${ found_value }</strong> <a href="?query=${ solr_query['q'] }&fq=${'|'.join(remove_list)}&sort=${solr_query["sort"]}"><i class="icon-remove"></i></a></li>
                  % endif
                % endfor
                % endif
            % endfor
          %endif

          % if response['facet_counts']['facet_ranges']:
            % for cat in response['facet_counts']['facet_ranges']:
                % if response['facet_counts']['facet_ranges'][cat]:
                  <%
                    found_value = ""
                    for fq in solr_query['fq'].split('|'):
                      if fq and fq.split(':')[0] == cat:
                        found_value = fq.split(':')[1]
                        remove_list = solr_query['fq'].split('|')
                        remove_list.remove(fq)
                  %>
                <li class="nav-header">${cat}</li>
                % for range, count in macros.pairwise(response['facet_counts']['facet_ranges'][cat]['counts']):
                 % if count > 0 and found_value == "":
                   <li><a href="?query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ cat }:${ range }&sort=${solr_query["sort"]}">${ range } (${ count })</a></li>
                  %endif
                  % if found_value != "":
                      <li><strong>${ found_value }</strong> <a href="?query=${ solr_query['q'] }&fq=${'|'.join(remove_list)}&sort=${solr_query["sort"]}"><i class="icon-remove"></i></a></li>
                  % endif
                % endfor
              % endif
            % endfor
          % endif

          % if response['facet_counts']['facet_dates']:
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
    % endif
    % if response and response['response']['docs'] and len(response['response']['docs']) > 0:
      %if response.get('facet_counts'):
      <div class="span10">
      %else:
      <div class="span12">
      %endif
      <ul class="breadcrumb">
        <li class="pull-right">
          <select class="sort-by">
            <option value="">${ _('Sort by') }</option>
          </select>
        </li>
        <li class="active">
        <%
          end_record = int(solr_query["start"])+int(solr_query["rows"])
          if end_record > int(response['response']['numFound']):
            end_record = response['response']['numFound'];
        %>
        ${_('Showing %s - %s of %s results') % (int(solr_query["start"])+1, end_record, response['response']['numFound'])}
        </li>
      </ul>

      <script src="/static/ext/js/mustache.js"></script>

      <div id="result-container"></div>

      <textarea id="mustacheTmpl" class="hide">${ hue_core.result.get_template(with_highlighting=True) | n,unicode }</textarea>
      <script>
      <%
        docs = response['response']['docs']
        for doc in response['response']['docs']:
          if doc['id'] in response.get('highlighting', []):
            doc.update(response['highlighting'][doc['id']])
        %>
        $.each(${ json.dumps([result for result in docs]) | n,unicode }, function (index, item) {
          $("<div>").addClass("result-row").html(
            Mustache.render($("#mustacheTmpl").text(), item)
          ).appendTo($("#result-container"));
        });
      </script>

      <div class="pagination">
        <ul>
          <%
            beginning = 0
            previous = int(solr_query["start"]) - int(solr_query["rows"])
            next = int(solr_query["start"]) + int(solr_query["rows"])
          %>
          % if int(solr_query["start"]) > 0:
            <li>
              <a title="${_('Beginning of List')}" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=${solr_query["sort"]}&rows=${solr_query["rows"]}&start=${beginning}">&larr; ${_('Beginning of List')}</a>
            </li>
            <li>
              <a title="Previous Page" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=${solr_query["sort"]}&rows=${solr_query["rows"]}&start=${previous}">${_('Previous Page')}</a>
            </li>
          % endif
          % if end_record < int(response["response"]["numFound"]):
            <li>
              <a title="Next page" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=${solr_query["sort"]}&rows=${solr_query["rows"]}&start=${next}">${_('Next Page')}</a>
            </li>
          % endif
        </ul>
      </div>
    </div>
    % else:
    <div class="span12">
      <div class="alert">
        ${_('Your search - %s - did not match any documents.') % (solr_query["q"])}
      </div>
    </div>
    % endif
  </div>
  % endif
</div>

<div class="hide">
  ${ rr | n,unicode }
</div>


<link rel="stylesheet" href="/search/static/css/search.css">

<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>

<script>
  $(document).ready(function () {
    $(".current-core").text($("select[name='cores'] option:selected").text());
    % if user.is_superuser:
        $(".dropdown-core").each(function () {
          if ($(this).data("value") == $("select[name='cores']").val()) {
            $(".change-settings").attr("href", $(this).data("settings-url"));
          }
        });
    % endif

    $(".dropdown-core").click(function (e) {
      e.preventDefault();
      $(".current-core").text($(this).text());
      $("select[name='cores']").val($(this).data("value"));
      % if user.is_superuser:
          $(".change-settings").attr("href", $(this).data("settings-url"));
      % endif
      $("form").submit();
    });

    $("#recordsPerPage").change(function () {
      $("input[name='rows']").val($(this).val());
      $("input[name='rows']").closest("form").submit();
    });
    $("#recordsPerPage").val($("input[name='rows']").val());

    var sortingData = ${ hue_core.sorting.data | n,unicode };
    if (sortingData && sortingData.fields && sortingData.fields.length > 0) {
      $.each(sortingData.fields, function (index, item) {
        $("<option>").attr("value", item.label).text(item.label).data("field", item.field).data("asc", item.asc).appendTo($(".sort-by"));
      });
      var activeSorting = "${solr_query["sort"]}";
      if (activeSorting != "" && activeSorting.indexOf(" ") > -1) {
        $.each(sortingData.fields, function (index, item) {
          if (item.field == activeSorting.split(" ")[0] && item.asc == (activeSorting.split(" ")[1] == "asc")) {
            $(".sort-by").val(item.label);
          }
        });
      }
    }
    else {
      $(".sort-by").hide();
    }

    $(".sort-by").change(function () {
      var _sort = $(".sort-by option:selected").data("field") + "+" + ($(".sort-by option:selected").data("asc") ? "asc" : "desc");
      if ($(".sort-by").val() == "") {
        _sort = "";
      }
      location.href = "?query=${solr_query["q"]}&fq=${solr_query["fq"]}&sort=" + _sort + "&rows=${solr_query["rows"]}&start=${solr_query["start"]}";
    });

    $("#id_query").keydown(function() {
      var query = $("#id_query").val();
      $.ajax("${ url('search:query_suggest', core=hue_core.name) }" + query, {
        type: 'GET',
        success: function (data) {
          if (data.message.spellcheck && ! jQuery.isEmptyObject(data.message.spellcheck.suggestions)) {
            $('#id_query').typeahead({source: data.message.spellcheck.suggestions[1].suggestion});
          }
        }
      });

    });

  });
</script>

${ commonfooter(messages) | n,unicode }
