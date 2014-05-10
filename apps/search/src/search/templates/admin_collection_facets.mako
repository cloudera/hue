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
<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user, "29px") | n,unicode }

<%layout:skeleton>
  <%def name="title()">
    <h4>${ _('Facets for') } <strong>${ hue_collection.name }</strong></h4>
  </%def>
  <%def name="navigation()">
    ${ layout.sidebar(hue_collection, 'facets') }
  </%def>
  <%def name="content()">

    <link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">
    <script src="/static/ext/js/bootstrap-editable.min.js"></script>
    <script src="/static/ext/js/knockout.x-editable.js"></script>

    <form method="POST" class="form-horizontal" data-bind="submit: submit">
      <div class="well">
      <div class="section">
        <div class="alert alert-info">
          <div class="pull-right" style="margin-top: 10px">
            <label>
              <input type='checkbox' data-bind="checked: properties().isEnabled" style="margin-top: -2px; margin-right: 4px"/> ${_('Enabled') }
            </label>
          </div>
          <h3>${_('Facets')}</h3>
          ${_('Facets provide an intuitive way to filter the results.')}
          ${_('Different types of facets can be added on the following steps.')}
          <strong>&nbsp;<span data-bind="visible: !properties().isEnabled()">${_('Facets are currently disabled.')}</span></strong>
        </div>
      </div>

      <div id="facets" class="section">
        <ul class="nav nav-pills">
          <li class="active"><a href="#step1" class="step">${ _('Step 1: General') }</a></li>
          <li><a href="#step2" class="step">${ _('Step 2: Field Facets') }</a></li>
          <li><a href="#step3" class="step">${ _('Step 3: Range Facets') }</a></li>
          <li><a href="#step4" class="step">${ _('Step 4: Date Facets') }</a></li>
          <li><a href="#step5" class="step">${ _('Step 5: Graphical Facet') }</a></li>
          <li><a href="#step6" class="step">${ _('Step 6: Facets Order') }</a></li>
        </ul>

        <div id="step1" class="stepDetails">
          <div class="control-group">
            <label class="control-label"> ${_('Limit') }</label>
            <div class="controls">
              <input type='number' data-bind="value: properties().limit" class="input-mini"/>
            </div>
          </div>
          <div class="control-group">
            <label class="control-label"> ${_('Mincount') }</label>
            <div class="controls">
              <input type='number' data-bind="value: properties().mincount" class="input-mini"/>
            </div>
          </div>
          <div class="control-group">
            <label class="control-label"> ${_('Sort') }</label>
            <div class="controls">
              <select data-bind="value: properties().sort">
                <option value="count">count</option>
                <option value="index">index</option>
              </select>
            </div>
          </div>
        </div>

        <div id="step2" class="stepDetails hide">
          <div data-bind="visible: fieldFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
            <em>${_('There are currently no field facets defined.')}</em>
          </div>
          <div data-bind="foreach: fieldFacets">
            <div class="bubble">
              <strong><span data-bind="editable: label"></span></strong>
              <span style="color:#666;font-size: 12px">(<span data-bind="text: field"></span>)</span>
              <a class="btn btn-small" data-bind="click: $root.removeFieldFacet"><i class="fa fa-trash-o"></i></a>
            </div>
          </div>
          <div class="clearfix"></div>
          <div class="miniform">
            ${_('Field')}
            <select id="select-field-facet" data-bind="options: fieldFacetsList, value: selectedFieldFacet"></select>
            &nbsp;${_('Label')}
            <input id="selectedFieldLabel" type="text" data-bind="value: selectedFieldLabel" class="input" />
            <br/>
            <br/>
            <a class="btn" data-bind="click: $root.addFieldFacet"><i class="fa fa-plus-circle"></i> ${_('Add to Field Facets')}</a>
            &nbsp;<span id="field-facet-error" class="label label-important hide">${_('The field you are trying to add is already in the list.')}</span>
          </div>
        </div>

      <div id="step3" class="stepDetails hide">
        <div data-bind="visible: rangeFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no range facets defined.')}</em>
        </div>
        <div data-bind="foreach: rangeFacets">
          <div class="bubble">
            <strong><span data-bind="editable: label"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: field"></span>, <span data-bind="editable: start"></span> <i class="fa fa-double-angle-right"></i> <span data-bind="editable: end"></span>,
              <i class="fa fa-resize-horizontal"></i> <span data-bind="editable: gap"></span>)
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeRangeFacet"><i class="fa fa-trash-o"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select data-bind="options: rangeFacetsList, value: selectedRangeFacet"></select>
          &nbsp;${_('Label')}
          <input id="selectedRangeLabel" type="text" data-bind="value: selectedRangeLabel" class="input" />
          <br/>
          <br/>
          ${_('Start')}
          <input type="number" data-bind="value: selectedRangeStartFacet" class="input-mini" />
          &nbsp;${_('End')}
          <input type="number" data-bind="value: selectedRangeEndFacet" class="input-mini" />
          &nbsp;${_('Gap')}
          <input type="number" data-bind="value: selectedRangeGapFacet" class="input-mini" />
          <br/>
          <br/>
          <a class="btn" data-bind="click: $root.addRangeFacet"><i class="fa fa-plus-circle"></i> ${_('Add to Range Facets')}</a>
        </div>
      </div>

      <div id="step4" class="stepDetails hide">
        <div data-bind="visible: dateFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no date facets defined.')}</em>
        </div>
        <div data-bind="foreach: dateFacets">
          <div class="bubble">
            <strong><span data-bind="editable: label"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: field"></span>, <span data-bind="editable: start"></span> <i class="fa fa-double-angle-right"></i> <span data-bind="editable: end"></span>,
              <i class="fa fa-resize-horizontal"></i> <span data-bind="editable: gap"></span>, <i class="fa fa-calendar"></i> <span data-bind="editable: format"></span>)
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeDateFacet"><i class="fa fa-trash-o"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select data-bind="options: dateFacetsList, value: selectedDateFacet"></select>
          &nbsp;${_('Label')}
          <input id="selectedDateLabel" type="text" data-bind="value: selectedDateLabel" class="input" />
          <br/>
          <br/>
          <span>
            ${_('Range from')}
            <span data-bind="template: {name: 'scriptDateMath', data: selectedDateDateMaths()[0]}"/>
          </span>
          <span>
            &nbsp;${_('before today until')}
            <span  data-bind="template: {name: 'scriptDateMath', data: selectedDateDateMaths()[1]}"/>
          </span>
          <span>
            &nbsp;${_('before today. Goes up by increments of')}
            <span id="scriptTable" data-bind="template: {name: 'scriptDateMath', data: selectedDateDateMaths()[2]}"/>
          </span>
          <br/>
          <br/>
          ${_('Date format')}
          <input id="dateFormatInput" type="text" data-bind="value: selectedDateFormat" class="input" /> <a href="#formatHelpModal" class="btn btn-mini" data-toggle="modal"><i class="fa fa-question-circle"></i></a>
          <br/>
          <br/>
          <a class="btn" data-bind="click: $root.addDateFacet"><i class="fa fa-plus-circle"></i> ${_('Add to Date Facets')}</a>
        </div>
      </div>

      <div id="step5" class="stepDetails hide">
        <div data-bind="visible: chartFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There is currently no graphical facet defined. Remember, you can add just one field as graphical facet.')}</em>
        </div>
        <div data-bind="foreach: chartFacets">
          <div class="bubble">
            <strong><span data-bind="editable: label"></span></strong>
            <span style="color:#666;font-size: 12px">
              (<span data-bind="text: field"></span>, <span data-bind="editable: start"></span> <i class="fa fa-double-angle-right"></i> <span data-bind="editable: end"></span>,
              <i class="fa fa-resize-horizontal"></i> <span data-bind="editable: gap"></span>)
            </span>
            <a class="btn btn-small" data-bind="click: $root.removeChartFacet"><i class="fa fa-trash-o"></i></a>
          </div>
        </div>
        <div class="clearfix"></div>
        <div class="miniform">
          ${_('Field')}
          <select id="select-chart-facet" data-bind="options: chartFacetsList, value: selectedChartFacet"></select>
          &nbsp;${_('Label')}
          <input id="selectedChartLabel" type="text" data-bind="value: selectedChartLabel" class="input" />
          <br/>
          <br/>
          ${_('Start')}
          <input id="selectedChartStartFacet" type="text" data-bind="value: selectedChartStartFacet" class="input-mini" data-placeholder-general="${_('ie. 0')}" data-placeholder-date="${_('ie. NOW-12HOURS/MINUTES')}" />
          &nbsp;${_('End')}
          <input id="selectedChartEndFacet" type="text" data-bind="value: selectedChartEndFacet" class="input-mini" data-placeholder-general="${_('ie. 100')}" data-placeholder-date="${_('ie. NOW')}" />
          &nbsp;${_('Gap')}
          <input id="selectedChartGapFacet" type="text" data-bind="value: selectedChartGapFacet" class="input-mini" data-placeholder-general="${_('ie. 10')}" data-placeholder-date="${_('ie. +30MINUTES')}" />
          <span class="muted">&nbsp;${_('If empty this will be treated as a simple Field Facet.')} &nbsp;<a href="http://wiki.apache.org/solr/SimpleFacetParameters#rangefaceting" target="_blank"><i class="fa fa-external-link"></i> ${_('Read more about facets...')}</a></span>
          <br/>
          <br/>
          <a class="btn" data-bind="click: $root.addChartFacet, css:{disabled: $root.chartFacets().length == 1}"><i class="fa fa-plus-circle"></i> ${_('Set as Graphical Facet')}</a>
          &nbsp;<span id="chart-facet-error" class="label label-important hide">${_('You can add just one field as graphical facet')}</span>
          <span id="chart-facet-error-wrong-field-type" class="label label-important hide">${_('You can add just one field as graphical facet')}</span>
        </div>
      </div>

      <div id="step6" class="stepDetails hide">
        <div data-bind="visible: sortableFacets().length == 0" style="padding-left: 10px;margin-bottom: 20px">
          <em>${_('There are currently no Facets defined.')}</em>
        </div>
        <div data-bind="sortable: sortableFacets, afterMove: isSaveBtnVisible(true)">
          <div class="bubble" style="float: none;cursor: move">
            <i class="fa fa-arrows"></i>
            <strong><span data-bind="text: label"></span></strong>
            <span style="color:#666;font-size: 12px">(<span data-bind="text: field"></span>)</span>
          </div>
        </div>
      </div>

      <script id="scriptDateMath" type="text/html">
        <input class="input-mini" type="number" data-bind="value: frequency" />
        <select class="input-small" data-bind="value: unit">
          <option value="YEAR">YEARS</option>
          <option value="MONTH">MONTHS</option>
          <option value="DAYS">DAYS</option>
          <option value="DATE">DATE</option>
          <option value="HOURS">HOURS</option>
          <option value="MINUTES">MINUTES</option>
          <option value="SECONDS">SECONDS</option>
          <option value="MILLISECONDS">MILLISECONDS</option>
        </select>
      </script>

      </div>

      <div class="form-actions" style="margin-top: 80px">
        <a id="backBtn" class="btn disabled disable-feedback">${ _('Back') }</a>
        <a id="nextBtn" class="btn btn-primary disable-feedback">${ _('Next') }</a>
        <button type="submit" class="btn btn-primary" data-bind="visible: isSaveBtnVisible()" id="save-facets">${_('Save')}</button>
      </div>
    </div>
    </form>
  </%def>
