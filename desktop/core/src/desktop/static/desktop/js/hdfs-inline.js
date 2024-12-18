
(function () {
    var viewModel = new HdfsViewModel();
    ko.cleanNode($('#securityHdfsComponents')[0]);
    ko.applyBindings(viewModel, $('#securityHdfsComponents')[0]);

    $(document).ready(function () {

      $(document).on("loadedUsers", function(){
        $(".user-list").select2("val", viewModel.doAs());
      });

      var _initialPath = "/";
      if (window.location.hash != "") {
        _initialPath = window.location.hash.substr(1).replace(/(<([^>]+)>)/ig, "");
      }
      viewModel.init(_initialPath);

      $("#path").jHueHdfsAutocomplete({
        home: viewModel.assist.path(),
        skipKeydownEvents: true,
        onPathChange: function (path) {
          viewModel.assist.path(path);
        },
        onEnter: function (el) {
          viewModel.assist.path(el.val());
        },
        smartTooltip: "Did you know? You can use the tab key or CTRL + Space to autocomplete file and folder names"
      });

      function resizeComponents () {
        $("#path").width($(".tree-toolbar").width() - 64);
        $("#expandableTree").height($(window).height() - 260);
        $(".acl-panel-content").height($(window).height() - 260);
      }

      resizeComponents();

      $(document).on("renderedTree", function() {
        var _path = viewModel.assist.path();
        if (_path[_path.length-1] == "/"){
          _path = _path.substr(0, _path.length - 1);
        }
        window.setTimeout(function(){
          if ($("a.anchor[href^='"+_path+"']").length > 0){
            $("#expandableTree").animate({
              scrollTop: ($("a.anchor[href^='"+_path+"']:first").position().top + $("#expandableTree").scrollTop() - $("#expandableTree").position().top - 4)+"px"
            }, 200);
          }
        }, 200)
      });

      $(document).on("updatedAcls", function() {
        huePubSub.publish('hue.global.info', { message: "The selected ACLs have been successfully updated."});
      });

      $(document).on("addedBulkAcls", function() {
        huePubSub.publish('hue.global.info', { message: "The current ACLs have been successfully added to the checked paths."});
        $("#bulkActionsModal").modal("hide");
      });

      $(document).on("deletedBulkAcls", function() {
        huePubSub.publish('hue.global.info', { message: "All the ACLs have been successfully removed from the checked paths."});
        $("#bulkActionsModal").modal("hide");
      });

      $(document).on("syncdBulkAcls", function() {
        huePubSub.publish('hue.global.info', { message: "All the ACLs for the checked items have been replaced with the current selection."});
        $("#bulkActionsModal").modal("hide");
      });

      var _resizeTimeout = -1;
      $(window).resize(function(){
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(resizeComponents, 100);
      });

      window.onhashchange = function() {
        if (window.location.pathname.indexOf('/security/hdfs') > -1) {
          viewModel.assist.path(window.location.hash.substr(1));
        }
      };

      $("#bulkActionsModal").modal({
        show: false
      });

      huePubSub.subscribe('app.gained.focus', function (app) {
        if (app === 'security_hdfs') {
          window.setTimeout(function () {
            window.location.hash = viewModel.lastHash;
          }, 0);
        }
      }, 'security_hdfs');

    });
  })();
