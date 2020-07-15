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

import { IEntity, IRelation } from './interfaces';
import { EntityTypes } from './enums';
import { Column } from './entities';

class EntityNode {
  entity: IEntity;
  level: number;
  relations: Array<EntityNode>;

  constructor(entity: IEntity) {
    this.entity = entity;
    this.relations = new Array<EntityNode>();
    this.level = 0;
  }
}

/**
 * To visualize the ERD in a more human-readable form - Entities will be grouped based on
 * it's level (Distance from root entity) in the relationship graph. entities[0] will be
 * taken as the root entity.
 */
export function groupEntities(
  entities: Array<IEntity>,
  relations: Array<IRelation>
): Array<Array<IEntity>> {
  const nodesMap: Map<string, EntityNode> = generateGraph(entities, relations);

  let level = 0;
  nodesMap.forEach((node: EntityNode) => {
    // To ensure levels are set even for disjoint graphs
    if (node.level === 0) {
      level = setLevels(node, level + 1);
    }
  });

  return breadthFirstTraverse(nodesMap);
}

function getNodeMapId(entity: IEntity) {
  if (entity.type === EntityTypes.Column) {
    return (entity as Column).tableId;
  }
  return entity.id;
}

function generateGraph(
  entities: Array<IEntity>,
  relations: Array<IRelation>
): Map<string, EntityNode> {
  const nodesMap = new Map<string, EntityNode>();

  entities.forEach((entity: IEntity) => {
    switch (entity.type) {
      // We now support only Table & Literal nodes, column will be shown inside Table
      case EntityTypes.Table:
      case EntityTypes.Literal:
        nodesMap.set(entity.id, new EntityNode(entity));
    }
  });

  relations.forEach((relation: IRelation) => {
    const leftEntity: EntityNode | undefined = nodesMap.get(getNodeMapId(relation.left));
    const rightEntity: EntityNode | undefined = nodesMap.get(getNodeMapId(relation.right));
    if (leftEntity && rightEntity) {
      leftEntity.relations.push(rightEntity);
    }
  });

  return nodesMap;
}

function setLevels(entityNode: EntityNode, level: number): number {
  let maxLevel = 0;
  if (entityNode.level === 0) {
    entityNode.level = level;
    maxLevel = level++;
    entityNode.relations.forEach((childNode: EntityNode) => {
      maxLevel = Math.max(maxLevel, setLevels(childNode, level));
    });
  }
  return maxLevel;
}

function breadthFirstTraverse(nodesMap: Map<string, EntityNode>): Array<Array<IEntity>> {
  const entities: Array<Array<IEntity>> = new Array<Array<IEntity>>();

  nodesMap.forEach((entityNode: EntityNode) => {
    const level = entityNode.level - 1;
    if (level >= 0) {
      if (entities[level] === undefined) {
        entities[level] = new Array<IEntity>();
      }
      entities[level].push(entityNode.entity);
    }
  });

  return entities;
}
