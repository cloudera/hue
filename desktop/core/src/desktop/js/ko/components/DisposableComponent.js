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

export default class DisposableComponent {
  constructor() {
    this.disposals = [];
  }

  subscribe(subscribable, callback) {
    if (typeof subscribable === 'string') {
      const pubSub = huePubSub.subscribe(subscribable, callback);
      this.disposals.push(() => {
        pubSub.remove();
      });
      return pubSub;
    }
    if (subscribable.subscribe) {
      const sub = subscribable.subscribe(callback);
      this.disposals.push(() => {
        sub.dispose();
      });
      return sub;
    }
  }

  addDisposalCallback(callback) {
    this.disposals.push(callback);
  }

  dispose() {
    while (this.disposals.length) {
      try {
        this.disposals.pop()();
      } catch (err) {
        console.warn(err);
      }
    }
  }
}
