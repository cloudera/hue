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
import d3v3 from 'd3v3';
import nv from 'ext/nv.d3.1.1.15b.custom';

import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const MS = 1;
const SECOND_MS = 1000 * MS;
const MINUTE_MS = SECOND_MS * 60;
const HOUR_MS = MINUTE_MS * 60;
const DAY_MS = HOUR_MS * 24;
const WEEK_MS = DAY_MS * 7;
const MONTH_MS = DAY_MS * 30.5;
const YEAR_MS = DAY_MS * 365;

const addLegend = element => {
  const $el = d3v3.select($(element)[0]);
  const $div = $el.select('div');
  if (!$div.size()) {
    $el
      .append('div')
      .style('position', 'absolute')
      .style('overflow', 'auto')
      .style('top', '20px')
      .style('right', '0px')
      .style('width', '175px')
      .style('height', 'calc(100% - 20px)')
      .append('svg');
  } else {
    $div.append('svg');
  }
};

const barChartBuilder = (element, options, isTimeline) => {
  let _datum = options.transformer(options.datum, isTimeline);
  $(element).height(300);

  const _isPivot = options.isPivot != null ? options.isPivot : false;

  if ($(element).find('svg').length > 0 && (_datum.length === 0 || _datum[0].values.length === 0)) {
    $(element)
      .find('svg')
      .remove();
  }

  if (_datum.length > 0 && _datum[0].values.length > 0 && isNaN(_datum[0].values[0].y)) {
    _datum = [];
    $(element)
      .find('svg')
      .remove();
  }

  nv.addGraph(() => {
    if (
      $(element).find('svg').length > 0 &&
      $(element).find('.nv-discreteBarWithAxes').length > 0
    ) {
      $(element)
        .find('svg')
        .empty();
    }
    const _chart = nv.models.multiBarWithBrushChart();
    _chart.noData(_datum.message || I18n('No Data Available.'));
    if (_datum.length > 0) {
      $(element).data('chart_type', 'multibar_brush');
    }
    _chart.onSelectRange((from, to) => {
      huePubSub.publish('charts.state', { updating: true });
      options.onSelectRange(from, to);
    });
    _chart.multibar.dispatch.on('elementClick', d => {
      if (typeof options.onClick != 'undefined') {
        huePubSub.publish('charts.state', { updating: true });
        options.onClick(d.point);
      }
    });
    _chart.onStateChange(options.onStateChange);
    if (options.selectedSerie) {
      _chart.onLegendChange(state => {
        const selectedSerie = options.selectedSerie();
        const _datum = d3v3.select($(element).find('svg')[0]).datum();
        for (let i = 0; i < state.disabled.length; i++) {
          selectedSerie[_datum[i].key] = !state.disabled[i];
        }
        options.selectedSerie(selectedSerie);
      });
    }
    _chart.multibar.hideable(true);
    _chart.multibar.stacked(typeof options.stacked != 'undefined' ? options.stacked : false);
    if (isTimeline) {
      _chart.convert = function(d) {
        return isTimeline ? new Date(moment(d[0].obj.from).valueOf()) : parseFloat(d);
      };
      _chart.staggerLabels(false);
      _chart.tooltipContent(values => {
        return values.map(value => {
          value = JSON.parse(JSON.stringify(value));
          value.x = moment(value.x)
            .utc()
            .format('YYYY-MM-DD HH:mm:ss');
          value.y = _chart.yAxis.tickFormat()(value.y);
          return value;
        });
      });
      _chart.xAxis.tickFormat(multi(_chart.xAxis));
      _chart.multibar.stacked(typeof options.stacked != 'undefined' ? options.stacked : false);
      _chart.onChartUpdate(() => {
        _d3.selectAll('g.nv-x.nv-axis g text').each(function(d) {
          insertLinebreaks(_chart, d, this);
        });
      });
    } else if (numeric(_datum)) {
      _chart.xAxis.showMaxMin(false).tickFormat(d3v3.format(',0f'));
      _chart.staggerLabels(false);
    } else if (!_isPivot) {
      _chart.multibar.barColor(nv.utils.defaultColor());
      _chart.staggerLabels(true);
    }
    if ($(element).width() < 300 && typeof _chart.showLegend != 'undefined') {
      _chart.showLegend(false);
    }
    _chart.transitionDuration(0);

    _chart.yAxis.tickFormat(d3v3.format('s'));

    $(element).data('chart', _chart);
    handleSelection(_chart, options, _datum);
    const _d3 =
      $(element).find('svg').length > 0
        ? d3v3.select($(element).find('svg')[0])
        : d3v3.select($(element)[0]).insert('svg', ':first-child');
    if ($(element).find('svg').length < 2) {
      addLegend(element);
    }
    _d3
      .datum(_datum)
      .transition()
      .duration(150)
      .each('end', () => {
        if (options.onComplete != null) {
          options.onComplete();
        }
        if (isTimeline) {
          _d3.selectAll('g.nv-x.nv-axis g text').each(function(d) {
            insertLinebreaks(_chart, d, this);
          });
        }
        if (options.slot && _chart.recommendedTicks) {
          options.slot(_chart.recommendedTicks());
        }
      })
      .call(_chart);

    if (!options.skipWindowResize) {
      let _resizeTimeout = -1;
      nv.utils.windowResize(() => {
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(() => {
          _chart.update();
        }, 200);
      });
    }

    $(element).on('forceUpdate', () => {
      _chart.update();
    });

    return _chart;
  });
};

