var listDirOptionsElement = document.getElementById('listDirOptions');
listDirOptions = JSON.parse(listDirOptionsElement.textContent);
var _dragged;
var _dropzone;

ko.bindingHandlers.drag = {
  update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
    var dragElement = $(element);
    try {
      dragElement.draggable('destroy');
    }
    catch (e) {}
    var dragOptions = {
      helper: 'clone',
      revert: true,
      revertDuration: 0,
      start: function () {
        if ($(element).is('[draggable]')) {
          viewModel.selected(true);
        }
        _dragged = ko.utils.unwrapObservable(valueAccessor().value);
      },
      cursor: "move",
      delay: 300
    };
    dragElement.draggable(dragOptions).disableSelection();
  }
};

ko.bindingHandlers.drop = {
  update: function (element, valueAccessor) {
    var dropElement = $(element);
    try {
      dropElement.droppable('destroy');
    }
    catch (e) {}
    if (valueAccessor().enabled) {
      var dropOptions = {
        hoverClass: 'drag-hover',
        accept: '.draggable-fb',
        drop: function (event, ui) {
          var destpath = valueAccessor().value.path;

          dropElement.fadeOut(200, function () {
            dropElement.fadeIn(200);
          });

          if (destpath) {
            $('#moveDestination').val(destpath);
            fileBrowserViewModel.move('nomodal', _dragged);
          }
        }
      };
      dropElement.droppable(dropOptions);
    }
  }
};

var apiHelper = window.apiHelper;

// ajax modal windows
var openChownWindow = function (path, user, group, next) {
  $.ajax({
    url: "/filebrowser/chown",
    data: {"path": path, "user": user, "group": group, "next": next},
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-Requested-With", "Hue");
    },
    dataType: "html",
    success: function (data) {
      $("#changeOwnerModal").html(data);
      $("#changeOwnerModal").modal({
        keyboard:true,
        show:true
      });
    },
    error: function (xhr, textStatus, errorThrown) {
      huePubSub.publish('hue.global.error', {message: xhr.responseText});
      resetPrimaryButtonsStatus();
    }
  });
};

var fileExists = function (newName) {
  if (fileBrowserViewModel) {
    var files = fileBrowserViewModel.files();
    for (var i = 0; i < files.length; i++) {
      if (files[i].name == newName) {
        return true;
      }
    }
  }
  return false;
};

var resetActionbar = function() {
  $(".actionbar").attr("style", "min-width: 800px");
  $(".actionbar").data("originalWidth", $(".actionbar").width());
  $(".actionbarGhost").addClass("hide");
};

