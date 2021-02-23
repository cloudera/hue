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
  <div class="dag-swimlane-process-visual">
    <div class="base-line" />
    <ProcessLine
      :process="process"
      :processor="processor"
      @showTooltip="showTooltip"
      @hideTooltip="hideTooltip"
      @click="click"
    />
    <BlockingEvent
      v-for="blocking in process.blocking"
      :key="blocking._id"
      :blocking="blocking"
      :process="process"
      :processor="processor"
      @showTooltip="showTooltip"
      @hideTooltip="hideTooltip"
      @click="click"
    />
    <EventBar
      v-for="(bar, index) in process.eventBars"
      :key="index"
      :bar="bar"
      :bar-index="index"
      :process="process"
      :processor="processor"
      @showTooltip="showTooltip"
      @hideTooltip="hideTooltip"
      @click="click"
    />
    <EventToken
      v-for="event in process.events"
      :key="event.name"
      :event="event"
      :process="process"
      :processor="processor"
      @showTooltip="showTooltip"
      @hideTooltip="hideTooltip"
      @click="click"
    />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import VertexProcess, { ProcessEvent } from '../libs/VertexProcess';
  import Processor from '../libs/Processor';

  import ProcessLine from './ProcessLine.vue';
  import BlockingEvent from './BlockingEvent.vue';
  import EventBar from './EventBar.vue';
  import EventToken from './EventToken.vue';

  const BUBBLE_DIA = 10; // Same as that in css

  export default defineComponent({
    components: {
      ProcessLine,
      BlockingEvent,
      EventBar,
      EventToken
    },

    props: {
      process: {
        type: Object as PropType<VertexProcess>,
        required: true
      },

      processor: {
        type: Object as PropType<Processor>,
        required: true
      }
    },

    methods: {
      sendMouseAction(name: string, type: string, process: Process, options: unknown): void {
        this.$emit(name, type, process, options);
      },

      showTooltip(
        type: string,
        process: Process,
        options: { mouseEvent: MouseEvent; events: ProcessEvent[] }
      ): void {
        if (type === 'event') {
          const clientX = options.mouseEvent.clientX;
          const events = process.events;
          const eventsUnderMouse: ProcessEvent[] = [];

          const eventElements: NodeListOf<HTMLElement> = this.$el.querySelectorAll(
            '.dag-swimlane-event'
          );

          eventElements.forEach((element: HTMLElement, index: number) => {
            const offsetLeft = element.getBoundingClientRect().left;
            if (clientX >= offsetLeft - BUBBLE_DIA && clientX <= offsetLeft + BUBBLE_DIA) {
              eventsUnderMouse.push(events[index]);
            }
          });

          if (events.length) {
            eventsUnderMouse.sort(function (eventA, eventB) {
              return eventA.time - eventB.time;
            });
            options.events = eventsUnderMouse;
          }
        }

        this.sendMouseAction('showTooltip', type, process, options);
      },

      hideTooltip(type: string, process: Process, options: unknown): void {
        this.sendMouseAction('hideTooltip', type, process, options);
      },

      click(type: string, process: Process, options: unknown): void {
        this.sendMouseAction('click', type, process, options);
      }
    }
  });
</script>
