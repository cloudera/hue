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
    <div class="autocompleter-header">
      <i class="fa fa-fw fa-superscript" />
      <span>{{ udfName }}</span>
    </div>
    <div class="autocompleter-details-contents">
      <div class="autocompleter-details-contents-inner">
        <div class="details-code">{{ details.signature }}</div>
        <div class="details-description">{{ details.description }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { UdfDetails } from 'sql/reference/types';
  import { Suggestion } from '../AutocompleteResults';

  export default defineComponent({
    props: {
      suggestion: {
        type: Object as PropType<Suggestion>,
        required: true
      }
    },

    computed: {
      details(): UdfDetails {
        return <UdfDetails>this.suggestion.details;
      },

      udfName(): string {
        return this.details.signature.substring(0, this.details.signature.indexOf('('));
      }
    }
  });
</script>
