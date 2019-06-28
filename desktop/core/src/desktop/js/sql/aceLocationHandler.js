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

import AssistStorageEntry from 'ko/components/assist/assistStorageEntry';
import dataCatalog from 'catalog/dataCatalog';
import hueDebug from 'utils/hueDebug';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import SqlParseSupport from 'parse/sqlParseSupport';
import sqlStatementsParser from 'parse/sqlStatementsParser';
import sqlUtils from 'sql/sqlUtils';

// TODO: depends on Ace, sqlStatementsParser

const STATEMENT_COUNT_AROUND_ACTIVE = 10;

const VERIFY_LIMIT = 50;
const VERIFY_DELAY = 50;

class AceLocationHandler {
  constructor(options) {
    const self = this;
    self.editor = options.editor;
    self.editorId = options.editorId;
    self.snippet = options.snippet;
    self.expandStar =
      (options.i18n && options.i18n.expandStar) || 'Right-click to expand with columns';
    self.contextTooltip =
      (options.i18n && options.i18n.contextTooltip) || 'Right-click for details';

    self.sqlSyntaxWorkerSub = null;
    self.disposeFunctions = [];
    self.databaseIndex = {};

    self.attachStatementLocator();
    self.attachSqlWorker();
    self.attachGutterHandler();
    self.attachMouseListeners();

    self.verifyThrottle = -1;

    const updateDatabaseIndex = function(databaseList) {
      self.databaseIndex = {};
      databaseList.forEach(database => {
        self.databaseIndex[database.toLowerCase()] = true;
      });
    };

    const databaseSub = self.snippet.availableDatabases.subscribe(updateDatabaseIndex);

    self.disposeFunctions.push(() => {
      databaseSub.dispose();
    });

    updateDatabaseIndex(self.snippet.availableDatabases());
  }

