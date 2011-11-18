/*
* jHue fileChooser plugin
*/
;(function ($, window, document, undefined) {

	var pluginName = "jHueFileChooser",
	defaults = {
		initialPath: "",
		createFolder: true,
		uploadFile: true,
		onFileChoose: function(){}
	};

	function Plugin(element, options) {
		this.element = element;
		this.options = $.extend({}, defaults, options) ;
		this._defaults = defaults;
		this._name = pluginName;
		this.init();
	}
	
	Plugin.prototype.setOptions = function(options) {
		this.options = $.extend({}, defaults, options) ;
	};

	Plugin.prototype.navigateTo = function (path) {
		var _parent = this;
		currentPath = path;
		$(_parent.element).empty();
		$.getJSON("/filebrowser/chooser"+path, function(data){
			var _flist = $("<ul>").addClass("unstyled");
			$(data.files).each(function(cnt, file){
				var _f = $("<li>");
				var _flink = $("<a>");
				_flink.attr("href","#").text(file.name).appendTo(_f);
				if (file.type == "dir"){
					_f.addClass("folder");
					_flink.click(function(){
						_parent.navigateTo(file.path);
					});
				}
				if (file.type == "file"){
					_f.addClass("file");
					_flink.click(function(){
						_parent.options.onFileChoose(file.path)
					});
				}
				_f.appendTo(_flist);
			});
			_flist.appendTo($(_parent.element));
			var _actions = $("<div>").addClass("clearfix").attr('id', 'actionsDiv');
			var _uploadFileBtn;
			var _createFolderBtn;
			if (_parent.options.uploadFile){
				_uploadFileBtn = $("<div>").attr('id', 'file-uploader');
				_uploadFileBtn.appendTo(_actions);
				
			
				if ($.fn.upload){

					//_uploadFileBtn.upload();
				}
			}
			$("<span> </span>").appendTo(_actions);
			if (_parent.options.createFolder){
				_createFolderBtn = $("<button>").addClass("btn").addClass("small").text("Create folder");
				_createFolderBtn.appendTo(_actions);
				var _createFolderDetails = $("<div>").css("padding-top","10px");
				_createFolderDetails.hide();
				
				var _folderName = $("<input>").attr("type","text").attr("placeholder","Folder name").appendTo(_createFolderDetails);
				$("<span> </span>").appendTo(_createFolderDetails);
				var _folderBtn = $("<input>").attr("type","button").attr("value","Create").addClass("btn primary").appendTo(_createFolderDetails);
				$("<span> or </span>").appendTo(_createFolderDetails);
				var _folderCancel = $("<a>").attr("href","#").text("cancel").appendTo(_createFolderDetails);
				_folderCancel.click(function(){
					if (_uploadFileBtn){
						_uploadFileBtn.removeClass("disabled");
					}
					_createFolderBtn.removeClass("disabled");
					_createFolderDetails.slideUp();
				});
				_folderBtn.click(function(){
					$.ajax({
						type: "POST",
						url: "/filebrowser/mkdir",
						data: {
							name: _folderName.val(),
							path: path
						},
						beforeSend: function(xhr){ 
							xhr.setRequestHeader("X-Requested-With", "Hue"); // need to override the default one because otherwise Django returns HTTP 500
						},
						success: function(xhr, status){
							if (status == "success"){
								_parent.navigateTo(path);
								if (_uploadFileBtn){
									_uploadFileBtn.removeClass("disabled");
								}
								_createFolderBtn.removeClass("disabled");
								_createFolderDetails.slideUp();
							}
						}
					});
					
				});
				
				_createFolderDetails.appendTo(_actions);
				
				_createFolderBtn.click(function(){
					if (_uploadFileBtn){
						_uploadFileBtn.addClass("disabled");
					}
					_createFolderBtn.addClass("disabled");
					_createFolderDetails.slideDown();
				});
			}
			_actions.appendTo($(_parent.element));
			initUploader(path, _parent);
		});
		
	};
	function initUploader(path, _parent){
		completeRefreshPath = path;
		var uploader = new qq.FileUploader({
            element: document.getElementById('file-uploader'),
            action: '/filebrowser/upload',
            params:{
                dest: path,
                fileFieldLabel: 'hdfs_file'
            },
            onComplete:function(id, fileName, responseJSON){
				_parent.navigateTo(path);
            },
            debug: true
        });
	}

	Plugin.prototype.init = function () {
		if ($.trim(this.options.initialPath)!=""){
			this.navigateTo(this.options.initialPath);
		}
		else {
			this.navigateTo("/");
		}
	};

	$.fn[pluginName] = function (options) {
		return this.each(function () {
			if (!$.data(this, 'plugin_' + pluginName)) {
				$.data(this, 'plugin_' + pluginName, new Plugin( this, options));
			}
			else {
				$.data(this, 'plugin_' + pluginName).setOptions(options);
			}
		});
	}

})(jQuery, window, document );