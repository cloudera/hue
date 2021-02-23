/*
 * This file was originally copied from Apache Tez and has been modified. The modifications are subject to the
 * following provisions.
 *
 * HORTONWORKS DATAPLANE SERVICE AND ITS CONSTITUENT SERVICES
 *
 * (c) 2016-2018 Hortonworks, Inc. All rights reserved.
 *
 * This code is provided to you pursuant to your written agreement with Hortonworks, which may be the terms of the
 * Affero General Public License version 3 (AGPLv3), or pursuant to a written agreement with a third party authorized
 * to distribute this code.  If you do not have a written agreement with Hortonworks or with an authorized and
 * properly licensed third party, you do not have any rights to this code.
 *
 * If this code is provided to you under the terms of the AGPLv3:
 * (A) HORTONWORKS PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY KIND;
 * (B) HORTONWORKS DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT
 *   LIMITED TO IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE;
 * (C) HORTONWORKS IS NOT LIABLE TO YOU, AND WILL NOT DEFEND, INDEMNIFY, OR HOLD YOU HARMLESS FOR ANY CLAIMS ARISING
 *   FROM OR RELATED TO THE CODE; AND
 * (D) WITH RESPECT TO YOUR EXERCISE OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, HORTONWORKS IS NOT LIABLE FOR ANY
 *   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,
 *   DAMAGES RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF BUSINESS ADVANTAGE OR UNAVAILABILITY,
 *   OR LOSS OR CORRUPTION OF DATA.
 *
 */

import { Dag, KeyHash, Vertex, VertexEvent } from '../../../index';

let processIndex = 1;

export interface ProcessEvent {
  name: string;
  time: number;
}

export interface EventBar {
  fromEvent: string;
  toEvent: string;
  color?: string;
}

export interface ToolTipProp {
  name: string;
  value: string | number;
  type?: string;
}

export interface TooltipContent {
  title?: string | null;
  description?: string;
  properties?: ToolTipProp[];
}

interface ProcessColor {
  l: number;
  h: number;
  s: number;
}

type VertexEdge = KeyHash<string>;

export interface VertexEventInternal {
  name: string;
  time: number;
  edge?: VertexEdge;
  info?: KeyHash<unknown>;
}

export default class VertexProcess {
  _id = '';

  index = 0;
  color: ProcessColor | null = null;

  blockers: VertexProcess[] = []; // Array of processes that's blocking the current process
  blocking: VertexProcess[] = []; // Array of processes blocked by the current process

  vertex: Vertex;
  name: string;
  completeTime: number;

  blockingEventName = 'VERTEX_FINISHED';

  edgeHash: KeyHash<VertexEdge>;

  eventBars: EventBar[] = [
    {
      fromEvent: 'FIRST_TASK_STARTED',
      toEvent: 'LAST_TASK_FINISHED'
    },
    {
      fromEvent: 'DEPENDENT_VERTICES_COMPLETE',
      toEvent: 'LAST_TASK_FINISHED'
    }
  ];

  constructor(vertex: Vertex) {
    this._id = `process-id-${processIndex}`;
    processIndex++;

    this.vertex = vertex;
    this.name = vertex.name;
    this.completeTime = vertex.endTime;
    this.edgeHash = {};
  }

  getColor(lightnessFactor: number | undefined = undefined): string {
    const color = this.color;
    let l;

    if (!color) {
      return '#0';
    }
    l = color.l;
    if (lightnessFactor !== undefined) {
      l += 5 + 25 * lightnessFactor;
    }
    return `hsl( ${color.h}, ${color.s}%, ${l}% )`;
  }

  getBarColor(barIndex: number): string {
    const barCount = this.eventBars.length || 1;
    return this.getColor(1 - barIndex / barCount);
  }

  // Watch : "events.@each.time"
  get startEvent(): ProcessEvent | undefined {
    let startEvent: ProcessEvent | undefined = undefined;
    if (this.events) {
      startEvent = this.events[0];
      this.events.forEach(event => {
        if (startEvent && startEvent.time > event.time) {
          startEvent = event;
        }
      });
    }
    return startEvent;
  }

