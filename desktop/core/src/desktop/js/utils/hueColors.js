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

import d3v3 from 'd3v3';

const HueColors = {
  CUIScaleColors: [
    {
      name: 'gray',
      colors: [
        '#F8F8F8',
        '#E7E7E7',
        '#E0E0E0',
        '#DCDCDC',
        '#C8C8C8',
        '#B4B4B4',
        '#A0A0A0',
        '#787878',
        '#424242',
        '#212121'
      ]
    },
    {
      name: 'blue-gray',
      colors: [
        '#ECEFF1',
        '#CFD8DC',
        '#B0BEC5',
        '#90A4AE',
        '#78909C',
        '#607D8B',
        '#546E7A',
        '#455A64',
        '#36454F',
        '#232C34'
      ]
    },
    {
      name: 'blue',
      colors: [
        '#E9F6FB',
        '#BEE4F5',
        '#A9DBF1',
        '#7ECAEB',
        '#53B8E4',
        '#29A7DE',
        '#2496C7',
        '#0B7FAD',
        '#1C749B',
        '#186485'
      ]
    },
    {
      name: 'steel',
      colors: [
        '#E8EEEE',
        '#C6D6D6',
        '#A0BABA',
        '#7A9F9F',
        '#5D8A8A',
        '#417575',
        '#3C6C6C',
        '#345E5E',
        '#2D5252',
        '#274646'
      ]
    },
    {
      name: 'teal',
      colors: [
        '#E0F6F5',
        '#B3EAE6',
        '#80DCD5',
        '#4DCEC4',
        '#26C3B7',
        '#00B9AA',
        '#00AA9D',
        '#009488',
        '#008177',
        '#006F66'
      ]
    },
    {
      name: 'green',
      colors: [
        '#E2F3EA',
        '#B7E2CD',
        '#87CEAB',
        '#57BB89',
        '#33AC6F',
        '#0F9D56',
        '#0E914F',
        '#0C7E45',
        '#0A6E3C',
        '#095E34'
      ]
    },
    {
      name: 'lime',
      colors: [
        '#EDF5E2',
        '#D2E6B9',
        '#B4D689',
        '#96C55A',
        '#7FB836',
        '#69AC13',
        '#619F12',
        '#548A0F',
        '#49780D',
        '#3F670B'
      ]
    },
    {
      name: 'yellow',
      colors: [
        '#FFFCE6',
        '#FFFACC',
        '#FFF599',
        '#FFF066',
        '#FFEB3B',
        '#FFE600',
        '#E6CF00',
        '#B3A100',
        '#807300',
        '#4D4500'
      ]
    },
    {
      name: 'orange',
      colors: [
        '#FBF1E1',
        '#FFE8AF',
        '#FFD466',
        '#EDB233',
        '#EBA81A',
        '#E99F01',
        '#D18F00',
        '#BA7F00',
        '#A36F00',
        '#8B572A'
      ]
    },
    {
      name: 'red',
      colors: [
        '#FFE5E5',
        '#FFCCCC',
        '#FFB2B2',
        '#E7808D',
        '#DE4D5F',
        '#D0021B',
        '#BB0118',
        '#A60115',
        '#910112',
        '#7C0110'
      ]
    },
    {
      name: 'pink',
      colors: [
        '#F2DEDE',
        '#F3BFD4',
        '#EC93B7',
        '#E4689A',
        '#DE4784',
        '#D8276F',
        '#C72466',
        '#AD1F59',
        '#971B4D',
        '#821743'
      ]
    },
    {
      name: 'purple',
      colors: [
        '#EFE9F5',
        '#D8C8E7',
        '#BDA3D6',
        '#A37EC6',
        '#8F62B9',
        '#7B46AD',
        '#71419F',
        '#62388A',
        '#563179',
        '#4A2A68'
      ]
    },
    {
      name: 'purple-gray',
      colors: [
        '#F1EFEF',
        '#D5CFD1',
        '#BAB0B3',
        '#ACA0A4',
        '#9F9095',
        '#977F86',
        '#837077',
        '#766168',
        '#6A575D',
        '#5E4D53'
      ]
    },
    {
      name: 'green-gray',
      colors: [
        '#E9E8E3',
        '#C8C6BA',
        '#B2AF9F',
        '#A7A391',
        '#9C9883',
        '#918D76',
        '#827E6A',
        '#74705E',
        '#656252',
        '#575446'
      ]
    }
  ],

  hexToR: function(h) {
    return parseInt(this.cutHex(h).substring(0, 2), 16);
  },

  hexToG: function(h) {
    return parseInt(this.cutHex(h).substring(2, 4), 16);
  },

  hexToB: function(h) {
    return parseInt(this.cutHex(h).substring(4, 6), 16);
  },

  cutHex: function(h) {
    return h.charAt(0) === '#' ? h.substring(1, 7) : h;
  },

  decToHex: function(i) {
    return (i + 0x100)
      .toString(16)
      .substr(-2)
      .toUpperCase();
  },

  scale: function(from, to, bands) {
    const fromRGB = [this.hexToR(from), this.hexToG(from), this.hexToB(from)];
    const toRGB = [this.hexToR(to), this.hexToG(to), this.hexToB(to)];
    let i;
    const delta = [];
    const result = [];

    for (i = 0; i < 4; i++) {
      delta[i] = (fromRGB[i] - toRGB[i]) / (bands + 1);
    }

    for (i = 0; i < bands; i++) {
      const r = Math.round(fromRGB[0] - delta[0] * i);
      const g = Math.round(fromRGB[1] - delta[1] * i);
      const b = Math.round(fromRGB[2] - delta[2] * i);
      result.push('#' + this.decToHex(r) + this.decToHex(g) + this.decToHex(b));
    }
    return result;
  },

  getNormalizedColors: function() {
    const normalizedColors = {};
    this.CUIScaleColors.forEach(scaleDef => {
      normalizedColors[scaleDef.name] = scaleDef.colors;
    });
    return normalizedColors;
  },

  getCUIChartColors: function() {
    let i;

    const normalizedColors = this.getNormalizedColors();

    // optimal visual sequence by contrasting colors
    const sequence = [
        'blue',
        'lime',
        'blue-gray',
        'pink',
        'steel',
        'purple',
        'teal',
        'red',
        'orange',
        'green'
      ],
      wholeSpectrum = [],
      sequenceHalfLength = sequence.length / 2;

    function addMain(mainSwatch) {
      wholeSpectrum.push({ color: normalizedColors[mainSwatch][sequenceHalfLength] });
    }

    function addPlus(mainSwatch) {
      wholeSpectrum.push({ color: normalizedColors[mainSwatch][sequenceHalfLength + i] });
    }

    function addMinus(mainSwatch) {
      wholeSpectrum.push({ color: normalizedColors[mainSwatch][sequenceHalfLength - i] });
    }

    for (i = 1; i < sequenceHalfLength; i++) {
      if (i === 1) {
        sequence.forEach(addMain);
      }

      sequence.forEach(addPlus);
      sequence.forEach(addMinus);
    }
    return wholeSpectrum;
  },

  d3Scale: function() {
    return d3v3.scale
      .category20()
      .range()
      .concat(
        d3v3.scale
          .category20b()
          .range()
          .concat(d3v3.scale.category20c().range())
      );
  },
  cuiD3Scale: function(swatch) {
    let colors = this.getCUIChartColors().map(c => {
      return c.color;
    });
    if (swatch) {
      this.CUIScaleColors.forEach(s => {
        if (s.name === swatch) {
          colors = s.colors;
        }
      });
    }
    return colors;
  },
  LIGHT_BLUE: '#DBE8F1',
  BLUE: '#87BAD5',
  DARK_BLUE: '#0B7FAD',
  DARKER_BLUE: '#205875',
  PURPLE: '#C0B1E9',
  GRAY: '#666666',
  WHITE: '#FFFFFF',
  ORANGE: '#FF7F0E'
};

export default HueColors;
