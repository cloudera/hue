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
  <div class="em-table-facet-panel hide-filter">
    <ul class="field-list">
      <li v-if="facets.length > 10">
        <input placeholder="Filter" type="text" v-model="filter" class="field-filter-box">
      </li>
      <template v-for="selection in filteredFacets">
        <facet-value-list
            :facet="selection.facet"
            :selected-values="selection.selectedValues"
            v-on:values-selected="selectedValues => { selection.selectedValues = selectedValues }"
        ></facet-value-list>
      </template>
    </ul>
    <div class="buttons">
      <button type="button" class="btn btn-primary" @click="apply">Apply</button>
      <button type="button" class="btn btn-default" @click="clear">Clear</button>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import FacetValueList from './FacetValueList.vue';
  import { Facet, FacetValue } from '../../index';

  interface FacetSelection {
    facet: Facet;
    selectedValues: FacetValue[];
  }

  @Component({
    components: { FacetValueList }
  })
  export default class FacetsPanel extends Vue {
    @Prop({ required: true })
    facets!: Facet[];

    filter = '';

    get facetSelection(): FacetSelection[] {
      return this.facets.map(facet => ({ facet, selectedValues: [...facet.values] }))
    }

    get filteredFacets(): FacetSelection[] {
      if (!this.filter) {
        return this.facetSelection;
      }
      const filterLower = this.filter.toLowerCase();
      return this.facetSelection.filter(selection => selection.facet.facetField.toLowerCase().indexOf(filterLower) !== -1);
    }

    apply() {
      const searchFacets: { field: string, values: string []}[] = [];
      this.facetSelection.forEach(selection => {
        if (selection.facet.values.length !== selection.selectedValues.length) {
          searchFacets.push({
            field: selection.facet.facetField,
            values: selection.selectedValues.map(value => value.key)
          })
        }
      })
      this.$emit('search-facets-changed', searchFacets);
    }

    clear() {
      this.facetSelection.forEach(selection => { selection.selectedValues = [...selection.facet.values]})
    }
  }
</script>

<style lang="scss" scoped>
</style>