</%layout:skeleton>


<div id="formatHelpModal" class="modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${ _('Format Help') }</h3>
  </div>
  <div class="modal-body">
    <p>
      ${ _('You can specify here how you want the date to be formatted.')}
      <br/>
      ${ _('Use a predefined format:')}
      <br/>
      <table class="table table-striped table-bordered">
      <tr>
        <td>
          <a href="javascript:void(0)" class="formatChooser">FROMNOW</a>
        </td>
      </tr>
      <tr>
        <td>
          <a href="javascript:void(0)" class="formatChooser">YYYY/MM/DD</a>
        </td>
      </tr>
      <tr>
        <td>
          <a href="javascript:void(0)" class="formatChooser">YYYY/MM/DD HH:mm</a>
        </td>
      </tr>
      <tr>
        <td>
          <a href="javascript:void(0)" class="formatChooser">YYYY/MM/DD HH:mm:ss</a>
        </td>
      </tr>
      <tr>
        <td>
          <a href="javascript:void(0)" class="formatChooser">HH:mm</a>
        </td>
      </tr>
      <tr>
        <td>
          <a href="javascript:void(0)" class="formatChooser">HH:mm:ss</a>
        </td>
      </tr>
    </table>
    ${ _('or any combination of these fields:')} <br/><br/>

    <table class="table table-striped table-bordered">
  <tbody>
    <tr>
      <th></th>
      <th>${ _('Token')}</th>
      <th>${ _('Output')}</th>
    </tr>
    <tr>
      <td><b>${ _('Relative time')}</b></td>
      <td>FROMNOW</td>
      <td>${_('9 hours ago')}</td>
    </tr>
    <tr>
      <td><b>${ _('Month')}</b></td>
      <td>M</td>
      <td>1 2 ... 11 12</td>
    </tr>
    <tr>
      <td></td>
      <td>Mo</td>
      <td>1st 2nd ... 11th 12th</td>
    </tr>
    <tr>
      <td></td>
      <td>MM</td>
      <td>01 02 ... 11 12</td>
    </tr>
    <tr>
      <td></td>
      <td>MMM</td>
      <td>${ _('Jan Feb ... Nov Dec')}</td>
    </tr>
    <tr>
      <td></td>
      <td>MMMM</td>
      <td>${ _('January February ... November December')}</td>
    </tr>
    <tr>
      <td><b>${ _('Day of Month')}</b></td>
      <td>D</td>
      <td>1 2 ... 30 30</td>
    </tr>
    <tr>
      <td></td>
      <td>Do</td>
      <td>${ _('1st 2nd ... 30th 31st')}</td>
    </tr>
    <tr>
      <td></td>
      <td>DD</td>
      <td>01 02 ... 30 31</td>
    </tr>
    <tr>
      <td><b>${ _('Day of Year')}</b></td>
      <td>DDD</td>
      <td>1 2 ... 364 365</td>
    </tr>
    <tr>
      <td></td>
      <td>DDDo</td>
      <td>${ _('1st 2nd ... 364th 365th')}</td>
    </tr>
    <tr>
      <td></td>
      <td>DDDD</td>
      <td>001 002 ... 364 365</td>
    </tr>
    <tr>
      <td><b>${ _('Day of Week')}</b></td>
      <td>d</td>
      <td>0 1 ... 5 6</td>
    </tr>
    <tr>
      <td></td>
      <td>do</td>
      <td>${ _('0th 1st ... 5th 6th')}</td>
    </tr>
    <tr>
      <td></td>
      <td>ddd</td>
      <td>${ _('Sun Mon ... Fri Sat')}</td>
    </tr>
    <tr>
      <td></td>
      <td>dddd</td>
      <td>${ _('Sunday Monday ... Friday Saturday')}</td>
    </tr>
    <tr>
      <td><b>${ _('Week of Year')}</b></td>
      <td>w</td>
      <td>1 2 ... 52 53</td>
    </tr>
    <tr>
      <td></td>
      <td>wo</td>
      <td>${ _('1st 2nd ... 52nd 53rd')}</td>
    </tr>
    <tr>
      <td></td>
      <td>ww</td>
      <td>01 02 ... 52 53</td>
    </tr>
    <tr>
      <td><b>${ _('ISO Week of Year')}</b></td>
      <td>W</td>
      <td>1 2 ... 52 53</td>
    </tr>
    <tr>
      <td></td>
      <td>Wo</td>
      <td>${ _('1st 2nd ... 52nd 53rd')}</td>
    </tr>
    <tr>
      <td></td>
      <td>WW</td>
      <td>01 02 ... 52 53</td>
    </tr>
    <tr>
      <td><b>${ _('Year')}</b></td>
      <td>YY</td>
      <td>70 71 ... 29 30</td>
    </tr>
    <tr>
      <td></td>
      <td>YYYY</td>
      <td>1970 1971 ... 2029 2030</td>
    </tr>
    <tr>
      <td><b>AM/PM</b></td>
      <td>A</td>
      <td>AM PM</td>
    </tr>
    <tr>
      <td></td>
      <td>a</td>
      <td>am pm</td>
    </tr>
    <tr>
      <td><b>${ _('Hour')}</b></td>
      <td>H</td>
      <td>0 1 ... 22 23</td>
    </tr>
    <tr>
      <td></td>
      <td>HH</td>
      <td>00 01 ... 22 23</td>
    </tr>
    <tr>
      <td></td>
      <td>h</td>
      <td>1 2 ... 11 12</td>
    </tr>
    <tr>
      <td></td>
      <td>hh</td>
      <td>01 02 ... 11 12</td>
    </tr>
    <tr>
      <td><b>${ _('Minute')}</b></td>
      <td>m</td>
      <td>0 1 ... 58 59</td>
    </tr>
    <tr>
      <td></td>
      <td>mm</td>
      <td>00 01 ... 58 59</td>
    </tr>
    <tr>
      <td><b>${ _('Second')}</b></td>
      <td>s</td>
      <td>0 1 ... 58 59</td>
    </tr>
    <tr>
      <td></td>
      <td>ss</td>
      <td>00 01 ... 58 59</td>
    </tr>
    <tr>
      <td><b>${ _('Fractional Second')}</b></td>
      <td>S</td>
      <td>0 1 ... 8 9</td>
    </tr>
    <tr>
      <td></td>
      <td>SS</td>
      <td>0 1 ... 98 99</td>
    </tr>
    <tr>
      <td></td>
      <td>SSS</td>
      <td>0 1 ... 998 999</td>
    </tr>
    <tr>
      <td></td>
      <td>ss</td>
      <td>00 01 ... 58 59</td>
    </tr>
    <tr>
      <td><b>${ _('Unix Timestamp')}</b></td>
      <td>X</td>
      <td>1360013296</td>
    </tr>
  </tbody>
