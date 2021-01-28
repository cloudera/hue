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
      <span>{{ I18n('Popular aggregate') }}</span>
      <i class="popular fa fa-fw fa-star-o" :title="popularityTitle" />
    </div>
    <div class="autocompleter-details-contents">
      <div class="autocompleter-details-contents-inner">
        <div class="details-code">
          <sql-text :value="suggestion.value" :dialect="dialect" />
        </div>
        <div class="details-comment" data-bind="text: details.function.description">
          {{ description }}
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';

  import { Suggestion } from '../AutocompleteResults';
  import { TopAggValue } from 'catalog/MultiTableEntry';
  import SqlText from 'components/SqlText.vue';
  import { Connector } from 'types/config';
  import I18n from 'utils/i18n';

  @Component({
    components: { SqlText },
    methods: { I18n }
  })
  export default class PopularAggregateUdfPanel extends Vue {
    @Prop({ required: true })
    suggestion!: Suggestion;
    @Prop({ required: false })
    connector?: Connector;

    get details(): TopAggValue {
      return <TopAggValue>this.suggestion.details;
    }

    get description(): string {
      return (this.details.function && this.details.function.description) || '';
    }

    get dialect(): string | undefined {
      return this.connector && this.connector.dialect;
    }

    get popularityTitle(): string {
      return `${I18n('Relative popularity')}: ${this.details.relativePopularity || '?'}%`;
    }
  }
</script>
