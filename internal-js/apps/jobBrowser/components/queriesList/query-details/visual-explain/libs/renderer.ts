/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import d3 from 'd3v3';

export default function doRender(
  data: any,
  containerElement: HTMLElement,
  onRequestDetail: any,
): void {
  const width = '100%';
  const height = '400';

  const isSingleReducer = isSingleReducerAvailable(data);

  d3.select(containerElement).select('*').remove();

  const svg = d3.select(containerElement).append('svg').attr('width', width).attr('height', height);
  const container = svg.append('g');
  const containerNode: HTMLElement = container.node();

  const drag = d3.behavior.drag().on('drag', () => {
    const x = parseInt(containerNode.dataset.x || '0') + d3.event.dx;
    const y = parseInt(containerNode.dataset.y || '0') + d3.event.dy;
    containerNode.dataset.x = x;
    containerNode.dataset.y = y;
    container.attr('transform', 'translate(' + [x, y] + ')');
  });

  svg.call(drag);

  const root = container
    .selectAll('g.vertex')
    .data([data.tree])
    .enter()
    .append('g')
    .attr('class', 'vertex')
    .attr('data-vertex', (d: any) => d._vertex);

  root.call(recurseC, onRequestDetail, isSingleReducer);
  root.call(recurseV, onRequestDetail, isSingleReducer);

  container
    .selectAll('path.edge')
    .data(data.connections)
    .enter()
    .insert('path', ':first-child')
    .attr('class', 'edge')
    .attr('d', (d: any) => getConnectionPath(d, svg, container, data));

  root
    .selectAll('path.arrow')
    .data(data.connections)
    .enter()
    .insert('path')
    .attr('class', 'arrow')
    .style('stroke-width', (d: any) => {
      return Math.sqrt(d.value);
    })
    .attr('d', (d: any) => getConnectionPathArrow(d, svg, container));

  alignGraph(container, svg);
}

function alignGraph(container: any, svg: any): void {
  const containerNode = container.node();
  const bound = containerNode.getBoundingClientRect();
  const svgBound = svg.node().getBoundingClientRect();

  const x = svgBound.x - bound.x + 20;
  const y = svgBound.y - bound.y + 20;

  containerNode.dataset.x = x;
  containerNode.dataset.y = y;

  container.attr('transform', 'translate(' + [x, y] + ')');
}

function isSingleReducerAvailable(data: any): boolean {
  const reducerCount = data.verticesData.filter((item: any) => {
    return item['_vertex'].indexOf('Reducer') === 0;
  });
  if (reducerCount && reducerCount.length === 1) {
    return true;
  }
  return false;
}

function recurseV(vertices: any, onRequestDetail: any, isSingleReducer: boolean): void {
  vertices.each(function (cVertx: any): void {
    const vertex = d3.select(this);

    const vertices = vertex
      .selectAll('g.vertex')
      .data((d: any) => d._vertices)
      .enter()
      .append('g')
      .attr('class', 'vertex')
      .attr('data-vertex', (d: any) => d._vertex)
      .style(
        'transform',
        (d: any) => `translate(${d._widthOfSelf * 200}px, ${d._offsetY * 100}px)`
      );

    vertices.call(recurseC, onRequestDetail, isSingleReducer);
    vertices.call(recurseV, onRequestDetail, isSingleReducer);
  });
}

