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
/* eslint-disable  @typescript-eslint/explicit-module-boundary-types*/

/**
 * The data processing part of Dag View.
 *
 * Converts raw DAG-plan into an internal data representation as shown below.
 * Data processor exposes just a functions and an enum to the outside world, everything else
 * happens inside the main closure:
 *   - types (Enum of node types) TODO: Once we bring in ES6 classes NodeType wont be required ---------------------------------------
 *   - graphifyData
 *
 * Links, Edges: TODO: Convert all to edges ------------------------------------------------------------------------------------------
 * --------------
 * d3 layout & graph-view uses the term links, and dag-plan uses edges. Hence you would
 * see both getting used in this file.
 *
 * Graphify Data
 * -------------
 *  graphifyData function is a translator that translates the dagPlan object
 *  into another object that graph-view and in turn d3.layout.tree can digest.
 *
 * Input object(Tez dag-plan as it is):
 *  {
 *    dagName, version,
 *    vertices: [ // Array of vertex objects with following properties
 *      {
 *        vertexName, processorClass, outEdgeIds {Array}, additionalInputs {Array}
 *      }
 *    ],
 *    edges: [ // Array of edge objects with following properties
 *      {
 *        edgeId, inputVertexName, outputVertexName, dataMovementType, dataSourceType
 *        schedulingType, edgeSourceClass, edgeDestinationClass
 *      }
 *    ],
 *    vertexGroups: [ // Array of vertexGroups objects with following properties
 *      {
 *        groupName, groupMembers {Array}, edgeMergedInputs {Array}
 *      }
 *    ]
 *  }
 *
 * Output object:
 *  We are having a graph that must be displayed like a tree. Hence data processor was created
 *  to make a tree structure out of the available data. The tree structure is made by creating
 *  DataNodes instances and populating their children array with respective child DataNodes
 *   - tree: Represents the tree structure with each node being a DataNodes instance
 *   - links: Represents the connections between the nodes to create the graph
 *    {
 *      tree: { // This object points to the RootDataNode instance
 *        children {Array} // Array of DataNodes under the node, as expected by d3.layout.tree
 *        + Other custom properties including data that needs to be displayed
 *      }
 *      links: [ // An array of all links in the tree
 *        {
 *          sourceId // Source vertex name
 *          targetId // Target vertex name
 *          + Other custom properties including data to be displayed
 *        }
 *      ]
 *      maxDepth, leafCount
 *    }
 *
 * Data Nodes:
 * -----------
 *  To make the implementation simpler each node in the graph will be represented as an
 *  instance of any of the 4 inherited classes of Data Node abstract class.
 *  DataNode
 *    |-- RootDataNode
 *    |-- VertexDataNode
 *    |-- InputDataNode
 *    +-- OutputDataNode
 *
 * Extra Nodes:
 * ------------
 * Root Node (Invisible):
 *  Dag view support very complex DAGs, even those without interconnections and backward links.
 *  Hence to fit it into a tree layout I have inserted an invisible root node.
 *
 * Dummy Node (Invisible):
 *  Sinks of a vertex are added at the same level of its parent node, Hence to ensure that all
 *  nodes come under the root, a dummy node was added as the child of the root. The visible tree
 *  would be added as child of dummy node.
 *  Dummy also ensures the view symmetry when multiple outputs are present at the dummy level.
 *
 * Sample Structure, inverted tree representation:
 *
 *            As in the view
 *
 *               Source_m1
 *                  |
 *   Source_m2      M1----------+
 *      |           |           |
 *      +-----------M2      Sink_M1
 *                  |
 *      +-----------R1----------+
 *      |                       |
 *   Sink1_R1               Sink2_R1
 *
 *
 *        Internal representation
 *
 *               Source_m1
 *                  |
 *   Source_m2      M1
 *      |           |
 *      +-----------M2      Sink_M1
 *                  |           |
 *                  R1----------+
 *                  |
 *   Sink1_R1     Dummy     Sink2_R1
 *      |           |           |
 *      +-----------+-----------+
 *                  |
 *                 Root
 *
 *     Internal data representation
 *
 *     Root
 *      |
 *      +-- children[Sink1_R1, Dummy, Sink2_R1]
 *                              |
 *                              +-- children[R1]
 *                                            |
 *                                            +-- children[M2, Sink_M1]
 *                                                          |
 *                                                          +-- children[Source_m2, M1]
 *                                                                                   |
 *                                                                                   +-- children[Source_m1]
 *
 * Steps:
 * ------
 * The job is done in 4 steps, and is modularized using 4 separate recursive functions.
 * 1. _treefyData      : Get the tree structure in place with vertices and inputs/sources
 * 2. _addOutputs      : Add outputs/sinks. A separate step had to be created as outputs
 *                       are represented in the opposite direction of inputs.
 * 3. _cacheChildren   : Make a cache of children in allChildren property for later use
 * 4. _getGraphDetails : Get a graph object with all the required details
 *
 */

