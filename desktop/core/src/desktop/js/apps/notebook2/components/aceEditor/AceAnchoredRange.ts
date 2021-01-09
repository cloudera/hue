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

import ace from 'ext/aceHelper';
import { Ace } from 'ext/ace';

import { Disposable } from 'components/utils/SubscriptionTracker';
import { ParsedLocation } from 'parse/types';

const removeGutterDecoration = (
  cssClass: string,
  session: Ace.Session,
  startRow: number,
  endRow: number
): void => {
  for (let row = startRow; row <= endRow; row++) {
    session.removeGutterDecoration(row, cssClass);
  }
};

const addGutterDecoration = (
  cssClass: string,
  session: Ace.Session,
  startRow: number,
  endRow: number
): void => {
  for (let row = startRow; row <= endRow; row++) {
    session.addGutterDecoration(row, cssClass);
  }
};

export default class AceAnchoredRange implements Disposable {
  editor: Ace.Editor;
  gutterStart: Ace.Anchor;
  gutterEnd: Ace.Anchor;
  rowStart: Ace.Anchor;
  rowEnd: Ace.Anchor;

  changed = false;
  rowMarkerSpec?: { cssClass: string; rowOffset: number; marker: number };
  gutterSpec?: { cssClass: string; span: { start: number; end: number } };
  refreshThrottle = -1;

  constructor(editor: Ace.Editor) {
    this.editor = editor;
    const doc = this.editor.getSession().doc;
    this.gutterStart = doc.createAnchor(0, 0);
    this.gutterEnd = doc.createAnchor(0, 0);
    this.rowStart = doc.createAnchor(0, 0);
    this.rowEnd = doc.createAnchor(0, 0);

    this.attachChangeHandler();
  }

  attachChangeHandler(): void {
    const throttledRefresh = () => {
      window.clearTimeout(this.refreshThrottle);
      this.refreshThrottle = window.setTimeout(this.refresh.bind(this), 10);
    };

    this.gutterStart.on('change', throttledRefresh);
    this.gutterEnd.on('change', throttledRefresh);
    this.rowStart.on('change', throttledRefresh);
    this.rowEnd.on('change', throttledRefresh);
  }

  refresh(): void {
    const session = this.editor.getSession();
    const newStart = this.gutterStart.getPosition();
    const newEnd = this.gutterEnd.getPosition();
    if (this.gutterSpec) {
      const rowSpan = this.gutterSpec.span;
      removeGutterDecoration(this.gutterSpec.cssClass, session, rowSpan.start, rowSpan.end);
      rowSpan.start = newStart.row;
      rowSpan.end = newEnd.row;
      addGutterDecoration(this.gutterSpec.cssClass, session, rowSpan.start, rowSpan.end);
    }
    if (this.rowMarkerSpec) {
      const offset = this.rowMarkerSpec.rowOffset;
      const cssClass = this.rowMarkerSpec.cssClass;
      this.removeMarkerRowCss();
      this.setMarkerRowCss(cssClass, offset);
    }
  }

  move(parseLocation: ParsedLocation, leadingEmptyLineCount?: number): void {
    const lastRow = parseLocation.last_line - 1;
    const firstRow = Math.min(lastRow, parseLocation.first_line - 1 + (leadingEmptyLineCount || 0));
    const firstCol = leadingEmptyLineCount ? 0 : parseLocation.first_column;
    this.gutterStart.setPosition(firstRow, firstCol);
    this.gutterEnd.setPosition(lastRow, parseLocation.last_column);
    if (this.rowMarkerSpec) {
      this.refreshRowAnchors(this.rowMarkerSpec.rowOffset);
    }
  }

  setGutterCss(cssClass: string): void {
    if (this.gutterSpec) {
      this.removeGutterCss();
    }
    const session = this.editor.getSession();
    const startRow = this.gutterStart.getPosition().row;
    const endRow = this.gutterEnd.getPosition().row;
    this.gutterSpec = { cssClass, span: { start: startRow, end: endRow } };
    addGutterDecoration(cssClass, session, startRow, endRow);
  }

  refreshRowAnchors(rowOffset: number): void {
    const markerRow = this.gutterStart.row + rowOffset;
    this.rowStart.setPosition(markerRow, 0);
    this.rowEnd.setPosition(markerRow, this.editor.getSession().getLine(markerRow).length);
  }

  setMarkerRowCss(cssClass: string, rowOffset: number): void {
    if (this.rowMarkerSpec) {
      this.removeMarkerRowCss();
    }
    this.refreshRowAnchors(rowOffset);
    const AceRange = ace.require('ace/range').Range;
    const range: Ace.Range = new AceRange(0, 0, 0, 0);
    range.start = this.rowStart;
    range.end = this.rowEnd;
    const marker = this.editor.getSession().addMarker(range, cssClass);
    this.rowMarkerSpec = { cssClass, rowOffset, marker };
    this.rowMarkerSpec.marker = marker;
  }

  removeMarkerRowCss(): void {
    if (this.rowMarkerSpec) {
      this.editor.getSession().removeMarker(this.rowMarkerSpec.marker);
      this.rowMarkerSpec = undefined;
    }
  }

  removeGutterCss(): void {
    if (this.gutterSpec) {
      const session = this.editor.getSession();
      const rowSpan = this.gutterSpec.span;
      removeGutterDecoration(this.gutterSpec.cssClass, session, rowSpan.start, rowSpan.end);
      this.gutterSpec = undefined;
    }
  }

  dispose(): void {
    window.clearTimeout(this.refreshThrottle);
    this.gutterStart.detach();
    this.gutterEnd.detach();
    this.rowStart.detach();
    this.rowEnd.detach();

    this.removeGutterCss();
    this.removeMarkerRowCss();
  }
}
