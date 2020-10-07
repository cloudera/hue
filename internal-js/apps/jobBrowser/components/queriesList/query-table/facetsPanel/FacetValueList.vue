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
  <div class="em-table-facet-panel-values">
    <div class="field-name" :title="facet.facetField" @click="toggleOpen">
      <div class="field-title">
        {{ facet.facetField }}
      </div>
      <div class="field-count">
        {{ facet.values.length }}
      </div>
      <a
        v-if="facet.values.length !== selectedFacetValues.length"
        class="all-button"
        title="Select all"
        @click="selectAll"
      >
        All
      </a>
    </div>
    <ul v-if="open" class="value-list">
      <li v-if="facet.values.length > 10">
        <input v-model="filter" placeholder="Filter" type="text" class="filter-box" />
      </li>
      <li
        v-for="selectableValue in filteredFacetValues"
        :key="selectableValue.facetValue.key"
        :title="selectableValue.facetValue.key"
      >
        <div class="checkbox-container">
          <input v-model="selectableValue.selected" type="checkbox" @change="onChange" />
        </div>
        <div class="facet-value">
          {{ selectableValue.facetValue.value }}
        </div>
        <a class="only-button" @click="onlySelect(selectableValue)">only</a>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import {
    Facet,
    FacetValue
  } from '../../../../../../../desktop/core/src/desktop/js/components/FacetSelector';

  interface SelectableFacetValue {
    selected: boolean;
    facetValue: FacetValue;
  }

  @Component
  export default class FacetValueList extends Vue {
    @Prop({ required: true })
    facet!: Facet;
    @Prop({ required: true })
    selectedValues!: FacetValue[];

    open = false;
    filter = '';

    get selectableFacetValues(): SelectableFacetValue[] {
      return this.facet.values.map(facetValue => ({
        facetValue,
        selected: this.selectedValues.indexOf(facetValue) !== -1
      }));
    }

    get selectedFacetValues(): FacetValue[] {
      const selectedFacetValues: FacetValue[] = [];
      this.selectableFacetValues.forEach(selectable => {
        if (selectable.selected) {
          selectedFacetValues.push(selectable.facetValue);
        }
      });
      return selectedFacetValues;
    }

    get filteredFacetValues(): SelectableFacetValue[] {
      if (!this.filter) {
        return this.selectableFacetValues;
      }
      const filterLower = this.filter.toLowerCase();
      return this.selectableFacetValues.filter(
        val => val.facetValue.key.toLowerCase().indexOf(filterLower) != -1
      );
    }

    toggleOpen(): void {
      this.open = !this.open;
    }

    onChange(): void {
      this.$emit('values-selected', this.selectedFacetValues);
    }

    selectAll(): void {
      this.selectableFacetValues.forEach(selectable => {
        selectable.selected = true;
      });
      this.onChange();
    }

    onlySelect(selectable: SelectableFacetValue): void {
      this.selectableFacetValues.forEach(otherSelectable => {
        otherSelectable.selected = otherSelectable === selectable;
      });
      this.onChange();
    }
  }
</script>

<style lang="scss" scoped></style>