/**
 * Enum of various node types
 */
export enum NodeType {
  ROOT = 'root',
  DUMMY = 'dummy',
  VERTEX = 'vertex',
  INPUT = 'input',
  OUTPUT = 'output'
}

export class Edge {
  data: any;

  source!: DataNode;
  target!: DataNode;
  sourceId!: string;
  targetId!: string;

  constructor(data: any) {
    this.data = data;
  }
}

/**
 * Abstract class for all types of data nodes
 */
export abstract class DataNode {
  type: NodeType;
  data: any;

  id!: string;

  depth = 0;

  children!: DataNode[] | null;
  allChildren!: DataNode[] | null; // All children under this node
  treeParent!: DataNode | null; // Direct parent DataNode in our tree structure

  constructor(type: NodeType, data: any) {
    this.type = type;
    this.data = data;

    /**
     * Children that would be displayed in the view, to hide a child it would be removed from this array.
     * Not making this a computed property because - No d3 support, low performance.
     */
    // _init
    this.children = null;
    this.allChildren = null;
    this.treeParent = null;
  }

  /**
   * Private function.
   * Set the child array as it is. Created because of performance reasons.
   * @param children {Array} Array to be set
   */
  _setChildren(children: DataNode[]): void {
    this.children = children && children.length > 0 ? children : null;
  }

  /**
   * Public function.
   * Set the child array after filtering
   * @param children {Array} Array of DataNodes to be set
   */
  setChildren(children: DataNode[]): void {
    const allChildren = this.allChildren;
    if (allChildren) {
      this._setChildren(
        allChildren.filter((child: DataNode) => children.indexOf(child) !== -1) // true if child is in children
      );
    }
  }

  /**
   * Filter out the given children from the children array.
   * @param childrenToRemove {Array} Array of DataNodes to be removed
   */
  removeChildren(childrenToRemove: any): void {
    let children = this.children;
    if (children) {
      children = children.filter((child: any) => {
        return childrenToRemove.indexOf(child) === -1; // false if child is in children
      });
      this._setChildren(children);
    }
  }

  /**
   * Return true if this DataNode is same as or the ancestor of vertex
   * @param vertex {DataNode}
   */
  isSelfOrAncestor(vertex: any): boolean {
    while (vertex) {
      if (vertex === this) {
        return true;
      }
      vertex = vertex.treeParent;
    }
    return false;
  }

  /**
   * If the property is available, expects it to be an array and iterate over
   * its elements using the callback.
   * @param vertex {DataNode}
   * @param callback {Function}
   */
  // ifForEach(property: string, callback: any): void {
  //   if (this[property]) {
  //     this[property].forEach(callback);
  //   }
  // }

  /**
   * Recursively call the function specified in all children
   * its elements using the callback.
   * @param functionName {String} Name of the function to be called
   */
  recursivelyCall(functionName: string): void {
    if (this[functionName]) {
      this[functionName]();
    }
    if (this.children) {
      this.children.forEach((child: DataNode) => child.recursivelyCall(functionName));
    }
  }
}

class DummyNode extends DataNode {
  vertexName: string;

  constructor() {
    super(NodeType.DUMMY, {});
    this.vertexName = 'dummy';
    this.depth = 1;
  }
}

class RootDataNode extends DataNode {
  dummy: DummyNode; // Dummy node used in the tree, check top comments for explanation
  depth = 0; // Depth of the node in the tree structure

  vertexName: string;

