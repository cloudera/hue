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

import $ from 'jquery';
import * as ko from 'knockout';
import qq from 'ext/fileuploader.custom';

import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

/*
 * jHue fileChooser plugin
 */

const pluginName = 'jHueFileChooser',
  defaults = {
    initialPath: '',
    forceRefresh: false,
    errorRedirectPath: '',
    createFolder: true,
    uploadFile: true,
    selectFolder: false,
    suppressErrors: false,
    displayOnlyFolders: false,
    showExtraHome: false,
    extraHomeProperties: {},
    filterExtensions: '',
    labels: {
      BACK: 'Back',
      SELECT_FOLDER: 'Select this folder',
      CREATE_FOLDER: 'Create folder',
      FOLDER_NAME: 'Folder name',
      CANCEL: 'Cancel',
      FILE_NOT_FOUND: 'The file has not been found',
      UPLOAD_FILE: 'Upload a file',
      FAILED: 'Failed',
      HOME: 'Home'
    },
    filesystems: ['hdfs'],
    filesysteminfo: {
      '': {
        scheme: '',
        root: '/',
        home: '/?default_to_home',
        icon: {
          brand: 'fa-files-o',
          home: 'fa-home'
        },
        label: {
          home: 'home',
          name: 'HDFS'
        }
      },
      hdfs: {
        scheme: '',
        root: '/',
        home: '/?default_to_home',
        icon: {
          brand: 'fa-files-o',
          home: 'fa-home'
        },
        label: {
          home: 'home',
          name: 'HDFS'
        }
      },
      s3a: {
        scheme: 's3a',
        root: 's3a://',
        home: 's3a://',
        icon: {
          brand: 'fa-cubes',
          home: 'fa-cubes'
        },
        label: {
          home: '',
          name: 'S3'
        }
      },
      adl: {
        scheme: 'adl',
        root: 'adl:/',
        home: 'adl:/',
        icon: {
          svg: {
            brand: '#hi-adls',
            home: '#hi-adls'
          },
          brand: 'fa-windows',
          home: 'fa-windows'
        },
        label: {
          home: '',
          name: 'ADLS'
        }
      },
      abfs: {
        scheme: 'abfs',
        root: 'abfs://',
        home: 'abfs://',
        icon: {
          svg: {
            brand: '#hi-adls',
            home: '#hi-adls'
          },
          brand: 'fa-windows',
          home: 'fa-windows'
        },
        label: {
          home: '',
          name: 'ABFS'
        }
      }
    },
    fsSelected: 'hdfs',
    user: '',
    onNavigate: function () {},
    onFileChoose: function () {},
    onFolderChoose: function () {},
    onFolderChange: function () {},
    onError: function () {}
  },
  STORAGE_PREFIX = 'hueFileBrowserLastPathForUser_';

const DEFAULT_I18n = {
  BACK: I18n('Back'),
  SELECT_FOLDER: I18n('Select this folder'),
  CREATE_FOLDER: I18n('Create folder'),
  FOLDER_NAME: I18n('Folder name'),
  CANCEL: I18n('Cancel'),
  FILE_NOT_FOUND: I18n('The file has not been found'),
  UPLOAD_FILE: I18n('Upload a file'),
  FAILED: I18n('Failed')
};

function Plugin(element, options) {
  this.element = element;
  $(element).data('jHueFileChooser', this);

  this.options = $.extend({}, defaults, { user: window.LOGGED_USERNAME }, options);
  this.options.labels = $.extend({}, defaults.labels, DEFAULT_I18n, options ? options.labels : {});
  this._defaults = defaults;
  this._name = pluginName;
  this.previousPath = '';
  this.init();
}

