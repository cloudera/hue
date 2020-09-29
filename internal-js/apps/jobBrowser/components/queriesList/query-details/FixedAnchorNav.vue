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
  <div class="buttons">
    <hue-button @click="showQueries">Queries</hue-button>
    <template v-if="!query.isComplete">
      <hue-button v-if="stoppingQuery">
        <i class="fa fa-spinner fa-pulse fa-fw" /> Stopping query
      </hue-button>
      <hue-button v-else @click="stopQuery">Stop</hue-button>
    </template>

    <hue-button @click="downloadLogs">Download</hue-button>
  </div>
</template>

<script lang="ts">
  import { Inject } from 'vue-property-decorator';
  import HueButton from '../../../../../../desktop/core/src/desktop/js/components/HueButton.vue';
  import Component from 'vue-class-component';
  import SingleQueryComponent from './SingleQueryComponent.vue';

  @Component({
    components: { HueButton }
  })
  export default class FixedAnchorNav extends SingleQueryComponent {
    @Inject()
    showQueries?: () => void;

    stoppingQuery = false;

    stopQuery(): void {
      this.stoppingQuery = true;
      // TODO: Implement (see fixed-anchor-nav.js)
    }

    downloadLogs(): void {
      // TODO: Implement (see fixed-anchor-nav.js)
    }
  }
</script>

<style lang="scss" scoped></style>
