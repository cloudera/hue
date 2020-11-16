// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { IdentifierLocation, SyntaxError } from 'parse/types';

declare namespace Ace {
  export interface Editor {
    $blockScrolling: number;
    addError(message:string, line:number): void;
    addWarning(message:string, line:number): void;
    container: HTMLElement;
    completer: any;
    completers: any[];
    clearErrorsAndWarnings(type: string): void;
    customMenuOptions: { [option: string]: (val?: any) => any };
    enabledMenuOptions: { [option: string]: boolean };
    execCommand(cmd: string, arg?: unknown): void;
    focus(): void;
    getCursorPosition(): Position;
    getOption(option: string): string|boolean|number;
    getSelectedText(): string;
    getSelectionRange(): Range;
    getSession(): Session
    getTextAfterCursor(): string;
    getTextBeforeCursor(): string;
    getValue(): string;
    keyBinding: {
      addKeyboardHandler(hashHandler: HashHandler): void;
      removeKeyboardHandler(hashHandler: HashHandler): void;
    }
    lastChangeTime: number;
    off(ev: string, callback: ((e: any) => any) | number): void;
    on(event: string, fn: (e: any) => any): number;
    removeTextAfterCursor(length: number): void;
    renderer: {
      scrollLeft: number;
      gutterWidth: number;
      lineHeight: number;
      layerConfig: {
        lineHeight: number;
        offset: number;
      };
      $cursorLayer: {
        getPixelPosition(anchor?: Anchor, b?: boolean): { top: number; left: number };
      };
      screenToTextCoordinates(left: number, top: number): Position;
      scrollCursorIntoView(position?: Position, u?: number): void;
      textToScreenCoordinates(row: number, column: number): { pageX: number; pageY: number }
    };
    resize(force: boolean): void;
    scrollToLine(line: number, u: boolean, v: boolean, callback: () => void): void;
    selection: {
      getRange(): Range;
      getAllRanges(): Range[];
      lead: Position;
    };
    session: Session;
    setOption(option: string, value: OptionValue): void;
    setOptions(options: Options): void;
    setTheme(theme: string): void;
    useHueAutocompleter: boolean;
  }

  export type OptionValue = string | boolean | number;

  export interface Options {
    [option: string]: OptionValue;
  }

  export interface AceUtil {
    retrievePrecedingIdentifier(row: number, column: number, regex?: RegExp): string;
  }

  export interface Position {
    column: number;
    row: number;
  }

  export interface SimpleRange {
    end: Position | Anchor;
    start: Position | Anchor;
  }

  export interface Range extends SimpleRange {
    endColumn: number;
    endRow: number;
    isEmpty(): boolean;
    startColumn: number;
    startRow: number;
  }

  export interface Document {
    createAnchor(position: Position): Anchor;
    createAnchor(x: number, y: number): Anchor;
  }

  export interface Anchor extends Position {
    $insertRight: boolean;
    detach(): void;
    getPosition(): Position;
    on(event: string, fn: (e: any) => any): number;
    setPosition(row: number, column: number, noClip?: boolean): void;
  }

  export interface Marker {
    clazz: string;
    dispose(): void;
    range: Range;
    token: HueToken;
  }

  export interface Session {
    $backMarkers: { [markerId: number]: Marker };
    addGutterDecoration(line: number, clazz: string): void;
    addMarker(range: Range, clazz: string): number;
    doc: Document;
    getLine(row: number): number;
    getTextRange(range: SimpleRange): string;
    getTokenAt(row: number, column: number): HueToken | null;
    getTokens(line?: number): HueToken[];
    remove(range: Range): void;
    removeGutterDecoration(line: number, clazz: string): void;
    removeMarker(markerId: number): void;
    setMode(mode: string): void;
  }

  export interface HueToken {
    actualValue: string;
    index?: number;
    notFound?: boolean;
    parseLocation?: IdentifierLocation;
    qualifiedIdentifier?: string;
    start?: number;
    syntaxError?: SyntaxError;
    value: string;
  }

  export class HashHandler {
    constructor();
    bindKeys(bindings: { [keys: string]: (editor: Ace.Editor, event: unknown) => void }): void;
  }
}
