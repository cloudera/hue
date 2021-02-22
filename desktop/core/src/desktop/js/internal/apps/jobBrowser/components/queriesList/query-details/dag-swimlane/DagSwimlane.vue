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
      <ToolTip :contents="tooltipContents" />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';
  import { Dag, KeyHash } from '../../index';

  import ToolTip from './components/ToolTip.vue';
  import ProcessName from './components/ProcessName.vue';
  import ProcessVisual from './components/ProcessVisual.vue';
  import ConsolidatedProcess from './components/ConsolidatedProcess.vue';
  import Ruler from './components/Ruler.vue';
  import { createProcesses } from './libs/VertexProcess';

  import Processor from './libs/Processor';
  import Process, { TooltipContent } from './libs/Process';

  import './dag-swimlane.scss';

  // TODO: Use dag-swimlane-vertex-name.scss

  export default defineComponent({
    components: {
      ToolTip,
      ProcessName,
      ProcessVisual,
      ConsolidatedProcess,
      Ruler
    },

    props: {
      dag: {
        type: Object as PropType<Dag>,
        required: true
      },
      consolidate: {
        type: Boolean,
        default: true
      }
    },

    setup(): {
      processor: Processor;
      focusedProcess?: Process;
    } {
      return {
        processor: new Processor()
      };
    },

    data(): {
      processes: Process[];
      tooltipContents: TooltipContent[] | null;

      errMessage: string;

      scroll: number;
      zoom: number;
    } {
      const processes: Process[] = [];

      return {
        processes,

        tooltipContents: null,

        errMessage: '',

        scroll: 0,
        zoom: 100
      };
    },

    computed: {
      // Watch - "processes.@each.blockers"
      normalizedProcesses(): Process[] {
        const processes = this.processes;
        let normalizedProcesses: Process[];
        const idHash: KeyHash<number> = {};
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
              blockers.forEach((blocker: Process) => {
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
    },

    mounted(): void {
      try {
        this.processorSetup();
      } catch (e) {
        this.errMessage = 'Invalid data!';
      }
    },

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

    unmounted() {
      // Release listeners
    },

    methods: {
      // Watch : "processes.@each.startEvent"
      startTime(processes: Process[]): number {
        if (processes.length) {
          let startTime = processes[0].startTime;
          processes.forEach(process => {
            const time = process.startTime;
            if (startTime > time) {
              startTime = time;
            }
          });
          return startTime;
        }
        return 0;
      },

      // Watch - "processes.@each.endEvent"
      endTime(processes: Process[]): number {
        if (processes.length) {
          let endTime = processes[0].endTime;
          processes.forEach(process => {
            const time = process.endTime;
            if (endTime < time) {
              endTime = time;
            }
          });
          return endTime;
        }
        return 0;
      },

      // Watch - "startTime", "endTime", "processes.length"
      // On - Init
      processorSetup(): void {
        const processes = createProcesses(this.dag);

        this.processes = processes;
        this.processor.startTime = this.startTime(processes);
        this.processor.endTime = this.endTime(processes);
        this.processor.processCount = this.processes.length;
      },

      showTooltip(type: string, process: Process, options: unknown): void {
        this.tooltipContents = process.getTooltipContents(type, options);
        this.focusedProcess = process;
      },

      hideTooltip(): void {
        this.tooltipContents = null;
        this.focusedProcess = undefined;
      },

      click(): void {
        // Received params - type: string, process: Process, options: unknown
      }
    }
  });
</script>
