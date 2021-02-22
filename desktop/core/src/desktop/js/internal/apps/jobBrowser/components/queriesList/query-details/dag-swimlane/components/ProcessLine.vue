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
  <div @mouseenter="mouseEnter" @mouseleave="mouseLeave">
    <div class="process-line" />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import Process from '../libs/Process';
  import Processor from '../libs/Processor';

  export default defineComponent({
    props: {
      process: {
        type: Object as PropType<Process>,
        required: true
      },

      processor: {
        type: Object as PropType<Processor>,
        required: true
      }
    },

    // Watch : "process.startEvent.time", "process.endEvent.time", "processor.timeWindow"
    mounted(): void {
      const startPos = this.processor.timeToPositionPercent(this.process.startTime);
      const endPos = this.processor.timeToPositionPercent(this.process.endTime);

      const processLine: HTMLElement = <HTMLElement>this.$el.querySelector('.process-line');

      if (processLine) {
        Object.assign(processLine.style, {
          left: startPos + '%',
          right: `${100 - endPos}%`,
          backgroundColor: this.process.getColor()
        });
      }
    },

    methods: {
      sendMouseAction(name: string, mouseEvent: MouseEvent): void {
        this.$emit(name, 'process-line', this.process, {
          mouseEvent: mouseEvent
        });
      },

      mouseEnter(mouseEvent: MouseEvent): void {
        this.sendMouseAction('showTooltip', mouseEvent);
      },

      mouseLeave(mouseEvent: MouseEvent): void {
        this.sendMouseAction('hideTooltip', mouseEvent);
      },

      mouseUp(mouseEvent: MouseEvent): void {
        this.sendMouseAction('click', mouseEvent);
      }
    }
  });
</script>
