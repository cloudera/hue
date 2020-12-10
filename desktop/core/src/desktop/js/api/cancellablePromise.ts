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

export interface Cancellable {
  cancel(): void;
}

export class CancellablePromise<T> extends Promise<T> implements Cancellable {
  private readonly onCancel?: () => void;
  private readonly rejectHandler?: (reason?: unknown) => void;
  private cancelPrevented?: boolean;
  cancelled?: boolean;

  constructor(
    handlers: (
      resolve: (value?: T | PromiseLike<T>) => void,
      reject: (reason?: unknown) => void,
      onCancel: (cancelHandler: () => void) => void
    ) => void
  ) {
    let onCancel: undefined | (() => void) = undefined;
    let rejectHandler: undefined | ((reason?: unknown) => void) = undefined;
    super((resolve, reject) => {
      rejectHandler = reject;
      return handlers(resolve, reject, (cancelHandler: () => void) => (onCancel = cancelHandler));
    });
    this.rejectHandler = rejectHandler;
    this.onCancel = onCancel;
  }

  async cancel(): Promise<void> {
    if (!this.cancelPrevented) {
      const testSymbol = Symbol();
      const firstToFinish = await Promise.race([this, Promise.resolve(testSymbol)]);
      if (firstToFinish === testSymbol) {
        if (this.onCancel) {
          this.onCancel();
        }
        if (this.rejectHandler) {
          this.rejectHandler();
        }
        this.cancelled = true;
      }
    }
  }

  preventCancel(): void {
    this.cancelPrevented = true;
  }

  static reject<T = unknown>(reason?: unknown): CancellablePromise<T> {
    return new CancellablePromise<T>((resolve, reject) => {
      reject(reason);
    });
  }

  static resolve<T = unknown>(value?: T | PromiseLike<T>): CancellablePromise<T> {
    return new CancellablePromise<T>(resolve => {
      resolve(value);
    });
  }
}
