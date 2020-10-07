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
  <dropdown-panel :text="label">
    <template #contents="{ closePanel }">
      <div class="status-facet">
        <div class="status-list-entry">
          <label>
            <input v-model="allSelected" type="checkbox" />
            <span v-if="allSelected">Select none</span>
            <span v-else>Select all</span>
          </label>
        </div>
        <div class="facet-selection">
          <div v-for="status in statuses" :key="status.value" class="status-list-entry">
            <label>
              <input v-model="selectedStatuses" type="checkbox" :value="status" />
              {{ status.label }}
            </label>
          </div>
        </div>
        <div class="status-facet-actions">
          <hue-link @click="cancel(closePanel)">Cancel</hue-link>
          <hue-button
            :small="true"
            :primary="true"
            :disabled="applyDisabled"
            @click="apply(closePanel)"
          >
            Apply
          </hue-button>
        </div>
      </div>
    </template>
  </dropdown-panel>
</template>

<script lang="ts">
  import I18n from '../../../../../../desktop/core/src/desktop/js/utils/i18n';
  import DropdownPanel from '../../../../../../desktop/core/src/desktop/js/components/dropdown/DropdownPanel.vue';
  import HueButton from '../../../../../../desktop/core/src/desktop/js/components/HueButton.vue';
  import HueLink from '../../../../../../desktop/core/src/desktop/js/components/HueLink.vue';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { SearchFacet } from '../api-utils/search';

  interface Status {
    label: string;
    value: string;
  }

  @Component({
    components: { DropdownPanel, HueButton, HueLink }
  })
  export default class StatusFacet extends Vue {
    statuses: Status[] = [
      {
        label: I18n('Started'),
        value: 'STARTED'
      },
      {
        label: I18n('Running'),
        value: 'RUNNING'
      },
      {
        label: I18n('Success'),
        value: 'SUCCESS'
      },
      {
        label: I18n('Error'),
        value: 'ERROR'
      }
    ];

    selectedStatuses: Status[] = [];
    previousSelection: Status[] = [];

    mounted(): void {
      this.selectedStatuses = [...this.statuses];
      this.previousSelection = [...this.statuses];
    }

    clear(): void {
      this.selectedStatuses = [...this.statuses];
      this.$emit('facet-removed', 'status');
    }

    get allSelected(): boolean {
      return this.selectedStatuses.length === this.statuses.length;
    }

    set allSelected(val: boolean) {
      if (val) {
        this.selectedStatuses = [...this.statuses];
      } else {
        this.selectedStatuses = [];
      }
    }

    get applyDisabled(): boolean {
      return !this.selectedStatuses.length;
    }

    get label(): string {
      if (this.allSelected) {
        return `${I18n('Status')}: ${I18n('All')}`;
      }
      if (this.selectedStatuses.length === 1) {
        return `${I18n('Status')}: ${this.selectedStatuses[0].label}`;
      }
      if (this.selectedStatuses.length === 0) {
        return `${I18n('Status')}: ${I18n('None')}`;
      }
      return `${I18n('Status')}: ${I18n('Multiple')}`;
    }

    cancel(closePanel: () => void): void {
      this.selectedStatuses = [...this.previousSelection];
      closePanel();
    }

    apply(closePanel: () => void): void {
      this.previousSelection = [...this.selectedStatuses];
      if (this.allSelected) {
        this.$emit('facet-removed', 'status');
      } else {
        this.$emit('facet-changed', <SearchFacet>{
          field: 'status',
          values: this.selectedStatuses.map(status => status.value)
        });
      }

      closePanel();
    }
  }
</script>

<style lang="scss" scoped>
  @import '../../../../../../desktop/core/src/desktop/js/components/styles/colors';
  @import '../../../../../../desktop/core/src/desktop/js/components/styles/mixins';

  .status-facet {
    width: 150px;
    padding: 3px 0;

    .status-list-entry {
      width: 100%;
      padding: 3px 16px;
      margin: 6px 0;
    }

    .status-facet-actions {
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

    .facet-selection {
      border-bottom: 1px solid $hue-border-color;
      border-top: 1px solid $hue-border-color;
    }
  }
</style>
