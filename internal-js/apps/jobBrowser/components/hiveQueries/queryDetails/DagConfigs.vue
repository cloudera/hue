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

<script lang="ts">
  import Component from 'vue-class-component';
  import { Query } from '../index';
  import QueryConfig from './QueryConfig.vue';

  @Component
  export default class DagConfigs extends QueryConfig {
    getConfigs(query: Query): { [configName: string]: unknown } {
      const configs: { [configName: string]: unknown } = {};
      query.dags.forEach(dag => {
        if (dag.config) {
          Object.keys(dag.config).forEach(configName => {
            configs[configName] = dag.config![configName];
          })
        }
      })
      return configs;
    }
  }
</script>

<style lang="scss" scoped></style>
