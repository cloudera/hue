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

import { Cancellable } from 'api/cancellablePromise';
import { DIALECT } from 'apps/notebook2/snippet';
import DataCatalogEntry from 'catalog/dataCatalogEntry';
import ko, { PureComputed } from 'knockout';
import { Observable, ObservableArray } from 'knockout';
import { IdentifierLocation } from 'parse/types';
import { Connector } from 'types/config';
import { defer } from 'utils/hueUtils';

interface VariableMetaRaw {
  type: string;
  placeholder: string;
  options?: VariableOption[];
}

interface VariableMeta {
  type: Observable<string>;
  placeholder: Observable<string>;
  options: ObservableArray<VariableOption>;
}

const variableMetaFromJs = (variableMetaRaw: VariableMetaRaw): VariableMeta => ({
  type: ko.observable(variableMetaRaw.type),
  placeholder: ko.observable(variableMetaRaw.placeholder),
  options: ko.observableArray(variableMetaRaw.options || [])
});

const variableMetaToJs = (variableMeta: VariableMeta): VariableMetaRaw => ({
  type: variableMeta.type(),
  placeholder: variableMeta.placeholder(),
  options: variableMeta.options()
});

interface VariableRaw {
  name: string;
  defaultValue?: VariableMetaRaw | string;
  meta?: VariableMetaRaw;
  value: string;
  type: string;
  catalogEntry?: DataCatalogEntry;
  sample: VariableOption[];
  sampleUser: VariableOption[];
  path: string;
  step: string;
}

interface ExtractedVariable {
  name: string;
  meta: VariableMeta;
}

interface VariableOption {
  text: string;
  value: string;
}

class Variable {
  name: Observable<string>;
  meta: VariableMeta;
  value: Observable<string>;
  type: Observable<string>;
  sample: ObservableArray<VariableOption>;
  sampleUser: ObservableArray<VariableOption>;
  path: Observable<string>;
  step: Observable<string> = ko.observable('');
  catalogEntry?: DataCatalogEntry;

  constructor(variableRaw?: VariableRaw) {
    this.meta = variableMetaFromJs(
      (typeof variableRaw?.defaultValue === 'object' && variableRaw?.defaultValue) ||
        variableRaw?.meta || {
          type: 'text',
          placeholder: ''
        }
    );
    this.name = ko.observable(variableRaw?.name || '');
    this.value = ko.observable(variableRaw?.value || '');
    this.type = ko.observable(variableRaw?.type || '');
    this.sampleUser = ko.observableArray(variableRaw?.sampleUser || []);
    this.path = ko.observable(variableRaw?.path || '');

    this.sample = ko.observableArray(); // TODO: in raw?
    this.sampleUser = ko.observableArray(); // TODO: in raw?
  }

  toJs(): VariableRaw {
    return {
      name: this.name(),
      meta: variableMetaToJs(this.meta),
      value: this.value(),
      type: this.type(),
      sample: this.sample(),
      sampleUser: this.sampleUser(),
      path: this.path(),
      step: this.step(),
      catalogEntry: this.catalogEntry
    };
  }
}

const LOCATION_VALUE_REGEX = /\${(\w*)=?([^{}]*)}/g;

export class VariableSubstitutionHandler {
  variables: ObservableArray<Variable> = ko.observableArray();
  connector: Observable<Connector>;
  variableNames: PureComputed<ExtractedVariable[]>;
  statementRaw: Observable<string>;
  variableValues: { [key: string]: VariableRaw } = {};
  activeCancellables: Cancellable[] = [];

  constructor(
    connector: Observable<Connector>,
    statementRaw: Observable<string>,
    rawVariables?: VariableRaw[]
  ) {
    this.connector = connector;
    this.statementRaw = statementRaw;
    if (rawVariables) {
      this.variables(rawVariables.map(rawVariable => new Variable(rawVariable)));
    }

    this.variableNames = ko.pureComputed(() => this.extractVariables(this.statementRaw()));

    this.variableNames.extend({ rateLimit: 150 });

    this.variableNames.subscribe(newVal => {
      const variablesLength = this.variables().length;
      const diffLengthVariables = variablesLength - newVal.length;
      const needsMore = diffLengthVariables < 0;
      const needsLess = diffLengthVariables > 0;

      this.variableValues = {};
      this.variables().forEach(variable => {
        const name = variable.name();
        if (!this.variableValues[name]) {
          this.variableValues[name] = variable.toJs();
        }
      });

      if (needsMore) {
        for (let i = 0, length = Math.abs(diffLengthVariables); i < length; i++) {
          this.variables.push(
            new Variable({
              name: '',
              value: '',
              meta: { type: 'text', placeholder: '', options: [] },
              sample: [],
              sampleUser: [],
              type: 'text',
              step: '',
              path: ''
            })
          );
        }
      } else if (needsLess) {
        this.variables.splice(this.variables().length - diffLengthVariables, diffLengthVariables);
      }

      newVal.forEach((item, index) => {
        const variable = this.variables()[index];
        const variableValue = this.variableValues[item.name];
        variable.name(item.name);
        window.setTimeout(() => {
          variable.value(
            variableValue ? variableValue.value : (!needsMore && variable.value()) || ''
          );
        }, 0);
        variable.meta.placeholder(item.meta.placeholder());
        variable.meta.options(item.meta.options());
        variable.meta.type(item.meta.type());
        variable.sample(
          variable.meta.options()
            ? variable.meta.options().concat(variable.sampleUser())
            : variable.sampleUser()
        );
        variable.sampleUser(variableValue?.sampleUser || []);
        variable.type(variableValue?.type || 'text');
        variable.path(variableValue?.path || '');
        variable.catalogEntry = variableValue?.catalogEntry;
      });
    });
  }

