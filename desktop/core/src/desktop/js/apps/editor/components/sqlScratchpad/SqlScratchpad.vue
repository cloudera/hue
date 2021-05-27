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
  <div class="sql-scratchpad">
    <HueIcons />
    <Spinner v-if="loading" spin="true" />
    <div v-if="!loading && executor" class="sql-scratchpad-container">
      <div class="sql-scratchpad-editor">
        <AceEditor
          :id="id"
          :ace-options="aceOptions"
          :executor="executor"
          :sql-parser-provider="sqlParserProvider"
          :sql-reference-provider="sqlReferenceProvider"
          @active-statement-changed="onActiveStatementChanged"
        />
      </div>
      <div class="sql-scratchpad-progress">
        <ExecutableProgressBar :executable="activeExecutable" />
      </div>
      <div class="sql-scratchpad-actions">
        <ExecuteButton :executable="activeExecutable" />
        <ExecuteLimitInput :executable="activeExecutable" />
      </div>
      <div class="sql-scratchpad-result">
        <ResultTable :executable="activeExecutable" />
      </div>
    </div>
    <div v-else-if="!loading && !executor && errorMessage">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, onMounted, PropType, ref, toRefs } from 'vue';
  import { Ace } from 'ext/ace';

  import genericAutocompleteParser from 'parse/sql/generic/genericAutocompleteParser';
  import genericSyntaxParser from 'parse/sql/generic/genericSyntaxParser';
  import { SqlParserProvider } from 'parse/types';
  import { SqlReferenceProvider } from 'sql/reference/types';

  import './SqlScratchpad.scss';
  import AceEditor from '../aceEditor/AceEditor.vue';
  import { ActiveStatementChangedEventDetails } from '../aceEditor/types';
  import ExecutableProgressBar from '../ExecutableProgressBar.vue';
  import ExecuteButton from '../ExecuteButton.vue';
  import ExecuteLimitInput from '../ExecuteLimitInput.vue';
  import ResultTable from '../result/ResultTable.vue';
  import Executor from '../../execution/executor';
  import SqlExecutable from '../../execution/sqlExecutable';
  import { login } from 'api/auth';
  import { setBaseUrl } from 'api/utils';
  import contextCatalog from 'catalog/contextCatalog';
  import HueIcons from 'components/icons/HueIcons.vue';
  import Spinner from 'components/Spinner.vue';
  import { findEditorConnector, getConfig } from 'config/hueConfig';
  import { Compute, Connector, Namespace } from 'config/types';
  import UUID from 'utils/string/UUID';

  export default defineComponent({
    name: 'SqlScratchpad',
    components: {
      Spinner,
      HueIcons,
      ResultTable,
      ExecuteLimitInput,
      ExecuteButton,
      ExecutableProgressBar,
      AceEditor
    },
    props: {
      apiUrl: {
        type: String as PropType<string | null>,
        default: null
      },
      dialect: {
        type: String as PropType<string | null>,
        default: null
      },
      username: {
        type: String as PropType<string | null>,
        default: null
      },
      email: {
        type: String as PropType<string | null>,
        default: null
      },
      password: {
        type: String as PropType<string | null>,
        default: null
      }
    },
    setup(props) {
      const { apiUrl, dialect, username, email, password } = toRefs(props);
      const activeExecutable = ref<SqlExecutable>(null);
      const executor = ref<Executor>(null);
      const loading = ref<boolean>(true);
      const errorMessage = ref<string>(null);
      const id = UUID();

      const sqlParserProvider: SqlParserProvider = {
        getAutocompleteParser: () => Promise.resolve(genericAutocompleteParser),
        getSyntaxParser: () => Promise.resolve(genericSyntaxParser)
      };

      const sqlReferenceProvider: SqlReferenceProvider = {
        getReservedKeywords: () => Promise.resolve(new Set<string>()),
        getSetOptions: () => Promise.resolve({}),
        getUdfCategories: () => Promise.resolve([]),
        hasUdfCategories: () => false
      };

      const aceOptions: Ace.Options = {
        showLineNumbers: true,
        showGutter: true,
        maxLines: null,
        minLines: null
      };

      const initialize = async (): Promise<void> => {
        if (apiUrl.value) {
          setBaseUrl(apiUrl.value);
        }

        if (password.value !== null) {
          try {
            await login(
              username.value ? username.value : '',
              email.value ? email.value : '',
              password.value
            );
          } catch (err) {
            errorMessage.value = 'Login failed!';
            console.error(err);
            return;
          }
        }

        try {
          await getConfig(true);
        } catch (err) {
          errorMessage.value = 'Failed loading the Hue config!';
          console.error(err);
          return;
        }

        const connector = findEditorConnector(
          connector => !dialect.value || connector.dialect === dialect.value
        );
        if (!connector) {
          errorMessage.value = 'No connector found!';
          return;
        }

        try {
          const { namespaces } = await contextCatalog.getNamespaces({ connector });

          if (!namespaces.length || !namespaces[0].computes.length) {
            errorMessage.value = 'No namespaces or computes found!';
            return;
          }

          const namespace = namespaces[0];
          const compute = namespace.computes[0];

          executor.value = new Executor({
            connector: (() => connector as Connector) as KnockoutObservable<Connector>,
            namespace: (() => namespace) as KnockoutObservable<Namespace>,
            compute: (() => compute) as KnockoutObservable<Compute>,
            database: (() => 'default') as KnockoutObservable<string>
          });
        } catch {}
      };

      const onActiveStatementChanged = (event: ActiveStatementChangedEventDetails) => {
        if (executor.value) {
          executor.value.update(event, false);
          activeExecutable.value = executor.value.activeExecutable as SqlExecutable;
        }
      };

      onMounted(async () => {
        loading.value = true;
        try {
          await initialize();
        } catch (err) {
          console.error(err);
        }
        loading.value = false;
      });

      return {
        aceOptions,
        activeExecutable,
        errorMessage,
        executor,
        id,
        onActiveStatementChanged,
        sqlParserProvider,
        sqlReferenceProvider
      };
    }
  });
</script>