  attachMouseListeners() {
    const self = this;

    const Tooltip = ace.require('ace/tooltip').Tooltip;
    const AceRange = ace.require('ace/range').Range;

    const contextTooltip = new Tooltip(self.editor.container);
    let tooltipTimeout = -1;
    let disableTooltip = false;
    let lastHoveredToken = null;
    const activeMarkers = [];
    let keepLastMarker = false;

    const hideContextTooltip = function() {
      clearTimeout(tooltipTimeout);
      contextTooltip.hide();
    };

    const clearActiveMarkers = function() {
      hideContextTooltip();
      while (activeMarkers.length > keepLastMarker ? 1 : 0) {
        self.editor.session.removeMarker(activeMarkers.shift());
      }
    };

    const markLocation = function(parseLocation) {
      let range;
      if (parseLocation.type === 'function') {
        // Todo: Figure out why functions need an extra char at the end
        range = new AceRange(
          parseLocation.location.first_line - 1,
          parseLocation.location.first_column - 1,
          parseLocation.location.last_line - 1,
          parseLocation.location.last_column
        );
      } else {
        range = new AceRange(
          parseLocation.location.first_line - 1,
          parseLocation.location.first_column - 1,
          parseLocation.location.last_line - 1,
          parseLocation.location.last_column - 1
        );
      }
      activeMarkers.push(self.editor.session.addMarker(range, 'hue-ace-location'));
      return range;
    };

    const popoverShownSub = huePubSub.subscribe('context.popover.shown', () => {
      hideContextTooltip();
      keepLastMarker = true;
      disableTooltip = true;
    });

    self.disposeFunctions.push(() => {
      popoverShownSub.remove();
    });

    const popoverHiddenSub = huePubSub.subscribe('context.popover.hidden', () => {
      disableTooltip = false;
      clearActiveMarkers();
      keepLastMarker = false;
    });

    self.disposeFunctions.push(() => {
      popoverHiddenSub.remove();
    });

    const mousemoveListener = self.editor.on('mousemove', e => {
      clearTimeout(tooltipTimeout);
      const selectionRange = self.editor.selection.getRange();
      if (selectionRange.isEmpty()) {
        const pointerPosition = self.editor.renderer.screenToTextCoordinates(
          e.clientX + 5,
          e.clientY
        );
        const endTestPosition = self.editor.renderer.screenToTextCoordinates(
          e.clientX + 15,
          e.clientY
        );
        if (endTestPosition.column !== pointerPosition.column) {
          const token = self.editor.session.getTokenAt(pointerPosition.row, pointerPosition.column);
          if (
            token !== null &&
            !token.notFound &&
            token.parseLocation &&
            !disableTooltip &&
            token.parseLocation.type !== 'alias'
          ) {
            tooltipTimeout = window.setTimeout(() => {
              if (token.parseLocation) {
                const endCoordinates = self.editor.renderer.textToScreenCoordinates(
                  pointerPosition.row,
                  token.start
                );

                let tooltipText =
                  token.parseLocation.type === 'asterisk' ? self.expandStar : self.contextTooltip;
                let colType;
                if (token.parseLocation.type === 'column') {
                  const tableChain = token.parseLocation.identifierChain.concat();
                  const lastIdentifier = tableChain.pop();
                  if (tableChain.length > 0 && lastIdentifier && lastIdentifier.name) {
                    const colName = lastIdentifier.name.toLowerCase();
                    // Note, as cachedOnly is set to true it will call the successCallback right away (or not at all)
                    dataCatalog
                      .getEntry({
                        sourceType: self.snippet.type(),
                        namespace: self.snippet.namespace(),
                        compute: self.snippet.compute(),
                        temporaryOnly: self.snippet.autocompleteSettings.temporaryOnly,
                        path: $.map(tableChain, identifier => {
                          return identifier.name;
                        })
                      })
                      .done(entry => {
                        entry
                          .getSourceMeta({ cachedOnly: true, silenceErrors: true })
                          .done(sourceMeta => {
                            if (sourceMeta && sourceMeta.extended_columns) {
                              sourceMeta.extended_columns.every(col => {
                                if (col.name.toLowerCase() === colName) {
                                  colType = col.type.match(/^[^<]*/g)[0];
                                  return false;
                                }
                                return true;
                              });
                            }
                          });
                      });
                  }
                }
                if (token.parseLocation.identifierChain) {
                  let sqlIdentifier = $.map(token.parseLocation.identifierChain, identifier => {
                    return identifier.name;
                  }).join('.');
                  if (colType) {
                    sqlIdentifier += ' (' + colType + ')';
                  }
                  tooltipText = sqlIdentifier + ' - ' + tooltipText;
                } else if (token.parseLocation.function) {
                  tooltipText = token.parseLocation.function + ' - ' + tooltipText;
                }
                contextTooltip.show(
                  tooltipText,
                  endCoordinates.pageX,
                  endCoordinates.pageY + self.editor.renderer.lineHeight + 3
                );
              }
            }, 500);
          } else if (token !== null && token.notFound) {
            tooltipTimeout = window.setTimeout(() => {
              // TODO: i18n
              if (token.notFound && token.syntaxError) {
                let tooltipText;
                if (token.syntaxError.expected.length > 0) {
                  tooltipText =
                    I18n('Did you mean') + ' "' + token.syntaxError.expected[0].text + '"?';
                } else {
                  tooltipText =
                    I18n('Could not find') +
                    ' "' +
                    (token.qualifiedIdentifier || token.value) +
                    '"';
                }
                const endCoordinates = self.editor.renderer.textToScreenCoordinates(
                  pointerPosition.row,
                  token.start
                );
                contextTooltip.show(
                  tooltipText,
                  endCoordinates.pageX,
                  endCoordinates.pageY + self.editor.renderer.lineHeight + 3
                );
              }
            }, 500);
          } else if (token !== null && token.syntaxError) {
            tooltipTimeout = window.setTimeout(() => {
              if (token.syntaxError) {
                let tooltipText;
                if (token.syntaxError.expected.length > 0) {
                  tooltipText =
                    I18n('Did you mean') + ' "' + token.syntaxError.expected[0].text + '"?';
                } else if (token.syntaxError.expectedStatementEnd) {
                  tooltipText = I18n('Expected end of statement');
                }
                if (tooltipText) {
                  const endCoordinates = self.editor.renderer.textToScreenCoordinates(
                    pointerPosition.row,
                    token.start
                  );
                  contextTooltip.show(
                    tooltipText,
                    endCoordinates.pageX,
                    endCoordinates.pageY + self.editor.renderer.lineHeight + 3
                  );
                }
              }
            }, 500);
          } else {
            hideContextTooltip();
          }
          if (lastHoveredToken !== token) {
            clearActiveMarkers();
            if (
              token !== null &&
              !token.notFound &&
              token.parseLocation &&
              ['alias', 'whereClause', 'limitClause', 'selectList'].indexOf(
                token.parseLocation.type
              ) === -1
            ) {
              markLocation(token.parseLocation);
            }
            lastHoveredToken = token;
          }
        } else {
          clearActiveMarkers();
          lastHoveredToken = null;
        }
      }
    });

    self.disposeFunctions.push(() => {
      self.editor.off('mousemove', mousemoveListener);
    });

    const inputListener = self.editor.on('input', () => {
      clearActiveMarkers();
      lastHoveredToken = null;
    });

    self.disposeFunctions.push(() => {
      self.editor.off('input', inputListener);
    });

    const mouseoutListener = function() {
      clearActiveMarkers();
      clearTimeout(tooltipTimeout);
      contextTooltip.hide();
      lastHoveredToken = null;
    };

    self.editor.container.addEventListener('mouseout', mouseoutListener);

    self.disposeFunctions.push(() => {
      self.editor.container.removeEventListener('mouseout', mouseoutListener);
    });

    const onContextMenu = function(e) {
      const selectionRange = self.editor.selection.getRange();
      huePubSub.publish('context.popover.hide');
      huePubSub.publish('sql.syntax.dropdown.hide');
      if (selectionRange.isEmpty()) {
        const pointerPosition = self.editor.renderer.screenToTextCoordinates(
          e.clientX + 5,
          e.clientY
        );
        const token = self.editor.session.getTokenAt(pointerPosition.row, pointerPosition.column);
        if (
          token &&
          ((token.parseLocation &&
            ['alias', 'whereClause', 'limitClause', 'selectList'].indexOf(
              token.parseLocation.type
            ) === -1) ||
            token.syntaxError)
        ) {
          const range = token.parseLocation
            ? markLocation(token.parseLocation)
            : new AceRange(
                token.syntaxError.loc.first_line - 1,
                token.syntaxError.loc.first_column,
                token.syntaxError.loc.last_line - 1,
                token.syntaxError.loc.first_column + token.syntaxError.text.length
              );
          const startCoordinates = self.editor.renderer.textToScreenCoordinates(
            range.start.row,
            range.start.column
          );
          const endCoordinates = self.editor.renderer.textToScreenCoordinates(
            range.end.row,
            range.end.column
          );
          const source = {
            // TODO: add element likely in the event
            left: startCoordinates.pageX - 3,
            top: startCoordinates.pageY,
            right: endCoordinates.pageX - 3,
            bottom: endCoordinates.pageY + self.editor.renderer.lineHeight
          };

          if (token.parseLocation && token.parseLocation.identifierChain && !token.notFound) {
            token.parseLocation
              .resolveCatalogEntry({
                temporaryOnly: self.snippet.autocompleteSettings.temporaryOnly
              })
              .done(entry => {
                huePubSub.publish('context.popover.show', {
                  data: {
                    type: 'catalogEntry',
                    catalogEntry: entry
                  },
                  pinEnabled: true,
                  source: source
                });
              })
              .fail(() => {
                token.notFound = true;
              });
          } else if (token.parseLocation && !token.notFound) {
            // Asterisk, function etc.
            if (token.parseLocation.type === 'file') {
              AssistStorageEntry.getEntry(token.parseLocation.path).done(entry => {
                entry.open(true);
                huePubSub.publish('context.popover.show', {
                  data: {
                    type: 'storageEntry',
                    storageEntry: entry,
                    editorLocation: token.parseLocation.location
                  },
                  pinEnabled: true,
                  source: source
                });
              });
            } else {
              huePubSub.publish('context.popover.show', {
                data: token.parseLocation,
                sourceType: self.snippet.type(),
                namespace: self.snippet.namespace(),
                compute: self.snippet.compute(),
                defaultDatabase: self.snippet.database(),
                pinEnabled: true,
                source: source
              });
            }
          } else if (token.syntaxError) {
            huePubSub.publish('sql.syntax.dropdown.show', {
              snippet: self.snippet,
              data: token.syntaxError,
              editor: self.editor,
              range: range,
              sourceType: self.snippet.type(),
              defaultDatabase: self.snippet.database(),
              source: source
            });
          }
          e.preventDefault();
          return false;
        }
      }
    };

    const contextmenuListener = self.editor.container.addEventListener(
      'contextmenu',
      onContextMenu
    );

    self.disposeFunctions.push(() => {
      self.editor.container.removeEventListener('contextmenu', contextmenuListener);
    });
  }

