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
    <div class="autocompleter-header">{{ suggestion.value }}</div>
    <div class="autocompleter-details-contents">
      <div class="autocompleter-details-contents-inner">
        <div class="details-code">
          {{ I18n('Type:') }} <span>{{ details.type }}</span>
        </div>
        <div class="details-code">
          {{ I18n('Default:') }} <span>{{ details.default }}</span>
        </div>
        <div class="details-description">{{ details.description }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Suggestion } from '../AutocompleteResults';
  import { SetDetails } from 'sql/reference/types';
  import I18n from 'utils/i18n';

  export default defineComponent({
    props: {
      suggestion: {
        type: Object as PropType<Suggestion>,
        required: true
      }
    },

    computed: {
      details(): SetDetails {
        return <SetDetails>this.suggestion.details;
      }
    },

    methods: {
      I18n
    }
  });
</script>
