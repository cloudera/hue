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
    <div v-if="explainRendered" class="button-container">
      <button class="btn btn-default" title="Full screen" @click="toggleFullscreen">
        <em class="fa fa-expand" />
      </button>
      <button
        class="download-button btn btn-default"
        title="Download explain JSON"
        @click="downloadExplain"
      >
        <em class="fa fa-download" aria-hidden="true" />
      </button>
    </div>
    <h2 v-else class="error-title">Reder failed!</h2>

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
  import { defineComponent, PropType } from 'vue';

  import { Query, KeyHash } from '../..';
  import hueUtils from 'utils/hueUtils';

  import { saveAs } from 'file-saver';

  import explain from './libs/index';

  import './visual-explain.scss';

  const toggleFullScreen = hueUtils.toggleFullScreen;

  export default defineComponent({
    props: {
      query: {
        type: Object as PropType<Query>,
        required: true
      }
    },

    data() {
      return {
        explainPlan: this.query && this.query.details ? this.query.details.explainPlan : null,
        explainDetailData: '',
        vectorizedInfo: '',

        explainRendered: true
      };
    },

    computed: {
      isQueryRunning(): boolean {
        return this.query && this.query.status.toLowerCase() == 'running';
      }
    },

    mounted(): void {
      const onRequestDetail = (data: KeyHash<unknown>, vectorized: KeyHash<string>) => {
        this.explainDetailData = JSON.stringify(data, null, '  ');
        this.vectorizedInfo = vectorized['Execution mode:'];
      };

      setTimeout(() => {
        const container: HTMLElement | null = this.$el.querySelector('.explain-container');
        if (container) {
          this.explainRendered = explain(
            this.explainPlan,
            container,
            onRequestDetail,
            this.query.details
          );
        }
      }, 200);
    },

    methods: {
      toggleFullscreen(): void {
        toggleFullScreen(this.$el);
      },

      downloadExplain(): void {
        const explainData: KeyHash<string> = Object.assign({}, this.explainPlan);

        if (explainData.CBOPlan) {
          explainData.CBOPlan = JSON.parse(explainData.CBOPlan);
        }
        const file = new Blob([JSON.stringify(explainData, null, 2)], {
          type: 'text/plain;charset=utf-8'
        });
        saveAs(file, this.query.queryId + '_explain.json');
      },

      closePopup(event: MouseEvent): void {
        this.explainDetailData = '';
        this.vectorizedInfo = '';
        event.preventDefault();
      }
    }
  });
</script>

<style lang="scss" scoped></style>
