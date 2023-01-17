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
  <div
    v-if="!root"
    v-bind="hasPossibleChildren ? { role: 'button', tabIndex: 0 } : {}"
    :class="{ leaf: !hasPossibleChildren }"
    @click="onEntryClick"
  >
    <span>
      <DropRightIcon v-if="showFirstLevelArrows && !open" />
      <DropDownIcon v-else-if="showFirstLevelArrows && open" />

      <DatabaseIcon v-if="entry.isDatabase()" />
      <ViewIcon v-else-if="entry.isView()" />
      <TableIcon v-else-if="entry.isTable()" />
      <ColumnIcon v-else-if="entry.isField()" />
    </span>
    {{ entry.getDisplayName() }}
  </div>
  <div v-if="open">
    <ul v-if="loadingChildren">
      <li class="spinner-container">
        <Spinner :spin="true" :inline="true" :size="'large'" />
      </li>
    </ul>
    <ul v-if="!loadingChildren && children && children.length">
      <li v-for="childEntry in children" :key="childEntry.getQualifiedPath()">
        <SqlAssistEntry
          :entry="childEntry"
          :show-first-level-arrows="root && showFirstLevelArrows"
        />
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType, ref, toRefs, watch } from 'vue';

  import ColumnIcon from '../icons/vue/ColumnIcon';
  import DatabaseIcon from '../icons/vue/DatabaseIcon';
  import DropDownIcon from '../icons/vue/DropDownIcon';
  import DropRightIcon from '../icons/vue/DropRightIcon';
  import TableIcon from '../icons/vue/TableIcon';
  import ViewIcon from '../icons/vue/ViewIcon';
  import Spinner from '../Spinner.vue';
  import DataCatalogEntry from 'catalog/DataCatalogEntry';

  export default defineComponent({
    name: 'SqlAssistEntry',
    components: {
      DropDownIcon,
      DropRightIcon,
      ColumnIcon,
      ViewIcon,
      TableIcon,
      DatabaseIcon,
      Spinner
    },
    props: {
      entry: {
        type: Object as PropType<DataCatalogEntry>,
        required: true
      },
      root: {
        type: Boolean,
        default: false
      },
      showFirstLevelArrows: {
        type: Boolean,
        default: false
      }
    },
    setup(props) {
      const { entry, root } = toRefs(props);
      const open = ref(false);
      const loadingChildren = ref(false);
      const children = ref<DataCatalogEntry[] | null>(null);
      const hasPossibleChildren = ref(true);

      watch(
        entry,
        () => {
          hasPossibleChildren.value = !entry.value || entry.value.hasPossibleChildren();
        },
        { immediate: true }
      );

      const onEntryClick = async (): Promise<void> => {
        if (!hasPossibleChildren.value) {
          return;
        }
        open.value = !open.value;
        if (open.value && !loadingChildren.value && children.value === null) {
          loadingChildren.value = true;
          try {
            children.value = await entry.value.getChildren();
          } catch (err) {
            console.warn(err);
          }
          loadingChildren.value = false;
        }
      };

      if (root.value) {
        onEntryClick();
      }

      return {
        children,
        hasPossibleChildren,
        loadingChildren,
        onEntryClick,
        open
      };
    }
  });
</script>
