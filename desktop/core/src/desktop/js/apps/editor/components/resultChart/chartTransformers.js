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

import HueColors from 'utils/hueColors';
import html2text from 'utils/html/html2text';
import { CHART_MAP_TYPE, CHART_SORTING } from 'apps/editor/components/resultChart/ko.resultChart';

// The leaflet map can freeze the browser with numbers outside the map
const MIN_LAT = -90;
const MAX_LAT = 90;
const MIN_LNG = -180;
const MAX_LNG = 180;

const isNotNullForCharts = val => val !== 'NULL' && val !== null;

export const pieChartTransformer = function (rawDatum) {
  let data = [];

  if (rawDatum.chartX() != null && rawDatum.chartYSingle() != null) {
    let valueIndex = -1;
    let labelIndex = -1;
    rawDatum.meta().some((col, index) => {
      if (col.name === rawDatum.chartX()) {
        labelIndex = index;
      }
      if (col.name === rawDatum.chartYSingle()) {
        valueIndex = index;
      }
      return valueIndex !== -1 && labelIndex !== -1;
    });
    const colors = HueColors.cuiD3Scale();
    rawDatum.data().forEach((item, index) => {
      if (isNotNullForCharts(item[valueIndex])) {
        let val = item[valueIndex] * 1;
        if (isNaN(val)) {
          val = 0;
        }
        data.push({
          label: html2text(item[labelIndex]),
          value: val,
          color: colors[index % colors.length],
          obj: item
        });
      }
    });
  }

  if (rawDatum.chartSorting() === CHART_SORTING.ASC) {
    data.sort((a, b) => a.value - b.value);
  } else if (rawDatum.chartSorting() === CHART_SORTING.DESC) {
    data.sort((a, b) => b.value - a.value);
  }

  if (rawDatum.chartLimit()) {
    data = data.slice(0, rawDatum.chartLimit());
  }

  return data;
};

export const mapChartTransformer = function (rawDatum) {
  let datum = [];
  if (rawDatum.chartX() != null && rawDatum.chartYSingle() != null) {
    let regionIndex = -1;
    let valueIndex = -1;
    rawDatum.meta().some((col, idx) => {
      if (col.name === rawDatum.chartX()) {
        regionIndex = idx;
      }
      if (col.name === rawDatum.chartYSingle()) {
        valueIndex = idx;
      }
      return regionIndex !== -1 && valueIndex !== -1;
    });

    rawDatum.data().forEach(item => {
      if (isNotNullForCharts(item[valueIndex]) && isNotNullForCharts(item[regionIndex])) {
        datum.push({
          label: item[regionIndex],
          value: item[valueIndex],
          obj: item
        });
      }
    });
  }

  if (rawDatum.chartLimit()) {
    datum = datum.slice(0, rawDatum.chartLimit());
  }

  return datum;
};

export const leafletMapChartTransformer = function (rawDatum) {
  let datum = [];
  if (rawDatum.chartX() != null && rawDatum.chartYSingle() != null) {
    let latIndex = -1;
    let lngIndex = -1;
    let labelIndex = -1;
    let heatIndex = -1;
    rawDatum.meta().some((col, idx) => {
      if (col.name === rawDatum.chartX()) {
        latIndex = idx;
      }
      if (col.name === rawDatum.chartYSingle()) {
        lngIndex = idx;
      }
      if (col.name === rawDatum.chartMapLabel()) {
        labelIndex = idx;
      }
      if (col.name === rawDatum.chartMapHeat()) {
        heatIndex = idx;
      }
      return latIndex !== -1 && lngIndex !== -1 && labelIndex !== -1 && heatIndex !== -1;
    });

    rawDatum.data().forEach(item => {
      if (isNotNullForCharts(item[latIndex]) && isNotNullForCharts(item[lngIndex])) {
        datum.push({
          lat: Math.min(Math.max(MIN_LAT, item[latIndex]), MAX_LAT),
          lng: Math.min(Math.max(MIN_LNG, item[lngIndex]), MAX_LNG),
          label: labelIndex !== -1 ? html2text(item[labelIndex]) : undefined,
          isHeat: rawDatum.chartMapType() === CHART_MAP_TYPE.HEAT,
          intensity:
            heatIndex > -1 ? (!isNaN(item[heatIndex] * 1) ? item[heatIndex] * 1 : null) : null,
          obj: item
        });
      }
    });
  }

  if (rawDatum.chartLimit()) {
    datum = datum.slice(0, rawDatum.chartLimit());
  }

  return datum;
};

