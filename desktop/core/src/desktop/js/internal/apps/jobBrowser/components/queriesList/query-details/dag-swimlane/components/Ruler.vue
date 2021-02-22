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
  import { defineComponent, PropType } from 'vue';

  import { duration } from '../../../../../../../../components/Duration.vue';
  import Processor from '../libs/Processor';

  const DEFAULT_MARK_COUNT = 10;

  interface Mark {
    duration: number;
  }

  export default defineComponent({
    props: {
      zoom: {
        type: Number,
        default: 1
      },
      scroll: {
        type: Number,
        default: 0
      },

      processor: {
        type: Object as PropType<Processor>,
        required: true
      }
    },

    computed: {
      // Watch : "processor.timeWindow", "zoom"
      markDef() {
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
      },

      // Watch : "processor.timeWindow", "markDef"
      marks(): Mark[] {
        const def = this.markDef;
        const markWindow = def.markWindow;
        const marks: Mark[] = [];

        for (let i = 0, count = def.count; i < count; i++) {
          marks.push({
            duration: Math.floor(markWindow * i)
          });
        }

        return marks;
      }
    },

    methods: {
      fmtDuration: (val: number) => duration(val, true)
    }
  });
</script>