const handleSelection = (_chart, _options, _datum) => {
  let i, j;
  if (_options.selectedSerie) {
    const selectedSerie = _options.selectedSerie();
    let enabledCount = 0;
    for (i = 0; i < _datum.length; i++) {
      if (!selectedSerie[_datum[i].key]) {
        _datum[i].disabled = true;
      } else {
        enabledCount++;
      }
    }
    if (enabledCount === 0) {
      // Get the 5 series with the most non zero elements on x axis & total value.
      const stats = {};
      for (i = 0; i < _datum.length; i++) {
        if (!stats[_datum[i].key]) {
          stats[_datum[i].key] = { count: 0, total: 0 };
        }
        for (j = 0; j < _datum[i].values.length; j++) {
          stats[_datum[i].key].count += Math.min(_datum[i].values[j].y, 1);
          stats[_datum[i].key].total += _datum[i].values[j].y;
        }
      }
      const aStats = Object.keys(stats).map(key => {
        return { key: key, stat: stats[key] };
      });
      aStats.sort((a, b) => {
        return a.stat.count - b.stat.count || a.stat.total - b.stat.total;
      });
      for (i = aStats.length - 1; i >= Math.max(aStats.length - 5, 0); i--) {
        _datum[i].disabled = false;
        selectedSerie[_datum[i].key] = true;
      }
    }
  }
  const _isPivot = _options.isPivot != null ? _options.isPivot : false;
  const _hideSelection =
    typeof _options.hideSelection !== 'undefined'
      ? typeof _options.hideSelection === 'function'
        ? _options.hideSelection()
        : _options.hideSelection
      : false;
  let _enableSelection =
    typeof _options.enableSelection !== 'undefined'
      ? typeof _options.enableSelection === 'function'
        ? _options.enableSelection()
        : _options.enableSelection
      : true;
  _enableSelection = _enableSelection && numeric(_datum);
  const _hideStacked =
    _options.hideStacked !== null
      ? typeof _options.hideStacked === 'function'
        ? _options.hideStacked()
        : _options.hideStacked
      : false;
  const _displayValuesInLegend =
    _options.displayValuesInLegend !== null
      ? typeof _options.displayValuesInLegend === 'function'
        ? _options.displayValuesInLegend()
        : _options.displayValuesInLegend
      : false;
  const fHideSelection = _isPivot || _hideSelection ? _chart.hideSelection : _chart.showSelection;
  if (fHideSelection) {
    fHideSelection.call(_chart);
  }
  const fEnableSelection = _enableSelection ? _chart.enableSelection : _chart.disableSelection;
  if (fEnableSelection) {
    fEnableSelection.call(_chart);
  }
  const fHideStacked = _hideStacked ? _chart.hideStacked : _chart.showStacked;
  if (fHideStacked) {
    fHideStacked.call(_chart);
  }
  if (_chart.displayValuesInLegend) {
    _chart.displayValuesInLegend(_displayValuesInLegend);
  }
  if (_chart.selectBars) {
    const _field = typeof _options.field == 'function' ? _options.field() : _options.field;
    let bHasSelection = false;
    $.each(_options.fqs ? _options.fqs() : [], (cnt, item) => {
      if (item.id() === _options.datum.widget_id) {
        if (item.field() === _field) {
          if (item.properties && typeof item.properties === 'function') {
            bHasSelection = true;
            _chart.selectBars({
              singleValues: $.map(item.filter(), it => {
                return it.value();
              }),
              rangeValues: $.map(item.properties(), it => {
                return { from: it.from(), to: it.to() };
              })
            });
          } else {
            bHasSelection = true;
            _chart.selectBars(
              $.map(item.filter(), it => {
                return it.value();
              })
            );
          }
        }
        if (Array.isArray(item.field())) {
          bHasSelection = true;
          _chart.selectBars({
            field: item.field(),
            selected: $.map(item.filter(), it => {
              return { values: it.value() };
            })
          });
        }
      }
    });
    if (!bHasSelection) {
      _chart.selectBars({ field: '', selected: [] });
    }
  }
};

