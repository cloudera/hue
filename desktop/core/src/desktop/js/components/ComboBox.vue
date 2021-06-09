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
  <div class="combo-box" v-bind="$attrs">
    <TypeaheadInput
      v-model="inputText"
      :typeahead="typeaheadOption"
      @focusin="onFocus"
      @input-element="inputElement = $event"
    />
    <DropdownMenuOptions
      :options="filteredOptions"
      :open="dropdownVisible"
      :keydown-element="inputElement"
      @close="onDropdownClose"
      @option-selected="onSelectOption"
      @option-active="onOptionActive"
    />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType, ref, watch, computed, toRefs } from 'vue';

  import TypeaheadInput from './TypeaheadInput.vue';
  import DropdownMenuOptions from './dropdown/DropdownMenuOptions.vue';
  import { Option } from './dropdown/DropDownMenuOptions';

  const getLabel = (option: Option): string =>
    (option as { label: string }).label || (option as string);

  export default defineComponent({
    name: 'ComboBox',
    components: { DropdownMenuOptions, TypeaheadInput },
    props: {
      modelValue: {
        type: String as PropType<string | null>,
        default: null
      },
      options: {
        type: Array as PropType<Option[]>,
        default: () => []
      }
    },
    emits: ['update:model-value'],
    setup(props, { emit }) {
      const { modelValue, options } = toRefs(props);

      const inputText = ref('');
      const activeOption = ref<Option | null>(null);
      const inputElement = ref<HTMLElement | null>(null);
      const dropdownVisible = ref(false);
      const filteredOptions = ref<Option[]>([]);

      const typeaheadOption = computed<Option>(
        () => (activeOption.value && getLabel(activeOption.value)) || inputText.value
      );

      const updateFromInput = (input: string): void => {
        if (!options.value || !options.value.length) {
          return;
        }

        filteredOptions.value = options.value.filter(option => getLabel(option).startsWith(input));

        if (!activeOption.value || !getLabel(activeOption.value).startsWith(input)) {
          if (!input) {
            activeOption.value = options.value[0];
          } else {
            activeOption.value =
              options.value.find(option => getLabel(option).startsWith(input)) || null;
          }
        }

        if (
          activeOption.value &&
          input !== getLabel(activeOption.value) &&
          !dropdownVisible.value
        ) {
          dropdownVisible.value = true;
        }

        const foundOption = options.value.find(option => input === getLabel(option));
        if (foundOption) {
          emit(
            'update:model-value',
            typeof foundOption === 'string' ? foundOption : foundOption.value
          );
        } else {
          emit('update:model-value', input);
        }
      };

      watch(
        modelValue,
        () => {
          if (typeof modelValue.value !== 'undefined' && options.value) {
            const found = options.value.find(val => modelValue.value === getLabel(val));
            if (found) {
              activeOption.value = found;
            }
          }
        },
        { immediate: true }
      );

      watch(inputText, newVal => {
        updateFromInput(newVal);
      });

      const onDropdownClose = () => {
        dropdownVisible.value = false;
      };

      const onFocus = () => {
        updateFromInput(inputText.value);
      };

      const onSelectOption = (option: Option) => {
        dropdownVisible.value = false;
        inputText.value = getLabel(option);
      };

      const onOptionActive = (option: Option) => {
        activeOption.value = option;
      };

      return {
        dropdownVisible,
        inputText,
        activeOption,
        getLabel,
        inputElement,
        typeaheadOption,
        filteredOptions,
        onDropdownClose,
        onFocus,
        onOptionActive,
        onSelectOption
      };
    }
  });
</script>
