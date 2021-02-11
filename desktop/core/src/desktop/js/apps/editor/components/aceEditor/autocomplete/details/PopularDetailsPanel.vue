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
      <span>{{ title }}</span>
      <i class="popular fa fa-fw fa-star-o" :title="popularityTitle" />
    </div>
    <div class="autocompleter-details-contents">
      <div class="autocompleter-details-contents-inner">
        <sql-text :value="suggestion.value" :dialect="dialect" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Suggestion } from '../AutocompleteResults';
  import { CategoryId } from '../Category';
  import SqlText from 'components/SqlText.vue';
  import { Connector } from 'types/config';
  import I18n from 'utils/i18n';

  interface PopularityDetails {
    workloadPercent?: number;
    relativePopularity?: number;
  }

  export default defineComponent({
    components: {
      SqlText
    },

    props: {
      suggestion: {
        type: Object as PropType<Suggestion>,
        required: true
      },
      connector: {
        type: Object as PropType<Connector>,
        default: undefined
      }
    },

    computed: {
      details(): PopularityDetails {
        return <PopularityDetails>this.suggestion.details;
      },

      dialect(): string | undefined {
        return this.connector && this.connector.dialect;
      },

      popularityTitle(): string {
        if (
          this.suggestion.category.categoryId === CategoryId.PopularGroupBy ||
          this.suggestion.category.categoryId === CategoryId.PopularOrderBy
        ) {
          return `${I18n('Workload percent')}: ${this.details.workloadPercent || '?'}%`;
        }
        return `${I18n('Relative popularity')}: ${this.details.relativePopularity || '?'}%`;
      },

      title(): string {
        switch (this.suggestion.category.categoryId) {
          case CategoryId.PopularFilter:
            return I18n('Popular filter');
          case CategoryId.PopularGroupBy:
            return I18n('Popular group by');
          case CategoryId.PopularOrderBy:
            return I18n('Popular order by');
          case CategoryId.PopularActiveJoin:
          case CategoryId.PopularJoin:
            return I18n('Popular join');
          case CategoryId.PopularJoinCondition:
            return I18n('Popular join condition');
        }
        return I18n('Popular');
      }
    }
  });
</script>
