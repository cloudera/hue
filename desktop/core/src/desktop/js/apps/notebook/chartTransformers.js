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

import HueColors from '../../utils/hueColors';
import hueUtils from '../../utils/hueUtils';

const isNotNullForCharts = val => val !== 'NULL' && val !== null;

const jQuery = $;

const pieChartTransformer = function(rawDatum) {
  let _data = [];

  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
    let _idxValue = -1;
    let _idxLabel = -1;
    rawDatum.snippet.result.meta().forEach((col, idx) => {
      if (col.name === rawDatum.snippet.chartX()) {
        _idxLabel = idx;
      }
      if (col.name === rawDatum.snippet.chartYSingle()) {
        _idxValue = idx;
      }
    });
    const colors = HueColors.cuiD3Scale();
    $(rawDatum.counts()).each((cnt, item) => {
      if (isNotNullForCharts(item[_idxValue])) {
        let val = item[_idxValue] * 1;
        if (isNaN(val)) {
          val = 0;
        }
        _data.push({
          label: hueUtils.html2text(item[_idxLabel]),
          value: val,
          color: colors[cnt % colors.length],
          obj: item
        });
      }
    });
  }

  if (rawDatum.sorting === 'asc') {
    _data.sort((a, b) => a.value - b.value);
  } else if (rawDatum.sorting === 'desc') {
    _data.sort((a, b) => b.value - a.value);
  }

  if (rawDatum.snippet.chartLimit()) {
    _data = _data.slice(0, rawDatum.snippet.chartLimit());
  }

  return _data;
};

const mapChartTransformer = function(rawDatum) {
  let _data = [];
  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
    let _idxRegion = -1;
    let _idxValue = -1;
    rawDatum.snippet.result.meta().forEach((col, idx) => {
      if (col.name === rawDatum.snippet.chartX()) {
        _idxRegion = idx;
      }
      if (col.name === rawDatum.snippet.chartYSingle()) {
        _idxValue = idx;
      }
    });

    $(rawDatum.counts()).each((cnt, item) => {
      if (isNotNullForCharts(item[_idxValue]) && isNotNullForCharts(item[_idxRegion])) {
        _data.push({
          label: item[_idxRegion],
          value: item[_idxValue],
          obj: item
        });
      }
    });
  }

  if (rawDatum.snippet.chartLimit()) {
    _data = _data.slice(0, rawDatum.snippet.chartLimit());
  }

  return _data;
};

// The leaflet map can freeze the browser with numbers outside the map
const MIN_LAT = -90;
const MAX_LAT = 90;
const MIN_LNG = -180;
const MAX_LNG = 180;

const leafletMapChartTransformer = function(rawDatum) {
  let _data = [];
  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
    let _idxLat = -1;
    let _idxLng = -1;
    let _idxLabel = -1;
    let _idxHeat = -1;
    rawDatum.snippet.result.meta().forEach((col, idx) => {
      if (col.name === rawDatum.snippet.chartX()) {
        _idxLat = idx;
      }
      if (col.name === rawDatum.snippet.chartYSingle()) {
        _idxLng = idx;
      }
      if (col.name === rawDatum.snippet.chartMapLabel()) {
        _idxLabel = idx;
      }
      if (col.name === rawDatum.snippet.chartMapHeat()) {
        _idxHeat = idx;
      }
    });
    if (rawDatum.snippet.chartMapLabel() != null) {
      $(rawDatum.counts()).each((cnt, item) => {
        if (isNotNullForCharts(item[_idxLat]) && isNotNullForCharts(item[_idxLng])) {
          _data.push({
            lat: Math.min(Math.max(MIN_LAT, item[_idxLat]), MAX_LAT),
            lng: Math.min(Math.max(MIN_LNG, item[_idxLng]), MAX_LNG),
            label: hueUtils.html2text(item[_idxLabel]),
            isHeat: rawDatum.snippet.chartMapType() === 'heat',
            intensity:
              _idxHeat > -1 ? (item[_idxHeat] * 1 != NaN ? item[_idxHeat] * 1 : null) : null,
            obj: item
          });
        }
      });
    } else {
      $(rawDatum.counts()).each((cnt, item) => {
        if (isNotNullForCharts(item[_idxLat]) && isNotNullForCharts(item[_idxLng])) {
          _data.push({
            lat: Math.min(Math.max(MIN_LAT, item[_idxLat]), MAX_LAT),
            lng: Math.min(Math.max(MIN_LNG, item[_idxLng]), MAX_LNG),
            isHeat: rawDatum.snippet.chartMapType() === 'heat',
            intensity:
              _idxHeat > -1 ? (item[_idxHeat] * 1 != NaN ? item[_idxHeat] * 1 : null) : null,
            obj: item
          });
        }
      });
    }
  }

  if (rawDatum.snippet.chartLimit()) {
    _data = _data.slice(0, rawDatum.snippet.chartLimit());
  }

  return _data;
};

