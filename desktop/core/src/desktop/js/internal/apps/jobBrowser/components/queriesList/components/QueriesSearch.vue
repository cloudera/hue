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
      <dropdown-menu :text="'Searches'">
        <dropdown-menu-group header="Suggested">
          <dropdown-menu-text v-if="!listedSearches.suggested.length">
            No suggestions
          </dropdown-menu-text>
          <dropdown-menu-button
            v-for="listedSearch in listedSearches.suggested"
            :key="listedSearch.name"
            @click="searchSelected(listedSearch)"
          >
            {{ listedSearch.name }}
          </dropdown-menu-button>
        </dropdown-menu-group>
        <dropdown-menu-group header="Suggested">
          <dropdown-menu-text v-if="!listedSearches.saved.length">
            No saved searches
          </dropdown-menu-text>
          <dropdown-menu-item v-for="listedSearch in listedSearches.saved" :key="listedSearch.name">
            <a href="javascript: void(0);" @click="searchSelected(listedSearch)">{{
              listedSearch.name
            }}</a>
            <i class="fa fa-times" aria-hidden="true" @click="deleteSearch(listedSearch)" />
            {{ listedSearch.name }}
          </dropdown-menu-item>
        </dropdown-menu-group>
      </dropdown-menu>

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
  import { defineComponent, PropType } from 'vue';

  import RangePanel from './RangePanel.vue';
  import * as api from '../api-utils/search';
  import { Search, TableDefinition } from '../index';
  import DropdownMenu from 'components/dropdown/DropdownMenu.vue';
  import DropdownMenuGroup from 'components/dropdown/DropdownMenuGroup.vue';
  import DropdownMenuItem from 'components/dropdown/DropdownMenuItem.vue';
  import DropdownMenuButton from 'components/dropdown/DropdownMenuButton.vue';
  import DropdownMenuText from 'components/dropdown/DropdownMenuText.vue';
  import Modal from 'components/Modal.vue';

  export default defineComponent({
    name: 'QueriesSearch',
    components: {
      DropdownMenuItem,
      DropdownMenuText,
      DropdownMenuButton,
      DropdownMenuGroup,
      DropdownMenu,
      Modal,
      RangePanel
    },
    props: {
      searches: {
        type: Array as PropType<Search[]>,
        required: true
      },
      tableDefinition: {
        type: Object as PropType<TableDefinition>,
        required: true
      }
    },
    emits: ['search'],
    data() {
      return {
        searchText: '',
        searchName: '',
        includeFilterAndColumns: false,
        isShowingSaveModal: false
      };
    },
    computed: {
      listedSearches(): { suggested: Search[]; saved: Search[] } {
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
    },
    methods: {
      async deleteSearch(search: Search): Promise<void> {
        await api.deleteSearch(search);
      },
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
      },
      search(): void {
        this.$emit('search', this.searchText);
      },
      searchSelected(search: Search): void {
        this.searchText = search.clause;
      },
      toggleSaveModal(): void {
        this.isShowingSaveModal = !this.isShowingSaveModal;
      }
    }
  });
</script>
