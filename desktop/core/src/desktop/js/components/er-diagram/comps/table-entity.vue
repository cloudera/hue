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
  <div :class="`table-entity ${entity.cssClassName || ''}`">
    <div :title="entity.database" class="db-name">
      {{ entity.database }}
    </div>
    <div :title="entity.name" class="table-name">
      <span @click="$emit('click', entity)">
        {{ entity.name }}
      </span>
    </div>
    <div class="columns-container">
      <div
        v-for="column in entity.columns.slice(0, maxCols)"
        :key="column.id"
        :data-entity-id="column.id"
        :title="column.name"
        :class="`column-entity ${column.cssClassName || ''}`"
        @click="$emit('click', column)"
      >
        <div class="left-point" />
        <div class="right-point" />
        {{ column.name }}
      </div>
      <div
        v-if="entity.columns.length > maxCols"
        :data-entity-id="
          entity.columns
            .slice(maxCols)
            .map(column => column.id)
            .join(' ')
        "
        class="grouped-columns"
        @click.stop="expandColumns()"
      >
        <div class="left-point" />
        <div class="right-point" />
        +{{ entity.columns.length - maxCols }} columns
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Table } from '../lib/entities';

  export default defineComponent({
    props: {
      entity: {
        type: Object as PropType<Table>,
        required: true
      },
      maxColumns: {
        type: Number,
        default: 10
      }
    },

    emits: ['click', 'updated'],

    data(): {
      maxCols: number;
    } {
      return {
        maxCols: 0
      };
    },

    created(): void {
      this.maxCols = this.maxColumns;
    },

    updated(): void {
      this.$emit('updated');
    },

    methods: {
      expandColumns(): void {
        this.maxCols = Number.MAX_SAFE_INTEGER;
      }
    }
  });
</script>

<style lang="scss">
  @import './table-entity.scss';
</style>