const timelineChartTransformer = function(rawDatum) {
  const _datum = [];
  let _plottedSerie = 0;

  rawDatum.snippet.result.meta().forEach(meta => {
    if (rawDatum.snippet.chartYMulti().indexOf(meta.name) > -1) {
      const col = meta.name;
      let _idxValue = -1;
      let _idxLabel = -1;
      rawDatum.snippet.result.meta().forEach((icol, idx) => {
        if (icol.name === rawDatum.snippet.chartX()) {
          _idxLabel = idx;
        }
        if (icol.name === col) {
          _idxValue = idx;
        }
      });

      if (_idxValue > -1) {
        let _data = [];
        const colors = HueColors.cuiD3Scale();
        $(rawDatum.counts()).each((cnt, item) => {
          if (isNotNullForCharts(item[_idxLabel]) && isNotNullForCharts(item[_idxValue])) {
            _data.push({
              series: _plottedSerie,
              x: new Date(moment(hueUtils.html2text(item[_idxLabel])).valueOf()),
              y: item[_idxValue] * 1,
              color: colors[_plottedSerie % colors.length],
              obj: item
            });
          }
        });
        if (rawDatum.sorting === 'asc') {
          _data.sort((a, b) => {
            return a.y - b.y;
          });
        }
        if (rawDatum.sorting === 'desc') {
          _data.sort((a, b) => {
            return b.y - a.y;
          });
        }
        if (rawDatum.snippet.chartLimit()) {
          _data = _data.slice(0, rawDatum.snippet.chartLimit());
        }
        _datum.push({
          key: col,
          values: _data
        });
        _plottedSerie++;
      }
    }
  });

  return _datum;
};

const multiSerieChartTransformer = function(rawDatum) {
  let _datum = [];

  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYMulti().length > 0) {
    let _plottedSerie = 0;

    if (typeof rawDatum.snippet.chartXPivot() !== 'undefined') {
      let _idxValue = -1;
      let _idxLabel = -1;
      let _isXDate = false;

      rawDatum.snippet.result.meta().forEach((icol, idx) => {
        if (icol.name === rawDatum.snippet.chartX()) {
          _isXDate = icol.type.toUpperCase().indexOf('DATE') > -1;
          _idxLabel = idx;
        }
        if (icol.name === rawDatum.snippet.chartYSingle()) {
          _idxValue = idx;
        }
      });

      rawDatum.snippet.result.meta().forEach((meta, cnt) => {
        if (rawDatum.snippet.chartXPivot() === meta.name) {
          const _idxPivot = cnt;
          const colors = HueColors.cuiD3Scale();
          let pivotValues = $.map(rawDatum.counts(), p => {
            return p[_idxPivot];
          });
          pivotValues = pivotValues.filter((item, pos) => {
            return pivotValues.indexOf(item) === pos;
          });
          pivotValues.forEach((val, pivotCnt) => {
            const _data = [];
            $(rawDatum.counts()).each((cnt, item) => {
              if (item[_idxPivot] === val) {
                if (isNotNullForCharts(item[_idxValue]) && isNotNullForCharts(item[_idxLabel])) {
                  _data.push({
                    x: _isXDate ? moment(item[_idxLabel]) : hueUtils.html2text(item[_idxLabel]),
                    y: item[_idxValue] * 1,
                    color: colors[pivotCnt % colors.length],
                    obj: item
                  });
                }
              }
            });
            _datum.push({
              key: hueUtils.html2text(val),
              values: _data
            });
          });
        }
      });

      // fills in missing values
      let longest = 0;
      const allXValues = [];
      _datum.forEach(d => {
        d.values.forEach(val => {
          if (allXValues.indexOf(val.x) === -1) {
            allXValues.push(val.x);
          }
        });
      });

      _datum.forEach(d => {
        allXValues.forEach(val => {
          if (
            !d.values.some(item => {
              return item.x === val;
            })
          ) {
            const zeroObj = jQuery.extend({}, d.values[0]);
            zeroObj.y = 0;
            zeroObj.x = val;
            d.values.push(zeroObj);
          }
        });
        if (d.values.length > longest) {
          longest = d.values.length;
        }
      });

      // this is to avoid D3 js errors when the data the user is trying to display is bogus
      if (allXValues.length < longest) {
        _datum.forEach(d => {
          for (let i = d.values.length; i < longest; i++) {
            const zeroObj = jQuery.extend({}, d.values[0]);
            zeroObj.y = 0;
            zeroObj.x = '';
            d.values.push(zeroObj);
          }
        });
      }

      if (rawDatum.snippet.chartLimit()) {
        _datum = _datum.slice(0, rawDatum.snippet.chartLimit());
      }

      if (rawDatum.sorting === 'desc') {
        _datum.forEach(d => {
          d.values.sort((a, b) => {
            if (a.x > b.x) {
              return -1;
            }
            if (a.x < b.x) {
              return 1;
            }
            return 0;
          });
        });
      } else {
        _datum.forEach(d => {
          d.values.sort((a, b) => {
            if (a.x > b.x) {
              return 1;
            }
            if (a.x < b.x) {
              return -1;
            }
            return 0;
          });
        });
      }
    } else {
      rawDatum.snippet.result.meta().forEach(meta => {
        if (rawDatum.snippet.chartYMulti().indexOf(meta.name) > -1) {
          const col = meta.name;
          let _idxValue = -1;
          let _idxLabel = -1;
          let _isXDate = false;
          rawDatum.snippet.result.meta().forEach((icol, idx) => {
            if (icol.name === rawDatum.snippet.chartX()) {
              _isXDate = icol.type.toUpperCase().indexOf('DATE') > -1;
              _idxLabel = idx;
            }
            if (icol.name === col) {
              _idxValue = idx;
            }
          });

          if (_idxValue > -1) {
            let _data = [];
            const colors = HueColors.cuiD3Scale();
            $(rawDatum.counts()).each((cnt, item) => {
              if (isNotNullForCharts(item[_idxValue]) && isNotNullForCharts(item[_idxLabel])) {
                _data.push({
                  series: _plottedSerie,
                  x: _isXDate ? moment(item[_idxLabel]) : hueUtils.html2text(item[_idxLabel]),
                  y: item[_idxValue] * 1,
                  color: colors[cnt % colors.length],
                  obj: item
                });
              }
            });
            if (rawDatum.sorting === 'asc') {
              _data.sort((a, b) => {
                return a.y - b.y;
              });
            }
            if (rawDatum.sorting === 'desc') {
              _data.sort((a, b) => {
                return b.y - a.y;
              });
            }
            if (rawDatum.snippet.chartLimit()) {
              _data = _data.slice(0, rawDatum.snippet.chartLimit());
            }
            _datum.push({
              key: col,
              values: _data
            });
            _plottedSerie++;
          }
        }
      });
    }
  }
  return _datum;
};

