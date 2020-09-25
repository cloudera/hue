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
    <div>
      Rows per page:
      <a href="javascript: void(0);" @click="setLimit(25)">25</a>
      <a href="javascript: void(0);" @click="setLimit(50)">50</a>
      <a href="javascript: void(0);" @click="setLimit(100)">100</a>
    </div>
    <div>{{ offset + 1 }}-{{ Math.min(offset + limit, totalEntries) }} of {{ totalEntries }}</div>
    <div>
      <a href="javascript: void(0);" @click="gotoFirstPage">|&lt;</a>
      <a href="javascript: void(0);" @click="gotoPreviousPage">&lt;</a>
      <a href="javascript: void(0);" @click="gotoNextPage">&gt;</a>
      <a href="javascript: void(0);" @click="gotoLastPage">&gt;|</a>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop, Watch } from 'vue-property-decorator';

  @Component
  export default class Paginator extends Vue {
    @Prop({ required: true })
    totalEntries!: number;

    currentPage = 1;
    limit = 25;

    mounted(): void {
      this.notifyPageChanged();
    }

    get offset(): number {
      return (this.currentPage - 1) * this.limit;
    }

    get lastDisplayedIndex(): number {
      return Math.min(this.offset + this.limit, this.totalEntries - 1);
    }

    get totalPages(): number {
      return Math.ceil(this.totalEntries / this.limit) || 1;
    }

    @Watch('currentPage')
    notifyPageChanged(): void {
      this.$emit('page-changed', {
        offset: this.offset,
        limit: this.limit
      });
    }

    gotoFirstPage(): void {
      this.currentPage = 1;
    }

    gotoPreviousPage(): void {
      this.currentPage = Math.max(this.currentPage - 1, 1);
    }

    gotoNextPage(): void {
      this.currentPage = Math.min(this.currentPage + 1, this.totalPages);
    }

    gotoLastPage(): void {
      this.currentPage = this.totalPages;
    }

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
</script>

<style lang="scss" scoped></style>
