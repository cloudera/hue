/*
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

// The Error interface is based on the new Improved Hue Error UX
// specification. It is not yet implemented but lets try to follow the
// spec since it wil become the new standard.
//
// EXAMPLE - adding an error to the UI:
// throw new HueErrorProperties('It failed big time', {errorCode: 01});
// EXAMPLE - using cause to wrap an existing error:
// catch (e: Error) { throw new HueErrorProperties('Better msg', {cause: e}); }

export interface HueErrorProperties {
  message: string; // Error
  messageParameters?: string; // Map used to create UI specific error message from the errorCode
  errorCode?: string;
  origin?: string;
  stackTrace?: string; // Possible stack trace from the backend
  description?: string; // html format, possibly with links for docs and actionable,
}

export default class HueError extends Error {
  messageParameters?: string;
  errorCode?: string;
  origin?: string;
  description?: string;
  stackTrace?: string;
  cause?: Error;

  constructor(message: string, options?: Omit<HueErrorProperties, 'message'> & { cause?: Error }) {
    super(message);
    // Standard Error properties
    this.name = this.constructor.name;
    this.cause = options?.cause;

    // Custom API Error properties
    this.messageParameters = options?.messageParameters;
    this.errorCode = options?.errorCode;
    this.origin = options?.origin;
    this.stackTrace = options?.stackTrace;
    this.description = options?.description;
  }
}
