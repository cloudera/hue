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
  <div class="dag-swimlane-ruler">
    <div class="ruler-line" />
    <div class="mark-container">
      <div v-for="(mark, index) in marks" :key="index" class="ruler-mark" :style="markDef.style">
        <ul class="sub-marks">
          <li />
          <li />
          <li />
          <li />
          <li />
          <li />
          <li />
          <li />
          <li />
          <li />
        </ul>
        &nbsp;{{ fmtDuration(mark.duration) }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  /* eslint-disable  @typescript-eslint/no-explicit-any */
  /* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

  import { Component, Prop, Vue } from 'vue-property-decorator';
  import { duration } from '../../../../../../../../desktop/core/src/desktop/js/components/Duration.vue';

  const DEFAULT_MARK_COUNT = 10;

  @Component({
    methods: {
      fmtDuration: val => duration(val, true)
    }
  })
  export default class Ruler extends Vue {
    @Prop() zoom: any;
    @Prop() processor: any;
    @Prop() scroll: any = 0;

    // Watch : "processor.timeWindow", "zoom"
    get markDef(): any {
      const markCount = Math.floor((DEFAULT_MARK_COUNT * this.zoom) / 100);
      const timeWindow = this.processor.timeWindow;
      const duration = moment.duration(Math.floor(timeWindow / markCount));

      let markWindow = 0;
      let styleWidth = 0;
      let markUnit = 'Milliseconds';
      let markBaseValue = 0;

      if ((markBaseValue = duration.years())) {
        markUnit = 'Years';
      } else if ((markBaseValue = duration.months())) {
        markUnit = 'Months';
      } else if ((markBaseValue = duration.days())) {
        markUnit = 'Days';
      } else if ((markBaseValue = duration.hours())) {
        markUnit = 'Hours';
      } else if ((markBaseValue = duration.minutes())) {
        markUnit = 'Minutes';
      } else if ((markBaseValue = duration.seconds())) {
        markUnit = 'Seconds';
      } else {
        markBaseValue = duration.milliseconds();
      }

      if (markBaseValue > 10) {
        markBaseValue = Math.floor(markBaseValue / 10) * 10;
      }

      markWindow = moment.duration(markBaseValue, markUnit.toLowerCase()).asMilliseconds();
      styleWidth = (markWindow / timeWindow) * 100;

      return {
        unit: markUnit,
        baseValue: markBaseValue,
        markWindow: markWindow,
        style: `width: ${styleWidth}%;`, // TODO: Check if this works
        count: Math.floor((100 / styleWidth) * 1.1)
      };
    }

    // Watch : "processor.timeWindow", "markDef"
    get marks(): any {
      const def = this.markDef;
      const markWindow = def.markWindow;
      const marks = [];

      for (let i = 0, count = def.count; i < count; i++) {
        marks.push({
          duration: Math.floor(markWindow * i)
        });
      }

      return marks;
    }
  }
</script>
