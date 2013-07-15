$("<style type='text/css'> .tooltip {z-index: 30000} .tourBuilder td { vertical-align: text-top } .tourBuilder span[rel='tooltip'] {cursor: pointer; color: #FFF; font-size: 14px} .tourBuilder { overflow-y: auto; overflow-x: hidden; color: #FFF; font-size: 11px; background-color: #333; padding: 10px; opacity: 0.9; position: fixed; width: 360px; right: 0; top: 0; z-index: 15000 } .tourBuilder select, .tourBuilder textarea  { font-size: 11px; } .tourBuilder input { font-size: 11px; height: 14px } </style>").appendTo($("head"));

     var _tbTour = {
       name: "",
       desc: "",
       path: location.pathname,
       steps: []
     };

     var _origTbTour = _tbTour;

     var _tb = $("<div>");
     _tb.addClass("tourBuilder");
     _tb.height($(window).height());
     _tb.appendTo($("body"));

     var _tbCog = $("<div>").attr("id", "tbCog").html('<i class="icon-cogs"></i>').addClass("jHueTourBadge").css("top", "64px");
     _tbCog.on("click", function () {
       _tb.show();
     });

     _tbCog.appendTo($("body"));

     var _html = "<h4>General</h4>" +
             "<table><tr><td>ID:</td><td><input class='input' type='text' id='tbName' /> <span rel='tooltip' title='unique tour name (location.pathname scope)'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>Name:</td><td><input class='input' type='text' id='tbDesc' /> <span rel='tooltip' title='the label shown on the question mark'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>Path:</td><td><input class='input' type='text' id='tbPath' value='" + _tbTour.path + "'/> <span rel='tooltip' title='string for the path to show this tour on, regex allowed'><i class='icon-question-sign'></i></span></td></tr></table>" +
             "<h4>New step</h4><table>" +
             "<tr><td>Visit URL:</td><td><input class='input' type='text' id='tbNewURL' /> <span rel='tooltip' title='overrides everything, redirects to specific url'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td colspan='2'>&nbsp;</td></tr>" +
             "<tr><td>Arrow on:</td><td><input class='input' type='text' id='tbNewArrow' /> <span rel='tooltip' title='the element relative to the popover is positioned'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>Expose:</td><td><input class='input' type='text' id='tbNewExpose' /> <span rel='tooltip' title='optional, the exposed object. if not present, arrowOn will be exposed'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>Title:</td><td><input class='input' type='text' id='tbNewTitle'/> <span rel='tooltip' title='popover title'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>Content:</td><td><textarea id='tbNewContent'></textarea> <span rel='tooltip' title='popover content, html enabled'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>Placement:</td><td><select class='input' id='tbNewPlacement'><option value='top' selected='selected'>Top</option><option value='bottom'>Bottom</option><option value='left'>Left</option><option value='right'>Right</option> </select> <span rel='tooltip' title='popover placement'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>Left:</td><td>Offset <input type='text' class='input-mini' id='tbNewOffsetLeft'/> Abs <input type='text' class='input-mini' id='tbNewAbsLeft'/></td></tr>" +
             "<tr><td>Top:</td><td>Offset <input type='text' class='input-mini' id='tbNewOffsetTop'/> Abs <input type='text' class='input-mini' id='tbNewAbsTop'/></td></tr>" +
             "<tr><td>On shown:</td><td><textarea id='tbNewShown'></textarea> <span rel='tooltip' title='javascript run on popover step shown. DANGER!'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>Wait:</td><td><input type='checkbox' id='tbNewWait'/> <span rel='tooltip' title='does not show the next button and waits for an action to go on with the tour'><i class='icon-question-sign'></i></span></td></tr>" +
             "<tr><td>&nbsp;</td><td style='text-align: right'><a href='javascript:void(0)' id='tbNewShow' class='btn btn-mini'>Show</a> <a id='tbNewAdd' href='javascript:void(0)' class='btn btn-mini'>Add to tour</a> </td></tr>" +
             "</table><h4>Steps</h4>" +
             "<div id='tbSteps'></div>" +
             "<h4>JSON</h4>" +
             "<textarea id='tbPreview' style='width: 90%'>" + JSON.stringify(_tbTour) + "</textarea><br/><a href='javascript:void(0)' id='tbLoadJson' class='btn btn-mini'>Load from JSON</a><br/><br/>" +
             "<div style='text-align: right'><a id='tbManageTours' class='btn' href='javascript:void(0)' style='float:left'><i class='icon-sitemap'></i></a> <a id='tbAddTour' class='btn' href='javascript:void(0)'><i class='icon-plus-sign-alt'></i></a> <a id='tbClearCache' class='btn' href='javascript:void(0)'><i class='icon-trash'></i></a> <a id='tbTryTour' title='Try tour' class='btn' href='javascript:void(0)'><i class='icon-eye-open'></i></a></div><br/><br/>";


     _tb.html(_html);


     var _managerHtml = "<div id='tbToursModal' class='modal hide fade'>" +
             "<div class='modal-header'>" +
             "<button type='button' class='close' data-dismiss='modal' aria-hidden='true'>&times;</button>" +
             "<h3>Available tours</h3>" +
             "</div>" +
             "<div class='modal-body'>" +
             "<p><span id='tbTourList'></span><br/><h4>Content for available.tours.js</h4><textarea id='tbAvailableContent' style='width:90%'></textarea><br/><a href='javascript:void(0)' id='tbLoadToursJson' class='btn btn-mini'>Load from JSON</a></p>" +
             "</div>" +
             "<div class='modal-footer'><a href='javascript:void(0)' data-dismiss='modal' class='btn'>Close</a></div></div>";

     $(_managerHtml).appendTo($("body"));


     $("span[rel='tooltip']").tooltip({
       placement: "left"
     });

     _tb.find("input").on("change", function () {
       updateTour();
     });

     $("textarea").on("focus", function () {
       var $this = $(this);
       $this.select();

       // Work around Chrome's little problem
       $this.mouseup(function () {
         // Prevent further mouseup intervention
         $this.unbind("mouseup");
         return false;
       });
     });

     var _tbTourIsEditing = -1;
     var _tbTourIsStepEditing = -1;


     function updateTour() {
       _tbTour.name = $("#tbName").val();
       _tbTour.desc = $("#tbDesc").val();
       _tbTour.path = $("#tbPath").val();

       if ($("#tbNewExpose").val() == "") {
         $("#tbNewExpose").val($("#tbNewArrow").val());
       }
       function fillItem(item) {
         $("#tbNewURL").val(item.visitUrl);
         $("#tbNewArrow").val(item.arrowOn);
         $("#tbNewExpose").val(item.expose);
         $("#tbNewTitle").val(item.title);
         $("#tbNewContent").val(item.content);
         $("#tbNewPlacement").val(item.placement);
         $("#tbNewShown").val(item.onShown);
         if (item.waitForAction == true){
           $("#tbNewWait").prop("checked", true);
         }
         else {
           $("#tbNewWait").prop("checked", false);
         }
         $("#tbNewOffsetTop").val("");
         $("#tbNewAbsTop").val("");
         $("#tbNewOffsetLeft").val("");
         $("#tbNewAbsLeft").val("");
         if (item.left != undefined && item.left != "") {
           if ($.isNumeric(item.left)) {
             $("#tbNewOffsetLeft").val(item.left);
           }
           else {
             $("#tbNewAbsLeft").val(item.left.substring(0, item.left.length - 2));
           }
         }
         if (item.top != undefined && item.top != "") {
           if ($.isNumeric(item.top)) {
             $("#tbNewOffsetTop").val(item.top);
           }
           else {
             $("#tbNewAbsTop").val(item.top.substring(0, item.top.length - 2));
           }
         }
       }

       $("#tbSteps").empty();
       $(_tbTour.steps).each(function (cnt, item) {
         var _trow = $("<div>").html("&nbsp;" + (item.visitUrl!="" && item.visitUrl!=undefined?"URL: " + item.visitUrl:"Title: "+item.title));

         var _trowdelete = $("<a>");
         _trowdelete.addClass("btn").addClass("btn-mini").html("<i class='icon-trash'></i>").css("margin", "3px").on("click", function () {
           _tbTour.steps.splice(cnt, 1);
           updateTour();
         });
         _trowdelete.prependTo(_trow);

         var _trowcopy = $("<a>");
         _trowcopy.addClass("btn").addClass("btn-mini").html("<i class='icon-copy'></i>").css("margin", "3px").on("click", function () {
           fillItem(item);
         });
         _trowcopy.prependTo(_trow);

         var _trowedit = $("<a>");
         _trowedit.addClass("btn").addClass("btn-mini").html("<i class='icon-edit'></i>").css("margin", "3px").on("click", function () {
           fillItem(item);
           _tbTourIsStepEditing = cnt;
           $("#tbNewAdd").text("Update step");
         });
         _trowedit.prependTo(_trow);

         var _trowup = $("<a>");
         _trowup.addClass("btn").addClass("btn-mini").html("<i class='icon-arrow-up'></i>").css("margin", "3px").on("click", function () {
           var _newPos = cnt - 1;
           if (cnt == 0) {
             _newPos = _tbTour.steps.length - 1;
           }
           _tbTour.steps.move(cnt, _newPos);
           updateTour();
         });
         _trowup.prependTo(_trow);

         var _trowdown = $("<a>");
         _trowdown.addClass("btn").addClass("btn-mini").html("<i class='icon-arrow-down'></i>").css("margin", "3px").on("click", function () {
           var _newPos = cnt + 1;
           if (cnt == _tbTour.steps.length - 1) {
             _newPos = 0;
           }
           _tbTour.steps.move(cnt, _newPos);
           updateTour();
         });
         _trowdown.prependTo(_trow);

         _trow.appendTo($("#tbSteps"));
       });

       $("#tbPreview").val(JSON.stringify(_tbTour));

       $.totalStorage("jHueTourBuilderTemp", _tbTour);
     }

     $("#tbLoadJson").on("click", function () {
       _tbTourIsStepEditing = -1;
       try {
         _tbTour = JSON.parse($.trim($("#tbPreview").val()));
         $("#tbName").val(_tbTour.name);
         $("#tbDesc").val(_tbTour.desc);
         $("#tbPath").val(_tbTour.path);
         updateTour();
       }
       catch (exception) {
         alert("It seems you don't eat JSON for breakfast:" + exception)
       }
     });

      $("#tbLoadToursJson").on("click", function () {
        _tbTourIsEditing = -1;
       _tbTourIsStepEditing = -1;
       try {
         var _paste = $.trim($("#tbAvailableContent").val());
         if (_paste.indexOf("$.jHueTour") > -1){
           _paste = _paste.substr(11);
         }
         if (_paste[_paste.length - 1] == ";"){
           _paste = _paste.substring(0, _paste.length - 2);
         }
         var _trz = JSON.parse(_paste);
         $.totalStorage("jHueTourBuilderTours", _trz.tours);
         $("#tbManageTours").click();
       }
       catch (exception) {
         alert("It seems you don't eat JSON for breakfast:" + exception)
       }
     });

     $("#tbNewShow").on("click", function () {
       $(".popover").remove();
       _tbTourIsEditing = -1;
       _tbTourIsStepEditing = -1;
       $(".jHueTourExposed").removeClass("jHueTourExposed").css("position", "");
       $("#jHueTourMask").width($(document).width()).height($(document).height()).show();
       var _closeBtn = $("<a>");
       _closeBtn.addClass("btn").addClass("btn-mini").html('<i class="icon-remove"></i>').css("float", "right").css("margin-top", "-4px").css("margin-right", "-6px");
       _closeBtn.click(function () {
         $(".popover").remove();
         $(".jHueTourExposed").removeClass("jHueTourExposed");
         $("#jHueTourMask").hide();
       });

       if ($($("#tbNewArrow").val()).length > 0) {
         $($("#tbNewArrow").val()).popover('destroy').popover({
           title: $("#tbNewTitle").val(),
           content: $("#tbNewContent").val() + "<br/>",
           html: true,
           trigger: 'manual',
           placement: $("#tbNewPlacement").val()
         }).popover('show');
         if ($("#tbNewOffsetTop").val() != "") {
           $(".popover").css("top", ($(".popover").position().top + ($("#tbNewOffsetTop").val() * 1)) + "px");
         }
         if ($("#tbNewAbsTop").val() != "") {
           $(".popover").css("top", $("#tbNewAbsTop").val() + "px");
         }
         if ($("#tbNewOffsetLeft").val() != "") {
           $(".popover").css("left", ($(".popover").position().left + ($("#tbNewOffsetLeft").val() * 1)) + "px");
         }
         if ($("#tbNewAbsLeft").val() != "") {
           $(".popover").css("left", $("#tbNewAbsLeft").val() + "px");
         }
         $(".popover-title").html($("#tbNewTitle").val());
         _closeBtn.prependTo($(".popover-title"));
         $("<a class='btn btn-mini' style='margin-top:10px' onclick='alert(\"Nothing else to do? :)\")'><i class='icon-smile'></i></a>").appendTo($(".popover-content p"));
       }

       var _exposedElement = $($("#tbNewExpose").val());
       if (_exposedElement.css("position") === undefined || _exposedElement.css("position") != "fixed") {
         _exposedElement.css("position", "relative");
       }
       _exposedElement.addClass("jHueTourExposed");

       if ($("#tbNewShown").val() != "") {
         window.setTimeout($("#tbNewShown").val(), 10);
       }
     });

     Array.prototype.move = function (old_index, new_index) {
       if (new_index >= this.length) {
         var k = new_index - this.length;
         while ((k--) + 1) {
           this.push(undefined);
         }
       }
       this.splice(new_index, 0, this.splice(old_index, 1)[0]);
       return this;
     };

     $("#tbNewAdd").on("click", function () {
       var _newStep = {
         arrowOn: $("#tbNewArrow").val(),
         expose: $("#tbNewExpose").val(),
         title: $("#tbNewTitle").val(),
         content: $("#tbNewContent").val(),
         placement: $("#tbNewPlacement").val(),
         onShown: $("#tbNewShown").val(),
         waitForAction: $("#tbNewWait").is(":checked")
       };

       if ($("#tbNewURL").val() != ""){
         _newStep = {
           visitUrl: $("#tbNewURL").val()
         }
       }

       if ($("#tbNewOffsetTop").val() != "") {
         _newStep.top = $("#tbNewOffsetTop").val() * 1;
       }
       if ($("#tbNewAbsTop").val() != "") {
         _newStep.top = $("#tbNewAbsTop").val() + "px";
       }
       if ($("#tbNewOffsetLeft").val() != "") {
         _newStep.left = $("#tbNewOffsetLeft").val() * 1;
       }
       if ($("#tbNewAbsLeft").val() != "") {
         _newStep.left = $("#tbNewAbsLeft").val() + "px";
       }
       if (_tbTourIsStepEditing > -1) {
         _tbTour.steps[_tbTourIsStepEditing] = _newStep;
         _tbTourIsStepEditing = -1;
         $("#tbNewAdd").text("Add to tour");
       }
       else {
         _tbTour.steps.push(_newStep);
       }
       updateTour();
       $(".popover").remove();
       $(".jHueTourExposed").removeClass("jHueTourExposed");
       $("#jHueTourMask").hide();

       $("#tbNewURL").val("");
       $("#tbNewArrow").val("");
       $("#tbNewExpose").val("");
       $("#tbNewTitle").val("");
       $("#tbNewContent").val("");
       $("#tbNewShown").val("");
       $("#tbNewWait").prop("checked", false);
       $("#tbNewPlacement").val("");
       $("#tbNewOffsetTop").val("");
       $("#tbNewAbsTop").val("");
       $("#tbNewOffsetLeft").val("");
       $("#tbNewAbsLeft").val("");
     });

     $("#tbTryTour").on("click", function () {
       $.jHueTour("clear");
       $.jHueTour({ tours: [_tbTour]});
       _tb.hide();
       $.jHueTour("play");
     });

     $("#tbClearCache").on("click", function () {
       $.totalStorage("jHueTourBuilderTemp", null);
       _tbTour = _origTbTour;
       $("#tbName").val(_tbTour.name);
       $("#tbDesc").val(_tbTour.desc);
       $("#tbPath").val(_tbTour.path);
       updateTour();
     });

     $("#tbAddTour").on("click", function () {

       var _tbStoredTours = [];
       if ($.totalStorage("jHueTourBuilderTours") != null){
         _tbStoredTours = $.totalStorage("jHueTourBuilderTours");
       }

       if (_tbTourIsEditing > -1) {
         _tbStoredTours[_tbTourIsEditing] = _tbTour;
         _tbTourIsEditing = -1;
         $("#tbAddTour").html("<i class='icon-plus-sign-alt'></i>");
       }
       else {
         _tbStoredTours.push(_tbTour);
       }

       $.totalStorage("jHueTourBuilderTours", _tbStoredTours);
       $("#tbClearCache").click();
     });

     $("#tbManageTours").on("click", function () {
       $("#tbTourList").empty();
       $($.totalStorage("jHueTourBuilderTours")).each(function (cnt, item) {
         var _trow = $("<div>").html("&nbsp;Name: " + item.name + ", Desc: "+ item.desc + ", Path: "+ item.path);

         var _trowdelete = $("<a>");
         _trowdelete.addClass("btn").addClass("btn-mini").html("<i class='icon-trash'></i>").css("margin", "3px").on("click", function () {
           var _tmpTrz = $.totalStorage("jHueTourBuilderTours");
           _tmpTrz.splice(cnt, 1);
           $.totalStorage("jHueTourBuilderTours", _tmpTrz);
           $("#tbManageTours").click();
         });
         _trowdelete.prependTo(_trow);

         var _trowcopy = $("<a>");
         _trowcopy.addClass("btn").addClass("btn-mini").html("<i class='icon-copy'></i>").css("margin", "3px").on("click", function () {
           $.totalStorage("jHueTourBuilderTemp", null);
           _tbTour = item;
           $("#tbName").val(_tbTour.name);
           $("#tbDesc").val(_tbTour.desc);
           $("#tbPath").val(_tbTour.path);
           updateTour();
           $("#tbToursModal").modal("hide");
         });
         _trowcopy.prependTo(_trow);

         var _trowedit = $("<a>");
         _trowedit.addClass("btn").addClass("btn-mini").html("<i class='icon-edit'></i>").css("margin", "3px").on("click", function () {
           $.totalStorage("jHueTourBuilderTemp", null);
           _tbTour = item;
           $("#tbName").val(_tbTour.name);
           $("#tbDesc").val(_tbTour.desc);
           $("#tbPath").val(_tbTour.path);
           updateTour();
           _tbTourIsEditing = cnt;
           $("#tbAddTour").html("<i class='icon-save'></i>");
           $("#tbToursModal").modal("hide");
         });
         _trowedit.prependTo(_trow);

         _trow.appendTo($("#tbTourList"));
       });

       var _trz = {
         tours: $.totalStorage("jHueTourBuilderTours")
       };
       $("#tbAvailableContent").val("$.jHueTour(" + JSON.stringify(_trz) + ");");
       $("#tbToursModal").modal("show");
     });

     var _changeSide = $("<a>");
     _changeSide.addClass("btn").addClass("btn-mini").addClass("pull-right");
     _changeSide.on("click", function (e) {
       e.preventDefault();
       e.stopImmediatePropagation();
       if (_tb.css("left") != "0px") {
         _tb.css("left", "0");
         _tb.css("right", "auto");
         $(this).html("<i class='icon-arrow-right'></i>");
       }
       else {
         _tb.css("right", "0");
         _tb.css("left", "auto");
         $(this).html("<i class='icon-arrow-left'></i>");
       }
     });
     _changeSide.html("<i class='icon-arrow-left'></i>");
     _changeSide.prependTo(_tb);

     var _hideTb = $("<a>");
     _hideTb.addClass("btn").addClass("btn-mini").addClass("pull-right").css("margin-left", "4px");
     _hideTb.on("click", function (e) {
       e.preventDefault();
       e.stopImmediatePropagation();
       _tb.hide();
     });
     _hideTb.html("<i class='icon-remove'></i>");
     _hideTb.prependTo(_tb);

      // preload
      if ($.totalStorage("jHueTourBuilderTemp") != null){
       _tbTour = $.totalStorage("jHueTourBuilderTemp");
       $("#tbName").val(_tbTour.name);
       $("#tbDesc").val(_tbTour.desc);
       $("#tbPath").val(_tbTour.path);
       updateTour();
     }
     if ($.totalStorage("jHueTourBuilderTours") == null){
       $.totalStorage("jHueTourBuilderTours", []);
     }
      else {
       $($.totalStorage("jHueTourBuilderTours")).each(function (cnt, item) {
         if (item.name == _tbTour.name && item.path == _tbTour.path){
            _tbTourIsEditing = cnt;
           $("#tbAddTour").html("<i class='icon-save'></i>");
         }
       });
     }

     $(window).resize(function () {
       _tb.height($(window).height());
     });