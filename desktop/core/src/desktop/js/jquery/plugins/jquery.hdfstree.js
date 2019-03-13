// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import jQuery from 'jquery';

import hueUtils from '../../utils/hueUtils';
import I18n from 'utils/i18n';

// TODO: don't create multiple jquery instances from chunks
const $ = window.$ || jQuery;

/*
 * jHue HDFS tree plugin
 * shows a tree HDFS picker, if initialPath is set it pre-populates the path
 * if home is specified a home link will appear
 * use attached to an element, ie:
 * $("#el").jHueHdfsTree({
 *    initialPath: "/user",
 *    home: "/user/hue"
 *    onPathChange: function (path) {
 *      console.log(path);
 *    }
 * });
 */

const pluginName = 'jHueHdfsTree',
  defaults = {
    home: '',
    initialPath: '/',
    isS3: false,
    withTopPadding: true,
    onPathChange: function() {},
    createFolder: true,
    labels: {
      CREATE_FOLDER: 'Create folder',
      FOLDER_NAME: 'Folder name',
      CANCEL: 'Cancel',
      HOME: 'Home'
    }
  };

function Plugin(element, options) {
  this.element = element;
  this.options = $.extend({}, defaults, options);
  this.options.labels = $.extend(
    {},
    defaults.labels,
    {
      GO_TO_COLUMN: I18n('Go to column:'),
      PLACEHOLDER: I18n('column name...'),
      LOCK: I18n('Lock this row'),
      UNLOCK: I18n('Unlock this row'),
      ROW_DETAILS: I18n('Show row details')
    },
    options ? options.labels : {}
  );
  this._defaults = defaults;
  this._name = pluginName;
  this.lastPath = '';
  this.previousPath = '';
  this.init();
}