  attachGutterHandler() {
    const self = this;
    const lastMarkedGutterLines = [];

    const changedSubscription = huePubSub.subscribe(
      'editor.active.statement.changed',
      statementDetails => {
        if (statementDetails.id !== self.editorId || !statementDetails.activeStatement) {
          return;
        }
        let leadingEmptyLineCount = 0;
        const leadingWhiteSpace = statementDetails.activeStatement.statement.match(/^\s+/);
        if (leadingWhiteSpace) {
          const lineBreakMatch = leadingWhiteSpace[0].match(/(\r\n)|(\n)|(\r)/g);
          if (lineBreakMatch) {
            leadingEmptyLineCount = lineBreakMatch.length;
          }
        }

        while (lastMarkedGutterLines.length) {
          self.editor
            .getSession()
            .removeGutterDecoration(lastMarkedGutterLines.shift(), 'ace-active-gutter-decoration');
        }
        for (
          let line =
            statementDetails.activeStatement.location.first_line - 1 + leadingEmptyLineCount;
          line < statementDetails.activeStatement.location.last_line;
          line++
        ) {
          lastMarkedGutterLines.push(line);
          self.editor.getSession().addGutterDecoration(line, 'ace-active-gutter-decoration');
        }
      }
    );

    self.disposeFunctions.push(() => {
      changedSubscription.remove();
    });
  }