  constructor(dummy: DummyNode) {
    super(NodeType.ROOT, {});
    this.dummy = dummy;
    this.vertexName = 'root';
    this._setChildren([this.dummy]);
  }
}

export class VertexDataNode extends DataNode {
  vertexName: string;

  inputs: DataNode[]; // Array of sources
  outputs: DataNode[]; // Array of sinks

  vertexGroup!: any;

  _additionalsIncluded = true;

  constructor(data: any) {
    super(NodeType.VERTEX, data);

    // Initialize data members
    this.id = this.data.vertexName;
    this.vertexName = this.data.vertexName;
    this.inputs = [];
    this.outputs = [];

    if (data.additionalInputs) {
      data.additionalInputs.forEach((input: DataNode) => {
        this.inputs.push(new InputDataNode(this, input));
      });
    }

    if (data.additionalOutputs) {
      data.additionalOutputs.forEach((output: DataNode) => {
        this.outputs.push(new OutputDataNode(this, output));
      });
    }
  }

  /**
   * Sets depth of the vertex and all its input children
   * @param depth {Number}
   */
  setDepth(depth: number): void {
    this.depth = depth;

    depth++;
    this.inputs.forEach((input: DataNode) => {
      input.depth = depth;
    });
  }

  /**
   * Sets vertex tree parents
   * @param parent {DataNode}
   */
  setParent(parent: DataNode): void {
    this.treeParent = parent;
  }

  /**
   * Include sources and sinks in the children list, so that they are displayed
   */
  includeAdditionals(): void {
    this.setChildren(this.inputs.concat(this.children || []));

    // TODO : Check if the following parent to treeParent conversion is valid -----------------------------------------------------------
    //const ancestor: DataNode = this.parent.parent;
    const ancestor: DataNode | null = this.treeParent && this.treeParent.treeParent;
    if (ancestor) {
      ancestor.setChildren(this.outputs.concat(ancestor.children || []));
    }
    this._additionalsIncluded = true;
  }

  /**
   * Exclude sources and sinks in the children list, so that they are hidden
   */
  excludeAdditionals(): void {
    this.removeChildren(this.inputs);

    // TODO : Check if the following parent to treeParent conversion is valid -----------------------------------------------------------
    //const ancestor: DataNode = this.parent.parent;
    const ancestor: DataNode | null = this.treeParent && this.treeParent.treeParent;
    if (ancestor) {
      ancestor.removeChildren(this.outputs);
    }
    this._additionalsIncluded = false;
  }

  /**
   * Toggle inclusion/display of sources and sinks.
   */
  toggleAdditionalInclusion(): void {
    const include = !this._additionalsIncluded;
    this._additionalsIncluded = include;

    if (include) {
      this.includeAdditionals();
    } else {
      this.excludeAdditionals();
    }
  }
}

export class InputDataNode extends DataNode {
  id: string;
  vertex: VertexDataNode; // The vertex DataNode to which this node is linked

  constructor(vertex: VertexDataNode, data: any) {
    super(NodeType.INPUT, data);
    this.vertex = vertex;
    this.depth = vertex.depth + 1;
    this.id = vertex.vertexName + this.data.name;
  }
}

export class OutputDataNode extends DataNode {
  id: string;
  vertex: VertexDataNode; // The vertex DataNode to which this node is linked

  constructor(vertex: VertexDataNode, data: any) {
    super(NodeType.OUTPUT, data);
    this.vertex = vertex;
    this.id = vertex.vertexName + this.data.name;
  }
}

/**
 * Step 1: Recursive
 * Creates primary skeletal structure with vertices and inputs as nodes,
 * All child vertices & inputs will be added to an array property named children
 * As we are trying to treefy graph data, nodes might reoccur. Reject if its in
 * the ancestral chain, and if the new depth is lower (Higher value) than the old
 * reposition the node.
 *
 * @param vertex {VertexDataNode} Root vertex of current sub tree
 * @param depth {Number} Depth of the passed vertex
 * @param vertex {VertexDataNode}
 */
