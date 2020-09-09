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

import { Cancellable } from 'api/cancellablePromise';
import $ from 'jquery';
import { cancelActiveRequest } from './apiUtils';

export default class CancellableJqPromise<T> implements Cancellable {
  cancelCallbacks: (() => void)[] = [];
  deferred: JQuery.Deferred<T>;
  request?: JQuery.jqXHR;
  otherCancellables?: CancellableJqPromise<unknown>[];
  cancelled = false;
  cancelPrevented = false;

  constructor(
    deferred: JQuery.Deferred<T>,
    request?: JQuery.jqXHR,
    otherCancellables?: CancellableJqPromise<unknown>[]
  ) {
    this.deferred = deferred;
    this.request = request;
    this.otherCancellables = otherCancellables;
  }

  /**
   * A promise might be shared across multiple components in the UI, in some cases cancel is not an option and calling
   * this will prevent that to happen.
   *
   * One example is autocompletion of databases while the assist is loading the database tree, closing the autocomplete
   * results would make the assist loading fail if cancel hasn't been prevented.
   *
   * @returns {CancellableJqPromise}
   */
  preventCancel(): CancellableJqPromise<T> {
    this.cancelPrevented = true;
    return this;
  }

  cancel(): JQuery.Promise<unknown> {
    if (this.cancelPrevented || this.cancelled || this.state() !== 'pending') {
      return $.Deferred().resolve().promise();
    }

    this.cancelled = true;
    if (this.request) {
      cancelActiveRequest(this.request);
    }

    if (this.state && this.state() === 'pending' && this.deferred.reject) {
      this.deferred.reject();
    }

    const cancelPromises: JQuery.Promise<unknown>[] = [];
    if (this.otherCancellables) {
      this.otherCancellables.forEach(cancellable => {
        if (cancellable.cancel) {
          cancelPromises.push(cancellable.cancel());
        }
      });
    }

    while (this.cancelCallbacks.length) {
      const fn = this.cancelCallbacks.pop();
      if (fn) {
        fn();
      }
    }
    return $.when(cancelPromises);
  }

  onCancel(callback: () => void): CancellableJqPromise<T> {
    if (this.cancelled) {
      callback();
    } else {
      this.cancelCallbacks.push(callback);
    }
    return this;
  }

  then(then: (result: T) => void): CancellableJqPromise<T> {
    this.deferred.then(then);
    return this;
  }

  done(done: (result: T) => void): CancellableJqPromise<T> {
    this.deferred.done(done);
    return this;
  }

  fail(fail: (error: unknown) => void): CancellableJqPromise<T> {
    this.deferred.fail(fail);
    return this;
  }

  always(always: (result: T) => void): CancellableJqPromise<T> {
    this.deferred.always(always);
    return this;
  }

  pipe(pipe: (result: T) => void): CancellableJqPromise<T> {
    this.deferred.pipe(pipe);
    return this;
  }

  progress(progress: (progress: unknown) => void): CancellableJqPromise<T> {
    this.deferred.progress(progress);
    return this;
  }

  state(): string {
    return this.deferred.state && this.deferred.state();
  }
}
