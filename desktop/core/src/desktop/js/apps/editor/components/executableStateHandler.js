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

import * as ko from 'knockout';
import { RESULT_UPDATED_EVENT } from 'apps/editor/execution/executionResult';
import huePubSub from 'utils/huePubSub';

export const trackResult = (activeExecutable, onChange) => {
  if (!activeExecutable) {
    return { dispose: () => {} };
  }

  const disposals = [];

  let executable = ko.unwrap(activeExecutable);

  if (ko.isObservable(activeExecutable)) {
    const koSub = activeExecutable.subscribe(newExecutable => {
      executable = newExecutable;
      onChange(executable.result);
    });
    disposals.push(() => {
      koSub.dispose();
    });
  } else if (!executable) {
    return { dispose: () => {} };
  }

  const updateSub = huePubSub.subscribe(RESULT_UPDATED_EVENT, executionResult => {
    if (executionResult === executable.result) {
      onChange(executionResult);
    }
  });
  disposals.push(() => {
    updateSub.remove();
  });

  return {
    dispose: () => {
      while (disposals.length) {
        disposals.pop()();
      }
    }
  };
};

export const attachTracker = (activeExecutable, id, target, trackedObservables) => {
  const disposals = [];
  if (!activeExecutable) {
    return { dispose: () => {} };
  }

  let ignoreObservableChange = false;

  const updateFromState = state => {
    ignoreObservableChange = true;
    Object.keys(state).forEach(key => target[key](state[key]));
    ignoreObservableChange = false;
  };

  updateFromState(trackedObservables);

  const sub = activeExecutable.subscribe(executable => {
    const state = Object.assign({}, trackedObservables, executable.observerState[id]);
    updateFromState(state);
  });

  disposals.push(() => {
    sub.dispose();
  });

  Object.keys(trackedObservables).forEach(observableAttr => {
    const sub = target[observableAttr].subscribe(val => {
      if (ignoreObservableChange || !activeExecutable()) {
        return;
      }
      if (!activeExecutable().observerState[id]) {
        activeExecutable().observerState[id] = {};
      }
      activeExecutable().observerState[id][observableAttr] = val;
    });
    disposals.push(() => {
      sub.dispose();
    });
  });

  return {
    dispose: () => {
      while (disposals.length) {
        disposals.pop()();
      }
    }
  };
};
