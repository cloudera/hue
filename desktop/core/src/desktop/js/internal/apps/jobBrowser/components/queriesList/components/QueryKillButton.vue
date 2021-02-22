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
  <hue-button v-if="info" :disabled="info.disable" @click="killQueries">
    <em v-if="info.icon" :class="`fa ${info.icon}`" />
    {{ info.msg }} {{ info.disable }}
  </hue-button>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';
  import I18n from 'utils/i18n';

  import { Query } from '../index';
  import { isRunning, kill, waitIf } from '../api-utils/query';
  import HueButton from 'components/HueButton.vue';

  enum ButtonState {
    NONE = 0,
    KILL,
    KILLING,
    KILLED,
    ERROR,
    UNKNOWN
  }

  export default defineComponent({
    name: 'QueryKillButton',
    components: {
      HueButton
    },
    props: {
      queries: {
        type: Array as PropType<Query[]>,
        required: true
      }
    },
    emits: ['killed'],
    data() {
      return {
        buttonState: ButtonState.NONE
      };
    },
    computed: {
      info(): { msg: string; icon: string; disable: boolean } | null {
        let msg = '';
        let icon = '';
        let disable = true;

        const hasRunningQuery =
          this.queries && this.queries.some((query: Query) => isRunning(query));
        const displayState = hasRunningQuery
          ? this.buttonState || ButtonState.KILL
          : ButtonState.NONE;

        switch (displayState) {
          case ButtonState.NONE:
            msg = 'Kill';
            break;
          case ButtonState.KILL:
            msg = 'Kill';
            disable = false;
            break;
          case ButtonState.KILLING:
            msg = 'Killing...';
            icon = 'fa-circle-o-notch fa-spin';
            break;
          case ButtonState.KILLED:
            msg = 'Killed';
            break;
          case ButtonState.ERROR:
            msg = 'Error!';
            icon = 'fa-exclamation-triangle';
            break;
          case ButtonState.UNKNOWN:
            msg = 'Unknown!';
            icon = 'fa-exclamation-triangle';
            break;
          default:
            return null;
        }
        return {
          msg: I18n(msg),
          icon,
          disable
        };
      }
    },
    methods: {
      async waitToKillAll(runingQueries: Query[]): Promise<boolean> {
        let killedAll = true;
        for (const query of runingQueries) {
          if (await waitIf(query, isRunning)) {
            killedAll = false;
            break;
          }
        }
        return killedAll;
      },
      async killQueries(): Promise<void> {
        this.buttonState = ButtonState.KILLING;
        const runingQueries: Query[] = this.queries.filter((query: Query) => isRunning(query));

        try {
          await kill(runingQueries);

          const killedAll = await this.waitToKillAll(runingQueries);
          if (killedAll) {
            this.buttonState = ButtonState.NONE;
            this.$emit('killed');
          } else {
            this.buttonState = ButtonState.UNKNOWN;
          }
        } catch (e) {
          this.buttonState = ButtonState.ERROR;
        }
      }
    }
  });
</script>