Plugin.prototype.init = function(optionalPath) {
  const _this = this;

  if (typeof optionalPath != 'undefined') {
    _this.options.initialPath = optionalPath;
  }
  const _el = $(_this.element);
  _el.empty();
  _el.addClass('jHueHdfsTree');

  let _homeLink;
  if (_this.options.home != '') {
    _homeLink = $('<a>')
      .html('<i class="fa fa-home"></i> ' + _this.options.labels.HOME)
      .click(() => {
        const _path = _this.options.home;
        _this.options.onPathChange(_path);
        _this.lastPath = _path;
        _tree.find('a').removeClass('selected');
        const _paths = [];
        const _re = /\//g;
        let match;
        while ((match = _re.exec(_path)) != null) {
          _paths.push(_path.substr(0, match.index));
        }
        _paths.push(_path);

        showHdfsLeaf({
          paths: _paths,
          scroll: true
        });
      });
    _homeLink.css({
      cursor: 'pointer',
      position: 'fixed',
      'padding-bottom': '4px',
      'font-size': '16px',
      'border-bottom': '1px solid #FFF',
      'background-color': '#FFF',
      width: 560 - hueUtils.scrollbarWidth() + 'px'
    });
  }

  const _tree = $('<ul>')
    .addClass('content unstyled')
    .html('<li><a class="pointer"><i class="fa fa-folder-open-o"></i> /</a></li>');
  if (_this.options.withTopPadding) {
    _tree.css('padding-top', '30px');
  }

  if (_this.options.home != '') {
    _homeLink.appendTo(_el);
    _el.parent().on('scroll', () => {
      if (_el.parent().scrollTop() > 0) {
        _homeLink.css({
          'border-bottom': '1px solid #EEE'
        });
      } else {
        _homeLink.css({
          'border-bottom': '1px solid #FFF'
        });
      }
    });
  }
  _tree.appendTo(_el);

  _tree.find('a').on('click', () => {
    _this.options.onPathChange('/');
    _tree.find('a').removeClass('selected');
    _tree.find('a:eq(0)').addClass('selected');
  });

  const _root = $('<ul>')
    .addClass('content unstyled')
    .attr('data-path', '__JHUEHDFSTREE__ROOT__')
    .attr('data-loaded', 'true');
  _root.appendTo(_tree.find('li'));

  const BASE_PATH = '/filebrowser/view=';
  let _currentFiles = [];

  function escapeSingleQuote(path) {
    return path.replace(/\'/gi, "\\'");
  }

  function removeLeadingSlash(path) {
    if (path.indexOf('/') == 0) {
      return path.substr(1);
    }
    return path;
  }

  function showHdfsLeaf(options) {
    let autocompleteUrl = BASE_PATH,
      currentPath = '';

    if (options.paths != null && options.paths.length > 0) {
      const shiftedPath = options.paths.shift();
      if (_this.options.isS3) {
        currentPath = shiftedPath;
      } else {
        currentPath = shiftedPath != '' ? shiftedPath : '/';
      }
    } else {
      currentPath = options.leaf != null ? options.leaf : '/';
    }
    autocompleteUrl += currentPath;
    $.getJSON(autocompleteUrl + '?pagesize=1000&format=json', data => {
      _currentFiles = [];
      if (data.error == null) {
        const filteredCurrentPath = _this.options.isS3 ? currentPath.substr(5) : currentPath;
        const _dataPathForCurrent =
          filteredCurrentPath != ''
            ? removeLeadingSlash(filteredCurrentPath)
            : '__JHUEHDFSTREE__ROOT__';
        _el
          .find("[data-path='" + escapeSingleQuote(_dataPathForCurrent) + "']")
          .attr('data-loaded', true);
        _el
          .find("[data-path='" + escapeSingleQuote(_dataPathForCurrent) + "']")
          .siblings('a')
          .find('.fa-folder-o')
          .removeClass('fa-folder-o')
          .addClass('fa-folder-open-o');
        _tree.find('a').removeClass('selected');
        _el
          .find("[data-path='" + escapeSingleQuote(_dataPathForCurrent) + "']")
          .siblings('a')
          .addClass('selected');

        if (options.scroll) {
          _el.parent().scrollTop(
            _el
              .find("[data-path='" + escapeSingleQuote(_dataPathForCurrent) + "']")
              .siblings('a')
              .position().top +
              _el.parent().scrollTop() -
              30
          );
        }
        $(data.files).each((cnt, item) => {
          if (item.name != '.' && item.name != '..' && item.type == 'dir') {
            const _path = item.path;
            const filteredPath = _this.options.isS3 ? _path.substr(5) : _path;
            const _escapedPath = escapeSingleQuote(filteredPath);
            if (_el.find("[data-path='" + removeLeadingSlash(_escapedPath) + "']").length == 0) {
              const _li = $('<li>').html(
                '<a class="pointer"><i class="fa fa-folder-o"></i> ' +
                  item.name +
                  '</a><ul class="content unstyled" data-path="' +
                  removeLeadingSlash(_escapedPath) +
                  '" data-loaded="false"></ul>'
              );
              let _destination = filteredPath.substr(0, filteredPath.lastIndexOf('/'));
              if (_destination == '') {
                _destination = '__JHUEHDFSTREE__ROOT__';
              }
              _destination = removeLeadingSlash(_destination);
              _li.appendTo(_el.find("[data-path='" + escapeSingleQuote(_destination) + "']"));
              _li.find('a').on('click', () => {
                _this.options.onPathChange(_path);
                _this.lastPath = _path;
                _tree.find('a').removeClass('selected');
                _li.find('a:eq(0)').addClass('selected');
                if (_li.find('.content').attr('data-loaded') == 'false') {
                  showHdfsLeaf({
                    leaf: _path,
                    scroll: false
                  });
                } else if (_li.find('.content').is(':visible')) {
                  _li.find('.content').hide();
                } else {
                  _li.find('.content').show();
                }
              });
            }
          }
        });
        if (_this.options.createFolder) {
          const filteredCurrentPath = _this.options.isS3 ? currentPath.substr(5) : currentPath;
          const _createFolderLi = $('<li>').html(
            '<a class="pointer"><i class="fa fa-plus-square-o"></i> ' +
              _this.options.labels.CREATE_FOLDER +
              '</a>'
          );
          _createFolderLi.appendTo(
            _el.find(
              "[data-path='" + removeLeadingSlash(escapeSingleQuote(filteredCurrentPath)) + "']"
            )
          );

          const _createFolderDetails = $('<form>')
            .css('margin-top', '10px')
            .addClass('form-inline');
          _createFolderDetails.hide();
          const _folderName = $('<input>')
            .attr('type', 'text')
            .attr('placeholder', _this.options.labels.FOLDER_NAME)
            .appendTo(_createFolderDetails);
          $('<span> </span>').appendTo(_createFolderDetails);
          const _folderBtn = $('<input>')
            .attr('type', 'button')
            .attr('value', _this.options.labels.CREATE_FOLDER)
            .addClass('btn primary')
            .appendTo(_createFolderDetails);
          $('<span> </span>').appendTo(_createFolderDetails);
          const _folderCancel = $('<input>')
            .attr('type', 'button')
            .attr('value', _this.options.labels.CANCEL)
            .addClass('btn')
            .appendTo(_createFolderDetails);
          _folderCancel.click(() => {
            _createFolderDetails.slideUp();
          });
          _folderBtn.click(() => {
            $.ajax({
              type: 'POST',
              url: '/filebrowser/mkdir',
              data: {
                name: _folderName.val(),
                path: currentPath
              },
              beforeSend: function(xhr) {
                xhr.setRequestHeader('X-Requested-With', 'Hue'); // need to override the default one because otherwise Django returns HTTP 500
              },
              success: function(xhr, status) {
                if (status == 'success') {
                  _createFolderDetails.slideUp();
                  const _newFolder = currentPath + '/' + _folderName.val();
                  _this.init(_newFolder);
                  _this.options.onPathChange(_newFolder);
                }
              }
            });
          });
          _createFolderDetails.appendTo(
            _el.find(
              "[data-path='" + removeLeadingSlash(escapeSingleQuote(filteredCurrentPath)) + "']"
            )
          );

          _createFolderLi.find('a').on('click', () => {
            _createFolderDetails.slideDown();
          });
        }
        if (options.paths != null && options.paths.length > 0) {
          showHdfsLeaf({
            paths: options.paths,
            scroll: options.scroll
          });
        }
      } else {
        $.jHueNotify.error(data.error);
      }
    });
  }

  Plugin.prototype.showHdfsLeaf = showHdfsLeaf;

  const _paths = [];
  if (_this.options.initialPath != '/') {
    const _re = /\//g;
    let match;
    while ((match = _re.exec(_this.options.initialPath)) != null) {
      _paths.push(_this.options.initialPath.substr(0, match.index));
    }
    _paths.push(_this.options.initialPath);
  }

  if (_this.options.isS3) {
    _paths.shift();
    _paths[0] = 's3a://';
  }

  showHdfsLeaf({
    paths: _paths
  });
};

Plugin.prototype.setOptions = function(options) {
  this.options = $.extend({}, defaults, options);
};

$.fn[pluginName] = function(options) {
  return this.each(function() {
    if (!$.data(this, 'plugin_' + pluginName)) {
      $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
    }
  });
};

$[pluginName] = function(options) {
  if (typeof console != 'undefined') {
    console.warn('$(elem).jHueHdfsTree() is a preferred call method.');
  }
  $(options.element).jHueHdfsTree(options);
};
