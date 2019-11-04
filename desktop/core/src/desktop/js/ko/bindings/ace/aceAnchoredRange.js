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

// TODO: depends on Ace

const clearGutterCss = (cssClass, session, startRow, endRow) => {
  for (let row = startRow; row <= endRow; row++) {
    session.removeGutterDecoration(row, cssClass);
  }
};

const setGutterCss = (cssClass, session, startRow, endRow) => {
  for (let row = startRow; row <= endRow; row++) {
    session.addGutterDecoration(row, cssClass);
  }
};

export default class AceAnchoredRange {
  constructor(editor) {
    this.editor = editor;
    const doc = this.editor.getSession().doc;
    this.startAnchor = doc.createAnchor(0, 0);
    this.endAnchor = doc.createAnchor(0, 0);
    this.changed = false;

    this.markerCssClasses = {};
    this.gutterCssClasses = {};
    this.refreshThrottle = -1;

    this.attachChangeHandler();
  }

  attachChangeHandler() {
    const throttledRefresh = () => {
      window.clearTimeout(this.refreshThrottle);
      this.refreshThrottle = window.setTimeout(this.refresh.bind(this), 10);
    };

    this.startAnchor.on('change', throttledRefresh);
    this.endAnchor.on('change', throttledRefresh);
  }

  refresh() {
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

  move(parseLocation, leadingEmptyLineCount) {
    const lastRow = parseLocation.last_line - 1;
    const firstRow = Math.min(lastRow, parseLocation.first_line - 1 + (leadingEmptyLineCount || 0));
    const firstCol = leadingEmptyLineCount ? 0 : parseLocation.first_column;
    this.startAnchor.setPosition(firstRow, firstCol);
    this.endAnchor.setPosition(lastRow, parseLocation.last_column);
  }

  addGutterCss(cssClass) {
    const session = this.editor.getSession();
    const startRow = this.startAnchor.getPosition().row;
    const endRow = this.endAnchor.getPosition().row;
    this.gutterCssClasses[cssClass] = { start: startRow, end: endRow };
    setGutterCss(cssClass, session, startRow, endRow);
  }

  addMarkerCss(cssClass) {
    if (!this.markerCssClasses[cssClass]) {
      const AceRange = ace.require('ace/range').Range;
      const range = new AceRange(0, 0, 0, 0);
      range.start = this.startAnchor;
      range.end = this.endAnchor;
      this.markerCssClasses[cssClass] = this.editor.getSession().addMarker(range, cssClass);
    }
  }

  removeMarkerCss(cssClass) {
    if (this.markerCssClasses[cssClass]) {
      this.editor.getSession().removeMarker(this.markerCssClasses[cssClass]);
      delete this.markerCssClasses[cssClass];
    }
  }

  removeGutterCss(cssClass) {
    if (this.gutterCssClasses[cssClass]) {
      const session = this.editor.getSession();
      const rowSpan = this.gutterCssClasses[cssClass];
      delete this.gutterCssClasses[cssClass];
      clearGutterCss(cssClass, session, rowSpan.start, rowSpan.end);
    }
  }

  dispose() {
    window.clearTimeout(this.refreshThrottle);
    this.startAnchor.detach();
    this.endAnchor.detach();

    Object.keys(this.gutterCssClasses).forEach(this.removeGutterCss.bind(this));
    Object.keys(this.markerCssClasses).forEach(this.removeMarkerCss.bind(this));
  }
}
