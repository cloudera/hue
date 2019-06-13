// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';
import ko from 'knockout';

ko.bindingHandlers.dateRangePicker = {
  INTERVAL_OPTIONS: [
    {
      value: '+200MILLISECONDS',
      label: '200ms'
    },
    {
      value: '+1SECONDS',
      label: '1s'
    },
    {
      value: '+5SECONDS',
      label: '5s'
    },
    {
      value: '+30SECONDS',
      label: '30s'
    },
    {
      value: '+1MINUTES',
      label: '1m'
    },
    {
      value: '+5MINUTES',
      label: '5m'
    },
    {
      value: '+10MINUTES',
      label: '10m'
    },
    {
      value: '+30MINUTES',
      label: '30m'
    },
    {
      value: '+1HOURS',
      label: '1h'
    },
    {
      value: '+3HOURS',
      label: '3h'
    },
    {
      value: '+6HOURS',
      label: '6h'
    },
    {
      value: '+12HOURS',
      label: '12h'
    },
    {
      value: '+1DAYS',
      label: '1d'
    },
    {
      value: '+7DAYS',
      label: '7d'
    },
    {
      value: '+1MONTHS',
      label: '1M'
    },
    {
      value: '+6MONTHS',
      label: '6M'
    },
    {
      value: '+1YEARS',
      label: '1y'
    },
    {
      value: '+10YEARS',
      label: '10y'
    }
  ],
  EXTRA_INTERVAL_OPTIONS: [],

  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    const DATE_FORMAT = 'YYYY-MM-DD';
    const TIME_FORMAT = 'HH:mm:ss';
    const DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT;

    const _el = $(element);
    const _options = $.extend(valueAccessor(), {});

    const _intervalOptions = [];
    ko.bindingHandlers.dateRangePicker.INTERVAL_OPTIONS.forEach(interval => {
      _intervalOptions.push(
        '<option value="' + interval.value + '">' + interval.label + '</option>'
      );
    });

    function enableOptions() {
      const _opts = [];
      const _tmp = $('<div>').html(_intervalOptions.join(''));
      $.each(arguments, (cnt, item) => {
        if (_tmp.find("option[value='+" + item + "']").length > 0) {
          _opts.push(
            '<option value="+' +
              item +
              '">' +
              _tmp
                .find("option[value='+" + item + "']")
                .eq(0)
                .text() +
              '</option>'
          );
        }
      });
      return _opts;
    }

    function renderOptions(opts) {
      let _html = '';
      for (let i = 0; i < opts.length; i++) {
        _html += opts[i];
      }
      return _html;
    }

    const _tmpl = $(
      '<div class="simpledaterangepicker">' +
        '<div class="facet-field-cnt custom">' +
        '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
        '<div class="facet-field-switch"><i class="fa fa-calendar muted"></i> <a href="javascript:void(0)">' +
        KO_DATERANGEPICKER_LABELS.DATE_PICKERS +
        '</a></div>' +
        '</div>' +
        '<div class="facet-field-cnt picker">' +
        '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
        '<div class="facet-field-switch"><i class="fa fa-calendar-o muted"></i> <a href="javascript:void(0)">' +
        KO_DATERANGEPICKER_LABELS.CUSTOM_FORMAT +
        '</a></div>' +
        '</div>' +
        '<div class="facet-field-cnt picker">' +
        '<div class="facet-field-label facet-field-label-fixed-width">' +
        KO_DATERANGEPICKER_LABELS.START +
        '</div>' +
        '<div class="input-prepend input-group">' +
        '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
        '<input type="text" class="input-small form-control start-date" />' +
        '</div>' +
        '<div class="input-prepend input-group left-margin">' +
        '<span class="add-on input-group-addon"><i class="fa fa-clock-o"></i></span>' +
        '<input type="text" class="input-mini form-control start-time" />' +
        '</div>' +
        '</div>' +
        '<div class="facet-field-cnt picker">' +
        '<div class="facet-field-label facet-field-label-fixed-width">' +
        KO_DATERANGEPICKER_LABELS.END +
        '</div>' +
        '<div class="input-prepend input-group">' +
        '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
        '<input type="text" class="input-small form-control end-date" />' +
        '</div>' +
        '<div class="input-prepend input-group left-margin">' +
        '<span class="add-on input-group-addon"><i class="fa fa-clock-o"></i></span>' +
        '<input type="text" class="input-mini form-control end-time" />' +
        '</div>' +
        '</div>' +
        '<div class="facet-field-cnt picker">' +
        '<div class="facet-field-label facet-field-label-fixed-width">' +
        KO_DATERANGEPICKER_LABELS.INTERVAL +
        '</div>' +
        '<div class="input-prepend input-group"><span class="add-on input-group-addon"><i class="fa fa-repeat"></i></span></div>&nbsp;' +
        '<select class="input-small interval-select" style="margin-right: 6px">' +
        renderOptions(_intervalOptions) +
        '</select>' +
        '<input class="input interval hide" type="hidden" value="" />' +
        '</div>' +
        '<div class="facet-field-cnt custom">' +
        '<div class="facet-field-label facet-field-label-fixed-width">' +
        KO_DATERANGEPICKER_LABELS.START +
        '</div>' +
        '<div class="input-prepend input-group">' +
        '<span class="add-on input-group-addon"><i class="fa fa-calendar-o"></i></span>' +
        '<input type="text" class="input-large form-control start-date-custom" />' +
        '</div>' +
        '<span class="pointer custom-popover" data-trigger="click" data-toggle="popover" data-placement="right" rel="popover" data-html="true"' +
        '       title="' +
        KO_DATERANGEPICKER_LABELS.CUSTOM_POPOVER_TITLE +
        '"' +
        '       data-content="' +
        KO_DATERANGEPICKER_LABELS.CUSTOM_POPOVER_CONTENT +
        '">' +
        '&nbsp;&nbsp;<i class="fa fa-question-circle"></i>' +
        ' </span>' +
        '</div>' +
        '<div class="facet-field-cnt custom">' +
        '<div class="facet-field-label facet-field-label-fixed-width">' +
        KO_DATERANGEPICKER_LABELS.END +
        '</div>' +
        '<div class="input-prepend input-group">' +
        '<span class="add-on input-group-addon"><i class="fa fa-calendar-o"></i></span>' +
        '<input type="text" class="input-large form-control end-date-custom" />' +
        '</div>' +
        '</div>' +
        '<div class="facet-field-cnt custom">' +
        '<div class="facet-field-label facet-field-label-fixed-width">' +
        KO_DATERANGEPICKER_LABELS.INTERVAL +
        '</div>' +
        '<div class="input-prepend input-group">' +
        '<span class="add-on input-group-addon"><i class="fa fa-repeat"></i></span>' +
        '<input type="text" class="input-large form-control interval-custom" />' +
        '</div>' +
        '</div>' +
        '</div>'
    );

    _tmpl.insertAfter(_el);

    $('.custom-popover').popover();

    const _minMoment = moment(_options.min());
    const _maxMoment = moment(_options.max());

    if (_minMoment.isValid() && _maxMoment.isValid()) {
      _tmpl.find('.facet-field-cnt.custom').hide();
      _tmpl.find('.facet-field-cnt.picker').show();
      _tmpl.find('.start-date').val(_minMoment.utc().format(DATE_FORMAT));
      _tmpl.find('.start-time').val(_minMoment.utc().format(TIME_FORMAT));
      _tmpl.find('.end-date').val(_maxMoment.utc().format(DATE_FORMAT));
      _tmpl.find('.end-time').val(_maxMoment.utc().format(TIME_FORMAT));
      _tmpl.find('.interval').val(_options.gap());
      _tmpl.find('.interval-select').val(_options.gap());
      _tmpl.find('.interval-custom').val(_options.gap());
      if (
        _tmpl.find('.interval-select').val() == null ||
        ko.bindingHandlers.dateRangePicker.EXTRA_INTERVAL_OPTIONS.indexOf(
          _tmpl.find('.interval-select').val()
        ) > -1
      ) {
        pushIntervalValue(_options.gap());
        _tmpl.find('.facet-field-cnt.custom').show();
        _tmpl.find('.facet-field-cnt.picker').hide();
      }
    } else {
      _tmpl.find('.facet-field-cnt.custom').show();
      _tmpl.find('.facet-field-cnt.picker').hide();
      _tmpl.find('.start-date-custom').val(_options.min());
      _tmpl.find('.end-date-custom').val(_options.max());
      _tmpl.find('.interval-custom').val(_options.gap());
      pushIntervalValue(_options.gap());
    }

    if (typeof _options.relatedgap != 'undefined') {
      pushIntervalValue(_options.relatedgap());
    }

    _tmpl
      .find('.start-date')
      .datepicker({
        format: DATE_FORMAT.toLowerCase()
      })
      .on('changeDate', () => {
        rangeHandler(true);
      });

    _tmpl.find('.start-date').on('change', () => {
      rangeHandler(true);
    });

    _tmpl.find('.start-time').timepicker({
      minuteStep: 1,
      showSeconds: true,
      showMeridian: false,
      defaultTime: false
    });

    _tmpl
      .find('.end-date')
      .datepicker({
        format: DATE_FORMAT.toLowerCase()
      })
      .on('changeDate', () => {
        rangeHandler(false);
      });

    _tmpl.find('.end-date').on('change', () => {
      rangeHandler(true);
    });

    _tmpl.find('.end-time').timepicker({
      minuteStep: 1,
      showSeconds: true,
      showMeridian: false,
      defaultTime: false
    });

    _tmpl.find('.start-time').on('change', () => {
      // the timepicker plugin doesn't have a change event handler
      // so we need to wait a bit to handle in with the default field event
      window.setTimeout(() => {
        rangeHandler(true);
      }, 200);
    });

    _tmpl.find('.end-time').on('change', () => {
      window.setTimeout(() => {
        rangeHandler(false);
      }, 200);
    });

    if (_minMoment.isValid() && _maxMoment.isValid()) {
      rangeHandler(true);
    }

    _tmpl.find('.facet-field-cnt.picker .facet-field-switch a').on('click', () => {
      _tmpl.find('.facet-field-cnt.custom').show();
      _tmpl.find('.facet-field-cnt.picker').hide();
    });

    _tmpl.find('.facet-field-cnt.custom .facet-field-switch a').on('click', () => {
      _tmpl.find('.facet-field-cnt.custom').hide();
      _tmpl.find('.facet-field-cnt.picker').show();
    });

    _tmpl.find('.start-date-custom').on('change', () => {
      _options.min(_tmpl.find('.start-date-custom').val());
      _tmpl.find('.start-date').val(
        moment(_options.min())
          .utc()
          .format(DATE_FORMAT)
      );
      _tmpl.find('.start-time').val(
        moment(_options.min())
          .utc()
          .format(TIME_FORMAT)
      );
      _options.start(_options.min());
    });

    _tmpl.find('.end-date-custom').on('change', () => {
      _options.max(_tmpl.find('.end-date-custom').val());
      _tmpl.find('.end-date').val(
        moment(_options.max())
          .utc()
          .format(DATE_FORMAT)
      );
      _tmpl.find('.end-time').val(
        moment(_options.max())
          .utc()
          .format(TIME_FORMAT)
      );
      _options.end(_options.max());
    });

    _tmpl.find('.interval-custom').on('change', () => {
      _options.gap(_tmpl.find('.interval-custom').val());
      matchIntervals(true);
      if (typeof _options.relatedgap != 'undefined') {
        _options.relatedgap(_options.gap());
      }
    });

    function pushIntervalValue(newValue) {
      let _found = false;
      ko.bindingHandlers.dateRangePicker.INTERVAL_OPTIONS.forEach(interval => {
        if (interval.value == newValue) {
          _found = true;
        }
      });
      if (!_found) {
        ko.bindingHandlers.dateRangePicker.INTERVAL_OPTIONS.push({
          value: newValue,
          label: newValue
        });
        ko.bindingHandlers.dateRangePicker.EXTRA_INTERVAL_OPTIONS.push(newValue);
        _intervalOptions.push('<option value="' + newValue + '">' + newValue + '</option>');
      }
    }

    function matchIntervals(fromCustom) {
      _tmpl.find('.interval-select').val(_options.gap());
      if (_tmpl.find('.interval-select').val() == null) {
        if (fromCustom) {
          pushIntervalValue(_options.gap());
          if (bindingContext.$root.intervalOptions) {
            bindingContext.$root.intervalOptions(
              ko.bindingHandlers.dateRangePicker.INTERVAL_OPTIONS
            );
          }
        } else {
          _tmpl.find('.interval-select').val(_tmpl.find('.interval-select option:first').val());
          _options.gap(_tmpl.find('.interval-select').val());
          if (typeof _options.relatedgap != 'undefined') {
            _options.relatedgap(_options.gap());
          }
          _tmpl.find('.interval-custom').val(_options.gap());
        }
      }
    }

    _tmpl.find('.interval-select').on('change', () => {
      _options.gap(_tmpl.find('.interval-select').val());
      if (typeof _options.relatedgap != 'undefined') {
        _options.relatedgap(_options.gap());
      }
      _tmpl.find('.interval').val(_options.gap());
      _tmpl.find('.interval-custom').val(_options.gap());
    });

    function rangeHandler(isStart) {
      const startDate = moment(
        _tmpl.find('.start-date').val() + ' ' + _tmpl.find('.start-time').val(),
        DATETIME_FORMAT
      );
      const endDate = moment(
        _tmpl.find('.end-date').val() + ' ' + _tmpl.find('.end-time').val(),
        DATETIME_FORMAT
      );
      if (startDate.valueOf() > endDate.valueOf()) {
        if (isStart) {
          _tmpl.find('.end-date').val(startDate.utc().format(DATE_FORMAT));
          _tmpl.find('.end-date').datepicker('setValue', startDate.utc().format(DATE_FORMAT));
          _tmpl.find('.end-date').data('original-val', _tmpl.find('.end-date').val());
          _tmpl.find('.end-time').val(startDate.utc().format(TIME_FORMAT));
        } else {
          if (_tmpl.find('.end-date').val() === _tmpl.find('.start-date').val()) {
            _tmpl.find('.end-time').val(startDate.utc().format(TIME_FORMAT));
            _tmpl
              .find('.end-time')
              .data('timepicker')
              .setValues(startDate.format(TIME_FORMAT));
          } else {
            _tmpl.find('.end-date').val(_tmpl.find('.end-date').data('original-val'));
            _tmpl
              .find('.end-date')
              .datepicker('setValue', _tmpl.find('.end-date').data('original-val'));
          }
          // non-sticky error notification
          $.jHueNotify.notify({
            level: 'ERROR',
            message: 'The end cannot be before the starting moment'
          });
        }
      } else {
        _tmpl.find('.end-date').data('original-val', _tmpl.find('.end-date').val());
        _tmpl.find('.start-date').datepicker('hide');
        _tmpl.find('.end-date').datepicker('hide');
      }

      const _calculatedStartDate = moment(
        _tmpl.find('.start-date').val() + ' ' + _tmpl.find('.start-time').val(),
        DATETIME_FORMAT
      );
      const _calculatedEndDate = moment(
        _tmpl.find('.end-date').val() + ' ' + _tmpl.find('.end-time').val(),
        DATETIME_FORMAT
      );

      _options.min(_calculatedStartDate.format('YYYY-MM-DD[T]HH:mm:ss[Z]'));
      _options.start(_options.min());
      _options.max(_calculatedEndDate.format('YYYY-MM-DD[T]HH:mm:ss[Z]'));
      _options.end(_options.max());

      _tmpl.find('.start-date-custom').val(_options.min());
      _tmpl.find('.end-date-custom').val(_options.max());

      let _opts = [];
      // hide not useful options from interval
      if (
        _calculatedEndDate.diff(_calculatedStartDate, 'minutes') > 1 &&
        _calculatedEndDate.diff(_calculatedStartDate, 'minutes') <= 60
      ) {
        _opts = enableOptions(
          '200MILLISECONDS',
          '1SECONDS',
          '1MINUTES',
          '5MINUTES',
          '10MINUTES',
          '30MINUTES'
        );
      }
      if (
        _calculatedEndDate.diff(_calculatedStartDate, 'hours') > 1 &&
        _calculatedEndDate.diff(_calculatedStartDate, 'hours') <= 12
      ) {
        _opts = enableOptions('5MINUTES', '10MINUTES', '30MINUTES', '1HOURS', '3HOURS');
      }
      if (
        _calculatedEndDate.diff(_calculatedStartDate, 'hours') > 12 &&
        _calculatedEndDate.diff(_calculatedStartDate, 'hours') < 36
      ) {
        _opts = enableOptions('10MINUTES', '30MINUTES', '1HOURS', '3HOURS', '6HOURS', '12HOURS');
      }
      if (
        _calculatedEndDate.diff(_calculatedStartDate, 'days') > 1 &&
        _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 7
      ) {
        _opts = enableOptions('30MINUTES', '1HOURS', '3HOURS', '6HOURS', '12HOURS', '1DAYS');
      }
      if (
        _calculatedEndDate.diff(_calculatedStartDate, 'days') > 7 &&
        _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 14
      ) {
        _opts = enableOptions('3HOURS', '6HOURS', '12HOURS', '1DAYS');
      }
      if (
        _calculatedEndDate.diff(_calculatedStartDate, 'days') > 14 &&
        _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 31
      ) {
        _opts = enableOptions('12HOURS', '1DAYS', '7DAYS');
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') >= 1) {
        _opts = enableOptions('1DAYS', '7DAYS', '1MONTHS');
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 6) {
        _opts = enableOptions('1DAYS', '7DAYS', '1MONTHS', '6MONTHS');
      }
      if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 12) {
        _opts = enableOptions('7DAYS', '1MONTHS', '6MONTHS', '1YEARS', '10YEARS');
      }

      $('.interval-select').html(renderOptions(_opts));

      matchIntervals(true);
    }
  }
};