</table>
    </p>
  </div>
  <div class="modal-footer">
    <a href="javascript:void(0)" class="btn" data-dismiss="modal">${ _('Close')}</a>
  </div>
</div>

<link rel="stylesheet" href="/static/ext/css/bootstrap-datepicker.min.css" type="text/css" media="screen" title="no title" charset="utf-8" />
<link href="/static/ext/css/bootstrap-editable.css" rel="stylesheet">

<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-datepicker.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/bootstrap-editable.min.js"></script>
<script src="/static/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/knockout-sortable.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-1.10.4.draggable-droppable-sortable.min.js"></script>

<script type="text/javascript">
  var MOMENT_DATE_FORMAT = "MM-DD-YYYY";

  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
  }

  function UUID() {
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
            s4() + '-' + s4() + s4() + s4();
  }

  var Facet = function (args) {
    var _facet = {
      uuid: (typeof args['uuid'] !== 'undefined' && args['uuid'] != null) ? args['uuid'] : UUID(),
      type: args['type'],
      field: args['field'],
      label: ko.observable(args['label']),
      format: ko.observable(args['format']),
      start: ko.observable(args['start']),
      end: ko.observable(args['end']),
      gap: ko.observable(args['gap']),
      isVerbatim: false,
      verbatim: ""
    }
    _facet.label.subscribe(function (newValue) {
      if ($.trim(newValue) == ""){
        _facet.label(_facet.field);
      }
      viewModel.isSaveBtnVisible(true);
    });
    _facet.format.subscribe(function (newValue) {
      viewModel.isSaveBtnVisible(true);
    });
    _facet.start.subscribe(function (newValue) {
      if (_facet.type == "date" && typeof newValue == "string"){
        valueParseHelper(newValue, _facet.start, 10);
      }
      viewModel.isSaveBtnVisible(true);
    });
    _facet.end.subscribe(function (newValue) {
      if (_facet.type == "date" && typeof newValue == "string"){
        valueParseHelper(newValue, _facet.end, 0);
      }
      viewModel.isSaveBtnVisible(true);
    });
    _facet.gap.subscribe(function (newValue) {
      if (_facet.type == "date" && typeof newValue == "string"){
        valueParseHelper(newValue, _facet.gap, 1);
      }
      viewModel.isSaveBtnVisible(true);
    });
    return _facet;
  }

  function valueParseHelper(value, field, defaultFrequency){
    // try to parse the user free input
    try {
      field(new DateMath({frequency: parseFloat($.trim(value).split(" ")[0]), unit: $.trim(value).split(" ")[1]}));
    }
    catch (exception){
      $(document).trigger("error", "${ _('There was an error parsing your input') }");
      field(new DateMath({frequency: defaultFrequency, unit: 'DAYS'}));
    }
  }

  var FieldFacet = function (obj) {
    return new Facet({type: "field", field: obj.field, label: obj.label, uuid: obj.uuid});
  }

  var ChartFacet = function (obj) {
    return new Facet({type: "chart", field: obj.field, label: obj.label, start: obj.start, end: obj.end, gap: obj.gap, uuid: obj.uuid});
  }

  var RangeFacet = function (obj) {
    return new Facet({type: "range", field: obj.field, label: obj.label, start: obj.start, end: obj.end, gap: obj.gap, uuid: obj.uuid});
  }

  var DateFacet = function (obj) {
    return new Facet({type: "date", field: obj.field, label: obj.label, format: obj.format, start: obj.start, end: obj.end, gap: obj.gap, uuid: obj.uuid});
  }

  var Properties = function (properties) {
    var self = this;

    self.isEnabled = ko.observable(properties.isEnabled);
    self.limit = ko.observable(properties.limit);
    self.mincount = ko.observable(properties.mincount);
    self.sort = ko.observable(properties.sort);

    self.isEnabled.subscribe(function (newValue) {
      viewModel.isSaveBtnVisible(true);
    });

    self.limit.subscribe(function (newValue) {
      viewModel.isSaveBtnVisible(true);
    });

    self.mincount.subscribe(function (newValue) {
      viewModel.isSaveBtnVisible(true);
    });

    self.sort.subscribe(function (newValue) {
      viewModel.isSaveBtnVisible(true);
    });
  }

  var DateMath = function (args) {
    var self = this;

    self.frequency = ko.observable(args['frequency']);
    self.unit = ko.observable(args['unit']);
    self.isVerbatim = ko.observable(typeof args['isVerbatim'] !== 'undefined' ? args['isVerbatim'] : false);
    self.verbatim = ko.observable(args['verbatim']);
    self.isRounded = ko.observable(typeof args['isRounded'] !== 'undefined' ? args['isRounded'] : true);

    self.toString = function() {
      return self.frequency() + ' ' + self.unit();
    };
  }

  function ViewModel() {
    var self = this;

    self.isSaveBtnVisible = ko.observable(false);

    self.fields = ko.observableArray(${ hue_collection.fields(user) | n,unicode });

    self.fullFields = {}
    $.each(${ hue_collection.fields_data(user) | n,unicode }, function(index, field) {
      self.fullFields[field.name] = field;
    });

    self.properties = ko.observable(new Properties(${ hue_collection.facets.data | n,unicode }.properties));

    self.fieldFacets = ko.observableArray(ko.utils.arrayMap(${ hue_collection.facets.data | n,unicode }.fields, function (obj) {
      return new FieldFacet(obj);
    }));

    // Remove already selected fields
    self.fieldFacetsList = ko.observableArray(${ hue_collection.fields(user) | n,unicode });
    $.each(self.fieldFacets(), function(index, field) {
      self.fieldFacetsList.remove(field.field);
    });

    self.rangeFacets = ko.observableArray(ko.utils.arrayMap(${ hue_collection.facets.data | n,unicode }.ranges, function (obj) {
      return new RangeFacet(obj);
    }));

    // Only ranges
    self.rangeFacetsList = ko.observableArray([]);
    $.each(self.fields(), function(index, field) {
      if (self.fullFields[field] && ['tdate', 'date', 'tint', 'int', 'tlong', 'long', 'double', 'tdouble'].indexOf(self.fullFields[field].type) >= 0) {
        self.rangeFacetsList.push(field);
      }
    });

    self.dateFacets = ko.observableArray(ko.utils.arrayMap(${ hue_collection.facets.data | n,unicode }.dates, function (obj) {
      return new DateFacet({
          field: obj.field,
          label: obj.label,
          format: obj.format,
          start: new DateMath(obj.start),
          end: new DateMath(obj.end),
          gap: new DateMath(obj.gap),
          uuid: obj.uuid,
      });
    }));
    // Only dates
    self.dateFacetsList = ko.observableArray([]);
    $.each(self.fields(), function(index, field) {
      if (self.fullFields[field] && ['tdate', 'date'].indexOf(self.fullFields[field].type) >= 0) {
        self.dateFacetsList.push(field);
      }
    });

    self.chartFacets = ko.observableArray(ko.utils.arrayMap(${ hue_collection.facets.data | n,unicode }.charts, function (obj) {
      return new ChartFacet(obj);
    }));

    // Only dates and numbers
    self.chartFacetsList = ko.observableArray([]);
    $.each(self.fields(), function(index, field) {
      if (self.fullFields[field] && ['tdate', 'date', 'tint', 'int', 'tlong', 'long', 'double', 'tdouble'].indexOf(self.fullFields[field].type) >= 0) {
        self.chartFacetsList.push(field);
      }
    });

    // List of all facets sorted by UUID
    self.sortableFacets = ko.observableArray(self.fieldFacets().concat(self.rangeFacets()).concat(self.dateFacets()));
    self.sortableFacets.sort(function(left, right) {
      var sorted_ids = ${ hue_collection.facets.data | n,unicode }.order;
      return sorted_ids.indexOf(left.uuid) > sorted_ids.indexOf(right.uuid);
    })

    self.selectedFieldFacet = ko.observable();
    self.selectedFieldFacet.subscribe(function (newValue) {
      $("#selectedFieldLabel").prop("placeholder", newValue);
    });
    self.selectedFieldLabel = ko.observable("");

    self.selectedRangeFacet = ko.observable();
    self.selectedRangeFacet.subscribe(function (newValue) {
      $("#selectedRangeLabel").prop("placeholder", newValue);
    });
    self.selectedRangeLabel = ko.observable("");
    self.selectedRangeStartFacet = ko.observable(0);
    self.selectedRangeEndFacet = ko.observable(100);
    self.selectedRangeGapFacet = ko.observable(10);

    self.selectedDateFacet = ko.observable();
    self.selectedDateFacet.subscribe(function (newValue) {
      $("#selectedDateLabel").prop("placeholder", newValue);
    });
    self.selectedDateLabel = ko.observable("");
    self.selectedDateFormat = ko.observable("");

    self.selectedDateDateMaths = ko.observableArray([
        // Same as addDateFacet()
        new DateMath({frequency: 10, unit: 'DAYS'}),
        new DateMath({frequency: 0, unit: 'DAYS'}),
        new DateMath({frequency: 1, unit: 'DAYS'})
    ]);

    self.selectedChartFacet = ko.observable();
    self.selectedChartFacet.subscribe(function (newValue) {
      var _field = self.fullFields[newValue];
      if (_field.type == "tdate"){
        $("#selectedChartStartFacet").attr("placeholder", $("#selectedChartStartFacet").data("placeholder-date")).removeClass("input-mini");
        $("#selectedChartEndFacet").attr("placeholder", $("#selectedChartEndFacet").data("placeholder-date")).removeClass("input-mini");
        $("#selectedChartGapFacet").attr("placeholder", $("#selectedChartGapFacet").data("placeholder-date")).removeClass("input-mini");
      }
      else {
        $("#selectedChartStartFacet").attr("placeholder", $("#selectedChartStartFacet").data("placeholder-general")).addClass("input-mini");
        $("#selectedChartEndFacet").attr("placeholder", $("#selectedChartEndFacet").data("placeholder-general")).addClass("input-mini");
        $("#selectedChartGapFacet").attr("placeholder", $("#selectedChartGapFacet").data("placeholder-general")).addClass("input-mini");
      }
      $("#selectedChartLabel").prop("placeholder", newValue);
    });
    self.selectedChartLabel = ko.observable("");
    self.selectedChartStartFacet = ko.observable("");
    self.selectedChartEndFacet = ko.observable("");
    self.selectedChartGapFacet = ko.observable("");


    self.removeFieldFacet = function (facet) {
      self.fieldFacets.remove(facet);
      self.sortableFacets.remove(facet);
      self.fieldFacetsList.push(facet.field);
      self.fieldFacetsList.sort();
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.removeRangeFacet = function (facet) {
      self.rangeFacets.remove(facet);
      self.sortableFacets.remove(facet);
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.removeDateFacet = function (facet) {
      self.dateFacets.remove(facet);
      self.sortableFacets.remove(facet);
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.removeChartFacet = function (facet) {
      self.chartFacets.remove(facet);
      self.sortableFacets.remove(facet);
      self.chartFacetsList.push(facet.field);
      self.chartFacetsList.sort();
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.updateSortableFacets = function () {
      self.isSaveBtnVisible(true);
    };

    self.addFieldFacet = function () {
      var found = false;
      ko.utils.arrayForEach(self.fieldFacets(), function(facet) {
        if (facet.field == self.selectedFieldFacet()){
          found = true;
        }
      });
      if (!found){
        if (self.selectedFieldLabel() == ""){
          self.selectedFieldLabel(self.selectedFieldFacet());
        }
        var newFacet = new FieldFacet({field: self.selectedFieldFacet(), label: self.selectedFieldLabel()});
        self.fieldFacets.push(newFacet);
        self.sortableFacets.push(newFacet);
        self.selectedFieldLabel("");
        self.fieldFacetsList.remove(self.selectedFieldFacet());
        self.properties().isEnabled(true);
        self.updateSortableFacets();
        self.isSaveBtnVisible(true);
      }
      else {
        $("#field-facet-error").show();
      }
    };

    self.addRangeFacet = function () {
      if (self.selectedRangeLabel() == ""){
        self.selectedRangeLabel(self.selectedRangeFacet());
      }
      var newFacet = new RangeFacet({
          field: self.selectedRangeFacet(),
          label: self.selectedRangeLabel(),
          start: self.selectedRangeStartFacet(),
          end: self.selectedRangeEndFacet(),
          gap: self.selectedRangeGapFacet()
       });
      self.rangeFacets.push(newFacet);
      self.sortableFacets.push(newFacet);
      self.selectedRangeLabel("");
      self.selectedRangeStartFacet(0);
      self.selectedRangeEndFacet(100);
      self.selectedRangeGapFacet(10);
      self.properties().isEnabled(true);
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };

    self.addDateFacet = function () {
      if (self.selectedDateLabel() == ""){
        self.selectedDateLabel(self.selectedDateFacet());
      }
      var newFacet = new DateFacet({
          field: self.selectedDateFacet(),
          label: self.selectedDateLabel(),
          format: self.selectedDateFormat(),
          start: self.selectedDateDateMaths()[0],
          end: self.selectedDateDateMaths()[1],
          gap: self.selectedDateDateMaths()[2]
      });
      self.dateFacets.push(newFacet);
      self.sortableFacets.push(newFacet);
      self.selectedDateLabel("");
      self.selectedDateFormat("");
      self.selectedDateDateMaths([
        new DateMath({frequency: 10, unit: 'DAYS'}),
        new DateMath({frequency: 0, unit: 'DAYS'}),
        new DateMath({frequency: 1, unit: 'DAYS'})
      ]);
      self.properties().isEnabled(true);
      self.updateSortableFacets();
      self.isSaveBtnVisible(true);
    };


    self.addChartFacet = function () {
      if (self.chartFacets().length == 0){
        var found = false;
        ko.utils.arrayForEach(self.chartFacets(), function(facet) {
          if (facet.field == self.selectedChartFacet()){
            found = true;
          }
        });
        if (!found){
          if (self.selectedChartLabel() == ""){
            self.selectedChartLabel(self.selectedChartFacet());
          }
          var newFacet = new ChartFacet({field: self.selectedChartFacet(), label: self.selectedChartLabel()});
          var newFacet = new ChartFacet({
            field: self.selectedChartFacet(),
            label: self.selectedChartLabel(),
            start: self.selectedChartStartFacet(),
            end: self.selectedChartEndFacet(),
            gap: self.selectedChartGapFacet()
         });
          self.chartFacets.push(newFacet);
          self.selectedChartLabel("");
          self.selectedChartStartFacet("");
          self.selectedChartEndFacet("");
          self.selectedChartGapFacet("");
          self.chartFacetsList.remove(self.selectedChartFacet());
          self.properties().isEnabled(true);
          self.isSaveBtnVisible(true);
        }
      }
      else {
        $("#chart-facet-error").show();
      }
    };

    self.submit = function () {
      $.ajax("${ url('search:admin_collection_facets', collection_id=hue_collection.id) }", {
        data: {
          'properties': ko.toJSON(self.properties),
          'fields': ko.toJSON(self.fieldFacets),
          'ranges': ko.toJSON(self.rangeFacets),
          'dates': ko.toJSON(self.dateFacets),
          'charts': ko.toJSON(self.chartFacets),
          'order': ko.toJSON(ko.utils.arrayMap(self.sortableFacets(), function (obj) {
              return obj.uuid;
           }))
        },
        contentType: 'application/json',
        type: 'POST',
        success: function () {
          $(document).trigger("info", "${_('Facets updated')}");
          self.isSaveBtnVisible(false);
        },
        error: function (data) {
          $(document).trigger("error", "${_('Error: ')}" + data);
        },
        complete: function() {
          $("#save-facets").button('reset');
        }
      });
    };
  };

  var viewModel = new ViewModel();

  $(document).ready(function () {
    $(".btn-primary").button("reset");
    ko.applyBindings(viewModel);
    viewModel.isSaveBtnVisible(false);

    $("#select-field-facet").click(function(){
      $("#field-facet-error").hide();
    });

    $("#select-chart-facet").click(function(){
      $("#chart-facet-error").hide();
    });

    var currentStep = "step1";

    routie({
      "step1":function () {
        showStep("step1");
      },
      "step2":function () {
        if (validateStep("step1")) {
          showStep("step2");
        }
      },
      "step3":function () {
        if (validateStep("step1") && validateStep("step2")) {
          showStep("step3");
        }
      },
      "step4":function () {
        if (validateStep("step1") && validateStep("step2")) {
          showStep("step4");
        }
      },
      "step5":function () {
        if (validateStep("step1") && validateStep("step2")) {
          showStep("step5");
        }
      },
      "step6":function () {
        if (validateStep("step1") && validateStep("step2")) {
          showStep("step6");
        }
      }
    });

      function showStep(step) {
        currentStep = step;
        if (step != "step1") {
          $("#backBtn").removeClass("disabled");
        }
        else {
          $("#backBtn").addClass("disabled");
        }
        if (step != $(".stepDetails:last").attr("id")) {
          $("#nextBtn").removeClass("disabled");
        }
        else {
          $("#nextBtn").addClass("disabled");
        }
        $("a.step").parent().removeClass("active");
        $("a.step[href=#" + step + "]").parent().addClass("active");
        $(".stepDetails").hide();
        $("#" + step).show();
      }

      function showSection(section) {
        $(".section").hide();
        $("#" + section).show();
      }

      function validateStep(step) {
        var proceed = true;
        $("#" + step).find("[validate=true]").each(function () {
          if ($(this).val().trim() == "") {
            proceed = false;
            routie(step);
            $(this).parents(".control-group").addClass("error");
            $(this).parent().find(".help-inline").remove();
            $(this).after("<span class=\"help-inline\"><strong>${ _('This field is required.') }</strong></span>");
          }
        });
        return proceed;
      }

      $("#backBtn").click(function () {
        var nextStep = (currentStep.substr(4) * 1 - 1);
        if (nextStep >= 1) {
          routie("step" + nextStep);
        }
      });

      $("#nextBtn").click(function () {
        var nextStep = (currentStep.substr(4) * 1 + 1);
        if (nextStep <= $(".step").length) {
          routie("step" + nextStep);
        }
      });

      $(".formatChooser").on("click", function(){
        viewModel.selectedDateFormat($(this).text());
        $("#formatHelpModal").modal("hide");
      });
      var _typeSource = [];
      $(".formatChooser").each(function(){
        _typeSource.push($(this).text());
      });

      $("#dateFormatInput").typeahead({
        source: _typeSource
      });

  });
</script>

${ commonfooter(messages) | n,unicode }
