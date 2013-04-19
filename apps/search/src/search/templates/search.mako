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
import urllib
%>

<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user, "40px") | n,unicode }

<link rel="stylesheet" href="/search/static/css/search.css">
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>

<div class="search-bar">
  % if user.is_superuser:
    <div class="pull-right" style="margin-top: 4px">
      <a class="change-settings" href="#"><i class="icon-edit"></i> ${ _('Customize result display') }</a>
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
      <div class="icon-search" style="position: absolute;top: 7px;left: 11px;background-image: url('http://twitter.github.com/bootstrap/assets/img/glyphicons-halflings.png');"></div>
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
    % if response and response['response']['docs'] and len(response['response']['docs']) > 0 and response['normalized_facets']:
    <div class="span2">
      <ul class="facet-list">
        % for fld in response['normalized_facets']:
        % if fld['type'] == 'date':
            <li class="nav-header dateFacetHeader">${fld['label']}</li>
        % else:
            <li class="nav-header">${fld['label']}</li>
        % endif

        <%
          found_value = ""
          for fq in solr_query['fq'].split('|'):
            if fq and fq.split(':')[0] == fld['field']:
              found_value = fq[fq.find(":")+1:]
              remove_list = solr_query['fq'].split('|')
              remove_list.remove(fq)
        %>
          % for group, count in macros.pairwise(fld['counts']):
            %if count > 0 and group != "" and found_value == "":
              % if fld['type'] == 'field':
                <li><a href='?collection=${ current_core }&query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ fld['field'] }:"${ urllib.quote_plus(group.encode('ascii', 'xmlcharrefreplace')) }"${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'>${group}</a> <span class="counter">(${ count })</span></li>
              % endif
              % if fld['type'] == 'range':
                <li><a href='?collection=${ current_core }&query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ fld['field'] }:["${ group }" TO "${ str(int(group) + int(fld['gap']) - 1) }"]${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'>${ group } (${ count })</a></li>
              % endif
              % if fld['type'] == 'date':
                <li class="dateFacetItem"><a href='?collection=${ current_core }&query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ fld['field'] }:"${ group }"${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'><span class="dateFacet">${ group }</span> (${ count })</a></li>
              % endif
            %endif
            % if found_value != "":
              % if fld['type'] == 'field' and '"' + group + '"' == found_value:
                <li><strong>${ group }</strong> <a href="?collection=${ current_core }&query=${ solr_query['q'] }&fq=${'|'.join(remove_list)}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="icon-remove"></i></a></li>
              %endif
              % if fld['type'] == 'range' and '["' + group + '" TO "' + str(int(group) + int(fld['gap']) - 1) + '"]' == found_value:
                <li><strong>${ group }</strong> <a href="?collection=${ current_core }&query=${ solr_query['q'] }&fq=${'|'.join(remove_list)}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="icon-remove"></i></a></li>
              %endif
              % if fld['type'] == 'date' and '"' + group + '"' == found_value:
                <li><strong><span class="dateFacet">${group}</span></strong> <a href="?collection=${ current_core }&query=${ solr_query['q'] }&fq=${'|'.join(remove_list)}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="icon-remove"></i></a></li>
              %endif
            %endif
          % endfor
        % endfor
      </ul>
    </div>
    % endif
    % if response and response['response']['docs'] and len(response['response']['docs']) > 0:
      %if response['normalized_facets']:
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

        function genericFormatDate(val, item, format){
          var d = moment(Mustache.render(val, item));
          if (d.isValid()) {
            return d.format(format);
          }
          else {
            return Mustache.render(val, item);
          }
        }

        $.each(${ json.dumps([result for result in docs]) | n,unicode }, function (index, item) {
          item.viewfile = function () {
            return function (val) {
              return '<a href="/filebrowser/view/' + $.trim(Mustache.render(val, item)) + '">' + $.trim(Mustache.render(val, item)) + '</a>';
            }
          };
          item.downloadfile = function () {
            return function (val) {
              return '<a href="/filebrowser/download/' + $.trim(Mustache.render(val, item)) + '?disposition=inline">' + $.trim(Mustache.render(val, item)) + '</a>';
            }
          };
          item.date = function () {
            return function (val) {
              return genericFormatDate(val, item, "DD-MM-YYYY");
            }
          };
          item.time = function () {
            return function (val) {
              return genericFormatDate(val, item, "HH:mm:ss");
            }
          };
          item.datetime = function () {
            return function (val) {
              return genericFormatDate(val, item, "DD-MM-YYYY HH:mm:ss");
            }
          };
          item.fulldate = function () {
            return function (val) {
              return genericFormatDate(val, item, null);
            }
          };
          item.timestamp = function () {
            return function (val) {
              var d = moment(Mustache.render(val, item));
              if (d.isValid()) {
                return d.valueOf();
              }
              else {
                return Mustache.render(val, item);
              }
            }
          };
          item.fromnow = function () {
            return function (val) {
              var d = moment(Mustache.render(val, item));
              if (d.isValid()) {
                return d.fromNow();
              }
              else {
                return Mustache.render(val, item);
              }
            }
          };
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
              <a title="${_('Beginning of List')}" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}&rows=${solr_query["rows"]}&start=${beginning}">&larr; ${_('Beginning of List')}</a>
            </li>
            <li>
              <a title="Previous Page" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}&rows=${solr_query["rows"]}&start=${previous}">${_('Previous Page')}</a>
            </li>
          % endif
          % if end_record < int(response["response"]["numFound"]):
            <li>
              <a title="Next page" href="?query=${solr_query["q"]}&fq=${solr_query["fq"]}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}&rows=${solr_query["rows"]}&start=${next}">${_('Next Page')}</a>
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


