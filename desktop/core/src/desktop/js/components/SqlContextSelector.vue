<template>
  <ul v-if="listView && connectors.length > 1">
    <li v-for="connector in connectors" :key="connector.id">
      <div @click="connectorSelected(connector)"><ConnectorIcon /> {{ connector.displayName }}</div>
    </li>
  </ul>
  <DropdownMenu
    v-if="!listView && connectors.length > 1"
    :link="true"
    :text="modelValue?.connector.name || I18n('Source')"
  >
    <DropdownMenuButton
      v-for="connector in connectors"
      :key="connector.id"
      @click="connectorSelected(connector)"
    >
      {{ connector.displayName }}
    </DropdownMenuButton>
  </DropdownMenu>
</template>

<script lang="ts">
  import { defineComponent, onMounted, PropType, ref, toRefs } from 'vue';

  import DropdownMenuButton from './dropdown/DropdownMenuButton.vue';
  import DropdownMenu from './dropdown/DropdownMenu.vue';
  import ConnectorIcon from './icons/vue/ConnectorIcon';
  import { SqlContext } from './SqlContextSelector';
  import SubscriptionTracker from './utils/SubscriptionTracker';
  import { EditorInterpreter } from 'config/types';
  import { filterEditorConnectors, getConfig } from 'config/hueConfig';
  import { CONFIG_REFRESHED_TOPIC, ConfigRefreshedEvent } from 'config/events';
  import I18n from 'utils/i18n';
  import { getNamespaces } from '../catalog/contextCatalog';

  export default defineComponent({
    name: 'SqlContextSelector',
    components: { ConnectorIcon, DropdownMenuButton, DropdownMenu },
    props: {
      allowNull: {
        type: Boolean,
        default: false
      },
      fixedDialect: {
        type: String as PropType<string | null>,
        default: null
      },
      listView: {
        type: Boolean,
        default: false
      },
      modelValue: {
        type: Object as PropType<SqlContext | null>,
        default: null
      }
    },
    emits: ['update:model-value'],
    setup(props, { emit }) {
      const { modelValue, allowNull, fixedDialect } = toRefs(props);
      const subTracker = new SubscriptionTracker();
      const connectors = ref<EditorInterpreter[]>([]);

      const connectorSelected = async (connector: EditorInterpreter | null) => {
        if (connector) {
          const { namespaces } = await getNamespaces({ connector });
          const namespacesWithCompute = namespaces.filter(namespace => namespace.computes.length);
          if (namespacesWithCompute.length) {
            // TODO: Add support for namespace and compute selection
            const namespace = namespacesWithCompute[0];
            const compute = namespace.computes[0];
            emit('update:model-value', { connector, namespace, compute });
          } else {
            console.warn(`Couldn't find a namespace and/or compute for connector: ${connector.id}`);
          }
        }
      };

      const updateConnectors = () => {
        connectors.value = filterEditorConnectors(
          connector =>
            connector.is_sql && (!fixedDialect.value || connector.dialect === fixedDialect.value)
        );

        let updatedConnector: EditorInterpreter | null = null;
        // Set the activeConnector to 1. updated version, 2. same dialect, 3. first connector
        if (modelValue.value) {
          updatedConnector =
            connectors.value.find(connector => connector.id === modelValue.value!.connector.id) ||
            connectors.value.find(
              connector => connector.dialect === modelValue.value!.connector.dialect
            );
        }
        if (!allowNull.value && !updatedConnector && connectors.value.length) {
          updatedConnector = connectors.value[0];
        }

        if (!updatedConnector && connectors.value.length === 1) {
          updatedConnector = connectors.value[0];
        }

        connectorSelected(updatedConnector || null);
      };

      onMounted(() => {
        getConfig().then(updateConnectors);
      });

      subTracker.subscribe<ConfigRefreshedEvent>(CONFIG_REFRESHED_TOPIC, updateConnectors);

      return { connectors, connectorSelected, I18n };
    }
  });
</script>