function recurseC(children: any, onRequestDetail: any, isSingleReducer: boolean): void {
  children.each(function (d: any): void {
    const child = d3.select(this);

    const children = child
      .selectAll('g.child')
      .data((d: any) => d._children || [])
      .enter()
      .append('g')
      .attr('class', 'child')
      .style('transform', (d: any, index: number) => `translate(-${200}px, ${index * 100}px)`);

    children
      .append('rect')
      .attr('id', (d: any) => d._uuid)
      .attr('data-operator', (d: any) => d._operator)
      .attr(
        'class',
        (d: any) => `operator__box operator__box--${d._operator.toString().replace(/[ ]/g, '_')}`
      )
      .attr('height', (d: any) => (d._operator === 'Fetch Operator' ? 55 : 55))
      .attr('width', 140);

    children
      .append('foreignObject')
      .attr('data-uuid', (d: any) => d._uuid)
      .attr('data-operator', (d: any) => d._operator)
      .style('cursor', 'pointer')
      .attr(
        'class',
        (d: any) => `operator operator--${d._operator.toString().replace(/[ ]/g, '_')}`
      )
      .attr('height', (d: any) => (d._operator === 'Fetch Operator' ? 55 : 55))
      .attr('width', 140)
      .append('xhtml:div')
      .style('height', (d: any) => (d._operator === 'Fetch Operator' ? '55px' : 'auto'))
      .style('margin', 0)
      .style('padding', '5px')
      .html((d: any) => getRenderer(d._operator, isSingleReducer)(d))
      .on('click', function (d: any): void {
        let classNames = $('[uniqueid=visualexp-selected]').attr('class');
        if (classNames) {
          classNames = classNames.replace('visualexp-selected', '');
          $('[uniqueid=visualexp-selected]').attr('class', classNames);
          $('[uniqueid=visualexp-selected]').attr('uniqueid', '');
        }
        classNames = $('rect#' + d._uuid).attr('class');
        $('rect#' + d._uuid).attr('class', classNames + ' visualexp-selected');
        $('rect#' + d._uuid).attr('uniqueId', 'visualexp-selected');
        const vertex = d3.select($(d3.select(this).node()).closest('.vertex').get(0)).data()[0];
        onRequestDetail(doClean(d), vertex);
      });

    children.call(recurseC, onRequestDetail, isSingleReducer);
  });
}

function getRenderer(type: string, isSingleReducer: boolean): any {
  if (type === 'Fetch Operator') {
    return (d: any) => {
      return `
        <div style='display:flex;align-items: center; pointer-events: none;'>
          <div class='operator-meta'>
            <i class='fa ${getOperatorIcon(d._operator)}' aria-hidden='true'></i>
          </div>
          <div class='operator-body' style='margin-left: 10px;'>
            <div class="ellipsis-node" title="${getOperatorLabel(
              d,
              isSingleReducer
            )}">${getOperatorLabel(d, isSingleReducer)}</div>
            ${
              d['limit:'] && d['limit:'] > -1
                ? '<div><span class="operator-limit">Limit:</span> ' + d['limit:'] + ' </div>'
                : ''
            }
          </div>
        </div>
      `;
    };
  }

  return (d: any) => {
    let stats = '';
    if (d['Statistics:']) {
      if (d.counters) {
        const actualCount = abbreviate(d.counters.recordsOut);
        const estimatedCount = abbreviate(getNumberOfRows(d['Statistics:']));
        stats = `<div title='Actual: ${actualCount}, Estimated: ${estimatedCount}'><span class='operator-limit'>Rows:</span> ${actualCount}/${estimatedCount}</div>`;
      } else {
        const estimatedCount = abbreviate(getNumberOfRows(d['Statistics:']));
        stats = `<div title='Estimated rows: ${estimatedCount}'><span class='operator-limit'>Rows:</span> ${estimatedCount}</div>`;
      }
    }

    return `
      <div style='display:flex;'>
        <div class='operator-meta'>
          <i class='fa ${getOperatorIcon(d._operator)}' aria-hidden='true'></i>
        </div>
        <div class='operator-body' style='margin-left: 10px;'>
          <div class="ellipsis-node" title="${getOperatorLabel(
            d,
            isSingleReducer
          )}">${getOperatorLabel(d, isSingleReducer)}</div>
          ${stats}
        </div>
      </div>
    `;
  };
}

function getNumberOfRows(statistics: string): number {
  const match = statistics.match(/([^\?]*)\Num rows: (\d*)/) || [];
  return match.length === 3 && Number.isNaN(Number(match[2])) === false ? parseFloat(match[2]) : 0;
}

function getOperatorLabel(d: any, isSingleReducer: boolean): string {
  const operator = d._operator;
  if (operator === 'Partition/Sort Pseudo-Edge' && isSingleReducer) {
    return 'Sort';
  }
  if (operator === 'TableScan') {
    return d['alias:'];
  }

  const operatorStr = operator.toString();

  if (operatorStr.indexOf('Map Join Operator') > -1) {
    return 'Hash Join';
  }
  if (operatorStr.endsWith(' Operator')) {
    return operatorStr.substring(0, operatorStr.length - ' Operator'.length);
  }
  if (operatorStr.endsWith(' Pseudo-Edge')) {
    return operatorStr.substring(0, operatorStr.length - ' Pseudo-Edge'.length);
  }
  return operatorStr ? operatorStr : 'Unknown';
}