export const timelineChartTransformer = function (rawDatum) {
  const datum = [];
  let plottedSeries = 0;

  rawDatum.meta().forEach(meta => {
    if (rawDatum.chartYMulti().indexOf(meta.name) > -1) {
      const col = meta.name;
      let valueIndex = -1;
      let labelIndex = -1;
      rawDatum.meta().some((icol, idx) => {
        if (icol.name === rawDatum.chartX()) {
          labelIndex = idx;
        }
        if (icol.name === col) {
          valueIndex = idx;
        }
        return labelIndex !== -1 && valueIndex !== -1;
      });

      if (valueIndex > -1) {
        let values = [];
        const colors = HueColors.cuiD3Scale();
        rawDatum.data().forEach(item => {
          if (isNotNullForCharts(item[labelIndex]) && isNotNullForCharts(item[valueIndex])) {
            values.push({
              series: plottedSeries,
              x: new Date(moment(html2text(item[labelIndex])).valueOf()),
              y: item[valueIndex] * 1,
              color: colors[plottedSeries % colors.length],
              obj: item
            });
          }
        });
        if (rawDatum.chartSorting() === CHART_SORTING.ASC) {
          values.sort((a, b) => {
            return a.y - b.y;
          });
        } else if (rawDatum.chartSorting() === CHART_SORTING.DESC) {
          values.sort((a, b) => {
            return b.y - a.y;
          });
        }
        if (rawDatum.chartLimit()) {
          values = values.slice(0, rawDatum.chartLimit());
        }
        datum.push({
          key: col,
          values: values
        });
        plottedSeries++;
      }
    }
  });

  return datum;
};

