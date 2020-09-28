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

/* eslint-disable  @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

export function getProcessedVertices(vertices: any[], edges: any[]): any[] {
  const edgedVertices = processEdges(vertices, edges);
  return processSource(edgedVertices);
}

function processEdges(vertices: any[], edges: any[]): any[] {
  return vertices.map(cVertex => {
    const isVertexPartOfSimpleEdge = edges.some(
      cEdge => cEdge.type === 'SIMPLE_EDGE' && cEdge._source === cVertex._vertex
    );
    const isVertexPartOfBroadcastEdge = edges.some(
      cEdge => cEdge.type === 'BROADCAST_EDGE' && cEdge._source === cVertex._vertex
    );
    const isVertexPartOfCustomSimpleEdge = edges.some(
      cEdge => cEdge.type === 'CUSTOM_SIMPLE_EDGE' && cEdge._source === cVertex._vertex
    );
    const isVertexPartOfCustomEdge = edges.some(
      cEdge => cEdge.type === 'CUSTOM_EDGE' && cEdge._source === cVertex._vertex
    );
    const isVertexPartOfXProdEdge = edges.some(
      cEdge => cEdge.type === 'XPROD_EDGE' && cEdge._source === cVertex._vertex
    );
    const isVertexPartOfUnionEdge = edges.some(
      cEdge => cEdge.type === 'CONTAINS' && cEdge._source === cVertex._vertex
    );

    let tVertex = cVertex;

    if (isVertexPartOfSimpleEdge) {
      tVertex = appendIfTerminusOfOperator(tVertex, {
        _operator: 'Partition/Sort Pseudo-Edge'
      });
    }
    if (isVertexPartOfBroadcastEdge) {
      tVertex = appendIfTerminusOfOperator(tVertex, {
        _operator: 'Broadcast Pseudo-Edge'
      });
    }
    if (isVertexPartOfCustomSimpleEdge) {
      tVertex = appendIfTerminusOfOperator(tVertex, {
        _operator: 'Partition Pseudo-Edge'
      });
    }
    if (isVertexPartOfCustomEdge) {
      tVertex = appendIfTerminusOfOperator(tVertex, {
        _operator: 'Co-partition Pseudo-Edge'
      });
    }
    if (isVertexPartOfXProdEdge) {
      tVertex = appendIfTerminusOfOperator(tVertex, {
        _operator: 'Cross-product Distribute Pseudo-Edge'
      });
    }
    if (isVertexPartOfUnionEdge) {
      tVertex = appendIfTerminusOfOperator(tVertex, {
        _operator: 'Partition/Sort Pseudo-Edge'
      });
    }

    return tVertex;
  });
}

function appendIfTerminusOfOperator(node: any, pseudoNode: any): any {
  if (Array.isArray(node._children) === false || node._children.length === 0) {
    // is terminus
    switch (node._operator) {
      case 'Reduce Output Operator':
        return Object.assign({}, node, pseudoNode);
      default:
        return node;
    }
  }

  return Object.assign({}, node, {
    _children: node._children.map((cChild: any) => appendIfTerminusOfOperator(cChild, pseudoNode))
  });
}

function processSource(vertices: any[]): any[] {
  return vertices.map((cVertex: any) =>
    Object.assign({}, cVertex, {
      _children: cVertex._children.map((cChild: any) => getProcessedSequenceViaStack(cChild))
    })
  );
}

// DANGER: impure function
function getProcessedSequenceViaStack(root): void {
  const stack = [];

  let cNode = root;
  stack.push(cNode);
  doCompaction(stack);
  while (cNode._children.length === 1) {
    cNode = cNode._children[0];

    stack.push(cNode);
    doCompaction(stack);
  }

  const lNode = stack[stack.length - 1];
  if (lNode._children.length > 1) {
    // begin processing new subtree
    lNode._children = lNode._children.map((cChild: any) => getProcessedSequenceViaStack(cChild));
  }

  return stack[0];
}

function doCompaction(stack: any[]): void {
  let index = stack.length;

  while (index > 0) {
    const cNode = stack[index - 0 - 1];
    const cNodeMinus1 = stack[index - 1 - 1];
    const cNodeMinus2 = stack[index - 2 - 1];
    const cNodeMinus3 = stack[index - 3 - 1];
    const cNodeMinus4 = stack[index - 4 - 1];

    if (cNodeMinus1) {
      if (
        cNode._operator === 'Select Operator' ||
        cNode._operator === 'HASHTABLEDUMMY' ||
        cNode._operator === 'File Output Operator'
      ) {
        // remove cNode from stack
        stack.pop();
        index--;
        // recreate groups
        cNodeMinus1._groups = [
          ...(cNodeMinus1._groups || [doCloneAndOmit(cNodeMinus1, ['_groups'])]),
          ...(cNode._groups || [doCloneAndOmit(cNode, ['_groups'])])
        ];
        // move children
        cNodeMinus1._children = cNode._children;

        continue;
      }
      if (
        cNodeMinus1._operator === 'Select Operator' ||
        cNodeMinus1._operator === 'HASHTABLEDUMMY' ||
        cNodeMinus1._operator === 'File Output Operator'
      ) {
        // remove cNode and cNodeMinus1 from stack
        stack.pop();
        index--;
        stack.pop();
        index--;

        // recreate groups
        cNode._groups = [
          ...(cNodeMinus1._groups || [doCloneAndOmit(cNodeMinus1, ['_groups'])]),
          ...(cNode._groups || [doCloneAndOmit(cNode, ['_groups'])])
        ];
        // no need to move chldren
        // reinsert cNode
        stack.push(cNode);
        index++;

        continue;
      }

      if (
        cNode._operator === 'Map Join Operator' &&
        cNodeMinus1._operator === 'Map Join Operator'
      ) {
        // remove cNode from stack
        stack.pop();
        index--;
        // recreate groups
        cNodeMinus1._groups = [
          ...(cNodeMinus1._groups || [doCloneAndOmit(cNodeMinus1, ['_groups'])]),
          ...(cNode._groups || [doCloneAndOmit(cNode, ['_groups'])])
        ];
        // move chldren
        cNodeMinus1._children = cNode._children;

        continue;
      }

      if (cNode._operator === 'Filter Operator' && cNodeMinus1._operator === 'TableScan') {
        // remove cNode from stack
        stack.pop();
        index--;
        // recreate groups
        cNodeMinus1._groups = [
          ...(cNodeMinus1._groups || [doCloneAndOmit(cNodeMinus1, ['_groups'])]),
          ...(cNode._groups || [doCloneAndOmit(cNode, ['_groups'])])
        ];
        // move children
        cNodeMinus1._children = cNode._children;

        continue;
      }

      if (cNodeMinus2 && cNodeMinus3) {
        if (
          cNode._operator === 'Broadcast Pseudo-Edge' &&
          cNodeMinus1._operator === 'Group By Operator' &&
          cNodeMinus2._operator === 'Reduce Output Operator' &&
          cNodeMinus3._operator === 'Group By Operator'
        ) {
          // remove cNode from stack
          stack.pop();
          index--;
          // remove cNodeMinus1 from stack
          stack.pop();
          index--;
          // remove cNodeMinus2 from stack
          stack.pop();
          index--;
          // remove cNodeMinus3 from stack
          stack.pop();
          index--;

          // recreate groups
          cNodeMinus1._groups = [
            ...(cNodeMinus3._groups || [doCloneAndOmit(cNodeMinus3, ['_groups'])]),
            ...(cNodeMinus2._groups || [doCloneAndOmit(cNodeMinus2, ['_groups'])]),
            ...(cNodeMinus1._groups || [doCloneAndOmit(cNodeMinus1, ['_groups'])])
          ];
          // move children if required, cNodeMinus1 as child of cNodeMinus4
          if (cNodeMinus4) {
            cNodeMinus4._children = cNodeMinus2._children;
          }
          // rename
          cNodeMinus1._operator = 'Build Bloom Filter';
          // add renamed node
          stack.push(cNodeMinus1);
          index++;
          // add original broadcast edge node
          stack.push(cNode);
          index++;
          continue;
        }
      }
    }
    index--;
  }
}

function doCloneAndOmit(obj: any, keys: string[]): void {
  return Object.keys(obj)
    .filter(cObjKey => keys.indexOf(cObjKey) === -1)
    .reduce(
      (tObj: any, cObjKey: string) =>
        Object.assign({}, tObj, {
          [cObjKey]: obj[cObjKey]
        }),
      {}
    );
}

export function getEdgesWithCorrectedUnion(edges: any[]): any[] {
  return edges.map((cEdge: any) => {
    if (cEdge.type === 'CONTAINS') {
      return Object.assign({}, cEdge, {
        _source: cEdge._target,
        _target: cEdge._source
      });
    } else {
      return cEdge;
    }
  });
}

// outputOperator: comes only with the plan in compose page and breaks the explain visualization, hence disabling
// function findAllOutputOperators(vertices, edges, patterns) {
//     vertices.forEach(cEdge => {
//       edges.push(cEdge);
//       let outputOperator = cEdge["outputOperator:"];
//       if(outputOperator && outputOperator.length) {
//         patterns.push({
//              outputOperator:outputOperator[0],
//              cEdge:[edges[edges.length-4],
//              edges[edges.length-3],
//              edges[edges.length-2],
//              edges[edges.length-1]]
//            });
//       }
//       findAllOutputOperators(cEdge._children, edges, patterns);
//     });
// }
function findAllOperatorsVertex(cEdge: any[], operatorIdList: any[], edgesOp: any[]): void {
  cEdge.forEach(cChild => {
    const operatorId = cChild['OperatorId:'];
    if (operatorId) {
      const operatorObj = {};
      operatorObj[operatorId] = cChild['_operator'];
      operatorIdList.push(operatorObj);
      edgesOp.push(cChild);
      if (edgesOp.length > 4) {
        edgesOp.pop();
      }
    }
    findAllOperatorsVertex(cChild._children, operatorIdList, edgesOp);
  });
}
function findTheOperatorIDChains(vertices, operatorIdList, edgesOp): void {
  vertices.forEach(cChild => {
    const subOperatorList = [];
    edgesOp = [];
    findAllOperatorsVertex(cChild._children, subOperatorList, edgesOp);
    operatorIdList.push({ subOperatorList, edgesOp });
  });
}

function findPatternParent(edges: any, patternArray: any[]): void {
  let newVertex;
  edges._children.forEach((cChild: any) => {
    cChild._children.forEach((cSubChild: any) => {
      if (cSubChild && cSubChild['OperatorId:'] === patternArray[0]['OperatorId:']) {
        if (cChild._children.length > 1) {
          cChild._children = [cChild._children[0]];
          cChild['outputOperator:'] = patternArray[1]['outputOperator:'];
          newVertex = Object.assign(patternArray[2], {
            _operator: 'Build Bloom Filter',
            _children: [],
            _groups: [
              ...(patternArray[0].groups || [doCloneAndOmit(patternArray[0], ['_groups'])]),
              ...(patternArray[1].groups || [doCloneAndOmit(patternArray[1], ['_groups'])]),
              ...(patternArray[2].groups || [doCloneAndOmit(patternArray[2], ['_groups'])]),
              ...(patternArray[3].groups || [doCloneAndOmit(patternArray[3], ['_groups'])])
            ]
          });
        }
      } else if (
        cSubChild &&
        patternArray[patternArray.length - 1] &&
        cSubChild['OperatorId:'] === patternArray[patternArray.length - 1]['OperatorId:']
      ) {
        cChild._children = newVertex ? [newVertex] : [];
      } else {
        findPatternParent(cChild, patternArray);
      }
    });
  });
}

function findTheOperatorIndex(vertices: any[], patternArray: any[]): void {
  vertices.forEach(cChild => {
    findPatternParent(cChild, patternArray);
  });
}

function setTheNewVertex(vertices: any[], patternArray: any[]): void {
  findTheOperatorIndex(vertices, patternArray);
}

function isPatternExists(outputOperators: any, operatorIds: any, vertices: any[]): void {
  const patternArray = [
    outputOperators.cEdge[2],
    outputOperators.cEdge[3],
    operatorIds.edgesOp[0],
    operatorIds.edgesOp[1]
  ];
  setTheNewVertex(vertices, patternArray);
}

function findPatterns(
  operatorIdList: any[],
  pattern: any[],
  patterns: any[],
  vertices: any[]
): void {
  patterns.forEach(item => {
    operatorIdList.forEach(operatorDetails => {
      operatorDetails.edgesOp.forEach(op => {
        if (op['OperatorId:'] === item.outputOperator) {
          pattern.push(op['OperatorId:']);
          isPatternExists(item, operatorDetails, vertices);
        }
      });
    });
  });
}

// DANGER: impure function
// DANGER: breaks if there is a many-one / one-many connection
export function getAdjustedVerticesAndEdges(vertices: any[], edges: any[]) {
  const operatorIdList = [];
  const pattern = [];
  const edges_operatorId = [];
  const patterns = [];
  // findAllOutputOperators(vertices, edges_opOperator, patterns);
  findTheOperatorIDChains(vertices, operatorIdList, edges_operatorId);
  findPatterns(operatorIdList, pattern, patterns, vertices);

  vertices
    .filter(
      cVertex =>
        ['Select Operator', 'HASHTABLEDUMMY', 'File Output Operator'].indexOf(
          getFirstOperatorOf(cVertex)._operator
        ) >= 0
    )
    .map(cVertex => edges.filter(cEdge => cEdge._target === cVertex._vertex))
    .forEach(cEdges => {
      const source = vertices.find(cVertex =>
        cEdges.some(tcEdge => cVertex._vertex === tcEdge._source)
      );
      const target = vertices.find(cVertex =>
        cEdges.some(tcEdge => cVertex._vertex === tcEdge._target)
      );

      const operatorLastOfSource = getLastOperatorOf(source);
      const operatorFirstOfTarget = getFirstOperatorOf(target);

      operatorLastOfSource._groups = [
        ...(operatorLastOfSource._groups || [doCloneAndOmit(operatorLastOfSource, ['_groups'])]),
        ...(operatorFirstOfTarget._groups || [doCloneAndOmit(operatorFirstOfTarget, ['_groups'])])
      ];
      target._children = operatorFirstOfTarget._children;

      target._isGroupedWith = source._vertex;
    });

  // cleanup
  const adjustedVertices = vertices.filter(cVertex => cVertex._children.length > 0);
  const cleanedVertices = vertices.filter(cVertex => cVertex._children.length === 0);

  const adjustedEdges = edges.reduce((accumulator, cEdge) => {
    const cleanedAtSourceVertex = cleanedVertices.find(
      cVertex => cEdge._source === cVertex._vertex
    );
    const cleanedAtTargetVertex = cleanedVertices.find(
      cVertex => cEdge._target === cVertex._vertex
    );

    if (cleanedAtSourceVertex) {
      // do not add edge back
      // add new edge instead
      accumulator.push(
        Object.assign({}, cEdge, {
          _source: cleanedAtSourceVertex._isGroupedWith,
          _target: cEdge._target
        })
      );
    } else if (cleanedAtTargetVertex) {
      // do not add edge back
    } else {
      accumulator.push(cEdge);
    }
    return accumulator;
  }, []);

  return {
    adjustedVertices,
    adjustedEdges
  };
}

function getLastOperatorOf(vertex) {
  let operator = vertex._children[0];
  while (operator._children.length > 0) {
    operator = operator._children[0];
  }
  return operator;
}

function getFirstOperatorOf(vertex) {
  return vertex._children[0];
}