function getOperatorIcon(operator: any): string {
  switch (operator) {
    case 'File Output Operator':
      return 'fa-file-o';
    case 'Partition/Sort Pseudo-Edge':
    case 'Broadcast Pseudo-Edge':
    case 'Partition Pseudo-Edge':
    case 'Co-partition Pseudo-Edge':
    case 'Cross-product Distribute Pseudo-Edge':
    case 'Reduce Output Operator':
      return 'fa-compress';
    case 'Filter Operator':
      return 'fa-filter';
    case 'Dynamic Partitioning Event Operator':
      return 'fa-columns';
    case 'Map Join Operator':
      return 'fa-code-fork';
    case 'Limit':
    case 'Group By Operator':
    case 'Select Operator':
    case 'TableScan':
    case 'Fetch Operator':
      return 'fa-table';
    default:
      return '';
  }
}

function getIcon(type: string): string {
  switch (type) {
    case 'join':
      return 'fa-code-fork';
    case 'vectorization':
    case 'job':
      return '';
    case 'broadcast':
    case 'partition-sort':
      return 'fa-compress';
    case 'source':
    case 'sink':
    case 'group-by':
    case 'select':
      return 'fa-table';
  }
  return '';
}

function abbreviate(value: number): string {
  let newValue = '' + value;
  if (value >= 1000) {
    const suffixes = ['', 'k', 'm', 'b', 't'];
    const suffixNum = Math.floor(('' + value).length / 3);
    let shortValue = 0;
    for (let precision = 2; precision >= 1; precision--) {
      shortValue = parseFloat(
        (suffixNum !== 0 ? value / Math.pow(1000, suffixNum) : value).toPrecision(precision)
      );
      const dotLessShortValue = (shortValue + '').replace(/[^a-zA-Z 0-9]+/g, '');
      if (dotLessShortValue.length <= 2) {
        break;
      }
    }
    newValue = shortValue + suffixes[suffixNum];
  }
  return newValue;
}

// function reset(zoom: any, svg: any, container: any, data: any) {
//   const vertices = container.selectAll('g.vertex');
//   const bounds: any[] = [];

//   vertices.each(function (d: any): void {
//     const cVertex = d3.select(this);
//     const box = cVertex.node().getBoundingClientRect();
//     bounds.push(box);
//   });

//   const PADDING_PERCENT = 0.95;
//   const svgRect = svg.node().getBoundingClientRect();
//   const fullWidth = svgRect.width;
//   const fullHeight = svgRect.height;
//   const offsetY = svgRect.top;
//   const top = Math.min(...bounds.map(cBound => cBound.top));
//   const left = Math.min(...bounds.map(cBound => cBound.left));
//   const width = Math.max(...bounds.map(cBound => cBound.right)) - left;
//   const height = Math.max(...bounds.map(cBound => cBound.bottom)) - top;
//   const midX = left + width / 2;
//   const midY = top + height / 2;
//   if (width === 0 || height === 0) {
//     // nothing to fit
//     return;
//   }
//   const scale = PADDING_PERCENT / Math.max(width / fullWidth, height / fullHeight);
//   const translate = [fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY];

//   zoom.scale(scale).translate(translate);

//   svg.transition().delay(750).call(zoom.event);
// }

function getConnectionPath(connector: any, svg: any, container: any, data: any): string {
  const operators = container.selectAll('.operator');
  const source = container.select(`#${connector._source._uuid}`);
  const target = container.select(`#${connector._target._uuid}`);
  const rSource = source.node().getBoundingClientRect();
  const rTarget = target.node().getBoundingClientRect();

  const pSource = {
    x: (rSource.left + rSource.right) / 2,
    y: (rSource.top + rSource.bottom) / 2
  };
  const pTarget = {
    x: (rTarget.left + rTarget.right) / 2,
    y: (rTarget.top + rTarget.bottom) / 2
  };
  const path = [pTarget];
  const junctionXMultiplier = pTarget.x - pSource.x < 0 ? +1 : -1;
  const padding = 20;

  if (pSource.y !== pTarget.y) {
    path.push(
      {
        x: pTarget.x + junctionXMultiplier * 90,
        y: pTarget.y
      },
      {
        x: pTarget.x + junctionXMultiplier * 90,
        y: pSource.y
      }
    );
  }

  path.push(pSource);
  const offsetY = svg.node().getBoundingClientRect().top;
  const leftOffset = svg.node().getBoundingClientRect().left;
  let isEdgeReversed = false;
  let edgeReversalVal: any;

  return path.reduce((accumulator: any, cPoint: any, index: number) => {
    if (index === 0) {
      if (cPoint.x > cPoint.y - offsetY) {
        edgeReversalVal = cPoint.x;
        isEdgeReversed = true;
      }
      return accumulator + `M ${cPoint.x - leftOffset} , ${cPoint.y - offsetY}\n`;
    } else {
      if (
        isEdgeReversed &&
        path.length === 4 &&
        index !== path.length - 1 &&
        edgeReversalVal > cPoint.x
      ) {
        return accumulator + `L ${cPoint.x + 150 - leftOffset}, ${cPoint.y - offsetY}\n`;
      }
      return accumulator + `L ${cPoint.x - leftOffset}, ${cPoint.y - offsetY}\n`;
    }
  }, '');
}