${ hue_core.result.get_extracode() | n,unicode }

<script>
  $(document).ready(function () {
    $(".dateFacet").each(function () {
      var _m = moment($(this).text());
      $(this).text(_m.fromNow());
      $(this).parents(".dateFacetItem").data("epoch", _m.valueOf());
    });

    var orderedDateFacets = $(".dateFacetItem");
    orderedDateFacets.sort(function (a, b) {
      a = $(a).data("epoch");
      b = $(b).data("epoch");
      if (a > b) {
        return -1;
      } else if (a < b) {
        return 1;
      } else {
        return 0;
      }
    });
    $(".dateFacetHeader").after(orderedDateFacets);

    $(".current-core").text($("select[name='collection'] option:selected").text());
    % if user.is_superuser:
        $(".dropdown-core").each(function () {
          if ($(this).data("value") == $("select[name='collection']").val()) {
            $(".change-settings").attr("href", $(this).data("settings-url"));
          }
        });
    % endif

    $(".dropdown-core").click(function (e) {
      e.preventDefault();
      $(".current-core").text($(this).text());
      $("select[name='collection']").val($(this).data("value"));
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
      var activeSorting = "${solr_query.get("sort", "")}";
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
      location.href = "?query=${solr_query["q"]}&fq=${solr_query["fq"]}&rows=${solr_query["rows"]}&start=${solr_query["start"]}" + (_sort != "" ? "&sort=" + _sort : "");
    });

    $("#id_query").on("click", function (e) {
      if (e.pageX - $(this).position().left >= $(this).width()) {
        $(this).val("");
        $("#id_query").removeClass("deletable");
      }
    });

    $("#id_query").on("mousemove", function (e) {
      if (e.pageX - $(this).position().left >= $(this).width() && $(this).hasClass("deletable")) {
        $(this).css("cursor", "pointer");
      }
      else {
        $(this).css("cursor", "auto");
      }
    });

    if ($("#id_query").val().trim() != "") {
      $("#id_query").addClass("deletable");
    }

    $("#id_query").on("keyup", function() {
      var query = $("#id_query").val();
      if ($.trim(query) != "") {
        $("#id_query").addClass("deletable");
        $.ajax("${ url('search:query_suggest', core=hue_core.name) }" + query, {
          type: 'GET',
          success: function (data) {
            if (data.message.spellcheck && ! jQuery.isEmptyObject(data.message.spellcheck.suggestions)) {
              $('#id_query').typeahead({source: data.message.spellcheck.suggestions[1].suggestion});
            }
          }
        });
      }
      else {
        $("#id_query").removeClass("deletable");
      }
    });

  });
</script>

${ commonfooter(messages) | n,unicode }
