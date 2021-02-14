<!--
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
-->

<template>
  <div class="variable-substitution">
    <span v-for="variable of activeVariables" :key="variable.name">
      <div class="variable-value">
        <div class="variable-label">{{ variable.name }}</div>
        <input
          v-model="variable.value"
          class="variable-input"
          :placeholder="variable.meta.placeholder"
        />
      </div>
    </span>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { cloneDeep } from 'lodash';

  import { Variable, VariableIndex, VariableOption } from './types';
  import { IdentifierLocation } from 'parse/types';
  import DataCatalogEntry, { FieldSourceMeta } from 'catalog/DataCatalogEntry';
  import { noop } from 'utils/hueUtils';

  const NAMED_OPTION_REGEX = /^(.+)\(([^)]+)\)$/;
  const LOCATION_VALUE_REGEX = /\${(\w+)=?([^{}]*)}/;

  interface KnownVariable extends Variable {
    active: boolean;
    index: number;
  }

  const parseOption = (val: string): VariableOption => {
    const namedMatch = val.match(NAMED_OPTION_REGEX);
    if (namedMatch) {
      return {
        value: namedMatch[1].trim(),
        text: namedMatch[2].trim()
      };
    }
    const trimmed = val.trim();
    return {
      value: trimmed,
      text: trimmed
    };
  };

  const updateFromDataCatalog = async (
    variable: Variable,
    entry: DataCatalogEntry
  ): Promise<void> => {
    try {
      variable.path = entry.getQualifiedPath();
      variable.catalogEntry = entry;

      const sourceMeta = <FieldSourceMeta>await entry.getSourceMeta({ silenceErrors: true });

      const colType = (sourceMeta && sourceMeta.type) || 'string';

      switch (colType) {
        case 'timestamp':
          variable.type = 'datetime-local';
          variable.step = '1';
          if (!variable.value) {
            variable.value = String(Date.now());
          }
          break;
        case 'date':
          variable.type = 'date';
          variable.step = '';
          if (!variable.value) {
            variable.value = String(Date.now());
          }
          break;
        case 'decimal':
        case 'double':
        case 'float':
          variable.type = 'number';
          variable.step = 'any';
          break;
        case 'int':
        case 'smallint':
        case 'tinyint':
        case 'bigint':
          variable.type = 'number';
          variable.step = '1';
          break;
        case 'boolean':
          variable.type = 'checkbox';
          variable.step = '';
          break;
        default:
          variable.type = 'text';
          variable.step = '';
      }
    } catch (err) {}
  };

  export default defineComponent({
    props: {
      initialVariables: {
        type: Object as PropType<{ [name: string]: Variable }>,
        required: false,
        default: {}
      },
      locations: {
        type: Object as PropType<IdentifierLocation[]>,
        required: false,
        default: undefined
      }
    },

    emits: ['variables-changed'],

    data(): {
      knownVariables: { [name: string]: KnownVariable };
    } {
      return {
        knownVariables: {}
      };
    },

    computed: {
      activeVariables(): Variable[] {
        const active = Object.values(this.knownVariables).filter(variable => variable.active);
        active.sort((a, b) => a.index - b.index);
        return active;
      }
    },

    watch: {
      activeVariables(): void {
        this.$emit(
          'variables-changed',
          this.activeVariables.reduce((result, variable) => {
            result[variable.name] = variable;
            return result;
          }, <VariableIndex>{})
        );
      },
      locations(locations?: IdentifierLocation[]): void {
        const toDeactivate = new Set<string>(Object.keys(this.knownVariables));

        if (locations) {
          locations
            .filter(location => location.type === 'variable' && location.value)
            .forEach(location => {
              const match = location.value && location.value.match(LOCATION_VALUE_REGEX);
              if (!match) {
                return;
              }

              const name = match[1];
              let variable = this.knownVariables[name];
              if (variable) {
                toDeactivate.delete(variable.name);
                if (!variable.active) {
                  variable.active = true;
                  this.$forceUpdate();
                }
              } else {
                variable = {
                  meta: { type: 'text', placeholder: '', options: [] },
                  sample: [],
                  sampleUser: [],
                  step: '',
                  type: 'text',
                  value: '',
                  name: name,
                  active: true,
                  index: Object.keys(this.knownVariables).length + 1
                };
                this.knownVariables[name] = variable;
                this.$forceUpdate();
              }

              // Case for ${name=1} or ${name=a,b,c}
              if (match[2]) {
                const optionStrings = match[2].split(',');

                // When it's just one option it's a placeholder only
                if (optionStrings.length === 1) {
                  const option = parseOption(optionStrings[0]);
                  if (variable.meta.placeholder !== option.value) {
                    variable.meta.placeholder = option.value;
                    this.$forceUpdate();
                  }
                  variable.meta.options = [];
                } else {
                  variable.type = 'select';
                  variable.meta.placeholder = '';
                  variable.meta.options = optionStrings.map(parseOption);
                }
              } else {
                if (variable.type === 'select') {
                  // Revert to last known type if options are removed
                  if (variable.catalogEntry) {
                    updateFromDataCatalog(variable, variable.catalogEntry);
                  } else {
                    variable.type = 'text';
                  }
                }
                variable.meta.placeholder = '';
                variable.meta.options = [];
              }

              if (location.colRef && location.resolveCatalogEntry) {
                location
                  .resolveCatalogEntry()
                  .then(async entry => {
                    await updateFromDataCatalog(variable, entry);
                  })
                  .catch(noop);
              }
            });
        }

        toDeactivate.forEach(name => {
          const variable = this.knownVariables[name];
          if (variable) {
            variable.active = false;
            this.$forceUpdate();
          }
        });
      }
    },

    mounted(): void {
      if (this.initialVariables) {
        Object.values(this.initialVariables).forEach((variable, index) => {
          const cloned = <KnownVariable>cloneDeep(variable);
          cloned.active = true;
          cloned.index = index;
          this.knownVariables[cloned.name] = cloned;
          this.$forceUpdate();
        });
      }
    }
  });
</script>

<style lang="scss">
  @import './VariableSubstitution.scss';
</style>
