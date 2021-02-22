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
  <div class="dag-swimlane-vertex-name">
    <span class="progress-text">
      {{ progressText }}
    </span>
    <!-- {{em-table-status-cell content=process.vertex.finalStatus}} -->
    {{ process.name }}
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';
  import Process from '../libs/Process';

  export default defineComponent({
    props: {
      process: {
        type: Object as PropType<Process>,
        required: true
      }
    },

    computed: {
      // Watch : "process.vertex.finalStatus", "process.vertex.progress"
      progressText(): string {
        if (this.process.vertex.finalStatus === 'RUNNING') {
          const progress = this.process.vertex.progress;
          if (!isNaN(progress)) {
            const percent = Math.floor(progress * 100);
            return `${percent}%`;
          }
        }
        return '';
      }
    },

    methods: {
      sendMouseAction(name: string, mouseEvent: MouseEvent): void {
        this.$emit(name, 'process-name', this.process, {
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