const insertLinebreaks = (_chart, d, ref) => {
  const _el = d3v3.select(ref);
  const _mom = moment(d);
  if (_mom != null && _mom.isValid()) {
    const _words = _el.text().split(' ');
    _el.text('');
    for (let i = 0; i < _words.length; i++) {
      const tspan = _el.append('tspan').text(_words[i]);
      if (i > 0) {
        tspan.attr('x', 0).attr('dy', '15');
      }
    }
  }
};

const lineChartBuilder = (element, options, isTimeline) => {
  let _datum = options.transformer(options.datum);
  $(element).height(300);
  if ($(element).find('svg').length > 0 && (_datum.length === 0 || _datum[0].values.length === 0)) {
    $(element)
      .find('svg')
      .empty();
  }
  if (
    _datum.length > 0 &&
    _datum[0].values.length > 0 &&
    (isNaN(_datum[0].values[0].x) || isNaN(_datum[0].values[0].y))
  ) {
    _datum = [];
    $(element)
      .find('svg')
      .empty();
  }

  if ($(element).is(':visible')) {
    nv.addGraph(() => {
      const _chart = nv.models.lineWithBrushChart();
      _chart.noData(_datum.message || I18n('No Data Available.'));
      $(element).data('chart', _chart);
      _chart.transitionDuration(0);
      _chart.convert = function(d) {
        return isTimeline ? new Date(moment(d[0].obj.from).valueOf()) : parseFloat(d);
      };
      if (options.showControls != null) {
        _chart.showControls(false);
      }
      _chart.onSelectRange((from, to) => {
        huePubSub.publish('charts.state', { updating: true });
        options.onSelectRange(
          $.isNumeric(from) && isTimeline ? new Date(moment(from).valueOf()) : parseInt(from),
          $.isNumeric(to) && isTimeline ? new Date(moment(to).valueOf()) : parseInt(to)
        ); // FIXME when using pdouble we should not parseInt.
      });
      if (options.selectedSerie) {
        _chart.onLegendChange(state => {
          const selectedSerie = options.selectedSerie();
          const _datum = d3v3.select($(element).find('svg')[0]).datum();
          for (let i = 0; i < state.disabled.length; i++) {
            selectedSerie[_datum[i].key] = !state.disabled[i];
          }
          options.selectedSerie(selectedSerie);
        });
      }
      _chart.xAxis.showMaxMin(false);
      if (isTimeline) {
        _chart.xScale(d3v3.time.scale.utc());
        _chart.tooltipContent(values => {
          return values.map(value => {
            value = JSON.parse(JSON.stringify(value));
            value.x = moment(value.x)
              .utc()
              .format('YYYY-MM-DD HH:mm:ss');
            value.y = _chart.yAxis.tickFormat()(value.y);
            return value;
          });
        });
        _chart.xAxis.tickFormat(multi(_chart.xAxis, _chart));
        _chart.onChartUpdate(() => {
          _d3.selectAll('g.nv-x.nv-axis g text').each(function(d) {
            insertLinebreaks(_chart, d, this);
          });
        });
      }

      _chart.yAxis.tickFormat(d3v3.format('s'));
      handleSelection(_chart, options, _datum);
      const _d3 =
        $(element).find('svg').length > 0
          ? d3v3.select($(element).find('svg')[0])
          : d3v3.select($(element)[0]).insert('svg', ':first-child');
      if ($(element).find('svg').length < 2) {
        addLegend(element);
      }
      _d3
        .datum(_datum)
        .transition()
        .duration(150)
        .each('end', () => {
          if (options.onComplete != null) {
            options.onComplete();
          }
          if (isTimeline) {
            _d3.selectAll('g.nv-x.nv-axis g text').each(function(d) {
              insertLinebreaks(_chart, d, this);
            });
          }
        })
        .call(_chart);

      let _resizeTimeout = -1;
      nv.utils.windowResize(() => {
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(() => {
          _chart.update();
        }, 200);
      });

      $(element).on('forceUpdate', () => {
        _chart.update();
      });
      _chart.lines.dispatch.on('elementClick', d => {
        if (typeof options.onClick != 'undefined') {
          huePubSub.publish('charts.state', { updating: true });
          options.onClick(d.point);
        }
      });

      return _chart;
    });
  }
};