function getConnectionPathArrow(connector: any, svg: any, container: any) {
  const operators = container.selectAll('.operator');
  const source = container.select(`#${connector._source._uuid}`);
  const target = container.select(`#${connector._target._uuid}`);
  const rSource = source.node().getBoundingClientRect();
  const rTarget = target.node().getBoundingClientRect();
  const pSource = {
    x: (rSource.left + rSource.right) / 2,
    y: (rSource.top + rSource.bottom) / 2
  };
  const pTarget = {
    x: (rTarget.left + rTarget.right) / 2,
    y: (rTarget.top + rTarget.bottom) / 2
  };
  const path = [pTarget];
  const junctionXMultiplier = pTarget.x - pSource.x < 0 ? +1 : -1;
  if (pSource.y !== pTarget.y) {
    path.push(
      {
        x: pTarget.x + junctionXMultiplier * 90,
        y: pTarget.y
      },
      {
        x: pTarget.x + junctionXMultiplier * 90,
        y: pSource.y
      }
    );
  }
  path.push(pSource);
  const offsetY = svg.node().getBoundingClientRect().top;
  const leftOffset = svg.node().getBoundingClientRect().left;
  const arrowOffset = 20;
  let arrowClosure = 0;

  if (Math.floor((arrowOffset / 140) * 15) % 10 >= 5) {
    arrowClosure =
      Math.round(
        100 -
          (Math.floor((arrowOffset / 140) * 15) +
            (10 - (Math.floor((arrowOffset / 140) * 15) % 10)))
      ) - 5;
  } else {
    arrowClosure =
      Math.round(
        100 - (Math.floor((arrowOffset / 140) * 15) - (Math.floor((arrowOffset / 140) * 15) % 10))
      ) - 5;
  }

  return path.reduce((accumulator: any, cPoint: any, index: number) => {
    const tempOffset = cPoint.x - arrowOffset - leftOffset;
    const temp = tempOffset + arrowClosure;

    if (path.length === 2) {
      if (index === 0) {
        if (cPoint.x > 0) {
          return (
            accumulator +
            `M ${temp}, ${cPoint.y - offsetY - 7} V 0, ${
              ((cPoint.y - offsetY - 15) / 100) * 100 + 23
            }  L ${temp - 5}, ${cPoint.y - offsetY} Z\n`
          );
        } else {
          return (
            accumulator +
            `M ${temp}, ${cPoint.y - offsetY - 7} V 0, ${
              ((cPoint.y - offsetY - 15) / 100) * 100 + 23
            }  L ${temp - 5}, ${cPoint.y - offsetY} Z\n`
          );
        }
      } else {
        return accumulator;
      }
    } else if (index === 0) {
      if (cPoint.x > 0) {
        return (
          accumulator +
          `M ${temp}, ${cPoint.y - offsetY - 7} V 0, ${
            ((cPoint.y - offsetY - 15) / 100) * 100 + 23
          } L ${temp - 5}, ${cPoint.y - offsetY} Z\n`
        );
      } else {
        return (
          accumulator +
          `M ${temp}, ${cPoint.y - offsetY + 9} V 0, 67 L ${temp - 5}, ${cPoint.y - offsetY} Z\n`
        );
      }
    } else {
      return accumulator;
    }
  }, '');
}

function doClean(node: any): any {
  if (Array.isArray(node._groups)) {
    return node._groups.map((cGroup: any) => doClean(cGroup));
  } else {
    return Object.keys(node)
      .filter(cNodeKey => cNodeKey === '_operator' || !cNodeKey.startsWith('_'))
      .reduce((accumulator: any, cNodeKey: string) => {
        accumulator[cNodeKey] = node[cNodeKey];
        return accumulator;
      }, {});
  }
}
