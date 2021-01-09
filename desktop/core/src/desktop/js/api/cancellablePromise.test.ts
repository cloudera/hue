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

import { noop } from 'lodash';

import { CancellablePromise } from './cancellablePromise';

describe('cancellablePromise.ts', () => {
  it('it should not reject a running promise when cancelled', async () => {
    let resolved = false;
    let rejected = false;
    let resolveHandler: () => void = noop;
    const subject = new CancellablePromise<void>(resolve => {
      resolveHandler = resolve;
    });
    subject.cancel();
    if (resolveHandler) {
      resolveHandler();
    }
    try {
      await subject;
      resolved = true;
    } catch {
      rejected = true;
    }
    expect(resolved).toBeTruthy();
    expect(rejected).toBeFalsy();
  });

  it('it should set cancelled on cancel of a running promise', () => {
    const subject = new CancellablePromise<void>(() => {
      // Do nothing
    });
    subject.catch(noop);
    expect(subject.cancelled).toBeFalsy();
    subject.cancel();
    expect(subject.cancelled).toBeTruthy();
  });

  it('should not cancel a resolved promises', () => {
    const subject = CancellablePromise.resolve();
    subject.catch(noop);
    subject.cancel();
    expect(subject.cancelled).toBeFalsy();
  });

  it('should not cancel a rejected promises', () => {
    const subject = CancellablePromise.reject();
    subject.catch(noop);
    subject.cancel();
    expect(subject.cancelled).toBeFalsy();
  });

  it('should not call onCancel on a resolved promises', () => {
    let onCancelCalled = false;
    const subject = new CancellablePromise<void>((resolve, reject, onCancel) => {
      onCancel(() => {
        onCancelCalled = true;
      });
      resolve();
    });
    subject.catch(noop);
    subject.cancel();
    expect(onCancelCalled).toBeFalsy();
  });

  it('should not call onCancel on a rejected promises', () => {
    let onCancelCalled = false;
    const subject = new CancellablePromise<void>((resolve, reject, onCancel) => {
      onCancel(() => {
        onCancelCalled = true;
      });
      reject('banana');
    });
    subject.catch(noop);
    subject.cancel();
    expect(onCancelCalled).toBeFalsy();
  });
});
