/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

import { breakLongComments } from './formattingUtils';

describe('formattingUtils', () => {
  describe('breakLongComments', () => {
    it('should break long comments that use /* */ after around 70 characters', () => {
      const sql = `Select * \n/* this is a very long comment that should have a line break in it somehwere arund after 70 characters without splitting words */\nfrom table`;
      const sqlWithLineBreaks = `Select * \n/* this is a very long comment that should have a line break in it \nsomehwere arund after 70 characters without splitting words */ \nfrom table`;
      expect(breakLongComments(sql)).toEqual(sqlWithLineBreaks);
    });
    it('should break multiple long comments that use /* */ in the same SQL after around 70 characters', () => {
      const sql = `/* this is a very long comment that should have a line break in it somehwere arund after 70 characters without splitting words */\nSelect * \n/* this is a very long comment that should have a line break in it somehwere arund after 70 characters without splitting words */\nfrom table`;
      const sqlWithLineBreaks = `/* this is a very long comment that should have a line break in it \nsomehwere arund after 70 characters without splitting words */ \nSelect * \n/* this is a very long comment that should have a line break in it \nsomehwere arund after 70 characters without splitting words */ \nfrom table`;
      expect(breakLongComments(sql)).toEqual(sqlWithLineBreaks);
    });
    it('should break long comments that use /* */ after a custom length of characters', () => {
      const sql = `Select * \n/* this is a very long comment that should have a line break in it somehwere arund after 70 characters without splitting words */\nfrom table`;
      const sqlWithLineBreaks = `Select * \n/* this is a very long comment that should have a line break in it somehwere arund after \n70 characters without splitting words */ \nfrom table`;
      expect(breakLongComments(sql, 90)).toEqual(sqlWithLineBreaks);
    });
    it('should not break short comments that use /* */', () => {
      const sql = `Select * \n/* this is a short comment and should not be split */\nfrom table`;
      expect(breakLongComments(sql)).toEqual(sql);
    });
    it('should not break long comments that use --', () => {
      const sql = `Select * \n-- this is a very long comment that should have a line break in it somehwere arund after 70 characters without splitting words \nfrom table`;
      expect(breakLongComments(sql)).toEqual(sql);
    });
  });
});
