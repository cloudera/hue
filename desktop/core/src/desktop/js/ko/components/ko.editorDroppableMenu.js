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
import * as ko from 'knockout';

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import sqlUtils from 'sql/sqlUtils';
import DisposableComponent from './DisposableComponent';
import { DRAGGABLE_TEXT_META_EVENT } from 'ko/bindings/ko.draggableText';
import { INSERT_AT_CURSOR_EVENT } from 'ko/bindings/ace/ko.aceEditor';
import { defer, sleep } from 'utils/hueUtils';

export const NAME = 'hue-editor-droppable-menu';

const TYPES = {
  VALUE: 'value',
  SELECT: 'select',
  INSERT: 'insert',
  UPDATE: 'update',
  DROP: 'drop'
};

// prettier-ignore
const TEMPLATE = `
  <ul class="table-drop-menu hue-context-menu">
    <!-- ko if: meta -->
    <li><a href="javascript: void(0);" data-bind="click: insertValue.bind($data, '${ TYPES.VALUE }')">"<span data-bind="text: identifier"></span>"</a></li>
    <li class="divider"></li>
    <li><a href="javascript: void(0);" data-bind="click: insertValue.bind($data, '${ TYPES.SELECT }')">SELECT FROM <span data-bind="text: identifier"></span>...</a></li>
    <!-- ko ifnot: meta().isView -->
      <li><a href="javascript: void(0);" data-bind="click: insertValue.bind($data, '${ TYPES.INSERT }')">INSERT INTO <span data-bind="text: identifier"></span>...</a></li>
      <li><a href="javascript: void(0);" data-bind="click: insertValue.bind($data, '${ TYPES.UPDATE }')">UPDATE <span data-bind="text: identifier"></span>...</a></li>
      <li><a href="javascript: void(0);" data-bind="click: insertValue.bind($data, '${ TYPES.DROP }')">DROP TABLE <span data-bind="text: identifier"></span>...</a></li>
    <!-- /ko -->
    <!-- ko if: meta().isView -->
      <li><a href="javascript: void(0);"data-bind="click: insertValue.bind($data, '${ TYPES.DROP }')">DROP VIEW <span data-bind="text: identifier"></span>...</a></li>
    <!-- /ko -->
    <!-- /ko -->
  </ul>
`;

class EditorDroppableMenu extends DisposableComponent {
  constructor(params, element) {
    super();
    this.editor = params.editor;
    const $parentDropTarget = $(params.parentDropTarget);
    const $tableDropMenu = $(element).parent().find('.table-drop-menu');

    this.meta = ko.observable();

    this.identifier = ko.observable('');

    this.meta.subscribe(async meta => {
      if (meta && meta.database && meta.table) {
        this.identifier(
          (await sqlUtils.backTickIfNeeded(meta.connector, meta.database)) +
            '.' +
            (await sqlUtils.backTickIfNeeded(meta.connector, meta.table))
        );
      } else {
        this.identifier('');
      }
    });

    super.subscribe(DRAGGABLE_TEXT_META_EVENT, this.meta);

    this.menu = ko.bindingHandlers.contextMenu.initContextMenu(
      $tableDropMenu,
      $('.content-panel'),
      async () => {
        await defer();
        $(document).on('click.' + NAME, async () => {
          if (this.menu) {
            $tableDropMenu.css('opacity', 0);
            await sleep(300);
            this.menu.hide();
          }
        });
      },
      () => {
        $(document).off('click.' + NAME);
      }
    );

    $parentDropTarget.droppable({
      accept: '.draggableText',
      drop: (e, ui) => {
        const editor = this.editor();
        const meta = this.meta();
        if (!meta || !editor) {
          return;
        }
        const position = editor.renderer.screenToTextCoordinates(e.clientX, e.clientY);
        let text = ui.helper.text();
        if (
          meta.type === 's3' ||
          meta.type === 'hdfs' ||
          meta.type === 'adls' ||
          meta.type === 'abfs'
        ) {
          text = "'" + meta.definition.path + "'";
        }
        editor.moveCursorToPosition(position);
        const before = editor.getTextBeforeCursor();
        if (meta.database && meta.table && !meta.column && /.*;|^\s*$/.test(before)) {
          this.menu.show(e);
        } else {
          if (/\S+$/.test(before) && before.charAt(before.length - 1) !== '.') {
            text = ' ' + text;
          }
          const after = editor.getTextAfterCursor();
          if (after.length > 0 && after.charAt(0) !== ' ' && text.charAt(text.length - 1) !== ' ') {
            text += ' ';
          }
          editor.session.insert(position, text);
          position.column += text.length;
          editor.clearSelection();
        }
      }
    });
  }

  insertValue(type) {
    let textToInsert = '';
    let cursorEndAdjust = 0;
    switch (type) {
      case TYPES.UPDATE:
        textToInsert = 'UPDATE ' + this.identifier() + '\nSET ';
        cursorEndAdjust = -1;
        break;
      case TYPES.DROP:
        textToInsert =
          (this.meta().isView ? 'DROP VIEW ' : 'DROP TABLE ') + this.identifier() + ';';
        cursorEndAdjust = -2;
        break;
      case TYPES.INSERT:
        textToInsert = 'INSERT INTO ' + this.identifier() + '\nVALUES ();';
        cursorEndAdjust = -3;
        break;
      case TYPES.SELECT:
        textToInsert = 'SELECT *\nFROM ' + this.identifier() + '\nLIMIT 100\n;';
        cursorEndAdjust = -2;
        break;
      default:
        textToInsert = this.identifier();
        break;
    }

    huePubSub.publish(INSERT_AT_CURSOR_EVENT, {
      text: textToInsert,
      targetEditor: this.editor(),
      cursorEndAdjust: cursorEndAdjust
    });

    this.menu.hide();
  }
}

componentUtils.registerComponent(
  NAME,
  {
    createViewModel: (params, componentInfo) =>
      new EditorDroppableMenu(params, componentInfo.element)
  },
  TEMPLATE
);