const scatterChartTransformer = function(rawDatum) {
  const datum = {};

  if (rawDatum.snippet.chartX() != null && rawDatum.snippet.chartYSingle() != null) {
    let idxX = -1;
    let idxY = -1;
    let idxSize = -1;
    let idxGroup = -1;
    rawDatum.snippet.result.meta().forEach((icol, idx) => {
      if (icol.name === rawDatum.snippet.chartX()) {
        idxX = idx;
      }
      if (icol.name === rawDatum.snippet.chartYSingle()) {
        idxY = idx;
      }
      if (icol.name === rawDatum.snippet.chartScatterSize()) {
        idxSize = idx;
      }
      if (icol.name === rawDatum.snippet.chartScatterGroup()) {
        idxGroup = idx;
      }
    });

    if (idxX > -1 && idxY > -1) {
      const createAndAddToArray = function(key, item) {
        if (!datum[key]) {
          datum[key] = [];
        }
        if (isNotNullForCharts(item[idxX]) && isNotNullForCharts(item[idxY])) {
          datum[key].push({
            x: item[idxX],
            y: item[idxY],
            shape: 'circle',
            size: idxSize > -1 ? item[idxSize] : 100,
            obj: item
          });
        }
      };

      if (idxGroup > -1) {
        $(rawDatum.counts()).each((cnt, item) => {
          createAndAddToArray(item[idxGroup], item);
        });
      } else {
        $(rawDatum.counts()).each((cnt, item) => {
          createAndAddToArray('distro', item);
        });
      }
    }
  }

  const returndDatum = [];

  Object.keys(datum).forEach(key => {
    returndDatum.push({
      key: key,
      values: rawDatum.snippet.chartLimit()
        ? datum[key].slice(0, rawDatum.snippet.chartLimit())
        : datum[key]
    });
  });

  return returndDatum;
};

export default {
  pie: pieChartTransformer,
  map: mapChartTransformer,
  leafletMap: leafletMapChartTransformer,
  timeline: timelineChartTransformer,
  multiSerie: multiSerieChartTransformer,
  scatter: scatterChartTransformer
};
