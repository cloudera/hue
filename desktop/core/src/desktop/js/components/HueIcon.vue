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
  <svg class="hue-icon">
    <use :xlink:href="xlinkAttr" />
  </svg>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  export default defineComponent({
    props: {
      type: {
        type: String,
        required: true
      }
    },

    computed: {
      xlinkAttr(): string {
        return '#' + this.type;
      }
    }
  });
</script>

<style lang="scss" scoped>
  button .hue-icon {
    font-size: 16px;
  }

  .hue-icon {
    vertical-align: middle;
    display: inline-block !important; // d3 conflict
    width: 1em !important; // d3 conflict
    height: 1em !important; // d3 conflict
    fill: currentColor;
    margin-bottom: 0.2em;

    &.hue-icon-fw {
      width: 1.28571429em !important; // To match FA
    }

    &.hue-icon-bigger {
      height: 1.1em !important;
    }
  }
</style>
