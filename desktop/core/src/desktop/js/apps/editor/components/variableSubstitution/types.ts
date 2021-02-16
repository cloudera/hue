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

import DataCatalogEntry from 'catalog/DataCatalogEntry';

export interface VariableOption {
  text: string;
  value: string;
}

export interface VariableMeta {
  type: string;
  placeholder: string;
  options: VariableOption[];
}

export type VariableType = 'checkbox' | 'date' | 'datetime-local' | 'number' | 'select' | 'text';

export interface Variable {
  defaultValue?: VariableMeta | string;
  name: string;
  meta: VariableMeta;
  value: string;
  type: VariableType;
  sample: VariableOption[];
  sampleUser: VariableOption[];
  path?: string;
  step: string;
  catalogEntry?: DataCatalogEntry;
}

export type VariableIndex = { [name: string]: Variable };