Plugin.prototype.setOptions = function (options) {
  const self = this;
  self.options = $.extend({}, defaults, { user: window.LOGGED_USERNAME }, options);
  self.options.labels = $.extend({}, defaults.labels, DEFAULT_I18n, options ? options.labels : {});
  const initialPath = $.trim(self.options.initialPath);
  const scheme = initialPath && initialPath.substring(0, initialPath.indexOf(':'));
  if (scheme && scheme.length) {
    self.options.fsSelected = scheme;
  }

  $(self.element).find('.filechooser-services li').removeClass('active');
  $(self.element)
    .find('.filechooser-services li[data-fs="' + self.options.fsSelected + '"]')
    .addClass('active');

  if (self.options.forceRefresh) {
    if (initialPath != '') {
      self.navigateTo(self.options.initialPath);
    } else if (
      $.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected) != null
    ) {
      self.navigateTo($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected));
    } else {
      self.navigateTo('/?default_to_home');
    }
  } else if (initialPath != '') {
    self.navigateTo(self.options.initialPath);
  } else if ($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected) != null) {
    self.navigateTo($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected));
  }
};

function getScheme(path) {
  const index = path.indexOf('://');
  return index >= 0 ? path.substring(0, index) : 'hdfs';
}

function getFs(scheme) {
  if (scheme === 'adl') {
    return 'adls';
  } else if (scheme === 's3a') {
    return 's3';
  } else if (!scheme || scheme === 'hdfs') {
    return 'hdfs';
  } else {
    return scheme;
  }
}

Plugin.prototype.setFileSystems = function (filesystems) {
  const self = this;
  let filters, filesystemsFiltered;
  self.options.filesystems = [];
  Object.keys(filesystems).forEach(k => {
    if (filesystems[k]) {
      self.options.filesystems.push(k);
    }
  });
  self.options.filesystems.sort();
  if (self.options.filesystemsFilter) {
    filters = self.options.filesystemsFilter.reduce((filters, fs) => {
      filters[fs] = true;
      return filters;
    }, {});
    filesystemsFiltered = self.options.filesystems.filter(fs => {
      return filters[fs];
    });
  } else {
    filesystemsFiltered = self.options.filesystems;
  }

  $(self.element).data('fs', filesystemsFiltered);
  if (filesystemsFiltered.length > 1) {
    const $ul = $('<ul>').addClass('nav nav-list').css('border', 'none');
    filesystemsFiltered.forEach(fs => {
      const filesysteminfo = self.options.filesysteminfo;
      const $li = $('<li>')
        .attr('data-fs', fs)
        .addClass(self.options.fsSelected === fs ? 'active' : '')
        .html(
          '<a class="pointer" style="padding-left: 6px">' +
            (filesysteminfo[fs] ? filesysteminfo[fs].label.name : fs.toUpperCase()) +
            '</a>'
        );
      $li.on('click', function () {
        $(this).siblings().removeClass('active');
        $(this).addClass('active');
        self.options.fsSelected = fs;
        const storedPath = $.totalStorage(
          STORAGE_PREFIX + self.options.user + self.options.fsSelected
        );
        if (storedPath !== null) {
          if (filesysteminfo[fs] && storedPath.toLowerCase().indexOf(fs) === -1) {
            self.navigateTo(filesysteminfo[fs].home);
          } else {
            self.navigateTo(storedPath);
          }
        } else {
          self.navigateTo(filesysteminfo[fs] ? filesysteminfo[fs].home : '/?default_to_home');
        }
      });
      $li.appendTo($ul);
    });
    $(self.element).find('.filechooser-services').empty().width(80);
    $(self.element)
      .find('.filechooser-tree')
      .width(480)
      .css('paddingLeft', '6px')
      .css('borderLeft', '1px solid #EEE')
      .css('marginLeft', '80px')
      .css('min-height', '330px');
    $ul.appendTo($(self.element).find('.filechooser-services'));
  }
};

