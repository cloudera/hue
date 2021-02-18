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
  <div class="sidebar-drawer" role="dialog" :class="{ open: show }" :aria-hidden="!show">
    <slot v-if="show" />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import { defer } from 'utils/hueUtils';

  export default defineComponent({
    provide(): {
      hideDrawer: () => void;
    } {
      return {
        hideDrawer: (): void => {
          this.$emit('close');
        }
      };
    },

    props: {
      show: Boolean
    },

    emits: ['close'],

    data(): {
      subTracker: SubscriptionTracker;
      deferredShow: boolean;
    } {
      return {
        subTracker: new SubscriptionTracker(),
        deferredShow: false
      };
    },

    watch: {
      show(newValue: boolean): void {
        // deferredShow is used to prevent closing it immediately after the document click event triggered by opening
        defer(() => {
          this.deferredShow = newValue;
        });
      }
    },

    mounted(): void {
      this.subTracker.addEventListener(document, 'click', (event: MouseEvent) => {
        if (
          this.deferredShow &&
          document.contains(<Node>event.target) &&
          !this.$el.contains(<Node>event.target)
        ) {
          this.$emit('close');
        }
      });
    }
  });
</script>