var stripHashes = function (str) {
  return str.replace(/#/gi, encodeURIComponent("#"));
};

var formatBytes = function (bytes, decimals) {
  if (bytes == -1) return window.I18n('Not available.');
  if (bytes == 0) return "0 Byte";
  var k = 1024;
  var dm = decimals + 1 || 3;
  var sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  var i = Math.floor(Math.log(bytes) / Math.log(k));
  return (bytes / Math.pow(k, i)).toPrecision(dm) + ' ' + sizes[i];
}

var Page = function (page) {
  if (page != null) {
    return {
      number: page.number,
      num_pages: page.num_pages,
      previous_page_number: page.previous_page_number,
      next_page_number: page.next_page_number,
      start_index: page.start_index,
      end_index: page.end_index,
      total_count: page.total_count
    }
  }
  return {
  }
};

var File = function (file) {
  file.tooltip = "";

  if (file.name == "."){
    file.tooltip = window.I18n('This folder');
  }

  if (file.name == ".."){
    file.tooltip = window.I18n('One level up');
  }

  return {
    name: file.name,
    path: file.path,
    url: file.url,
    type: file.type,
    permissions: file.rwx,
    mode: file.mode,
    isSentryManaged: file.is_sentry_managed,
    stats: {
      size: file.humansize,
      user: file.stats.user,
      group: file.stats.group,
      mtime: file.mtime,
      replication: file.stats.replication
    },
    isBucket: ko.pureComputed(function(){
      return (file.path.toLowerCase().indexOf('s3a://') == 0 && file.path.substr(6).indexOf('/') == -1) || (file.path.toLowerCase().indexOf('gs://') == 0 && file.path.substr(5).indexOf('/') == -1)
    }),
    selected: ko.observable(file.highlighted && fileBrowserViewModel.isArchive(file.name) || false),
    highlighted: ko.observable(file.highlighted || false),
    deleted: ko.observable(file.deleted || false),
    handleSelect: function (row, e) {
      e.preventDefault();
      e.stopPropagation();
      this.selected(!this.selected());
      if (!this.selected()) {
        hideContextMenu();
      }
      this.highlighted(false);
      this.deleted(false);
      fileBrowserViewModel.allSelected(false);
    },
    // display the context menu when an item is right/context clicked
    showContextMenu: function (row, e) {
      var cm = $('.context-menu'),
        actions = $('#ch-dropdown'),
        rect = document.querySelector('body').getBoundingClientRect();

      e.stopPropagation();

      // close the actions menu from button area if open
      if (actions.hasClass('open')) {
        actions.removeClass('open');
      }

      // display context menu and ensure it is on-screen
      if ($.inArray(row.name, ['..', '.Trash']) === -1) {
        this.selected(true);
        var verticalCorrection = 0;
        verticalCorrection = $('.page-content').scrollTop() - $('.navbar-default').height() - $('.banner').height();
        cm.css({ display: 'block', top: e.pageY - 15 + verticalCorrection, left: (e.offsetX < rect.right - 300 ) ? e.offsetX + 100 : e.offsetX - 250 });
      } else {
        cm.css({ display: 'none' });
      }
    },
    hovered: ko.observable(false),
    toggleHover: function (row, e) {
      this.hovered(! this.hovered());
    },
    tooltip:file.tooltip
  }
};

var Breadcrumb = function (breadcrumb) {
  return {
    url: breadcrumb.url,
    label: breadcrumb.label,
    show: function (breadcrumb, e) {
      var isLeftButton = (e.which || e.button) === 1;
      if (isLeftButton) {
        if (! (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey)) {
          e.stopPropagation();
          e.preventDefault();
          if (this.url == null || this.url == "") {
            // forcing root on empty breadcrumb url
            this.url = "/";
          }              
          fileBrowserViewModel.targetPageNum(1);              
          const pathPrefix = "/filebrowser/view=";
          huePubSub.publish('open.filebrowserlink', { pathPrefix, decodedPath: this.url, fileBrowserModel: fileBrowserViewModel});
          window.hueAnalytics.log('filebrowser', 'directory-breadcrumb-navigation');
        }
        else {
          window.open($(e.target).attr('href'));
        }
      }
    }
  }
};

var FileBrowserModel = function (files, page, breadcrumbs, currentDirPath) {
  var self = this;

  self.page = ko.observable(new Page(page));
  self.recordsPerPageChoices = ["15", "30", "45", "60", "100", "200", "1000"],
  self.recordsPerPage = ko.observable(hueUtils.hueLocalStorage('fb.records_per_page') || 45);
  self.targetPageNum = ko.observable(1);
  self.targetPath = ko.observable(listDirOptions.current_request_path);
  self.sortBy = ko.observable("name");
  self.sortDescending = ko.observable(false);
  self.searchQuery = ko.observable("");
  self.skipTrash = ko.observable(false);
  self.enableFilterAfterSearch = true;
  self.enableMoveButton = ko.observable(false);
  self.enableCopyButton = ko.observable(false);
  self.isCurrentDirSentryManaged = ko.observable(false);
  self.errorMessage = ko.observable("");
  self.pendingUploads = ko.observable(0);
  self.pendingUploads.subscribe(function (val) {
    if (val > 0) {
      if ($('#uploadFileModal').data('modal')) {
        $('#uploadFileModal').data('modal').$element.off('keyup.dismiss.modal');
        if ($('#uploadFileModal').data('modal').$backdrop){
          $('#uploadFileModal').data('modal').$backdrop.off('click');
        }
      }
    }
  });
  self.filesToHighlight = ko.observableArray([]);

  self.fileNameSorting = function (l, r) {
    if (l.name == "..") {
      return -1;
    }
    else if (r.name == "..") {
      return 1;
    }
    else if (l.name == ".") {
      return -1;
    }
    else if (r.name == ".") {
      return 1;
    }
    else {
      var _ret = l.name > r.name ? 1 : -1;
      if (self.sortDescending()){
        _ret = _ret * -1;
      }
      return _ret;
    }
  }
  self.files = ko.observableArray(ko.utils.arrayMap(files, function (file) {
    return new File(file);
  }));

  if (self.sortBy() == "name"){
    self.files.sort(self.fileNameSorting);
  }

  self.homeDir = ko.observable(listDirOptions.home_directory);

  self.breadcrumbs = ko.observableArray(ko.utils.arrayMap(breadcrumbs, function (breadcrumb) {
    return new Breadcrumb(breadcrumb);
  }));

  self.sort = function (viewModel, event) {
    var el = $(event.currentTarget);

    el.siblings(".sortable").attr("class", "sortable sorting");

    self.sortBy(el.data("sort"));

    el.removeClass("sorting");

    if (el.hasClass("sorting_asc")) {
      self.sortDescending(true);
    } else {
      self.sortDescending(false);
    }

    el.attr("class", "sortable");

    if (self.sortDescending() == true) {
      el.addClass("sorting_desc");
    } else {
      el.addClass("sorting_asc");
    }
    self.retrieveData();
  }

  self.isLoading = ko.observable(true);

  self.allSelected = ko.observable(false);

  self.compressArchiveName = ko.observable('');

  self.selectedFiles = ko.computed(function () {
    return ko.utils.arrayFilter(self.files(), function (file) {
      return file.selected();
    });
  }, self).extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });

  self.selectedSentryFiles = ko.computed(function () {
    return ko.utils.arrayFilter(self.files(), function (file) {
      return file.selected() && file.isSentryManaged;
    });
  }, self).extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });

  self.isCurrentDirSelected = ko.computed(function () {
    return ko.utils.arrayFilter(self.files(), function (file) {
      return file.name == "." && file.selected();
    });
  }, self).extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });

  self.selectedFile = ko.computed(function () {
    return self.selectedFiles()[0];
  }, self).extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });

  self.isSelectedFileSql = ko.pureComputed(function() {
    return self.selectedFile().name.endsWith('.sql') || self.selectedFile().name.endsWith('.hql');
  });

  self.openFileInEditor = function() {
    huePubSub.publish('open.editor.new.query', {'statementType': 'file', 'statementPath': self.selectedFile().path});
  };

  self.currentPath = ko.observable(currentDirPath);

  self.currentPath.subscribe(function (path) {        
    $(document).trigger('currPathLoaded', { path: path });
  });

  self.isS3 = ko.pureComputed(function () {
    return self.currentPath().toLowerCase().indexOf('s3a://') === 0;
  });

  self.isGS = ko.pureComputed(function () {
    return self.currentPath().toLowerCase().indexOf('gs://') === 0;
  });

  self.isAdls = ko.pureComputed(function () {
    return self.currentPath().toLowerCase().indexOf('adl:/') === 0;
  });

  self.isABFS = ko.pureComputed(function () {
    return self.currentPath().toLowerCase().indexOf('abfs://') === 0;
  });

  self.isOFS = ko.pureComputed(function () {
    return self.currentPath().toLowerCase().indexOf('ofs://') === 0;
  });

  self.isTaskServerEnabled = ko.computed(function() {
    return window.getLastKnownConfig().hue_config.enable_chunked_file_uploader && window.getLastKnownConfig().hue_config.enable_task_server;
  });

  self.scheme = ko.pureComputed(function () {
    var path = self.currentPath();
    return path.substring(0, path.indexOf(':/')) || "hdfs";
  });

  self.fs = ko.pureComputed(function () {
    var scheme = self.scheme();
    if (scheme === 'adl') {
      return 'adls';
    } else if (scheme === 's3a' ){
      return 's3';
    } else if (scheme === 'gs' ){
      return 'gs';
    } else if (scheme === 'ofs' ){
      return 'ofs';
    } else if (!scheme || scheme == 'hdfs') {
      return 'hdfs';
    } else {
      return scheme;
    }
  });

  function root(path) {
    var path = path && path.toLowerCase();
    if (path.indexOf('s3a://') >= 0) {
      return 's3a://';
    } else if (path.indexOf('gs://') >= 0) {
      return 'gs://';
    } else if (path.indexOf('adl:/') >= 0) {
      return 'adl:/';
    } else if (path.indexOf('abfs://') >= 0) {
      return 'abfs://';
    } else if (path.indexOf('ofs://') >= 0) {
      return 'ofs://';
    } else {
      return '/';
    }
  };

  self.rootCurrent = ko.pureComputed(function () {
    return root(self.currentPath());
  });

  self.rootTarget = ko.pureComputed(function () {
    return root(self.targetPath());
  });

  self.isHdfs = ko.pureComputed(function () {
    var currentPath = self.currentPath().toLowerCase();
    return currentPath.indexOf('/') === 0 || currentPath.indexOf('hdfs') === 0
  });
  self.isCompressEnabled = ko.pureComputed(function () {
    return !self.isS3() && !self.isGS() && !self.isAdls() && !self.isABFS() && !self.isOFS();
  });
  self.isSummaryEnabled = ko.pureComputed(function () {
    return self.isHdfs() || self.isOFS();
  });
  self.isPermissionEnabled = ko.pureComputed(function () {
    return !self.isS3() && !self.isGS() && !self.isABFSRoot() && !self.isOFS();
  });
  self.isReplicationEnabled = ko.pureComputed(function () {
    return self.isHdfs();
  });

  self.isS3.subscribe(function (newVal) {
    if (newVal) {
      huePubSub.publish('update.autocompleters');
    }
  });

  self.isGS.subscribe(function (newVal) {
    if (newVal) {
      huePubSub.publish('update.autocompleters');
    }
  });

  self.isS3Root = ko.pureComputed(function () {
    return self.isS3() && self.currentPath().toLowerCase() === 's3a://';
  });

  self.isGSRoot = ko.pureComputed(function () {
    return self.isGS() && self.currentPath().toLowerCase() === 'gs://';
  });

  self.isABFSRoot = ko.pureComputed(function () {
    return self.isABFS() && self.currentPath().toLowerCase() === 'abfs://';
  });

  self.isOFSRoot = ko.pureComputed(function () {
    return self.isOFS() && self.currentPath().toLowerCase() === 'ofs://';
  });

  self.isOFSServiceID = ko.pureComputed(function () {
    return self.isOFS() && self.currentPath().split("/").length === 3 && self.currentPath().split("/")[2] !== '';
  });

  self.isOFSVol = ko.pureComputed(function () {
    return self.isOFS() && self.currentPath().split("/").length === 4 && self.currentPath().split("/")[3] !== '';
  });

  self.inTrash = ko.computed(function() {
    return self.currentPath().match(/^\/user\/.+?\/\.Trash/);
  });

  self.inRestorableTrash = ko.computed(function() {
    return self.currentPath().match(/^\/user\/.+?\/\.Trash\/.+?/);
  });

  self.isLoadingSummary = ko.observable(true);
  self.contentSummary = ko.observable(ko.mapping.fromJS({
    spaceConsumed: -1,
    quota: -1,
    spaceQuota: -1,
    length: 0,
    directoryCount: 0,
    fileCount: 0,
    replication: 0
  }));
  self.showSummary = function () {
    self.isLoadingSummary(true);
    $("#contentSummaryModal").modal("show");
    $.getJSON("/filebrowser/content_summary=" + encodeURIComponent(self.selectedFile().path), function (data) {
      if (data.status == 0) {
        self.contentSummary(ko.mapping.fromJS(data.summary));
        self.isLoadingSummary(false);
      } else {
        huePubSub.publish('hue.global.error', {message: data.message});
        $("#contentSummaryModal").modal("hide");
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      huePubSub.publish('hue.global.error', {message: xhr.responseText});
      $("#contentSummaryModal").modal("hide");
    });
  }

  self.getStats = function (callback) {
    $.getJSON(self.targetPath() + (self.targetPath().indexOf('?') > 0 ? '&' : '?') + "pagesize=1&format=json", callback);
  };

  self.retrieveData = function (clearAssistCache) {
    self.isLoading(true);
    const encodedSearchFilter = encodeURIComponent(self.searchQuery());
    $.getJSON(self.targetPath() + (self.targetPath().indexOf('?') > 0 ? '&' : '?') + "pagesize=" + self.recordsPerPage() + "&pagenum=" + self.targetPageNum() + "&filter=" + encodedSearchFilter + "&sortby=" + self.sortBy() + "&descending=" + self.sortDescending() + "&format=json", function (data) {
      if (data.error){
        huePubSub.publish('hue.global.error', {message: data.error});
        self.isLoading(false);
        return false;
      }

      if (data.type != null && data.type == "file") {
        huePubSub.publish('open.link', data.url);
        return false;
      }

      self.updateFileList(data.files, data.page, data.breadcrumbs, data.current_dir_path, data.is_sentry_managed, data.s3_listing_not_allowed);

      if (clearAssistCache) {
        huePubSub.publish('assist.'+self.fs()+'.refresh');
      }
      if (data.s3_listing_not_allowed) {
        if (!$("#hueBreadcrumbText").is(":visible")) {
          $(".hue-breadcrumbs").hide();
          $("#hueBreadcrumbText").show();
          $("#editBreadcrumb").hide();
        }
        $("#hueBreadcrumbText").focus();
      } else {
        if ($("#hueBreadcrumbText").is(":visible")) {
          $(".hue-breadcrumbs").show();
          $("#hueBreadcrumbText").hide();
          $("#editBreadcrumb").show();
        }
      }

    });
  };

  self.updateFileList = function (files, page, breadcrumbs, currentDirPath, isSentryManaged, s3_listing_not_allowed) {
    $(".tooltip").hide();

    self.isCurrentDirSentryManaged(isSentryManaged);
    self.errorMessage(s3_listing_not_allowed);

    self.page(new Page(page));
    self.files(ko.utils.arrayMap(files, function (file) {
      file.highlighted = self.filesToHighlight.indexOf(file.path) > -1;
      var f = new File(file);
      window.setTimeout(function(){
        f.highlighted(false);
      }, 3000);
      return f;
    }));
    self.filesToHighlight([]);
    if (self.sortBy() == "name"){
      self.files.sort(self.fileNameSorting);
    }

    self.breadcrumbs(ko.utils.arrayMap(breadcrumbs, function (breadcrumb) {
      return new Breadcrumb(breadcrumb);
    }));

    self.currentPath(currentDirPath);

    $('.uploader').trigger('fb:updatePath', {dest:self.currentPath()});

    self.isLoading(false);

    $("*[rel='tooltip']").tooltip({ placement:"left" });

    var $scrollable = $(window);
    $scrollable = $('.page-content');


    if ($('.row-highlighted').length > 0) {
      $scrollable.scrollTop($('.row-highlighted:eq(0)').offset().top - 150);
    }
    else if ($('.row-deleted').length > 0) {
      $scrollable.scrollTop($('.row-deleted:eq(0)').offset().top - 150);
    }
    else {
      $scrollable.scrollTop(0);
    }

    resetActionbar();
  };

  self.recordsPerPage.subscribe(function (newValue) {
    window.hueUtils.hueLocalStorage('fb.records_per_page', newValue)
    self.retrieveData();
  });

  self.skipTo = function () {
    var doc = document,
      old_page = doc.querySelector('#current_page').value,
      page = doc.querySelector('.pagination-input');

    if (! isNaN(page.value) && (page.value > 0 && page.value <= self.page().num_pages)) {
      self.goToPage(page.value);
    } else {
      page.value = old_page;
    }
  };

  self.goToPage = function (pageNumber) {
    self.targetPageNum(pageNumber);
    self.retrieveData();
  };

  self.firstPage = function () {
    self.goToPage(1)
  };

  self.previousPage = function () {
  if (self.page().previous_page_number != 0) {
      self.goToPage(self.page().previous_page_number)
    }
  };

  self.nextPage = function () {
    if (self.page().next_page_number != 0) {
      self.goToPage(self.page().next_page_number)
    }
  };

  self.lastPage = function () {
    self.goToPage(self.page().num_pages)
  };

  self.selectAll = function () {
    self.allSelected(!self.allSelected());
    ko.utils.arrayForEach(self.files(), function (file) {
      if (file.name != "." && file.name != "..") {
        file.selected(self.allSelected());
      }
    });
    return true;
  };

  self.searchQuery.subscribe(function (newValue) {
    if (newValue !== '' || self.enableFilterAfterSearch) {
      window.hueAnalytics.log('filebrowser', newValue === '' ? 'search-file-name-clear' : 'search-file-name');
      self.filter();
    }
    self.enableFilterAfterSearch = true;
  });

  self.filter = function () {
    self.targetPageNum(1);
    self.retrieveData();
  };

  self.openDefaultFolder = function (vm, e, folderPath) {
    var isLeftButton = (e.which || e.button) === 1;
    if (isLeftButton) {
      if (! (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey)) {
        e.stopPropagation();
        e.preventDefault();
        fileBrowserViewModel.targetPageNum(1);
        fileBrowserViewModel.targetPath("/filebrowser/view=?" + folderPath);
        fileBrowserViewModel.retrieveData();
      }
      else {
        window.open("/filebrowser/view=?" + folderPath);
      }
    }
  }

  self.openHome = function (vm, e) {
    self.openDefaultFolder(vm, e, 'default_to_home');
    window.hueAnalytics.log('filebrowser', 'home-btn-click');
  }

  self.openTrash = function (vm, e) {
    self.openDefaultFolder(vm, e, 'default_to_trash');
  }

  self.viewFile = function (file, e) {
    e.stopImmediatePropagation();
    const decodedPath = file.path;
    const pathPrefix = "/filebrowser/view=";

    if (file.type == "dir") {
      // Reset page number so that we don't hit a page that doesn't exist
      self.targetPageNum(1);        
      self.enableFilterAfterSearch = false;
      self.searchQuery("");
      huePubSub.publish('open.filebrowserlink', { pathPrefix, decodedPath, fileBrowserModel: self });
    } else {
      huePubSub.publish('open.filebrowserlink', { pathPrefix, decodedPath });
    }        
  };

  self.downloadFile = function () {
    huePubSub.publish('ignore.next.unload');
    huePubSub.publish('open.filebrowserlink', { pathPrefix: '/filebrowser/download=', decodedPath: self.selectedFile().path });  
  };

  self.renameFile = function () {
    $("#renameSrcPath").attr("value", self.selectedFile().path);

    $("#renameFileName").text(self.selectedFile().path);

    $("#newNameInput").val(self.selectedFile().name);

    $("#renameForm").attr("action", "/filebrowser/rename?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));

    $('#renameForm').ajaxForm({
      dataType:  'json',
      success: function() {
        $("#renameModal").modal('hide');
        self.filesToHighlight.push(self.currentPath() + '/' + $('#newNameInput').val());
        self.retrieveData(true);
      }
    });

    $("#renameModal").modal({
      keyboard:true,
      show:true
    });
  };

  self.setReplicationFactor = function () {
    $("#SrcPath").attr("value", self.selectedFile().path);

    $("#setReplFileName").text(self.selectedFile().path);

    $("#setReplicationFactorForm").attr("action", "/filebrowser/set_replication?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));

    $('#setReplicationFactorForm').ajaxForm({
      dataType: 'json',
      success: function() {
        $("#setReplicationModal").modal('hide');
        $("#newRepFactorInput").val('');
        self.retrieveData(true);
      }
    });

    $("#setReplicationModal").modal({
      keyboard:true,
      show:true
    }).on('shown', function(){
      $('#newRepFactorInput').val(self.selectedFile().stats.replication);
    });
  };
  
  const removeLastSlash = function (path) {
    if (path.charAt(path.length - 1) === '/') {
      return path.slice(0, -1);
    }
    return path;
  };

  self.allowCopyMoveTo = function (destination) {
    const source = self.currentPath();
    return removeLastSlash(source) !== removeLastSlash(destination);
  };

  self.move = function (mode, unselectedDrag) {
    var paths = [];

    var isMoveOnSelf = false;
    $(self.selectedFiles()).each(function (index, file) {
      if (file.path == $('#moveDestination').val()){
        isMoveOnSelf = true;
      }
      paths.push(file.path);
    });

    if (paths.length == 0 && typeof unselectedDrag !== 'undefined'){
      paths.push(_dragged.path);
    }

    if (!isMoveOnSelf){
      hiddenFields($("#moveForm"), "src_path", paths);
      $("#moveForm").attr("action", "/filebrowser/move?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));
      $('#moveForm').ajaxForm({
        dataType:  'json',
        success: function() {
          $("#moveModal").modal('hide');
          self.filesToHighlight.push(self.currentPath() + '/' + $('#moveDestination').val());
          self.retrieveData(true);
        },
        error: function(xhr){
          huePubSub.publish('hue.global.error', {
            message: xhr.responseText
          });
          resetPrimaryButtonsStatus();
          $('#moveDestination').val('');
        }
      });

      if (mode === 'nomodal') {
        huePubSub.publish('hue.global.info', {
          message: window.I18n('Items moving to') + $('#moveDestination').val() + '"'
        });
        $("#moveForm").submit();
      } else {
        $("#moveModal").modal({
          keyboard: true,
          show: true
        });

        $("#moveModal").on("shown", function () {
          self.enableMoveButton(false);
          $("#moveDestination").val('');
          $("#moveNameRequiredAlert").hide();
          $("#moveForm").find("input[name='*dest_path']").removeClass("fieldError");
          $("#moveModal .modal-footer div").show();
          $("#moveFilechooser").remove();
          $("<div>").attr("id", "moveFilechooser").appendTo($("#moveModal .modal-body"));
          $("#moveFilechooser").jHueFileChooser({
            initialPath: paths[0] || '',
            filesystemsFilter: [self.scheme()],
            onNavigate: function (filePath) {
              $("#moveDestination").val(filePath);
              self.enableMoveButton(self.allowCopyMoveTo(filePath));            
            },
            onFolderChange: function () {
              self.enableMoveButton(false);
            },
            createFolder: false,
            uploadFile: false
          });
        });
      }
    }
    else {
      huePubSub.publish('hue.global.warning', {
        message: window.I18n('You cannot copy a folder into itself.')
      });
      $('#moveDestination').val('');
    }
  };

  self.copy = function () {
    var paths = [];

    $(self.selectedFiles()).each(function (index, file) {
      paths.push(file.path);
    });

    hiddenFields($("#copyForm"), "src_path", paths);

    $("#copyForm").attr("action", "/filebrowser/copy?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));

    $("#copyModal").modal({
      keyboard:true,
      show:true
    });

    $('#copyForm').ajaxForm({
      dataType:  'json',
      success: function() {
        $("#copyModal").modal('hide');
        self.filesToHighlight.push(self.currentPath() + '/' + $('#copyDestination').val());
        self.retrieveData(true);
      },
      error: function(xhr){
        huePubSub.publish('hue.global.error', {
          message: xhr.responseText
        });
        resetPrimaryButtonsStatus();
      }
    });

    $("#copyModal").on("shown", function () {
      self.enableCopyButton(false);
      $("#copyDestination").val('');
      $("#copyNameRequiredAlert").hide();
      $("#copyForm").find("input[name='*dest_path']").removeClass("fieldError");
      $("#copyModal .modal-footer div").show();
      $("#copyFilechooser").remove();
      $("<div>").attr("id", "copyFilechooser").appendTo($("#copyModal .modal-body"));
      $("#copyFilechooser").jHueFileChooser({
        initialPath: paths[0] || '',
        filesystemsFilter: [self.scheme()],
        onNavigate: function (filePath) {
          $("#copyDestination").val(filePath);
          self.enableCopyButton(self.allowCopyMoveTo(filePath)); 
        },
        onFolderChange: function () {
          self.enableCopyButton(false);
        },            
        createFolder: false,
        uploadFile: false
      });
    });

  };

  self.changeOwner = function (data, event) {
    if (!self.isCurrentDirSentryManaged()) {
      var paths = [];
      event.preventDefault();
      event.stopPropagation();

      $(self.selectedFiles()).each(function (index, file) {
        paths.push(file.path);
      });

      hiddenFields($("#chownForm"), 'path', paths);

      $("#chownForm").attr("action", "/filebrowser/chown?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));

      $("select[name='user']").val(self.selectedFile().stats.user);

      $("#chownForm input[name='group_other']").removeClass("fieldError");
      $("#chownForm input[name='user_other']").removeClass("fieldError");
      $("#chownRequired").hide();

      if ($("select[name='group'] option:contains('" + self.selectedFile().stats.group + "')").length > 0) {
        $("select[name='group']").val(self.selectedFile().stats.group);
      } else {
        $("select[name='group']").val("__other__");
        $("input[name='group_other']").val(self.selectedFile().stats.group);
      }

      $("select[name='group']").change();

      $("#changeOwnerModal").modal({
        keyboard: true,
        show: true
      });

      $('#chownForm').ajaxForm({
        dataType:  'json',
        success: function() {
          $("#changeOwnerModal").modal('hide');
          $(self.selectedFiles()).each(function (index, file) {
            self.filesToHighlight.push(file.path);
          });
          self.retrieveData(true);
        },
        error: function (xhr, textStatus, errorThrown) {
          huePubSub.publish('hue.global.error', {message: xhr.responseText});
          resetPrimaryButtonsStatus();
        }
      });
    }
  };

  self.changePermissions = function (data, event) {
    window.hueAnalytics.log('filebrowser', 'actions-menu/change-permissions-click');
    if (!self.isCurrentDirSentryManaged()) {
      var paths = [];

      event.preventDefault();
      event.stopPropagation();

      $(self.selectedFiles()).each(function (index, file) {
        paths.push(file.path);
      });

      hiddenFields($("#chmodForm"), 'path', paths);

      $("#chmodForm").attr("action", "/filebrowser/chmod?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));

      $("#changePermissionModal").modal({
        keyboard: true,
        show: true
      });

      $('#chmodForm').ajaxForm({
        dataType:  'json',
        success: function() {
          $("#changePermissionModal").modal('hide');
          $(self.selectedFiles()).each(function (index, file) {
            self.filesToHighlight.push(file.path);
          });
          self.retrieveData(true);
        },
        error: function (xhr, textStatus, errorThrown) {
          huePubSub.publish('hue.global.error', {message: xhr.responseText});
          resetPrimaryButtonsStatus();
        }
      });

      // Initial values for form
      var permissions = ["sticky", "user_read", "user_write", "user_execute", "group_read", "group_write", "group_execute", "other_read", "other_write", "other_execute"].reverse();
      var mode = octal(self.selectedFile().mode) & 01777;

      for (var i = 0; i < permissions.length; i++) {
        if (mode & 1) {
          $("#chmodForm input[name='" + permissions[i] + "']").prop("checked", true);
        } else {
          $("#chmodForm input[name='" + permissions[i] + "']").prop("checked", false);
        }
        mode >>>= 1;
      }
    }
  };

  var deleteSelected = function() {
    var paths = [];

    $(self.selectedFiles()).each(function (index, file) {
      paths.push(file.path);
    });

    hiddenFields($("#deleteForm"), 'path', paths);

    $("#deleteForm").attr("action", "/filebrowser/rmtree" + "?" +
      (self.skipTrash() ? "skip_trash=true&" : "") +
      "next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));

    $("#deleteModal").modal({
      keyboard:true,
      show:true
    });

    $('#deleteForm').ajaxForm({
      dataType:  'json',
      success: function() {
        $("#deleteModal").modal('hide');
        window.setTimeout(function () {
          $(self.selectedFiles()).each(function (index, file) {
            file.deleted(true);
          });
          var $scrollable = $(window);
          $scrollable = $('.page-content');
          if ($('.row-deleted').length > 0 && $('.row-deleted:eq(0)').offset()) {
            $scrollable.scrollTop($('.row-deleted:eq(0)').offset().top - 150);
          }
        }, 500);
        window.setTimeout(function () {
          $(self.selectedFiles()).each(function (index, file) {
            self.files.remove(file);
          });
          self.retrieveData(true);
        }, 1000);
      },
      error: function(xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
        resetPrimaryButtonsStatus();
      }
    });
  };

  self.deleteSelected = function () {
    self.skipTrash(true);
    deleteSelected();
  };

  self.copyPath = function () {
    const path = $('<input>').val(self.selectedFile().path).appendTo('body').select()
    document.execCommand('copy');
    path.remove();
    huePubSub.publish('hue.global.info', {
      message: window.I18n('Path copied successfully to the clipboard')
    });
  }

  self.openInImporter = function () {
    huePubSub.publish('open.in.importer', self.selectedFile().path);
  }

  self.trashSelected = function () {
    self.skipTrash(false);
    deleteSelected();
  };
  self.submitSelected = function() {       
    if (window.HUE_APPS && window.HUE_APPS.includes('oozie')) {
      var oozieAppPath = window.HUE_APPS_PATHS['oozie']; // Assuming you have a similar array for app paths
      $.get(oozieAppPath + "/submit_external_job/" + "../" + self.selectedFile().path, { 'format': 'json' }, function (response) {
        $('#submit-wf-modal').html(response);
        $('#submit-wf-modal').modal('show');
      });
    } else {
      huePubSub.publish('hue.global.warning', {
        message: window.I18n('Submitting is not available as the Oozie app is disabled')
      });
    }     
  };
  self.isArchive = function(fileName) {
    return fileName.endsWith('.zip') || fileName.endsWith('.tar.gz') || fileName.endsWith('.tgz') || fileName.endsWith('.bz2') || fileName.endsWith('.bzip2');
  };

  self.confirmExtractArchive = function() {
    $("#confirmExtractModal").modal({
      keyboard:true,
      show:true
    });
  };

  self.showCompressButton = ko.computed(function() {
    var fileNames = self.selectedFiles().map(function(file) {
      return file.name;
    });
    if (fileNames.indexOf('.') !== -1) {
      return false;
    }
    return self.isCompressEnabled() && (self.selectedFiles().length > 1 || !(self.selectedFiles().length === 1 && self.isArchive(self.selectedFile().name)));
  });

  self.setCompressArchiveDefault = function() {
    if (self.selectedFiles().length == 1) {
      self.compressArchiveName(self.selectedFile().name + '.zip');
    } else {
      if (self.breadcrumbs().length === 1) {
        self.compressArchiveName('root.zip'); // When compressing multiple files in root directory
      }
      else {
        self.compressArchiveName(self.breadcrumbs()[self.breadcrumbs().length - 1].label + '.zip'); // Setting to parent directory name
      }
    }
  };

  self.confirmCompressFiles = function() {
    $("#confirmCompressModal").modal({
      keyboard:true,
      show:true
    });
  };

  self.extractSelectedArchive = function() {
    $("#confirmExtractModal").modal("hide");
    $.post("/filebrowser/extract_archive", {
      "archive_name": self.selectedFile().name,
      "upload_path": self.currentPath(),
      "start_time": ko.mapping.toJSON((new Date()).getTime())
    }, function (data) {
      if (data.status == 0) {
        huePubSub.publish('hue.global.info', {
          message: window.I18n('Task ') + data.history_uuid + window.I18n(' submitted.')
        });
        huePubSub.publish('notebook.task.submitted', data);
      } else {
        huePubSub.publish('hue.global.error', {message: data.message});
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      huePubSub.publish('hue.global.error', {message: xhr.responseText});
    });
  };

  self.archiveOverrideWarning = function() {
    $("#confirmCompressModal").modal("hide");
    var fileNames = self.files().map(function(file) {
      return file.name;
    });
    if (fileNames.indexOf(self.compressArchiveName()) !== -1) {
      $("#compressWarningModal").modal("show");
    } else {
      self.compressSelectedFiles();
    }
  }

  self.compressSelectedFiles = function() {
    $("#compressWarningModal").modal("hide");
    var fileNames = [];
    $(self.selectedFiles()).each(function (index, file) {
      fileNames.push(file.name);
    });

    $.post("/filebrowser/compress_files", {
      "files": fileNames,
      "upload_path": self.currentPath(),
      "archive_name": self.compressArchiveName(),
      "start_time": ko.mapping.toJSON((new Date()).getTime())
    }, function (data) {
      if (data.status == 0) {
        huePubSub.publish('hue.global.info', {
          message: window.I18n('Task ') + data.history_uuid + window.I18n(' submitted.')
        });
        huePubSub.publish('notebook.task.submitted', data);
      } else {
        huePubSub.publish('hue.global.error', {message: data.message});
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      huePubSub.publish('hue.global.error', {message: xhr.responseText});
    });
  };

  self.createDirectory = function (formElement) {
    $(formElement).attr("action", "/filebrowser/mkdir?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));
    if ($.trim($("#newDirectoryNameInput").val()) == "") {
      $("#directoryNameRequiredAlert").show();
      $("#newDirectoryNameInput").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }

    if (fileExists($("#newDirectoryNameInput").val())) {
      $("#directoryNameExistsAlert").find(".newName").text($("#newDirectoryNameInput").val());
      $("#directoryNameExistsAlert").show();
      $("#newDirectoryNameInput").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }
    if ($("#newDirectoryNameInput").val().length < 3 && self.isABFSRoot()) {
      $("#smallFileSystemNameAlert").show();
      $("#newDirectoryNameInput").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }
    if (self.isOFSServiceID() || self.isOFSVol()) {
      if ($("#newDirectoryNameInput").val().length < 3 || $("#newDirectoryNameInput").val().length > 63) {
        $("#volumeBucketNameAlert").show();
        $("#newDirectoryNameInput").addClass("fieldError");
        resetPrimaryButtonsStatus(); //globally available
        return false;
      }
      if ($("#newDirectoryNameInput").val() !== $("#newDirectoryNameInput").val().toLowerCase()) {
        $("#upperCaseVolumeBucketNameAlert").show();
        $("#newDirectoryNameInput").addClass("fieldError");
        resetPrimaryButtonsStatus(); //globally available
        return false;
      }
    }
    $(formElement).ajaxSubmit({
      dataType:  'json',
      success: function() {
        self.filesToHighlight.push(self.currentPath() + '/' + $('#newDirectoryNameInput').val());
        $("#createDirectoryModal").modal('hide');
        self.retrieveData(true);
      },
      error: function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
        resetPrimaryButtonsStatus();
      }
    });
    return false;
  };

  self.createFile = function (formElement) {
    $(formElement).attr("action", "/filebrowser/touch?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));
    if ($.trim($("#newFileNameInput").val()) == "") {
      $("#fileNameRequiredAlert").show();
      $("#newFileNameInput").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }

    if (fileExists($("#newFileNameInput").val())) {
      $("#fileNameExistsAlert").find(".newName").text($("#newFileNameInput").val());
      $("#fileNameExistsAlert").show();
      $("#newFileNameInput").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }
    $(formElement).ajaxSubmit({
      dataType:  'json',
      success: function() {
        self.filesToHighlight.push(self.currentPath() + '/' + $('#newFileNameInput').val());
        $("#createFileModal").modal('hide');
        self.retrieveData(true);
      },
      error: function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
        resetPrimaryButtonsStatus();
      }
    });
    return false;
  };

  self.restoreTrashSelected = function(formElement) {
    var paths = [];

    $(self.selectedFiles()).each(function (index, file) {
      paths.push(file.path);
    });

    hiddenFields($("#restoreTrashForm"), 'path', paths);

    $("#restoreTrashForm").attr("action", "/filebrowser/trash/restore?next=/filebrowser/view=" + encodeURIComponent(self.currentPath()));

    $("#restoreTrashModal").modal({
      keyboard:true,
      show:true
    });

    $('#restoreTrashForm').ajaxForm({
      dataType:  'json',
      success: function() {
        $("#restoreTrashModal").modal('hide');
        self.retrieveData(true);
      },
      error: function(xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
        resetPrimaryButtonsStatus();
      }
    });
  };

  self.purgeTrash = function(formElement) {
    var paths = [];

    $(self.selectedFiles()).each(function (index, file) {
      paths.push(file.path);
    });

    hiddenFields($("#purgeTrashForm"), 'path', paths);

    $("#purgeTrashForm").attr("action", "/filebrowser/trash/purge?next=/filebrowser/view=" + fileBrowserViewModel.homeDir() + "/.Trash");

    $("#purgeTrashModal").modal({
      keyboard:true,
      show:true
    });

    $('#purgeTrashForm').ajaxForm({
      dataType:  'json',
      success: function() {
        $("#purgeTrashModal").modal('hide');
        self.retrieveData(true);
      }
    });
  };

  function pollForTaskProgress(taskId, listItem, fileName) {
    var taskStatus = 'pending';
    var pollingInterval = 10000;

    var doPoll = function() {
      if (taskStatus === 'pending') {
        $.get('/desktop/api2/taskserver/check_upload_status/' + taskId, function(data) {
          if (data.isFinalized || data.isFailure || data.is_revoked) {
            taskStatus = data.isFinalized ? 'finalized' : 'failed';

            if (data.isFinalized) {
              listItem.find('.progress-row-bar').css('width', '100%');
              listItem.find('.progress-row-text').text('Upload complete.');
              $(document).trigger('info', fileName + window.I18n(' uploaded successfully.'));
              self.retrieveData(true);
            } else if (data.isFailure) {
              listItem.find('.progress-row-bar').css('width', '100%');
              listItem.find('.progress-row-text').text('Upload failed.');
              $(document).trigger('error', fileName + window.I18n(' file upload failed. Please check the logs for task id: ') + taskId);
            }
            
          } else if (data.isRunning) {
            var progressPercentage = 90; // Adjust based on data.progress if available
            listItem.find('.progress-row-bar').css('width', progressPercentage + '%');
            setTimeout(doPoll, pollingInterval);
          }
        }).fail(function(xhr, textStatus, errorThrown) {
          if (xhr.status === 404) {
            setTimeout(doPoll, pollingInterval); // Retry after 10 seconds
          }
        });
      }
    };
    self.retrieveData(true);
    doPoll();
  }

  self.checkAndDisplayAvailableSpace = function () {
    $.ajax({
        url: '/filebrowser/upload/taskserver/get_available_space_for_file_uploads/',
        success: function(response) {
            if (typeof window.MAX_FILE_SIZE_UPLOAD_LIMIT === 'undefined') {
              window.MAX_FILE_SIZE_UPLOAD_LIMIT = 5 * 1024 * 1024 * 1024; // 5GB in bytes
            }
            var freeSpace = Math.min(response.upload_available_space, window.MAX_FILE_SIZE_UPLOAD_LIMIT);
            $('.free-space-info').text('- Max file size upload limit: ' + formatBytes(freeSpace));
        },
        error: function(xhr, status, error) {
            huePubSub.publish('hue.global.error', { message: '${ _("Error checking available space: ") }' + error});
            $('.free-space-info').text('Error checking available space');
        }
    });
  };


  self.uploadFile = (function () {  
      var uploader; 
      var scheduleUpload;
      
      if ((window.getLastKnownConfig().hue_config.enable_chunked_file_uploader) && (window.getLastKnownConfig().hue_config.enable_task_server))  {
        
        self.pendingUploads(0);
        var action = "/filebrowser/upload/chunks/";
        self.taskIds = [];
        self.listItems = [];
        self.checkAndDisplayAvailableSpace();
        uploader = new qq.FileUploader({
          element: document.getElementById("fileUploader"),
          request: {
              endpoint: action,
              paramsInBody: false,
              params: {
                  dest: self.currentPath(),
                  inputName: "hdfs_file"
              }
          },
          maxConnections: window.CONCURRENT_MAX_CONNECTIONS || 5,
          chunking: {
              enabled: true,
              concurrent: {
                  enabled: true
              },
              partSize: window.FILE_UPLOAD_CHUNK_SIZE || 5242880,
              success: {
                  endpoint: "/filebrowser/upload/complete/"
              },
              paramNames: {
                  partIndex: "qqpartindex",
                  partByteOffset: "qqpartbyteoffset",
                  chunkSize: "qqchunksize",
                  totalFileSize: "qqtotalfilesize",
                  totalParts: "qqtotalparts"
              }
          },

          template: 'qq-template',
          callbacks: {
              onProgress: function (id, fileName, loaded, total) {

                $('.qq-upload-files').find('li').each(function(){
                  var listItem = $(this);
                  if (listItem.find('.qq-upload-file-selector').text() == fileName){
                    //cap the progress at 80%
                    listItem.find('.progress-row-bar').css('width', (loaded/total)*80 + '%');
                    if ((loaded/total) === 80) {
                      listItem.find('.progress-row-text').text('Finalizing upload...');
                    }
                  }
                });            
              },

              onComplete: function (id, fileName, response) {
                self.pendingUploads(self.pendingUploads() - 1);
                if (response.status != 0) {
                  huePubSub.publish('hue.global.error', {message: window.I18n('Error: ') + response.data});
                }
                else {
                  var task_id = response.task_id;
                  self.taskIds.push(task_id);
                  var listItem = $('.qq-upload-files').find('li').filter(function() {
                    return $(this).find('.qq-upload-file-selector').text() === fileName;
                  });
                  self.listItems.push(listItem);
                    if (scheduleUpload && self.pendingUploads() === 0) {
                      $('#uploadFileModal').modal('hide');
                      huePubSub.publish('hue.global.info', { message: '${ _("File upload scheduled. Please check the task server page for progress.") }'});
                    }
                    // Add a delay of 2 seconds before calling pollForTaskProgress, to ensure the upload task is received by the task_server before checking its status. 
                    setTimeout(function() {
                      pollForTaskProgress(response.task_id, listItem, fileName);
                    }, 2000);  
                  self.filesToHighlight.push(response.path);                       
                }
                if (self.pendingUploads() === 0) {                    
                  self.taskIds=[];
                  self.listItems=[];
                  self.retrieveData(true);
                }
              },
              onSubmit: function (id, fileName, responseJSON) {
                  var deferred = new qq.Promise(); // Create a promise to defer the upload
                  var uploader = this;
                  
                  // Make an AJAX request to check available disk space
                  $.ajax({
                    url: '/filebrowser/upload/taskserver/get_available_space_for_file_uploads/',
                    success: function(response) {
                      if (typeof window.MAX_FILE_SIZE_UPLOAD_LIMIT === 'undefined' || window.MAX_FILE_SIZE_UPLOAD_LIMIT === -1) {
                        window.MAX_FILE_SIZE_UPLOAD_LIMIT = 5 * 1024 * 1024 * 1024; // 5GB in bytes
                      }
                      var freeSpace = Math.min(response.upload_available_space, window.MAX_FILE_SIZE_UPLOAD_LIMIT);
                      var file = uploader.getFile(id); // Use the stored reference
                      // Update the free space display
                      $('.free-space-info').text('- Max file size upload limit: ' + formatBytes(freeSpace));
                      if ((file.size > freeSpace) || (file.size > window.MAX_FILE_SIZE_UPLOAD_LIMIT)) {
                        huePubSub.publish('hue.global.error', { message: '${ _("Not enough space available to upload this file.") }'});
                        deferred.failure(); // Reject the promise to cancel the upload
                      } else if (file.size > window.MAX_FILE_SIZE_UPLOAD_LIMIT) {
                        huePubSub.publish('hue.global.error', { message: '${ _("File size is bigger than MAX_FILE_SIZE_UPLOAD_LIMIT.") }'});
                        deferred.failure(); // Reject the promise to cancel the upload
                      } else {
                        var newPath = "/filebrowser/upload/chunks/file?dest=" + encodeURIComponent(self.currentPath().normalize('NFC'));
                        uploader.setEndpoint(newPath);
                        self.pendingUploads(self.pendingUploads() + 1);
                        deferred.success(); // Resolve the promise to allow the upload
                      }
                    },
                    error: function(xhr, status, error) {
                      huePubSub.publish('hue.global.error', { message: '${ _("Error checking available space: ") }' + error});
                      deferred.failure(); // Reject the promise to cancel the upload
                    }
                  });

                  return deferred; // Return the promise to Fine Uploader
              },
              onCancel: function (id, fileName) {
                self.pendingUploads(self.pendingUploads() - 1);
              }
          },
          debug: false
        });
      }
      // Chunked Fileuploader without Taskserver
      else if ((window.getLastKnownConfig().hue_config.enable_chunked_file_uploader) && !(window.getLastKnownConfig().hue_config.enable_task_server)) {
        self.pendingUploads(0);
        var action = "/filebrowser/upload/chunks/";
        uploader = new qq.FileUploader({
          element: document.getElementById("fileUploader"),
          request: {
              endpoint: action,
              paramsInBody: false,
              params: {
                  dest: self.currentPath(),
                  inputName: "hdfs_file"
              }
          },
          maxConnections: window.CONCURRENT_MAX_CONNECTIONS || 5,
          chunking: {
              enabled: true,
              concurrent: {
                  enabled: true
              },
              partSize: window.FILE_UPLOAD_CHUNK_SIZE || 5242880,
              success: {
                  endpoint: "/filebrowser/upload/complete/"
              },
              paramNames: {
                  partIndex: "qqpartindex",
                  partByteOffset: "qqpartbyteoffset",
                  chunkSize: "qqchunksize",
                  totalFileSize: "qqtotalfilesize",
                  totalParts: "qqtotalparts"
              }
          },

          template: 'qq-template',
          callbacks: {
              onProgress: function (id, fileName, loaded, total) {
              $('.qq-upload-files').find('li').each(function(){
                var listItem = $(this);
                if (listItem.find('.qq-upload-file-selector').text() == fileName){
                  listItem.find('.progress-row-bar').css('width', (loaded/total)*100 + '%');
                }
              });
              },
              onComplete: function (id, fileName, response) {
                self.pendingUploads(self.pendingUploads() - 1);
                if (response.status != 0) {
                  huePubSub.publish('hue.global.error', {message: window.I18n('Error: ') + response.data});
                }
                else {
                  huePubSub.publish('hue.global.info', {message: response.path + window.I18n(' uploaded successfully.')});
                  self.filesToHighlight.push(response.path);
                }
                if (self.pendingUploads() == 0) {
                  $('#uploadFileModal').modal('hide');
                  self.retrieveData(true);
                }
              },

              onAllComplete: function(succeeded, failed){
                $('#uploadFileModal').modal('hide');
              },
              onSubmit: function (id, fileName, responseJSON) {
                var newPath = "/filebrowser/upload/chunks/file?dest=" + encodeURIComponent(self.currentPath().normalize('NFC'));
                this.setEndpoint(newPath);
                self.pendingUploads(self.pendingUploads() + 1);
              },
              onCancel: function (id, fileName) {
                self.pendingUploads(self.pendingUploads() - 1);
              }
          },

          debug: false
        });
      }
      //Regular fileuploads
      else {
        self.pendingUploads(0);
        var action = "/filebrowser/upload/file";
        uploader = new fileuploader.FileUploader({
          element: document.getElementById("fileUploader"),
          action: action,
          template: '<div class="qq-uploader" style="margin-left: 10px">' +
          '<div class="qq-upload-drop-area"><span>'+ window.I18n('Drop the files here to upload')+'</span></div>' +
          '<div class="qq-upload-button qq-no-float">'+ window.I18n('Select files')+'</div> &nbsp; <span class="muted">'+ window.I18n('or drag and drop them here') +'</span>' +
          '<ul class="qq-upload-list qq-upload-files unstyled qq-no-float" style="margin-right: 0;"></ul>' +
          '</div>',
          fileTemplate: '<li><span class="qq-upload-file-extended" style="display:none"></span><span class="qq-upload-spinner hide" style="display:none"></span>' +
          '<div class="progress-row dz-processing">' +
          '<span class="break-word qq-upload-file"></span>' +
          '<div class="pull-right">' +
          '<span class="muted qq-upload-size"></span>&nbsp;&nbsp;' +
          '<a href="#" title='+window.I18n('Cancel') +' class="complex-layout"><i class="fa fa-fw fa-times qq-upload-cancel"></i></a>' +
          '<span class="qq-upload-done" style="display:none"><i class="fa fa-fw fa-check muted"></i></span>' +
          '<span class="qq-upload-failed-text">'+window.I18n('Failed')+'</span>' +
          '</div>' +
          '<div class="progress-row-bar" style="width: 0%;"></div>' +
          '</div></li>',
          params: {
            dest: self.currentPath(),
            fileFieldLabel: "hdfs_file"
          },
          onProgress: function (id, fileName, loaded, total) {
            $('.qq-upload-files').find('li').each(function(){
              var listItem = $(this);
              if (listItem.find('.qq-upload-file-extended').text() == fileName){
                listItem.find('.progress-row-bar').css('width', (loaded/total)*100 + '%');
              }
            });
          },
          onComplete: function (id, fileName, response) {
            self.pendingUploads(self.pendingUploads() - 1);
            if (response.status != 0) {
              huePubSub.publish('hue.global.error', {message: window.I18n('Error: ') + response.data});
              
            }
            else {
              huePubSub.publish('hue.global.info', {message: response.path + window.I18n(' uploaded successfully.')});
              self.filesToHighlight.push(response.path);
            }
            if (self.pendingUploads() == 0) {
              $('#uploadFileModal').modal('hide');
              self.retrieveData(true);
            }
          },
          onSubmit: function (id, fileName, responseJSON) {
            self.pendingUploads(self.pendingUploads() + 1);
          },
          onCancel: function (id, fileName) {
            self.pendingUploads(self.pendingUploads() - 1);
          },
          debug: false
        });
      }

      $("#fileUploader").on('fb:updatePath', function (e, options) {
      const uploadingToOzone = self.currentPath().startsWith("ofs://");
      const ozoneSizeLimit = Math.min(
        ...[UPLOAD_CHUNK_SIZE, MAX_FILE_SIZE_UPLOAD_LIMIT].filter(Number.isFinite)
      );
      const newSizeLimit = uploadingToOzone ? ozoneSizeLimit : MAX_FILE_SIZE_UPLOAD_LIMIT;
      if (newSizeLimit) {
        uploader.setOption('sizeLimit', newSizeLimit);
      }
      uploader.setParams({
        dest: options.dest,
        fileFieldLabel: "hdfs_file"
      });
    });

    return function (isScheduled) {
      scheduleUpload = isScheduled;
      $("#uploadFileModal").modal({
        show: true
      });
    };
  })();

  // Place all values into hidden fields under parent element.
  // Looks for managed hidden fields and handles sizing appropriately.
  var hiddenFields = function (parentEl, name, values) {
    if (!(parentEl instanceof jQuery)){
      parentEl = $(parentEl);
    }
    parentEl.find("input.hidden-field").remove();

    $(values).each(function (index, value) {
      var field = $("<input type='hidden' />");
      field.attr("name", name);
      field.attr("class", "hidden-field")
      field.val(value);
      parentEl.append(field);
    });
  };

  var octal = function (strInt) {
    return parseInt("0" + strInt, 8);
  };
};

// hide the context menu based on specific events
var hideContextMenu = function () {
  var cm = $('.context-menu');

  if (cm.is(':visible')) {
    cm.css({ display: 'none' });
  }
};

var fileBrowserViewModel = new FileBrowserModel([], null, [], "/");
ko.applyBindings(fileBrowserViewModel, $('.filebrowser')[0]);

$(document).ready(function () {
  // hide context menu
  $('body').on('click', function (e) {
    hideContextMenu();
  });

  $('body').on('contextmenu', function (e) {
    if ($.inArray(e.toElement, $('.table-huedatatable *')) === -1) {
      hideContextMenu();
    }
  });

  $('body').on('contextmenu', '.context-menu', function (e) {
    hideContextMenu();
  });

  if (window.SHOW_UPLOAD_BUTTON) {

  // Drag and drop uploads from anywhere on filebrowser screen
  if (window.FileReader) {
    var showHoverMsg = function (msg) {
      $('.filebrowser .hoverText').html(msg);
      $('.filebrowser .hoverMsg').removeClass('hide');
    };

    var hideHoverMsg = function () {
      $('.filebrowser .hoverMsg').addClass('hide');
    };

    var _isDraggingOverText = false,
      // determine if the item dragged originated outside DOM
      _isExternalFile = true;

    $('.filebrowser').on('dragstart', function (e) {
      // External files being dragged into the DOM won't have a dragstart event
      _isExternalFile = false;
    });

    $('.filebrowser').on('dragend', function (e) {
      _isExternalFile = true;
    });

    $('.filebrowser').on('dragenter', function (e) {
      e.preventDefault();

      if (_isExternalFile && !($("#uploadFileModal").is(":visible")) && ((!fileBrowserViewModel.isS3() || (fileBrowserViewModel.isS3() && !fileBrowserViewModel.isS3Root())) || (!fileBrowserViewModel.isGS() || (fileBrowserViewModel.isGS() && !fileBrowserViewModel.isGSRoot())))) {
        showHoverMsg(window.I18n('Drop files here to upload'));
      }
    });

    $('.filebrowser .hoverText').on('dragenter', function (e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      _isDraggingOverText = true;
    });

    $('.filebrowser .hoverText').on('dragleave', function (e) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      _isDraggingOverText = false;
      _isExternalFile = true;
    });

    $('.filebrowser .hoverMsg').on('dragleave', function (e) {
      if (!_isDraggingOverText) {
        hideHoverMsg();
      }
    });

    $(document).on('currPathLoaded', function (e, ops) {
      try {
        _dropzone.destroy();
      }
      catch (exc) {
      }
      var options = {
        url: '/filebrowser/upload/file?dest=' + encodeURI(ops.path),
        paramName: 'hdfs_file',
        params: {
          dest: ops.path
        },
        autoDiscover: false,
        timeout: 300000,
        maxFilesize: 5000000,
        previewsContainer: '#progressStatusContent',
        previewTemplate: '<div class="progress-row">' +
            '<span class="break-word" data-dz-name></span>' +
            '<div class="pull-right">' +
            '<span class="muted" data-dz-size></span>&nbsp;&nbsp;' +
            '<span data-dz-remove><a href="javascript:undefined;" title="' + I18n('Cancel upload') + '"><i class="fa fa-fw fa-times"></i></a></span>' +
            '<span style="display: none" data-dz-uploaded><i class="fa fa-fw fa-check muted"></i></span>' +
            '</div>' +
            '<div class="progress-row-bar" data-dz-uploadprogress></div>' +
            '</div>',
        drop: function (e) {
          $('.filebrowser .hoverMsg').addClass('hide');

          // Ensure dropped item was a file
          if (e.dataTransfer.files.length > 0) {
            $('#progressStatus').removeClass('hide');
            $('#progressStatusBar').removeClass('hide');
            $('#progressStatus .progress-row').remove();
            $('#progressStatusBar div').css('width', '0');
          }
        },
        processing: function (file) {
          var newDest = ops.path;
          if (file.fullPath) {
            newDest = ops.path + '/' + file.fullPath.substr(0, file.fullPath.length - file.name.length);
          }
          this.options.params.dest = newDest;
          this.options.url = '/filebrowser/upload/file?dest=' + encodeURI(newDest);
        },
        uploadprogress: function (file, progress) {
          $('[data-dz-name]').each(function (cnt, item) {
            if ($(item).text() === file.name) {
              $(item).parents('.progress-row').find('[data-dz-uploadprogress]').width(progress.toFixed() + '%');
              if (progress.toFixed() === '100') {
                $(item).parents('.progress-row').find('[data-dz-remove]').hide();
                $(item).parents('.progress-row').find('[data-dz-uploaded]').show();
              }
            }
          });
        },
        totaluploadprogress: function (progress) {
          $('#progressStatusBar div').width(progress.toFixed() + "%");
        },
        canceled: function () {
          huePubSub.publish('hue.global.info', {
            message: I18n('The upload has been canceled')
          });
        },
        complete: function (data) {
          if (data.xhr.response != '') {
            var response = JSON.parse(data.xhr.response);
            if (response && response.status != null) {
              if (response.status != 0) {
                huePubSub.publish('hue.global.error', {message: response.data});
              } else {
                huePubSub.publish('hue.global.info', { message: response.path + ' ' + I18n('uploaded successfully')});
                fileBrowserViewModel.filesToHighlight.push(response.path);
              }
            }
          }
        }
      };
      if (ops.path.toLowerCase() !== 's3a://' && ops.path.toLowerCase() !== 'gs://') {
        _dropzone = new Dropzone($('.filebrowser .hoverMsg')[0], options);

        _dropzone.on('queuecomplete', function () {
          setTimeout(function () {
                $('#progressStatus').addClass('hide');
                $('#progressStatusBar').addClass('hide');
                $('#progressStatusBar div').css("width", "0");
                fileBrowserViewModel.retrieveData(true);
              },
              2500);
        });
      }
    });
  }
  }

  $("#chownForm select[name='user']").change(function () {
    if ($(this).val() == "__other__") {
      $("input[name='user_other']").show();
    } else {
      $("input[name='user_other']").hide();
    }
  });

  $("#chownForm select[name='group']").change(function () {
    if ($(this).val() == "__other__") {
      $("input[name='group_other']").show();
    } else {
      $("input[name='group_other']").hide();
    }
  });

  $("#chownForm").submit(function () {
    if ($("#chownForm select[name='user']").val() == null) {
      $("#chownRequired").find(".label").text(window.I18n('User is required.'));
      $("#chownRequired").show();
      resetPrimaryButtonsStatus(); //globally available
      return false;
    } else if ($("#chownForm select[name='group']").val() == null) {
      $("#chownRequired").find(".label").text(window.I18n('Group is required.'));
      $("#chownRequired").show();
      resetPrimaryButtonsStatus(); //globally available
      return false;
    } else {
      if ($("#chownForm select[name='group']").val() == "__other__" && $("input[name='group_other']").val() == "") {
        $("#chownRequired").find(".label").text(window.I18n('Specify another group.'));
        $("#chownForm input[name='group_other']").addClass("fieldError");
        $("#chownRequired").show();
        resetPrimaryButtonsStatus(); //globally available
        return false;
      }

      if ($("#chownForm select[name='user']").val() == "__other__" && $("input[name='user_other']").val() == "") {
        $("#chownRequired").find(".label").text(window.I18n('Specify another user.'));
        $("#chownForm input[name='user_other']").addClass("fieldError");
        $("#chownRequired").show();
        return false;
        resetPrimaryButtonsStatus(); //globally available
      }
      return true;
    }
  });

  // Modal file chooser
  // The file chooser should be at least 2 levels deeper than the modal container
  $(".fileChooserBtn").on('click', function (e) {
    e.preventDefault();

    var _destination = $(this).attr("data-filechooser-destination");
    var fileChooser = $(this).parent().parent().find(".fileChooserModal");

    fileChooser.jHueFileChooser({
      initialPath:$("input[name='" + _destination + "']").val(),
      onFolderChange:function (folderPath) {
        $("input[name='" + _destination + "']").val(folderPath);
      },
      onFolderChoose:function (folderPath) {
        $("input[name='" + _destination + "']").val(folderPath);
        fileChooser.slideUp();
      },
      selectFolder:true,
      createFolder:true,
      uploadFile:false
    });
    fileChooser.slideDown();
  });

  $("#renameForm").submit(function () {
    if ($("#newNameInput").val() == "") {
      $("#renameNameRequiredAlert").show();
      $("#newNameInput").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }

    if (fileExists($("#newNameInput").val())) {
      $("#renameNameExistsAlert").find(".newName").text($("#newNameInput").val());
      $("#renameNameExistsAlert").show();
      $("#newNameInput").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }
    return true;
  });

  $("#newNameInput").focus(function () {
    $("#renameNameRequiredAlert").hide();
    $("#renameNameExistsAlert").hide();
    $("#newNameInput").removeClass("fieldError");
  });

  $("#moveForm").on("submit", function () {
    if ($.trim($("#moveDestination").val()) == "") {
      $("#moveNameRequiredAlert").show();
      $("#moveForm").find("input[name='*dest_path']").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }
    var isMoveOnSelf = false;
    $(fileBrowserViewModel.selectedFiles()).each(function (index, file) {
      if (file.path == $('#moveDestination').val()) {
        isMoveOnSelf = true;
        return false;
      }
    });
    if(isMoveOnSelf){
      huePubSub.publish('hue.global.warning', {
        message: window.I18n('You cannot copy a folder into itself.')
      });
      $('#moveDestination').val('');
      return false;
    }
    return true;
  });

  $("#moveForm").bind("keypress", function(e) {
    if (e.keyCode == 13) {
      return false;
    }
  });

  $("#setReplicationFactorForm").submit(function () {
    if ($("#newRepFactorInput").val() == "") {
      $("#replicationFactorRequiredAlert").show();
      $("#newRepFactorInput").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }
  });

  $("#newRepFactorInput").focus(function () {
    $("#replicationFactorRequiredAlert").hide();
    $("#newRepFactorInput").removeClass("fieldError");
  });

  huePubSub.subscribe('fb.' + fileBrowserViewModel.fs() + '.refresh', function (path) {
    if (path === fileBrowserViewModel.currentPath()) {
      fileBrowserViewModel.retrieveData();
    }
  }, 'filebrowser');

  huePubSub.subscribe('update.autocompleters', function(){
    $("#moveDestination").jHueHdfsAutocomplete({
      showOnFocus: true,
      skipEnter: true,
      skipKeydownEvents: true,
      onEnter: function (el) {
        $("#jHueHdfsAutocomplete").hide();            
        const allowMove = fileBrowserViewModel.allowCopyMoveTo(el.val());
        fileBrowserViewModel.enableMoveButton(allowMove);
      },
      isS3: fileBrowserViewModel.isS3(),
      isGS: fileBrowserViewModel.isGS(),
      root: fileBrowserViewModel.rootCurrent()
    });
    $("#copyDestination").jHueHdfsAutocomplete({
      showOnFocus: true,
      skipEnter: true,
      skipKeydownEvents: true,
      onEnter: function (el) {
        $("#jHueHdfsAutocomplete").hide();
        const allowCopy = fileBrowserViewModel.allowCopyMoveTo(el.val());
        fileBrowserViewModel.enableCopyButton(allowCopy);
      },
      isS3: fileBrowserViewModel.isS3(),
      isGS: fileBrowserViewModel.isGS(),
      root: fileBrowserViewModel.rootCurrent()
    });
  });

  huePubSub.subscribe('submit.popup.return', function (data) {
    if (data.type == 'external_workflow') {
      huePubSub.publish('hue.global.info', {
        message: window.I18n('Workflow submitted.')
      });
      huePubSub.publish('open.link', '/jobbrowser/#!id=' + data.job_id);
      huePubSub.publish('browser.job.open.link', data.job_id);
      $('.submit-modal').modal('hide');
      $('.modal-backdrop').hide();
    }
  }, 'filebrowser');

  $("#copyForm").on("submit", function () {
    if ($.trim($("#copyDestination").val()) == "") {
      $("#copyNameRequiredAlert").show();
      $("#copyForm").find("input[name='*dest_path']").addClass("fieldError");
      resetPrimaryButtonsStatus(); //globally available
      return false;
    }
    return true;
  });

  $("#copyForm").bind("keypress", function(e) {
    if (e.keyCode == 13) {
      return false;
    }
  });

  huePubSub.publish('update.autocompleters');

  $(".create-directory-link").click(function () {
    window.hueAnalytics.log('filebrowser', 'new-directory-btn-click');
    $("#newDirectoryNameInput").val('');
    $("#createDirectoryModal").modal({
      keyboard:true,
      show:true
    });
  });

  $(".create-file-link").click(function () {
    $("#newFileNameInput").val('');
    $("#createFileModal").modal({
      keyboard:true,
      show:true
    });
  });

  $("#newDirectoryNameInput").focus(function () {
    $("#newDirectoryNameInput").removeClass("fieldError");
    $("#directoryNameRequiredAlert").hide();
    $("#directoryNameExistsAlert").hide();
    $("#smallFileSystemNameAlert").hide();
    $("#volumeBucketNameAlert").hide();
    $("#upperCaseVolumeBucketNameAlert").hide();
  });

  $("#newFileNameInput").focus(function () {
    $("#newFileNameInput").removeClass("fieldError");
    $("#fileNameRequiredAlert").hide();
    $("#fileNameExistsAlert").hide();
  });

  $(".pathChooser").click(function () {
    var self = this;
    $("#fileChooserRename").jHueFileChooser({
      initialPath:$(self).val(),
      onFileChoose:function (filePath) {
        $(self).val(filePath);
      },
      onFolderChange:function (folderPath) {
        $(self).val(folderPath);
      },
      createFolder:false,
      uploadFile:false
    });
    $("#fileChooserRename").slideDown();
  });

  $("*[rel='tooltip']").tooltip({ placement:"bottom" });

  fileBrowserViewModel.retrieveData();


  $("#editBreadcrumb").click(function (e) {
    if ($(e.target).is('ul')){
      $(this).hide();
      $(".hue-breadcrumbs").hide();
      $("#hueBreadcrumbText").show().focus();
      window.hueAnalytics.log('filebrowser', 'edit-breadcrumb-click');
    }
  });

  $("#hueBreadcrumbText").jHueHdfsAutocomplete({
    home: listDirOptions.home_directory,
    root: fileBrowserViewModel.rootTarget(),
    skipKeydownEvents: true,
    onEnter: function (el) {
      var target_path = stripHashes(el.val());
      if (el.val().split('/')[2] === '' && window.RAZ_IS_ENABLED){
        huePubSub.publish('hue.global.warning', {
          message: window.I18n('Listing of buckets is not allowed. Redirecting to the home directory.')
        });
        target_path = window.USER_HOME_DIR;
      } 
      fileBrowserViewModel.targetPath("/filebrowser/view=" + encodeURIComponent(target_path)); 
      fileBrowserViewModel.getStats(function (data) {
        const pathPrefix = "/filebrowser/view=";
        if (data.type != null && data.type == "file") {              
          huePubSub.publish('open.filebrowserlink', { pathPrefix, decodedPath: target_path});              
          return false;
        } else {
          huePubSub.publish('open.filebrowserlink', { pathPrefix, decodedPath: target_path, fileBrowserModel: fileBrowserViewModel});
        }
        $("#jHueHdfsAutocomplete").hide();
      });
    },
    onBlur: function() {
      $("#hueBreadcrumbText").hide();
      $(".hue-breadcrumbs").show();
      $("#editBreadcrumb").show();
    },
    smartTooltip: window.I18n('Did you know? You can use the tab key or CTRL + Space to autocomplete file and folder names')
  });

  $.ajaxSetup({
    error:function (x, e) {
      if (x.status == 500 && x.responseText.indexOf("jobbrowser") == -1) {
        if (x.responseJSON && x.responseJSON.detail) {
          huePubSub.publish('hue.global.error', {message: x.responseJSON.detail});
        }
        else {
          huePubSub.publish('hue.global.error', {message: window.I18n('There was a problem with your request.')});
        }
        $("#hueBreadcrumbText").blur();
      }
    }
  });


  $(".actionbar").data("originalWidth", $(".actionbar").width());

  $(".actionbarGhost").height($(".actionbar").outerHeight());

  resetActionbar();

  $('.page-content').scroll(function () {
    if ($('.page-content').scrollTop() > 50) {
      $(".actionbar").width($(".actionbar").data("originalWidth"));
      $(".actionbar").css("position", "fixed").css("top", "50px").css("zIndex", "1001");
      $(".actionbarGhost").removeClass("hide");
    } else {
      resetActionbar();
    }
  });

  $("#uploadFileModal").on("shown", function () {
    if (typeof _dropzone != "undefined") {
      _dropzone.disable();
    }
  });
  $("#uploadFileModal").on("hidden", function () {
    if (typeof _dropzone != "undefined") {
      _dropzone.enable();
    }
    $(".qq-upload-list").empty();
    $(".qq-upload-list-selector").empty();
    $(".qq-upload-drop-area").hide();
    $(".qq-upload-drop-area-selector").hide();
  });
});