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

<!-- eslint-disable vue/no-v-html -->
<template>
  <span v-html="content" />
</template>
<!-- eslint-enable -->

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Suggestion } from './AutocompleteResults';

  export default defineComponent({
    props: {
      suggestion: {
        type: Object as PropType<Suggestion>,
        required: true
      },
      filter: {
        type: String,
        required: true
      },
      isComment: {
        type: Boolean,
        required: false,
        default: false
      }
    },

    computed: {
      content(): string {
        const value =
          (this.isComment
            ? (<{ comment?: string }>this.suggestion.details).comment
            : this.suggestion.value) || '';
        if (
          this.filter &&
          typeof this.suggestion.matchIndex !== 'undefined' &&
          this.suggestion.matchIndex > -1 &&
          typeof this.suggestion.matchLength !== 'undefined' &&
          ((!this.isComment && !this.suggestion.matchComment) ||
            (this.isComment && this.suggestion.matchComment))
        ) {
          const before = value.substring(0, this.suggestion.matchIndex);
          const match = value.substring(
            this.suggestion.matchIndex,
            this.suggestion.matchIndex + this.suggestion.matchLength
          );
          const after = value.substring(this.suggestion.matchIndex + this.suggestion.matchLength);
          return `${before}<b>${match}</b>${after}`;
        }
        return value || '';
      }
    }
  });
</script>
