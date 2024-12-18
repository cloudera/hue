
(function () {
  var FileViewOptionsElement = document.getElementById('FileViewOptions');
  FileViewOptions = JSON.parse(FileViewOptionsElement.textContent);
  var viewOptions = FileViewOptions.view;

  var pages = {};
  var viewModel = new DisplayViewModel({
    base_url: FileViewOptions.url,
    compression: viewOptions['compression'],
    mode: viewOptions['mode'],
    begin: viewOptions['offset'] + 1,
    end: viewOptions['end'],
    length: viewOptions['length'],
    size: FileViewOptions['stats']['size'],
    max_size: viewOptions['max_chunk_size']
  });

  function resizeText() {
    hueUtils.waitForRendered('#fileArea', function(el){ return el.is(':visible') }, function(){
      $("#fileArea").height($(window).height() - $("#fileArea").offset().top - 30);
    });
  }

  function formatHex(number, padding) {
    if ("undefined" != typeof number) {
      var _filler = "";
      for (var i = 0; i < padding - 1; i++) {
        _filler += "0";
      }
      return (_filler + number.toString(16)).substr(-padding);
    }
    return "";
  }

  function renderPages() {
    var _html = "";
    for (var i = viewModel.page(); i <= viewModel.upperPage(); i++) {
      _html += "<a id='page" + i + "'><div class='fill-file-area'></div></a>";
    }
    $("#fileArea pre").html(_html);
  }

  var getChunks = function (startPage, endPage, view) {
    var chunkSize = view.length / (endPage - startPage + 1);
    return view.contents.match(new RegExp('[\\s\\S]{1,' + chunkSize + '}', 'g'));
  }

  // The python backend incorrectly encodes a couple of characters that we fix
  // in the frontend here 
  function fixSpecialCharacterEncoding (url) {
    // Singel quotes (') encoded as Unicode Hex Character
    // will cause the $.getJSON call and file downloads to produce an incorrect url, 
    // so we remove the encoding and use plain single quotes.
    const modifiedUrl = url.replaceAll('&#x27;', "'");
    // Entity encoded ampersand doesn't work in file or folder names and
    // needs to be replaced with '&'
    return modifiedUrl.replaceAll('&amp;', "&");    
  }

  function getContent (callback) {
    // We don't use the python variable path_enc here since that will 
    // produce a double encoded path after calling the python url function
    // In this case we don't want to sanitize the path for XSS as we want exact match on the actual file name,
    // so to prevent breaking the page on substitution we enforce a js compatible string by only encoding the backtick
    // char (`) with a js decode to restore it in case file actually has backtick in the name.
    const decodedPath = `/user/admin/ai_case.txt`.replaceAll('&#96;', '`');
    const encodedPath = encodeURIComponent(decodedPath);
    const pathPrefix = "/filebrowser/view=";
    const contentPath = pathPrefix+encodedPath;
    
    viewModel.isLoading(true);

    var startPage = viewModel.page();
    var endPage = viewModel.upperPage();

    var params = {
      offset: (startPage - 1) * viewModel.length(),
      length: viewModel.length() * (endPage - startPage + 1),
      compression: viewModel.compression(),
      mode: viewModel.mode()
    };

    $.getJSON(contentPath, params, function (data) {
      var _html = "";

      viewModel.file(ko.mapping.fromJS(data, { 'ignore': ['view.contents', 'view.xxd'] }));
      if (data.view.contents) {
        $('#fileArea pre').show();
        $('.binary').hide();
        var chunks = getChunks(startPage, endPage, data.view)
        for (var i = startPage; i <= endPage; i++) {
          pages[i] = chunks.shift();
        }
        if ($("#fileArea pre").children().length == 0) {
          renderPages();
        }
        $.each(pages, function (page, content) {
          var $page = $('#page' + page);
          if ($page.children('.fill-file-area').length > 0) {
            $page.html("<div style='display: inline'>" + $("<span>").text(content).html() + "</div>")
          }
        });
      }

      if (data.view.xxd != null) {
        pages[startPage] = data.view.xxd;
        $('#fileArea pre').hide();
        $('.binary').show();

        $(data.view.xxd).each(function (cnt, item) {
          _html += "<tr><td>" + formatHex(item[0], 7) + ":&nbsp;</td><td>";

          for (var i = 0; i < item[1].length; i++) {
            _html += formatHex(item[1][i][0], 2) + " " + formatHex(item[1][i][1], 2) + " ";
          }

          _html += "</td><td>&nbsp;&nbsp;" + $("<span>").text(item[2]).html() + "</td></tr>";
        });

        $(".binary tbody").html(_html);
      }

      if (callback) {
        callback();
      }

      viewModel.isLoading(false);
    });
  }

  function DisplayViewModel (params) {
    var self = this;

    self.goToParentDirectory = function () {
      huePubSub.publish('open.filebrowserlink', { pathPrefix: "/filebrowser/view=", decodedPath: viewOptions['dirname'] });
    }

    self.changePage = function () {
      renderPages();
      getContent(function () {
        $("#fileArea").scrollTop(0);
      });
    }

    self.MAX_ALLOWED_PAGES_PER_REQUEST = 255;
    self.PAGES_PER_CHUNK = 50;

    self.isViewing = ko.observable(true);
    self.isViewing.subscribe(function(val){
      if (val){
        window.setTimeout(resizeText, 0);
      }
    });

    self.base_url = ko.observable(params.base_url);
    self.compression = ko.observable(params.compression);
    self.mode = ko.observable(params.mode);
    self.mode.subscribe(function(val){
      window.setTimeout(resizeText, 0);
    });
    self.begin = ko.observable(params.begin);
    self.end = ko.observable(params.end);
    self.length = ko.observable(params.length);
    self.size = ko.observable(params.size);
    self.page = ko.observable(1);
    self.isLoading = ko.observable(false);

    self.file = ko.observable();

    self.totalPages = ko.computed(function () {
      return Math.max(Math.ceil(self.size() / self.length()), 1);
    });

    self.upperPage = ko.observable(Math.min(self.totalPages(), 50));

    self.offset = ko.computed(function () {
      return ((self.page() - 1) * self.length()) - 1;
    });

    self.url = ko.computed(function () {
      return self.base_url()
              + "?offset=" + self.offset()
              + "&length=" + self.length()
              + "&compression=" + self.compression()
              + "&mode=" + self.mode();
    });

    self.switchMode = function (newMode) {
      self.mode(newMode);
      self.changePage();
    }

    self.switchCompression = function (newCompression) {
      self.compression(newCompression);
      self.page(1);
      self.upperPage(1);
      self.changePage();
    }

    self.editFile = function() {
      self.isViewing(false);
      self.isLoading(true);

      const encodedPath = encodeURIComponent(FileViewOptions['path']);
      $.ajax({
        url: '/filebrowser/edit=' + encodedPath + '?is_embeddable=true',
        beforeSend:function (xhr) {
          xhr.setRequestHeader('X-Requested-With', 'Hue');
        },
        dataType:'html',
        success:function (response) {
          $('#fileeditor').html(response);
          self.isLoading(false);
        }
      });
    }

    self.viewFile = function() {
      $('#fileeditor').html('');
      self.isViewing(true);
      self.page(1);
      self.upperPage(1);
      self.changePage();
    }

    self.downloadFile = function () {
      huePubSub.publish('open.filebrowserlink', { pathPrefix: "/filebrowser/download=", decodedPath:  FileViewOptions['path'] });
    };

    self.pageChanged = function () {
      self.page(self.page() * 1);
      self.upperPage(self.upperPage() * 1);
      if (self.page() > self.totalPages()) {
        self.page(self.totalPages());
      }
      if (self.page() < 1 || !$.isNumeric(self.page())) {
        self.page(1);
      }
      if (self.page() > self.upperPage()) {
        self.upperPage(self.page());
      }
      self.changePage();
    };

    self.upperPageChanged = function () {
      self.page(self.page() * 1);
      self.upperPage(self.upperPage() * 1);
      if (self.upperPage() > self.totalPages()) {
        self.upperPage(self.totalPages());
      }
      if (self.upperPage() < 1 || !$.isNumeric(self.upperPage())) {
        self.upperPage(1);
      }
      if (self.upperPage() < self.page()) {
        self.page(self.upperPage());
      }
      if (self.upperPage() - self.page() > self.MAX_ALLOWED_PAGES_PER_REQUEST) {
        self.upperPage(self.page() + self.MAX_ALLOWED_PAGES_PER_REQUEST);
        huePubSub.publish('hue.global.info', {
          message: "Sorry, you cannot request for more than 255 pages."
        });
      }
      self.changePage();
    };

    self.nextPage = function () {
      self.page(self.page() * 1);
      self.upperPage(self.upperPage() * 1);
      if (!($("#fileviewerComponents .next-page").hasClass("disabled"))) {
        if (self.page() == self.upperPage()) {
          self.page(self.page() + 1);
          self.upperPage(self.upperPage() + 1);
        } else {
          var _difference = self.upperPage() - self.page();
          self.page(self.upperPage() + 1);
          self.upperPage(Math.min(self.page() + _difference, self.totalPages()));
        }
        self.changePage();
      }
    };

    self.previousPage = function () {
      self.page(self.page() * 1);
      self.upperPage(self.upperPage() * 1);
      if (!($("#fileviewerComponents .previous-page").hasClass("disabled"))) {
        if (self.page() == self.upperPage()) {
          self.page(self.page() - 1);
          self.upperPage(self.upperPage() - 1);
        } else {
          var _difference = self.upperPage() - self.page();
          self.upperPage(self.page() - 1);
          self.page(Math.max(self.page() - _difference - 1, 1));
        }
        self.changePage();
      }
    };

    self.lastPage = function () {
      if (!($("#fileviewerComponents .last-page").hasClass("disabled"))) {
        var lastDiff = self.upperPage() - self.page() + 1;
        self.page(Math.max(1, self.totalPages() - lastDiff));
        self.upperPage(self.totalPages());
        self.changePage();
      }
    };

    self.firstPage = function () {
      if (!($("#fileviewerComponents .first-page").hasClass("disabled"))) {
        var lastDiff = self.upperPage() - self.page() + 1;
        self.page(1);
        if (lastDiff > 1) {
          self.upperPage(Math.min(self.totalPages(), lastDiff))
        } else {
          self.upperPage(Math.min(self.totalPages(), 50));
        }
        self.changePage();
      }
    };
  }

  $(document).ready(function () {
    ko.applyBindings(viewModel, $('#fileviewerComponents')[0]);


    setTimeout(function () {
      resizeText();
      getContent();
    }, 100);

    var _resizeTimeout = -1;

    $(window).on("resize", function () {
      clearTimeout(_resizeTimeout);
      _resizeTimeout = setTimeout(function () {
        resizeText();
        $('#fileviewerComponents .fill-file-area').css('height', $("#fileArea").height() + 'px');
      }, 300);
    });

    $("#fileArea").jHueScrollUp();
  });
}());
