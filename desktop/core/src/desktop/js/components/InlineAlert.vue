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
  <div :class="['inline-alert', definition.cssClass]">
    <em
      v-if="showClose"
      class="inline-alert-close fa fa-times alert-color"
      @click="$emit('close')"
    />

    <em :class="['fa alert-icon alert-color', definition.faClass]" />
    <div class="inline-alert-title">{{ definition.title }}</div>

    <span class="inline-alert-message">
      {{ message }}
    </span>

    <div v-if="showDetails">
      <a v-if="details" class="more-less-button" @click="showDetails = false">
        {{ I18n('Less details') }}
      </a>
      <pre class="inline-alert-details">
        {{ details }}
      </pre>
    </div>
    <a v-else-if="details" class="more-less-button" @click="showDetails = true">
      {{ I18n('More details') }}
    </a>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import I18n from 'utils/i18n';

  export enum AlertType {
    Success,
    Error,
    Warning,
    Info,
    Unknown
  }

  class AlertDef {
    title: string;
    faClass: string;
    cssClass: string;

    constructor(title: string, faClass: string, cssClass: string) {
      this.title = I18n(title);
      this.faClass = faClass;
      this.cssClass = cssClass;
    }
  }

  const UNKNOWN_DEF = new AlertDef('Unknown!', 'fa-question-circle', 'ea-unknown');
  const TYPE_DEFS: Map<AlertType, AlertDef> = new Map([
    [AlertType.Success, new AlertDef('Success!', 'fa-check-circle', 'ea-success')],
    [AlertType.Error, new AlertDef('Error', 'fa-exclamation-circle', 'ea-error')],
    [AlertType.Warning, new AlertDef('Warning', 'fa-exclamation-triangle', 'ea-warning')],
    [AlertType.Info, new AlertDef('Info', 'fa-info-circle', 'ea-info')],
    [AlertType.Unknown, UNKNOWN_DEF]
  ]);

  export default defineComponent({
    props: {
      type: {
        type: Number as PropType<AlertType>,
        default: AlertType.Unknown
      },

      message: {
        type: String,
        default: undefined
      },
      details: {
        type: String,
        default: undefined
      },

      showClose: Boolean
    },

    emits: ['close'],

    data(): {
      showDetails: boolean;
    } {
      return {
        showDetails: false
      };
    },

    computed: {
      definition(): AlertDef {
        return TYPE_DEFS.get(this.type) || UNKNOWN_DEF;
      }
    },

    methods: {
      I18n
    }
  });
</script>

<style lang="scss" scoped>
  @import '../components/styles/colors';
  @import '../components/styles/mixins';

  .inline-alert {
    position: relative;

    padding: 10px 10px 10px 40px;
    border-radius: $hue-panel-border-radius;

    // ea-unknown
    background-color: $fluid-gray-050;
    border: 1px solid $fluid-gray-500;
    .alert-color {
      color: $fluid-gray-500;
    }

    &.ea-success {
      background-color: $fluid-green-050;
      border: 1px solid $fluid-green-400;
      .alert-color {
        color: $fluid-green-500;
      }
    }

    &.ea-error {
      background-color: $fluid-red-050;
      border: 1px solid $fluid-red-400;
      .alert-color {
        color: $fluid-red-500;
      }
    }

    &.ea-warning {
      background-color: $fluid-orange-050;
      border: 1px solid $fluid-orange-400;
      .alert-color {
        color: $fluid-orange-500;
      }
    }

    &.ea-info {
      background-color: $fluid-blue-050;
      border: 1px solid $fluid-blue-400;
      .alert-color {
        color: $fluid-blue-500;
      }
    }

    .alert-icon {
      position: absolute;
      left: 15px;
      top: 10px;

      font-size: 20px;
    }

    .inline-alert-close {
      position: absolute;
      top: 5px;
      right: 5px;

      cursor: pointer;
    }

    .more-less-button {
      cursor: pointer;
    }

    .inline-alert-title,
    .inline-alert-message,
    .inline-alert-details {
      color: $fluid-gray-900;
    }

    .inline-alert-message {
      margin-right: 5px;
    }

    .inline-alert-title {
      font-weight: bold;
    }

    .inline-alert-details {
      margin-top: 10px;
      background-color: rgba(255, 255, 255, 0.6);
    }
  }
</style>
