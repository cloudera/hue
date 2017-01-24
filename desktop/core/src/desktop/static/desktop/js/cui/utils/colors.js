// (c) Copyright 2016 Cloudera, Inc. All rights reserved.

var _ = require('_');

var baseColors = [
  { name: 'black', color: '#000000' },
  { name: 'white', color: '#FFFFFF' },
  { name: 'gray', color: '#B4B4B4' },
  { name: 'blue-gray', color: '#607D8B' },
  { name: 'blue', color: '#29A7DE' },
  { name: 'steel', color: '#417575' },
  { name: 'teal', color: '#00B9AA' },
  { name: 'green', color: '#0F9D56' },
  { name: 'lime', color: '#69AC13' },
  { name: 'yellow', color: '#FFE600' },
  { name: 'orange', color: '#E99F01' },
  { name: 'red', color: '#D0021B' },
  { name: 'pink', color: '#D8276F' },
  { name: 'purple', color: '#7B46AD' },
  { name: 'purple-gray', color: '#977F86' },
  { name: 'green-gray', color: '#918D76' }];

var serviceColors = [
  { name: 'hive-color', color: '#B3A100' },
  { name: 'hdfs-color', color: '#00AA9D' },
  { name: 'hbase-color', color: '#C72466' },
  { name: 'hue-color', color: '#A37EC6' },
  { name: 'mapreduce-color', color: '#5D8A8A' },
  { name: 'zookeeper-color', color: '#619F12' },
  { name: 'oozie-color', color: '#29A7DE' },
  { name: 'flume-color', color: '#D18F00' },
  { name: 'impala-color', color: '#186485' },
  { name: 'sqoop-color', color: '#0E914F' },
  { name: 'solr-color', color: '#821743' },
  { name: 'spark-color', color: '#8B572A' },
  { name: 'pig-color', color: '#4A2A68' },
  { name: 'yarn-color', color: '#4D4500' }];

var scaleColors = [
  { name: 'gray', colors: ['#F8F8F8', '#E7E7E7', '#E0E0E0', '#DCDCDC', '#C8C8C8', '#B4B4B4', '#A0A0A0', '#787878',
    '#424242', '#212121'] },
  { name: 'blue-gray', colors: ['#ECEFF1', '#CFD8DC', '#B0BEC5', '#90A4AE', '#78909C', '#607D8B', '#546E7A',
    '#455A64', '#36454F', '#232C34'] },
  { name: 'blue', colors: ['#E9F6FB', '#BEE4F5', '#A9DBF1', '#7ECAEB', '#53B8E4', '#29A7DE', '#2496C7', '#0B7FAD',
    '#1C749B', '#186485'] },
  { name: 'steel', colors: ['#E8EEEE', '#C6D6D6', '#A0BABA', '#7A9F9F', '#5D8A8A', '#417575', '#3C6C6C', '#345E5E',
    '#2D5252', '#274646'] },
  { name: 'teal', colors: ['#E0F6F5', '#B3EAE6', '#80DCD5', '#4DCEC4', '#26C3B7', '#00B9AA', '#00AA9D', '#009488',
    '#008177', '#006F66'] },
  { name: 'green', colors: ['#E2F3EA', '#B7E2CD', '#87CEAB', '#57BB89', '#33AC6F', '#0F9D56', '#0E914F', '#0C7E45',
    '#0A6E3C', '#095E34'] },
  { name: 'lime', colors: ['#EDF5E2', '#D2E6B9', '#B4D689', '#96C55A', '#7FB836', '#69AC13', '#619F12', '#548A0F',
    '#49780D', '#3F670B'] },
  { name: 'yellow', colors: ['#FFFCE6', '#FFFACC', '#FFF599', '#FFF066', '#FFEB3B', '#FFE600', '#E6CF00', '#B3A100',
    '#807300', '#4D4500'] },
  { name: 'orange', colors: ['#FBF1E1', '#FFE8AF', '#FFD466', '#EDB233', '#EBA81A', '#E99F01', '#D18F00', '#BA7F00',
    '#A36F00', '#8B572A'] },
  { name: 'red', colors: ['#FFE5E5', '#FFCCCC', '#FFB2B2', '#E7808D', '#DE4D5F', '#D0021B', '#BB0118', '#A60115',
    '#910112', '#7C0110'] },
  { name: 'pink', colors: ['#F2DEDE', '#F3BFD4', '#EC93B7', '#E4689A', '#DE4784', '#D8276F', '#C72466', '#AD1F59',
    '#971B4D', '#821743'] },
  { name: 'purple', colors: ['#EFE9F5', '#D8C8E7', '#BDA3D6', '#A37EC6', '#8F62B9', '#7B46AD', '#71419F', '#62388A',
    '#563179', '#4A2A68'] },
  { name: 'purple-gray', colors: ['#F1EFEF', '#D5CFD1', '#BAB0B3', '#ACA0A4', '#9F9095', '#977F86', '#837077',
    '#766168', '#6A575D', '#5E4D53'] },
  { name: 'green-gray', colors: ['#E9E8E3', '#C8C6BA', '#B2AF9F', '#A7A391', '#9C9883', '#918D76', '#827E6A',
    '#74705E', '#656252', '#575446'] }
    ];

