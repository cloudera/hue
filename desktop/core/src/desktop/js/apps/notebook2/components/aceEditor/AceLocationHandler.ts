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
import ace from 'ext/aceHelper';

import apiHelper from 'api/apiHelper';
import Executor from 'apps/notebook2/execution/executor';
import DataCatalogEntry from 'catalog/dataCatalogEntry';
import SubscriptionTracker, { Disposable } from 'components/utils/SubscriptionTracker';
import AssistStorageEntry from 'ko/components/assist/assistStorageEntry';
import dataCatalog from 'catalog/dataCatalog';
import { IdentifierChainEntry, IdentifierLocation, ParsedLocation, ParsedTable } from 'parse/types';
import { EditorInterpreter } from 'types/config';
import { hueWindow } from 'types/types';
import huePubSub, { HueSubscription } from 'utils/huePubSub';
import I18n from 'utils/i18n';
import sqlStatementsParser, { ParsedSqlStatement } from 'parse/sqlStatementsParser';
import sqlUtils from 'sql/sqlUtils';
import stringDistance from 'sql/stringDistance';
import { DIALECT } from 'apps/notebook2/snippet';
import {
  POST_FROM_LOCATION_WORKER_EVENT,
  POST_FROM_SYNTAX_WORKER_EVENT,
  POST_TO_LOCATION_WORKER_EVENT,
  POST_TO_SYNTAX_WORKER_EVENT
} from 'sql/sqlWorkerHandler';

export const REFRESH_STATEMENT_LOCATIONS_EVENT = 'editor.refresh.statement.locations';
export const ACTIVE_STATEMENT_CHANGED_EVENT = 'editor.active.statement.changed';
export const CURSOR_POSITION_CHANGED_EVENT = 'editor.cursor.position.changed';

const STATEMENT_COUNT_AROUND_ACTIVE = 10;

const VERIFY_LIMIT = 50;
const VERIFY_DELAY = 50;

const EXPAND_STAR_LABEL = I18n('Right-click to expand with columns');
const CONTEXT_TOOLTIP_LABEL = I18n('Right-click to expand with columns');

