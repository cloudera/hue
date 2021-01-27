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

export interface UdfArgument {
  type: string;
  multiple?: boolean;
  keywords?: string[];
  optional?: boolean;
}

export interface UdfDetails {
  returnTypes: string[];
  name: string;
  arguments: UdfArgument[][];
  altArguments?: UdfArgument[][];
  signature: string;
  draggable: string;
  description?: string;
  described?: boolean;
}

export interface UdfCategoryFunctions {
  [attr: string]: UdfDetails;
}

export interface UdfCategory {
  name: string;
  functions: UdfCategoryFunctions;
  isAnalytic?: boolean;
  isAggregate?: boolean;
}

export interface SetOptions {
  [attr: string]: SetDetails;
}

export interface SetDetails {
  default: string;
  type: string;
  description: string;
}

export interface TypeConversion {
  [attr: string]: { [attr: string]: boolean };
}

export interface SqlReferenceProvider {
  getReservedKeywords(dialect: string): Promise<Set<string>>;
  getSetOptions(dialect: string): Promise<SetOptions>;
  getUdfCategories(dialect: string): Promise<UdfCategory[]>;
  hasUdfCategories(dialect: string): boolean;
}
