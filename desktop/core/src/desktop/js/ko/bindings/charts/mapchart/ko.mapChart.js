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
import nv from 'ext/nv.d3.1.1.15b.custom';

import Datamap from './datamap';
import huePubSub from 'utils/huePubSub';
import HueColors from 'utils/hueColors';
import HueGeo from 'utils/hueGeo';

ko.bindingHandlers.mapChart = {
  render: function(element, valueAccessor) {
    const _options = valueAccessor();

    const $element = $(element);
    window.clearTimeout($element.data('drawThrottle'));

    const timeout = window.setTimeout(() => {
      $element.empty();

      $element.css('position', 'relative');
      $element.css('marginLeft', 'auto');
      $element.css('marginRight', 'auto');

      if (typeof _options.maxWidth != 'undefined') {
        const _max = _options.maxWidth * 1;
        $element.width(Math.min($element.parent().width(), _max));
      } else {
        $element.width($element.parent().width() - 10);
      }

      $element.height($element.width() / 2.23);

      const _scope =
        typeof _options.data.scope != 'undefined' ? String(_options.data.scope) : 'world';
      const _data = _options.transformer(_options.data);
      let _is2d = false;
      const _pivotCategories = [];
      let _maxWeight = 0;

      function comparePivotValues(a, b) {
        if (a.count < b.count) {
          return 1;
        }
        if (a.count > b.count) {
          return -1;
        }
        return 0;
      }

      $(_data).each((cnt, item) => {
        if (item.value > _maxWeight) {
          _maxWeight = item.value;
        }
        if (item.obj.is2d) {
          _is2d = true;
        }
        if (item.obj.pivot && item.obj.pivot.length > 0) {
          item.obj.pivot.forEach(piv => {
            let _category = null;
            _pivotCategories.forEach(category => {
              if (category.value === piv.value) {
                _category = category;
                if (piv.count > _category.count) {
                  _category.count = piv.count;
                }
              }
            });

            if (_category == null) {
              _category = {
                value: piv.value,
                count: -1
              };
              _pivotCategories.push(_category);
            }
          });
        }
      });

      _pivotCategories.sort(comparePivotValues);

      const _chunk = _maxWeight / _data.length;
      const _mapdata = {};
      const _maphovers = {};
      const _fills = {};
      const _legend = [];

      const _noncountries = [];

      if (_options.isScale) {
        _fills['defaultFill'] = HueColors.WHITE;
        const _colors = _is2d
          ? HueColors.d3Scale()
          : HueColors.scale(HueColors.LIGHT_BLUE, HueColors.DARK_BLUE, _data.length);
        $(_colors).each((cnt, item) => {
          _fills['fill_' + cnt] = item;
        });

        const getHighestCategoryValue = (cnt, item) => {
          let _cat = '';
          let _max = -1;
          if (item.obj.pivot && item.obj.pivot.length > 0) {
            item.obj.pivot.forEach(piv => {
              if (piv.count > _max) {
                _max = piv.count;
                _cat = piv.value;
              }
            });
          }
          let _found = cnt;
          if (_cat !== '') {
            _pivotCategories.forEach((cat, i) => {
              if (cat.value === _cat) {
                _found = i;
              }
            });
          }
          return {
            idx: _found,
            cat: _cat
          };
        };

        const addToLegend = category => {
          let _found = false;
          _legend.forEach(lg => {
            if (lg.cat === category.cat) {
              _found = true;
            }
          });
          if (!_found) {
            _legend.push(category);
          }
        };

        $(_data).each((cnt, item) => {
          addToLegend(getHighestCategoryValue(cnt, item));
          let _place = typeof item.label == 'string' ? item.label.toUpperCase() : item.label;
          if (_place != null) {
            if (
              _scope !== 'world' &&
              _scope !== 'usa' &&
              _scope !== 'europe' &&
              _place.indexOf('.') === -1
            ) {
              _place = HueGeo.getISOAlpha2(_scope) + '.' + _place;
            }
            if ((_scope === 'world' || _scope === 'europe') && _place.length === 2) {
              _place = HueGeo.getISOAlpha3(_place);
            }
            _mapdata[_place] = {
              fillKey:
                'fill_' +
                (_is2d
                  ? getHighestCategoryValue(cnt, item).idx
                  : Math.ceil(item.value / _chunk) - 1),
              id: _place,
              cat: item.obj.cat,
              value: item.obj.values ? item.obj.values : item.obj.value,
              pivot: _is2d ? item.obj.pivot : [],
              selected: item.obj.selected,
              fields: item.obj.fields ? item.obj.fields : null
            };
            _maphovers[_place] = item.value;
          } else {
            _noncountries.push(item);
          }
        });
      } else {
        _fills['defaultFill'] = HueColors.LIGHT_BLUE;
        _fills['selected'] = HueColors.DARK_BLUE;
        $(_data).each((cnt, item) => {
          let _place = item.label.toUpperCase();
          if (_place != null) {
            if (
              _scope !== 'world' &&
              _scope !== 'usa' &&
              _scope !== 'europe' &&
              _place.indexOf('.') === -1
            ) {
              _place = HueGeo.getISOAlpha2(_scope) + '.' + _place;
            }
            if ((_scope === 'world' || _scope === 'europe') && _place.length === 2) {
              _place = HueGeo.getISOAlpha3(_place);
            }
            _mapdata[_place] = {
              fillKey: 'selected',
              id: _place,
              cat: item.obj.cat,
              value: item.obj.values ? item.obj.values : item.obj.value,
              pivot: [],
              selected: item.obj.selected,
              fields: item.obj.fields ? item.obj.fields : null
            };
            _maphovers[_place] = item.value;
          } else {
            _noncountries.push(item);
          }
        });
      }

      let _map = null;

      function createDatamap(element, options, fills, mapData, nonCountries, mapHovers) {
        _map = new Datamap({
          element: element,
          fills: fills,
          scope: _scope,
          data: mapData,
          legendData: _legend,
          onClick: function(data) {
            if (typeof options.onClick != 'undefined') {
              huePubSub.publish('charts.state', { updating: true });
              options.onClick(data);
            }
          },
          done: function() {
            const _bubbles = [];
            if (options.enableGeocoding) {
              $(nonCountries).each((cnt, item) => {
                HueGeo.getCityCoordinates(item.label, (lat, lng) => {
                  _bubbles.push({
                    fillKey: 'selected',
                    label: item.label,
                    value: item.value,
                    radius: 4,
                    latitude: lat,
                    longitude: lng
                  });
                  _map.bubbles(_bubbles, {
                    popupTemplate: function(geo, data) {
                      return (
                        '<div class="hoverinfo" style="text-align: center"><strong>' +
                        data.label +
                        '</strong><br/>' +
                        item.value +
                        '</div>'
                      );
                    }
                  });
                });
              });
            }
          },
          geographyConfig: {
            hideAntarctica: true,
            borderWidth: 1,
            borderColor: HueColors.DARK_BLUE,
            highlightOnHover: true,
            highlightFillColor: HueColors.DARK_BLUE,
            highlightBorderColor: HueColors.BLUE,
            selectedFillColor: HueColors.DARKER_BLUE,
            selectedBorderColor: HueColors.DARKER_BLUE,
            popupTemplate: function(geography, data) {
              let _hover = '';
              if (data != null) {
                _hover = '<br/>';
                if (data.pivot && data.pivot.length > 0) {
                  data.pivot.sort(comparePivotValues);
                  data.pivot.forEach((piv, cnt) => {
                    _hover +=
                      (cnt === 0 ? '<strong>' : '') +
                      piv.value +
                      ': ' +
                      piv.count +
                      (cnt === 0 ? '</strong>' : '') +
                      '<br/>';
                  });
                } else {
                  _hover += mapHovers[data.id];
                }
              }
              return (
                '<div class="hoverinfo" style="text-align: center"><strong>' +
                geography.properties.name +
                '</strong>' +
                _hover +
                '</div>'
              );
            }
          }
        });
        if (options.onComplete != null) {
          options.onComplete();
        }
        if (_is2d) {
          _map.legend();
        }
      }

      createDatamap(element, _options, _fills, _mapdata, _noncountries, _maphovers);

      const _parentSelector =
        typeof _options.parentSelector != 'undefined' ? _options.parentSelector : '.card-widget';

      $element.parents(_parentSelector).one('resize', () => {
        ko.bindingHandlers.mapChart.render(element, valueAccessor);
      });

      let _resizeTimeout = -1;
      nv.utils.windowResize(() => {
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(() => {
          ko.bindingHandlers.mapChart.render(element, valueAccessor);
        }, 200);
      });

      huePubSub.publish('charts.state');
    }, 50);

    $element.data('drawThrottle', timeout);
  },
  init: function(element, valueAccessor) {
    ko.bindingHandlers.mapChart.render(element, valueAccessor);
  },
  update: function(element, valueAccessor, allBindingsAccessor) {
    if (typeof allBindingsAccessor().mapChart.visible != 'undefined') {
      if (
        (typeof allBindingsAccessor().mapChart.visible == 'boolean' &&
          allBindingsAccessor().mapChart.visible) ||
        (typeof allBindingsAccessor().mapChart.visible == 'function' &&
          allBindingsAccessor().mapChart.visible())
      ) {
        $(element).show();
        ko.bindingHandlers.mapChart.render(element, valueAccessor);
      } else {
        $(element).hide();
      }
    } else {
      ko.bindingHandlers.mapChart.render(element, valueAccessor);
    }
  }
};