  attachStatementLocator() {
    const self = this;
    let lastKnownStatements = [];
    let activeStatement;

    const isPointInside = function(parseLocation, editorPosition) {
      const row = editorPosition.row + 1; // ace positioning has 0 based rows while the parser has 1
      const column = editorPosition.column;
      return (
        (parseLocation.first_line < row && row < parseLocation.last_line) ||
        (parseLocation.first_line === row &&
          row === parseLocation.last_line &&
          parseLocation.first_column <= column &&
          column < parseLocation.last_column) ||
        (parseLocation.first_line === row &&
          row < parseLocation.last_line &&
          column >= parseLocation.first_column) ||
        (parseLocation.first_line < row &&
          row === parseLocation.last_line &&
          column < parseLocation.last_column)
      );
    };

    let lastExecutingStatement = null;
    const updateActiveStatement = function(cursorChange) {
      if (!self.snippet.isSqlDialect()) {
        return;
      }
      const selectionRange = self.editor.getSelectionRange();
      const editorLocation = selectionRange.start;
      if (
        selectionRange.start.row !== selectionRange.end.row ||
        selectionRange.start.column !== selectionRange.end.column
      ) {
        if (!cursorChange && self.snippet.result && self.snippet.result.statement_range()) {
          let executingStatement = self.snippet.result.statement_range();
          // Row and col are 0 for both start and end on execute, so if the selection hasn't changed we'll use last known executed statement
          if (
            executingStatement.start.row === 0 &&
            executingStatement.start.column === 0 &&
            executingStatement.end.row === 0 &&
            executingStatement.end.column === 0 &&
            lastExecutingStatement
          ) {
            executingStatement = lastExecutingStatement;
          }
          if (executingStatement.start.row === 0) {
            editorLocation.column += executingStatement.start.column;
          } else if (executingStatement.start.row !== 0 || executingStatement.start.column !== 0) {
            editorLocation.row += executingStatement.start.row;
            editorLocation.column = executingStatement.start.column;
          }
          lastExecutingStatement = executingStatement;
        } else {
          lastExecutingStatement = null;
        }
      }

      if (cursorChange && activeStatement) {
        // Don't update when cursor stays in the same statement
        if (isPointInside(activeStatement.location, editorLocation)) {
          return;
        }
      }
      const precedingStatements = [];
      const followingStatements = [];
      activeStatement = null;

      let found = false;
      let statementIndex = 0;
      if (lastKnownStatements.length === 1) {
        activeStatement = lastKnownStatements[0];
      } else {
        lastKnownStatements.forEach(statement => {
          if (isPointInside(statement.location, editorLocation)) {
            statementIndex++;
            found = true;
            activeStatement = statement;
          } else if (!found) {
            statementIndex++;
            if (precedingStatements.length === STATEMENT_COUNT_AROUND_ACTIVE) {
              precedingStatements.shift();
            }
            precedingStatements.push(statement);
          } else if (found && followingStatements.length < STATEMENT_COUNT_AROUND_ACTIVE) {
            followingStatements.push(statement);
          }
        });

        // Can happen if multiple statements and the cursor is after the last one
        if (!found) {
          precedingStatements.pop();
          activeStatement = lastKnownStatements[lastKnownStatements.length - 1];
        }
      }

      huePubSub.publish('editor.active.statement.changed', {
        id: self.editorId,
        editorChangeTime: lastKnownStatements.editorChangeTime,
        activeStatementIndex: statementIndex,
        totalStatementCount: lastKnownStatements.length,
        precedingStatements: precedingStatements,
        activeStatement: activeStatement,
        followingStatements: followingStatements
      });

      if (activeStatement) {
        self.checkForSyntaxErrors(activeStatement.location, editorLocation);
      }
    };

    const parseForStatements = function() {
      if (self.snippet.isSqlDialect()) {
        try {
          const lastChangeTime = self.editor.lastChangeTime;
          lastKnownStatements = sqlStatementsParser.parse(self.editor.getValue());
          lastKnownStatements.editorChangeTime = lastChangeTime;

          if (typeof hueDebug !== 'undefined' && hueDebug.logStatementLocations) {
            console.log(lastKnownStatements);
          }
        } catch (error) {
          console.warn('Could not parse statements!');
          console.warn(error);
        }
      }
    };

    let changeThrottle = window.setTimeout(parseForStatements, 0);
    const updateThrottle = window.setTimeout(updateActiveStatement, 0);
    let cursorChangePaused = false; // On change the cursor is also moved, this limits the calls while typing

    let lastStart;
    let lastCursorPosition;
    const changeSelectionListener = self.editor.on('changeSelection', () => {
      if (cursorChangePaused) {
        return;
      }
      window.clearTimeout(changeThrottle);
      changeThrottle = window.setTimeout(() => {
        const newCursorPosition = self.editor.getCursorPosition();
        if (
          !lastCursorPosition ||
          lastCursorPosition.row !== newCursorPosition.row ||
          lastCursorPosition.column !== newCursorPosition.column
        ) {
          self.snippet.aceCursorPosition(newCursorPosition);
          lastCursorPosition = newCursorPosition;
        }

        // The active statement is initially the top one in the selection, batch execution updates this.
        const newStart = self.editor.getSelectionRange().start;
        if (
          self.snippet.isSqlDialect() &&
          (!lastStart || lastStart.row !== newStart.row || lastStart.column !== newStart.column)
        ) {
          window.clearTimeout(updateThrottle);
          updateActiveStatement(true);
          lastStart = newStart;
        }
      }, 100);
    });

    const changeListener = self.editor.on('change', () => {
      if (self.snippet.isSqlDialect()) {
        window.clearTimeout(changeThrottle);
        cursorChangePaused = true;
        changeThrottle = window.setTimeout(() => {
          window.clearTimeout(updateThrottle);
          parseForStatements();
          updateActiveStatement();
          cursorChangePaused = false;
        }, 500);
        self.editor.lastChangeTime = Date.now();
      }
    });

    const locateSubscription = huePubSub.subscribe(
      'editor.refresh.statement.locations',
      snippet => {
        if (snippet === self.snippet) {
          cursorChangePaused = true;
          window.clearTimeout(changeThrottle);
          window.clearTimeout(updateThrottle);
          parseForStatements();
          updateActiveStatement();
          cursorChangePaused = false;
        }
      }
    );

    self.disposeFunctions.push(() => {
      window.clearTimeout(changeThrottle);
      window.clearTimeout(updateThrottle);
      self.editor.off('changeSelection', changeSelectionListener);
      self.editor.off('change', changeListener);
      locateSubscription.remove();
    });
  }

