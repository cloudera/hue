import {IdentifierLocation, SyntaxError} from 'parse/types';

declare namespace Ace {
  export interface Editor {
    addError(message:string, line:number): void;
    addWarning(message:string, line:number): void;
    container: HTMLElement;
    completer: any;
    completers: any[];
    clearErrorsAndWarnings(type: string): void;
    customMenuOptions: { [option: string]: (val?: any) => any };
    enabledMenuOptions: { [option: string]: boolean };
    getCursorPosition(): Position;
    getOption(option: string): string|boolean|number;
    getSelectedText(): string;
    getSelectionRange(): Range;
    getSession(): Session
    getTextAfterCursor(): string;
    getTextBeforeCursor(): string;
    getValue(): string;
    lastChangeTime: number;
    off(ev: string, callback: ((e: any) => any) | number): void;
    on(event: string, fn: (e: any) => any): number;
    renderer: {
      lineHeight: number;
      screenToTextCoordinates(left: number, top: number): Position;
      scrollCursorIntoView(position: Position, u: number): void;
      textToScreenCoordinates(row: number, column: number): { pageX: number; pageY: number }
    };
    resize(force: boolean): void;
    scrollToLine(line: number, u: boolean, v: boolean, callback: () => void): void;
    selection: {
      getRange(): Range;
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

  export interface Position {
    column: number;
    row: number;
  }

  export interface Range {
    end: Position | Anchor;
    endColumn:number;
    endRow:number;
    isEmpty(): boolean;
    start: Position | Anchor;
    startColumn:number;
    startRow:number;
  }

  export interface Document {
    createAnchor(position: Position): Anchor;
    createAnchor(x: number, y: number): Anchor;
  }

  export interface Anchor extends Position {
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
    getTextRange(range: Range): string;
    getTokenAt(row: number, column: number): HueToken | null;
    getTokens(line?: number): HueToken[];
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
}
