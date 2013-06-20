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
<script src="/search/static/js/search.utils.js" type="text/javascript" charset="utf-8"></script>

<%
  if "q" not in solr_query:
    solr_query["q"] = ""
  if "fq" not in solr_query:
    solr_query["fq"] = ""
  if "rows" not in solr_query:
    solr_query["rows"] = ""
  if "start" not in solr_query:
    solr_query["start"] = ""
%>

<div class="search-bar">
  % if user.is_superuser:
    <div class="pull-right" style="margin-top: 4px">
      <a class="change-settings" href="#"><i class="icon-edit"></i> ${ _('Customize this collection') }</a> &nbsp;&nbsp;
      <a href="${ url('search:admin_collections') }"><i class="icon-sitemap"></i> ${ _('Collection manager') }</a>
    </div>
  % endif
  <form class="form-search" style="margin: 0">
    <div class="dropdown" style="display: inline">
      Search in <a href="#" data-toggle="dropdown"><strong class="current-collection"></strong> <i class="icon-caret-down"></i></a>
      <ul class="dropdown-menu">
        % if user.is_superuser:
          % for collection in hue_collections:
            <li><a class="dropdown-collection" href="#" data-value="${ collection.id }" data-settings-url="${ collection.get_absolute_url() }">${ collection.label }</a></li>
          % endfor
        % else:
          % for collection in hue_collections:
            <li><a class="dropdown-collection" href="#" data-value="${ collection.id }">${ collection.label }</a></li>
          % endfor
        % endif
      </ul>
    </div>
    <div class="input-append">
      ${ search_form | n,unicode }
      <button type="submit" class="btn"><i class="icon-search"></i></button>
    </div>
  </form>
</div>