  clearMarkedErrors(type) {
    const self = this;
    for (const marker in self.editor.getSession().$backMarkers) {
      if (
        self.editor
          .getSession()
          .$backMarkers[marker].clazz.indexOf('hue-ace-syntax-' + (type || '')) === 0
      ) {
        self.editor.getSession().$backMarkers[marker].dispose();
      }
    }
  }

  checkForSyntaxErrors(statementLocation, cursorPosition) {
    const self = this;
    if (
      self.sqlSyntaxWorkerSub !== null &&
      (self.snippet.type() === 'impala' || self.snippet.type() === 'hive')
    ) {
      const AceRange = ace.require('ace/range').Range;
      const editorChangeTime = self.editor.lastChangeTime;
      const beforeCursor = self.editor
        .getSession()
        .getTextRange(
          new AceRange(
            statementLocation.first_line - 1,
            statementLocation.first_column,
            cursorPosition.row,
            cursorPosition.column
          )
        );
      const afterCursor = self.editor
        .getSession()
        .getTextRange(
          new AceRange(
            cursorPosition.row,
            cursorPosition.column,
            statementLocation.last_line - 1,
            statementLocation.last_column
          )
        );
      huePubSub.publish('ace.sql.syntax.worker.post', {
        id: self.snippet.id(),
        editorChangeTime: editorChangeTime,
        beforeCursor: beforeCursor,
        afterCursor: afterCursor,
        statementLocation: statementLocation,
        type: self.snippet.type()
      });
    }
  }

  addAnchoredMarker(range, token, clazz) {
    const self = this;
    range.start = self.editor.getSession().doc.createAnchor(range.start);
    range.end = self.editor.getSession().doc.createAnchor(range.end);
    const markerId = self.editor.getSession().addMarker(range, clazz);
    const marker = self.editor.getSession().$backMarkers[markerId];
    marker.token = token;
    marker.dispose = function() {
      range.start.detach();
      range.end.detach();
      delete marker.token.syntaxError;
      delete marker.token.notFound;
      self.editor.getSession().removeMarker(markerId);
    };
  }

  attachSqlSyntaxWorker() {
    const self = this;

    if (self.sqlSyntaxWorkerSub !== null) {
      return;
    }

    self.sqlSyntaxWorkerSub = huePubSub.subscribe('ace.sql.syntax.worker.message', e => {
      if (
        e.data.id !== self.snippet.id() ||
        e.data.editorChangeTime !== self.editor.lastChangeTime
      ) {
        return;
      }
      self.clearMarkedErrors('error');

      if (
        !e.data.syntaxError ||
        !e.data.syntaxError.expected ||
        e.data.syntaxError.expected.length === 0
      ) {
        // Only show errors that we have suggestions for
        return;
      }

      const suppressedRules = window.apiHelper.getFromTotalStorage(
        'hue.syntax.checker',
        'suppressedRules',
        {}
      );
      if (
        e.data.syntaxError &&
        e.data.syntaxError.ruleId &&
        !suppressedRules[
          e.data.syntaxError.ruleId.toString() + e.data.syntaxError.text.toLowerCase()
        ]
      ) {
        if (
          self.snippet.positionStatement() &&
          sqlUtils.locationEquals(
            e.data.statementLocation,
            self.snippet.positionStatement().location
          )
        ) {
          self.snippet.positionStatement().syntaxError = true;
        }
        if (hueDebug && hueDebug.showSyntaxParseResult) {
          console.log(e.data.syntaxError);
        }

        const token = self.editor
          .getSession()
          .getTokenAt(
            e.data.syntaxError.loc.first_line - 1,
            e.data.syntaxError.loc.first_column + 1
          );

        // Don't mark the current edited word as an error if the cursor is at the end of the word
        // For now [a-z] is fine as we only check syntax for keywords
        if (
          /[a-z]$/i.test(self.editor.getTextBeforeCursor()) &&
          !/^[a-z]/i.test(self.editor.getTextAfterCursor())
        ) {
          const cursorPos = self.editor.getCursorPosition();
          const cursorToken = self.editor.getSession().getTokenAt(cursorPos.row, cursorPos.column);
          if (cursorToken === token) {
            return;
          }
        }

        // If no token is found it likely means that the parser response came back after the text was changed,
        // at which point it will trigger another parse so we can ignore this.
        if (token) {
          token.syntaxError = e.data.syntaxError;
          const AceRange = ace.require('ace/range').Range;
          const range = new AceRange(
            e.data.syntaxError.loc.first_line - 1,
            e.data.syntaxError.loc.first_column,
            e.data.syntaxError.loc.last_line - 1,
            e.data.syntaxError.loc.first_column + e.data.syntaxError.text.length
          );
          self.addAnchoredMarker(range, token, 'hue-ace-syntax-error');
        }
      }
    });

    huePubSub.publish('editor.refresh.statement.locations', self.snippet);
  }

