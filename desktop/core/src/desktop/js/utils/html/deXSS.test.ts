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

import deXSS from './deXSS';

describe('deXSS.ts', () => {
  it('should return empty string when the value is undefined', () => {
    expect(deXSS(undefined)).toEqual('');
  });

  it('should return false when the value is false', () => {
    expect(deXSS(false)).toEqual('false');
  });

  it('should return 0 when the value is 0', () => {
    expect(deXSS(0)).toEqual('0');
  });

  it('should return null when the value is null', () => {
    expect(deXSS(null)).toEqual('null');
  });

  it('should remove JS code from a string', () => {
    expect(deXSS('hello <script>alert(123)</script>world')).toEqual('hello world');
  });

  it('Should not remove strong tag from a string', () => {
    expect(deXSS('<strong>Hello World</strong>')).toEqual('<strong>Hello World</strong>');
  });

  it('Should remove img tag from a string', () => {
    expect(deXSS('<img src=asf onerror=alert(document.cookie) />hello')).toEqual('hello');
  });

  it('Should not remove p tag from a string', () => {
    expect(deXSS('<p> Hello World </p>')).toEqual('<p> Hello World </p>');
  });

  it('Should not remove h1 tag from a string', () => {
    expect(deXSS('<h1> Hello World </h1>')).toEqual('<h1> Hello World </h1>');
  });

  it('should preserve entities as such', () => {
    expect(deXSS('<a name="&lt;silly&gt;">&lt;Kapow!&gt;</a>')).toEqual(
      '<a name="&lt;silly&gt;">&lt;Kapow!&gt;</a>'
    );
  });

  it('should dump comments', () => {
    expect(deXSS('<p><!-- Blah blah -->Whee</p>')).toEqual('<p>Whee</p>');
  });

  it('should dump an uppercase javascript url', () => {
    expect(deXSS('<a href="JAVASCRIPT:alert(\'foo\')">Hax</a>')).toEqual('<a>Hax</a>');
  });
});
