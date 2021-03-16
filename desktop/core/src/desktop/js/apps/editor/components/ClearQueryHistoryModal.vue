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
  <Modal
    v-if="modelValue"
    :header="I18n('Confirm History Clear')"
    @close="$emit('update:model-value', false)"
  >
    <template #body>
      <p>{{ I18n('Are you sure you want to clear the query history?') }}</p>
    </template>
    <template #footer>
      <HueButton :disabled="clearingHistory" @click="$emit('update:model-value', false)">
        {{ I18n('No') }}
      </HueButton>
      <HueButton :alert="true" :disabled="clearingHistory" @click="clearHistory">
        <span v-if="!clearingHistory">{{ I18n('Yes') }}</span>
        <span v-else>{{ I18n('Clearing...') }}</span>
      </HueButton>
    </template>
  </Modal>
</template>

<script lang="ts">
  import { defineComponent, PropType, ref, toRefs } from 'vue';

  import { post } from 'api/utils';
  import Modal from 'components/Modal.vue';
  import HueButton from 'components/HueButton.vue';
  import { Connector } from 'config/types';
  import huePubSub from 'utils/huePubSub';
  import I18n from 'utils/i18n';

  const HISTORY_CLEARED_EVENT = 'query.history.cleared';

  export default defineComponent({
    name: 'ClearQueryHistoryModal',
    components: {
      HueButton,
      Modal
    },
    props: {
      modelValue: {
        type: Boolean,
        default: false
      },
      connector: {
        type: Object as PropType<Connector | undefined>,
        default: undefined
      }
    },
    emits: ['update:model-value', 'history-cleared'],
    setup(props, { emit }) {
      const { connector } = toRefs(props);
      const clearingHistory = ref(false);

      const clearHistory = async (): Promise<void> => {
        if (!connector.value) {
          return;
        }
        clearingHistory.value = true;

        try {
          await post('/notebook/api/clear_history', {
            doc_type: connector.value.dialect
          });
          emit('history-cleared');
          huePubSub.publish(HISTORY_CLEARED_EVENT);
        } catch (err) {}
        clearingHistory.value = false;
        emit('update:model-value', false);
      };
      return {
        clearHistory,
        clearingHistory,
        I18n
      };
    }
  });
</script>
