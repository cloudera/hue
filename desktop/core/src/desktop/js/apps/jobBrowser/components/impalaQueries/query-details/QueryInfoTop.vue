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
  <div class="hue-info-box">
    <LabeledInfo label="Query ID" class="inline-info">
      {{ query.queryId }}
      <a href="javascript:void(0);" class="fa fa-copy" @click="copyQueryId(query.queryId)" />
    </LabeledInfo>

    <LabeledInfo label="User" class="inline-info">
      {{ query.userName }}
    </LabeledInfo>

    <LabeledInfo label="Status" class="inline-info">
      <StatusIndicator :value="query.status" />
      {{ query.status }}
    </LabeledInfo>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import StatusIndicator from '../../../../../components/StatusIndicator.vue';
  import LabeledInfo from './LabeledInfo.vue';

  import { ImpalaQuery } from '..';

  export default defineComponent({
    components: {
      StatusIndicator,
      LabeledInfo
    },

    props: {
      query: {
        type: Object as PropType<ImpalaQuery>,
        required: true
      }
    },

    methods: {
      copyQueryId(queryId: string): void {
        navigator.clipboard.writeText(queryId);
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../components/styles/variables.scss';
  @import '../../../../../components/styles/mixins';

  .hue-info-box {
    padding: 10px;

    border: 1px solid $fluidx-gray-300;
    border-radius: $hue-panel-border-radius;

    @include nowrap-ellipsis;

    margin-bottom: 10px;

    .inline-info {
      display: inline-block;
      margin-right: 20px;

      vertical-align: baseline;
    }
  }
</style>
