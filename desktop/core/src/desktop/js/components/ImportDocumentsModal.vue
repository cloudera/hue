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
  <Modal v-if="modelValue" :header="header || I18n('Import Hue Documents')" @close="onModalClose">
    <template #body>
      <FileUpload
        v-if="!uploadStats && !importingDocuments"
        v-model="selectedFiles"
        :accept="'.json'"
        :disabled="fileSelectionDisabled"
      />
      <Spinner v-else-if="importingDocuments" :inline="true" :label="I18n('Importing....')" />
      <div v-else>
        <div>
          {{ I18n('Imported: ') }} <span>{{ uploadStats.count }}</span>
        </div>
        <div>
          {{ I18n('Created: ') }} <span>{{ uploadStats.created_count }}</span>
        </div>
        <div>
          {{ I18n('Updated: ') }} <span>{{ uploadStats.updated_count }}</span>
        </div>
      </div>
      <div v-if="failed">
        {{ I18n('Import failed!') }}
      </div>
    </template>
    <template #footer>
      <HueButton :disabled="importingDocuments" @click="onModalClose">
        {{ I18n('Close') }}
      </HueButton>
      <HueButton v-if="!uploadStats" :alert="true" :disabled="importDisabled" @click="onImport">
        {{ I18n('Import') }}
      </HueButton>
    </template>
  </Modal>
</template>

<script lang="ts">
  import { computed, defineComponent, ref } from 'vue';

  import FileUpload from './FileUpload.vue';
  import HueButton from './HueButton.vue';
  import Spinner from './Spinner.vue';
  import Modal from './Modal.vue';
  import { upload } from 'api/utils';
  import I18n from 'utils/i18n';

  interface UploadStats {
    count: number;
    created_count: number;
    updated_count: number;
  }

  export default defineComponent({
    name: 'ImportDocumentsModal',
    components: {
      Spinner,
      FileUpload,
      HueButton,
      Modal
    },
    props: {
      modelValue: {
        type: Boolean,
        default: false
      },
      header: {
        type: String,
        default: ''
      }
    },
    emits: ['update:model-value', 'documents-imported'],
    setup(props, { emit }) {
      const importingDocuments = ref(false);
      const isUploading = ref(false);
      const selectedFiles = ref<FileList | null>(null);
      const uploadStats = ref<UploadStats | null>(null);
      const failed = ref(false);

      const importDisabled = computed((): boolean => {
        return isUploading.value || importingDocuments.value || !selectedFiles.value?.length;
      });

      const fileSelectionDisabled = computed((): boolean => {
        return isUploading.value || importingDocuments.value;
      });

      const onModalClose = (): void => {
        emit('update:model-value', false);
        selectedFiles.value = null;
        uploadStats.value = null;
      };

      const onImport = async (): Promise<void> => {
        const fileList = selectedFiles.value;
        if (!fileList || !fileList.length) {
          return;
        }
        importingDocuments.value = true;

        const formData = new FormData();
        formData.append('documents', fileList[0]);

        try {
          uploadStats.value = await upload<UploadStats>('/desktop/api2/doc/import', formData);
          emit('documents-imported');
        } catch (err) {
          failed.value = true;
        }
        importingDocuments.value = false;
      };

      return {
        I18n,
        fileSelectionDisabled,
        importDisabled,
        importingDocuments,
        onImport,
        onModalClose,
        selectedFiles,
        uploadStats
      };
    }
  });
</script>
