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
  <dropdown-panel :text="label" :disabled="disabled">
    <template #contents="{ closePanel }">
      <div class="facet-selector">
        <div v-if="facet.values.length > 1" class="facet-select-all">
          <div class="facet-list-entry">
            <label>
              <input v-model="allSelected" type="checkbox" />
              <span v-if="allSelected">{{ I18n('Select None') }}</span>
              <span v-else>{{ I18n('Select All') }}</span>
            </label>
          </div>
        </div>
        <div class="facet-selection">
          <div v-for="facetValue in facet.values" :key="facetValue.key" class="facet-list-entry">
            <label>
              <input v-model="selectedValues" type="checkbox" :value="facetValue.key" />
              {{ valueLabels[facetValue.key] || facetValue.key }}
              <span v-if="facetValue.value">({{ facetValue.value }})</span>
            </label>
          </div>
        </div>
        <div class="facet-selector-actions">
          <hue-link @click="cancel(closePanel)">{{ I18n('Cancel') }}</hue-link>
          <hue-button
            :small="true"
            :primary="true"
            :disabled="applyDisabled"
            @click="apply(closePanel)"
          >
            {{ I18n('Apply') }}
          </hue-button>
        </div>
      </div>
    </template>
  </dropdown-panel>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import I18n from '../utils/i18n';
  import DropdownPanel from './dropdown/DropdownPanel.vue';
  import HueButton from './HueButton.vue';
  import HueLink from './HueLink.vue';
  import { Facet, SearchFacet, FacetValueLabels } from './FacetSelector';

  export default defineComponent({
    components: {
      DropdownPanel,
      HueButton,
      HueLink
    },

    props: {
      valueLabels: {
        type: Object as PropType<FacetValueLabels>,
        required: false,
        default: () => ({})
      },
      fieldLabel: {
        type: Object as PropType<string | null>,
        required: false,
        default: null
      },
      facet: {
        type: Object as PropType<Facet>,
        required: true
      },
      disabled: {
        type: Boolean,
        required: false,
        default: false
      },
      filterEnabled: {
        type: Boolean,
        required: false,
        default: false
      }
    },

    emits: ['facet-removed', 'facet-changed'],

    data(): {
      selectedValues: string[];
      previousSelection: string[];

      lastKnownValues?: string[];
    } {
      return {
        selectedValues: [],
        previousSelection: []
      };
    },

    computed: {
      allSelected: {
        get(): boolean {
          return this.selectedValues.length === this.facet.values.length;
        },
        set(val: boolean) {
          if (val) {
            this.selectedValues = this.facet.values.map(val => val.key);
          } else {
            this.selectedValues = [];
          }
        }
      },

      applyDisabled(): boolean {
        return !this.selectedValues.length;
      },

      label(): string {
        if (this.allSelected) {
          return `${this.fieldLabel || this.facet.facetField}: ${I18n('All')}`;
        }
        if (this.selectedValues.length === 1) {
          return `${this.fieldLabel || this.facet.facetField}: ${
            this.valueLabels[this.selectedValues[0]] || this.selectedValues[0]
          }`;
        }
        if (this.selectedValues.length === 0) {
          return `${this.fieldLabel || this.facet.facetField}: ${I18n('None')}`;
        }
        return `${this.fieldLabel || this.facet.facetField}: ${I18n('Multiple')}`;
      }
    },

    created() {
      this.$watch(
        () => this.facet.values,
        (): void => {
          const newValues = this.facet.values.map(val => val.key);
          if (!this.lastKnownValues) {
            // Select all initially
            this.selectedValues = newValues;
            this.previousSelection = newValues;
          } else {
            // Keep previous selection on change
            const selected = new Set(this.selectedValues);

            // Select any new values that might have appeared
            const oldValues = new Set(this.lastKnownValues);

            this.selectedValues = newValues.filter(
              newValue => selected.has(newValue) || !oldValues.has(newValue)
            );
          }
          this.lastKnownValues = newValues;
        }
      );
    },

    methods: {
      I18n,
      clear(): void {
        this.selectedValues = this.facet.values.map(val => val.key);
        this.$emit('facet-removed', this.facet.facetField);
      },

      cancel(closePanel: () => void): void {
        this.selectedValues = [...this.previousSelection];
        closePanel();
      },

      apply(closePanel: () => void): void {
        this.previousSelection = [...this.selectedValues];
        if (this.allSelected) {
          this.$emit('facet-removed', this.facet.facetField);
        } else {
          this.$emit('facet-changed', <SearchFacet>{
            field: this.facet.facetField,
            values: this.selectedValues
          });
        }
        closePanel();
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import './styles/colors';
  @import './styles/mixins';

  .facet-selector {
    width: 150px;
    padding: 3px 0;

    .facet-list-entry {
      width: 100%;
      padding: 3px 16px;
      margin: 6px 0;
    }

    .facet-selector-actions {
      line-height: 24px;
      padding: 5px 10px;
      margin-top: 3px;

      a {
        font-size: 12px;
      }

      button {
        float: right;
      }
    }

    /deep/ label {
      margin: 0;
    }

    /deep/ input {
      margin: 0 10px 0 0;
    }

    .facet-select-all {
      border-bottom: 1px solid $hue-border-color;
    }

    .facet-selection {
      border-bottom: 1px solid $hue-border-color;
      overflow-x: hidden;
      overflow-y: auto;
      max-height: 350px;
    }
  }
</style>