export const multiSerieChartTransformer = function (rawDatum) {
  let datum = [];

  if (rawDatum.chartX() != null && rawDatum.chartYMulti().length > 0) {
    let plottedSerie = 0;

    if (typeof rawDatum.chartXPivot() !== 'undefined') {
      let valueIndex = -1;
      let labelIndex = -1;
      let isDate = false;

      rawDatum.meta().some((col, idx) => {
        if (col.name === rawDatum.chartX()) {
          isDate = col.type.toUpperCase().indexOf('DATE') > -1;
          labelIndex = idx;
        }
        if (col.name === rawDatum.chartYSingle()) {
          valueIndex = idx;
        }
        return labelIndex !== -1 && valueIndex !== -1;
      });

      rawDatum.meta().forEach((meta, cnt) => {
        if (rawDatum.chartXPivot() === meta.name) {
          const pivotIndex = cnt;
          const colors = HueColors.cuiD3Scale();
          let pivotValues = rawDatum.data().map(p => p[pivotIndex]);
          pivotValues = pivotValues.filter((item, pos) => {
            return pivotValues.indexOf(item) === pos;
          });
          pivotValues.forEach((val, pivotCnt) => {
            const values = [];
            rawDatum.data().forEach(item => {
              if (item[pivotIndex] === val) {
                if (isNotNullForCharts(item[valueIndex]) && isNotNullForCharts(item[labelIndex])) {
                  values.push({
                    x: isDate ? moment(item[labelIndex]) : html2text(item[labelIndex]),
                    y: item[valueIndex] * 1,
                    color: colors[pivotCnt % colors.length],
                    obj: item
                  });
                }
              }
            });
            datum.push({
              key: html2text(val),
              values: values
            });
          });
        }
      });

      // fills in missing values
      let longest = 0;
      const allXValues = [];
      datum.forEach(d => {
        d.values.forEach(val => {
          if (allXValues.indexOf(val.x) === -1) {
            allXValues.push(val.x);
          }
        });
      });

      datum.forEach(d => {
        allXValues.forEach(val => {
          if (
            !d.values.some(item => {
              return item.x === val;
            })
          ) {
            const zeroObj = $.extend({}, d.values[0]);
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
        datum.forEach(d => {
          for (let i = d.values.length; i < longest; i++) {
            const zeroObj = $.extend({}, d.values[0]);
            zeroObj.y = 0;
            zeroObj.x = '';
            d.values.push(zeroObj);
          }
        });
      }

      if (rawDatum.chartLimit()) {
        datum = datum.slice(0, rawDatum.chartLimit());
      }

      if (rawDatum.chartSorting() === CHART_SORTING.DESC) {
        datum.forEach(d => {
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
        datum.forEach(d => {
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
      rawDatum.meta().forEach(meta => {
        if (rawDatum.chartYMulti().indexOf(meta.name) > -1) {
          const col = meta.name;
          let valueIndex = -1;
          let labelIndex = -1;
          let isDate = false;
          rawDatum.meta().some((icol, idx) => {
            if (icol.name === rawDatum.chartX()) {
              isDate = icol.type.toUpperCase().indexOf('DATE') > -1;
              labelIndex = idx;
            }
            if (icol.name === col) {
              valueIndex = idx;
            }
            return labelIndex !== -1 && valueIndex !== -1;
          });

          if (valueIndex > -1) {
            let values = [];
            const colors = HueColors.cuiD3Scale();
            rawDatum.data().forEach((item, index) => {
              if (isNotNullForCharts(item[valueIndex]) && isNotNullForCharts(item[labelIndex])) {
                values.push({
                  series: plottedSerie,
                  x: isDate ? moment(item[labelIndex]) : html2text(item[labelIndex]),
                  y: item[valueIndex] * 1,
                  color: colors[index % colors.length],
                  obj: item
                });
              }
            });
            if (rawDatum.chartSorting() === CHART_SORTING.ASC) {
              values.sort((a, b) => {
                return a.y - b.y;
              });
            } else if (rawDatum.chartSorting() === CHART_SORTING.DESC) {
              values.sort((a, b) => {
                return b.y - a.y;
              });
            }
            if (rawDatum.chartLimit()) {
              values = values.slice(0, rawDatum.chartLimit());
            }
            datum.push({
              key: col,
              values: values
            });
            plottedSerie++;
          }
        }
      });
    }
  }
  return datum;
};

export const scatterChartTransformer = function (rawDatum) {
  const datumIndex = {};

  if (rawDatum.chartX() != null && rawDatum.chartYSingle() != null) {
    let xIndex = -1;
    let yIndex = -1;
    let sizeIndex = -1;
    let groupIndex = -1;
    rawDatum.meta().some((col, idx) => {
      if (col.name === rawDatum.chartX()) {
        xIndex = idx;
      }
      if (col.name === rawDatum.chartYSingle()) {
        yIndex = idx;
      }
      if (col.name === rawDatum.chartScatterSize()) {
        sizeIndex = idx;
      }
      if (col.name === rawDatum.chartScatterGroup()) {
        groupIndex = idx;
      }
      return xIndex !== -1 && yIndex !== -1 && sizeIndex !== -1 && groupIndex !== -1;
    });

    if (xIndex > -1 && yIndex > -1) {
      const createAndAddToArray = function (key, item) {
        if (!datumIndex[key]) {
          datumIndex[key] = [];
        }
        if (isNotNullForCharts(item[xIndex]) && isNotNullForCharts(item[yIndex])) {
          datumIndex[key].push({
            x: item[xIndex],
            y: item[yIndex],
            shape: 'circle',
            size: sizeIndex > -1 ? item[sizeIndex] : 100,
            obj: item
          });
        }
      };

      if (groupIndex > -1) {
        rawDatum.data().forEach(item => {
          createAndAddToArray(item[groupIndex], item);
        });
      } else {
        rawDatum.data().forEach(item => {
          createAndAddToArray('distro', item);
        });
      }
    }
  }

  const datum = [];

  Object.keys(datumIndex).forEach(key => {
    datum.push({
      key: key,
      values: rawDatum.chartLimit()
        ? datumIndex[key].slice(0, rawDatum.chartLimit())
        : datumIndex[key]
    });
  });

  return datum;
};
