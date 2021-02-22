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

import { DateTime } from 'luxon';
import d3 from 'd3v3';
import { get } from 'lodash';

import { NodeType, DataNode, VertexDataNode, OutputDataNode, Edge } from './data-processor';
import Tip from './tip';

/**
 * The view part of Dag View.
 *
 * Displays TEZ DAG graph in a tree layout. (Uses d3.layout.tree)
 * Graph view exposes just 4 functions to the outside world, everything else
 * happens inside the main closure:
 *   1. create
 *   2. fitGraph
 *   3. additionalDisplay
 *   4. toggleLayouts
 *
 * Links, Paths:
 * --------------
 * d3 layout uses the term links, and SVG uses path. Hence you would see both getting used
 * in this file. You can consider link to be a JavaScript data object, and path to be a visible
 * SVG DOM element on the screen.
 *
 * Extra Nodes:
 * ------------
 * Root Node (Invisible):
 *  Dag view support very complex DAGs, even DAGs without interconnections and backward links.
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
 */

export interface GraphView {
  create: (component: any, element: HTMLElement, data: any) => void;
  fitGraph: () => void;
  additionalDisplay: (hide: boolean) => void;
  toggleLayouts: () => boolean;
}

interface Pos {
  x: number;
  y: number;
}

interface Layout {
  hSpacing: number;
  vSpacing: number;
  depthSpacing: number;
  linkDelta: number;
  projector: (x: number, y: number) => Pos;
  pathFormatter: (
    mx: number,
    my: number,
    q1x1: number,
    q1y1: number,
    q1x: number,
    q1y: number,
    q2x1: number,
    q2y1: number,
    q2x: number,
    q2y: number
  ) => string;
}

