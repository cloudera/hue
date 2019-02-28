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

import '../customIntervals';

(function() {
  describe('hue4.utils.js', () => {
    beforeEach(function() {
      this.intervalCallback = jasmine.createSpy('intervalCallback');
    });

    // TODO: Disabled as setInterval doesn't seem to work with jsdom

    // it("should accept both formats of window.setInterval", function () {
    //   var id1 = window.setInterval(this.intervalCallback, 100);
    //   var id2 = window.setInterval(this.intervalCallback, 100, 'jasmine');
    //   expect(id1).toBeGreaterThan(0);
    //   expect(id2).toBeGreaterThan(0);
    //   window.clearInterval(id1);
    //   window.clearInterval(id2);
    // });

    // it("should make the hue setInterval behave like the default window.setInterval", function () {
    //   jasmine.clock().install();
    //   var id = window.setInterval(this.intervalCallback, 10);
    //   expect(this.intervalCallback).not.toHaveBeenCalled();
    //   jasmine.clock().tick(11);
    //   expect(this.intervalCallback).toHaveBeenCalled();
    //   window.clearInterval(id);
    //   jasmine.clock().uninstall();
    // });

    // it("should pause and resume all the intervals of an app", function (done) {
    //   var id = window.setInterval(this.intervalCallback, 10, 'jasmine-dash');
    //   expect(this.intervalCallback).not.toHaveBeenCalled();
    //   window.pauseAppIntervals('jasmine');
    //   window.setTimeout(function () {
    //     expect(this.intervalCallback).not.toHaveBeenCalled();
    //     window.resumeAppIntervals('jasmine');
    //     window.setTimeout(function () {
    //       expect(this.intervalCallback).toHaveBeenCalled();
    //       window.clearInterval(id);
    //       done();
    //     }, 20);
    //   }, 20)
    // });

    // it("should clear the original interval id after a pause and resume", function (done) {
    //   var id = window.setInterval(this.intervalCallback, 30, 'jasmine-dash');
    //   expect(this.intervalCallback).not.toHaveBeenCalled();
    //   window.pauseAppIntervals('jasmine');
    //   window.resumeAppIntervals('jasmine');
    //   window.clearInterval(id);
    //   window.setTimeout(function () {
    //     expect(this.intervalCallback).not.toHaveBeenCalled();
    //     done();
    //   }, 20)
    // });
  });
})();
