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
    <div class="input-group">
      <div class="input-group-btn">
        <button
          type="button"
          class="btn btn-default dropdown-toggle"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        >
          Searches <span class="caret" />
        </button>
        <ul class="dropdown-menu">
          <li class="dropdown-header">Suggested</li>
          <li
            v-for="search in listedSearches.suggested"
            :key="search.name"
            @click="searchSelected(search)"
          >
            <a href="javascript: void(0);">{{ search.name }}</a>
          </li>
          <li v-if="listedSearches.suggested.length === 0" class="message">No suggestions!</li>
          <li class="dropdown-header">Saved Searches</li>
          <li v-for="search in listedSearches.saved" :key="search.name" class="saved-search">
            <a href="javascript: void(0);" @click="searchSelected(search)">{{ search.name }}</a>
            <i class="fa fa-times" aria-hidden="true" @click="deleteSearch(search)" />
          </li>
          <li v-if="listedSearches.saved.length === 0" class="message">No saved searches</li>
        </ul>
      </div>

      <input
        v-model="searchText"
        type="search"
        class="form-control"
        placeholder="Search Queries"
        @keyup.enter="search"
      />

      <div class="input-group-btn time-dropdown">
        <button
          type="button"
          class="btn btn-default dropdown-toggle"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        >
          {{ tableDefinition.rangeData.title }} <span class="caret" />
        </button>
        <div class="dropdown-menu range-panel pull-right">
          <range-panel :table-definition="tableDefinition" />
        </div>

        <button class="btn btn-default search" type="button" @click="search">
          <i class="fa fa-search" aria-hidden="true" />
        </button>
      </div>

      <div class="input-group-btn save-button">
        <button class="btn btn-default" type="button" @click="toggleSaveModal">
          <i class="fa fa-save" aria-hidden="true" />
        </button>
      </div>
    </div>
    <modal v-if="isShowingSaveModal" @close="toggleSaveModal">
      <template #header>
        <span class="modal-title">Save Search</span>
        <i class="fa fa-exclamation-circle" aria-hidden="true" />
      </template>
      <template #body>
        NAME *
        <input v-model="searchName" type="text" class="form-control" />
        <div>
          <label>
            <input v-model="includeFilterAndColumns" type="checkbox" class="form-control" />
            Include Filters and Columns
          </label>
        </div>
      </template>
      <template #footer>
        <button type="button" class="modal-default-button" @click="toggleSaveModal">CANCEL</button>
        <button type="button" class="" @click="saveSearch">SAVE</button>
      </template>
    </modal>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import Modal from '../../../../../../desktop/core/src/desktop/js/components/Modal.vue';
  import RangePanel from './RangePanel.vue';
  import { Search, TableDefinition } from '../index';
  import * as api from '../apiUtils';

  @Component({
    components: { Modal, RangePanel }
  })
  export default class QueriesSearch extends Vue {
    @Prop({ required: true })
    searches!: Search[];
    @Prop({ required: true })
    tableDefinition!: TableDefinition;

    searchText = '';
    searchName = '';
    includeFilterAndColumns = false;

    isShowingSaveModal = false;

    get listedSearches(): { suggested: Search[]; saved: Search[] } {
      const result = { suggested: <Search[]>[], saved: <Search[]>[] };
      this.searches.forEach(search => {
        if (search.category === 'SUGGEST') {
          result.suggested.push(search);
        } else if (search.category === 'SAVED') {
          result.saved.push(search);
        }
      });
      return result;
    }

    async deleteSearch(search: Search): Promise<void> {
      await api.deleteSearch(search);
    }

    searchSelected(search: Search): void {
      this.searchText = search.clause;
    }

    search(): void {
      this.$emit('search', this.searchText);
    }

    toggleSaveModal(): void {
      this.isShowingSaveModal = !this.isShowingSaveModal;
    }

    async saveSearch(): Promise<void> {
      this.toggleSaveModal();
      if (this.searchName) {
        await api.saveSearch({
          name: this.searchName,
          category: 'SAVED',
          type: 'ADVANCED',
          entity: 'query',
          clause: this.searchText
        });
        this.searchName = '';
      }
    }
  }
</script>

<style lang="scss" scoped></style>