  // Watch : "events.@each.time"
  get endEvent(): ProcessEvent | undefined {
    let endEvent: ProcessEvent | undefined;
    if (this.events) {
      endEvent = this.events[this.events.length - 1];
      this.events.forEach(event => {
        if (endEvent && endEvent.time < event.time) {
          endEvent = event;
        }
      });
    }
    return endEvent;
  }

  get startTime(): number {
    return this.startEvent ? this.startEvent.time : 0;
  }

  get endTime(): number {
    return this.endEvent ? this.endEvent.time : 0;
  }

  getAllBlockers(parentHash: KeyHash<boolean> = {}): VertexProcess[] {
    const blockers: VertexProcess[] = [];
    const currentId = this._id;

    parentHash = parentHash || {}; // To keep a check on cyclic blockers

    parentHash[currentId] = true;
    if (this.blockers.length) {
      this.blockers.forEach(blocker => {
        if (!parentHash[blocker._id]) {
          blockers.push(blocker);
          blockers.push(...blocker.getAllBlockers(parentHash));
        }
      });
    }
    parentHash[currentId] = false;

    return blockers;
  }

  // Watch : "vertex.events.@each.timestamp"
  get eventsHash(): KeyHash<VertexEventInternal> {
    const events: KeyHash<VertexEventInternal> = {};
    const eventsArr = this.vertex.events;

    if (eventsArr) {
      eventsArr.forEach((event: VertexEvent) => {
        if (event.timestamp > 0) {
          events[event.eventtype] = {
            name: event.eventtype,
            time: event.timestamp,
            info: event.eventinfo
          };
        }
      });
    }

    return events;
  }

  // Watch : "eventsHash", "vertex.initTime", "vertex.startTime", "vertex.endTime", "vertex.firstTaskStartTime", "vertex.lastTaskFinishTime", "unblockDetails"
  get events(): VertexEventInternal[] {
    const eventsHash = this.eventsHash;

    const initTime = this.vertex.initRequestedTime;
    const startTime = this.vertex.startTime;
    const endTime = this.vertex.endTime;

    const firstTaskStartTime = this.vertex.stats.firstTaskStartTime;
    const lastTaskFinishTime = this.vertex.stats.lastTaskFinishTime;
    const unblockDetails = this.unblockDetails;

    if (initTime > 0) {
      eventsHash['VERTEX_INITIALIZED'] = {
        name: 'VERTEX_INITIALIZED',
        time: initTime
      };
    }

    if (startTime > 0) {
      eventsHash['VERTEX_STARTED'] = {
        name: 'VERTEX_STARTED',
        time: startTime
      };
    }

    if (firstTaskStartTime > 0) {
      eventsHash['FIRST_TASK_STARTED'] = {
        name: 'FIRST_TASK_STARTED',
        time: firstTaskStartTime
      };
    }

    if (unblockDetails && unblockDetails.time >= firstTaskStartTime) {
      eventsHash['DEPENDENT_VERTICES_COMPLETE'] = {
        name: 'DEPENDENT_VERTICES_COMPLETE',
        time: unblockDetails.time,
        edge: unblockDetails.edge
      };
    }

    if (lastTaskFinishTime > 0) {
      eventsHash['LAST_TASK_FINISHED'] = {
        name: 'LAST_TASK_FINISHED',
        time: lastTaskFinishTime
      };
    }

    if (endTime > 0) {
      eventsHash['VERTEX_FINISHED'] = {
        name: 'VERTEX_FINISHED',
        time: endTime
      };
    }

    return Object.values(eventsHash);
  }

  // Watch : "blockers.@each.completeTime"
  get unblockDetails(): { time: number; edge: VertexEdge } | undefined {
    const data: { time: number; blocker: VertexProcess | undefined } = {
      time: 0,
      blocker: undefined
    };

    if (this.blockers) {
      this.blockers.forEach(currentBlocker => {
        const blockerComplete = currentBlocker.completeTime;

        if (!blockerComplete) {
          data.blocker = undefined;
          return false;
        } else if (blockerComplete > data.time) {
          data.blocker = currentBlocker;
          data.time = blockerComplete;
        }

        return true;
      });
    }

    if (data.blocker) {
      return {
        time: data.blocker.completeTime,
        edge: this.edgeHash[data.blocker.name]
      };
    }
  }