  extractVariables(statement: string): ExtractedVariable[] {
    if (this.connector().dialect === DIALECT.pig) {
      return this.getPigParameters(statement);
    }

    const foundParameters: { [key: string]: VariableMeta } = {};

    let match: RegExpExecArray | null;
    let matchList: RegExpExecArray | null;

    const re = /(?:^|\W)\${(\w*)=?([^{}]*)}/g;
    const reComment = /(^\s*--.*)|(\/\*[\s\S]*?\*\/)/gm;
    const reList = /(?!\s*$)\s*(?:(?:([^,|()\\]*)\(\s*([^,|()\\]*)\)(?:\\[\S\s][^,|()\\]*)?)|([^,|\\]*(?:\\[\S\s][^,|\\]*)*))\s*(?:,|\||$)/g;

    let matchComment = reComment.exec(statement);

    while ((match = re.exec(statement))) {
      while (matchComment && match.index > matchComment.index + matchComment[0].length) {
        // Comments before our match
        matchComment = reComment.exec(statement);
      }
      const isWithinComment = matchComment && match.index >= matchComment.index;
      if (isWithinComment) {
        continue;
      }

      const name = match[1];
      if (foundParameters[name]) {
        continue; // Return the first if multiple present
      }

      // If 1 match, text value
      // If multiple matches, list value
      const value: { type: string; placeholder: string; options: VariableOption[] } = {
        type: 'text',
        placeholder: '',
        options: []
      };

      while ((matchList = reList.exec(match[2]))) {
        const option: VariableOption = {
          text: matchList[2] || matchList[3],
          value: matchList[3] || matchList[1]
        };
        option.text = option.text && option.text.trim();
        option.value =
          option.value && option.value.trim().replace(',', ',').replace('(', '(').replace(')', ')');

        if (value.placeholder || matchList[2]) {
          value.type = 'select';
          value.options.push(option);
        }
        if (!value.placeholder) {
          value.placeholder = option.value;
        }
      }
      const isPlaceholderInOptions =
        !value.options || value.options.some(current => current.value === value.placeholder);
      if (!isPlaceholderInOptions) {
        value.options.unshift({ text: value.placeholder, value: value.placeholder });
      }

      foundParameters[name] = variableMetaFromJs(value);
    }

    return Object.keys(foundParameters).map(key => ({ name: key, meta: foundParameters[key] }));
  }

