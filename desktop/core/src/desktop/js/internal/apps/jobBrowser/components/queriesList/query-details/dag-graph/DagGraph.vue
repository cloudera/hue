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
  <div class="dag-view-container">
    <div v-if="errMessage" class="err-message">
      <h1>Rendering failed!</h1>
      <h5>{{ errMessage }}</h5>
    </div>
    <div v-else class="svg-container">
      <svg>
        <defs>
          <rect
            id="vertex-bg"
            class="vertex-node-bg"
            :style="{ fill: `url(${pathname}#vertex-grad)`, filter: `url(${pathname}#grey-glow)` }"
            rx="5"
            ry="5"
            width="80"
            height="30"
            x="-40"
            y="-15"
          />
          <rect
            id="input-bg"
            class="input-node-bg"
            :style="{ fill: `url(${pathname}#input-grad)`, filter: `url(${pathname}#grey-glow)` }"
            rx="15"
            ry="15"
            width="80"
            height="30"
            x="-40"
            y="-15"
          />
          <rect
            id="output-bg"
            class="output-node-bg"
            :style="{ fill: `url(${pathname}#output-grad)`, filter: `url(${pathname}#grey-glow)` }"
            rx="15"
            ry="15"
            width="80"
            height="30"
            x="-40"
            y="-15"
          />
          <circle
            id="task-bubble"
            class="task-bubble-bg"
            :style="{ fill: `url(${pathname}#task-grad)`, filter: `url(${pathname}#grey-glow)` }"
            r="10"
          />
          <circle
            id="io-bubble"
            class="input-node-bg"
            :style="{ fill: `url(${pathname}#input-grad)`, filter: `url(${pathname}#grey-glow)` }"
            r="10"
          />
          <circle
            id="group-bubble"
            class="group-bubble-bg"
            :style="{ fill: `url(${pathname}#group-grad)`, filter: `url(${pathname}#grey-glow)` }"
            r="8"
          />

          <marker
            id="arrow-marker"
            viewBox="0 -5 10 10"
            markerWidth="2"
            markerHeight="2"
            orient="auto"
          >
            <path style="fill: #aaa;" d="M0,-5L10,0L0,5" />
          </marker>

          <radialGradient id="vertex-grad" cx="50%" cy="50%" r="100%" fx="50%" fy="50%">
            <stop offset="0%" style="stop-color: #b0c4de;" />
            <stop offset="100%" style="stop-color: #769ccd;" />
          </radialGradient>

          <radialGradient id="input-grad" cx="50%" cy="50%" r="100%" fx="50%" fy="50%">
            <stop offset="0%" style="stop-color: #adff2e;" />
            <stop offset="100%" style="stop-color: #91d723;" />
          </radialGradient>

          <radialGradient id="output-grad" cx="50%" cy="50%" r="100%" fx="50%" fy="50%">
            <stop offset="0%" style="stop-color: #fa8072;" />
            <stop offset="100%" style="stop-color: #d26457;" />
          </radialGradient>

          <radialGradient id="task-grad" cx="50%" cy="50%" r="100%" fx="50%" fy="50%">
            <stop offset="0%" style="stop-color: #d0bfd1;" />
            <stop offset="100%" style="stop-color: #af8fb1;" />
          </radialGradient>

          <radialGradient id="group-grad" cx="50%" cy="50%" r="100%" fx="50%" fy="50%">
            <stop offset="0%" style="stop-color: #bbbbbb;" />
            <stop offset="100%" style="stop-color: #999999;" />
          </radialGradient>

          <filter id="grey-glow">
            <feColorMatrix
              type="matrix"
              values="0 0 0 0   0
                      0 0 0 0   0
                      0 0 0 0   0
                      0 0 0 0.3 0"
            />
            <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      </svg>
    </div>

    <div v-if="!errMessage" class="button-panel">
      <em
        :class="
          'tgl-additionals fa fa-circle ' + (hideAdditionals ? 'hide-additionals fa-circle-o' : '')
        "
        title="Toggle source/sink visibility"
        @click="tglAdditionals"
      />
      <em
        :class="
          'tgl-orientation fa fa-share-alt ' + (isHorizontal ? 'fa-rotate-270' : 'fa-rotate-180')
        "
        title="Toggle orientation"
        @click="tglOrientation"
      />
      <em class="fit-graph fa fa-arrows-alt" title="Fit DAG to viewport" @click="fitGraph" />
      <em class="tgl-fullscreen fa fa-expand" title="Toggle fullscreen" @click="fullscreen" />
    </div>

    <div class="tool-tip">
      <div class="bubble">
        <div class="tip-title">Title</div>
        <div class="tip-text" />
        <div class="tip-list" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';
  import { get } from 'lodash';

  import { Dag, DagPlan, Vertex, DagPlanVertex } from '../../index';
  import { toggleFullScreen } from 'utils/hueUtils';
  import { graphifyData } from './data-processor';
  import createGraphView from './graph-view';

  import './dag-graph.scss';

  export default defineComponent({
    props: {
      dag: {
        type: Object as PropType<Dag>,
        required: true
      }
    },

    setup() {
      return {
        graphView: createGraphView(),
        pathname: window.location.pathname + window.location.search
      };
    },

    data() {
      let vertices: DagPlanVertex[] | undefined = undefined;
      let edges: unknown[] | undefined = undefined;
      let vertexGroups: unknown[] | undefined = undefined;

      if (get(this, 'dag.dagDetails.dagPlan') && get(this, 'dag.vertices')) {
        const dagPlan: DagPlan = this.dag.dagDetails.dagPlan;
        vertices = this.combineVertexData(dagPlan.vertices, this.dag.vertices);
        edges = dagPlan.edges;
        vertexGroups = dagPlan.vertexGroups;
      }

      return {
        errMessage: '',

        vertices,
        edges,
        vertexGroups,

        isHorizontal: false,
        hideAdditionals: false,
        isFullscreen: false
      };
    },

    mounted(): void {
      if (!this.vertices) {
        this.errMessage = 'Vertices not found!';
      } else if (!this.vertices.find((vertex: DagPlanVertex) => !vertex.outEdgeIds)) {
        this.errMessage = 'Sink vertex not found!';
      } else {
        const graph = graphifyData(this.vertices, this.edges, this.vertexGroups);
        this.graphView.create(this, this.$el, graph);
      }
    },

    methods: {
      /**
       * dagPlanVertices - Contains vertex relation details - Edge Ids and additional Inputs / Outputs etc
       * eventVertices - Contains complete vertex information from vertex events
       * We combine both and create an array of vertices with all details
       */
      combineVertexData(
        dagPlanVertices: DagPlanVertex[],
        eventVertices: Vertex[]
      ): DagPlanVertex[] {
        const verticesHash: Map<string, DagPlanVertex> = new Map();

        dagPlanVertices.forEach((vertex: DagPlanVertex) => {
          verticesHash.set(vertex.vertexName, { ...vertex });
        });

        eventVertices.forEach((vertex: Vertex) => {
          const dpVertex: DagPlanVertex | undefined = verticesHash.get(vertex.name);
          if (dpVertex) {
            dpVertex.data = vertex;
          }
        });

        return Array.from(verticesHash.values());
      },

      // Actions
      tglOrientation(): void {
        const isTopBottom = this.graphView.toggleLayouts();
        this.isHorizontal = !isTopBottom;
      },
      tglAdditionals(): void {
        this.hideAdditionals = !this.hideAdditionals;
        this.graphView.additionalDisplay(this.hideAdditionals);
      },
      fullscreen(): void {
        this.isFullscreen = !this.isFullscreen;
        toggleFullScreen(this.$el);
      },
      fitGraph(): void {
        this.graphView.fitGraph();
      }
    }
  });
</script>
