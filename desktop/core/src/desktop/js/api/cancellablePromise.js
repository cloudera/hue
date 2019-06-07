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
import apiHelper from 'api/apiHelper';

class CancellablePromise {
  constructor(deferred, request, otherCancellables) {
    const self = this;
    self.cancelCallbacks = [];
    self.deferred = deferred;
    self.request = request;
    self.otherCancellables = otherCancellables;
    self.cancelled = false;
    self.cancelPrevented = false;
  }

  /**
   * A promise might be shared across multiple components in the UI, in some cases cancel is not an option and calling
   * this will prevent that to happen.
   *
   * One example is autocompletion of databases while the assist is loading the database tree, closing the autocomplete
   * results would make the assist loading fail if cancel hasn't been prevented.
   *
   * @returns {CancellablePromise}
   */
  preventCancel() {
    const self = this;
    self.cancelPrevented = true;
    return self;
  }

  cancel() {
    const self = this;
    if (self.cancelPrevented || self.cancelled || self.state() !== 'pending') {
      return $.Deferred()
        .resolve()
        .promise();
    }

    self.cancelled = true;
    if (self.request) {
      apiHelper.cancelActiveRequest(self.request);
    }

    if (self.state && self.state() === 'pending' && self.deferred.reject) {
      self.deferred.reject();
    }

    const cancelPromises = [];
    if (self.otherCancellables) {
      self.otherCancellables.forEach(cancellable => {
        if (cancellable.cancel) {
          cancelPromises.push(cancellable.cancel());
        }
      });
    }

    while (self.cancelCallbacks.length) {
      self.cancelCallbacks.pop()();
    }
    return $.when(cancelPromises);
  }

  onCancel(callback) {
    const self = this;
    if (self.cancelled) {
      callback();
    } else {
      self.cancelCallbacks.push(callback);
    }
    return self;
  }

  then() {
    const self = this;
    self.deferred.then.apply(self.deferred, arguments);
    return self;
  }

  done(callback) {
    const self = this;
    self.deferred.done.apply(self.deferred, arguments);
    return self;
  }

  fail(callback) {
    const self = this;
    self.deferred.fail.apply(self.deferred, arguments);
    return self;
  }

  always(callback) {
    const self = this;
    self.deferred.always.apply(self.deferred, arguments);
    return self;
  }

  pipe(callback) {
    const self = this;
    self.deferred.pipe.apply(self.deferred, arguments);
    return self;
  }

  progress(callback) {
    const self = this;
    self.deferred.progress.apply(self.deferred, arguments);
    return self;
  }

  state() {
    const self = this;
    return self.deferred.state && self.deferred.state();
  }
}

export default CancellablePromise;
