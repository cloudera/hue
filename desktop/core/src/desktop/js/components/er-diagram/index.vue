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
  <div class="er-diagram">
    <div class="buttons-panel">
      <button class="btn btn-default btn-sm" title="Toggle Fullscreen" @click="toggleFS">
        <expand-icon v-pre class="fa fa-expand" />
      </button>
    </div>

    <div class="erd-scroll-panel">
      <div class="erd-container">
        <div v-for="(group, index) in groups" :key="index" class="entity-group">
          <div v-for="entity in group" :key="entity.id" class="entity-container">
            <TableEntity
              v-if="entity.type === EntityTypes.Table"
              :entity="entity"
              @click="entityClicked"
              @updated="plotRelations()"
            />
            <LiteralEntity
              v-else-if="entity.type === EntityTypes.Literal"
              :entity="entity"
              :data-entity-id="entity.id"
              @click="entityClicked"
            />
          </div>
        </div>

        <!-- Relations -->
        <svg class="erd-relations">
          <path
            v-for="(relation, index) in relations"
            :key="index"
            :data-entity-id-left="relation.left.id"
            :data-entity-id-right="relation.right.id"
            class="relation-path"
          />
        </svg>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { Component, Prop, Vue } from 'vue-property-decorator';

  import { groupEntities } from './lib/processor';
  import { IEntity, IRelation } from './lib/interfaces';
  import { EntityTypes } from './lib/enums';

  import { toggleFullScreen } from '../../utils/hueUtils';

  import TableEntity from './comps/table-entity.vue';
  import LiteralEntity from './comps/literal-entity.vue';

  import './er-diagram.scss';

  const CURVATURE = 40;

  @Component({
    components: {
      TableEntity,
      LiteralEntity
    }
  })
  export default class ERDiagram extends Vue {
    @Prop()
    entities: IEntity[];
    @Prop()
    relations: IRelation[];

    EntityTypes = EntityTypes;

    get groups(): IEntity[][] | undefined {
      if (this.entities && this.relations) {
        return groupEntities(this.entities, this.relations);
      }
    }

    getSelectorPosition(
      selector: string,
      offset: { x: number; y: number }
    ): { x: number; y: number } {
      const element = this.$el.querySelector(selector);
      if (element) {
        const rect = element.getBoundingClientRect();
        let x = rect.left;
        let y = rect.top;

        if (offset) {
          x = x - offset.x;
          y = y - offset.y + 1;
        }

        return { x, y };
      }
    }

    plotRelations(): void {
      const relationPaths: HTMLElement[] = this.$el.querySelectorAll<HTMLElement>('.relation-path');
      const offset = this.getSelectorPosition('.erd-relations');

      relationPaths.forEach(element => {
        const leftPos = this.getSelectorPosition(
          `[data-entity-id~="${element.dataset.entityIdLeft}"] .right-point`,
          offset
        );
        const rightPos = this.getSelectorPosition(
          `[data-entity-id~="${element.dataset.entityIdRight}"] .left-point`,
          offset
        );

        if (leftPos && rightPos) {
          const path: string =
            `M ${leftPos.x},${leftPos.y} C ${leftPos.x + CURVATURE},${leftPos.y} ` +
            `${rightPos.x - CURVATURE},${rightPos.y} ${rightPos.x},${rightPos.y}`;
          element.setAttribute('d', path);

          element.style.visibility = 'visible';
        } else {
          element.style.visibility = 'hidden';
        }
      });
    }
    updated(): void {
      this.plotRelations();
    }
    mounted(): void {
      this.plotRelations();
    }

    toggleFS(): void {
      toggleFullScreen(this.$el);
      this.$emit('toggle-fullscreen');
    }

    entityClicked(entity: IEntity): void {
      this.$emit('entity-clicked', entity);
    }
  }
</script>
