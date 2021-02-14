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
  <div class="presentation-mode">
    <div class="presentation-mode-header">
      <h2 v-if="title">{{ title }}</h2>
      <h4 v-if="description">{{ description }}</h4>
      <hue-button class="presentation-mode-close-button" :borderless="true" @click="$emit('close')">
        <i class="fa fa-times fa-fw" />
      </hue-button>
    </div>
    <VariableSubstitution
      :locations="locations"
      :initial-variables="executor.variables"
      @variables-changed="onVariablesChanged"
    />
    <div class="presentation-mode-body">
      <div
        v-for="{ header, statement, executable } of presentationStatements"
        :key="executable.getKey()"
        class="presentation-mode-statement"
      >
        <h2 v-if="header">{{ header }}</h2>
        <h2 v-else>{{ I18n('Add -- comments on top of the SQL statement to display a title') }}</h2>

        <SqlText class="presentation-mode-sql-text" :dialect="dialect" :value="statement" />
        <ExecutableActions :executable="executable" :before-execute="beforeExecute" />
        <div class="presentation-mode-result-panel">
          <ResultTable :executable="executable" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Variable } from 'apps/editor/components/variableSubstitution/types';
  import VariableSubstitution from 'apps/editor/components/variableSubstitution/VariableSubstitution.vue';
  import { IdentifierLocation } from 'parse/types';

  import ExecutableActions from 'apps/editor/components/ExecutableActions.vue';
  import ResultTable from 'apps/editor/components/result/ResultTable.vue';
  import Executor from 'apps/editor/execution/executor';
  import SqlExecutable from 'apps/editor/execution/sqlExecutable';
  import HueButton from 'components/HueButton.vue';
  import SqlText from 'components/SqlText.vue';
  import I18n from 'utils/i18n';

  interface PresentationStatement {
    executable: SqlExecutable;
    statement: string;
    header?: string;
  }

  const headerRegEx = /--(.*)$/m;

  export default defineComponent({
    components: {
      VariableSubstitution,
      HueButton,
      ResultTable,
      ExecutableActions,
      SqlText
    },

    props: {
      executor: {
        type: Object as PropType<Executor>,
        required: true
      },

      title: {
        type: String,
        default: undefined
      },
      description: {
        type: String,
        default: undefined
      },
      locations: {
        type: Object as PropType<IdentifierLocation[]>,
        default: undefined
      }
    },

    emits: ['before-execute', 'variables-changed', 'close'],

    computed: {
      presentationStatements(): PresentationStatement[] {
        return (this.executor.executables as SqlExecutable[]).map(executable => {
          let statement = executable.parsedStatement.statement.trim();
          let header: string | undefined = undefined;
          const headerMatch = statement.match(headerRegEx);
          if (headerMatch && headerMatch.index === 0) {
            header = headerMatch[1].trim();
            statement = statement.replace(headerMatch[0], '').trim();
          }

          return {
            executable,
            statement,
            header
          };
        });
      },

      dialect(): string {
        return this.executor.connector().dialect as string;
      }
    },

    methods: {
      I18n,

      async beforeExecute(executable: SqlExecutable): Promise<void> {
        this.$emit('before-execute', executable);

        // eslint-disable-next-line vue/no-mutating-props
        this.executor.activeExecutable = executable;
      },

      onVariablesChanged(variables: Variable[]): void {
        this.$emit('variables-changed', variables);
      }
    }
  });
</script>

<style lang="scss">
  @import './PresentationMode.scss';
</style>
