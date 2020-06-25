<template>
  <div>
    {{ title }}
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import wrap from '@vue/web-component-wrapper';

export const HIVE_QUERY_PLAN_COMPONENT = 'hive-query-plan';

@Component
export default class HiveQueryPlan extends Vue {
  title: string = 'Web Components FTW.';
}

window.customElements.define(HIVE_QUERY_PLAN_COMPONENT, wrap(Vue, HiveQueryPlan));
</script>
