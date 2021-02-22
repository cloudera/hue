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

import { KeyHash } from '../../..';

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
  type: string;
}

export interface TooltipContent {
  title?: string | null;
  description?: string;
  properties?: ToolTipProp[];
}

export default class Process {
  _id = '';

  name = null;
  eventBars: EventBar[] = [];

  events: ProcessEvent[] = [];

  index = 0;
  color = null;

  blockers: Process[] = []; // Array of processes that's blocking the current process
  blocking: Process[] = []; // Array of processes blocked by the current process

  blockingEventName = null;

  constructor() {
    this._id = `process-id-${processIndex}`;
    processIndex++;
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

  getConsolidateColor(): string {
    return this.getColor();
  }

  get consolidateStartTime(): number {
    const event: ProcessEvent | undefined = this.startEvent;
    return event ? event.time : 0;
  }

  get consolidateEndTime(): number {
    const event: ProcessEvent | undefined = this.endEvent;
    return event ? event.time : 0;
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

  getAllBlockers(parentHash: KeyHash<boolean> = {}): Process[] {
    const blockers: Process[] = [];
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

  getTooltipContents(type: string, options?: unknown): TooltipContent[] {
    return [
      {
        title: this.name,
        description: 'Mouse on : ' + type + options
      }
    ];
  }
}
