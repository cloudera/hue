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
  <div>
    <div class="labeled-info-title">{{ I18n(label) }}</div>
    <div class="labled-info-value">
      <slot v-if="showSlot" />
      <span v-else>-</span>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, VNodeNormalizedChildren } from 'vue';
  import I18n from 'utils/i18n';

  export default defineComponent({
    props: {
      label: {
        type: String,
        required: true
      }
    },

    computed: {
      showSlot(): boolean {
        if (this.$slots.default) {
          for (const node of this.$slots.default()) {
            if (node && (node.type || this.validateTextChildren(node.children))) {
              return true;
            }
          }
        }
        return false;
      }
    },

    methods: {
      I18n,

      validateTextChildren(text: VNodeNormalizedChildren): boolean {
        if (typeof text === 'string') {
          text = text.replace(/(\r\n|\n|\r)/gm, '');
          return !!text.trim();
        }
        return false;
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../components/styles/variables.scss';

  .labeled-info-title {
    text-transform: uppercase;
    color: $fluidx-gray-500;
    font-weight: normal;
    font-size: 12px;
    margin: 0;
  }

  .labled-info-value {
    color: $fluidx-gray-700;
    margin-bottom: 5px;
  }
</style>
