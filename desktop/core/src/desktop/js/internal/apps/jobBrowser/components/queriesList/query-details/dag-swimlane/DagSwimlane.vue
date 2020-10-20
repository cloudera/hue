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
  <div class="dag-swimlane">
    <div v-if="errMessage">
      {{ errMessage }}
    </div>
    <div v-else>
      <div class="process-names">
        <ProcessName
          v-for="process in normalizedProcesses"
          :key="process._id"
          :process="process"
          @showTooltip="showTooltip"
          @hideTooltip="hideTooltip"
          @click="click"
        />
        <div class="consolidated-view-label">
          Consolidated
        </div>
      </div>
      <div class="process-visuals">
        <div class="zoom-panel">
          <ProcessVisual
            v-for="process in normalizedProcesses"
            :key="process._id"
            :process="process"
            :processor="processor"
            @showTooltip="showTooltip"
            @hideTooltip="hideTooltip"
            @click="click"
          />
          <div v-if="consolidate" class="consolidated-view">
            <ConsolidatedProcess
              v-for="process in normalizedProcesses"
              :key="process._id"
              :focused-process="focusedProcess"
              :process="process"
              :processor="processor"
              @showTooltip="showTooltip"
              @hideTooltip="hideTooltip"
              @click="click"
            />
          </div>
          <Ruler :scroll="scroll" :processor="processor" :zoom="zoom" />
        </div>
      </div>
      <!-- {{em-tooltip contents=tooltipContents}} -->
    </div>
  </div>
</template>

<script lang="ts">
  /* eslint-disable  @typescript-eslint/no-explicit-any */
  /* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

  import { Component, Prop, Vue } from 'vue-property-decorator';
  import { Dag } from '../../index';

  import ProcessName from './components/ProcessName.vue';
  import ProcessVisual from './components/ProcessVisual.vue';
  import ConsolidatedProcess from './components/ConsolidatedProcess.vue';
  import Ruler from './components/Ruler.vue';
  import { createProcesses } from './libs/VertexProcess';

  import Processor from './libs/Processor';
  import Process from './libs/Process';

  import './dag-swimlane.scss';

  // TODO: Refactor - This is just a direct port from Ember.js and many things can be optimised using Vue.js features
  // TODO: Use dag-swimlane-vertex-name.scss

  @Component({
    components: {
      ProcessName,
      ProcessVisual,
      ConsolidatedProcess,
      Ruler
    }
  })
  export default class DagSwimlane extends Vue {
    @Prop({ required: true }) dag!: Dag;
    @Prop({ default: true }) consolidate!: boolean;

    processes!: Process[];
    processor: Processor = new Processor();
    focusedProcess: Process | undefined;

    tooltipContents = null;

    errMessage = '';

    scroll = 0;
    zoom = 100;

    // Watch : "processes.@each.startEvent"
    startTime(processes: Process[]): number {
      if (processes.length) {
        let startTime = processes[0].startEvent.time;
        processes.forEach(process => {
          const time = process.startEvent.time;
          if (startTime > time) {
            startTime = time;
          }
        });
        return startTime;
      }
      return 0;
    }

    // Watch - "processes.@each.endEvent"
    endTime(processes: Process[]): number {
      if (processes.length) {
        let endTime = processes[0].endEvent.time;
        processes.forEach(process => {
          const time = process.endEvent.time;
          if (endTime < time) {
            endTime = time;
          }
        });
        return endTime;
      }
      return 0;
    }

    // Watch - "startTime", "endTime", "processes.length"
    // On - Init
    processorSetup(): void {
      const processes = createProcesses(this.dag);

      this.processes = processes;
      this.processor.startTime = this.startTime(processes);
      this.processor.endTime = this.endTime(processes);
      this.processor.processCount = this.processes.length;
    }

    created(): void {
      try {
        this.processorSetup();
      } catch (e) {
        this.errMessage = 'Invalid data!';
      }
    }

    // mounted(): void {
    //   this.onZoom();
    //   this.listenScroll();
    // }

    // // Watch - "zoom"
    // @Watch('zoom')
    // onZoom(): void {
    //   const zoomPanel: HTMLElement = <HTMLElement>this.$el.querySelector('.zoom-panel');
    //   zoomPanel.style.width = `${this.zoom}%`;
    // }

    // listenScroll(): void {
    //   const processVisuals: HTMLElement = <HTMLElement>this.$el.querySelector('.process-visuals');
    //   processVisuals.onscroll = () => {
    //     this.scroll = processVisuals.scrollLeft;
    //   };
    // }

    willDestroy(): void {
      // Release listeners
    }

    // Watch - "processes.@each.blockers"
    get normalizedProcesses(): any[] {
      const processes = this.processes;
      let normalizedProcesses: any[];
      const idHash: any = {};
      let containsBlockers = false;
      const processor = this.processor;

      // Validate and reset blocking
      processes.forEach(function (process) {
        if (!(process instanceof Process)) {
          console.error('em-swimlane : Unknown type, must be of type Process');
        }

        if (process.blockers.length) {
          containsBlockers = true;
        }
        process.blocking = [];
      });

      if (containsBlockers) {
        normalizedProcesses = [];

        // Recreate blocking list
        processes.forEach(process => {
          const blockers = process.blockers;
          if (blockers) {
            blockers.forEach((blocker: any) => {
              blocker.blocking.push(process);
            });
          }
        });

        // Give an array of the processes in blocking order
        processes.forEach((process: Process) => {
          if (process.blocking.length === 0) {
            // The root processes
            normalizedProcesses.push(process);
            normalizedProcesses.push.apply(normalizedProcesses, process.getAllBlockers());
          }
        });
        normalizedProcesses.reverse();
        normalizedProcesses = normalizedProcesses.filter((process: Process, index: number) => {
          // Filters out the recurring processes in the list (after graph traversal), we just
          // need the top processes
          const id = process._id;
          if (idHash[id] === undefined) {
            idHash[id] = index;
          }
          return idHash[id] === index;
        });
      } else {
        normalizedProcesses = processes;
      }

      // Set process colors & index
      normalizedProcesses.forEach(function (process, index) {
        process.index = index;
        process.color = processor.createProcessColor(index, 0);
      });

      return normalizedProcesses; // Note: Was an Ember Array
    }

    showTooltip(type: string, process: Process, options: any): void {
      this.tooltipContents = process.getTooltipContents(type, options);
      this.focusedProcess = process;
    }

    hideTooltip(): void {
      this.tooltipContents = null;
      this.focusedProcess = undefined;
    }

    sendAction(a: string, b: string, c: any, d: any): void {
      // eslint-disable-next-line no-restricted-syntax
      console.log(a, b, c, d);
    }

    click(type: string, process: Process, options: any): void {
      this.sendAction('click', type, process, options);
    }
  }
</script>
