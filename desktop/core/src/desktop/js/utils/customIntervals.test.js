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

import './customIntervals';

describe('hue4.utils.js', () => {
  let intervalCallback;

  beforeEach(() => {
    intervalCallback = jest.fn();
  });

  it('should accept both formats of window.setInterval', () => {
    const id1 = window.setInterval(intervalCallback, 100);
    const id2 = window.setInterval(intervalCallback, 100, 'jest');

    expect(id1).toBeGreaterThan(0);
    expect(id2).toBeGreaterThan(0);
    window.clearInterval(id1);
    window.clearInterval(id2);
  });

  it('should make the hue setInterval behave like the default window.setInterval', () => {
    jest.useFakeTimers();
    const id = window.setInterval(intervalCallback, 10);

    expect(intervalCallback).not.toHaveBeenCalled();
    jest.advanceTimersByTime(11);

    expect(intervalCallback).toHaveBeenCalled();
    window.clearInterval(id);
  });

  // TODO: Disabled as setInterval doesn't seem to work with jsdom
  xit('should pause and resume all the intervals of an app', done => {
    const id = window.setInterval(intervalCallback, 10, 'jest-dash');

    expect(intervalCallback).not.toHaveBeenCalled();
    window.pauseAppIntervals('jest');
    window.setTimeout(() => {
      expect(intervalCallback).not.toHaveBeenCalled();
      window.resumeAppIntervals('jest');
      window.setTimeout(() => {
        expect(intervalCallback).toHaveBeenCalled();
        window.clearInterval(id);
        done();
      }, 20);
      jest.advanceTimersByTime(21);
    }, 20);
    jest.advanceTimersByTime(21);
  });

  // TODO: Disabled as setInterval doesn't seem to work with jsdom
  xit('should clear the original interval id after a pause and resume', done => {
    const id = window.setInterval(intervalCallback, 30, 'jest-dash');

    expect(intervalCallback).not.toHaveBeenCalled();
    window.pauseAppIntervals('jest');
    window.resumeAppIntervals('jest');
    window.clearInterval(id);
    window.setTimeout(() => {
      expect(intervalCallback).not.toHaveBeenCalled();
      done();
    }, 20);
  });
});