  detachSqlSyntaxWorker() {
    const self = this;
    if (self.sqlSyntaxWorkerSub !== null) {
      self.sqlSyntaxWorkerSub.remove();
      self.sqlSyntaxWorkerSub = null;
    }
    self.clearMarkedErrors();
  }

  fetchChildren(identifierChain) {
    const self = this;
    const deferred = $.Deferred();
    dataCatalog
      .getChildren({
        sourceType: self.snippet.type(),
        namespace: self.snippet.namespace(),
        compute: self.snippet.compute(),
        temporaryOnly: self.snippet.autocompleteSettings.temporaryOnly,
        path: $.map(identifierChain, identifier => {
          return identifier.name;
        }),
        silenceErrors: true,
        cachedOnly: true
      })
      .done(deferred.resolve)
      .fail(() => {
        deferred.reject([]);
      });
    return deferred;
  }

  fetchPossibleValues(token) {
    const self = this;
    const promise = $.Deferred();
    if (token.parseLocation.tables && token.parseLocation.tables.length > 0) {
      const tablePromises = [];
      token.parseLocation.tables.forEach(table => {
        if (table.identifierChain) {
          tablePromises.push(self.fetchChildren(table.identifierChain));
        }
      });
      $.when
        .apply($, tablePromises)
        .done(function() {
          let joined = [];
          for (let i = 0; i < arguments.length; i++) {
            joined = joined.concat(arguments[i]);
          }
          if (token.parseLocation.type === 'column') {
            // Could be a table reference
            token.parseLocation.tables.forEach(table => {
              if (!table.alias) {
                // Aliases are added later
                joined.push(table.identifierChain[table.identifierChain.length - 1]);
              }
            });
          }
          promise.resolve(joined);
        })
        .fail(promise.reject);
    } else if (
      token.parseLocation.identifierChain &&
      token.parseLocation.identifierChain.length > 0
    ) {
      // fetch the parent
      return self.fetchChildren(
        token.parseLocation.identifierChain.slice(0, token.parseLocation.identifierChain.length - 1)
      );
    } else {
      promise.reject([]);
    }
    return promise;
  }

