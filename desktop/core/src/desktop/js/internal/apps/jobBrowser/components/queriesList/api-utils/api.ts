/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export class ApiError extends Error {
  details: string | undefined;

  constructor(error: string | Error | ApiError) {
    let message = 'Error';
    let details: string | undefined = undefined;

    if (typeof error === 'string' || error instanceof String) {
      const firstLineEnd = error.indexOf('\n');
      if (firstLineEnd != -1) {
        message = error.substring(0, firstLineEnd);
        details = error.substring(firstLineEnd + 1);
      } else {
        message = String(error);
      }
    } else if (error instanceof ApiError) {
      message = error.message;
      details = error.details;
    } else if (error instanceof Error) {
      message = error.message;
      details = error.stack;
    }

    super(message);
    this.details = details;
  }
}
