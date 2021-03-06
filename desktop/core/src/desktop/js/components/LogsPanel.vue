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
  <div ref="logsContainer" class="logs-panel" @scroll="onScroll">
    <span v-if="logs">{{ logs }}</span>
    <span v-else>{{ I18n('There are currently no logs available.') }}</span>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop, Watch } from 'vue-property-decorator';

  import I18n from 'utils/i18n';

  @Component({
    methods: { I18n }
  })
  export default class LogsPanel extends Vue {
    @Prop()
    logs = '';
    @Prop({ required: false })
    autoScroll = true;

    ignoreNextScrollEvent = false;
    userScrolled = false;

    onScroll(): void {
      if (!this.autoScroll) {
        return;
      }
      const containerEl = <HTMLDivElement>this.$refs.logsContainer;
      if (!this.ignoreNextScrollEvent && containerEl) {
        this.userScrolled =
          containerEl &&
          containerEl.scrollHeight - containerEl.clientHeight - containerEl.scrollTop > 10;
      }
      this.ignoreNextScrollEvent = false;
    }

    @Watch('logs', { immediate: true })
    scrollToLatest(): void {
      if (!this.autoScroll) {
        return;
      }
      const containerEl = <HTMLDivElement>this.$refs.logsContainer;
      if (
        !this.userScrolled &&
        containerEl &&
        containerEl.scrollHeight > containerEl.clientHeight
      ) {
        this.ignoreNextScrollEvent = true;
        containerEl.scrollTop = containerEl.scrollHeight - containerEl.clientHeight;
      }
    }
  }
</script>

<style lang="scss" scoped>
  .logs-panel {
    height: 100%;
    width: 100%;
    white-space: pre;
    overflow: auto;
    font-family: monospace;
    padding: 5px;
  }
</style>
