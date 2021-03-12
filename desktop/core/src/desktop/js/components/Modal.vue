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
  <transition name="hue-modal">
    <div class="hue-modal-mask">
      <div class="hue-modal-wrapper">
        <div class="hue-modal-container">
          <div class="hue-modal-header">
            <h3>{{ header }}</h3>
            <button
              class="hue-modal-close-button"
              type="button"
              aria-label="{{ I18n('Close') }}"
              @click="$emit('close')"
            >
              <span aria-hidden="true">×</span>
            </button>
          </div>
          <div class="hue-modal-body">
            <slot name="body" />
          </div>
          <div class="hue-modal-footer">
            <slot name="footer">
              <button class="hue-modal-default-button" @click="$emit('close')">CLOSE</button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import './Modal.scss';
  import I18n from 'utils/i18n';

  export default defineComponent({
    name: 'Modal',
    props: {
      header: {
        type: String,
        default: ''
      }
    },
    emits: ['close'],
    methods: { I18n }
  });
</script>