export default function createGraphView(): GraphView {
  const PADDING = 30; // Adding to be applied on the svg view

  const LAYOUTS: { [name: string]: Layout } = {
    // The view supports two layouts - left to right and top to bottom.
    leftToRight: {
      hSpacing: 180, // Horizontal spacing between nodes
      vSpacing: 70, // Vertical spacing between nodes
      depthSpacing: 180, // In leftToRight depthSpacing = hSpacing
      linkDelta: 30, // Used for links starting and ending at the same point
      projector: function (x: number, y: number) {
        // Converts coordinate based on current orientation
        return { x: y, y: x };
      },
      // Defines how path between nodes are drawn
      pathFormatter: function (
        mx: number,
        my: number,
        q1x1: number,
        q1y1: number,
        q1x: number,
        q1y: number,
        q2x1: number,
        q2y1: number,
        q2x: number,
        q2y: number
      ) {
        return `M ${mx} ${my} Q ${q1x1} ${q1y1} ${q1x} ${q1y} Q ${q2x1} ${q2y1} ${q2x} ${q2y}`;
      }
    },
    topToBottom: {
      hSpacing: 120,
      vSpacing: 100,
      depthSpacing: 100, // In topToBottom depthSpacing = vSpacing
      linkDelta: 15,
      projector: function (x: number, y: number) {
        return { x: x, y: y };
      },
      pathFormatter: function (
        mx: number,
        my: number,
        q1x1: number,
        q1y1: number,
        q1x: number,
        q1y: number,
        q2x1: number,
        q2y1: number,
        q2x: number,
        q2y: number
      ) {
        return `M ${my} ${mx} Q ${q1y1} ${q1x1} ${q1y} ${q1x} Q ${q2y1} ${q2x1} ${q2y} ${q2x}`;
      }
    }
  };

  const DURATION = 750; // Animation duration

  const HREF_TYPE_HASH = {
    // Used to assess the entity type from an event target
    '#task-bubble': 'task',
    '#vertex-bg': 'vertex',
    '#input-bg': 'input',
    '#output-bg': 'output',
    '#io-bubble': 'io',
    '#group-bubble': 'group'
  };

  let _width = 0;
  let _height = 0;

  let _component = null; // The parent ember component
  let _data = null; // Data object created by data processor
  let _treeData = null; // Points to root data node of the tree structure
  let _treeLayout = null; // Instance of d3 tree layout helper
  let _layout: Layout = null; // Current layout, one of the values defined in LAYOUTS object

  let _svg = null; // jQuery instance of svg DOM element
  let _g = null; // For pan and zoom: Svg DOM group element that encloses all the displayed items

  let _idCounter = 0; // To create a fresh id for all displayed nodes
  let _scheduledClickId; // Id of scheduled click, used for double click.

  let _tip; // Instance of tip.js

  let _panZoomValues; // Temporary storage of pan zoom values for fit toggle
  let _panZoom; // A closure returned by _attachPanZoom to reset/modify pan and zoom values

  /**
   * Texts greater than maxLength will be trimmed.
   * @param text {String} Text to trim
   * @param maxLength {Number}
   * @return Trimmed text
   */
  function _trimText(text: string, maxLength: number) {
    if (text) {
      text = text.toString();
      if (text.length > maxLength) {
        text = text.substr(0, maxLength - 1) + '..';
      }
    }
    return text;
  }

  /**
   * Add task bubble to a vertex node
   * @param node {SVG DOM element} Vertex node
   * @param d {VertexDataNode}
   */
  function _addTaskBubble(node: any, d: VertexDataNode) {
    const group = node.append('g');
    group.attr('class', 'task-bubble');
    group.append('use').attr('xlink:href', '#task-bubble');
    group.append('text').text(_trimText(d.data.data.taskCount || 0, 3));
  }

  /**
   * Add IO(source/sink) bubble to a vertex node
   * @param node {SVG DOM element} Vertex node
   * @param d {VertexDataNode}
   */
  function _addIOBubble(node: any, d: VertexDataNode) {
    if (d.inputs.length || d.outputs.length) {
      const group: any = node.append('g');
      group.attr('class', 'io-bubble');
      group.append('use').attr('xlink:href', '#io-bubble');
      group.append('text').text(_trimText(`${d.inputs.length}/${d.outputs.length}`, 3));
    }
  }

  /**
   * Add vertex group bubble to a vertex node
   * @param node {SVG DOM element} Vertex node
   * @param d {VertexDataNode}
   */
  function _addVertexGroupBubble(node: any, d: VertexDataNode) {
    if (d.vertexGroup) {
      const group: any = node.append('g');
      group.attr('class', 'group-bubble');
      group.append('use').attr('xlink:href', '#group-bubble');
      group.append('text').text(_trimText(d.vertexGroup.groupMembers.length, 2));
    }
  }

  /**
   * Add status bar to a vertex node
   * @param node {SVG DOM element} Vertex node
   * @param d {VertexDataNode}
   */
  function _addStatusBar(node: any, d: VertexDataNode) {
    const group: any = node.append('g');
    group.attr('class', 'status-bar');
    group
      .append('foreignObject')
      .attr('class', 'status')
      .attr('width', 70)
      .attr('height', 15)
      .html('<span class="msg-container">' + d.data.data.status + '</span>');
  }

  /**
   * Creates a base SVG DOM node, with bg and title based on the type of DataNode
   * @param node {SVG DOM element} Vertex node
   * @param d {DataNode}
   * @param titleProperty {String} d's property who's value is the title to be displayed.
   *    By default 'name'.
   * @param maxTitleLength {Number} Title would be trimmed beyond maxTitleLength. By default 3 chars
   */
  function _addBasicContents(node: any, d: DataNode, titleProperty?: string) {
    const className: string = d.type;

    titleProperty = titleProperty || 'name';

    node.attr('class', `node ${className}`);
    node.append('use').attr('xlink:href', `#${className}-bg`);
    node.append('text').attr('class', 'title').text(_trimText(d.data[titleProperty], 12));
  }

  /**
   * Populates the calling node with the required content.
   * @param s {DataNode}
   */
  function _addContent(d: DataNode) {
    const node: any = d3.select(this);

    switch (d.type) {
      case 'vertex':
        _addBasicContents(node, d, 'vertexName');
        _addStatusBar(node, <VertexDataNode>d);
        _addTaskBubble(node, <VertexDataNode>d);
        _addIOBubble(node, <VertexDataNode>d);
        _addVertexGroupBubble(node, <VertexDataNode>d);
        break;
      case 'input':
      case 'output':
        _addBasicContents(node, d);
        break;
    }
  }

  /**
   * Create a list of all links connecting nodes in the given array.
   * @param nodes {Array} A list of d3 nodes created by tree layout
   * @return links {Array} All links between nodes in the current DAG
   */
  function _getLinks(nodes: any[]): any[] {
    const links: any[] = [];
    const nodeHash: Map<string, any> = new Map();

    nodes.forEach((node: any) => {
      nodeHash.set(node.id, node);
    });

    _data.links.forEach((link: any) => {
      const source: any = nodeHash.get(link.sourceId);
      const target: any = nodeHash.get(link.targetId);

      if (source && target) {
        Object.assign(link, {
          source: source,
          target: target,
          isBackwardLink: source.isSelfOrAncestor(target)
        });
        links.push(link);
      }
    });

    return links;
  }

  /**
   * Apply proper depth spacing and remove the space occupied by dummy node
   * if the number of other nodes are odd.
   * @param nodes {Array} A list of d3 nodes created by tree layout
   */
  function _normalize(nodes: any[]) {
    // Set layout
    let farthestY = 0;
    nodes.forEach((d: any) => {
      d.y = d.depth * -_layout.depthSpacing;
      if (d.y < farthestY) {
        farthestY = d.y;
      }
    });

    farthestY -= PADDING;
    nodes.forEach((d: any) => {
      d.y -= farthestY;
    });

    //Remove space occupied by dummy
    const rootChildren = _treeData.children;
    const rootChildCount = rootChildren.length;
    let dummyIndex: number;
    let i: number;

    if (rootChildCount % 2 === 0) {
      dummyIndex = rootChildren.indexOf(_treeData.dummy);
      if (dummyIndex >= rootChildCount / 2) {
        for (i = 0; i < dummyIndex; i++) {
          rootChildren[i].x = rootChildren[i + 1].x;
          rootChildren[i].y = rootChildren[i + 1].y;
        }
      } else {
        for (i = rootChildCount - 1; i > dummyIndex; i--) {
          rootChildren[i].x = rootChildren[i - 1].x;
          rootChildren[i].y = rootChildren[i - 1].y;
        }
      }
    }

    // Put all single vertex outputs in-line with the vertex node
    // So that they are directly below the respective vertex in vertical layout
    nodes.forEach((node: any) => {
      if (
        node instanceof OutputDataNode &&
        get(node, 'vertex.outputs.length') === 1 &&
        !get(node, 'vertex.data.outEdgeIds.length') &&
        get(node, 'treeParent.data.x') !== node.data.x
      ) {
        node.data.x = node.vertex.data.x;
      }
    });
  }

  function _getType(node: any): string {
    if (node.tagName === 'path') {
      return 'path';
    }
    return HREF_TYPE_HASH[node.href];
  }

  function _getEndName(fullName: string): string {
    return fullName.substr(fullName.lastIndexOf('.') + 1);
  }

  /**
   * Mouse over handler for all displayed SVG DOM elements.
   * Later the implementation will be refactored and moved into the respective DataNode.
   * d {DataNode} Contains data to be displayed
   */
  function _onMouseOver(d: any) {
    const event = d3.event;
    let tooltipData: any = {}; // Will be populated with {title/text/kvList}.
    let node = event.target;

    node = node.correspondingUseElement || node;

    switch (_getType(node)) {
      case 'vertex':
        const vertex = d.data.data;
        let list = {};

        _component.vertexProperties.forEach((property: any) => {
          let value: any = {};

          if (vertex && property.getCellContent) {
            value = property.getCellContent(vertex);
            if (value && value.text !== undefined) {
              value = value.text;
            }
          } else if (property.contentPath) {
            value = d.data.data[property.contentPath]; // Was get ---
          }

          if (property.cellComponentName === 'date-formatter') {
            value = DateTime.fromMillis(value).toFormat('DD MMM YYYY HH:mm:ss:SSS');
          }

          if (property.id === 'progress' && value) {
            value = Math.round(value * 100) + '%';
          } else if (property.id === 'duration' && value) {
            value = value + ' ms';
          }

          if (typeof value !== 'object') {
            list[property.get('headerTitle')] = value;
          }
        });

        tooltipData = {
          title: (<VertexDataNode>d).vertexName,
          kvList: list
        };
        break;
      case 'input':
        list = {
          Class: _getEndName(d.data.class),
          Initializer: _getEndName(d.data.initializer),
          Configurations: d.data.configs.length || 0
        };
        tooltipData = {
          title: d.data.name,
          kvList: list
        };
        break;
      case 'output':
        list = {
          Class: _getEndName(d.data.class),
          Configurations: d.data.configs.length || 0
        };
        tooltipData = {
          title: d.data.name,
          kvList: list
        };
        break;
      case 'task':
        const totalTasks = d.data.data.totalTasks || 0;
        tooltipData.title = totalTasks > 1 ? `${totalTasks} Tasks` : `${totalTasks} Task`;
        break;
      case 'io':
        const inputs = d.data.inputs.length;
        const outputs = d.data.outputs.length;
        let title = '';

        title += inputs > 1 ? `${inputs} Sources` : `${inputs} Source`;
        title += ' & ';
        title += outputs > 1 ? `${outputs} Sinks` : `${outputs} Sink`;
        tooltipData.title = title;
        break;
      case 'group':
        tooltipData = {
          title: d.data.vertexGroup.groupName,
          text: d.data.vertexGroup.groupMembers.join(', ')
        };
        break;
      case 'path':
        const sourceName = d.source.name || d.source.vertexName;
        const targetName = d.target.name || d.target.vertexName;

        tooltipData = {
          position: {
            x: event.clientX,
            y: event.clientY
          },
          title: `${sourceName} - ${targetName}`
        };
        if (d.data && d.data.edgeId) {
          tooltipData.kvList = {
            'Edge Id': d.data.edgeId,
            'Data Movement Type': d.data.dataMovementType,
            'Data Source Type': d.data.dataSourceType,
            'Scheduling Type': d.data.schedulingType,
            'Edge Source Class': _getEndName(d.data.edgeSourceClass),
            'Edge Destination Class': _getEndName(d.data.edgeDestinationClass)
          };
        } else {
          tooltipData.text = get(d, 'data.source.type') === 'input' ? 'Source link' : 'Sink link';
        }
        break;
    }

    if (tooltipData.kvList) {
      const kvList = tooltipData.kvList;
      const newKVList = {};

      Object.keys(kvList).forEach((key: string) => {
        if (kvList[key]) {
          newKVList[key] = kvList[key];
        }
      });

      tooltipData.kvList = newKVList;
    }

    _tip.show(node, tooltipData, event);
  }

  /**
   * onclick handler scheduled using setTimeout
   * @params d {DataNode} data of the clicked element
   * @param node {D3 element} Element that was clicked
   */
  function _scheduledClick(d: DataNode, node: any) {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    node = node.correspondingUseElement || node;

    // TODO: Emit click action -------------------------------------------------------------------------------------------------------------
    // _component.sendAction('entityClicked', {
    //   type: _getType(node),
    //   d: d
    // });

    _tip.hide();
    _scheduledClickId = 0;
  }

  /**
   * Schedules an onclick handler. If double click event is not triggered the handler
   * will be called in 200ms.
   * @param d {DataNode} Data of the clicked element
   */
  function _onClick(d: DataNode) {
    if (!_scheduledClickId) {
      _scheduledClickId = setTimeout(_scheduledClick.bind(this, d, d3.event.target), 200);
    }
  }

  /**
   * Callback for mousedown & mousemove interactions. To disable click on drag
   * @param d {DataNode} Data of the clicked element
   */
  function _onMouse(/*d*/) {
    d3.select(this).on('click', d3.event.type === 'mousedown' ? _onClick : null);
  }

  /**
   * Double click event handler.
   * @param d {DataNode} Data of the clicked element
   */
  function _onDblclick(d: DataNode) {
    const event = d3.event;
    let node = event.target;

    node = node.correspondingUseElement || node;

    if (_scheduledClickId) {
      clearTimeout(_scheduledClickId);
      _scheduledClickId = 0;
    }

    switch (_getType(node)) {
      case 'io':
        (<VertexDataNode>d).toggleAdditionalInclusion();
        _update();
        break;
    }
  }

  /**
   * Creates a path data string for the given link. Google SVG path data to learn what it is.
   * @param d {Object} Must contain source and target properties with the start and end positions.
   * @return pathData {String} Path data string based on the current layout
   */
  function _createPathData(d) {
    let sX = d.source.y;
    const sY = d.source.x;
    let tX = d.target.y;
    const tY = d.target.x;
    const mX = (sX + tX) / 2;
    let mY = (sY + tY) / 2;

    let sH = Math.abs(sX - tX) * 0.35;
    let sV = 0; // strength

    if (d.isBackwardLink) {
      if (sY === tY) {
        sV = 45;
        mY -= 50;
        if (sX === tX) {
          sX += _layout.linkDelta;
          tX -= _layout.linkDelta;
        }
      }
      sH = Math.abs(sX - tX) * 1.1;
    }

    return _layout.pathFormatter(
      sX,
      sY,

      sX + sH,
      sY - sV,
      mX,
      mY,

      tX - sH,
      tY - sV,
      tX,
      tY
    );
  }

  /**
   * Get the node from/to which the node must transition on enter/exit
   * @param d {DataNode}
   * @param property {String} Property to be checked for
   * @return vertex node
   */
  function _getVertexNode(d: DataNode, property: string): any {
    //d.data.vertex[property]
    if (d[property]) {
      return d; //d.get('vertex');
    }
  }
  /**
   * Update position of all nodes in the list and preform required transitions.
   * @param nodes {Array} Nodes to be updated
   * @param source {d3 element} Node that trigged the update, in first update source will be root.
   */
  function _updateNodes(nodes: any, source: any) {
    // Enter any new nodes at the parent's previous position.
    nodes
      .enter()
      .append('g')
      .attr('transform', (d: any) => {
        let node = _getVertexNode(d, 'x0') || source;
        node = _layout.projector(node.x0, node.y0);
        return 'translate(' + node.x + ',' + node.y + ')';
      })
      .on({
        mouseover: _onMouseOver,
        mouseout: _tip.hide,
        mousedown: _onMouse,
        mousemove: _onMouse,
        dblclick: _onDblclick
      })
      .style('opacity', 1e-6)
      .each(_addContent);

    // Transition nodes to their new position.
    nodes
      .transition()
      .duration(DURATION)
      .attr('transform', (d: any) => {
        d = _layout.projector(d.x, d.y);
        return 'translate(' + d.x + ',' + d.y + ')';
      })
      .style('opacity', 1);

    // Transition exiting nodes to the parent's new position.
    nodes
      .exit()
      .transition()
      .duration(DURATION)
      .attr('transform', (d: any) => {
        let node = _getVertexNode(d, 'x') || source;
        node = _layout.projector(node.x, node.y);
        return 'translate(' + node.x + ',' + node.y + ')';
      })
      .style('opacity', 1e-6)
      .remove();
  }

  /**
   * Get the node from/to which the link must transition on enter/exit
   * @param d {DataNode}
   * @param property {String} Property to be checked for
   * @return node
   */
  function _getTargetNode(d: Edge, property: string) {
    if (d.target.type === NodeType.OUTPUT && d.source[property]) {
      return d.source;
    }
    if (d.target[property]) {
      return d.target;
    }
  }
  /**
   * Update position of all links in the list and preform required transitions.
   * @param links {Array} Links to be updated
   * @param source {d3 element} Node that trigged the update, in first update source will be root.
   */
  function _updateLinks(links: any, source: any) {
    // Enter any new links at the parent's previous position.
    links
      .enter()
      .insert('path', 'g')
      .attr('class', (d: any) => {
        const type = get(d, 'data.dataMovementType', '');
        return 'link ' + type.toLowerCase();
      })
      .attr('style', 'marker-mid: url(' + window.location.pathname + '#arrow-marker);')
      .attr('d', (d: any) => {
        const node = _getTargetNode(d, 'x0') || source;
        const o = { x: node.x0, y: node.y0 };
        return _createPathData({ source: o, target: o });
      })
      .on({
        mouseover: _onMouseOver,
        mouseout: _tip.hide
      });

    // Transition links to their new position.
    links.transition().duration(DURATION).attr('d', _createPathData);

    // Transition exiting nodes to the parent's new position.
    links
      .exit()
      .transition()
      .duration(DURATION)
      .attr('d', (d: any) => {
        const node = _getTargetNode(d, 'x') || source;
        const o = { x: node.x, y: node.y };
        return _createPathData({ source: o, target: o });
      })
      .remove();
  }

  function _getNodeId(d: any) {
    return d.id || (d.id = ++_idCounter);
  }
  function _getLinkId(d: any) {
    return d.source.id.toString() + d.target.id;
  }
  function _stashOldPositions(d: any) {
    d.x0 = d.x;
    d.y0 = d.y;
  }

  /**
   * Updates position of nodes and links based on changes in _treeData.
   */
  function _update() {
    const nodesData = _treeLayout.nodes(_treeData);
    const linksData = _getLinks(nodesData);

    _normalize(nodesData);

    const nodes = _g.selectAll('g.node').data(nodesData, _getNodeId);
    _updateNodes(nodes, _treeData);

    const links = _g.selectAll('path.link').data(linksData, _getLinkId);
    _updateLinks(links, _treeData);

    nodesData.forEach(_stashOldPositions);
  }

  /**
   * Attach pan and zoom events on to the container.
   * @param container {DOM element} Element onto which events are attached.
   * @param g {d3 DOM element} SVG(d3) element that will be moved or scaled
   */
  function _attachPanZoom(container: any, g: any, element: any) {
    const SCALE_TUNER = 1 / 700;
    const MIN_SCALE = 0.5;
    const MAX_SCALE = 2;

    let prevX = 0;
    let prevY = 0;

    let panX = PADDING;
    let panY = PADDING;
    let scale = 1;

    let scheduleId;

    /**
     * Transform g to current panX, panY and scale.
     * @param animate {Boolean} Animate the transformation in DURATION time.
     */
    function transform(animate = false): void {
      const base = animate ? g.transition().duration(DURATION) : g;
      base.attr('transform', `translate(${panX}, ${panY}) scale(${scale})`);
    }

    /**
     * Check if the item have moved out of the visible area, and reset if required
     */
    function visibilityCheck() {
      const graphBound = g.node().getBoundingClientRect();
      const containerBound = container.getBoundingClientRect();

      if (
        graphBound.right < containerBound.left ||
        graphBound.bottom < containerBound.top ||
        graphBound.left > containerBound.right ||
        graphBound.top > containerBound.bottom
      ) {
        panX = PADDING;
        panY = PADDING;
        scale = 1;
        transform(true);
      }
    }

    /**
     * Schedule a visibility check and reset if required
     */
    function scheduleVisibilityCheck() {
      if (scheduleId) {
        clearTimeout(scheduleId);
        scheduleId = 0;
      }
      scheduleId = setTimeout(visibilityCheck, 100);
    }

    /**
     * Set pan values
     */
    function onMouseMove(event) {
      panX += event.pageX - prevX;
      panY += event.pageY - prevY;

      transform();

      prevX = event.pageX;
      prevY = event.pageY;
    }
    /**
     * Set zoom values, pan also would change as we are zooming with mouse position as pivote.
     */
    function onWheel(event: any) {
      const prevScale = scale;

      const mouseX = event.pageX - container.clientLeft;
      const mouseY = event.pageY - container.clientTop;
      let factor = 0;

      scale += event.deltaY * SCALE_TUNER;
      if (scale < MIN_SCALE) {
        scale = MIN_SCALE;
      } else if (scale > MAX_SCALE) {
        scale = MAX_SCALE;
      }

      factor = 1 - scale / prevScale;
      panX += (mouseX - panX) * factor;
      panY += (mouseY - panY) * factor;

      transform();
      scheduleVisibilityCheck();

      _tip.reposition();
      event.preventDefault();
    }

    // Disabling zoom temporarily. Making this a condition to prevent lint errors
    if (false) {
      element.addEventListener('wheel', onWheel);
    }

    container.addEventListener('mousedown', (event: MouseEvent) => {
      prevX = event.pageX;
      prevY = event.pageY;

      container.addEventListener('mousemove', onMouseMove);
      container.parentElement.classList.add('panning');
    });

    container.addEventListener('mouseup', () => {
      container.removeEventListener('mousemove', onMouseMove);
      container.parentElement.classList.remove('panning');

      scheduleVisibilityCheck();
    });

    /**
     * A closure to reset/modify panZoom based on an external event
     * @param newPanX {Number}
     * @param newPanY {Number}
     * @param newScale {Number}
     */
    return (newPanX: number, newPanY: number, newScale: number) => {
      const values = {
        panX: panX,
        panY: panY,
        scale: scale
      };

      panX = newPanX === undefined ? panX : newPanX;
      panY = newPanY === undefined ? panY : newPanY;
      scale = newScale === undefined ? scale : newScale;

      transform(true);

      return values;
    };
  }

  /**
   * Sets the layout and update the display.
   * @param layout {Object} One of the values defined in LAYOUTS object
   */
  function _setLayout(layout) {
    let leafCount = _data.leafCount,
      dimention;

    // If count is even dummy will be replaced by output, so output would no more be leaf
    if (_data.tree.children.length % 2 === 0) {
      leafCount--;
    }
    dimention = layout.projector(leafCount, _data.maxDepth - 1);

    _layout = layout;

    _width = dimention.x *= _layout.hSpacing;
    _height = dimention.y *= _layout.vSpacing;

    dimention = _layout.projector(dimention.x, dimention.y); // Because tree is always top to bottom
    _treeLayout = d3.layout.tree().size([dimention.x, dimention.y]);

    _update();
  }

  return {
    /**
     * Creates a DAG view in the given element based on the data
     * @param component {DagViewComponent} Parent ember component, to sendAction
     * @param element {HTML DOM Element} HTML element in which the view will be created
     * @param data {Object} Created by data processor
     */
    create: (component: any, element: HTMLElement, data: any) => {
      const svg = d3.select(element).select('svg');

      _component = component;
      _data = data;
      _g = svg.append('g').attr('transform', `translate(${PADDING},${PADDING})`);
      _svg = svg.node();
      _tip = Tip;

      //_tip.init(element.querySelector('.tool-tip'), _svg);

      _treeData = data.tree;
      _treeData.x0 = 0;
      _treeData.y0 = 0;

      _panZoom = _attachPanZoom(_svg, _g, element);

      _setLayout(LAYOUTS.topToBottom);
    },

    /**
     * Calling this function would fit the graph to the available space.
     */
    fitGraph: function () {
      const bound: any = _svg.getBoundingClientRect();
      const scale = Math.min(
        (bound.width - PADDING * 2) / _width,
        (bound.height - PADDING * 2) / _height
      );
      const panZoomValues = _panZoom();

      if (
        panZoomValues.panX !== PADDING ||
        panZoomValues.panY !== PADDING ||
        panZoomValues.scale !== scale
      ) {
        _panZoomValues = _panZoom(PADDING, PADDING, scale);
      } else {
        // _panZoomValues = _panZoom(_panZoomValues.panX, _panZoomValues.panY, _panZoomValues.scale);
        _panZoomValues = _panZoom(_panZoomValues.panX, _panZoomValues.panY, 2); // Temporarily till zoom is enabled
      }
    },

    /**
     * Control display of additionals or sources and sinks.
     * @param hide {Boolean} If true the additionals will be excluded, else included in the display
     */
    additionalDisplay: function (hide: boolean) {
      if (hide) {
        _g.attr('class', 'hide-io');
        _treeData.recursivelyCall('excludeAdditionals');
      } else {
        _treeData.recursivelyCall('includeAdditionals');
        _g.attr('class', null);
      }
      _update();
    },

    /**
     * Toggle graph layouts between the available options
     */
    toggleLayouts: function (): boolean {
      _setLayout(_layout === LAYOUTS.topToBottom ? LAYOUTS.leftToRight : LAYOUTS.topToBottom);
      return _layout === LAYOUTS.topToBottom;
    }
  };
}
