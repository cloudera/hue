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
  <div class="dag-swimlane-event-bar">
    <div class="event-bar" />
  </div>
</template>

<script lang="ts">
  /* eslint-disable  @typescript-eslint/no-explicit-any */
  /* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

  import { Component, Prop, Vue } from 'vue-property-decorator';

  @Component
  export default class EventBar extends Vue {
    @Prop() bar: any;
    @Prop() barIndex: any = 0;

    @Prop() process: any;
    @Prop() processor: any;

    // Watch : "process.events.@each.name", "bar.fromEvent"
    get fromEvent(): any {
      const events = this.process.events;
      const fromEventName = this.bar.fromEvent;

      return events.find(function (event: any) {
        return event.name === fromEventName;
      });
    }

    // Watch : "process.events.@each.name", "bar.toEvent"
    get toEvent(): any {
      const events = this.process.events;
      const toEventName = this.bar.toEvent;

      return events.find(function (event: any) {
        return event.name === toEventName;
      });
    }

    // Watch : "fromEvent.time", "toEvent.time", "barIndex", "processor.timeWindow"
    mounted(): void {
      const fromEventPos = this.fromEvent
        ? this.processor.timeToPositionPercent(this.fromEvent.time)
        : 0;
      const toEventPos = this.toEvent ? this.processor.timeToPositionPercent(this.toEvent.time) : 0;
      const color = this.bar.color || this.process.getBarColor(this.barIndex);

      const currentComp: HTMLElement = <HTMLElement>this.$el;
      const eventBar: HTMLElement = <HTMLElement>this.$el.querySelector('.event-bar');

      if (fromEventPos && toEventPos) {
        currentComp.style.display = 'block';
        Object.assign(eventBar.style, {
          left: fromEventPos + '%',
          right: `${100 - toEventPos}%`,
          backgroundColor: color,
          borderColor: this.process.getColor()
        });
      } else {
        currentComp.style.display = 'none';
      }
    }

    sendAction(a: string, b: string, c: any, d: any): void {
      // eslint-disable-next-line no-restricted-syntax
      console.log(a, b, c, d);
    }

    sendMouseAction(name: string, mouseEvent: MouseEvent): void {
      this.sendAction(name, 'event-bar', this.process, {
        mouseEvent: mouseEvent,
        bar: this.bar,
        fromEvent: this.fromEvent,
        toEvent: this.toEvent
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