const isPointInside = (parseLocation: ParsedLocation, editorPosition: Ace.Position) => {
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

const getFirstPosition = (
  editorPositionOne: Ace.Position,
  editorPositionTwo: Ace.Position
): Ace.Position => {
  if (editorPositionOne.row === editorPositionTwo.row) {
    return editorPositionOne.column <= editorPositionTwo.column
      ? editorPositionOne
      : editorPositionTwo;
  }
  return editorPositionOne.row < editorPositionTwo.row ? editorPositionOne : editorPositionTwo;
};

const equalPositions = (editorPositionOne: Ace.Position, editorPositionTwo: Ace.Position) =>
  editorPositionOne.row === editorPositionTwo.row &&
  editorPositionOne.column === editorPositionTwo.column;

export default class AceLocationHandler implements Disposable {
  editor: Ace.Editor;
  editorId: string;
  executor: Executor;
  temporaryOnly: boolean;

  subTracker: SubscriptionTracker = new SubscriptionTracker();
  availableDatabases = new Set<string>();
  verifyThrottle = -1;
  sqlSyntaxWorkerSub?: HueSubscription;

  constructor(options: {
    editor: Ace.Editor;
    editorId: string;
    executor: Executor;
    temporaryOnly?: boolean;
  }) {
    this.editor = options.editor;
    this.editorId = options.editorId;
    this.executor = options.executor;
    this.temporaryOnly = !!options.temporaryOnly;

    this.attachStatementLocator();
    this.attachSqlWorker();
    this.attachMouseListeners();

    this.subTracker.subscribe(this.executor.connector, this.updateAvailableDatabases.bind(this));
    this.updateAvailableDatabases();
  }

  private updateAvailableDatabases() {
    dataCatalog
      .getChildren({
        connector: this.executor.connector(),
        namespace: this.executor.namespace(),
        compute: this.executor.compute(),
        path: []
      })
      .then(children => {
        this.availableDatabases.clear();
        children.forEach((dbEntry: DataCatalogEntry) => {
          this.availableDatabases.add(dbEntry.getDisplayName(false).toLowerCase());
        });
      });
  }

  private isSqlDialect(): boolean {
    return (<EditorInterpreter>this.executor.connector()).is_sql;
  }

  private getDialect(): string | undefined {
    return this.executor.connector().dialect;
  }

  attachMouseListeners(): void {
    const Tooltip = ace.require('ace/tooltip').Tooltip;
    const AceRange = ace.require('ace/range').Range;

    const contextTooltip = new Tooltip(this.editor.container);
    let tooltipTimeout = -1;
    let disableTooltip = false;
    let lastHoveredToken: Ace.HueToken | null = null;
    const activeMarkers: number[] = [];
    let keepLastMarker = false;

    const hideContextTooltip = () => {
      clearTimeout(tooltipTimeout);
      contextTooltip.hide();
    };

    const clearActiveMarkers = () => {
      hideContextTooltip();
      while (activeMarkers.length > (keepLastMarker ? 1 : 0)) {
        const marker = activeMarkers.shift();
        if (typeof marker !== 'undefined') {
          this.editor.session.removeMarker(marker);
        }
      }
    };

    const markLocation = (parseLocation: IdentifierLocation) => {
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
      activeMarkers.push(this.editor.session.addMarker(range, 'hue-ace-location'));
      return range;
    };

    this.subTracker.subscribe('context.popover.shown', () => {
      hideContextTooltip();
      keepLastMarker = true;
      disableTooltip = true;
    });

    this.subTracker.subscribe('context.popover.hidden', () => {
      disableTooltip = false;
      clearActiveMarkers();
      keepLastMarker = false;
    });

    const mousemoveListener = this.editor.on('mousemove', e => {
      clearTimeout(tooltipTimeout);
      const selectionRange = this.editor.selection.getRange();
      if (selectionRange.isEmpty()) {
        const pointerPosition = this.editor.renderer.screenToTextCoordinates(
          e.clientX + 5,
          e.clientY
        );
        const endTestPosition = this.editor.renderer.screenToTextCoordinates(
          e.clientX + 15,
          e.clientY
        );
        if (endTestPosition.column !== pointerPosition.column) {
          const token = this.editor.session.getTokenAt(pointerPosition.row, pointerPosition.column);
          if (
            token !== null &&
            !token.notFound &&
            token.parseLocation &&
            !disableTooltip &&
            token.parseLocation.type !== 'alias'
          ) {
            tooltipTimeout = window.setTimeout(() => {
              if (token.parseLocation) {
                const endCoordinates = this.editor.renderer.textToScreenCoordinates(
                  pointerPosition.row,
                  token.start || 0
                );

                let tooltipText =
                  token.parseLocation.type === 'asterisk'
                    ? EXPAND_STAR_LABEL
                    : CONTEXT_TOOLTIP_LABEL;
                let colType;
                if (token.parseLocation.type === 'column') {
                  const tableChain = [...(token.parseLocation.identifierChain || [])];
                  const lastIdentifier = tableChain.pop();
                  if (tableChain.length > 0 && lastIdentifier && lastIdentifier.name) {
                    const colName = lastIdentifier.name.toLowerCase();
                    // Note, as cachedOnly is set to true it will call the successCallback right away (or not at all)
                    dataCatalog
                      .getEntry({
                        namespace: this.executor.namespace(),
                        compute: this.executor.compute(),
                        connector: this.executor.connector(),
                        temporaryOnly: this.temporaryOnly,
                        path: tableChain.map(identifier => identifier.name)
                      })
                      .done(entry => {
                        entry
                          .getSourceMeta({ cachedOnly: true, silenceErrors: true })
                          .done(sourceMeta => {
                            if (sourceMeta && sourceMeta.extended_columns) {
                              sourceMeta.extended_columns.every(
                                (col: { name: string; type: string }) => {
                                  if (col.name.toLowerCase() === colName) {
                                    colType = (col.type.match(/^[^<]*/g) || ['T'])[0];
                                    return false;
                                  }
                                  return true;
                                }
                              );
                            }
                          });
                      });
                  }
                }
                if (token.parseLocation.identifierChain) {
                  let sqlIdentifier = token.parseLocation.identifierChain
                    .map(identifier => identifier.name)
                    .join('.');
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
                  endCoordinates.pageY + this.editor.renderer.lineHeight + 3
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
                const endCoordinates = this.editor.renderer.textToScreenCoordinates(
                  pointerPosition.row,
                  token.start || 0
                );
                contextTooltip.show(
                  tooltipText,
                  endCoordinates.pageX,
                  endCoordinates.pageY + this.editor.renderer.lineHeight + 3
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
                  const endCoordinates = this.editor.renderer.textToScreenCoordinates(
                    pointerPosition.row,
                    token.start || 0
                  );
                  contextTooltip.show(
                    tooltipText,
                    endCoordinates.pageX,
                    endCoordinates.pageY + this.editor.renderer.lineHeight + 3
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

    this.subTracker.addDisposable({
      dispose: () => this.editor.off('mousemove', mousemoveListener)
    });

    const inputListener = this.editor.on('input', () => {
      clearActiveMarkers();
      lastHoveredToken = null;
    });

    this.subTracker.addDisposable({
      dispose: () => this.editor.off('input', inputListener)
    });

    const mouseoutListener = function () {
      clearActiveMarkers();
      clearTimeout(tooltipTimeout);
      contextTooltip.hide();
      lastHoveredToken = null;
    };

    this.editor.container.addEventListener('mouseout', mouseoutListener);

    this.subTracker.addDisposable({
      dispose: () => this.editor.container.removeEventListener('mouseout', mouseoutListener)
    });

    const onContextMenu = (e: { clientX: number; clientY: number; preventDefault: () => void }) => {
      const selectionRange = this.editor.selection.getRange();
      huePubSub.publish('context.popover.hide');
      huePubSub.publish('sql.syntax.dropdown.hide');
      if (selectionRange.isEmpty()) {
        const pointerPosition = this.editor.renderer.screenToTextCoordinates(
          e.clientX + 5,
          e.clientY
        );
        const token = this.editor.session.getTokenAt(pointerPosition.row, pointerPosition.column);
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
                (token.syntaxError && token.syntaxError.loc.first_line - 1) || 1,
                (token.syntaxError && token.syntaxError.loc.first_column) || 1,
                (token.syntaxError && token.syntaxError.loc.last_line - 1) || 1,
                (token.syntaxError &&
                  token.syntaxError.loc.first_column + token.syntaxError.text.length) ||
                  1
              );

          const startCoordinates = this.editor.renderer.textToScreenCoordinates(
            range.start.row,
            range.start.column
          );
          const endCoordinates = this.editor.renderer.textToScreenCoordinates(
            range.end.row,
            range.end.column
          );
          const source = {
            // TODO: add element likely in the event
            left: startCoordinates.pageX - 3,
            top: startCoordinates.pageY,
            right: endCoordinates.pageX - 3,
            bottom: endCoordinates.pageY + this.editor.renderer.lineHeight
          };

          if (token.parseLocation && token.parseLocation.identifierChain && !token.notFound) {
            token.parseLocation
              .resolveCatalogEntry({
                temporaryOnly: this.temporaryOnly
              })
              .done(entry => {
                huePubSub.publish('context.popover.show', {
                  data: {
                    type: 'catalogEntry',
                    catalogEntry: entry
                  },
                  pinEnabled: true,
                  connector: this.executor.connector(),
                  source: source
                });
              })
              .fail(() => {
                token.notFound = true;
              });
          } else if (token.parseLocation && !token.notFound) {
            const parseLocation = token.parseLocation;
            // Asterisk, function etc.
            if (parseLocation.type === 'file' && parseLocation.path) {
              AssistStorageEntry.getEntry(parseLocation.path).then(entry => {
                entry.open(true);
                huePubSub.publish('context.popover.show', {
                  data: {
                    type: 'storageEntry',
                    storageEntry: entry,
                    editorLocation: parseLocation.location
                  },
                  connector: this.executor.connector(),
                  pinEnabled: true,
                  source: source
                });
              });
            } else {
              huePubSub.publish('context.popover.show', {
                data: parseLocation,
                connector: this.executor.connector(),
                sourceType: this.executor.connector().dialect,
                namespace: this.executor.namespace(),
                compute: this.executor.compute(),
                defaultDatabase: this.executor.database(),
                pinEnabled: true,
                source: source
              });
            }
          } else if (token.syntaxError) {
            huePubSub.publish('sql.syntax.dropdown.show', {
              editorId: this.editorId,
              data: token.syntaxError,
              editor: this.editor,
              range: range,
              sourceType: this.executor.connector().dialect,
              defaultDatabase: this.executor.database(),
              source: source
            });
          }
          e.preventDefault();
          return false;
        }
      }
    };

    this.editor.container.addEventListener('contextmenu', onContextMenu);

    this.subTracker.addDisposable({
      dispose: () => this.editor.container.removeEventListener('contextmenu', onContextMenu)
    });
  }

  attachStatementLocator(): void {
    const lastKnownStatements = {
      editorChangeTime: 0,
      statements: <ParsedSqlStatement[]>[]
    };
    let activeStatement: ParsedSqlStatement | undefined;
    //let lastExecutingStatement = null;

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const updateActiveStatement = (cursorChange?: boolean) => {
      if (!this.isSqlDialect()) {
        return;
      }
      const selectionRange = this.editor.getSelectionRange();
      const cursorLocation = selectionRange.start;
      if (!equalPositions(selectionRange.start, selectionRange.end)) {
        // TODO: Figure out what this does and why it needs the result.statement_range
        // if (!cursorChange && this.snippet.result && this.snippet.result.statement_range()) {
        //   let executingStatement = this.snippet.result.statement_range();
        //   // Row and col are 0 for both start and end on execute, so if the selection hasn't changed we'll use last known executed statement
        //   if (
        //     executingStatement.start.row === 0 &&
        //     executingStatement.start.column === 0 &&
        //     executingStatement.end.row === 0 &&
        //     executingStatement.end.column === 0 &&
        //     lastExecutingStatement
        //   ) {
        //     executingStatement = lastExecutingStatement;
        //   }
        //   if (executingStatement.start.row === 0) {
        //     cursorLocation.column += executingStatement.start.column;
        //   } else if (executingStatement.start.row !== 0 || executingStatement.start.column !== 0) {
        //     cursorLocation.row += executingStatement.start.row;
        //     cursorLocation.column = executingStatement.start.column;
        //   }
        //   lastExecutingStatement = executingStatement;
        // } else {
        //   lastExecutingStatement = null;
        // }
      }

      const selectedStatements: ParsedSqlStatement[] = [];
      const precedingStatements: ParsedSqlStatement[] = [];
      const followingStatements: ParsedSqlStatement[] = [];
      activeStatement = undefined;

      const firstSelectionPoint = getFirstPosition(selectionRange.start, selectionRange.end);
      const lastSelectionPoint =
        selectionRange.start === firstSelectionPoint ? selectionRange.end : selectionRange.start;

      let found = false;
      let statementIndex = 0;
      let insideSelection = false;
      if (lastKnownStatements.statements.length === 1) {
        activeStatement = lastKnownStatements.statements[0];
      } else {
        lastKnownStatements.statements.forEach(statement => {
          if (!equalPositions(firstSelectionPoint, lastSelectionPoint)) {
            if (!insideSelection && isPointInside(statement.location, firstSelectionPoint)) {
              insideSelection = true;
            }
            if (insideSelection) {
              selectedStatements.push(statement);

              if (
                isPointInside(statement.location, lastSelectionPoint) ||
                (statement.location.last_line === lastSelectionPoint.row + 1 &&
                  statement.location.last_column === lastSelectionPoint.column)
              ) {
                insideSelection = false;
              }
            }
          }
          if (isPointInside(statement.location, cursorLocation)) {
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
          activeStatement =
            lastKnownStatements.statements[lastKnownStatements.statements.length - 1];
        }
      }

      if (!selectedStatements.length && activeStatement) {
        selectedStatements.push(activeStatement);
      }

      huePubSub.publish(ACTIVE_STATEMENT_CHANGED_EVENT, {
        id: this.editorId,
        editorChangeTime: lastKnownStatements.editorChangeTime,
        activeStatementIndex: statementIndex,
        totalStatementCount: lastKnownStatements.statements.length,
        precedingStatements: precedingStatements,
        activeStatement: activeStatement,
        selectedStatements: selectedStatements,
        followingStatements: followingStatements
      });

      if (activeStatement) {
        this.checkForSyntaxErrors(activeStatement.location, firstSelectionPoint);
      }
    };

    const parseForStatements = () => {
      if (this.isSqlDialect()) {
        try {
          const lastChangeTime = this.editor.lastChangeTime;
          lastKnownStatements.statements = sqlStatementsParser.parse(this.editor.getValue());
          lastKnownStatements.editorChangeTime = lastChangeTime;

          const hueDebug = (<hueWindow>window).hueDebug;
          if (hueDebug && hueDebug.logStatementLocations) {
            // eslint-disable-next-line no-restricted-syntax
            console.log(lastKnownStatements);
          }
        } catch (error) {
          console.warn('Could not parse statements!');
          console.warn(error);
        }
      }
    };

    let changeThrottle = window.setTimeout(parseForStatements, 0);
    this.subTracker.trackTimeout(changeThrottle);

    window.setTimeout(updateActiveStatement, 0);

    let cursorChangePaused = false; // On change the cursor is also moved, this limits the calls while typing

    let lastStart: Ace.Position;
    let lastEnd: Ace.Position;
    let lastCursorPosition: Ace.Position;
    const changeSelectionListener = this.editor.on('changeSelection', () => {
      if (cursorChangePaused) {
        return;
      }
      window.clearTimeout(changeThrottle);
      changeThrottle = window.setTimeout(() => {
        const newCursorPosition = this.editor.getCursorPosition();
        if (
          !lastCursorPosition ||
          lastCursorPosition.row !== newCursorPosition.row ||
          lastCursorPosition.column !== newCursorPosition.column
        ) {
          huePubSub.publish(CURSOR_POSITION_CHANGED_EVENT, {
            editorId: this.editorId,
            position: newCursorPosition
          });
          lastCursorPosition = newCursorPosition;
        }

        // The active statement is initially the top one in the selection, batch execution updates this.
        const newStart = this.editor.getSelectionRange().start;
        const newEnd = this.editor.getSelectionRange().end;
        if (
          this.isSqlDialect() &&
          (!lastStart ||
            !equalPositions(lastStart, newStart) ||
            !lastEnd ||
            !equalPositions(lastEnd, newEnd))
        ) {
          updateActiveStatement(true);
          lastStart = newStart;
          lastEnd = newEnd;
        }
      }, 100);
    });

    this.subTracker.addDisposable({
      dispose: () => this.editor.off('changeSelection', changeSelectionListener)
    });

    const changeListener = this.editor.on('change', () => {
      if (this.isSqlDialect()) {
        window.clearTimeout(changeThrottle);
        cursorChangePaused = true;
        changeThrottle = window.setTimeout(() => {
          parseForStatements();
          updateActiveStatement();
          cursorChangePaused = false;
        }, 500);
        this.editor.lastChangeTime = Date.now();
      }
    });

    this.subTracker.addDisposable({
      dispose: () => this.editor.off('change', changeListener)
    });

    this.subTracker.subscribe(REFRESH_STATEMENT_LOCATIONS_EVENT, editorId => {
      if (editorId === this.editorId) {
        cursorChangePaused = true;
        window.clearTimeout(changeThrottle);
        parseForStatements();
        updateActiveStatement();
        cursorChangePaused = false;
      }
    });
  }

  clearMarkedErrors(type?: string): void {
    const markers = this.editor.getSession().$backMarkers;
    for (const markerId in markers) {
      if (markers[markerId].clazz.indexOf('hue-ace-syntax-' + (type || '')) === 0) {
        markers[markerId].dispose();
      }
    }
  }

  checkForSyntaxErrors(statementLocation: ParsedLocation, cursorPosition: Ace.Position): void {
    if (
      this.sqlSyntaxWorkerSub &&
      (this.getDialect() === DIALECT.impala || this.getDialect() === DIALECT.hive)
    ) {
      const AceRange = ace.require('ace/range').Range;
      const editorChangeTime = this.editor.lastChangeTime;
      const beforeCursor = this.editor
        .getSession()
        .getTextRange(
          new AceRange(
            statementLocation.first_line - 1,
            statementLocation.first_column,
            cursorPosition.row,
            cursorPosition.column
          )
        );
      const afterCursor = this.editor
        .getSession()
        .getTextRange(
          new AceRange(
            cursorPosition.row,
            cursorPosition.column,
            statementLocation.last_line - 1,
            statementLocation.last_column
          )
        );
      huePubSub.publish(POST_TO_SYNTAX_WORKER_EVENT, {
        id: this.editorId,
        editorChangeTime: editorChangeTime,
        beforeCursor: beforeCursor,
        afterCursor: afterCursor,
        statementLocation: statementLocation,
        connector: this.executor.connector()
      });
    }
  }

  addAnchoredMarker(range: Ace.Range, token: Ace.HueToken, clazz: string): void {
    range.start = this.editor.getSession().doc.createAnchor(range.start);
    range.end = this.editor.getSession().doc.createAnchor(range.end);
    const markerId = this.editor.getSession().addMarker(range, clazz);
    const marker = this.editor.getSession().$backMarkers[markerId];
    marker.token = token;
    marker.dispose = () => {
      (<Ace.Anchor>range.start).detach();
      (<Ace.Anchor>range.end).detach();
      delete marker.token.syntaxError;
      delete marker.token.notFound;
      this.editor.getSession().removeMarker(markerId);
    };
  }

  attachSqlSyntaxWorker(): void {
    if (this.sqlSyntaxWorkerSub) {
      return;
    }

    this.sqlSyntaxWorkerSub = huePubSub.subscribe(POST_FROM_SYNTAX_WORKER_EVENT, e => {
      if (e.data.id !== this.editorId || e.data.editorChangeTime !== this.editor.lastChangeTime) {
        return;
      }
      this.clearMarkedErrors('error');

      if (
        !e.data.syntaxError ||
        !e.data.syntaxError.expected ||
        e.data.syntaxError.expected.length === 0
      ) {
        // Only show errors that we have suggestions for
        return;
      }

      const suppressedRules = apiHelper.getFromTotalStorage(
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
        // TODO: Figure out why this is needed.

        // if (
        //   this.snippet.positionStatement() &&
        //   sqlUtils.locationEquals(
        //     e.data.statementLocation,
        //     this.snippet.positionStatement().location
        //   )
        // ) {
        //   this.snippet.positionStatement().syntaxError = true;
        // }
        const hueDebug = (<hueWindow>window).hueDebug;
        if (hueDebug && hueDebug.showSyntaxParseResult) {
          // eslint-disable-next-line no-restricted-syntax
          console.log(e.data.syntaxError);
        }

        const token = this.editor
          .getSession()
          .getTokenAt(
            e.data.syntaxError.loc.first_line - 1,
            e.data.syntaxError.loc.first_column + 1
          );

        // Don't mark the current edited word as an error if the cursor is at the end of the word
        // For now [a-z] is fine as we only check syntax for keywords
        if (
          /[a-z]$/i.test(this.editor.getTextBeforeCursor()) &&
          !/^[a-z]/i.test(this.editor.getTextAfterCursor())
        ) {
          const cursorPos = this.editor.getCursorPosition();
          const cursorToken = this.editor.getSession().getTokenAt(cursorPos.row, cursorPos.column);
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
          this.addAnchoredMarker(range, token, 'hue-ace-syntax-error');
        }
      }
    });

    huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, this.editorId);
  }

  detachSqlSyntaxWorker(): void {
    if (this.sqlSyntaxWorkerSub) {
      this.sqlSyntaxWorkerSub.remove();
      this.sqlSyntaxWorkerSub = undefined;
    }
    this.clearMarkedErrors();
  }

  async fetchChildren(identifierChain: IdentifierChainEntry[]): Promise<DataCatalogEntry[]> {
    return new Promise((resolve, reject) => {
      dataCatalog
        .getChildren({
          connector: this.executor.connector(),
          namespace: this.executor.namespace(),
          compute: this.executor.compute(),
          temporaryOnly: this.temporaryOnly,
          path: identifierChain.map(identifier => identifier.name),
          silenceErrors: true,
          cachedOnly: true
        })
        .done(resolve)
        .fail(reject);
    });
  }

  async fetchPossibleValues(
    token: Ace.HueToken
  ): Promise<(DataCatalogEntry | IdentifierChainEntry)[]> {
    if (
      token.parseLocation &&
      token.parseLocation.tables &&
      token.parseLocation.tables.length > 0
    ) {
      const tablePromises: Promise<DataCatalogEntry[]>[] = [];
      token.parseLocation.tables.forEach(table => {
        if (table.identifierChain) {
          tablePromises.push(this.fetchChildren(table.identifierChain));
        }
      });
      const children = await Promise.all(tablePromises);
      const joined: (DataCatalogEntry | IdentifierChainEntry)[] = [];
      children.forEach(childEntries => {
        joined.push(...childEntries);
      });
      if (
        token.parseLocation &&
        token.parseLocation.type === 'column' &&
        token.parseLocation.tables
      ) {
        // Could be a table reference
        token.parseLocation.tables.forEach(table => {
          if (!table.alias) {
            // Aliases are added later
            joined.push(table.identifierChain[table.identifierChain.length - 1]);
          }
        });
      }
      return joined;
    }

    if (
      token.parseLocation &&
      token.parseLocation.identifierChain &&
      token.parseLocation.identifierChain.length
    ) {
      // fetch the parent
      return await this.fetchChildren(
        token.parseLocation.identifierChain.slice(0, token.parseLocation.identifierChain.length - 1)
      );
    }

    return [];
  }

  verifyExists(tokens: Ace.HueToken[], allLocations: IdentifierLocation[]): void {
    window.clearInterval(this.verifyThrottle);
    this.clearMarkedErrors('warning');

    if (!this.sqlSyntaxWorkerSub) {
      return;
    }

    const cursorPos = this.editor.getCursorPosition();

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

    const aliasIndex: { [alias: string]: IdentifierLocation } = {};
    const aliases: { name: string }[] = [];

    allLocations.forEach(location => {
      if (
        location.type === 'alias' &&
        location.alias &&
        (location.source === 'column' ||
          location.source === 'table' ||
          location.source === 'subquery' ||
          location.source === 'cte')
      ) {
        aliasIndex[location.alias.toLowerCase()] = location;
        aliases.push({ name: location.alias.toLowerCase() });
      }
    });

    const resolvePathFromTables = (location: IdentifierLocation): Promise<void> => {
      return new Promise(resolve => {
        if (
          location.type === 'column' &&
          location.tables &&
          location.identifierChain &&
          location.identifierChain.length === 1
        ) {
          const findIdentifierChainInTable = (tablesToGo: ParsedTable[]) => {
            const nextTable = tablesToGo.shift();
            if (nextTable && !nextTable.subQuery) {
              dataCatalog
                .getChildren({
                  connector: this.executor.connector(),
                  namespace: this.executor.namespace(),
                  compute: this.executor.compute(),
                  temporaryOnly: this.temporaryOnly,
                  path: nextTable.identifierChain.map(identifier => identifier.name),
                  cachedOnly: true,
                  silenceErrors: true
                })
                .done((entries: DataCatalogEntry[]) => {
                  const containsColumn = entries.some(
                    entry =>
                      location.identifierChain &&
                      sqlUtils.identifierEquals(
                        entry.getDisplayName(false),
                        location.identifierChain[0].name
                      )
                  );

                  if (containsColumn) {
                    location.identifierChain = [
                      ...nextTable.identifierChain,
                      ...(location.identifierChain || [])
                    ];
                    delete location.tables;
                    resolve();
                  } else if (tablesToGo.length) {
                    findIdentifierChainInTable(tablesToGo);
                  } else {
                    resolve();
                  }
                })
                .fail(() => resolve());
            } else if (tablesToGo.length > 0) {
              findIdentifierChainInTable(tablesToGo);
            } else {
              resolve();
            }
          };
          if (location.tables.length > 1) {
            findIdentifierChainInTable([...location.tables]);
          } else if (location.tables.length === 1 && location.tables[0].identifierChain) {
            location.identifierChain = [
              ...location.tables[0].identifierChain,
              ...location.identifierChain
            ];
            delete location.tables;
            resolve();
          }
        } else {
          resolve();
        }
      });
    };

    const verify = () => {
      const token = tokensToVerify.shift();
      if (!token) {
        return;
      }
      const location = token.parseLocation;
      if (!location) {
        return;
      }

      // TODO: Verify columns in sub queries, i.e. 'code' in 'select code from (select * from web_logs) wl, customers c;'
      if ((location.type === 'column' || location.type === 'complex') && location.tables) {
        const hasSubQueries = location.tables.some(table => !!table.subQuery);
        if (hasSubQueries) {
          this.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
          return;
        }
      }

      resolvePathFromTables(location)
        .then(() => {
          if (location.type === 'column') {
            let possibleAlias;
            if (
              location.tables &&
              location.identifierChain &&
              location.identifierChain.length > 1 &&
              token.parseLocation &&
              token.parseLocation.identifierChain
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
              this.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
              return;
            }
          }

          this.fetchPossibleValues(token)
            .then(async possibleValues => {
              // Tokens might change while making api calls
              if (!token.parseLocation) {
                this.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
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
              const uniqueSet = new Set<string>();
              const uniqueValues: IdentifierChainEntry[] = [];
              for (let i = 0; i < possibleValues.length; i++) {
                const entry = <IdentifierChainEntry>possibleValues[i];
                entry.name = await sqlUtils.backTickIfNeeded(this.executor.connector(), entry.name);
                const nameLower = entry.name.toLowerCase();
                if (
                  nameLower === tokenValLower ||
                  (tokenValLower.indexOf('`') === 0 &&
                    tokenValLower.replace(/`/g, '') === nameLower)
                ) {
                  // Break if found
                  this.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
                  return;
                }
                if (!uniqueSet.has(nameLower)) {
                  uniqueValues.push(entry);
                  uniqueSet.add(nameLower);
                }
              }
              possibleValues = uniqueValues;

              const isLowerCase = tokenValLower === token.value;

              const weightedExpected = possibleValues.map(entry => {
                const name = (<IdentifierChainEntry>entry).name;
                return {
                  text: isLowerCase ? name.toLowerCase() : name,
                  distance: stringDistance(token.value, name)
                };
              });
              weightedExpected.sort((a, b) =>
                a.distance === b.distance ? a.text.localeCompare(b.text) : a.distance - b.distance
              );
              token.syntaxError = {
                loc: token.parseLocation.location,
                text: token.value,
                expected: weightedExpected.slice(0, 50)
              };
              token.notFound = true;

              if (
                token.parseLocation &&
                token.parseLocation.type === 'table' &&
                token.parseLocation.identifierChain
              ) {
                token.qualifiedIdentifier = token.parseLocation.identifierChain
                  .map(identifier => identifier.name)
                  .join('.');
              }

              if (token.parseLocation && weightedExpected.length > 0) {
                const AceRange = ace.require('ace/range').Range;
                const range = new AceRange(
                  token.parseLocation.location.first_line - 1,
                  token.parseLocation.location.first_column - 1,
                  token.parseLocation.location.last_line - 1,
                  token.parseLocation.location.last_column - 1
                );
                this.addAnchoredMarker(range, token, 'hue-ace-syntax-warning');
              }
              this.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
            })
            .catch(() => {
              // Can happen when tables aren't cached etc.
              this.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
            });
        })
        .catch(() => {
          // Can happen when tables aren't cached etc.
          this.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
        });
    };

    this.verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
  }

  isDatabase(databaseIdentifier: string): boolean {
    if (!databaseIdentifier) {
      return false;
    }
    const cleanIdentifier = databaseIdentifier
      .replace(/^\s*`/, '')
      .replace(/`\s*$/, '')
      .toLowerCase();
    return this.availableDatabases.has(cleanIdentifier);
  }

  attachSqlWorker(): void {
    const activeTokens: Ace.HueToken[] = [];

    let lastKnownLocations = {};

    this.subTracker.subscribe('get.active.editor.locations', callback => {
      callback(lastKnownLocations);
    });

    this.subTracker.subscribe(
      POST_FROM_LOCATION_WORKER_EVENT,
      (e: {
        data: {
          id: string;
          editorChangeTime: number;
          locations: IdentifierLocation[];
          activeStatementLocations: IdentifierLocation[];
          totalStatementCount: number;
          activeStatementIndex: number;
          precedingStatements: IdentifierLocation[];
          activeStatement: IdentifierLocation;
          selectedStatements: IdentifierLocation[];
          followingStatements: IdentifierLocation[];
        };
      }) => {
        if (
          e.data.id !== this.editorId ||
          e.data.editorChangeTime !== this.editor.lastChangeTime ||
          !this.isSqlDialect()
        ) {
          return;
        }

        lastKnownLocations = {
          id: this.editorId,
          connector: this.executor.connector(),
          namespace: this.executor.namespace(),
          compute: this.executor.compute(),
          defaultDatabase: this.executor.database(),
          locations: e.data.locations,
          editorChangeTime: e.data.editorChangeTime,
          activeStatementLocations: e.data.activeStatementLocations,
          totalStatementCount: e.data.totalStatementCount,
          activeStatementIndex: e.data.activeStatementIndex
        };

        // Clear out old parse locations to prevent them from being shown when there's a syntax error in the statement
        while (activeTokens.length > 0) {
          const activeToken = activeTokens.pop();
          if (activeToken) {
            delete activeToken.parseLocation;
          }
        }

        const tokensToVerify: Ace.HueToken[] = [];

        e.data.locations.forEach(location => {
          if (location.type === 'statementType' && this.getDialect() !== DIALECT.impala) {
            // We currently only have a good mapping from statement types to impala topics.
            // TODO: Extract links between Hive topic IDs and statement types
            return;
          }
          if (
            ['statement', 'selectList', 'whereClause', 'limitClause'].indexOf(location.type) !==
              -1 ||
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
              this.getDialect() === DIALECT.impala &&
              location.identifierChain.length > 2 &&
              (location.type === 'table' || location.type === 'column') &&
              this.isDatabase(location.identifierChain[0].name)
            ) {
              location.type = 'complex';
            }
          }

          let token = this.editor
            .getSession()
            .getTokenAt(location.location.first_line - 1, location.location.first_column);

          // Find open UDFs and prevent them from being marked as missing columns, i.e. cos in "SELECT * FROM foo where cos(a|"
          const rowTokens = this.editor.getSession().getTokens(location.location.first_line - 1);
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
            token = this.editor
              .getSession()
              .getTokenAt(location.location.first_line - 1, location.location.first_column + 1);
          }
          if (token && token.value && /^\s*\${\s*$/.test(token.value)) {
            token = null;
          }
          if (token && token.value) {
            const AceRange = ace.require('ace/range').Range;
            // The Ace tokenizer also splits on '{', '(' etc. hence the actual value;
            token.actualValue = this.editor
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

        if (this.getDialect() === DIALECT.impala || this.getDialect() === DIALECT.hive) {
          this.verifyExists(tokensToVerify, e.data.activeStatementLocations);
        }
        huePubSub.publish('editor.active.locations', lastKnownLocations);
      }
    );

    this.subTracker.subscribe('editor.active.statement.changed', statementDetails => {
      if (statementDetails.id !== this.editorId) {
        return;
      }
      if (this.isSqlDialect()) {
        huePubSub.publish(POST_TO_LOCATION_WORKER_EVENT, {
          id: this.editorId,
          statementDetails: statementDetails,
          connector: this.executor.connector(),
          namespace: this.executor.namespace(),
          compute: this.executor.compute(),
          defaultDatabase: this.executor.database()
        });
      }
    });
  }

  dispose(): void {
    this.subTracker.dispose();
    this.detachSqlSyntaxWorker();
  }
}
