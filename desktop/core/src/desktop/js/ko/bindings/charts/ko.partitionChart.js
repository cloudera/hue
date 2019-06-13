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
import ko from 'knockout';

import HueColors from 'utils/hueColors';
import huePubSub from 'utils/huePubSub';

ko.bindingHandlers.partitionChart = {
  render: function(element, valueAccessor) {
    huePubSub.publish('charts.state');
    const MIN_HEIGHT_FOR_TOOLTIP = 24;

    const _options = valueAccessor();
    const _data = _options.transformer(valueAccessor().datum);

    const _w = $(element).width(),
      _h = 300,
      _x = d3v3.scale.linear().range([0, _w]),
      _y = d3v3.scale.linear().range([0, _h]);

    if ($(element).find('svg').length > 0) {
      $(element)
        .find('svg')
        .empty();
    }

    const _tip = d3v3
      .tip()
      .attr('class', 'd3-tip')
      .html(d => {
        if (d.depth === 0) {
          return _options.tooltip || '';
        } else if (d.depth > 0 && d.depth < 2) {
          return d.name + ' (' + d.value + ')';
        } else {
          return d.parent.name + ' - ' + d.name + ' (' + d.value + ')';
        }
      })
      .offset([-12, 0]);

    const _svg =
      $(element).find('svg.tip').length > 0
        ? d3v3.select($(element).find('svg.tip')[0])
        : d3v3.select($(element)[0]).append('svg');
    _svg.attr('class', 'tip').style('height', '0px');
    _svg.call(_tip);

    const _vis =
      $(element).find('svg').length > 0
        ? d3v3.select($(element).find('svg')[0])
        : d3v3.select($(element)[0]).append('svg');
    _vis
      .attr('class', 'partitionChart')
      .style('width', _w + 'px')
      .style('height', _h + 'px')
      .attr('width', _w)
      .attr('height', _h);

    const _partition = d3v3.layout.partition().value(d => {
      return d.size;
    });

    const g = _vis
      .selectAll('g')
      .data(_partition.nodes(_data))
      .enter()
      .append('svg:g')
      .attr('transform', d => {
        return 'translate(' + _x(d.y) + ',' + _y(d.x) + ')';
      })
      .on('mouseover', function(d, i) {
        if (
          element.querySelectorAll('rect')[i].getBBox().height < MIN_HEIGHT_FOR_TOOLTIP ||
          d.depth === 0
        ) {
          _tip.attr('class', 'd3-tip').show(d);
        }

        if (typeof this.__data__.parent === 'undefined') {
          return;
        }
        d3v3
          .select(this)
          .select('rect')
          .classed('mouseover', true);
      })
      .on('mouseout', function(d, i) {
        if (
          element.querySelectorAll('rect')[i].getBBox().height < MIN_HEIGHT_FOR_TOOLTIP ||
          d.depth === 0
        ) {
          _tip.attr('class', 'd3-tip').show(d);
          _tip.hide();
        }
        d3v3
          .select(this)
          .select('rect')
          .classed('mouseover', false);
      });

    if (typeof _options.zoomable == 'undefined' || _options.zoomable) {
      g.on('click', click).on('dblclick', d => {
        if (typeof _options.onClick != 'undefined' && d.depth > 0) {
          huePubSub.publish('charts.state', { updating: true });
          _options.onClick(d);
        }
      });
    } else {
      g.on('click', d => {
        if (typeof _options.onClick != 'undefined' && d.depth > 0) {
          huePubSub.publish('charts.state', { updating: true });
          _options.onClick(d);
        }
      });
    }

    let _kx = _w / _data.dx,
      _ky = _h / 1;

    const _colors = [HueColors.cuiD3Scale('gray')[0]];

    g.append('svg:rect')
      .attr('width', _data.dy * _kx)
      .attr('height', d => {
        return d.dx * _ky;
      })
      .attr('class', d => {
        return d.children ? 'parent' : 'child';
      })
      .attr('stroke', () => {
        return HueColors.cuiD3Scale('gray')[3];
      })
      .attr('fill', d => {
        let _fill = _colors[d.depth] || _colors[_colors.length - 1];
        if (d.obj && _options.fqs) {
          $.each(_options.fqs(), (cnt, item) => {
            $.each(item.filter(), (icnt, filter) => {
              if (JSON.stringify(filter.value()) === JSON.stringify(d.obj.fq_values)) {
                _fill = HueColors.cuiD3Scale('gray')[3];
              }
            });
          });
        }
        return _fill;
      });

    g.append('svg:text')
      .attr('transform', transform)
      .attr('dy', '.35em')
      .style('opacity', d => {
        return d.dx * _ky > 12 ? 1 : 0;
      })
      .text(d => {
        if (d.depth < 2) {
          return d.name + ' (' + d.value + ')';
        } else {
          return d.parent.name + ' - ' + d.name + ' (' + d.value + ')';
        }
      });

    d3v3.select(window).on('click', () => {
      click(_data);
    });

    function click(d) {
      _tip.hide();
      if (!d.children) {
        return;
      }

      _kx = (d.y ? _w - 40 : _w) / (1 - d.y);
      _ky = _h / d.dx;
      _x.domain([d.y, 1]).range([d.y ? 40 : 0, _w]);
      _y.domain([d.x, d.x + d.dx]);

      const t = g
        .transition()
        .delay(250)
        .duration(d3v3.event.altKey ? 7500 : 750)
        .attr('transform', d => {
          return 'translate(' + _x(d.y) + ',' + _y(d.x) + ')';
        });

      t.select('rect')
        .attr('width', d.dy * _kx)
        .attr('height', d => {
          return d.dx * _ky;
        });

      t.select('text')
        .attr('transform', transform)
        .style('opacity', d => {
          return d.dx * _ky > 12 ? 1 : 0;
        });

      d3v3.event.stopPropagation();
    }

    function transform(d) {
      return 'translate(8,' + (d.dx * _ky) / 2 + ')';
    }

    if (_options.onComplete) {
      _options.onComplete();
    }
  },
  init: function(element, valueAccessor) {
    ko.bindingHandlers.partitionChart.render(element, valueAccessor);
  },
  update: function(element, valueAccessor) {
    ko.bindingHandlers.partitionChart.render(element, valueAccessor);
  }
};
