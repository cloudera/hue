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
/*
 * jHue fileChooser plugin
 */
;
(function ($, window, document, undefined) {

  var pluginName = "jHueFileChooser",
    defaults = {
      initialPath: "",
      forceRefresh: false,
      errorRedirectPath: "",
      createFolder: true,
      uploadFile: true,
      selectFolder: false,
      suppressErrors: false,
      displayOnlyFolders: false,
      showExtraHome: false,
      extraHomeProperties: {},
      filterExtensions: "",
      labels: {
        BACK: "Back",
        SELECT_FOLDER: "Select this folder",
        CREATE_FOLDER: "Create folder",
        FOLDER_NAME: "Folder name",
        CANCEL: "Cancel",
        FILE_NOT_FOUND: "The file has not been found",
        UPLOAD_FILE: "Upload a file",
        FAILED: "Failed",
        HOME: "Home"
      },
      filesystems: ['hdfs'],
      filesysteminfo: {
        "": {
          scheme: "",
          root: "/",
          home: "/?default_to_home",
          icon: {
            brand: "fa-files-o",
            home: "fa-home",
          },
          label : {
            home: "home",
            name: "HDFS",
          }
        },
        hdfs: {
          scheme: "",
          root: "/",
          home: "/?default_to_home",
          icon: {
            brand: "fa-files-o",
            home: "fa-home",
          },
          label : {
            home: "home",
            name: "HDFS",
          }
        },
        s3a: {
          scheme: "s3a",
          root: "s3a://",
          home: "s3a://",
          icon: {
            brand: "fa-cubes",
            home: "fa-cubes",
          },
          label : {
            home: "",
            name: "S3"
          }
        },
        adl: {
          scheme: "adl",
          root: "adl:/",
          home: "adl:/",
          icon: {
            svg:{
              brand: "#hi-adls",
              home: "#hi-adls"
            },
            brand: "fa-windows",
            home: "fa-windows"
          },
          label : {
            home: "",
            name: "ADLS"
          }
        }
      },
      fsSelected: 'hdfs',
      user: "",
      onNavigate: function () {
      },
      onFileChoose: function () {
      },
      onFolderChoose: function () {
      },
      onFolderChange: function () {
      },
      onError: function () {
      }
    },
    STORAGE_PREFIX = "hueFileBrowserLastPathForUser_";

  function Plugin(element, options) {
    this.element = element;
    $(element).data('jHueFileChooser', this);

    this.options = $.extend({}, defaults, { user: LOGGED_USERNAME }, options);
    this.options.labels = $.extend({}, defaults.labels, HUE_I18n.jHueFileChooser, options ? options.labels : {});
    this._defaults = defaults;
    this._name = pluginName;
    this.previousPath = "";
    this.init();
  }

  Plugin.prototype.setOptions = function (options) {
    var self = this;
    self.options = $.extend({}, defaults, { user: LOGGED_USERNAME }, options);
    self.options.labels = $.extend({}, defaults.labels, HUE_I18n.jHueFileChooser, options ? options.labels : {});
    var initialPath = $.trim(self.options.initialPath);
    var scheme = initialPath && initialPath.substring(0,initialPath.indexOf(":"));
    if (scheme && scheme.length) {
      self.options.fsSelected = scheme;
    }

    $(self.element).find('.filechooser-services li').removeClass('active');
    $(self.element).find('.filechooser-services li[data-fs="' + self.options.fsSelected + '"]').addClass('active');

    if (self.options.forceRefresh) {
      if (initialPath != "") {
        self.navigateTo(self.options.initialPath);
      } else if ($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected) != null) {
        self.navigateTo($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected));
      } else {
        self.navigateTo("/?default_to_home");
      }
    } else {
      if (initialPath != "") {
        self.navigateTo(self.options.initialPath);
      } else if ($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected) != null) {
        self.navigateTo($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected));
      }
    }
  };

  function getScheme (path) {
    var index = path.indexOf("://");
    return index >= 0 ? path.substring(0, index) : "hdfs";
  }

  function getFs (scheme) {
    if (scheme === 'adl') {
      return 'adls';
    } else if (scheme === 's3a' ){
      return 's3';
    } else if (!scheme || scheme === 'hdfs') {
      return 'hdfs';
    } else {
      return scheme;
    }
  }

  Plugin.prototype.setFileSystems = function (filesystems) {
    var self = this, filters, filesystemsFiltered;
    self.options.filesystems = [];
    Object.keys(filesystems).forEach(function (k) {
      if (filesystems[k]) {
        self.options.filesystems.push(k);
      }
    });
    self.options.filesystems.sort();
    if (self.options.filesystemsFilter) {
      filters = self.options.filesystemsFilter.reduce(function(filters, fs) {
      filters[fs] = true;
      return filters;
    }, {});
      filesystemsFiltered = self.options.filesystems.filter(function(fs) {
        return filters[fs];
      });
    } else {
      filesystemsFiltered = self.options.filesystems;
    }

    $(self.element).data('fs', filesystemsFiltered);
    if (filesystemsFiltered.length > 1) {
      var $ul = $('<ul>').addClass('nav nav-list').css('border', 'none');
      filesystemsFiltered.forEach(function (fs) {
        var filesysteminfo = self.options.filesysteminfo;
        var $li = $('<li>').attr('data-fs', fs).addClass(self.options.fsSelected === fs ? 'active' : '').html('<a class="pointer" style="padding-left: 6px">' + (filesysteminfo[fs] ? filesysteminfo[fs].label.name : fs.toUpperCase()) + '</a>');
        $li.on('click', function () {
          $(this).siblings().removeClass('active');
          $(this).addClass('active');
          self.options.fsSelected = fs;
          var storedPath = $.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected);
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
      $(self.element).find('.filechooser-tree').width(480).css('paddingLeft', '6px').css('borderLeft', '1px solid #EEE').css('marginLeft', '80px').css('min-height', '330px');
      $ul.appendTo($(self.element).find('.filechooser-services'));
    }
  };

  //TODO: refactor this method to template
  Plugin.prototype.navigateTo = function (path) {
    var _parent = this;
    $(_parent.element).find('.filechooser-tree').html("<i style=\"font-size: 24px; color: #DDD\" class=\"fa fa-spinner fa-spin\"></i>");
    var pageSize = '?pagesize=1000';
    if (path.indexOf('?') > -1) {
      pageSize = pageSize.replace(/\?/, '&');
    }
    $.getJSON("/filebrowser/view=" + path + pageSize, function (data) {
      $(_parent.element).find('.filechooser-tree').empty();

      path = data.current_dir_path || path; // use real path.
      var _flist = $("<ul>").addClass("unstyled").css({
        'height': '260px',
        'overflow-y': 'auto'
      });
      var $homeBreadcrumb = $("<ul>").addClass("hue-breadcrumbs").css({
        'padding': '0',
        'marginLeft': '0',
        'float': 'left',
        'white-space': 'nowrap'
      });
      var _home = $("<li>");
      //var filesysteminfo = self.options.filesysteminfo;
      var fs = _parent.options.filesysteminfo[_parent.options.fsSelected || "hdfs"];
      var el = fs.icon.svg ? '<svg class="hi"><use xlink:href="'+fs.icon.svg.home+'"></use></svg>' : '<i class="fa '+fs.icon.home+'"></i> ' + fs.label.home;
      var _homelink = $("<a>").addClass("nounderline").html(el).css("cursor", "pointer").click(function () {
        _parent.navigateTo(fs.home);
      });

      _homelink.appendTo(_home);
      _home.appendTo($homeBreadcrumb);

      $("<span>").addClass("divider").css("margin-right", "20px").appendTo(_home);

      if (data.error || (data.title != null && data.title == "Error")) {
        $homeBreadcrumb.appendTo($(_parent.element).find('.filechooser-tree'));
        $("<div class='clearfix'>").appendTo($(_parent.element).find('.filechooser-tree'));
        var _errorMsg = $("<div>").addClass("alert").addClass("alert-error").text(data.message ? data.message : data.error);
        _errorMsg.appendTo($(_parent.element).find('.filechooser-tree'));
        //TODO: allow user to user breadcrums when there is an error
        var _previousLink = $("<a>").addClass("btn").text(_parent.options.labels.BACK).click(function () {
          function getParentPath (path) {
            if (!path) return path;
            var indexFirst = path.indexOf("/");
            var indexLast = path.lastIndexOf("/");
            return indexLast - indexFirst > 1 && indexLast > 0 ? path.substring(0, indexLast + 1) : path;
          }
          var next = path !== _parent.previousPath && getScheme(path) === getScheme(_parent.previousPath) ? _parent.previousPath : getParentPath(path);
          _parent.options.onFolderChange(next);
          _parent.navigateTo(next);
        });
        _previousLink.appendTo($(_parent.element).find('.filechooser-tree'));
      } else {
        if (data.type == "file") {
          _parent.navigateTo(data.view.dirname);
          return;
        }
        $.totalStorage(STORAGE_PREFIX + _parent.options.user + _parent.options.fsSelected, path);
        _parent.previousPath = path;
        _parent.options.onNavigate(_parent.previousPath);

        var $search = $('<div>').html('<i class="fa fa-refresh inactive-action pointer" style="position: absolute; top: 3px; margin-left: -16px"></i> <i class="fa fa-search inactive-action pointer" style="position: absolute; top: 3px"></i><input type="text" class="small-search" style="display: none; width: 0; padding: 2px; padding-left: 20px">').css({
          'position': 'absolute',
          'right': '20px',
          'background-color': '#FFF'
        });

        function slideOutInput() {
          $search.find('input').animate({
            'width': '0'
          }, 100, function(){
            $search.find('input').hide();
            $search.find('.fa-refresh').show();
          });
        }

        var $searchInput = $search.find('input');
        function tog(v) {
          return v ? "addClass" : "removeClass";
        }
        $searchInput.addClass("clearable");
        $searchInput.on("input", function () {
          $searchInput[tog(this.value)]("x");
        })
        .on("mousemove", function (e) {
          $searchInput[tog(this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left)]("onX");
        })
        .on("click", function (e) {
          if (this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left) {
            $searchInput.removeClass("x onX").val("");
          }
        });
        if (!isIE11) {
          $searchInput.on("blur", function (e) {
            if ($searchInput.val() === ''){
              slideOutInput();
            }
          });
        }

        $search.find('.fa-search').on('click', function(){
          if ($searchInput.is(':visible')){
            slideOutInput();
          } else {
            $search.find('.fa-refresh').hide();
            $searchInput.show().animate({
              'width': '100px'
            }, 100, function(){
              $searchInput.focus();
            });
          }
        });

        $search.find('.fa-refresh').on('click', function(){
          _parent.navigateTo(path);
        });

        $search.appendTo($(_parent.element).find('.filechooser-tree'));

        var $scrollingBreadcrumbs = $("<ul>").addClass("hue-breadcrumbs editable-breadcrumbs").css({
          'padding': '0',
          'marginLeft': '10px',
          'marginBottom': '0',
          'paddingRight': '10px',
          'float': 'left',
          'width': '300px',
          'overflow-x': 'scroll',
          'overflow-y': 'hidden',
          'white-space': 'nowrap'
        });

        if (ko && ko.bindingHandlers.delayedOverflow) {
          ko.bindingHandlers.delayedOverflow.init($scrollingBreadcrumbs[0]);
        }

        if (_parent.options.showExtraHome) {
          var _extraHome = $("<li>");
          var _extraHomelink = $("<a>").addClass("nounderline").html('<i class="fa ' + _parent.options.extraHomeProperties.icon + '"></i> ' + _parent.options.extraHomeProperties.label).css("cursor", "pointer").click(function () {
            _parent.navigateTo(_parent.options.extraHomeProperties.path);
          });
          _extraHomelink.appendTo(_extraHome);
          $("<span>").addClass("divider").css("margin-right", "20px").appendTo(_extraHome);
          _extraHome.appendTo($scrollingBreadcrumbs);
        }

        var $hdfsAutocomplete = $('<input type="text">').addClass('editable-breadcrumb-input').val(path).hide();

        $scrollingBreadcrumbs.click(function (e) {
          if ($(e.target).is('ul') || $(e.target).hasClass('spacer')) {
            $(this).hide();
            $hdfsAutocomplete.show().focus();
          }
        });

        var $editBreadcrumbs = $("<li>").css('marginRight', '2px');
        var $crumbLink = $("<span>").addClass('spacer');
        $crumbLink.html('&nbsp;').appendTo($editBreadcrumbs);
        $editBreadcrumbs.appendTo($scrollingBreadcrumbs);
        if (typeof data.breadcrumbs != "undefined" && data.breadcrumbs != null) {
          var _bLength = data.breadcrumbs.length;
          $(data.breadcrumbs).each(function (cnt, crumb) {
            var _crumb = $("<li>");
            var _crumbLink = $("<a>");
            var _crumbLabel = (crumb.label != null && crumb.label != "") ? crumb.label : "/";
            _crumbLink.attr("href", "javascript:void(0)").text(_crumbLabel).appendTo(_crumb);
            if (cnt < _bLength - 1) {
              if (cnt > 0) {
                $("<span>").addClass("divider").text("/").appendTo(_crumb);
              } else {
                $("<span>").html("&nbsp;").appendTo(_crumb);
              }
            }
            _crumb.click(function () {
              var _url = (crumb.url != null && crumb.url != "") ? crumb.url : "/";
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
          home: "/user/" + _parent.options.user + "/",
          skipEnter: true,
          skipKeydownEvents: true,
          onEnter: function (el) {
            var _url = el.val();
            _parent.options.onFolderChange(_url);
            _parent.navigateTo(_url);
            $("#jHueHdfsAutocomplete").hide();
          },
          onBlur: function () {
            $hdfsAutocomplete.hide();
            $scrollingBreadcrumbs.show();
          },
          smartTooltip: _parent.options.labels.SMART_TOOLTIP
        });

        $('<div>').addClass('clearfix').appendTo($(_parent.element).find('.filechooser-tree'));

        var resizeBreadcrumbs = window.setInterval(function(){
          if ($homeBreadcrumb.is(':visible') && $homeBreadcrumb.width() > 0){
            window.clearInterval(resizeBreadcrumbs);
            $scrollingBreadcrumbs.width($(_parent.element).find('.filechooser-tree').width() - $homeBreadcrumb.width() - 65);
          }
        }, 100);

        $(data.files).each(function (cnt, file) {
          var _addFile = file.name !== '.';
          if (_parent.options.filterExtensions != "" && file.type == "file") {
            var _allowedExtensions = _parent.options.filterExtensions.split(",");
            var _fileExtension = file.name.split(".").pop().toLowerCase();
            _addFile = _allowedExtensions.indexOf(_fileExtension) > -1;
          }
          if (_addFile) {
            var _f = $("<li>");
            var _flink = $("<a>");

            if (file.type == "dir") {
              _flink.attr("href", "javascript:void(0)");
              if (file.path.toLowerCase().indexOf('s3a://') == 0 && (file.path.substr(6).indexOf('/') > -1 || file.path.substr(6) == '')) {
                _flink.text(" " + (cnt > 0 ? file.name : ".."))
              } else {
                _flink.text(" " + (file.name != "" ? file.name : ".."));
              }
              if (_flink.text() !== ' ..') {
                _f.addClass('file-list-item');
              }
              _flink.appendTo(_f);
              if (file.path.toLowerCase().indexOf('s3a://') == 0 && file.path.substr(5).indexOf('/') == -1) {
                $("<i class='fa fa-cloud'></i>").prependTo(_flink);
              } else {
                $("<i class='fa fa-folder'></i>").prependTo(_flink);
              }
              _flink.click(function () {
                _parent.options.onFolderChange(file.path);
                _parent.navigateTo(file.path);
              });
            }
            if (file.type == "file" && !_parent.options.displayOnlyFolders) {
              _f.addClass('file-list-item');
              _flink.attr("href", "javascript:void(0)").text(" " + (file.name != "" ? file.name : "..")).appendTo(_f);
              $("<i class='fa fa-file-o'></i>").prependTo(_flink);
              _flink.click(function () {
                _parent.options.onFileChoose(file.path);
              });
            }
            _f.appendTo(_flist);
          }
        });

        _flist.appendTo($(_parent.element).find('.filechooser-tree'));

        $searchInput.jHueDelayedInput(function () {
          var filter = $searchInput.val().toLowerCase();
          var results = 0;
          $(_parent.element).find('.filechooser-tree .no-results').hide();
          $(_parent.element).find('.filechooser-tree .file-list-item').each(function(){
            if ($(this).text().toLowerCase().indexOf(filter) > -1) {
              $(this).show();
              results++;
            } else {
              $(this).hide();
            }
          });
          if (results == 0){
            $(_parent.element).find('.filechooser-tree .no-results').show();
          }
        }, 300);

        var _actions = $("<div>").addClass("jHueFilechooserActions");
        var _showActions = false;
        var _uploadFileBtn;
        var _createFolderBtn;
        var _selectFolderBtn;
        if (_parent.options.uploadFile) {
          _uploadFileBtn = $("<div>").attr("id", "file-uploader").addClass('fileChooserActionUploader');
          _uploadFileBtn.appendTo(_actions);
          _showActions = true;
          initUploader(path, _parent, _uploadFileBtn, _parent.options.labels);
        }
        if (_parent.options.selectFolder) {
          _selectFolderBtn = $("<a>").addClass("btn").text(_parent.options.labels.SELECT_FOLDER);
          if (_parent.options.uploadFile) {
            _selectFolderBtn.css("margin-top", "10px");
          }
          _selectFolderBtn.appendTo(_actions);
          _showActions = true;
          _selectFolderBtn.click(function () {
            _parent.options.onFolderChoose(path);
          });
        }
        $("<span> </span>").appendTo(_actions);
        if (_parent.options.createFolder) {
          _createFolderBtn = $("<a>").addClass("btn").text(_parent.options.labels.CREATE_FOLDER);
          if (_parent.options.uploadFile) {
            _createFolderBtn.css("margin-top", "10px");
          }
          _createFolderBtn.appendTo(_actions);
          _showActions = true;
          var _createFolderDetails = $("<form>").css({"margin-top": "10px", "position": "fixed"}).addClass("form-inline");
          _createFolderDetails.hide();
          var _folderName = $("<input>").attr("type", "text").attr("placeholder", _parent.options.labels.FOLDER_NAME).appendTo(_createFolderDetails);
          $("<span> </span>").appendTo(_createFolderDetails);
          var _folderBtn = $("<input>").attr("type", "button").attr("value", _parent.options.labels.CREATE_FOLDER).addClass("btn primary").appendTo(_createFolderDetails);
          $("<span> </span>").appendTo(_createFolderDetails);
          var _folderCancel = $("<input>").attr("type", "button").attr("value", _parent.options.labels.CANCEL).addClass("btn").appendTo(_createFolderDetails);
          _folderCancel.click(function () {
            if (_uploadFileBtn) {
              _uploadFileBtn.removeClass("disabled");
            }
            _createFolderBtn.removeClass("disabled");
            _createFolderDetails.slideUp();
          });
          _folderBtn.click(function () {
            if (_folderName.val().length > 0) {
              $.ajax({
                type: "POST",
                url: "/filebrowser/mkdir",
                data: {
                  name: _folderName.val(),
                  path: path
                },
                success: function (xhr, status) {
                  if (status == "success") {
                    _parent.navigateTo(path);
                    if (_uploadFileBtn) {
                      _uploadFileBtn.removeClass("disabled");
                    }
                    _createFolderBtn.removeClass("disabled");
                    _createFolderDetails.slideUp();
                  }
                },
                error: function (xhr) {
                  $(document).trigger("error", xhr.responseText);
                }
              });
            }
          });

          _createFolderDetails.appendTo(_actions);

          _createFolderBtn.click(function () {
            if (_uploadFileBtn) {
              _uploadFileBtn.addClass("disabled");
            }
            _createFolderBtn.addClass("disabled");
            _createFolderDetails.slideDown();
          });
        }
        if (_showActions) {
          _actions.appendTo($(_parent.element).find('.filechooser-tree'));
        }

        window.setTimeout(function () {
          $(_parent.element).parent().scrollTop(0);
          $scrollingBreadcrumbs.animate({
            'scrollLeft': $scrollingBreadcrumbs.width()
          });
        }, 0);
      }
    }).error(function (e) {
      if (!_parent.options.suppressErrors) {
        $(document).trigger("info", _parent.options.labels.FILE_NOT_FOUND);
        _parent.options.onError();
      }
      if (e.status === 404 || e.status === 500) {
        var fs = _parent.options.filesysteminfo[_parent.options.fsSelected || "hdfs"];
        _parent.navigateTo(_parent.options.errorRedirectPath !== "" ? _parent.options.errorRedirectPath : fs.home);
      } else {
        console.error(e);
        $(document).trigger("error", e.statusText);
      }
    });
  };

  var num_of_pending_uploads = 0;

  function initUploader(path, _parent, el, labels) {
    var uploader = new qq.FileUploader({
      element: el[0],
      action: '/filebrowser/upload/file',
      params: {
        dest: path,
        fileFieldLabel: 'hdfs_file'
      },
      onComplete: function (id, fileName, responseJSON) {
        num_of_pending_uploads--;
        if (responseJSON.status == -1) {
          $(document).trigger("error", responseJSON.data);
        } else if (!num_of_pending_uploads) {
          _parent.navigateTo(path);
          window.huePubSub.publish('assist.' + getFs(getScheme(path)) + '.refresh');
        }
      },
      onSubmit: function (id, fileName) {
        num_of_pending_uploads++;
      },
      template: '<div class="qq-uploader">' +
      '<div class="qq-upload-drop-area"><span></span></div>' +
      '<div class="qq-upload-button">' + labels.UPLOAD_FILE + '</div><br>' +
      '<ul class="qq-upload-list"></ul>' +
      '</div>',
      fileTemplate: '<li>' +
      '<span class="qq-upload-file"></span>' +
      '<span class="qq-upload-spinner"></span>' +
      '<span class="qq-upload-size"></span>' +
      '<a class="qq-upload-cancel" href="#">' + labels.CANCEL + '</a>' +
      '<span class="qq-upload-failed-text">' + labels.FAILED + '</span>' +
      '</li>',
      debug: false
    });
  }

  Plugin.prototype.init = function () {
    var self = this;
    $(self.element).empty().html('<div class="filechooser-container" style="position: relative"><div class="filechooser-services" style="position: absolute"></div><div class="filechooser-tree" style="width: 560px"></div></div>');
    $.post('/filebrowser/api/get_filesystems', function (data) {
      var initialPath = $.trim(self.options.initialPath);
      var scheme = initialPath && initialPath.substring(0,initialPath.indexOf(":"));
      if (data && data.status === 0) {
        if (scheme && scheme.length && data.filesystems[scheme]) {
          self.options.fsSelected = scheme;
        }
        self.setFileSystems(data.filesystems);
      }
      if (initialPath != "") {
        self.navigateTo(self.options.initialPath);
      } else if ($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected) != null) {
        self.navigateTo($.totalStorage(STORAGE_PREFIX + self.options.user + self.options.fsSelected));
      } else {
        self.navigateTo("/?default_to_home");
      }
    });
  };

  $.fn[pluginName] = function (options) {
    return this.each(function () {
      if (!$.data(this, 'plugin_' + pluginName)) {
        $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
      }
      else {
        $.data(this, 'plugin_' + pluginName).setOptions(options);
      }
    });
  }

})(jQuery, window, document);