<div class="container results">
  <div id="loader" class="row" style="text-align: center">
    <img src="/static/art/spinner.gif" />
  </div>
  <div id="mainContent" class="row hide">
    % if error:
    <div class="span12 results">
      <div class="alert">
        ${ error['message'] }
      </div>
    </div>
    %else:
    % if response and 'response' in response and 'docs' in response['response'] and len(response['response']['docs']) > 0 and 'normalized_facets' in response:
    <div class="span2 results">
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
              found_value = fq[fq.find(":") + 1:]
              remove_list = solr_query['fq'].split('|')
              remove_list.remove(fq)
          %>
          % for group, count in macros.pairwise(fld['counts']):
            % if count > 0 and group != "" and found_value == "":
              % if fld['type'] == 'field':
                <li><a href='?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ fld['field'] }:"${ urllib.quote_plus(group.encode('ascii', 'xmlcharrefreplace')) }"${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'>${group}</a> <span class="counter">(${ count })</span></li>
              % endif
              % if fld['type'] == 'range':
                <li><a href='?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ fld['field'] }:["${ group }" TO "${ str(int(group) + int(fld['gap']) - 1) }"]${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'>${ group } - ${ str(int(group) + int(fld['gap']) - 1) }</a> <span class="counter">(${ count })</span></li>
              % endif
              % if fld['type'] == 'date':
                <li class="dateFacetItem"><a href='?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${ solr_query['fq'] }|${ fld['field'] }:[${ group } TO ${ group }${ urllib.quote_plus(fld['gap']) }]${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}'><span class="dateFacet" data-format="${fld['format']}">${ group }<span class="dateFacetGap hide">${ fld['gap'] }</span></span></a> <span class="counter">(${ count })</span></li>
              % endif
            % endif
            % if found_value != "":
              % if fld['type'] == 'field' and '"' + group + '"' == found_value:
                <li><strong>${ group }</strong> <a href="?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${'|'.join(remove_list)}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="icon-remove"></i></a></li>
              % endif
              % if fld['type'] == 'range' and '["' + group + '" TO "' + str(int(group) + int(fld['gap']) - 1) + '"]' == found_value:
                <li><strong>${ group } - ${ str(int(group) + int(fld['gap']) - 1) }</strong> <a href="?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${'|'.join(remove_list)}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="icon-remove"></i></a></li>
              % endif
              % if fld['type'] == 'date' and found_value.startswith('[' + group + ' TO'):
                <li><strong><span class="dateFacet" data-format="${fld['format']}">${ group }<span class="dateFacetGap hide">${ fld['gap'] }</span></span></strong> <a href="?collection=${ current_collection }&query=${ solr_query['q'] }&fq=${'|'.join(remove_list)}${solr_query.get("sort") and '&sort=' + solr_query.get("sort") or ''}"><i class="icon-remove"></i></a></li>
              % endif
            % endif
          % endfor
        % endfor
      </ul>
    </div>
    % endif

    % if response and 'response' in response and 'docs' in response['response'] and len(response['response']['docs']) > 0:
      % if response['normalized_facets']:
      <div class="span10 results">
      % else:
      <div class="span12 results">
      % endif
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
        ${_('Showing %s - %s of %s results') % (int(solr_query["start"]) + 1, end_record, response['response']['numFound'])}
        </li>
      </ul>

      <script src="/static/ext/js/mustache.js"></script>

      <div id="result-container"></div>

      <textarea id="mustacheTmpl" class="hide">${ hue_collection.result.get_template(with_highlighting=True) | n,unicode }</textarea>
      <script>

        <%
          docs = response['response']['docs']
          for doc in response['response']['docs']:
            # Beware, schema requires an 'id' field, silently do nothing
            if 'id' in doc and doc['id'] in response.get('highlighting', []):
              doc.update(response['highlighting'][doc['id']])
        %>

        var _mustacheTmpl = fixTemplateDotsAndFunctionNames($("#mustacheTmpl").text());
        $.each(${ json.dumps([result for result in docs]) | n,unicode }, function (index, item) {
          addTemplateFunctions(item);
          $("<div>").addClass("result-row").html(
            Mustache.render(_mustacheTmpl, item)
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

% if hue_collection:
  ${ hue_collection.result.get_extracode() | n,unicode }
% endif

<script>
  $(document).ready(function () {
    if ($(".errorlist").length > 0) {
      $(".errorlist li").each(function () {
        $.jHueNotify.error($(this).text());
      });
    }

    $("#loader").hide();
    $("#mainContent").removeClass("hide");
    window.onbeforeunload = function (e) {
      $("#loader").show();
      $("#mainContent").addClass("hide");
    };

    $(".dateFacet").each(function () {
      var _m = moment($(this).text());
      var _em = moment($(this).text());
      var _format = $(this).data("format");
      var _gap = $(this).find(".dateFacetGap").text();
      var _how = _gap.match(/\d+/)[0];
      var _what = _gap.substring(_how.length + 1).toLowerCase();
      _em.add(_what, _how * 1);

      if (_format != null && _format != "") {
        if (_format.toLowerCase().indexOf("fromnow") > -1){
          $(this).text(_m.fromNow() + " - " + _em.fromNow());
        }
        else {
          $(this).text(_m.format(_format) + " - " + _em.format(_format));
        }
      }
      else {
        $(this).text(_m.format() + " - " + _em.format());
      }
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

    % if hue_collection:
      $(".current-collection").text("${ hue_collection.label }");

      % if user.is_superuser:
        var collectionUrl = $(".dropdown-collection[data-value=${ hue_collection.id }]").data("settings-url");
        $(".change-settings").attr("href", collectionUrl);
      % endif
    % endif

    $(".dropdown-collection").click(function (e) {
      e.preventDefault();
      var collectionId = $(this).data("value");
      $("select[name='collection']").val(collectionId);
      % if user.is_superuser:
        $(".change-settings").attr("href", $(this).data("settings-url"));
      % endif
      $.cookie("hueSearchLastCollection", collectionId, {expires: 90});
      $("form").find("input[type='hidden']").val("");
      $("form").submit();
    });

    $("#recordsPerPage").change(function () {
      $("input[name='rows']").val($(this).val());
      $("input[name='rows']").closest("form").submit();
    });
    $("#recordsPerPage").val($("input[name='rows']").val());

    var sortingData = ${ hue_collection and hue_collection.sorting.data or '[]' | n,unicode };
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

    $("#id_query").focus();

    $(document).on("keydown", function (e) {
      if (!e.ctrlKey && !e.altKey && !e.metaKey){
        if (!$("#id_query").is(":focus")) {
          $("#id_query").focus();
          $("#id_query").val($("#id_query").val());
        }
      }
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

    % if hue_collection:
    $("#id_query").on("keyup", function() {
      var query = $("#id_query").val();
      if ($.trim(query) != "") {
        $("#id_query").addClass("deletable");
      }
      else {
        $("#id_query").removeClass("deletable");
      }
    });
    % endif

  });
</script>

${ commonfooter(messages) | n,unicode }
