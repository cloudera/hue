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

import debounce from '../../../../../../common/debounce';

/**
 * Displays a tooltip over an svg element.
 */
let _element = null; // jQuery tooltip DOM element
let _bubble = null; // Tooltip bubble in _element
// eslint-disable-next-line @typescript-eslint/no-unused-vars
let _svg = null; // HTML svg tag that contains the element
let _svgPoint = null; // A SVGPoint object

let _data = null; // Last displayed data, for re-render
let _node = null; // Last node over which tooltip was displayed

/**
 * Converts the provided list object into a tabular form.
 * @param list {Object} : An object with properties to be displayed as key value pairs
 *   {
 *     propertyName1: "property value 1",
 *     ..
 *     propertyNameN: "property value N",
 *   }
 */
function _createList(list: any[]) {
  const listContent = [];

  if (list) {
    listContent.push('<table>');
    for (const property in list) {
      listContent.push('<tr><td>', property, '</td><td>', list[property], '</td></tr>');
    }
    listContent.push('</table>');
    return listContent.join('');
  }
}

/**
 * Tip supports 3 visual entities in the tooltip. Title, description text and a list.
 * _setData sets all these based on the passed data object
 * @param data {Object} An object of the format
 * {
 *   title: "tip title",
 *   text: "tip description text",
 *   kvList: {
 *     propertyName1: "property value 1",
 *     ..
 *     propertyNameN: "property value N",
 *   }
 * }
 */
function _setData(data) {
  _element.querySelector('.tip-title').innerHTML = data.title || '';
  _element.querySelector('.tip-text').innerHTML = data.text || '';
  _element.querySelector('.tip-list').innerHTML = _createList(data.kvList) || '';
  _element.querySelector('.tip-text').style.visibility = data.text ? 'visible' : 'hidden';
}

export default {
  /**
   * Set the tip defaults
   * @param tipElement {$} jQuery reference to the tooltip DOM element.
   *    The element must contain 3 children with class tip-title, tip-text & tip-list.
   * @param svg {$} jQuery reference to svg html element
   */
  init(tipElement: any, svg: any): void {
    _element = tipElement;
    _bubble = _element.querySelector('.bubble');
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _svg = svg;
    _svgPoint = svg.createSVGPoint();
  },
  showTip: debounce((): void => {
    if (_data) {
      _element.classList.add('show');
    }
  }, 500),

  /**
   * Display a tooltip over an svg element.
   * @param node {SVG Element} Svg element over which tooltip must be displayed.
   * @param data {Object} An object of the format
   * {
   *   title: "tip title",
   *   text: "tip description text",
   *   kvList: {
   *     propertyName1: "property value 1",
   *     ..
   *     propertyNameN: "property value N",
   *   }
   * }
   * @param event {MouseEvent} Event that triggered the tooltip.
   */
  show(node: any, data: any, event: MouseEvent): void {
    let point: any = data.position;

    if (!_element) {
      return;
    }

    if (!point) {
      point = node.getScreenCTM
        ? _svgPoint.matrixTransform(node.getScreenCTM())
        : { x: event.x, y: event.y };
    }

    const windMid = window.innerHeight >> 1;
    const winWidth = window.innerWidth;

    const showAbove = point.y < windMid;

    let offsetX = 0;
    let width = 0;

    if (_data !== data) {
      _data = data;
      _node = node;

      _setData(data);
    }

    if (showAbove) {
      _element.classList.remove('below');
      _element.classList.add('above');
    } else {
      _element.classList.remove('above');
      _element.classList.add('below');

      point.y -= _element.getBoundingClientRect().height;
    }

    width = _element.getBoundingClientRect().width;
    offsetX = (width - 11) >> 1;

    if (point.x - offsetX < 0) {
      offsetX = point.x - 20;
    } else if (point.x + offsetX > winWidth) {
      offsetX = point.x - (winWidth - 10 - width);
    }

    _bubble.style.left = -offsetX;

    this.showTip();

    _element.style.left = point.x;
    _element.style.top = point.y;
  },
  /**
   * Reposition the tooltip based on last passed data & node.
   */
  reposition(): void {
    if (_data) {
      this.show(_node, _data);
    }
  },
  /**
   * Hide the tooltip.
   */
  hide(): void {
    if (!_element) {
      return;
    }

    _data = _node = null;
    _element.classList.remove('show');
  }
};
