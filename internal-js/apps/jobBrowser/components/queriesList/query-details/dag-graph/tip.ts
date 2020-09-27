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

import debounce from '../../../../../../common/debounce';

/**
 * Displays a tooltip over an svg element.
 */
let _element = null; // jQuery tooltip DOM element
let _bubble = null; // Tooltip bubble in _element
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
    list.forEach((property, value) => {
      listContent.push('<tr><td>', property, '</td><td>', value, '</td></tr>');
    });
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
  _element.find('.tip-title').html(data.title || '');
  _element.find('.tip-text').html(data.text || '');
  _element.find('.tip-text')[data.text ? 'show' : 'hide']();
  _element.find('.tip-list').html(_createList(data.kvList) || '');
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
    _bubble = _element.find('.bubble');
    _svg = svg;
    _svgPoint = svg[0].createSVGPoint();
  },
  showTip: debounce((): void => {
    if (_data) {
      _element.addClass('show');
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
      _element.removeClass('below');
      _element.addClass('above');
    } else {
      _element.removeClass('above');
      _element.addClass('below');

      point.y -= _element.height();
    }

    width = _element.width();
    offsetX = (width - 11) >> 1;

    if (point.x - offsetX < 0) {
      offsetX = point.x - 20;
    } else if (point.x + offsetX > winWidth) {
      offsetX = point.x - (winWidth - 10 - width);
    }

    _bubble.css({
      left: -offsetX
    });

    this.showTip();

    _element.css({
      left: point.x,
      top: point.y
    });
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
    _data = _node = null;
    _element.removeClass('show');
  }
};
