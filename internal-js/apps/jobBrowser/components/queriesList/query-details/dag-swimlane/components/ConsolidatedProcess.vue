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
  <div :class="'dag-swimlane-consolidated-process' + focused ? 'focused' : ''">&nbsp;</div>
</template>

<script lang="ts">
  import { Component, Prop, Vue } from 'vue-property-decorator';

  @Component
  export default class ConsolidatedProcess extends Vue {
    @Prop() process: any;
    @Prop() processor: any;
    @Prop() focusedProcess: any;

    // Watch : "process", "focusedProcess"
    get focused(): boolean {
      return this.process === this.focusedProcess;
    }

    // Watch : "process.consolidateStartTime", "processor.timeWindow"
    get fromPos(): number {
      const time = this.process.consolidateStartTime;
      if (time) {
        return this.processor.timeToPositionPercent(time);
      }
      return 0;
    }

    // Watch : "process.consolidateEndTime", "processor.timeWindow"
    get toPos(): number {
      const time = this.process.consolidateEndTime;
      if (time) {
        return this.processor.timeToPositionPercent(time);
      }
      return 0;
    }

    // Watch : "fromPos", "toPos"
    mounted(): void {
      const currentComp: HTMLElement = <HTMLElement>this.$el;

      const fromPos = this.fromPos;
      const toPos = this.toPos;

      if (fromPos && toPos) {
        currentComp.style.visibility = 'visible';
        Object.assign(currentComp.style, {
          visibility: 'visible',
          left: `${fromPos}%`,
          right: `${100 - toPos}%`,
          backgroundVolor: this.process.getConsolidateColor(),
          zIndex: Math.floor(toPos - fromPos)
        });
      } else {
        currentComp.style.visibility = 'hidden';
      }
    }

    sendAction(a: string, b: string, c: any, d: any): void {
      // eslint-disable-next-line no-restricted-syntax
      console.log(a, b, c, d);
    }
    sendMouseAction(name: string, mouseEvent: MouseEvent): void {
      const fromPos = this.fromPos || 0;
      const toPos = this.toPos || 0;

      this.sendAction(name, 'consolidated-process', this.process, {
        mouseEvent: mouseEvent,
        contribution: Math.floor(toPos - fromPos)
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
