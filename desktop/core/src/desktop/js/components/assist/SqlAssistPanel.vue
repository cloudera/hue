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
  <div class="hue-sql-assist-panel">
    <div
      v-if="useBreadcrumbs && activeSqlContext && !rootEntry"
      class="sql-assist-breadcrumb"
      role="button"
      tabindex="0"
      @click="activeSqlContext = null"
    >
      <ChevronLeftIcon /> <ConnectorIcon /> {{ activeSqlContext.connector.displayName }}
    </div>

    <SqlContextSelector
      v-if="!activeSqlContext"
      v-model="activeSqlContext"
      :fixed-dialect="fixedDialect"
      :list-view="true"
      :allow-null="true"
    />

    <div
      v-if="useBreadcrumbs && rootEntry && rootEntry.isDatabase()"
      class="sql-assist-breadcrumb"
      role="button"
      tabindex="0"
      @click="rootEntry = null"
    >
      <ChevronLeftIcon /> <DatabaseIcon /> {{ rootEntry.name }}
    </div>

    <spinner :spin="activeSqlContext && loading" :center="true" :size="'xlarge'" />
    <ul v-if="activeSqlContext && !loading && !rootEntry">
      <li v-for="database in databases" :key="database.name">
        <div role="button" tabindex="0" @click="onDatabaseClick(database)">
          <DatabaseIcon /> {{ database.name }}
        </div>
      </li>
    </ul>

    <SqlAssistEntry
      v-if="rootEntry"
      :entry="rootEntry"
      :root="true"
      :show-first-level-arrows="showFirstLevelArrows"
    />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType, ref, toRefs, watch } from 'vue';

  import './SqlAssistPanel.scss';
  import SubscriptionTracker from '../utils/SubscriptionTracker';
  import SqlAssistEntry from './SqlAssistEntry.vue';
  import ChevronLeftIcon from '../icons/vue/ChevronLeftIcon';
  import ConnectorIcon from '../icons/vue/ConnectorIcon';
  import Spinner from '../Spinner.vue';
  import DatabaseIcon from '../icons/vue/DatabaseIcon';
  import dataCatalog from 'catalog/dataCatalog';
  import DataCatalogEntry from 'catalog/DataCatalogEntry';
  import { SqlContext } from 'components/SqlContextSelector';
  import SqlContextSelector from 'components/SqlContextSelector.vue';
  import I18n from 'utils/i18n';

  export default defineComponent({
    name: 'SqlAssistPanel',
    components: {
      ConnectorIcon,
      ChevronLeftIcon,
      SqlAssistEntry,
      Spinner,
      DatabaseIcon,
      SqlContextSelector
    },
    props: {
      fixedDialect: {
        type: String as PropType<string | null>,
        default: null
      },
      showFirstLevelArrows: {
        type: Boolean as PropType<boolean>,
        default: false
      },
      useBreadcrumbs: {
        type: Boolean as PropType<boolean>,
        default: true
      }
    },
    setup(props) {
      const { useBreadcrumbs } = toRefs(props);
      const subTracker = new SubscriptionTracker();
      const activeSqlContext = ref<SqlContext | null>(null);
      const rootEntry = ref<DataCatalogEntry | null>(null);
      const loading = ref(false);
      const databases = ref<DataCatalogEntry[]>([]);

      const refresh = async (sqlContext: SqlContext): Promise<void> => {
        if (sqlContext) {
          loading.value = true;
          try {
            const sourceEntry = await dataCatalog.getEntry({
              path: [],
              ...sqlContext
            });
            if (useBreadcrumbs.value) {
              rootEntry.value = null;
              databases.value = await sourceEntry.getChildren();
            } else {
              databases.value = [];
              rootEntry.value = sourceEntry;
            }
          } catch {}
          loading.value = false;
        }
      };

      watch(activeSqlContext, refresh);

      const onDatabaseClick = (database: DataCatalogEntry): void => {
        rootEntry.value = database;
      };

      subTracker.subscribe('data.catalog.entry.refreshed', refresh);

      return {
        rootEntry,
        activeSqlContext,
        databases,
        loading,
        onDatabaseClick,
        I18n
      };
    }
  });
</script>
