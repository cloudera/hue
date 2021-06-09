<template>
  <DropdownDrawer
    :open="open && options.length"
    :trigger-element="keydownElement"
    @close="$emit('close')"
  >
    <ul>
      <DropdownMenuButton
        v-for="(option, idx) of options"
        :key="option.value || option"
        :class="{ selected: idx === selectedIndex }"
        @click="onOptionClick(option, idx)"
      >
        {{ getLabel(option) }}
      </DropdownMenuButton>
    </ul>
  </DropdownDrawer>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import DropdownDrawer from './DropdownDrawer.vue';
  import DropdownMenuButton from './DropdownMenuButton.vue';
  import { Option } from './DropDownMenuOptions';

  export const getLabel = (option: Option): string =>
    (option as { label: string }).label || (option as string);

  export default defineComponent({
    components: { DropdownMenuButton, DropdownDrawer },
    props: {
      options: {
        type: Array as PropType<Option[]>,
        default: () => []
      },
      keydownElement: {
        type: Object as PropType<HTMLElement>,
        default: null
      },
      open: {
        type: Boolean,
        default: false
      }
    },
    emits: ['close', 'option-active', 'option-selected'],
    data() {
      return {
        selectedIndex: 0,
        keydownDispose: null as (() => void) | null
      };
    },
    watch: {
      keydownElement(element) {
        if (this.keydownDispose) {
          this.keydownDispose();
        }
        if (element) {
          const handler = (event: KeyboardEvent) => {
            switch (event.key) {
              case 'ArrowDown':
                this.selectedIndex = (this.selectedIndex + 1) % this.options.length;
                break;
              case 'ArrowUp':
                this.selectedIndex =
                  this.selectedIndex !== 0 ? this.selectedIndex - 1 : this.options.length - 1;
                break;
              case 'Enter':
                this.$emit('option-selected', this.options[this.selectedIndex]);
            }
          };
          element.addEventListener('keydown', handler);
          this.keydownDispose = () => {
            element.removeEventListener('keydown', handler);
          };
        }
      },
      selectedIndex(index) {
        if (this.options.length) {
          this.$emit('option-active', this.options[index]);
        }
      },
      options() {
        this.selectedIndex = 0;
        if (this.options.length) {
          this.$emit('option-active', this.options[this.selectedIndex]);
        }
      }
    },
    beforeUnmount() {
      if (this.keydownDispose) {
        this.keydownDispose();
      }
    },
    methods: {
      getLabel,
      onOptionClick(option: Option, index: number) {
        this.selectedIndex = index;
        this.$emit('option-selected', option);
      }
    }
  });
</script>
