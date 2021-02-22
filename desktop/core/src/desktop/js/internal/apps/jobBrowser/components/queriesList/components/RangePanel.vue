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
  <div class="row">
    <div class="col-md-4 time-range-panel">
      <div class="title">Time Range</div>
      FROM
      <div class="form-group">
        <div id="from-date" class="input-group date">
          <input type="text" class="form-control" />
          <span class="input-group-addon">
            <span class="glyphicon glyphicon-calendar" />
          </span>
        </div>
      </div>
      TO
      <div class="form-group">
        <div id="to-date" class="input-group date">
          <input type="text" class="form-control" />
          <span class="input-group-addon">
            <span class="glyphicon glyphicon-calendar" />
          </span>
        </div>
      </div>

      <div class="input-group-btn">
        <button class="btn btn-success" type="button" @click="setCustomRange">APPLY</button>
      </div>
    </div>
    <div class="col-md-8 quick-range-panel">
      <div class="title">Quick Range</div>
      <div class="row">
        <div v-for="(set, index) in rangeSets" :key="index" class="col-md-3">
          <ul>
            <li v-for="range in set" :key="range.title">
              <a href="#" @click="setRange(range)">{{ range.title }}</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { TableDefinition } from '../index';

  const BASE = {
    MINUTE: 'minute',
    DAY: 'day',
    WEEK: 'week',
    MONTH: 'month',
    YEAR: 'year',
    CUSTOM: 'custom'
  };

  interface Range {
    title: string;
    from: number;
    to: number;
    base: string;
  }

  const RANGE_SETS: Range[][] = [
    [
      { title: 'Last 7 days', from: 7, to: -1, base: BASE.DAY },
      { title: 'Last 30 days', from: 30, to: -1, base: BASE.DAY },
      { title: 'Last 60 days', from: 60, to: -1, base: BASE.DAY },
      { title: 'Last 90 days', from: 90, to: -1, base: BASE.DAY },
      { title: 'Last 6 months', from: 183, to: -1, base: BASE.DAY },
      { title: 'Last 1 year', from: 365, to: -1, base: BASE.DAY },
      { title: 'Last 2 year', from: 365 * 2, to: -1, base: BASE.DAY },
      { title: 'Last 5 year', from: 365 * 5, to: -1, base: BASE.DAY }
    ],
    [
      { title: 'Yesterday', from: 1, to: 1, base: BASE.DAY },
      { title: 'Day before yesterday', from: 2, to: 2, base: BASE.DAY },
      { title: 'This day last week', from: 7, to: 7, base: BASE.DAY },
      { title: 'Previous week', from: 1, to: 1, base: BASE.WEEK },
      { title: 'Previous month', from: 1, to: 1, base: BASE.MONTH },
      { title: 'Previous year', from: 1, to: 1, base: BASE.YEAR }
    ],
    [
      { title: 'Today', from: 0, to: 0, base: BASE.DAY },
      { title: 'Today so far', from: 0, to: -1, base: BASE.DAY },
      { title: 'This week', from: 0, to: 0, base: BASE.WEEK },
      { title: 'This week so far', from: 0, to: -1, base: BASE.WEEK },
      { title: 'This month', from: 0, to: 0, base: BASE.MONTH },
      { title: 'This year', from: 0, to: 0, base: BASE.YEAR }
    ],
    [
      { title: 'Last 5 minutes', from: 5, to: -1, base: BASE.MINUTE },
      { title: 'Last 15 minutes', from: 15, to: -1, base: BASE.MINUTE },
      { title: 'Last 30 minutes', from: 30, to: -1, base: BASE.MINUTE },
      { title: 'Last 1 hour', from: 60, to: -1, base: BASE.MINUTE },
      { title: 'Last 3 hours', from: 60 * 3, to: -1, base: BASE.MINUTE },
      { title: 'Last 6 hours', from: 60 * 6, to: -1, base: BASE.MINUTE },
      { title: 'Last 12 hours', from: 60 * 12, to: -1, base: BASE.MINUTE },
      { title: 'Last 24 hours', from: 60 * 24, to: -1, base: BASE.MINUTE }
    ]
  ];

  export default defineComponent({
    name: 'RangePanel',
    props: {
      tableDefinition: {
        type: Object as PropType<TableDefinition>,
        required: true
      }
    },
    setup() {
      return { rangeSets: RANGE_SETS };
    },
    methods: {
      setCustomRange(): void {
        // TODO: Implement
      },
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      setRange(range: Range): void {
        // TODO: Implement
      }
    }
  });
</script>
