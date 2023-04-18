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
  <div v-if="varianceTxt">
    <div class="variance-bar">
      <div class="value2-bar" :style="{ width: variancePercent + '%' }" />
    </div>
    {{ varianceTxt }}
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Row, generateValueColumnKey } from './CounterSet';

  export default defineComponent({
    props: {
      data: {
        type: Object as PropType<Row>,
        required: true
      }
    },

    data() {
      return {
        varianceTxt: '',
        variancePercent: 0
      };
    },

    watch: {
      data: function () {
        const value1 = Number(this.data[generateValueColumnKey(0)]);
        const value2 = Number(this.data[generateValueColumnKey(1)]);

        if (isNaN(value1) || isNaN(value2) || value1 <= 0 || value2 <= 0) {
          this.varianceTxt = '';
        } else {
          this.variancePercent = (value2 / (value1 + value2)) * 100;
          const variance = value1 >= value2 ? value1 / value2 : value2 / value1;
          this.varianceTxt = `${Number(variance.toFixed(2))}x`;
        }
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/variables.scss';
  @import '../../../../../../components/styles/mixins';
  .variance-bar {
    display: inline-block;

    border: 1px solid $fluidx-gray-400;
    border-radius: $hue-panel-border-radius;

    width: 150px;
    height: 10px;

    overflow: hidden;

    .value2-bar {
      background-color: $fluidx-blue-100;
      height: 10px;
      width: 50%;

      border-left: 1px solid $fluidx-gray-400;

      margin-left: auto;
      margin-right: 0;
    }
  }
</style>