const multi = xAxis => {
  let previous = new Date(9999, 11, 31);
  return d3v3.time.format.utc.multi([
    [
      '%H:%M:%S %Y-%m-%d',
      function(d) {
        const domain = xAxis.domain();
        const result =
          (previous > d || d === domain[0]) &&
          moment(d)
            .utc()
            .seconds();
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%H:%M %Y-%m-%d',
      function(d) {
        const domain = xAxis.domain();
        const result = previous > d || d === domain[0];
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%S %H:%M',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          moment(previous)
            .utc()
            .minutes() !==
            moment(d)
              .utc()
              .minutes() && previousDiff < MINUTE_MS;
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%S',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          moment(previous)
            .utc()
            .seconds() !==
            moment(d)
              .utc()
              .seconds() && previousDiff < MINUTE_MS;
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%H:%M:%S %Y-%m-%d',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          moment(previous)
            .utc()
            .date() !==
            moment(d)
              .utc()
              .date() &&
          previousDiff < WEEK_MS &&
          moment(d)
            .utc()
            .seconds();
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%H:%M %Y-%m-%d',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          moment(previous)
            .utc()
            .date() !==
            moment(d)
              .utc()
              .date() && previousDiff < WEEK_MS;
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%H:%M:%S',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          (moment(previous)
            .utc()
            .hours() !==
            moment(d)
              .utc()
              .hours() ||
            moment(previous)
              .utc()
              .minutes() !==
              moment(d)
                .utc()
                .minutes()) &&
          previousDiff < WEEK_MS &&
          moment(d)
            .utc()
            .seconds();
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%H:%M',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          (moment(previous)
            .utc()
            .hours() !==
            moment(d)
              .utc()
              .hours() ||
            moment(previous)
              .utc()
              .minutes() !==
              moment(d)
                .utc()
                .minutes()) &&
          previousDiff < WEEK_MS;
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%d %Y-%m',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          moment(previous)
            .utc()
            .months() !==
            moment(d)
              .utc()
              .months() && previousDiff < MONTH_MS;
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%d',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          moment(previous)
            .utc()
            .date() !==
            moment(d)
              .utc()
              .date() && previousDiff < MONTH_MS;
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%m %Y',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          moment(previous)
            .utc()
            .years() !==
            moment(d)
              .utc()
              .years() && previousDiff < YEAR_MS;
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%m',
      function(d) {
        const previousDiff = Math.abs(d - previous);
        const result =
          moment(previous)
            .utc()
            .months() !==
            moment(d)
              .utc()
              .months() && previousDiff < YEAR_MS;
        if (result) {
          previous = d;
        }
        return result;
      }
    ],
    [
      '%Y',
      function(d) {
        previous = d;
        return true;
      }
    ]
  ]);
};

const numeric = _datum => {
  for (let j = 0; j < _datum.length; j++) {
    for (let i = 0; i < _datum[j].values.length; i++) {
      if (isNaN(_datum[j].values[i].x * 1)) {
        return false;
      }
    }
  }
  return true;
};

export { barChartBuilder, handleSelection, insertLinebreaks, lineChartBuilder, numeric };