function _treefyData(vertex: VertexDataNode, depth: number, data: any) {
  let children: DataNode[];

  depth++;

  children = centericMap(vertex.data.inEdgeIds, (edgeId: any) => {
    const child: VertexDataNode = data.vertices.get(data.edges.get(edgeId).data.inputVertexName);

    if (!child.isSelfOrAncestor(vertex)) {
      if (child.depth) {
        if (child.depth < depth && child.treeParent) {
          const parentChildren: DataNode[] | null = child.treeParent.children;
          if (parentChildren) {
            const index = parentChildren.indexOf(child);
            if (index > -1) {
              parentChildren.splice(index, 1);
            }
          }
        }
        return;
      }
      child.setParent(vertex);
      return _treefyData(child, depth, data);
    }
  });

  // Remove undefined entries
  children = children.filter((child: any) => child);

  vertex.setDepth(depth);

  // Adds a dummy child to intermediate inputs so that they
  // gets equal relevance as adjacent nodes on plotting the tree!
  if (children.length && vertex.inputs) {
    vertex.inputs.forEach((input: DataNode) => {
      input._setChildren([new DummyNode()]);
    });
  }

  children.push(...vertex.inputs);

  vertex._setChildren(children);
  return vertex;
}

/**
 * Part of step 1
 * To remove recurring vertices in the tree
 * @param vertex {Object} root vertex
 */
function _normalizeVertexTree(vertex: VertexDataNode): VertexDataNode {
  let children: DataNode[] | null = vertex.children;

  if (children) {
    children = children.filter((child: DataNode) => {
      if (child instanceof VertexDataNode) {
        _normalizeVertexTree(child);
      }
      return child.type !== NodeType.VERTEX || child.treeParent === vertex;
    });

    vertex._setChildren(children);
  }

  return vertex;
}

/**
 * Step 2: Recursive awesomeness
 * Attaches outputs into the primary structure created in step 1. As outputs must be represented
 * in the same level of the vertex's parent. They are added as children of its parent's parent.
 *
 * The algorithm is designed to get a symmetric display of output nodes.
 * A call to the function will iterate through all its children, and inserts output nodes at the
 * position that best fits the expected symmetry.
 *
 * @param vertex {VertexDataNode}
 * @return {Object} Nodes that would come to the left and right of the vertex.
 */
function _addOutputs(vertex: VertexDataNode | RootDataNode): any {
  const childVertices: VertexDataNode[] = <VertexDataNode[]>vertex.children;
  const childrenWithOutputs: DataNode[] = [];

  let midIndex = 0;

  const left: DataNode[] = [];
  const right: DataNode[] = [];

  // For a symmetric display of output nodes
  if (childVertices && childVertices.length) {
    midIndex = Math.floor(childVertices.length / 2);
    if (childVertices.length % 2 === 0) {
      midIndex--;
    }

    childVertices.forEach((child: VertexDataNode, index: number) => {
      const additionals: any = _addOutputs(child);
      let mid;

      childrenWithOutputs.push(...additionals.left);
      childrenWithOutputs.push(child);
      childrenWithOutputs.push(...additionals.right);

      if (child.outputs && child.outputs.length) {
        mid = child.outputs.length / 2;

        child.outputs.forEach((output: DataNode) => {
          output.depth = vertex.depth;
        });

        if (index < midIndex) {
          left.push(...child.outputs);
        } else if (index > midIndex) {
          right.push(...child.outputs);
        } else {
          left.push(...child.outputs.slice(mid));
          right.push(...child.outputs.slice(0, mid));
        }
      }
    });

    vertex._setChildren(childrenWithOutputs);
  }

  return {
    left: left,
    right: right
  };
}

/**
 * Step 3: Recursive
 * Create a copy of all possible children in allChildren for later use
 * @param node {DataNode}
 */
function _cacheChildren(node: DataNode) {
  if (node.children) {
    node.allChildren = node.children;
    node.children.forEach(_cacheChildren);
  }
}

/**
 * Return an array of the incoming edges/links and input-output source-sink edges of the node.
 * @param node {DataNode}
 * @return links {Array} Array of all incoming and input-output edges of the node
 */
