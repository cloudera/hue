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

import { Ace } from 'ext/ace';
import { Disposable } from 'components/utils/SubscriptionTracker';
import { Connector } from 'types/config';
import { getOptimizer, PredictResponse } from 'catalog/optimizer/optimizer';
import { CancellablePromise } from 'api/cancellablePromise';
import { defer } from 'utils/hueUtils';

type ActivePredict = { text: string; element: HTMLElement };

export const attachPredictTypeahead = (editor: Ace.Editor, connector: Connector): Disposable => {
  let activePredict: { text: string; element: HTMLElement } | undefined;

  const optimizer = getOptimizer(connector);

  const addPredictElement = (text: string): ActivePredict => {
    const element = document.createElement('div');
    element.innerText = text;
    element.style.marginLeft = '4px';
    element.classList.add('ace_invisible');
    element.classList.add('ace_emptyMessage');
    editor.renderer.scroller.append(element);
    return { text, element };
  };

  const removeActivePredict = (): void => {
    if (activePredict) {
      activePredict.element.remove();
      activePredict = undefined;
    }
  };

  const setActivePredict = (text: string): void => {
    removeActivePredict();
    activePredict = addPredictElement(text);
  };

  let activePredictPromise: CancellablePromise<PredictResponse> | undefined;
  let lastPrediction: string | undefined;

  const updatePredictTypeahead = () => {
    if (activePredictPromise) {
      activePredictPromise.cancel();
    }
    defer(() => {
      const editorText = editor.getValue();
      if (
        activePredict &&
        (!editorText.length ||
          activePredict.text === editorText ||
          activePredict.text.indexOf(editorText) !== 0)
      ) {
        removeActivePredict();
      }
      if (editorText.length && !activePredict) {
        optimizer
          .predict({
            beforeCursor: editor.getTextBeforeCursor(),
            afterCursor: editor.getTextAfterCursor()
          })
          .then(({ prediction }) => {
            if (prediction !== lastPrediction) {
              const beforeCursor = editor.getTextBeforeCursor();
              if (prediction && prediction.toLowerCase().startsWith(beforeCursor.toLowerCase())) {
                setActivePredict(beforeCursor + prediction.slice(beforeCursor.length));
              } else {
                removeActivePredict();
              }
            }
            lastPrediction = prediction;
          })
          .catch(() => {
            removeActivePredict();
          });
      }
    });
  };

  editor.commands.addCommand({
    name: 'applyPredict',
    bindKey: { win: 'Tab', mac: 'Tab' },
    exec: () => {
      if (activePredict) {
        editor.setValue(activePredict.text, 1);
        editor.clearSelection();
      } else {
        editor.indent();
      }
    },
    multiSelectAction: 'forEach',
    scrollIntoView: 'selectionPart'
  });

  editor.commands.addCommand({
    name: 'forceIndent',
    bindKey: { win: 'Shift-Tab', mac: 'Shift-Tab' },
    exec: () => {
      removeActivePredict();
      editor.indent();
    },
    multiSelectAction: 'forEach',
    scrollIntoView: 'selectionPart'
  });

  editor.commands.addCommand({
    name: 'cancelPredict',
    bindKey: { win: 'Escape', mac: 'Escape' },
    exec: () => {
      removeActivePredict();
    }
  });

  const predictOnInput = () => {
    updatePredictTypeahead();
  };

  editor.on('input', predictOnInput);

  return {
    dispose: () => {
      editor.off('input', predictOnInput);
    }
  };
};
