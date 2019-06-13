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

const NominatimAPI = function(options) {
  this.BASE_URL = 'http://nominatim.openstreetmap.org/search?format=json';
  this.limit = options && options.limit ? options.limit : 1;

  this.lookupCity = function(city, callback) {
    $.getJSON(
      this.BASE_URL + '&city=' + city + '&limit=' + this.limit + '&json_callback=?',
      data => {
        callback(data);
      }
    );
  };

  this.lookupAddress = function(address, callback) {
    $.getJSON(
      this.BASE_URL + '&q=' + address + '&limit=' + this.limit + '&json_callback=?',
      data => {
        callback(data);
      }
    );
  };
};

const HueGeo = {
  ISO_3166: [
    {
      name: 'Afghanistan',
      alpha2: 'AF',
      alpha3: 'AFG',
      'country-code': '004',
      'iso_3166-2': 'ISO 3166-2:AF',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Åland Islands',
      alpha2: 'AX',
      alpha3: 'ALA',
      'country-code': '248',
      'iso_3166-2': 'ISO 3166-2:AX',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Albania',
      alpha2: 'AL',
      alpha3: 'ALB',
      'country-code': '008',
      'iso_3166-2': 'ISO 3166-2:AL',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Algeria',
      alpha2: 'DZ',
      alpha3: 'DZA',
      'country-code': '012',
      'iso_3166-2': 'ISO 3166-2:DZ',
      'region-code': '002',
      'sub-region-code': '015'
    },
    {
      name: 'American Samoa',
      alpha2: 'AS',
      alpha3: 'ASM',
      'country-code': '016',
      'iso_3166-2': 'ISO 3166-2:AS',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'Andorra',
      alpha2: 'AD',
      alpha3: 'AND',
      'country-code': '020',
      'iso_3166-2': 'ISO 3166-2:AD',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Angola',
      alpha2: 'AO',
      alpha3: 'AGO',
      'country-code': '024',
      'iso_3166-2': 'ISO 3166-2:AO',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Anguilla',
      alpha2: 'AI',
      alpha3: 'AIA',
      'country-code': '660',
      'iso_3166-2': 'ISO 3166-2:AI',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Antarctica',
      alpha2: 'AQ',
      alpha3: 'ATA',
      'country-code': '010',
      'iso_3166-2': 'ISO 3166-2:AQ'
    },
    {
      name: 'Antigua and Barbuda',
      alpha2: 'AG',
      alpha3: 'ATG',
      'country-code': '028',
      'iso_3166-2': 'ISO 3166-2:AG',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Argentina',
      alpha2: 'AR',
      alpha3: 'ARG',
      'country-code': '032',
      'iso_3166-2': 'ISO 3166-2:AR',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Armenia',
      alpha2: 'AM',
      alpha3: 'ARM',
      'country-code': '051',
      'iso_3166-2': 'ISO 3166-2:AM',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Aruba',
      alpha2: 'AW',
      alpha3: 'ABW',
      'country-code': '533',
      'iso_3166-2': 'ISO 3166-2:AW',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Australia',
      alpha2: 'AU',
      alpha3: 'AUS',
      'country-code': '036',
      'iso_3166-2': 'ISO 3166-2:AU',
      'region-code': '009',
      'sub-region-code': '053'
    },
    {
      name: 'Austria',
      alpha2: 'AT',
      alpha3: 'AUT',
      'country-code': '040',
      'iso_3166-2': 'ISO 3166-2:AT',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'Azerbaijan',
      alpha2: 'AZ',
      alpha3: 'AZE',
      'country-code': '031',
      'iso_3166-2': 'ISO 3166-2:AZ',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Bahamas',
      alpha2: 'BS',
      alpha3: 'BHS',
      'country-code': '044',
      'iso_3166-2': 'ISO 3166-2:BS',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Bahrain',
      alpha2: 'BH',
      alpha3: 'BHR',
      'country-code': '048',
      'iso_3166-2': 'ISO 3166-2:BH',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Bangladesh',
      alpha2: 'BD',
      alpha3: 'BGD',
      'country-code': '050',
      'iso_3166-2': 'ISO 3166-2:BD',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Barbados',
      alpha2: 'BB',
      alpha3: 'BRB',
      'country-code': '052',
      'iso_3166-2': 'ISO 3166-2:BB',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Belarus',
      alpha2: 'BY',
      alpha3: 'BLR',
      'country-code': '112',
      'iso_3166-2': 'ISO 3166-2:BY',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Belgium',
      alpha2: 'BE',
      alpha3: 'BEL',
      'country-code': '056',
      'iso_3166-2': 'ISO 3166-2:BE',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'Belize',
      alpha2: 'BZ',
      alpha3: 'BLZ',
      'country-code': '084',
      'iso_3166-2': 'ISO 3166-2:BZ',
      'region-code': '019',
      'sub-region-code': '013'
    },
    {
      name: 'Benin',
      alpha2: 'BJ',
      alpha3: 'BEN',
      'country-code': '204',
      'iso_3166-2': 'ISO 3166-2:BJ',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Bermuda',
      alpha2: 'BM',
      alpha3: 'BMU',
      'country-code': '060',
      'iso_3166-2': 'ISO 3166-2:BM',
      'region-code': '019',
      'sub-region-code': '021'
    },
    {
      name: 'Bhutan',
      alpha2: 'BT',
      alpha3: 'BTN',
      'country-code': '064',
      'iso_3166-2': 'ISO 3166-2:BT',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Bolivia, Plurinational State of',
      alpha2: 'BO',
      alpha3: 'BOL',
      'country-code': '068',
      'iso_3166-2': 'ISO 3166-2:BO',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Bonaire, Sint Eustatius and Saba',
      alpha2: 'BQ',
      alpha3: 'BES',
      'country-code': '535',
      'iso_3166-2': 'ISO 3166-2:BQ',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Bosnia and Herzegovina',
      alpha2: 'BA',
      alpha3: 'BIH',
      'country-code': '070',
      'iso_3166-2': 'ISO 3166-2:BA',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Botswana',
      alpha2: 'BW',
      alpha3: 'BWA',
      'country-code': '072',
      'iso_3166-2': 'ISO 3166-2:BW',
      'region-code': '002',
      'sub-region-code': '018'
    },
    {
      name: 'Bouvet Island',
      alpha2: 'BV',
      alpha3: 'BVT',
      'country-code': '074',
      'iso_3166-2': 'ISO 3166-2:BV'
    },
    {
      name: 'Brazil',
      alpha2: 'BR',
      alpha3: 'BRA',
      'country-code': '076',
      'iso_3166-2': 'ISO 3166-2:BR',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'British Indian Ocean Territory',
      alpha2: 'IO',
      alpha3: 'IOT',
      'country-code': '086',
      'iso_3166-2': 'ISO 3166-2:IO'
    },
    {
      name: 'Brunei Darussalam',
      alpha2: 'BN',
      alpha3: 'BRN',
      'country-code': '096',
      'iso_3166-2': 'ISO 3166-2:BN',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Bulgaria',
      alpha2: 'BG',
      alpha3: 'BGR',
      'country-code': '100',
      'iso_3166-2': 'ISO 3166-2:BG',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Burkina Faso',
      alpha2: 'BF',
      alpha3: 'BFA',
      'country-code': '854',
      'iso_3166-2': 'ISO 3166-2:BF',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Burundi',
      alpha2: 'BI',
      alpha3: 'BDI',
      'country-code': '108',
      'iso_3166-2': 'ISO 3166-2:BI',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Cambodia',
      alpha2: 'KH',
      alpha3: 'KHM',
      'country-code': '116',
      'iso_3166-2': 'ISO 3166-2:KH',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Cameroon',
      alpha2: 'CM',
      alpha3: 'CMR',
      'country-code': '120',
      'iso_3166-2': 'ISO 3166-2:CM',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Canada',
      alpha2: 'CA',
      alpha3: 'CAN',
      'country-code': '124',
      'iso_3166-2': 'ISO 3166-2:CA',
      'region-code': '019',
      'sub-region-code': '021'
    },
    {
      name: 'Cape Verde',
      alpha2: 'CV',
      alpha3: 'CPV',
      'country-code': '132',
      'iso_3166-2': 'ISO 3166-2:CV',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Cayman Islands',
      alpha2: 'KY',
      alpha3: 'CYM',
      'country-code': '136',
      'iso_3166-2': 'ISO 3166-2:KY',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Central African Republic',
      alpha2: 'CF',
      alpha3: 'CAF',
      'country-code': '140',
      'iso_3166-2': 'ISO 3166-2:CF',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Chad',
      alpha2: 'TD',
      alpha3: 'TCD',
      'country-code': '148',
      'iso_3166-2': 'ISO 3166-2:TD',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Chile',
      alpha2: 'CL',
      alpha3: 'CHL',
      'country-code': '152',
      'iso_3166-2': 'ISO 3166-2:CL',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'China',
      alpha2: 'CN',
      alpha3: 'CHN',
      'country-code': '156',
      'iso_3166-2': 'ISO 3166-2:CN',
      'region-code': '142',
      'sub-region-code': '030'
    },
    {
      name: 'Christmas Island',
      alpha2: 'CX',
      alpha3: 'CXR',
      'country-code': '162',
      'iso_3166-2': 'ISO 3166-2:CX'
    },
    {
      name: 'Cocos (Keeling) Islands',
      alpha2: 'CC',
      alpha3: 'CCK',
      'country-code': '166',
      'iso_3166-2': 'ISO 3166-2:CC'
    },
    {
      name: 'Colombia',
      alpha2: 'CO',
      alpha3: 'COL',
      'country-code': '170',
      'iso_3166-2': 'ISO 3166-2:CO',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Comoros',
      alpha2: 'KM',
      alpha3: 'COM',
      'country-code': '174',
      'iso_3166-2': 'ISO 3166-2:KM',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Congo',
      alpha2: 'CG',
      alpha3: 'COG',
      'country-code': '178',
      'iso_3166-2': 'ISO 3166-2:CG',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Congo, the Democratic Republic of the',
      alpha2: 'CD',
      alpha3: 'COD',
      'country-code': '180',
      'iso_3166-2': 'ISO 3166-2:CD',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Cook Islands',
      alpha2: 'CK',
      alpha3: 'COK',
      'country-code': '184',
      'iso_3166-2': 'ISO 3166-2:CK',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'Costa Rica',
      alpha2: 'CR',
      alpha3: 'CRI',
      'country-code': '188',
      'iso_3166-2': 'ISO 3166-2:CR',
      'region-code': '019',
      'sub-region-code': '013'
    },
    {
      name: "Côte d'Ivoire",
      alpha2: 'CI',
      alpha3: 'CIV',
      'country-code': '384',
      'iso_3166-2': 'ISO 3166-2:CI',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Croatia',
      alpha2: 'HR',
      alpha3: 'HRV',
      'country-code': '191',
      'iso_3166-2': 'ISO 3166-2:HR',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Cuba',
      alpha2: 'CU',
      alpha3: 'CUB',
      'country-code': '192',
      'iso_3166-2': 'ISO 3166-2:CU',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Curaçao',
      alpha2: 'CW',
      alpha3: 'CUW',
      'country-code': '531',
      'iso_3166-2': 'ISO 3166-2:CW',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Cyprus',
      alpha2: 'CY',
      alpha3: 'CYP',
      'country-code': '196',
      'iso_3166-2': 'ISO 3166-2:CY',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Czech Republic',
      alpha2: 'CZ',
      alpha3: 'CZE',
      'country-code': '203',
      'iso_3166-2': 'ISO 3166-2:CZ',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Denmark',
      alpha2: 'DK',
      alpha3: 'DNK',
      'country-code': '208',
      'iso_3166-2': 'ISO 3166-2:DK',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Djibouti',
      alpha2: 'DJ',
      alpha3: 'DJI',
      'country-code': '262',
      'iso_3166-2': 'ISO 3166-2:DJ',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Dominica',
      alpha2: 'DM',
      alpha3: 'DMA',
      'country-code': '212',
      'iso_3166-2': 'ISO 3166-2:DM',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Dominican Republic',
      alpha2: 'DO',
      alpha3: 'DOM',
      'country-code': '214',
      'iso_3166-2': 'ISO 3166-2:DO',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Ecuador',
      alpha2: 'EC',
      alpha3: 'ECU',
      'country-code': '218',
      'iso_3166-2': 'ISO 3166-2:EC',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Egypt',
      alpha2: 'EG',
      alpha3: 'EGY',
      'country-code': '818',
      'iso_3166-2': 'ISO 3166-2:EG',
      'region-code': '002',
      'sub-region-code': '015'
    },
    {
      name: 'El Salvador',
      alpha2: 'SV',
      alpha3: 'SLV',
      'country-code': '222',
      'iso_3166-2': 'ISO 3166-2:SV',
      'region-code': '019',
      'sub-region-code': '013'
    },
    {
      name: 'Equatorial Guinea',
      alpha2: 'GQ',
      alpha3: 'GNQ',
      'country-code': '226',
      'iso_3166-2': 'ISO 3166-2:GQ',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Eritrea',
      alpha2: 'ER',
      alpha3: 'ERI',
      'country-code': '232',
      'iso_3166-2': 'ISO 3166-2:ER',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Estonia',
      alpha2: 'EE',
      alpha3: 'EST',
      'country-code': '233',
      'iso_3166-2': 'ISO 3166-2:EE',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Ethiopia',
      alpha2: 'ET',
      alpha3: 'ETH',
      'country-code': '231',
      'iso_3166-2': 'ISO 3166-2:ET',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Falkland Islands (Malvinas)',
      alpha2: 'FK',
      alpha3: 'FLK',
      'country-code': '238',
      'iso_3166-2': 'ISO 3166-2:FK',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Faroe Islands',
      alpha2: 'FO',
      alpha3: 'FRO',
      'country-code': '234',
      'iso_3166-2': 'ISO 3166-2:FO',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Fiji',
      alpha2: 'FJ',
      alpha3: 'FJI',
      'country-code': '242',
      'iso_3166-2': 'ISO 3166-2:FJ',
      'region-code': '009',
      'sub-region-code': '054'
    },
    {
      name: 'Finland',
      alpha2: 'FI',
      alpha3: 'FIN',
      'country-code': '246',
      'iso_3166-2': 'ISO 3166-2:FI',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'France',
      alpha2: 'FR',
      alpha3: 'FRA',
      'country-code': '250',
      'iso_3166-2': 'ISO 3166-2:FR',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'French Guiana',
      alpha2: 'GF',
      alpha3: 'GUF',
      'country-code': '254',
      'iso_3166-2': 'ISO 3166-2:GF',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'French Polynesia',
      alpha2: 'PF',
      alpha3: 'PYF',
      'country-code': '258',
      'iso_3166-2': 'ISO 3166-2:PF',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'French Southern Territories',
      alpha2: 'TF',
      alpha3: 'ATF',
      'country-code': '260',
      'iso_3166-2': 'ISO 3166-2:TF'
    },
    {
      name: 'Gabon',
      alpha2: 'GA',
      alpha3: 'GAB',
      'country-code': '266',
      'iso_3166-2': 'ISO 3166-2:GA',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Gambia',
      alpha2: 'GM',
      alpha3: 'GMB',
      'country-code': '270',
      'iso_3166-2': 'ISO 3166-2:GM',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Georgia',
      alpha2: 'GE',
      alpha3: 'GEO',
      'country-code': '268',
      'iso_3166-2': 'ISO 3166-2:GE',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Germany',
      alpha2: 'DE',
      alpha3: 'DEU',
      'country-code': '276',
      'iso_3166-2': 'ISO 3166-2:DE',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'Ghana',
      alpha2: 'GH',
      alpha3: 'GHA',
      'country-code': '288',
      'iso_3166-2': 'ISO 3166-2:GH',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Gibraltar',
      alpha2: 'GI',
      alpha3: 'GIB',
      'country-code': '292',
      'iso_3166-2': 'ISO 3166-2:GI',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Greece',
      alpha2: 'GR',
      alpha3: 'GRC',
      'country-code': '300',
      'iso_3166-2': 'ISO 3166-2:GR',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Greenland',
      alpha2: 'GL',
      alpha3: 'GRL',
      'country-code': '304',
      'iso_3166-2': 'ISO 3166-2:GL',
      'region-code': '019',
      'sub-region-code': '021'
    },
    {
      name: 'Grenada',
      alpha2: 'GD',
      alpha3: 'GRD',
      'country-code': '308',
      'iso_3166-2': 'ISO 3166-2:GD',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Guadeloupe',
      alpha2: 'GP',
      alpha3: 'GLP',
      'country-code': '312',
      'iso_3166-2': 'ISO 3166-2:GP',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Guam',
      alpha2: 'GU',
      alpha3: 'GUM',
      'country-code': '316',
      'iso_3166-2': 'ISO 3166-2:GU',
      'region-code': '009',
      'sub-region-code': '057'
    },
    {
      name: 'Guatemala',
      alpha2: 'GT',
      alpha3: 'GTM',
      'country-code': '320',
      'iso_3166-2': 'ISO 3166-2:GT',
      'region-code': '019',
      'sub-region-code': '013'
    },
    {
      name: 'Guernsey',
      alpha2: 'GG',
      alpha3: 'GGY',
      'country-code': '831',
      'iso_3166-2': 'ISO 3166-2:GG',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Guinea',
      alpha2: 'GN',
      alpha3: 'GIN',
      'country-code': '324',
      'iso_3166-2': 'ISO 3166-2:GN',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Guinea-Bissau',
      alpha2: 'GW',
      alpha3: 'GNB',
      'country-code': '624',
      'iso_3166-2': 'ISO 3166-2:GW',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Guyana',
      alpha2: 'GY',
      alpha3: 'GUY',
      'country-code': '328',
      'iso_3166-2': 'ISO 3166-2:GY',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Haiti',
      alpha2: 'HT',
      alpha3: 'HTI',
      'country-code': '332',
      'iso_3166-2': 'ISO 3166-2:HT',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Heard Island and McDonald Islands',
      alpha2: 'HM',
      alpha3: 'HMD',
      'country-code': '334',
      'iso_3166-2': 'ISO 3166-2:HM'
    },
    {
      name: 'Holy See (Vatican City State)',
      alpha2: 'VA',
      alpha3: 'VAT',
      'country-code': '336',
      'iso_3166-2': 'ISO 3166-2:VA',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Honduras',
      alpha2: 'HN',
      alpha3: 'HND',
      'country-code': '340',
      'iso_3166-2': 'ISO 3166-2:HN',
      'region-code': '019',
      'sub-region-code': '013'
    },
    {
      name: 'Hong Kong',
      alpha2: 'HK',
      alpha3: 'HKG',
      'country-code': '344',
      'iso_3166-2': 'ISO 3166-2:HK',
      'region-code': '142',
      'sub-region-code': '030'
    },
    {
      name: 'Hungary',
      alpha2: 'HU',
      alpha3: 'HUN',
      'country-code': '348',
      'iso_3166-2': 'ISO 3166-2:HU',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Iceland',
      alpha2: 'IS',
      alpha3: 'ISL',
      'country-code': '352',
      'iso_3166-2': 'ISO 3166-2:IS',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'India',
      alpha2: 'IN',
      alpha3: 'IND',
      'country-code': '356',
      'iso_3166-2': 'ISO 3166-2:IN',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Indonesia',
      alpha2: 'ID',
      alpha3: 'IDN',
      'country-code': '360',
      'iso_3166-2': 'ISO 3166-2:ID',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Iran, Islamic Republic of',
      alpha2: 'IR',
      alpha3: 'IRN',
      'country-code': '364',
      'iso_3166-2': 'ISO 3166-2:IR',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Iraq',
      alpha2: 'IQ',
      alpha3: 'IRQ',
      'country-code': '368',
      'iso_3166-2': 'ISO 3166-2:IQ',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Ireland',
      alpha2: 'IE',
      alpha3: 'IRL',
      'country-code': '372',
      'iso_3166-2': 'ISO 3166-2:IE',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Isle of Man',
      alpha2: 'IM',
      alpha3: 'IMN',
      'country-code': '833',
      'iso_3166-2': 'ISO 3166-2:IM',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Israel',
      alpha2: 'IL',
      alpha3: 'ISR',
      'country-code': '376',
      'iso_3166-2': 'ISO 3166-2:IL',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Italy',
      alpha2: 'IT',
      alpha3: 'ITA',
      'country-code': '380',
      'iso_3166-2': 'ISO 3166-2:IT',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Jamaica',
      alpha2: 'JM',
      alpha3: 'JAM',
      'country-code': '388',
      'iso_3166-2': 'ISO 3166-2:JM',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Japan',
      alpha2: 'JP',
      alpha3: 'JPN',
      'country-code': '392',
      'iso_3166-2': 'ISO 3166-2:JP',
      'region-code': '142',
      'sub-region-code': '030'
    },
    {
      name: 'Jersey',
      alpha2: 'JE',
      alpha3: 'JEY',
      'country-code': '832',
      'iso_3166-2': 'ISO 3166-2:JE',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Jordan',
      alpha2: 'JO',
      alpha3: 'JOR',
      'country-code': '400',
      'iso_3166-2': 'ISO 3166-2:JO',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Kazakhstan',
      alpha2: 'KZ',
      alpha3: 'KAZ',
      'country-code': '398',
      'iso_3166-2': 'ISO 3166-2:KZ',
      'region-code': '142',
      'sub-region-code': '143'
    },
    {
      name: 'Kenya',
      alpha2: 'KE',
      alpha3: 'KEN',
      'country-code': '404',
      'iso_3166-2': 'ISO 3166-2:KE',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Kiribati',
      alpha2: 'KI',
      alpha3: 'KIR',
      'country-code': '296',
      'iso_3166-2': 'ISO 3166-2:KI',
      'region-code': '009',
      'sub-region-code': '057'
    },
    {
      name: "Korea, Democratic People's Republic of",
      alpha2: 'KP',
      alpha3: 'PRK',
      'country-code': '408',
      'iso_3166-2': 'ISO 3166-2:KP',
      'region-code': '142',
      'sub-region-code': '030'
    },
    {
      name: 'Korea, Republic of',
      alpha2: 'KR',
      alpha3: 'KOR',
      'country-code': '410',
      'iso_3166-2': 'ISO 3166-2:KR',
      'region-code': '142',
      'sub-region-code': '030'
    },
    {
      name: 'Kuwait',
      alpha2: 'KW',
      alpha3: 'KWT',
      'country-code': '414',
      'iso_3166-2': 'ISO 3166-2:KW',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Kyrgyzstan',
      alpha2: 'KG',
      alpha3: 'KGZ',
      'country-code': '417',
      'iso_3166-2': 'ISO 3166-2:KG',
      'region-code': '142',
      'sub-region-code': '143'
    },
    {
      name: "Lao People's Democratic Republic",
      alpha2: 'LA',
      alpha3: 'LAO',
      'country-code': '418',
      'iso_3166-2': 'ISO 3166-2:LA',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Latvia',
      alpha2: 'LV',
      alpha3: 'LVA',
      'country-code': '428',
      'iso_3166-2': 'ISO 3166-2:LV',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Lebanon',
      alpha2: 'LB',
      alpha3: 'LBN',
      'country-code': '422',
      'iso_3166-2': 'ISO 3166-2:LB',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Lesotho',
      alpha2: 'LS',
      alpha3: 'LSO',
      'country-code': '426',
      'iso_3166-2': 'ISO 3166-2:LS',
      'region-code': '002',
      'sub-region-code': '018'
    },
    {
      name: 'Liberia',
      alpha2: 'LR',
      alpha3: 'LBR',
      'country-code': '430',
      'iso_3166-2': 'ISO 3166-2:LR',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Libya',
      alpha2: 'LY',
      alpha3: 'LBY',
      'country-code': '434',
      'iso_3166-2': 'ISO 3166-2:LY',
      'region-code': '002',
      'sub-region-code': '015'
    },
    {
      name: 'Liechtenstein',
      alpha2: 'LI',
      alpha3: 'LIE',
      'country-code': '438',
      'iso_3166-2': 'ISO 3166-2:LI',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'Lithuania',
      alpha2: 'LT',
      alpha3: 'LTU',
      'country-code': '440',
      'iso_3166-2': 'ISO 3166-2:LT',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Luxembourg',
      alpha2: 'LU',
      alpha3: 'LUX',
      'country-code': '442',
      'iso_3166-2': 'ISO 3166-2:LU',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'Macao',
      alpha2: 'MO',
      alpha3: 'MAC',
      'country-code': '446',
      'iso_3166-2': 'ISO 3166-2:MO',
      'region-code': '142',
      'sub-region-code': '030'
    },
    {
      name: 'Macedonia, the former Yugoslav Republic of',
      alpha2: 'MK',
      alpha3: 'MKD',
      'country-code': '807',
      'iso_3166-2': 'ISO 3166-2:MK',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Madagascar',
      alpha2: 'MG',
      alpha3: 'MDG',
      'country-code': '450',
      'iso_3166-2': 'ISO 3166-2:MG',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Malawi',
      alpha2: 'MW',
      alpha3: 'MWI',
      'country-code': '454',
      'iso_3166-2': 'ISO 3166-2:MW',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Malaysia',
      alpha2: 'MY',
      alpha3: 'MYS',
      'country-code': '458',
      'iso_3166-2': 'ISO 3166-2:MY',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Maldives',
      alpha2: 'MV',
      alpha3: 'MDV',
      'country-code': '462',
      'iso_3166-2': 'ISO 3166-2:MV',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Mali',
      alpha2: 'ML',
      alpha3: 'MLI',
      'country-code': '466',
      'iso_3166-2': 'ISO 3166-2:ML',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Malta',
      alpha2: 'MT',
      alpha3: 'MLT',
      'country-code': '470',
      'iso_3166-2': 'ISO 3166-2:MT',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Marshall Islands',
      alpha2: 'MH',
      alpha3: 'MHL',
      'country-code': '584',
      'iso_3166-2': 'ISO 3166-2:MH',
      'region-code': '009',
      'sub-region-code': '057'
    },
    {
      name: 'Martinique',
      alpha2: 'MQ',
      alpha3: 'MTQ',
      'country-code': '474',
      'iso_3166-2': 'ISO 3166-2:MQ',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Mauritania',
      alpha2: 'MR',
      alpha3: 'MRT',
      'country-code': '478',
      'iso_3166-2': 'ISO 3166-2:MR',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Mauritius',
      alpha2: 'MU',
      alpha3: 'MUS',
      'country-code': '480',
      'iso_3166-2': 'ISO 3166-2:MU',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Mayotte',
      alpha2: 'YT',
      alpha3: 'MYT',
      'country-code': '175',
      'iso_3166-2': 'ISO 3166-2:YT',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Mexico',
      alpha2: 'MX',
      alpha3: 'MEX',
      'country-code': '484',
      'iso_3166-2': 'ISO 3166-2:MX',
      'region-code': '019',
      'sub-region-code': '013'
    },
    {
      name: 'Micronesia, Federated States of',
      alpha2: 'FM',
      alpha3: 'FSM',
      'country-code': '583',
      'iso_3166-2': 'ISO 3166-2:FM',
      'region-code': '009',
      'sub-region-code': '057'
    },
    {
      name: 'Moldova, Republic of',
      alpha2: 'MD',
      alpha3: 'MDA',
      'country-code': '498',
      'iso_3166-2': 'ISO 3166-2:MD',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Monaco',
      alpha2: 'MC',
      alpha3: 'MCO',
      'country-code': '492',
      'iso_3166-2': 'ISO 3166-2:MC',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'Mongolia',
      alpha2: 'MN',
      alpha3: 'MNG',
      'country-code': '496',
      'iso_3166-2': 'ISO 3166-2:MN',
      'region-code': '142',
      'sub-region-code': '030'
    },
    {
      name: 'Montenegro',
      alpha2: 'ME',
      alpha3: 'MNE',
      'country-code': '499',
      'iso_3166-2': 'ISO 3166-2:ME',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Montserrat',
      alpha2: 'MS',
      alpha3: 'MSR',
      'country-code': '500',
      'iso_3166-2': 'ISO 3166-2:MS',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Morocco',
      alpha2: 'MA',
      alpha3: 'MAR',
      'country-code': '504',
      'iso_3166-2': 'ISO 3166-2:MA',
      'region-code': '002',
      'sub-region-code': '015'
    },
    {
      name: 'Mozambique',
      alpha2: 'MZ',
      alpha3: 'MOZ',
      'country-code': '508',
      'iso_3166-2': 'ISO 3166-2:MZ',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Myanmar',
      alpha2: 'MM',
      alpha3: 'MMR',
      'country-code': '104',
      'iso_3166-2': 'ISO 3166-2:MM',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Namibia',
      alpha2: 'NA',
      alpha3: 'NAM',
      'country-code': '516',
      'iso_3166-2': 'ISO 3166-2:NA',
      'region-code': '002',
      'sub-region-code': '018'
    },
    {
      name: 'Nauru',
      alpha2: 'NR',
      alpha3: 'NRU',
      'country-code': '520',
      'iso_3166-2': 'ISO 3166-2:NR',
      'region-code': '009',
      'sub-region-code': '057'
    },
    {
      name: 'Nepal',
      alpha2: 'NP',
      alpha3: 'NPL',
      'country-code': '524',
      'iso_3166-2': 'ISO 3166-2:NP',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Netherlands',
      alpha2: 'NL',
      alpha3: 'NLD',
      'country-code': '528',
      'iso_3166-2': 'ISO 3166-2:NL',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'New Caledonia',
      alpha2: 'NC',
      alpha3: 'NCL',
      'country-code': '540',
      'iso_3166-2': 'ISO 3166-2:NC',
      'region-code': '009',
      'sub-region-code': '054'
    },
    {
      name: 'New Zealand',
      alpha2: 'NZ',
      alpha3: 'NZL',
      'country-code': '554',
      'iso_3166-2': 'ISO 3166-2:NZ',
      'region-code': '009',
      'sub-region-code': '053'
    },
    {
      name: 'Nicaragua',
      alpha2: 'NI',
      alpha3: 'NIC',
      'country-code': '558',
      'iso_3166-2': 'ISO 3166-2:NI',
      'region-code': '019',
      'sub-region-code': '013'
    },
    {
      name: 'Niger',
      alpha2: 'NE',
      alpha3: 'NER',
      'country-code': '562',
      'iso_3166-2': 'ISO 3166-2:NE',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Nigeria',
      alpha2: 'NG',
      alpha3: 'NGA',
      'country-code': '566',
      'iso_3166-2': 'ISO 3166-2:NG',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Niue',
      alpha2: 'NU',
      alpha3: 'NIU',
      'country-code': '570',
      'iso_3166-2': 'ISO 3166-2:NU',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'Norfolk Island',
      alpha2: 'NF',
      alpha3: 'NFK',
      'country-code': '574',
      'iso_3166-2': 'ISO 3166-2:NF',
      'region-code': '009',
      'sub-region-code': '053'
    },
    {
      name: 'Northern Mariana Islands',
      alpha2: 'MP',
      alpha3: 'MNP',
      'country-code': '580',
      'iso_3166-2': 'ISO 3166-2:MP',
      'region-code': '009',
      'sub-region-code': '057'
    },
    {
      name: 'Norway',
      alpha2: 'NO',
      alpha3: 'NOR',
      'country-code': '578',
      'iso_3166-2': 'ISO 3166-2:NO',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Oman',
      alpha2: 'OM',
      alpha3: 'OMN',
      'country-code': '512',
      'iso_3166-2': 'ISO 3166-2:OM',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Pakistan',
      alpha2: 'PK',
      alpha3: 'PAK',
      'country-code': '586',
      'iso_3166-2': 'ISO 3166-2:PK',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Palau',
      alpha2: 'PW',
      alpha3: 'PLW',
      'country-code': '585',
      'iso_3166-2': 'ISO 3166-2:PW',
      'region-code': '009',
      'sub-region-code': '057'
    },
    {
      name: 'Palestine, State of',
      alpha2: 'PS',
      alpha3: 'PSE',
      'country-code': '275',
      'iso_3166-2': 'ISO 3166-2:PS',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Panama',
      alpha2: 'PA',
      alpha3: 'PAN',
      'country-code': '591',
      'iso_3166-2': 'ISO 3166-2:PA',
      'region-code': '019',
      'sub-region-code': '013'
    },
    {
      name: 'Papua New Guinea',
      alpha2: 'PG',
      alpha3: 'PNG',
      'country-code': '598',
      'iso_3166-2': 'ISO 3166-2:PG',
      'region-code': '009',
      'sub-region-code': '054'
    },
    {
      name: 'Paraguay',
      alpha2: 'PY',
      alpha3: 'PRY',
      'country-code': '600',
      'iso_3166-2': 'ISO 3166-2:PY',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Peru',
      alpha2: 'PE',
      alpha3: 'PER',
      'country-code': '604',
      'iso_3166-2': 'ISO 3166-2:PE',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Philippines',
      alpha2: 'PH',
      alpha3: 'PHL',
      'country-code': '608',
      'iso_3166-2': 'ISO 3166-2:PH',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Pitcairn',
      alpha2: 'PN',
      alpha3: 'PCN',
      'country-code': '612',
      'iso_3166-2': 'ISO 3166-2:PN',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'Poland',
      alpha2: 'PL',
      alpha3: 'POL',
      'country-code': '616',
      'iso_3166-2': 'ISO 3166-2:PL',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Portugal',
      alpha2: 'PT',
      alpha3: 'PRT',
      'country-code': '620',
      'iso_3166-2': 'ISO 3166-2:PT',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Puerto Rico',
      alpha2: 'PR',
      alpha3: 'PRI',
      'country-code': '630',
      'iso_3166-2': 'ISO 3166-2:PR',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Qatar',
      alpha2: 'QA',
      alpha3: 'QAT',
      'country-code': '634',
      'iso_3166-2': 'ISO 3166-2:QA',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Réunion',
      alpha2: 'RE',
      alpha3: 'REU',
      'country-code': '638',
      'iso_3166-2': 'ISO 3166-2:RE',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Romania',
      alpha2: 'RO',
      alpha3: 'ROU',
      'country-code': '642',
      'iso_3166-2': 'ISO 3166-2:RO',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Russian Federation',
      alpha2: 'RU',
      alpha3: 'RUS',
      'country-code': '643',
      'iso_3166-2': 'ISO 3166-2:RU',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Rwanda',
      alpha2: 'RW',
      alpha3: 'RWA',
      'country-code': '646',
      'iso_3166-2': 'ISO 3166-2:RW',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Saint Barthélemy',
      alpha2: 'BL',
      alpha3: 'BLM',
      'country-code': '652',
      'iso_3166-2': 'ISO 3166-2:BL',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Saint Helena, Ascension and Tristan da Cunha',
      alpha2: 'SH',
      alpha3: 'SHN',
      'country-code': '654',
      'iso_3166-2': 'ISO 3166-2:SH',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Saint Kitts and Nevis',
      alpha2: 'KN',
      alpha3: 'KNA',
      'country-code': '659',
      'iso_3166-2': 'ISO 3166-2:KN',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Saint Lucia',
      alpha2: 'LC',
      alpha3: 'LCA',
      'country-code': '662',
      'iso_3166-2': 'ISO 3166-2:LC',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Saint Martin (French part)',
      alpha2: 'MF',
      alpha3: 'MAF',
      'country-code': '663',
      'iso_3166-2': 'ISO 3166-2:MF',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Saint Pierre and Miquelon',
      alpha2: 'PM',
      alpha3: 'SPM',
      'country-code': '666',
      'iso_3166-2': 'ISO 3166-2:PM',
      'region-code': '019',
      'sub-region-code': '021'
    },
    {
      name: 'Saint Vincent and the Grenadines',
      alpha2: 'VC',
      alpha3: 'VCT',
      'country-code': '670',
      'iso_3166-2': 'ISO 3166-2:VC',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Samoa',
      alpha2: 'WS',
      alpha3: 'WSM',
      'country-code': '882',
      'iso_3166-2': 'ISO 3166-2:WS',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'San Marino',
      alpha2: 'SM',
      alpha3: 'SMR',
      'country-code': '674',
      'iso_3166-2': 'ISO 3166-2:SM',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Sao Tome and Principe',
      alpha2: 'ST',
      alpha3: 'STP',
      'country-code': '678',
      'iso_3166-2': 'ISO 3166-2:ST',
      'region-code': '002',
      'sub-region-code': '017'
    },
    {
      name: 'Saudi Arabia',
      alpha2: 'SA',
      alpha3: 'SAU',
      'country-code': '682',
      'iso_3166-2': 'ISO 3166-2:SA',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Senegal',
      alpha2: 'SN',
      alpha3: 'SEN',
      'country-code': '686',
      'iso_3166-2': 'ISO 3166-2:SN',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Serbia',
      alpha2: 'RS',
      alpha3: 'SRB',
      'country-code': '688',
      'iso_3166-2': 'ISO 3166-2:RS',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Seychelles',
      alpha2: 'SC',
      alpha3: 'SYC',
      'country-code': '690',
      'iso_3166-2': 'ISO 3166-2:SC',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Sierra Leone',
      alpha2: 'SL',
      alpha3: 'SLE',
      'country-code': '694',
      'iso_3166-2': 'ISO 3166-2:SL',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Singapore',
      alpha2: 'SG',
      alpha3: 'SGP',
      'country-code': '702',
      'iso_3166-2': 'ISO 3166-2:SG',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Sint Maarten (Dutch part)',
      alpha2: 'SX',
      alpha3: 'SXM',
      'country-code': '534',
      'iso_3166-2': 'ISO 3166-2:SX',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Slovakia',
      alpha2: 'SK',
      alpha3: 'SVK',
      'country-code': '703',
      'iso_3166-2': 'ISO 3166-2:SK',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'Slovenia',
      alpha2: 'SI',
      alpha3: 'SVN',
      'country-code': '705',
      'iso_3166-2': 'ISO 3166-2:SI',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Solomon Islands',
      alpha2: 'SB',
      alpha3: 'SLB',
      'country-code': '090',
      'iso_3166-2': 'ISO 3166-2:SB',
      'region-code': '009',
      'sub-region-code': '054'
    },
    {
      name: 'Somalia',
      alpha2: 'SO',
      alpha3: 'SOM',
      'country-code': '706',
      'iso_3166-2': 'ISO 3166-2:SO',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'South Africa',
      alpha2: 'ZA',
      alpha3: 'ZAF',
      'country-code': '710',
      'iso_3166-2': 'ISO 3166-2:ZA',
      'region-code': '002',
      'sub-region-code': '018'
    },
    {
      name: 'South Georgia and the South Sandwich Islands',
      alpha2: 'GS',
      alpha3: 'SGS',
      'country-code': '239',
      'iso_3166-2': 'ISO 3166-2:GS'
    },
    {
      name: 'South Sudan',
      alpha2: 'SS',
      alpha3: 'SSD',
      'country-code': '728',
      'iso_3166-2': 'ISO 3166-2:SS',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Spain',
      alpha2: 'ES',
      alpha3: 'ESP',
      'country-code': '724',
      'iso_3166-2': 'ISO 3166-2:ES',
      'region-code': '150',
      'sub-region-code': '039'
    },
    {
      name: 'Sri Lanka',
      alpha2: 'LK',
      alpha3: 'LKA',
      'country-code': '144',
      'iso_3166-2': 'ISO 3166-2:LK',
      'region-code': '142',
      'sub-region-code': '034'
    },
    {
      name: 'Sudan',
      alpha2: 'SD',
      alpha3: 'SDN',
      'country-code': '729',
      'iso_3166-2': 'ISO 3166-2:SD',
      'region-code': '002',
      'sub-region-code': '015'
    },
    {
      name: 'Suriname',
      alpha2: 'SR',
      alpha3: 'SUR',
      'country-code': '740',
      'iso_3166-2': 'ISO 3166-2:SR',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Svalbard and Jan Mayen',
      alpha2: 'SJ',
      alpha3: 'SJM',
      'country-code': '744',
      'iso_3166-2': 'ISO 3166-2:SJ',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Swaziland',
      alpha2: 'SZ',
      alpha3: 'SWZ',
      'country-code': '748',
      'iso_3166-2': 'ISO 3166-2:SZ',
      'region-code': '002',
      'sub-region-code': '018'
    },
    {
      name: 'Sweden',
      alpha2: 'SE',
      alpha3: 'SWE',
      'country-code': '752',
      'iso_3166-2': 'ISO 3166-2:SE',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'Switzerland',
      alpha2: 'CH',
      alpha3: 'CHE',
      'country-code': '756',
      'iso_3166-2': 'ISO 3166-2:CH',
      'region-code': '150',
      'sub-region-code': '155'
    },
    {
      name: 'Syrian Arab Republic',
      alpha2: 'SY',
      alpha3: 'SYR',
      'country-code': '760',
      'iso_3166-2': 'ISO 3166-2:SY',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Taiwan, Province of China',
      alpha2: 'TW',
      alpha3: 'TWN',
      'country-code': '158',
      'iso_3166-2': 'ISO 3166-2:TW',
      'region-code': '142',
      'sub-region-code': '030'
    },
    {
      name: 'Tajikistan',
      alpha2: 'TJ',
      alpha3: 'TJK',
      'country-code': '762',
      'iso_3166-2': 'ISO 3166-2:TJ',
      'region-code': '142',
      'sub-region-code': '143'
    },
    {
      name: 'Tanzania, United Republic of',
      alpha2: 'TZ',
      alpha3: 'TZA',
      'country-code': '834',
      'iso_3166-2': 'ISO 3166-2:TZ',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Thailand',
      alpha2: 'TH',
      alpha3: 'THA',
      'country-code': '764',
      'iso_3166-2': 'ISO 3166-2:TH',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Timor-Leste',
      alpha2: 'TL',
      alpha3: 'TLS',
      'country-code': '626',
      'iso_3166-2': 'ISO 3166-2:TL',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Togo',
      alpha2: 'TG',
      alpha3: 'TGO',
      'country-code': '768',
      'iso_3166-2': 'ISO 3166-2:TG',
      'region-code': '002',
      'sub-region-code': '011'
    },
    {
      name: 'Tokelau',
      alpha2: 'TK',
      alpha3: 'TKL',
      'country-code': '772',
      'iso_3166-2': 'ISO 3166-2:TK',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'Tonga',
      alpha2: 'TO',
      alpha3: 'TON',
      'country-code': '776',
      'iso_3166-2': 'ISO 3166-2:TO',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'Trinidad and Tobago',
      alpha2: 'TT',
      alpha3: 'TTO',
      'country-code': '780',
      'iso_3166-2': 'ISO 3166-2:TT',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Tunisia',
      alpha2: 'TN',
      alpha3: 'TUN',
      'country-code': '788',
      'iso_3166-2': 'ISO 3166-2:TN',
      'region-code': '002',
      'sub-region-code': '015'
    },
    {
      name: 'Turkey',
      alpha2: 'TR',
      alpha3: 'TUR',
      'country-code': '792',
      'iso_3166-2': 'ISO 3166-2:TR',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Turkmenistan',
      alpha2: 'TM',
      alpha3: 'TKM',
      'country-code': '795',
      'iso_3166-2': 'ISO 3166-2:TM',
      'region-code': '142',
      'sub-region-code': '143'
    },
    {
      name: 'Turks and Caicos Islands',
      alpha2: 'TC',
      alpha3: 'TCA',
      'country-code': '796',
      'iso_3166-2': 'ISO 3166-2:TC',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Tuvalu',
      alpha2: 'TV',
      alpha3: 'TUV',
      'country-code': '798',
      'iso_3166-2': 'ISO 3166-2:TV',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'Uganda',
      alpha2: 'UG',
      alpha3: 'UGA',
      'country-code': '800',
      'iso_3166-2': 'ISO 3166-2:UG',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Ukraine',
      alpha2: 'UA',
      alpha3: 'UKR',
      'country-code': '804',
      'iso_3166-2': 'ISO 3166-2:UA',
      'region-code': '150',
      'sub-region-code': '151'
    },
    {
      name: 'United Arab Emirates',
      alpha2: 'AE',
      alpha3: 'ARE',
      'country-code': '784',
      'iso_3166-2': 'ISO 3166-2:AE',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'United Kingdom',
      alpha2: 'GB',
      alpha3: 'GBR',
      'country-code': '826',
      'iso_3166-2': 'ISO 3166-2:GB',
      'region-code': '150',
      'sub-region-code': '154'
    },
    {
      name: 'United States',
      alpha2: 'US',
      alpha3: 'USA',
      'country-code': '840',
      'iso_3166-2': 'ISO 3166-2:US',
      'region-code': '019',
      'sub-region-code': '021'
    },
    {
      name: 'United States Minor Outlying Islands',
      alpha2: 'UM',
      alpha3: 'UMI',
      'country-code': '581',
      'iso_3166-2': 'ISO 3166-2:UM'
    },
    {
      name: 'Uruguay',
      alpha2: 'UY',
      alpha3: 'URY',
      'country-code': '858',
      'iso_3166-2': 'ISO 3166-2:UY',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Uzbekistan',
      alpha2: 'UZ',
      alpha3: 'UZB',
      'country-code': '860',
      'iso_3166-2': 'ISO 3166-2:UZ',
      'region-code': '142',
      'sub-region-code': '143'
    },
    {
      name: 'Vanuatu',
      alpha2: 'VU',
      alpha3: 'VUT',
      'country-code': '548',
      'iso_3166-2': 'ISO 3166-2:VU',
      'region-code': '009',
      'sub-region-code': '054'
    },
    {
      name: 'Venezuela, Bolivarian Republic of',
      alpha2: 'VE',
      alpha3: 'VEN',
      'country-code': '862',
      'iso_3166-2': 'ISO 3166-2:VE',
      'region-code': '019',
      'sub-region-code': '005'
    },
    {
      name: 'Viet Nam',
      alpha2: 'VN',
      alpha3: 'VNM',
      'country-code': '704',
      'iso_3166-2': 'ISO 3166-2:VN',
      'region-code': '142',
      'sub-region-code': '035'
    },
    {
      name: 'Virgin Islands, British',
      alpha2: 'VG',
      alpha3: 'VGB',
      'country-code': '092',
      'iso_3166-2': 'ISO 3166-2:VG',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Virgin Islands, U.S.',
      alpha2: 'VI',
      alpha3: 'VIR',
      'country-code': '850',
      'iso_3166-2': 'ISO 3166-2:VI',
      'region-code': '019',
      'sub-region-code': '029'
    },
    {
      name: 'Wallis and Futuna',
      alpha2: 'WF',
      alpha3: 'WLF',
      'country-code': '876',
      'iso_3166-2': 'ISO 3166-2:WF',
      'region-code': '009',
      'sub-region-code': '061'
    },
    {
      name: 'Western Sahara',
      alpha2: 'EH',
      alpha3: 'ESH',
      'country-code': '732',
      'iso_3166-2': 'ISO 3166-2:EH',
      'region-code': '002',
      'sub-region-code': '015'
    },
    {
      name: 'Yemen',
      alpha2: 'YE',
      alpha3: 'YEM',
      'country-code': '887',
      'iso_3166-2': 'ISO 3166-2:YE',
      'region-code': '142',
      'sub-region-code': '145'
    },
    {
      name: 'Zambia',
      alpha2: 'ZM',
      alpha3: 'ZMB',
      'country-code': '894',
      'iso_3166-2': 'ISO 3166-2:ZM',
      'region-code': '002',
      'sub-region-code': '014'
    },
    {
      name: 'Zimbabwe',
      alpha2: 'ZW',
      alpha3: 'ZWE',
      'country-code': '716',
      'iso_3166-2': 'ISO 3166-2:ZW',
      'region-code': '002',
      'sub-region-code': '014'
    }
  ],
  getCountryFromName: function(name) {
    for (let i = 0; i < this.ISO_3166.length; i++) {
      if (this.ISO_3166[i].name.toLowerCase().indexOf(name.toLowerCase()) > -1) {
        return this.ISO_3166[i];
      }
    }
    return null;
  },
  getCountryFromCode: function(code) {
    for (let i = 0; i < this.ISO_3166.length; i++) {
      if (
        code.toLowerCase().indexOf(this.ISO_3166[i].alpha2.toLowerCase()) > -1 ||
        code.toLowerCase().indexOf(this.ISO_3166[i].alpha3.toLowerCase()) > -1
      ) {
        return this.ISO_3166[i];
      }
    }
    return null;
  },
  getISOAlpha2: function(code) {
    const _country = HueGeo.getCountryFromCode(code);
    return _country ? _country.alpha2 : 'AQ';
  },
  getISOAlpha3: function(code) {
    const _country = HueGeo.getCountryFromCode(code);
    return _country ? _country.alpha3 : 'ATA';
  },
  getCity: function(city, callback) {
    const api = new NominatimAPI();
    api.lookupCity(city, rawdata => {
      if (rawdata.length > 1) {
        callback(rawdata);
      } else {
        callback(rawdata[0]);
      }
    });
  },
  getCityCoordinates: function(city, callback) {
    const api = new NominatimAPI();
    api.lookupCity(city, rawdata => {
      if (rawdata.length > 1) {
        callback(rawdata);
      } else {
        callback(rawdata[0].lat, rawdata[0].lon);
      }
    });
  },
  getAddressFromCoordinates: function(lat, lng, callback) {
    const api = new NominatimAPI();
    api.lookupAddress(lat + ',' + lng, rawdata => {
      if (rawdata.length > 1) {
        callback(rawdata);
      } else {
        callback(rawdata[0].display_name);
      }
    });
  },

  getAddressCoordinates: function(address, callback) {
    const api = new NominatimAPI();
    api.lookupAddress(address, rawdata => {
      if (rawdata.length > 1) {
        callback(rawdata);
      } else {
        callback(rawdata[0].lat, rawdata[0].lon);
      }
    });
  }
};

export default HueGeo;
