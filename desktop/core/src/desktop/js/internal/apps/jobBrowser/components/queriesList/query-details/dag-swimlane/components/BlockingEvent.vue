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
  <div class="dag-swimlane-blocking-event" @mouseenter="mouseEnter" @mouseleave="mouseLeave">
    <div class="event-line" />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import VertexProcess, { ProcessEvent } from '../libs/VertexProcess';
  import Processor from '../libs/Processor';

  export default defineComponent({
    props: {
      process: {
        type: Object as PropType<VertexProcess>,
        required: true
      },
      blocking: {
        type: Object as PropType<VertexProcess>,
        required: true
      },

      processor: {
        type: Object as PropType<Processor>,
        required: true
      }
    },

    computed: {
      blockingEvent(): ProcessEvent | undefined {
        const events = this.process.events;
        const blockingEventName = this.process.blockingEventName;

        return events.find((event: ProcessEvent) => event.name === blockingEventName);
      }
    },

    // Watch: "blockingEvent.time", "processor.timeWindow"
    mounted(): void {
      const blockTime: number = this.blockingEvent ? this.blockingEvent.time : 0;
      let blockerEventHeight: number;

      if (blockTime && this.blocking.endEvent && this.blocking.endEvent.time >= blockTime) {
        blockerEventHeight = (this.blocking.index - this.process.index) * 30;

        const currentComp: HTMLElement = <HTMLElement>this.$el;
        const eventLine: HTMLElement = <HTMLElement>this.$el.querySelector('.event-line');

        currentComp.style.left = this.processor.timeToPositionPercent(blockTime) + '%';
        eventLine.style.height = `${blockerEventHeight}px`;
        eventLine.style.borderColor = this.process.getColor();
      }
    },

    methods: {
      sendMouseAction(name: string, mouseEvent: MouseEvent): void {
        this.$emit(name, 'blocking-event', this.process, {
          mouseEvent: mouseEvent,
          blocking: this.blocking,
          blockingEvent: this.blockingEvent
        });
      },

      mouseEnter(mouseEvent: MouseEvent): void {
        this.sendMouseAction('showTooltip', mouseEvent);
      },

      mouseLeave(mouseEvent: MouseEvent): void {
        this.sendMouseAction('hideTooltip', mouseEvent);
      }
    }
  });
</script>
