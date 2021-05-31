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

import { onBeforeUnmount, Ref, watch } from 'vue';
import KnockoutObservable from '@types/knockout';

import huePubSub from 'utils/huePubSub';

export interface Disposable {
  dispose(): void;
}

const valueOrNull = <T>(val?: T): T | null => (typeof val === 'undefined' ? null : val);

export default class SubscriptionTracker {
  disposed = false;
  disposals: (() => void)[] = [];

  constructor() {
    onBeforeUnmount(this.dispose.bind(this));
  }

  addDisposable(disposable: Disposable): void {
    this.disposals.push(disposable.dispose.bind(disposable));
  }

  addEventListener<K extends keyof HTMLElementEventMap>(
    element: HTMLElement | Document,
    type: K,
    listener: (ev: HTMLElementEventMap[K]) => unknown
  ): void {
    element.addEventListener(type, listener as EventListenerOrEventListenerObject);
    this.disposals.push(() => {
      element.removeEventListener(type, listener as EventListenerOrEventListenerObject);
    });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  subscribe<T = any>(
    subscribable: string | KnockoutSubscribable<T>,
    callback: (event: T) => void
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

  /**
   * Helper function to link knockout observable with Vue refs. Note that it will update the Vue ref on changes to
   * the knockout observable but not the other way around.
   */
  trackObservable<T>(
    observableRef: Ref<KnockoutObservable<T | undefined | null>>,
    vueRef: Ref<T | null>
  ): void {
    const whenDef = new Promise<KnockoutObservable<T | null | undefined>>(resolve => {
      const stop = watch(
        observableRef,
        observable => {
          if (observable) {
            resolve(observable);
            stop();
          }
        },
        { immediate: true }
      );
    });
    whenDef.then(observable => {
      if (this.disposed) {
        return;
      }
      vueRef.value = valueOrNull(observable());
      this.subscribe<T | undefined | null>(observable, (newVal?: T | null) => {
        vueRef.value = valueOrNull(newVal);
      });
    });
  }

  trackTimeout(timeout: number): void {
    this.disposals.push(() => {
      window.clearTimeout(timeout);
    });
  }

  dispose(): void {
    this.disposed = true;
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
