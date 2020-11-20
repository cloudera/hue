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
      <i
        class="fa fa-fw"
        :class="{
          'fa-database': details.isDatabase(),
          'fa-eye': details.isView(),
          'fa-table': details.isTable(),
          'fa-columns': details.isField()
        }"
      />
      <span>{{ details.getTitle() }}</span>
      <div
        v-if="suggestion.popular && suggestion.relativePopularity"
        class="autocompleter-header-popularity"
      >
        <i class="fa fa-fw fa-star-o popular-color" :title="popularityTitle" />
      </div>
    </div>
    <div class="autocompleter-details-contents">
      <div class="autocompleter-details-contents-inner">
        <div v-if="details.isColumn()">
          <div class="details-attribute">
            <i class="fa fa-table fa-fw" />
            <span>{{ details.path[0] }}.{{ details.path[1] }}</span>
          </div>
        </div>
        <div v-if="details.isPartitionKey()" class="details-attribute">
          <i class="fa fa-key fa-fw" /> {{ I18n('Partition key') }}
        </div>
        <div v-else-if="details.isPrimaryKey()" class="details-attribute">
          <i class="fa fa-key fa-fw" /> {{ I18n('Primary key') }}
        </div>
        <div v-else-if="details.isForeignKey()" class="details-attribute">
          <i class="fa fa-key fa-fw" /> {{ I18n('Foreign key') }}
        </div>

        <div v-if="loading" class="details-comment">
          <spinner size="small" inline="true" />
        </div>
        <div v-else-if="comment" class="details-comment">{{ comment }}</div>
        <div v-else class="details-no-comment">{{ I18n('No description') }}</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import CancellableJqPromise from 'api/cancellableJqPromise';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';

  import DataCatalogEntry from 'catalog/dataCatalogEntry';
  import I18n from 'utils/i18n';
  import { Suggestion } from './AutocompleteResults';

  import Spinner from 'components/Spinner.vue';

  const COMMENT_LOAD_DELAY = 1500;

  @Component({
    components: { Spinner },
    methods: { I18n }
  })
  export default class CatalogEntryDetailsPanel extends Vue {
    @Prop({ required: true })
    suggestion!: Suggestion;

    loading = false;
    comment: string | null = null;
    loadTimeout = -1;
    commentPromise: CancellableJqPromise<string> | null = null;

    mounted(): void {
      if (this.details.hasResolvedComment()) {
        this.comment = this.details.getResolvedComment();
      } else {
        this.loading = true;
        this.loadTimeout = window.setTimeout(() => {
          this.commentPromise = this.details
            .getComment({ silenceErrors: true, cancellable: true })
            .done(comment => {
              this.comment = comment;
            })
            .always(() => {
              this.loading = false;
            });
        }, COMMENT_LOAD_DELAY);
      }
    }

    destroyed(): void {
      window.clearTimeout(this.loadTimeout);
      if (this.commentPromise) {
        this.commentPromise.cancel();
      }
    }

    get details(): DataCatalogEntry {
      return <DataCatalogEntry>this.suggestion.details;
    }

    get popularityTitle(): string {
      return `${I18n('Popularity')} ${this.suggestion.relativePopularity}%`;
    }

    get showTitle(): boolean {
      return false;
    }
  }
</script>

<style lang="scss" scoped></style>
