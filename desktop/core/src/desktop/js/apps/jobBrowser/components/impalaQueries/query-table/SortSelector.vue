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
  <dropdown-panel :text="label" :close-on-click="false">
    <template #default="slotProps">
      <div class="sort-selector">
        <div class="sort-selection">
          <div v-for="column in sortableColumns" :key="column.key" class="sort-list-entry">
            <label>
              <input
                name="sort-column"
                type="radio"
                :checked="column.key === currentSort.column"
                @change="setColumn(column)"
              />
              {{ column.label }}
            </label>
          </div>
        </div>

        <label class="order-selector">
          <input
            type="checkbox"
            :checked="currentSort.order === 'ASC'"
            @change="setOrder($event.target.checked)"
          />
          Ascending
        </label>

        <div class="sort-selector-actions">
          <hue-link @click="cancel(slotProps.closePanel)">{{ I18n('Cancel') }}</hue-link>
          <hue-button
            :small="true"
            :primary="true"
            :disabled="applyDisabled"
            @click="apply(slotProps.closePanel)"
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

  import I18n from 'utils/i18n';
  import DropdownPanel from 'components/dropdown/DropdownPanel.vue';
  import HueButton from 'components/HueButton.vue';
  import HueLink from 'components/HueLink.vue';
  import { SortInfo } from '../ImpalaQueries.vue';
  import { Column } from 'components/HueTable';
  import { ImpalaQuery } from '../index';

  const SORTABLE_COLUMNS = new Set<keyof ImpalaQuery>([
    'startTime',
    'endTime',
    'duration',
    'cpuTime',
    'rowsProduced',
    'peakMemory',
    'hdfsBytesRead'
  ]);

  export default defineComponent({
    name: 'SortSelector',
    components: {
      DropdownPanel,
      HueButton,
      HueLink
    },

    props: {
      sort: {
        type: Object as PropType<SortInfo>,
        required: true
      },
      columns: {
        type: Object as PropType<Column<ImpalaQuery>[]>,
        required: true
      }
    },

    emits: ['sort-changed'],

    data(): {
      sortableColumns: Column<ImpalaQuery>[];
      currentSort: SortInfo;
    } {
      return {
        sortableColumns: this.columns.filter(column => SORTABLE_COLUMNS.has(String(column.key))),
        currentSort: this.sort
      };
    },

    computed: {
      applyDisabled(): boolean {
        return this.currentSort === this.sort;
      },

      label(): string {
        const column = this.columns.find(col => col.key === this.sort.column);
        return column ? `${column.label}: ${I18n(this.sort.order === 'ASC' ? 'Asc' : 'Desc')}` : '';
      }
    },

    watch: {
      sort: function (sort: SortInfo): void {
        this.currentSort = sort;
      }
    },

    methods: {
      I18n,

      setColumn(column: Column<ImpalaQuery>): void {
        this.currentSort = { ...this.currentSort, column: String(column.key) };
      },

      setOrder(asc: boolean): void {
        this.currentSort = { ...this.currentSort, order: asc ? 'ASC' : 'DESC' };
      },

      cancel(closePanel: () => void): void {
        closePanel();
      },

      apply(closePanel: () => void): void {
        this.$emit('sort-changed', this.currentSort);
        closePanel();
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import 'components/styles/variables';
  @import 'components/styles/mixins';

  .sort-selector {
    width: 170px;
    padding: 3px 0;

    .sort-list-entry {
      width: 100%;
      padding: 3px 16px;
      margin: 6px 0;
    }

    .sort-selector-actions {
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

    ::v-deep(label) {
      margin: 0;
    }

    ::v-deep(input) {
      margin: 0 10px 0 0;
    }

    .sort-selection {
      border-bottom: 1px dotted $hue-border-color;
      overflow-x: hidden;
      overflow-y: auto;
      max-height: 350px;
    }

    .order-selector {
      padding: 5px 16px;
      border-bottom: 1px solid $hue-border-color;
    }
  }
</style>
