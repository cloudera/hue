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

import huePubSub from 'utils/huePubSub';

export interface Disposable {
  dispose(): void;
}

export default class SubscriptionTracker {
  disposals: (() => void)[] = [];

  subscribe(
    subscribable: string | KnockoutSubscribable<unknown>,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    callback: (...args: any[]) => any
  ): void {
    if (typeof subscribable === 'string') {
      const pubSub = huePubSub.subscribe(subscribable, callback);
      this.disposals.push(() => {
        pubSub.remove();
      });
    } else if (subscribable.subscribe) {
      const sub = subscribable.subscribe(callback);
      this.disposals.push(() => {
        sub.dispose();
      });
    }
  }

  addDisposable(disposable: Disposable): void {
    this.disposals.push(disposable.dispose.bind(disposable));
  }

  trackTimeout(timeout: number): void {
    this.disposals.push(() => {
      window.clearTimeout(timeout);
    });
  }

  dispose(): void {
    while (this.disposals.length) {
      try {
        const disposeFn = this.disposals.pop();
        if (disposeFn) {
          disposeFn();
        }
      } catch (err) {
        console.warn(err);
      }
    }
  }
}