//TODO: refactor this method to template
Plugin.prototype.navigateTo = function (path) {
  const _parent = this;
  $(_parent.element)
    .find('.filechooser-tree')
    .html('<i style="font-size: 24px; color: #DDD" class="fa fa-spinner fa-spin"></i>');
  let pageSize = '?pagesize=1000';
  const index = path.indexOf('?');
  if (index > -1) {
    pageSize = path.substring(index) + pageSize.replace(/\?/, '&');
    path = path.substring(0, index);
  }
  $.getJSON('/filebrowser/view=' + encodeURIComponent(path) + pageSize, data => {
    $(_parent.element).find('.filechooser-tree').empty();

    path = data.current_dir_path || path; // use real path.
    const _flist = $('<ul>').addClass('unstyled').css({
      height: '260px',
      'overflow-y': 'auto'
    });
    const $homeBreadcrumb = $('<ul>').addClass('hue-breadcrumbs').css({
      padding: '0',
      marginLeft: '0',
      float: 'left',
      'white-space': 'nowrap'
    });
    const _home = $('<li>').css({ 'padding-top': '6px' });
    //var filesysteminfo = self.options.filesysteminfo;
    const fs = _parent.options.filesysteminfo[_parent.options.fsSelected || 'hdfs'];
    const el = fs.icon.svg
      ? '<svg class="hi"><use xlink:href="' + fs.icon.svg.home + '"></use></svg>'
      : '<i class="fa ' + fs.icon.home + '"></i> ' + fs.label.home;
    const _homelink = $('<a>')
      .addClass('nounderline')
      .html(el)
      .css('cursor', 'pointer')
      .click(() => {
        _parent.navigateTo(fs.home);
      });

    _homelink.appendTo(_home);
    _home.appendTo($homeBreadcrumb);

    $('<span>').addClass('divider').css('margin-right', '20px').appendTo(_home);

    if (data.error || (data.title != null && data.title == 'Error')) {
      $homeBreadcrumb.appendTo($(_parent.element).find('.filechooser-tree'));
      $("<div class='clearfix'>").appendTo($(_parent.element).find('.filechooser-tree'));
      const _errorMsg = $('<div>')
        .addClass('alert')
        .addClass('alert-error')
        .text(data.message ? data.message : data.error);
      _errorMsg.appendTo($(_parent.element).find('.filechooser-tree'));
      //TODO: allow user to user breadcrums when there is an error
      const _previousLink = $('<a>')
        .addClass('btn')
        .text(_parent.options.labels.BACK)
        .click(() => {
          function getParentPath(path) {
            if (!path) {
              return path;
            }
            const indexFirst = path.indexOf('/');
            let indexLast = path.lastIndexOf('/');
            if (indexLast - indexFirst > 1 && indexLast == path.length - 1) {
              indexLast = path.substring(0, path.length - 1).lastIndexOf('/');
            }
            return indexLast - indexFirst > 1 && indexLast > 0
              ? path.substring(0, indexLast + 1)
              : path;
          }
          const next =
            path !== _parent.previousPath && getScheme(path) === getScheme(_parent.previousPath)
              ? _parent.previousPath || '/'
              : getParentPath(path) || '/';
          _parent.options.onFolderChange(next);
          _parent.navigateTo(next);
        });
      _previousLink.appendTo($(_parent.element).find('.filechooser-tree'));
    } else {
      if (data.type == 'file') {
        _parent.navigateTo(data.view.dirname);
        return;
      }
      $.totalStorage(STORAGE_PREFIX + _parent.options.user + _parent.options.fsSelected, path);
      _parent.previousPath = path;
      _parent.options.onNavigate(_parent.previousPath);

      const $search = $('<div>')
        .html(
          '<i class="fa fa-refresh inactive-action pointer" style="position: absolute; top: 8px; margin-left: -18px"></i> <i class="fa fa-search inactive-action pointer" style="position: absolute; top: 8px"></i><input type="text" class="small-search" style="display: none; width: 0; padding: 2px; padding-left: 20px">'
        )
        .css({
          position: 'absolute',
          right: '10px',
          'background-color': '#FFF'
        });

      const slideOutInput = () => {
        $search.find('input').animate(
          {
            width: '0'
          },
          100,
          () => {
            $search.find('input').hide();
            $search.find('.fa-refresh').show();
          }
        );
      };

      const $searchInput = $search.find('input');
      const tog = v => (v ? 'addClass' : 'removeClass');
      $searchInput.addClass('clearable');
      $searchInput
        .on('input', function () {
          $searchInput[tog(this.value)]('x');
        })
        .on('mousemove', function (e) {
          $searchInput[tog(this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left)](
            'onX'
          );
        })
        .on('click', function (e) {
          if (this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left) {
            $searchInput.removeClass('x onX').val('');
          }
        });
      if (!isIE11) {
        $searchInput.on('blur', e => {
          if ($searchInput.val() === '') {
            slideOutInput();
          }
        });
      }

      $search.find('.fa-search').on('click', () => {
        if ($searchInput.is(':visible')) {
          slideOutInput();
        } else {
          $search.find('.fa-refresh').hide();
          $searchInput.show().animate(
            {
              width: '100px'
            },
            100,
            () => {
              $searchInput.focus();
            }
          );
        }
      });

      $search.find('.fa-refresh').on('click', () => {
        _parent.navigateTo(path);
      });

      $search.appendTo($(_parent.element).find('.filechooser-tree'));

      const $scrollingBreadcrumbs = $('<ul>').addClass('hue-breadcrumbs editable-breadcrumbs').css({
        padding: '5px 4px',
        border: '1px solid #CCC',
        'border-radius': '3px',
        marginLeft: '10px',
        marginBottom: '0',
        float: 'left',
        width: '300px',
        'overflow-x': 'scroll',
        'overflow-y': 'hidden',
        'white-space': 'nowrap'
      });

      if (ko && ko.bindingHandlers.delayedOverflow) {
        ko.bindingHandlers.delayedOverflow.init($scrollingBreadcrumbs[0]);
      }

      if (_parent.options.showExtraHome) {
        const _extraHome = $('<li>');
        const _extraHomelink = $('<a>')
          .addClass('nounderline')
          .html(
            '<i class="fa ' +
              _parent.options.extraHomeProperties.icon +
              '"></i> ' +
              _parent.options.extraHomeProperties.label
          )
          .css('cursor', 'pointer')
          .click(() => {
            _parent.navigateTo(_parent.options.extraHomeProperties.path);
          });
        _extraHomelink.appendTo(_extraHome);
        $('<span>').addClass('divider').css('margin-right', '20px').appendTo(_extraHome);
        _extraHome.appendTo($scrollingBreadcrumbs);
      }

      const $hdfsAutocomplete = $('<input type="text">')
        .addClass('editable-breadcrumb-input')
        .val(path)
        .hide();

      $scrollingBreadcrumbs.click(function (e) {
        if ($(e.target).is('ul') || $(e.target).hasClass('spacer')) {
          $(this).hide();
          $hdfsAutocomplete.show().focus();
        }
      });

      const $editBreadcrumbs = $('<li>').css('marginRight', '2px');
      const $crumbLink = $('<span>').addClass('spacer');
      $crumbLink.html('&nbsp;').appendTo($editBreadcrumbs);
      $editBreadcrumbs.appendTo($scrollingBreadcrumbs);
      if (typeof data.breadcrumbs != 'undefined' && data.breadcrumbs != null) {
        const _bLength = data.breadcrumbs.length;
        $(data.breadcrumbs).each((cnt, crumb) => {
          const _crumb = $('<li>');
          const _crumbLink = $('<a>');
          const _crumbLabel = crumb.label != null && crumb.label != '' ? crumb.label : '/';
          _crumbLink.attr('href', 'javascript:void(0)').text(_crumbLabel).appendTo(_crumb);
          if (cnt < _bLength - 1) {
            if (cnt > 0) {
              $('<span>').addClass('divider').text('/').appendTo(_crumb);
            } else {
              $('<span>').html('&nbsp;').appendTo(_crumb);
            }
          }
          _crumb.click(() => {
            const _url = crumb.url != null && crumb.url != '' ? crumb.url : '/';
            _parent.options.onFolderChange(_url);
            _parent.navigateTo(_url);
          });
          _crumb.appendTo($scrollingBreadcrumbs);
        });
      }
      $homeBreadcrumb.appendTo($(_parent.element).find('.filechooser-tree'));
      $scrollingBreadcrumbs.appendTo($(_parent.element).find('.filechooser-tree'));
      $hdfsAutocomplete.appendTo($(_parent.element).find('.filechooser-tree'));

      $hdfsAutocomplete.jHueHdfsAutocomplete({
        home: '/user/' + _parent.options.user + '/',
        skipEnter: true,
        skipKeydownEvents: true,
        onEnter: function (el) {
          const _url = el.val();
          _parent.options.onFolderChange(_url);
          _parent.navigateTo(_url);
          $('#jHueHdfsAutocomplete').hide();
        },
        onBlur: function () {
          $hdfsAutocomplete.hide();
          $scrollingBreadcrumbs.show();
        },
        smartTooltip: _parent.options.labels.SMART_TOOLTIP
      });

      $('<div>').addClass('clearfix').appendTo($(_parent.element).find('.filechooser-tree'));

      const resizeBreadcrumbs = window.setInterval(() => {
        if ($homeBreadcrumb.is(':visible') && $homeBreadcrumb.width() > 0) {
          window.clearInterval(resizeBreadcrumbs);
          $scrollingBreadcrumbs.width(
            $(_parent.element).find('.filechooser-tree').width() - $homeBreadcrumb.width() - 65
          );
        }
      }, 100);

      if (data.s3_listing_not_allowed) {
        $("<div class='clearfix'>").appendTo($(_parent.element).find('.filechooser-tree'));
        const _errorMsg = $('<div>')
          .addClass('alert')
          .addClass('alert-warn')
          .text(data.s3_listing_not_allowed);
        _errorMsg.appendTo($(_parent.element).find('.filechooser-tree'));

        $scrollingBreadcrumbs.hide();
        $hdfsAutocomplete.show();
        $hdfsAutocomplete.focus();
      }

      $(data.files).each((cnt, file) => {
        let _addFile = file.name !== '.';
        if (_parent.options.filterExtensions != '' && file.type == 'file') {
          const _allowedExtensions = _parent.options.filterExtensions.split(',');
          const _fileExtension = file.name.split('.').pop().toLowerCase();
          _addFile = _allowedExtensions.indexOf(_fileExtension) > -1;
        }
        if (_addFile) {
          const _f = $('<li>');
          const _flink = $('<a>');

          if (file.type == 'dir') {
            _flink.attr('href', 'javascript:void(0)');
            if (
              file.path.toLowerCase().indexOf('s3a://') == 0 &&
              (file.path.substr(6).indexOf('/') > -1 || file.path.substr(6) == '')
            ) {
              _flink.text(' ' + (cnt > 0 ? file.name : '..'));
            } else {
              _flink.text(' ' + (file.name != '' ? file.name : '..'));
            }
            if (_flink.text() !== ' ..') {
              _f.addClass('file-list-item');
            }
            _flink.appendTo(_f);
            if (
              file.path.toLowerCase().indexOf('s3a://') == 0 &&
              file.path.substr(5).indexOf('/') == -1
            ) {
              $("<i class='fa fa-cloud'></i>").prependTo(_flink);
            } else {
              $("<i class='fa fa-folder'></i>").prependTo(_flink);
            }
            _flink.click(() => {
              _parent.options.onFolderChange(file.path);
              _parent.navigateTo(file.path);
            });
          }
          if (file.type == 'file' && !_parent.options.displayOnlyFolders) {
            _f.addClass('file-list-item');
            _flink
              .attr('href', 'javascript:void(0)')
              .text(' ' + (file.name != '' ? file.name : '..'))
              .appendTo(_f);
            $("<i class='fa fa-file-o'></i>").prependTo(_flink);
            _flink.click(() => {
              _parent.options.onFileChoose(file.path);
            });
          }
          _f.appendTo(_flist);
        }
      });

      _flist.appendTo($(_parent.element).find('.filechooser-tree'));

      $searchInput.jHueDelayedInput(() => {
        const filter = $searchInput.val().toLowerCase();
        let results = 0;
        $(_parent.element).find('.filechooser-tree .no-results').hide();
        $(_parent.element)
          .find('.filechooser-tree .file-list-item')
          .each(function () {
            if ($(this).text().toLowerCase().indexOf(filter) > -1) {
              $(this).show();
              results++;
            } else {
              $(this).hide();
            }
          });
        if (results == 0) {
          $(_parent.element).find('.filechooser-tree .no-results').show();
        }
      }, 300);

      const _actions = $('<div>').addClass('jHueFilechooserActions');
      let _showActions = false;
      let _uploadFileBtn;
      let _createFolderBtn;
      let _selectFolderBtn;
      if (_parent.options.uploadFile) {
        _uploadFileBtn = $('<div>')
          .attr('id', 'file-uploader')
          .addClass('fileChooserActionUploader');
        _uploadFileBtn.appendTo(_actions);
        _showActions = true;
        initUploader(path, _parent, _uploadFileBtn, _parent.options.labels);
      }
      if (_parent.options.selectFolder) {
        _selectFolderBtn = $('<a>').addClass('btn').text(_parent.options.labels.SELECT_FOLDER);
        if (_parent.options.uploadFile) {
          _selectFolderBtn.css('margin-top', '10px');
        }
        _selectFolderBtn.appendTo(_actions);
        _showActions = true;
        _selectFolderBtn.click(() => {
          _parent.options.onFolderChoose(path);
        });
      }
      $('<span> </span>').appendTo(_actions);
      if (_parent.options.createFolder) {
        _createFolderBtn = $('<a>').addClass('btn').text(_parent.options.labels.CREATE_FOLDER);
        if (_parent.options.uploadFile) {
          _createFolderBtn.css('margin-top', '10px');
        }
        _createFolderBtn.appendTo(_actions);
        _showActions = true;
        const _createFolderDetails = $('<form>')
          .css({ 'margin-top': '10px', position: 'fixed' })
          .addClass('form-inline');
        _createFolderDetails.hide();
        const _folderName = $('<input>')
          .attr('type', 'text')
          .attr('placeholder', _parent.options.labels.FOLDER_NAME)
          .appendTo(_createFolderDetails);
        $('<span> </span>').appendTo(_createFolderDetails);
        const _folderBtn = $('<input>')
          .attr('type', 'button')
          .attr('value', _parent.options.labels.CREATE_FOLDER)
          .addClass('btn primary')
          .appendTo(_createFolderDetails);
        $('<span> </span>').appendTo(_createFolderDetails);
        const _folderCancel = $('<input>')
          .attr('type', 'button')
          .attr('value', _parent.options.labels.CANCEL)
          .addClass('btn')
          .appendTo(_createFolderDetails);
        _folderCancel.click(() => {
          if (_uploadFileBtn) {
            _uploadFileBtn.removeClass('disabled');
          }
          _createFolderBtn.removeClass('disabled');
          _createFolderDetails.slideUp();
        });
        _folderBtn.click(() => {
          if (_folderName.val().length > 0) {
            $.ajax({
              type: 'POST',
              url: '/filebrowser/mkdir',
              data: {
                name: _folderName.val(),
                path: path
              },
              success: function (xhr, status) {
                if (status == 'success') {
                  _parent.navigateTo(path);
                  if (_uploadFileBtn) {
                    _uploadFileBtn.removeClass('disabled');
                  }
                  _createFolderBtn.removeClass('disabled');
                  _createFolderDetails.slideUp();
                }
              },
              error: function (xhr) {
                $(document).trigger('error', xhr.responseText);
              }
            });
          }
        });

        _createFolderDetails.appendTo(_actions);

        _createFolderBtn.click(() => {
          if (_uploadFileBtn) {
            _uploadFileBtn.addClass('disabled');
          }
          _createFolderBtn.addClass('disabled');
          _createFolderDetails.slideDown();
        });
      }
      if (_showActions) {
        _actions.appendTo($(_parent.element).find('.filechooser-tree'));
      }

      window.setTimeout(() => {
        $(_parent.element).parent().scrollTop(0);
        $scrollingBreadcrumbs.animate({
          scrollLeft: $scrollingBreadcrumbs.width()
        });
      }, 0);
    }
  }).fail(e => {
    if (!_parent.options.suppressErrors) {
      $(document).trigger('info', _parent.options.labels.FILE_NOT_FOUND);
      _parent.options.onError();
    }
    if (e.status === 404 || e.status === 500) {
      const fs = _parent.options.filesysteminfo[_parent.options.fsSelected || 'hdfs'];
      _parent.navigateTo(
        _parent.options.errorRedirectPath !== '' ? _parent.options.errorRedirectPath : fs.home
      );
    } else {
      console.error(e);
      $(document).trigger('error', e.statusText);
    }
  });
};

