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

import hueUtils from '../hueUtils';

describe('hue.utils.js', () => {
  // In polyfills.js
  // it("should skip the milliseconds in number format if the time is more than 60 seconds", function() {
  //   expect(Number(10000000344).toHHMMSS()).toEqual('115d, 17h, 46m, 40s');
  // });

  // In polyfills.js
  // it("should show the milliseconds in number format if the time is less than 60 seconds", function() {
  //   expect(Number(10123).toHHMMSS()).toEqual('10.12s');
  // });

  // In polyfills.js
  // it("should skip the seconds if it's zero and it's specified in the function", function() {
  //   expect(Number(60000).toHHMMSS(true)).toEqual('1m');
  // });

  // In polyfills.js
  // it("should have the String.startsWith polyfill", function() {
  //   expect('banana'.startsWith('ba')).toBeTruthy();
  // });

  // In polyfills.js
  // it("should have the String.endsWith polyfill", function() {
  //   expect('banana'.endsWith('na')).toBeTruthy();
  // });

  // In polyfills.js
  // it("should have the String.includes polyfill", function() {
  //   expect('banana'.includes('anan')).toBeTruthy();
  // });

  it('should change completely the URL', () => {
    hueUtils.changeURL('/banana');
    expect(window.location.pathname).toEqual('/banana');
    hueUtils.changeURL('/jasmine');
  });

  it('should change just a parameter in the URL', () => {
    hueUtils.changeURL('/banana?peeled=no');
    hueUtils.changeURLParameter('peeled', 'yes');
    expect(window.location.search).toEqual('?peeled=yes');
    hueUtils.changeURL('/jasmine');
  });

  it('should remove a parameter in the URL', () => {
    hueUtils.changeURL('/banana?peeled=no');
    hueUtils.removeURLParameter('peeled');
    expect(window.location.search).toEqual('');
    hueUtils.changeURL('/jasmine');
  });

  it('should remove JS code from a string', () => {
    expect(hueUtils.deXSS('hello <script>alert(123)</script>world')).toEqual('hello world');
  });
});