function _getLinks(node: DataNode, data: any): Edge[] {
  const links: Edge[] = [];

  if (node.data.inEdgeIds) {
    node.data.inEdgeIds.forEach((inEdge: string) => {
      const edge: Edge = data.edges.get(inEdge);
      edge.sourceId = edge.data.inputVertexName;
      edge.targetId = edge.data.outputVertexName;
      links.push(edge);
    });
  }

  if (node instanceof InputDataNode) {
    const edge: Edge = new Edge(null);
    edge.sourceId = node.id;
    edge.targetId = node.vertex.id;
    links.push(edge);
  } else if (node instanceof OutputDataNode) {
    const edge: Edge = new Edge(null);
    edge.sourceId = node.vertex.id;
    edge.targetId = node.id;
    links.push(edge);
  }

  return links;
}

/**
 * Step 4: Recursive
 * Create a graph based on the given tree structure and edges in data object.
 * @param tree {DataNode}
 * @param details {Object} Object with values tree, links, maxDepth & maxHeight
 */
function _getGraphDetails(tree: DataNode, data: any): any {
  let maxDepth = 0;
  let leafCount = 0;

  const links: Edge[] = _getLinks(tree, data);

  if (tree.children) {
    tree.children.forEach((child: DataNode) => {
      const details: any = _getGraphDetails(child, data);

      maxDepth = Math.max(maxDepth, details.maxDepth);
      leafCount += details.leafCount;

      links.push(...details.links);
    });
  } else {
    leafCount++;
  }

  return {
    tree: tree,
    links: links,
    maxDepth: maxDepth + 1,
    leafCount: leafCount
  };
}

/**
 * Converts vertices & edges into hashes for easy access.
 * Makes vertexGroup a property of the respective vertices.
 * @param data {Object}
 * @return {Object} An object with vertices hash, edges hash and array of root vertices.
 */
function _normalizeRawData(verticesData: any, edgesData: any, vertexGroupData: any) {
  const verticesHash: Map<string, VertexDataNode> = new Map();
  const edgesHash: Map<string, Edge> = new Map();
  const rootVertices: VertexDataNode[] = []; // Vertices without out-edges are considered root vertices

  verticesData.forEach((data: any) => {
    const vertexNode = new VertexDataNode(data);
    verticesHash.set(vertexNode.vertexName, vertexNode);

    if (!data.outEdgeIds) {
      rootVertices.push(vertexNode);
    }
  });

  if (edgesData) {
    edgesData.forEach((data: any) => {
      const edge: Edge = new Edge(data);
      edgesHash.set(data.edgeId, edge);
    });
  }

  if (vertexGroupData) {
    // Insert group information into each vertex
    vertexGroupData.forEach((groupData: any) => {
      groupData.groupMembers.forEach((vertexName: string) => {
        const vertex: VertexDataNode | undefined = verticesHash.get(vertexName);
        if (vertex) {
          vertex.vertexGroup = groupData;
        }
      });
    });
  }

  return {
    vertices: verticesHash,
    edges: edgesHash,
    rootVertices: rootVertices
  };
}

/**
 * Iterates the array in a symmetric order, from middle to outwards
 * @param array {Array} Array to be iterated
 * @param callback {Function} Function to be called for each item
 * @return A new array created with value returned by callback
 */
function centericMap(array: any[], callback: (array: any) => any): any[] {
  const retArray = [];
  let length: number, left: number, right: number;

  if (array) {
    length = array.length - 1;
    left = length >> 1;

    while (left >= 0) {
      retArray[left] = callback(array[left]);
      right = length - left;
      if (right !== left) {
        retArray[right] = callback(array[right]);
      }
      left--;
    }
  }
  return retArray;
}

/**
 * Converts raw DAG-plan into an internal data representation that graph-view,
 * and in turn d3.layout.tree can digest.
 * @param data {Object} Dag-plan data
 * @return {Object/String}
 *    - Object with values tree, links, maxDepth & maxHeight
 *    - Error message if the data was not as expected.
 */
export function graphifyData(vertices: any, edges: any, vertexGroup: any): any {
  const dummy: DummyNode = new DummyNode();
  const root: RootDataNode = new RootDataNode(dummy);

  const data: any = _normalizeRawData(vertices, edges, vertexGroup);

  dummy._setChildren(
    centericMap(data.rootVertices, vertex => {
      return _normalizeVertexTree(_treefyData(vertex, 2, data));
    })
  );

  _addOutputs(root);

  _cacheChildren(root);

  return _getGraphDetails(root, data);
}