  verifyExists(tokens, allLocations) {
    const self = this;
    window.clearInterval(self.verifyThrottle);
    self.clearMarkedErrors('warning');

    if (self.sqlSyntaxWorkerSub === null) {
      return;
    }

    const cursorPos = self.editor.getCursorPosition();

    const tokensToVerify = tokens
      .filter(token => {
        return (
          token &&
          token.parseLocation &&
          (token.parseLocation.type === 'table' || token.parseLocation.type === 'column') &&
          (token.parseLocation.identifierChain || token.parseLocation.tables) &&
          !(
            cursorPos.row + 1 === token.parseLocation.location.last_line &&
            cursorPos.column + 1 === token.parseLocation.location.first_column + token.value.length
          )
        );
      })
      .slice(0, VERIFY_LIMIT);

    if (tokensToVerify.length === 0) {
      return;
    }

    const aliasIndex = {};
    const aliases = [];

    allLocations.forEach(location => {
      if (
        location.type === 'alias' &&
        (location.source === 'column' ||
          location.source === 'table' ||
          location.source === 'subquery' ||
          location.source === 'cte')
      ) {
        aliasIndex[location.alias.toLowerCase()] = location;
        aliases.push({ name: location.alias.toLowerCase() });
      }
    });

    const resolvePathFromTables = function(location) {
      const promise = $.Deferred();
      if (
        location.type === 'column' &&
        typeof location.tables !== 'undefined' &&
        location.identifierChain.length === 1
      ) {
        const findIdentifierChainInTable = function(tablesToGo) {
          const nextTable = tablesToGo.shift();
          if (typeof nextTable.subQuery === 'undefined') {
            dataCatalog
              .getChildren({
                sourceType: self.snippet.type(),
                namespace: self.snippet.namespace(),
                compute: self.snippet.compute(),
                temporaryOnly: self.snippet.autocompleteSettings.temporaryOnly,
                path: $.map(nextTable.identifierChain, identifier => {
                  return identifier.name;
                }),
                cachedOnly: true,
                silenceErrors: true
              })
              .done(entries => {
                const containsColumn = entries.some(entry => {
                  return sqlUtils.identifierEquals(entry.name, location.identifierChain[0].name);
                });

                if (containsColumn) {
                  location.identifierChain = nextTable.identifierChain.concat(
                    location.identifierChain
                  );
                  delete location.tables;
                  promise.resolve();
                } else if (tablesToGo.length > 0) {
                  findIdentifierChainInTable(tablesToGo);
                } else {
                  promise.resolve();
                }
              })
              .fail(promise.resolve);
          } else if (tablesToGo.length > 0) {
            findIdentifierChainInTable(tablesToGo);
          } else {
            promise.resolve();
          }
        };
        if (location.tables.length > 1) {
          findIdentifierChainInTable(location.tables.concat());
        } else if (location.tables.length === 1 && location.tables[0].identifierChain) {
          location.identifierChain = location.tables[0].identifierChain.concat(
            location.identifierChain
          );
          delete location.tables;
          promise.resolve();
        }
      } else {
        promise.resolve();
      }
      return promise;
    };

    const verify = function() {
      if (tokensToVerify.length === 0) {
        return;
      }
      const token = tokensToVerify.shift();
      const location = token.parseLocation;

      // TODO: Verify columns in subqueries, i.e. 'code' in 'select code from (select * from web_logs) wl, customers c;'
      if ((location.type === 'column' || location.type === 'complex') && location.tables) {
        const hasSubQueries = location.tables.some(table => {
          return typeof table.subQuery !== 'undefined';
        });
        if (hasSubQueries) {
          self.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
          return;
        }
      }

      resolvePathFromTables(location)
        .done(() => {
          if (location.type === 'column') {
            let possibleAlias;
            if (
              !location.tables &&
              location.identifierChain &&
              location.identifierChain.length > 1
            ) {
              possibleAlias = aliasIndex[token.parseLocation.identifierChain[0].name.toLowerCase()];
            } else if (location.tables) {
              location.tables.some(table => {
                if (
                  table.identifierChain &&
                  table.identifierChain.length === 1 &&
                  table.identifierChain[0].name
                ) {
                  possibleAlias = aliasIndex[table.identifierChain[0].name.toLowerCase()];
                  return possibleAlias;
                }
                return false;
              });
            }
            if (possibleAlias && possibleAlias.source === 'cte') {
              // We currently don't discover the columns from a CTE so we can't say if a column exists or not
              self.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
              return;
            }
          }

          self
            .fetchPossibleValues(token)
            .done(possibleValues => {
              // Tokens might change while making api calls
              if (!token.parseLocation) {
                self.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
                return;
              }

              // Append aliases unless qualified i.e.for 'b' in SELECT a.b we shouldn't suggest aliases
              if (
                (token.parseLocation.type !== 'column' && token.parseLocation.type !== 'complex') ||
                !token.parseLocation.qualified
              ) {
                possibleValues = possibleValues.concat(aliases);
              }

              const tokenValLower = token.actualValue.toLowerCase();
              const uniqueIndex = {};
              const uniqueValues = [];
              for (let i = 0; i < possibleValues.length; i++) {
                possibleValues[i].name = sqlUtils.backTickIfNeeded(
                  self.snippet.type(),
                  possibleValues[i].name
                );
                const nameLower = possibleValues[i].name.toLowerCase();
                if (
                  nameLower === tokenValLower ||
                  (tokenValLower.indexOf('`') === 0 &&
                    tokenValLower.replace(/`/g, '') === nameLower)
                ) {
                  // Break if found
                  self.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
                  return;
                }
                if (!uniqueIndex[nameLower]) {
                  uniqueValues.push(possibleValues[i]);
                  uniqueIndex[nameLower] = true;
                }
              }
              possibleValues = uniqueValues;

              const isLowerCase = tokenValLower === token.value;

              const weightedExpected = $.map(possibleValues, val => {
                return {
                  text: isLowerCase ? val.name.toLowerCase() : val.name,
                  distance: SqlParseSupport.stringDistance(token.value, val.name)
                };
              });
              weightedExpected.sort((a, b) => {
                if (a.distance === b.distance) {
                  return a.text.localeCompare(b.text);
                }
                return a.distance - b.distance;
              });
              token.syntaxError = {
                expected: weightedExpected.slice(0, 50)
              };
              token.notFound = true;

              if (token.parseLocation && token.parseLocation.type === 'table') {
                const path = $.map(token.parseLocation.identifierChain, identifier => {
                  return identifier.name;
                });
                token.qualifiedIdentifier = path.join('.');
              }

              if (token.parseLocation && weightedExpected.length > 0) {
                const AceRange = ace.require('ace/range').Range;
                const range = new AceRange(
                  token.parseLocation.location.first_line - 1,
                  token.parseLocation.location.first_column - 1,
                  token.parseLocation.location.last_line - 1,
                  token.parseLocation.location.last_column - 1
                );
                self.addAnchoredMarker(range, token, 'hue-ace-syntax-warning');
              }
              self.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
            })
            .fail(() => {
              // Can happen when tables aren't cached etc.
              self.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
            });
        })
        .fail(() => {
          // Can happen when tables aren't cached etc.
          self.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
        });
    };

    self.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
  }

  isDatabase(databaseIdentifier) {
    const self = this;
    if (!databaseIdentifier) {
      return false;
    }
    const cleanIdentifier = databaseIdentifier
      .replace(/^\s*`/, '')
      .replace(/`\s*$/, '')
      .toLowerCase();
    return self.databaseIndex[cleanIdentifier];
  }

  attachSqlWorker() {
    const self = this;

    const activeTokens = [];

    let lastKnownLocations = {};

    const getLocationsSub = huePubSub.subscribe(
      'get.active.editor.locations',
      (callback, snippet) => {
        if (self.snippet === snippet && (self.snippet.inFocus() || self.snippet.editorMode())) {
          callback(lastKnownLocations);
        }
      }
    );

    self.disposeFunctions.push(() => {
      getLocationsSub.remove();
    });

    const locationWorkerSub = huePubSub.subscribe('ace.sql.location.worker.message', e => {
      if (
        e.data.id !== self.snippet.id() ||
        e.data.editorChangeTime !== self.editor.lastChangeTime ||
        !self.snippet.isSqlDialect()
      ) {
        return;
      }

      lastKnownLocations = {
        id: self.editorId,
        type: self.snippet.type(),
        namespace: self.snippet.namespace(),
        compute: self.snippet.compute(),
        defaultDatabase: self.snippet.database(),
        locations: e.data.locations,
        editorChangeTime: e.data.editorChangeTime,
        activeStatementLocations: e.data.activeStatementLocations,
        totalStatementCount: e.data.totalStatementCount,
        activeStatementIndex: e.data.activeStatementIndex
      };

      // Clear out old parse locations to prevent them from being shown when there's a syntax error in the statement
      while (activeTokens.length > 0) {
        delete activeTokens.pop().parseLocation;
      }

      const tokensToVerify = [];

      e.data.locations.forEach(location => {
        if (
          ['statement', 'selectList', 'whereClause', 'limitClause'].indexOf(location.type) !== -1 ||
          ((location.type === 'table' || location.type === 'column') &&
            typeof location.identifierChain === 'undefined')
        ) {
          return;
        }

        if (
          location.identifierChain &&
          location.identifierChain.length &&
          location.identifierChain[0].name
        ) {
          // The parser isn't aware of the DDL so sometimes it marks complex columns as tables
          // I.e. "Impala SELECT a FROM b.c" Is 'b' a database or a table? If table then 'c' is complex
          if (
            self.snippet.type() === 'impala' &&
            location.identifierChain.length > 2 &&
            (location.type === 'table' || location.type === 'column') &&
            self.isDatabase(location.identifierChain[0].name)
          ) {
            location.type = 'complex';
          }
        }

        let token = self.editor
          .getSession()
          .getTokenAt(location.location.first_line - 1, location.location.first_column);

        // Find open UDFs and prevent them from being marked as missing columns, i.e. cos in "SELECT * FROM foo where cos(a|"
        const rowTokens = self.editor.getSession().getTokens(location.location.first_line - 1);
        if (location.type === 'column' && token && rowTokens) {
          let tokenFound = false;
          let isFunction = false;
          rowTokens.some(rowToken => {
            if (tokenFound && /\s+/.test(rowToken.value)) {
              return false;
            }
            if (tokenFound) {
              isFunction = rowToken.value === '(';
              return true;
            }
            if (rowToken === token) {
              tokenFound = true;
            }
          });
          if (isFunction) {
            location.type = 'function';
            delete location.identifierChain;
            location.function = token.value;
            token = null;
          }
        }

        if (token && token.value && /`$/.test(token.value)) {
          // Ace getTokenAt() thinks the first ` is a token, column +1 will include the first and last.
          token = self.editor
            .getSession()
            .getTokenAt(location.location.first_line - 1, location.location.first_column + 1);
        }
        if (token && token.value && /^\s*\$\{\s*$/.test(token.value)) {
          token = null;
        }
        if (token && token.value) {
          const AceRange = ace.require('ace/range').Range;
          // The Ace tokenizer also splits on '{', '(' etc. hence the actual value;
          token.actualValue = self.editor
            .getSession()
            .getTextRange(
              new AceRange(
                location.location.first_line - 1,
                location.location.first_column - 1,
                location.location.last_line - 1,
                location.location.last_column - 1
              )
            );
        }

        if (token !== null) {
          token.parseLocation = location;
          activeTokens.push(token);
          delete token.notFound;
          delete token.syntaxError;
          if (location.active) {
            tokensToVerify.push(token);
          }
        }
      });

      if (self.snippet.type() === 'impala' || self.snippet.type() === 'hive') {
        self.verifyExists(tokensToVerify, e.data.activeStatementLocations);
      }
      huePubSub.publish('editor.active.locations', lastKnownLocations);
    });

    self.disposeFunctions.push(() => {
      locationWorkerSub.remove();
    });

    let lastContextRequest;
    const statementSubscription = huePubSub.subscribe(
      'editor.active.statement.changed',
      statementDetails => {
        if (statementDetails.id !== self.editorId) {
          return;
        }
        if (self.snippet.isSqlDialect()) {
          if (lastContextRequest) {
            lastContextRequest.dispose();
          }
          lastContextRequest = self.snippet.whenContextSet().done(() => {
            huePubSub.publish('ace.sql.location.worker.post', {
              id: self.snippet.id(),
              statementDetails: statementDetails,
              type: self.snippet.type(),
              namespace: self.snippet.namespace(),
              compute: self.snippet.compute(),
              defaultDatabase: self.snippet.database()
            });
          });
        }
      }
    );

    self.disposeFunctions.push(() => {
      statementSubscription.remove();
    });
  }

  dispose() {
    const self = this;
    if (self.sqlSyntaxWorkerSub !== null) {
      self.sqlSyntaxWorkerSub.remove();
      self.sqlSyntaxWorkerSub = null;
    }

    self.disposeFunctions.forEach(dispose => {
      dispose();
    });
  }
}

export default AceLocationHandler;
