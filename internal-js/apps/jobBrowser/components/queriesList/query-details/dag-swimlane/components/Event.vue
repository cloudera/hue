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
  <div class="dag-swimlane-event">
    <div class="event-line" />
    <div class="event-bubble" />
  </div>
</template>

<script lang="ts">
  /* eslint-disable  @typescript-eslint/no-explicit-any */
  /* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

  import { Component, Prop, Vue } from 'vue-property-decorator';

  @Component
  export default class Event extends Vue {
    @Prop() process: any;
    @Prop() event: any;

    @Prop() processor: any;

    // Watch : "event.time", "processor.timeWindow"
    mounted(): void {
      const color = this.process.getColor();

      const currentComp: HTMLElement = <HTMLElement>this.$el;
      const eventLine: HTMLElement = <HTMLElement>this.$el.querySelector('.event-line');
      const eventBubble: HTMLElement = <HTMLElement>this.$el.querySelector('.event-bubble');

      eventLine.style.borderColor = color;
      eventBubble.style.borderColor = color;

      currentComp.style.left = this.processor.timeToPositionPercent(this.event.time) + '%';
    }

    sendAction(a: string, b: string, c: any, d: any): void {
      // eslint-disable-next-line no-restricted-syntax
      console.log(a, b, c, d);
    }
    sendMouseAction(name: string, mouseEvent: MouseEvent): void {
      this.sendAction(name, 'event', this.process, {
        mouseEvent: mouseEvent,
        events: [this.event]
      });
    }

    mouseEnter(mouseEvent: MouseEvent): void {
      this.sendMouseAction('showTooltip', mouseEvent);
    }

    mouseLeave(mouseEvent: MouseEvent): void {
      this.sendMouseAction('hideTooltip', mouseEvent);
    }

    mouseUp(mouseEvent: MouseEvent): void {
      this.sendMouseAction('click', mouseEvent);
    }
  }
</script>