  getPigParameters(statement: string): ExtractedVariable[] {
    const foundParameters: { [key: string]: string } = {};

    const variables = statement.match(/([^\\]|^)\$[^\d'"](\w*)/g);
    if (variables) {
      variables.forEach(param => {
        const p = param.substring(param.indexOf('$') + 1);
        foundParameters[p] = '';
      });
    }

    const declares = statement.match(/%declare +([^ ])+/gi);
    if (declares) {
      declares.forEach(param => {
        const match = param.match(/(\w+)/g);
        if (match && match.length >= 2) {
          delete foundParameters[match[1]];
        }
      });
    }

    const defaults = statement.match(/%default +([^;])+/gi);
    if (defaults) {
      defaults.forEach(param => {
        const line = param.match(/(\w+)/g);
        if (line && line.length >= 2) {
          const name = line[1];
          foundParameters[name] = param.substring(param.indexOf(name) + name.length + 1);
        }
      });
    }

    const macroDefines = statement.match(/define [^ ]+ *\(([^)]*)\)/gi); // no multiline
    if (macroDefines) {
      macroDefines.forEach(param => {
        const line = param.match(/(\w+)/g);
        if (line && line.length > 2) {
          line.forEach((param, index) => {
            if (index >= 2) {
              // Skips define NAME
              delete foundParameters[param];
            }
          });
        }
      });
    }

    const macroReturns = statement.match(/returns +([^{]*)/gi); // no multiline
    if (macroReturns) {
      macroReturns.forEach(param => {
        const line = param.match(/(\w+)/g);
        if (line) {
          line.forEach((param, index) => {
            if (index >= 1) {
              // Skip returns
              delete foundParameters[param];
            }
          });
        }
      });
    }
    return Object.keys(foundParameters).map(key => ({
      name: key,
      meta: variableMetaFromJs({ type: 'text', placeholder: foundParameters[key] })
    }));
  }

  cancelRunningRequests(): void {
    while (this.activeCancellables.length) {
      const cancellable = this.activeCancellables.pop();
      if (cancellable) {
        cancellable.cancel();
      }
    }
  }

  updateFromLocations(locations: IdentifierLocation[]): void {
    const oLocations: { [key: string]: IdentifierLocation } = {};

    for (const location of locations) {
      if (location.type !== 'variable' || !location.colRef || !location.value) {
        continue;
      }
      const match = LOCATION_VALUE_REGEX.exec(location.value);
      if (match) {
        const name = match[1];
        oLocations[name] = location;
      }
    }

    const updateVariableType = (variable: Variable, sourceMeta?: { type?: string }) => {
      let type;
      if (sourceMeta && sourceMeta.type) {
        type = sourceMeta.type.toLowerCase();
      } else {
        type = 'string';
      }
      const variablesValues: { type: string; step: string; value?: string } = {
        type: '',
        step: ''
      };
      const value = variable.value();
      switch (type) {
        case 'timestamp':
          variablesValues.type = 'datetime-local';
          variablesValues.step = '1';
          variablesValues.value =
            (value && moment.utc(value).format('YYYY-MM-DD HH:mm:ss.S')) ||
            moment(Date.now()).format('YYYY-MM-DD 00:00:00.0');
          break;
        case 'decimal':
        case 'double':
        case 'float':
          variablesValues.type = 'number';
          variablesValues.step = 'any';
          break;
        case 'int':
        case 'smallint':
        case 'tinyint':
        case 'bigint':
          variablesValues.type = 'number';
          variablesValues.step = '1';
          break;
        case 'date':
          variablesValues.type = 'date';
          variablesValues.step = '';
          variablesValues.value =
            (value && moment.utc(value).format('YYYY-MM-DD')) ||
            moment(Date.now()).format('YYYY-MM-DD');
          break;
        case 'boolean':
          variablesValues.type = 'checkbox';
          variablesValues.step = '';
          break;
        default:
          variablesValues.type = 'text';
          variablesValues.step = '';
      }
      if (variablesValues.value) {
        defer(() => {
          if (variablesValues.value) {
            variable.value(variablesValues.value);
          }
        });
      }
      variable.type(variablesValues.type);
      variable.step(variablesValues.step);
    };
    this.variables().forEach(variable => {
      const location = oLocations[variable.name()];
      if (location && location.resolveCatalogEntry) {
        const catalogEntryPromise = location.resolveCatalogEntry({ cancellable: true });
        this.activeCancellables.push(catalogEntryPromise);
        catalogEntryPromise.then(entry => {
          variable.path(entry.getQualifiedPath());
          variable.catalogEntry = entry;

          const sourceMetaPromise = entry.getSourceMeta({
            silenceErrors: true,
            cancellable: true
          });

          this.activeCancellables.push(sourceMetaPromise);

          sourceMetaPromise.then(sourceMeta => {
            updateVariableType(variable, sourceMeta);
          });
        });
      } else {
        updateVariableType(variable, {
          type: 'text'
        });
      }
    });
  }

  substitute(statement: string): string {
    if (!this.variables().length) {
      return statement;
    }
    const variables: { [key: string]: Variable } = {};
    this.variables().forEach(variable => {
      variables[variable.name()] = variable;
    });

    const variablesString = this.variables()
      .map(variable => variable.name())
      .join('|');

    statement = statement.replace(
      RegExp(
        '([^\\\\])?\\$' +
          (this.connector().dialect !== DIALECT.pig ? '{(' : '(') +
          variablesString +
          ')(=[^}]*)?' +
          (this.connector().dialect !== DIALECT.pig ? '}' : ''),
        'g'
      ),
      (match, p1, p2) => {
        const variable = variables[p2];
        const pad =
          variable.type() === 'datetime-local' && variable.value().length === 16 ? ':00' : ''; // Chrome drops the seconds from the timestamp when it's at 0 second.
        const value = variable.value();
        const isValuePresent = //If value is string there is a need to check whether it is empty
          typeof value === 'string' ? value : value !== undefined && value !== null;
        return (
          p1 +
          (isValuePresent ? value + pad : variable.meta.placeholder && variable.meta.placeholder())
        );
      }
    );

    return statement;
  }
}
