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
  <div class="dag-swimlane-blocking-event">
    <div class="event-line" />
  </div>
</template>

<script lang="ts">
  /* eslint-disable  @typescript-eslint/no-explicit-any */
  /* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

  import { Component, Prop, Vue } from 'vue-property-decorator';

  @Component
  export default class BlockingEvent extends Vue {
    @Prop() process: any;
    @Prop() blocking: any;

    @Prop() processor: any;

    get blockingEvent(): any {
      const events = this.process.events;
      const blockingEventName = this.process.blockingEventName;

      return events.find(function (event: any) {
        return event.name === blockingEventName;
      });
    }

    // Watch: "blockingEvent.time", "processor.timeWindow"
    mounted(): void {
      const blockTime: number = this.blockingEvent.time;
      let blockerEventHeight: number;

      if (blockTime && this.blocking.endEvent.time >= blockTime) {
        blockerEventHeight = (this.blocking.index - this.process.index) * 30;

        const currentComp: HTMLElement = <HTMLElement>this.$el;
        const eventLine: HTMLElement = <HTMLElement>this.$el.querySelector('.event-line');

        currentComp.style.left = this.processor.timeToPositionPercent(blockTime) + '%';
        eventLine.style.height = `${blockerEventHeight}px`;
        eventLine.style.borderColor = this.process.getColor();
      }
    }

    sendAction(a: string, b: string, c: any, d: any): void {
      // eslint-disable-next-line no-restricted-syntax
      console.log(a, b, c, d);
    }
    sendMouseAction(name: string, mouseEvent: MouseEvent): void {
      this.sendAction(name, 'blocking-event', this.process, {
        mouseEvent: mouseEvent,
        blocking: this.blocking,
        blockingEvent: this.blockingEvent
      });
    }

    mouseEnter(mouseEvent: MouseEvent): void {
      this.sendMouseAction('showTooltip', mouseEvent);
    }

    mouseLeave(mouseEvent: MouseEvent): void {
      this.sendMouseAction('hideTooltip', mouseEvent);
    }
  }
</script>
