<template>
  <div class="typeahead-input">
    <input
      ref="mainInputElement"
      class="main-input"
      type="text"
      :value="modelValue"
      autocomplete="no"
      @focus="$emit('focus', $event)"
      @input="$emit('update:model-value', $event.target.value)"
      @keydown="onKeyDown"
    />
    <input class="typeahead-placeholder" type="text" :value="typeahead" disabled />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  export default defineComponent({
    props: {
      typeahead: {
        type: String,
        default: ''
      },
      modelValue: {
        type: String,
        default: ''
      }
    },
    emits: ['update:model-value', 'input-element', 'focus'],
    mounted() {
      this.$emit('input-element', this.$refs.mainInputElement);
    },
    methods: {
      onKeyDown(event: KeyboardEvent) {
        if (event.key === 'Tab' && this.typeahead && this.typeahead.startsWith(this.modelValue)) {
          this.$emit('update:model-value', this.typeahead);
          event.preventDefault();
        }
      }
    }
  });
</script>

<style scoped lang="scss">
  @import './styles/colors';

  .typeahead-input {
    position: relative;
    min-width: 100px;
    min-height: 20px;

    input {
      box-sizing: border-box;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }

    .main-input {
      z-index: 2;
      background-color: transparent;
      box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.08);
    }

    .typeahead-placeholder {
      z-index: 1;
      color: #ccc;
      background-color: $fluid-white;
      box-shadow: none;
    }
  }
</style>