/**
 * @module utils/colors
 * @description This module contains all the colors defined in the colors.less
 * and some helper methods for accessing them.
 */
module.exports = {

  /**
   * Gets the HEX value for a base color.
   * @param  {string} baseName  The name used for the base color, e.g. 'blue'.
   * @return {string}           The HEX-color
   */
  getBaseColor: function(baseName) {
    var base = _.find(baseColors, { name: baseName });

    return base.color;
  },

  /**
   * Gets the names and HEX values for all the base colors.
   * @return {array}            Array with color objects like { name: 'black', color: '#000000' }
   */
  getAllBaseColors: function() {
    return baseColors;
  },

  /**
   * Gets the HEX value for a service color,
   * @param  {string} name      The name used for the service color, e.g. 'pig-color'.
   * @return {string}           The HEX-color
   */
  getServiceColor: function(name) {
    var service = _.find(serviceColors, { name: name });
    if (service) {
      return service.color;
    } else {
      return this.getScaleColor('blue', 500);
    }
  },

  /**
   * Gets the names and HEX values for all the service colors.
   * @return {array}            Array with color objects like { name: 'pig-color', color: '#031F7F' }
   */
  getAllServiceColors: function() {
    return serviceColors;
  },

  /**
   * Gets the HEX value for a specific value in a base color scale.
   * @param  {string} baseName    The name used for the base color, e.g. 'blue'.
   * @param  {string} scaleNumber The number of the scale, e.g. '050' or '400'.
   * @return {string}             The HEX-color
   */
  getScaleColor: function(baseName, scaleNumber) {
    var scale = _.find(scaleColors, { name: baseName });
    var index = Math.floor(scaleNumber / 100);

    return scale.colors[index];
  },

  /**
   * Gets all the HEX values from a base color scale.
   * @param  {string} baseName    The name used for the base color, e.g. 'blue'.
   * @return {array}              Array with HEX-values e.g. ['#E0F6F5', '#B3EAE6', '#80DCD5' ... ]
   */
  getScaleColors: function(baseName) {
    var scale = _.find(scaleColors, { name: baseName });

    return scale.colors;
  },

  /**
   * Gets all the scales for all the base colors
   * @return {array}              Array with objects containing base color name and all the HEX values in the scale.
   */
  getAllScaleColors: function() {
    return scaleColors;
  },

  /**
   * Translates a 0-based index and base name into a scale color name.
   * E.g. base name 'green' and index 0 returns 'green-050' and base name 'purple-gray' and
   * index 4 returns 'purple-gray-400'.
   * @param  {string} baseName       The name used for the base color, e.g. 'blue'.
   * @param  {number} zeroBasedIndex The index representing the color in the scale as an array.
   * @return {string}                Name of specific color in a base color scale, e.g. 'green-050'.
   */
  getScaleColorName: function(baseName, zeroBasedIndex) {
    return zeroBasedIndex === 0 ? baseName + '-050' : baseName + '-' + (zeroBasedIndex * 100);
  },

  /**
   * Utility function to strip the leading '#' from a HEX color
   * @param  {string} h       The color in HEX format
   * @return {string}         The color without leading '#'
   */
  cutHex: function(h) {
    return (h.charAt(0) == '#') ? h.substring(1, 7) : h;
  },

  /**
   * Utility function to convert the HEX value of red to an int red for RGB
   * @param  {string} h       The color in HEX format
   * @return {number}         The R value of RGB
   */
  hexToR: function(h) {
    return parseInt((this.cutHex(h)).substring(0, 2), 16);
  },

  /**
   * Utility function to convert the HEX value of green to an int green for RGB
   * @param  {string} h       The color in HEX format
   * @return {number}         The G value of RGB
   */
  hexToG: function(h) {
    return parseInt((this.cutHex(h)).substring(2, 4), 16);
  },

  /**
   * Utility function to convert the HEX value of blue to an int blue for RGB
   * @param  {string} h       The color in HEX format
   * @return {number}         The B value of RGB
   */
  hexToB: function(h) {
    return parseInt((this.cutHex(h)).substring(4, 6), 16);
  },

  /**
   * Utility function to convert decimal to hexadecimal
   * @param  {number} i       The decimal value
   * @return {string}         The HEX value
   */
  decToHex: function(i) {
    return (i + 0x100).toString(16).substr(-2).toUpperCase();
  },

  /**
   * Gets a distributed color scale from HEX to HEX in N bands (using RGB sums)
   * @param  {string} from    The start color in HEX format
   * @param  {string} to      The end color in HEX format
   * @param  {number} bands   The number of colors to get
   * @return {array}          A list of colors in the {'color': '#HEX_VALUE'} format
   */
  getHEXScale: function(from, to, bands) {
    if (from.indexOf('#') === 0) {
      from = from.substr(1);
    }

    if (to.indexOf('#') === 0) {
      to = to.substr(1);
    }

    var fromRGB = [this.hexToR(from), this.hexToG(from), this.hexToB(from)],
      toRGB = [this.hexToR(to), this.hexToG(to), this.hexToB(to)],
      i,
      delta = [],
      resultingBands = [];

    for (i = 0; i < 4; i++) {
      delta[i] = (fromRGB[i] - toRGB[i]) / (bands + 1);
    }

    for (i = 0; i < bands; i++) {
      var r = Math.round(fromRGB[0] - delta[0] * i);
      var g = Math.round(fromRGB[1] - delta[1] * i);
      var b = Math.round(fromRGB[2] - delta[2] * i);
      resultingBands.push({ color: '#' + this.decToHex(r) + this.decToHex(g) + this.decToHex(b) });
    }

    return resultingBands;
  },

  /**
   * Gets a palette of colors to be used in charts
   * It can be used in several ways, e.g.
   * getChartColor() >> the whole spectrum
   * getChartColor(10) >> gets the first 10 colors from the whole spectrum
   * getChartColor('pink') >> gets all the pink variations of CUI
   * getChartColor('blue', 30) >> gets 30 variations of the CUI blue, calculating the missing ones from the color scale
   * getChartColor('orange', 9, true) >> gets the CUI orange scale reversed, from darker to lighter
   * getChartColor('green', 9, false, true) >> gets the CUI green scale optimized for contrast
   * @param  {string|number} swatch   The name used for the base color, e.g. 'blue' or a number of colors to get from the full spectrum
   * @param  {number} bands           The number of colors to get
   * @param  {boolean} reversed       If specified, it will return a list of colors from darker to lighter
   * @param  {boolean} distributed    If specified, it will return a list of colors using the preferred order of shade one after the other (useful for pie charts)
   * @return {array}                  A list of colors in the {'color': '#HEX_VALUE'} format
   */
  getChartColors: function(swatch, bands, reversed, distributed) {
    var normalizedColors = {}, semiScale, i, j;
    scaleColors.forEach(function(scaleDef) {
      normalizedColors[scaleDef.name] = scaleDef.colors;
    });

    // optimal visual sequence of color where we take contrast and good looking into consideration.
    var sequence = ['blue', 'lime', 'steel', 'teal', 'purple', 'green', 'pink', 'blue-gray', 'orange', 'red'];

    // optimal visual sequence of shade where 3 means 300 and 0 (means 050) is not used because it is too light.
    var shadeOrder = [3, 2, 4, 1, 5, 6, 9, 7, 8],
      wholeSpectrum = [],
      sequenceHalfLength = sequence.length / 2;

    for (i = 0; i < shadeOrder.length; i++) {
      for (j = 0; j < sequence.length; j++) {
        wholeSpectrum.push({ color: normalizedColors[sequence[j]][shadeOrder[i]] });
      }
    }

    if (typeof swatch === 'undefined') {
      return wholeSpectrum;
    }

    if (typeof swatch === 'number') {
      return wholeSpectrum.splice(0, swatch);
    }

    var scale = _.find(scaleColors, { name: swatch });

    if (typeof scale === 'undefined') {
      return [{ color: '#4A412A' }]; // the world's ugliest color, Pantone 448 C.
    }

    if (bands) {
      if (bands === 1) {
        // The best band to use is xxx-300
        return [{ color: scale.colors[shadeOrder[0]] }];
      }

      if (bands <= shadeOrder.length) {
        semiScale = [];
        if (distributed) {
          // the shade
          for (i = 0; i < bands; i++) {
            semiScale.push({ color: scale.colors[shadeOrder[i]] });
          }
        } else {
          semiScale = [{ color: scale.colors[0] }];
          var totalItems = scale.colors.length - 2;
          var interval = Math.floor(totalItems / (bands - 2));
          for (i = 1; i < bands - 1; i++) {
            semiScale.push({ color: scale.colors[i * interval] });
          }

          semiScale.push({ color: scale.colors[scale.colors.length - 1] });
        }

        return reversed ? semiScale.reverse().splice(0, bands) : semiScale.splice(0, bands);
      } else {
        semiScale = this.getHEXScale(scale.colors[1], scale.colors[5], Math.ceil(bands / 2)).concat(
          this.getHEXScale(scale.colors[5], scale.colors[9], Math.floor(bands / 2))
        );
        if (distributed) {
          var tempScale = [];
          for (i = 0; i < Math.floor(bands / 2); i++) {
            tempScale.push(semiScale[i]);
            tempScale.push(semiScale[bands - 1 - i]);
          }

          semiScale = tempScale.splice(0, bands);
        }

        return reversed ? semiScale.reverse() : semiScale;
      }
    }

    return _.map(reversed ? scale.colors.reverse() : scale.colors, function(hex) {
      return { color: hex };
    });
  }
};
