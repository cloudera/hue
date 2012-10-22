/*
 * jHue fileChooser plugin
 */
;
(function ($, window, document, undefined) {

    var pluginName = "jHueFileChooser",
        // global variables (jHueFileChooserGlobals, useful for i18n) can be set on
        // desktop/templates/common_header.mako
        defaults = {
            initialPath:"",
            errorRedirectPath:"",
            createFolder:true,
            uploadFile:true,
            selectFolder:false,
            labels: {
                BACK: "Back",
                SELECT_FOLDER: "Select this folder",
                CREATE_FOLDER: "Create folder",
                FOLDER_NAME: "Folder name",
                CANCEL: "Cancel",
                FILE_NOT_FOUND: "The file has not been found",
                UPLOAD_FILE: "Upload a file",
                FAILED: "Failed"
            },
            onFileChoose:function () {
            },
            onFolderChoose:function () {
            },
            onFolderChange:function () {
            },
            onError:function () {
            }
        };

    function Plugin(element, options) {
        this.element = element;
        if (typeof jHueFileChooserGlobals != 'undefined') {
            var extendedDefaults = $.extend({}, defaults, jHueFileChooserGlobals);
            extendedDefaults.labels = $.extend({}, defaults.labels, jHueFileChooserGlobals.labels);
            this.options = $.extend({}, extendedDefaults, options);
            if (options != null){
                this.options.labels = $.extend({}, extendedDefaults.labels, options.labels);
            }
        }
        else {
            this.options = $.extend({}, defaults, options);
            if (options != null){
                this.options.labels = $.extend({}, defaults.labels, options.labels);
            }
        }
        this._defaults = defaults;
        this._name = pluginName;
        this.previousPath = "";
        this.init();
    }

    Plugin.prototype.setOptions = function (options) {
        this.options = $.extend({}, defaults, options);
        if ($.trim(this.options.initialPath) != "") {
            this.navigateTo(this.options.initialPath);
        }
    };

    Plugin.prototype.navigateTo = function (path) {
        var _parent = this;
        $(_parent.element).empty();
        $.getJSON("/filebrowser/chooser" + path, function (data) {
            path = data.current_dir_path; // use real path.
            var _flist = $("<ul>").addClass("unstyled");
            if (data.title != null && data.title == "Error") {
                var _errorMsg = $("<div>").addClass("alert").addClass("alert-error").text(data.message);
                _errorMsg.appendTo($(_parent.element));
                var _previousLink = $("<a>").addClass("btn").addClass("bnt-small").text(_parent.options.labels.BACK).click(function () {
                    _parent.options.onFolderChange(_parent.previousPath);
                    _parent.navigateTo(_parent.previousPath);
                });
                _previousLink.appendTo($(_parent.element));
            }
            else {
                if (data.type == "file") {
                    _parent.navigateTo(data.view.dirname);
                    return;
                }
                $.cookie("hueFileBrowserLastPath", path, { expires: 90 });
                _parent.previousPath = path;
                var _breadcrumbs = $("<ul>").addClass("hueBreadcrumb").css("padding", "0");
                var _home = $("<li>");
                var _homelink = $("<a>").addClass("nounderline").html('<i class="icon-home"></i> Home').css("cursor", "pointer").click(function () {
                    _parent.navigateTo("/?default_to_home");
                });
                _homelink.appendTo(_home);
                $("<span>").addClass("divider").css("margin-right", "20px").appendTo(_home);
                _home.appendTo(_breadcrumbs);
                var _bLength = data.breadcrumbs.length;
                $(data.breadcrumbs).each(function (cnt, crumb) {
                    var _crumb = $("<li>");
                    var _crumbLink = $("<a>");
                    var _crumbLabel = (crumb.label != null && crumb.label != "") ? crumb.label : "/";
                    _crumbLink.attr("href", "javascript:void(0)").text(_crumbLabel).appendTo(_crumb);
                    if (cnt < _bLength - 1) {
                        if (cnt > 0) {
                            $("<span>").addClass("divider").text("/").appendTo(_crumb);
                        }
                        else {
                            $("<span>").html("&nbsp;").appendTo(_crumb);
                        }
                    }
                    _crumb.click(function () {
                        var _url = (crumb.url != null && crumb.url != "") ? crumb.url : "/";
                        _parent.options.onFolderChange(_url);
                        _parent.navigateTo(_url);
                    });
                    _crumb.appendTo(_breadcrumbs);
                });
                _breadcrumbs.appendTo($(_parent.element));

                $(data.files).each(function (cnt, file) {
                    var _f = $("<li>");
                    var _flink = $("<a>");
                    _flink.attr("href", "javascript:void(0)").text(file.name).appendTo(_f);
                    if (file.type == "dir") {
                        _f.addClass("folder");
                        _f.click(function () {
                            _parent.options.onFolderChange(file.path);
                            _parent.navigateTo(file.path);
                        });
                    }
                    if (file.type == "file") {
                        _f.addClass("file");
                        _f.click(function () {
                            _parent.options.onFileChoose(file.path);
                        });
                    }
                    _f.appendTo(_flist);
                });
                _flist.appendTo($(_parent.element));
                var _actions = $("<div>").addClass("jHueFilechooserActions");
                var _showActions = false;
                var _uploadFileBtn;
                var _createFolderBtn;
                var _selectFolderBtn;
                if (_parent.options.uploadFile) {
                    _uploadFileBtn = $("<div>").attr("id", "file-uploader");
                    _uploadFileBtn.appendTo(_actions);
                    _showActions = true;
                    initUploader(path, _parent, _uploadFileBtn, _parent.options.labels);
                }
                if (_parent.options.selectFolder) {
                    _selectFolderBtn = $("<a>").addClass("btn").addClass("small").text(_parent.options.labels.SELECT_FOLDER);
                    if (_parent.options.uploadFile){
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
                    _createFolderBtn = $("<a>").addClass("btn").addClass("small").text(_parent.options.labels.CREATE_FOLDER);
                    if (_parent.options.uploadFile){
                        _createFolderBtn.css("margin-top", "10px");
                    }
                    _createFolderBtn.appendTo(_actions);
                    _showActions = true;
                    var _createFolderDetails = $("<form>").css("margin-top", "10px").addClass("well form-inline");
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
                        $.ajax({
                            type:"POST",
                            url:"/filebrowser/mkdir",
                            data:{
                                name:_folderName.val(),
                                path:path
                            },
                            beforeSend:function (xhr) {
                                xhr.setRequestHeader("X-Requested-With", "Hue"); // need to override the default one because otherwise Django returns HTTP 500
                            },
                            success:function (xhr, status) {
                                if (status == "success") {
                                    _parent.navigateTo(path);
                                    if (_uploadFileBtn) {
                                        _uploadFileBtn.removeClass("disabled");
                                    }
                                    _createFolderBtn.removeClass("disabled");
                                    _createFolderDetails.slideUp();
                                }
                            }
                        });

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
                if (_showActions){
                    _actions.appendTo($(_parent.element));
                }
            }
        }).error(function(){
            _parent.options.onError();
            _parent.navigateTo(_parent.options.errorRedirectPath != "" ? _parent.options.errorRedirectPath : "/?default_to_home");
            if ($.jHueNotify) {
                $.jHueNotify.info(_parent.options.labels.FILE_NOT_FOUND);
            }
        });
    };

    var num_of_pending_uploads = 0;
    function initUploader(path, _parent, el, labels) {
        var uploader = new qq.FileUploader({
            element:el[0],
            action:'/filebrowser/upload/file',
            params:{
                dest:path,
                fileFieldLabel:'hdfs_file'
            },
            onComplete:function (id, fileName, responseJSON) {
                num_of_pending_uploads--;
                if(num_of_pending_uploads == 0){
                    _parent.navigateTo(path);
                }
            },
            onSubmit: function(id, fileName){
                num_of_pending_uploads++;
            },
            template: '<div class="qq-uploader">' +
                '<div class="qq-upload-drop-area"><span></span></div>' +
                '<div class="qq-upload-button">' + labels.UPLOAD_FILE + '</div>' +
                '<ul class="qq-upload-list"></ul>' +
                '</div>',
            fileTemplate: '<li>' +
                '<span class="qq-upload-file"></span>' +
                '<span class="qq-upload-spinner"></span>' +
                '<span class="qq-upload-size"></span>' +
                '<a class="qq-upload-cancel" href="#">' + labels.CANCEL + '</a>' +
                '<span class="qq-upload-failed-text">' + labels.FAILED + '</span>' +
                '</li>',
            debug:false
        });
    }

    Plugin.prototype.init = function () {
        if ($.trim(this.options.initialPath) != "") {
            this.navigateTo(this.options.initialPath);
        }
        else if ($.cookie("hueFileBrowserLastPath") != null) {
            this.navigateTo($.cookie("hueFileBrowserLastPath"));
        }
        else {
            this.navigateTo("/?default_to_home");
        }
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
