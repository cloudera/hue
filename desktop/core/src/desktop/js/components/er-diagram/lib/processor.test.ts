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

import { groupEntities } from './processor';
import { createTables } from '../test/utils';

describe('processor UTs', () => {
  test('Multiple unrelated entities (t0, t1, t2, t3, t4)', () => {
    const tableCount = 5;

    const entityGroups = groupEntities(createTables(tableCount, 0), []);

    expect(entityGroups).toHaveLength(5);
    expect(entityGroups.flat()).toHaveLength(tableCount);
  });

  test('Related entities - Linked list (t0-t1-t2-t3-t4)', () => {
    const tableCount = 5;

    const tables = createTables(tableCount, 2);
    const entityGroups = groupEntities(tables, [
      {
        desc: '',
        left: tables[0].columns[1],
        right: tables[1].columns[0]
      },
      {
        desc: '',
        left: tables[1].columns[1],
        right: tables[2].columns[0]
      },
      {
        desc: '',
        left: tables[2].columns[1],
        right: tables[3].columns[0]
      },
      {
        desc: '',
        left: tables[3].columns[1],
        right: tables[4].columns[0]
      }
    ]);

    expect(entityGroups).toHaveLength(5);
    expect(entityGroups.flat()).toHaveLength(tableCount);
  });

  test('Related entities - Binary tree (t0-t1, t0-t2, t2-t3, t2-t4)', () => {
    const tableCount = 5;

    const tables = createTables(tableCount, 3);
    const entityGroups = groupEntities(tables, [
      {
        desc: '',
        left: tables[0].columns[1],
        right: tables[1].columns[0]
      },
      {
        desc: '',
        left: tables[0].columns[2],
        right: tables[2].columns[0]
      },
      {
        desc: '',
        left: tables[2].columns[1],
        right: tables[3].columns[0]
      },
      {
        desc: '',
        left: tables[2].columns[2],
        right: tables[4].columns[0]
      }
    ]);

    expect(entityGroups).toHaveLength(3);
    expect(entityGroups.flat()).toHaveLength(tableCount);
  });

  test('Related entities - Graph (t0-t1, t0-t2, t2-t3, t2-t4, t3-t0, t4-t0)', () => {
    // Adding back links in the above binary tree to simulate graph
    const tableCount = 5;

    const tables = createTables(tableCount, 3);
    const entityGroups = groupEntities(tables, [
      {
        desc: '',
        left: tables[0].columns[1],
        right: tables[1].columns[0]
      },
      {
        desc: '',
        left: tables[0].columns[2],
        right: tables[2].columns[0]
      },
      {
        desc: '',
        left: tables[2].columns[1],
        right: tables[3].columns[0]
      },
      {
        // Back link - 1
        desc: '',
        left: tables[3].columns[1],
        right: tables[0].columns[0]
      },
      {
        desc: '',
        left: tables[2].columns[2],
        right: tables[4].columns[0]
      },
      {
        // Back link - 2
        desc: '',
        left: tables[4].columns[2],
        right: tables[0].columns[0]
      }
    ]);

    expect(entityGroups).toHaveLength(3);
    expect(entityGroups.flat()).toHaveLength(tableCount);
  });

  test('Related entities - Self relation (t0-t0, t1)', () => {
    const tableCount = 2;

    const tables = createTables(tableCount, 2);
    const entityGroups = groupEntities(tables, [
      {
        desc: '',
        left: tables[0].columns[1],
        right: tables[0].columns[0]
      }
    ]);

    expect(entityGroups).toHaveLength(2);
    expect(entityGroups.flat()).toHaveLength(tableCount);
  });

  test('Related entities - Self relation + external reference (t0-t0, t0-t1)', () => {
    const tableCount = 2;

    const tables = createTables(tableCount, 3);
    const entityGroups = groupEntities(tables, [
      {
        desc: '',
        left: tables[0].columns[1],
        right: tables[0].columns[0]
      },
      {
        desc: '',
        left: tables[0].columns[2],
        right: tables[1].columns[0]
      }
    ]);

    expect(entityGroups).toHaveLength(2);
    expect(entityGroups.flat()).toHaveLength(tableCount);
  });

  test('Related entities - Cyclic relation (t0-t1, t1-t0)', () => {
    const tableCount = 2;

    const tables = createTables(tableCount, 3);
    const entityGroups = groupEntities(tables, [
      {
        desc: '',
        left: tables[0].columns[1],
        right: tables[1].columns[0]
      },
      {
        desc: '',
        left: tables[1].columns[1],
        right: tables[0].columns[0]
      }
    ]);

    expect(entityGroups).toHaveLength(2);
    expect(entityGroups.flat()).toHaveLength(tableCount);
  });

  test('Unrelated entity groups (t0-t1, t2-t3, t2-t4)', () => {
    const tableCount = 5;

    const tables = createTables(tableCount, 2);
    const entityGroups = groupEntities(tables, [
      {
        desc: '',
        left: tables[0].columns[1],
        right: tables[1].columns[0]
      },
      {
        desc: '',
        left: tables[2].columns[1],
        right: tables[3].columns[0]
      },
      {
        desc: '',
        left: tables[2].columns[1],
        right: tables[4].columns[0]
      }
    ]);

    expect(entityGroups).toHaveLength(4);
    expect(entityGroups.flat()).toHaveLength(tableCount);
  });
});