  getTipProperties(propHash: KeyHash<unknown>, propArray: ToolTipProp[]): ToolTipProp[] {
    propArray = propArray || [];

    Object.keys(propHash).forEach((key: string) => {
      const value = propHash[key];

      switch (typeof value) {
        case 'string':
          propArray.push({
            name: key,
            value: value
          });
          break;
        case 'number':
          propArray.push({
            name: key,
            value: value,
            type: 'number'
          });
      }
    });

    return propArray;
  }

  getTooltipContents(
    type: string,
    options: { contribution: number; events: VertexEventInternal[] }
  ): TooltipContent[] | null {
    let contents: TooltipContent[] | null = null;
    let vertexDescription;

    switch (type) {
      case 'consolidated-process':
        vertexDescription = `Contribution ${options.contribution}%`;
      /* falls through */
      case 'process-name':
      case 'event-bar':
      case 'process-line':
        let properties: ToolTipProp[] = [];
        const vertex = this.vertex;

        if (vertex != null) {
          properties = [
            {
              name: 'Status',
              value: vertex.status
            },
            {
              name: 'Start Time',
              value: vertex.startTime,
              type: 'time'
            },
            {
              name: 'End Time',
              value: vertex.endTime,
              type: 'time'
            },
            {
              name: 'Duration',
              value: vertex.endTime ? vertex.endTime - vertex.startTime + 'ms' : '-',
              type: 'duration'
            },
            {
              name: 'Total Tasks',
              value: vertex.taskCount
            },
            {
              name: 'Succeeded Tasks',
              value: vertex.succeededTaskCount
            }
          ];
        }

        contents = [
          {
            title: this.name,
            properties: properties,
            description: vertexDescription
          }
        ];
        break;
      case 'event':
        let edge: VertexEdge = {};
        contents = options.events.map((event: VertexEventInternal) => {
          let properties: ToolTipProp[] = [
            {
              name: 'Time',
              value: event.time,
              type: 'time'
            }
          ];

          if (event.edge) {
            edge = event.edge;
          }
          if (event.info) {
            properties = this.getTipProperties(event.info, properties);
          }

          return {
            title: event.name,
            properties: properties
          };
        }, this);

        if (edge != null) {
          const sourceClass: string = edge.edgeSourceClass || '';
          const destClass: string = edge.edgeDestinationClass || '';

          contents.push({
            title: 'Edge From Final Dependent Vertex',
            properties: this.getTipProperties(
              {
                'Input Vertex': edge.inputVertexName,
                'Output Vertex': edge.outputVertexName,
                'Data Movement': edge.dataMovementType,
                'Data Source': edge.dataSourceType,
                Scheduling: edge.schedulingType,
                'Source Class': sourceClass.substr(sourceClass.lastIndexOf('.') + 1),
                'Destination Class': destClass.substr(destClass.lastIndexOf('.') + 1)
              },
              []
            )
          });
        }
        break;
    }

    return contents;
  }

  // Watch : "vertex.firstTaskStartTime", "unblockDetails.time"
  get consolidateStartTime(): number {
    return Math.max(
      this.vertex.stats.firstTaskStartTime || 0,
      (this.unblockDetails && this.unblockDetails.time) || 0
    );
  }
  // watch : "vertex.endTime"
  get consolidateEndTime(): number {
    return this.vertex.endTime;
  }

  getConsolidateColor(): string {
    return this.getBarColor(this.unblockDetails ? 1 : 0);
  }
}

export function createProcesses(dag: Dag): VertexProcess[] {
  const processes: VertexProcess[] = [];
  const processHash: KeyHash<VertexProcess> = {};

  if (dag) {
    const dagPlanEdges = dag.dagDetails.dagPlan.edges;

    // TODO : Create this from vertex entities list
    // Create process instances for each vertices
    dag.vertices.forEach((vertex: Vertex) => {
      const process = new VertexProcess(vertex);
      processHash[vertex.name] = process;
      processes.push(process);
    });

    // Add process(vertex) dependencies based on dagPlan
    if (dagPlanEdges) {
      dagPlanEdges.forEach((edge: KeyHash<string>) => {
        const process = processHash[edge.outputVertexName];
        if (process && processHash[edge.inputVertexName]) {
          process.blockers.push(processHash[edge.inputVertexName]);
          process.edgeHash[edge.inputVertexName] = edge;
        }
      });
    }
  }

  return processes;
}
