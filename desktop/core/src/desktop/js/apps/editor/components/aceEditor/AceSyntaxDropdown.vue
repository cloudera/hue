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
  <div class="ace-syntax-dropdown-container" :style="position">
    <DropdownMenuOptions
      :force-bottom-placement="true"
      :open="visible"
      :options="options"
      @close="closePanel"
      @option-selected="optionSelected"
    />
  </div>
</template>

<script lang="ts">
  import { Ace } from 'ext/ace';
  import { defineComponent, PropType, ref, toRefs } from 'vue';

  import './AceSyntaxDropdown.scss';
  import { SQL_SYNTAX_DROPDOWN_SHOW_TOPIC, SqlSyntaxDropdownShowEvent } from './events';
  import DropdownMenuOptions from 'components/dropdown/DropdownMenuOptions.vue';
  import { Option } from 'components/dropdown/types';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import huePubSub from 'utils/huePubSub';
  import I18n from 'utils/i18n';
  import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

  interface SyntaxOption extends Option {
    suppress?: string;
  }

  export default defineComponent({
    name: 'AceSyntaxDropdown',
    components: { DropdownMenuOptions },
    props: {
      editor: {
        type: Object as PropType<Ace.Editor>,
        required: true
      },
      editorId: {
        type: String,
        required: true
      }
    },
    emits: [],
    setup(props) {
      const { editor, editorId } = toRefs(props);
      const subTracker = new SubscriptionTracker();
      const visible = ref(false);
      const range = ref<Ace.Range>();
      const options = ref<SyntaxOption[]>([]);
      const position = ref<Pick<CSSStyleDeclaration, 'left' | 'top'>>();

      const closePanel = (): void => {
        options.value = [];
        range.value = undefined;
        visible.value = false;
      };

      const optionSelected = ({ suppress, value }: SyntaxOption) => {
        if (suppress) {
          const currentSuppressedRules = getFromLocalStorage(
            'hue.syntax.checker.suppressedRules',
            {} as Record<string, boolean>
          );
          currentSuppressedRules[suppress] = true;
          setInLocalStorage('hue.syntax.checker.suppressedRules', currentSuppressedRules);
          huePubSub.publish('editor.refresh.statement.locations', editorId.value);
        } else if (range.value) {
          editor.value.session.replace(range.value, value);
        }
      };

      subTracker.subscribe('sql.syntax.dropdown.hide', closePanel);

      subTracker.subscribe<SqlSyntaxDropdownShowEvent>(SQL_SYNTAX_DROPDOWN_SHOW_TOPIC, details => {
        if (details.editorId !== editorId.value) {
          return;
        }
        const newOptions: SyntaxOption[] = details.data.expected.map(expected => ({
          label: expected.text,
          value: expected.text
        }));
        if (details.data.ruleId) {
          newOptions.push({
            label: '-',
            value: '_divider_',
            divider: true
          });
          newOptions.push({
            label: I18n('Ignore this type of error'),
            value: '_suppress_',
            suppress: details.data.ruleId + details.data.text.toLowerCase()
          });
        }
        position.value = { top: `${details.source.bottom}px`, left: `${details.source.left}px` };
        range.value = details.range;
        options.value = newOptions;
        visible.value = true;
      });

      return { closePanel, options, optionSelected, position, visible };
    }
  });
</script>