let num_of_pending_uploads = 0;

function initUploader(path, _parent, el, labels) {
  new qq.FileUploader({
    element: el[0],
    action: '/filebrowser/upload/file',
    params: {
      dest: path,
      fileFieldLabel: 'hdfs_file'
    },
    onComplete: function (id, fileName, responseJSON) {
      num_of_pending_uploads--;
      if (responseJSON.status == -1) {
        $(document).trigger('error', responseJSON.data);
      } else if (!num_of_pending_uploads) {
        _parent.navigateTo(path);
        huePubSub.publish('assist.' + getFs(getScheme(path)) + '.refresh');
      }
    },
    onSubmit: function (id, fileName) {
      num_of_pending_uploads++;
    },
    template:
      '<div class="qq-uploader">' +
      '<div class="qq-upload-drop-area"><span></span></div>' +
      '<div class="qq-upload-button">' +
      labels.UPLOAD_FILE +
      '</div><br>' +
      '<ul class="qq-upload-list"></ul>' +
      '</div>',
    fileTemplate:
      '<li>' +
      '<span class="qq-upload-file"></span>' +
      '<span class="qq-upload-spinner"></span>' +
      '<span class="qq-upload-size"></span>' +
      '<a class="qq-upload-cancel" href="#">' +
      labels.CANCEL +
      '</a>' +
      '<span class="qq-upload-failed-text">' +
      labels.FAILED +
      '</span>' +
      '</li>',
    debug: false
  });
}

Plugin.prototype.init = function () {
  const self = this;
  $(self.element)
    .empty()
    .html(
      '<div class="filechooser-container" style="position: relative"><div class="filechooser-services" style="position: absolute"></div><div class="filechooser-tree" style="width: 560px"></div></div>'
    );
  $.post('/filebrowser/api/get_filesystems', data => {
    const initialPath = $.trim(self.options.initialPath);
    const scheme = initialPath && initialPath.substring(0, initialPath.indexOf(':'));
    if (data && data.status === 0) {
      if (scheme && scheme.length && data.filesystems[scheme]) {
        self.options.fsSelected = scheme;
      }
      self.setFileSystems(data.filesystems);
    }
    if (initialPath != '') {
      self.navigateTo(self.options.initialPath);
    } else if (
      $.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected) != null
    ) {
      self.navigateTo($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected));
    } else {
      self.navigateTo('/?default_to_home');
    }
  });
};

$.fn[pluginName] = function (options) {
  return this.each(function () {
    if (!$.data(this, 'plugin_' + pluginName)) {
      $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
    } else {
      $.data(this, 'plugin_' + pluginName).setOptions(options);
    }
  });
};
