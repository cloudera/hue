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

import { Disposable } from 'components/utils/SubscriptionTracker';
import { Ace } from 'ext/ace';
import { ParsedLocation } from 'parse/types';

const clearGutterCss = (
  cssClass: string,
  session: Ace.Session,
  startRow: number,
  endRow: number
): void => {
  for (let row = startRow; row <= endRow; row++) {
    session.removeGutterDecoration(row, cssClass);
  }
};

const setGutterCss = (
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
  startAnchor: Ace.Anchor;
  endAnchor: Ace.Anchor;

  changed = false;
  markerCssClasses: { [clazz: string]: number } = {};
  gutterCssClasses: { [clazz: string]: { start: number; end: number } } = {};
  refreshThrottle = -1;

  constructor(editor: Ace.Editor) {
    this.editor = editor;
    const doc = this.editor.getSession().doc;
    this.startAnchor = doc.createAnchor(0, 0);
    this.endAnchor = doc.createAnchor(0, 0);

    this.attachChangeHandler();
  }

  attachChangeHandler(): void {
    const throttledRefresh = () => {
      window.clearTimeout(this.refreshThrottle);
      this.refreshThrottle = window.setTimeout(this.refresh.bind(this), 10);
    };

    this.startAnchor.on('change', throttledRefresh);
    this.endAnchor.on('change', throttledRefresh);
  }

  refresh(): void {
    const session = this.editor.getSession();
    const newStart = this.startAnchor.getPosition();
    const newEnd = this.endAnchor.getPosition();

    Object.keys(this.gutterCssClasses).forEach(cssClass => {
      const rowSpan = this.gutterCssClasses[cssClass];
      clearGutterCss(cssClass, session, rowSpan.start, rowSpan.end);
      rowSpan.start = newStart.row;
      rowSpan.end = newEnd.row;
      setGutterCss(cssClass, session, rowSpan.start, rowSpan.end);
    });
  }

  move(parseLocation: ParsedLocation, leadingEmptyLineCount?: number): void {
    const lastRow = parseLocation.last_line - 1;
    const firstRow = Math.min(lastRow, parseLocation.first_line - 1 + (leadingEmptyLineCount || 0));
    const firstCol = leadingEmptyLineCount ? 0 : parseLocation.first_column;
    this.startAnchor.setPosition(firstRow, firstCol);
    this.endAnchor.setPosition(lastRow, parseLocation.last_column);
  }

  addGutterCss(cssClass: string): void {
    const session = this.editor.getSession();
    const startRow = this.startAnchor.getPosition().row;
    const endRow = this.endAnchor.getPosition().row;
    this.gutterCssClasses[cssClass] = { start: startRow, end: endRow };
    setGutterCss(cssClass, session, startRow, endRow);
  }

  addMarkerCss(cssClass: string): void {
    if (!this.markerCssClasses[cssClass]) {
      const AceRange = ace.require('ace/range').Range;
      const range = new AceRange(0, 0, 0, 0);
      range.start = this.startAnchor;
      range.end = this.endAnchor;
      this.markerCssClasses[cssClass] = this.editor.getSession().addMarker(range, cssClass);
    }
  }

  removeMarkerCss(cssClass: string): void {
    if (this.markerCssClasses[cssClass]) {
      this.editor.getSession().removeMarker(this.markerCssClasses[cssClass]);
      delete this.markerCssClasses[cssClass];
    }
  }

  removeGutterCss(cssClass: string): void {
    if (this.gutterCssClasses[cssClass]) {
      const session = this.editor.getSession();
      const rowSpan = this.gutterCssClasses[cssClass];
      delete this.gutterCssClasses[cssClass];
      clearGutterCss(cssClass, session, rowSpan.start, rowSpan.end);
    }
  }

  dispose(): void {
    window.clearTimeout(this.refreshThrottle);
    this.startAnchor.detach();
    this.endAnchor.detach();

    Object.keys(this.gutterCssClasses).forEach(this.removeGutterCss.bind(this));
    Object.keys(this.markerCssClasses).forEach(this.removeMarkerCss.bind(this));
  }
}
