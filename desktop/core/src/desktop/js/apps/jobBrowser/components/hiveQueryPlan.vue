<template>
  <div class="query-plan">
    {{ title }}
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import { wrap } from 'vue/webComponentWrapper';
  import Component from 'vue-class-component';

  export const HIVE_QUERY_PLAN_COMPONENT = 'hive-query-plan';

  @Component
  export default class HiveQueryPlan extends Vue {
    title: string = 'Web Components FTW.';
  }

  wrap(HIVE_QUERY_PLAN_COMPONENT, HiveQueryPlan);
</script>

<style lang="scss" scoped>
  .query-plan {
    color: #0a78a3;
  }
</style>
