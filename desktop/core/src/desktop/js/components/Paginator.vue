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
  <div class="hue-paginator">
    <div class="page-status">
      {{ offset + 1 }}-{{ Math.min(offset + limit, totalEntries) }} of {{ totalEntries }}
    </div>
    Rows per page:
    <dropdown-menu :link="true" :text="String(limit)">
      <dropdown-menu-button
        v-for="presetLimit of presetLimits"
        :key="presetLimit"
        @click="setLimit(presetLimit)"
      >
        {{ presetLimit }}
      </dropdown-menu-button>
    </dropdown-menu>
    <div class="navigation-actions">
      <a
        href="javascript: void(0);"
        :class="{ disabled: currentPage === 1 }"
        @click="gotoFirstPage"
      >
        <hue-icon type="hi-chevron-left-limit" />
      </a>
      <a
        href="javascript: void(0);"
        :class="{ disabled: currentPage === 1 }"
        @click="gotoPreviousPage"
      >
        <hue-icon type="hi-chevron-left" />
      </a>
      <a
        href="javascript: void(0);"
        :class="{ disabled: currentPage === totalPages }"
        @click="gotoNextPage"
      >
        <hue-icon type="hi-chevron-right" />
      </a>
      <a
        href="javascript: void(0);"
        :class="{ disabled: currentPage === totalPages }"
        @click="gotoLastPage"
      >
        <hue-icon type="hi-chevron-right-limit" />
      </a>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import HueIcon from './HueIcon.vue';
  import DropdownMenu from './dropdown/DropdownMenu.vue';
  import DropdownMenuButton from './dropdown/DropdownMenuButton.vue';

  const DEFAULT_LIMIT = 25;
  const PRESET_LIMITS = [DEFAULT_LIMIT, 50, 100];

  export default defineComponent({
    components: {
      HueIcon,
      DropdownMenu,
      DropdownMenuButton
    },

    props: {
      totalEntries: {
        type: Number,
        required: true
      }
    },

    emits: ['page-changed'],

    setup(): {
      presetLimits: number[];
    } {
      return {
        presetLimits: PRESET_LIMITS
      };
    },

    data(): {
      currentPage: number;
      limit: number;
    } {
      return {
        currentPage: 1,
        limit: DEFAULT_LIMIT
      };
    },

    computed: {
      offset(): number {
        return (this.currentPage - 1) * this.limit;
      },

      lastDisplayedIndex(): number {
        return Math.min(this.offset + this.limit, this.totalEntries - 1);
      },

      totalPages(): number {
        return Math.ceil(this.totalEntries / this.limit) || 1;
      }
    },

    watch: {
      currentPage(): void {
        this.notifyPageChanged();
      }
    },

    mounted(): void {
      this.notifyPageChanged();
    },

    methods: {
      notifyPageChanged(): void {
        this.$emit('page-changed', {
          offset: this.offset,
          limit: this.limit
        });
      },

      gotoFirstPage(): void {
        this.currentPage = 1;
      },

      gotoPreviousPage(): void {
        this.currentPage = Math.max(this.currentPage - 1, 1);
      },

      gotoNextPage(): void {
        this.currentPage = Math.min(this.currentPage + 1, this.totalPages);
      },

      gotoLastPage(): void {
        this.currentPage = this.totalPages;
      },

      setLimit(limit: number): void {
        if (limit === this.limit) {
          return;
        }
        const factor = limit / this.limit;
        this.limit = limit;
        const lastCurrentPage = this.currentPage;
        this.currentPage = Math.floor((this.currentPage - 1) / factor) + 1;
        if (lastCurrentPage === this.currentPage) {
          this.notifyPageChanged(); // this.limit isn't watched
        }
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import 'styles/colors';

  .hue-paginator {
    width: 100%;
    height: 25px;
    text-align: right;
    padding: 10px 0;

    .page-status {
      display: inline-block;
      margin-right: 15px;
    }

    .navigation-actions {
      a {
        color: $fluid-gray-700;

        &.disabled {
          cursor: default;
          color: $hue-action-disabled;
        }

        &:hover:not(.disabled) {
          color: $hue-action-primary-hover;
        }
      }

      font-size: 23px;
      margin-left: 15px;
      margin-right: 20px;
      display: inline-block;
    }
  }
</style>
