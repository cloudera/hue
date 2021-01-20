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

/* eslint-disable  @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/explicit-module-boundary-types*/
/* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

import Process from './Process';
import { Dag } from '../../../index';

export default class VertexProcess extends Process {
  vertex = null;
  name: string;
  completeTime: number;

  blockingEventName = 'VERTEX_FINISHED';

  edgeHash: any;

  eventBars = [
    {
      fromEvent: 'FIRST_TASK_STARTED',
      toEvent: 'LAST_TASK_FINISHED'
    },
    {
      fromEvent: 'DEPENDENT_VERTICES_COMPLETE',
      toEvent: 'LAST_TASK_FINISHED'
    }
  ];

  constructor(vertex: any) {
    super();

    this.vertex = vertex;
    this.name = vertex.name;
    this.completeTime = vertex.endTime;
    this.edgeHash = {};
  }

  // Watch : "vertex.events.@each.timestamp"
  get eventsHash(): any {
    const events = {};
    const eventsArr = this.vertex.events;

    if (eventsArr) {
      eventsArr.forEach((event: any) => {
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
  get events(): any[] {
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
  get unblockDetails(): any {
    const data = {
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

  getTipProperties(propHash: any, propArray: any[]): any[] {
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

  getTooltipContents(type: string, options: any): any {
    let contents;
    let vertexDescription;

    switch (type) {
      case 'consolidated-process':
        vertexDescription = `Contribution ${options.contribution}%`;
      /* falls through */
      case 'process-name':
      case 'event-bar':
      case 'process-line':
        let properties: any[] = [];
        const vertex: any = this.vertex;

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
        let edge: any;
        contents = options.events.map(function (event: any) {
          let properties = [
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

        if (edge) {
          const sourceClass = edge.edgeSourceClass || '';
          const destClass = edge.edgeDestinationClass || '';

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

export function createProcesses(dag: Dag): Process[] {
  const processes: Process[] = [];
  const processHash: any = {};

  if (dag) {
    const dagPlanEdges = dag.dagDetails.dagPlan.edges;

    // TODO : Create this from vertex entities list
    // Create process instances for each vertices
    dag.vertices.forEach((vertex: any) => {
      const process = new VertexProcess(vertex, () => this.visibleColumns, []);
      processHash[vertex.name] = process;
      processes.push(process);
    });

    // Add process(vertex) dependencies based on dagPlan
    if (dagPlanEdges) {
      dagPlanEdges.forEach((edge: any) => {
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
