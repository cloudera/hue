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
  <div class="visual-explain-container">
    <div class="visual-explain-header">
      <div v-if="explainRendered" class="button-container">
        <button class="btn btn-default" title="Full screen" @click="toggleFullscreen">
          <em class="fa fa-expand" />
        </button>
        <em class="fa fa-ellipsis-v" />
        <button
          class="download-button btn btn-default"
          title="Download explain JSON"
          @click="downloadExplain"
        >
          <em class="fa fa-download" aria-hidden="true" />
        </button>
      </div>
      <h2 v-else>Reder failed!</h2>
    </div>

    <div v-if="isQueryRunning">
      <div style="running-anim">
        <em class="fa fa-spinner fa-spin fa-2" />
      </div>
    </div>
    <div v-else class="explain-container" />

    <div v-if="explainDetailData" class="visual-explain-detail-container">
      <div class="visual-explain-detail">
        <div class="close" @click="closePopup">
          <em class="fa fa-close" />
        </div>
        <div class="col-md-12 details-container">
          <div v-if="vectorizedInfo" class="vector-info">{{ vectorizedInfo }}</div>
          <pre class="prettyprint">{{ explainDetailData }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  /* eslint-disable  @typescript-eslint/no-explicit-any */
  /* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

  import { Component, Prop, Vue } from 'vue-property-decorator';
  import { Query } from '../..';
  import { toggleFullScreen } from '../../../../../../../desktop/core/src/desktop/js/utils/hueUtils.js';

  import { saveAs } from 'file-saver';

  import explain from './libs';

  import './visual-explain.scss';

  @Component
  export default class VisualExplain extends Vue {
    @Prop({ required: true }) query!: Query;

    explainPlan: any;

    explainDetailData = '';
    vectorizedInfo = '';

    explainRendered: any = false;

    created(): void {
      if (this.query && this.query.details) {
        this.explainPlan = this.query.details.explainPlan;
      }
    }

    get isQueryRunning(): boolean {
      return this.query && this.query.status.toLowerCase() == 'running';
    }

    mounted(): void {
      const onRequestDetail = (data: any, vectorized: any) => {
        this.explainDetailData = JSON.stringify(data, null, '  ');
        this.vectorizedInfo = vectorized['Execution mode:'];
      };

      setTimeout(() => {
        const container: HTMLElement | null = this.$el.querySelector('.explain-container');
        if (container) {
          explain(this.explainPlan, container, onRequestDetail, this.query.details);
          this.explainRendered = true;
        }
      }, 200);
    }

    toggleFullscreen(): void {
      toggleFullScreen(this.$el);
    }

    downloadExplain(): void {
      const explainData = Object.assign({}, this.explainPlan);

      if (explainData.CBOPlan) {
        explainData.CBOPlan = JSON.parse(explainData.CBOPlan);
      }
      const file = new Blob([JSON.stringify(explainData, null, 2)], {
        type: 'text/plain;charset=utf-8'
      });
      saveAs(file, this.query.queryId + '_explain.json');
    }

    closePopup(event: MouseEvent): void {
      this.explainDetailData = '';
      this.vectorizedInfo = '';
      event.preventDefault();
    }
  }
</script>

<style lang="scss" scoped></style>
