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

/**
 * Modal Control
 * Displays a single node in a modal window of your choosing.
 * Make sure to update the 'context' member and 'template' members.
 * IMPORTANT: Use 'setTemplate', then 'show'.
 */
var ModalModule = function($, ko) {
  var module = function(modal, template) {
    var self = this;

    self.el = self.modal = $(modal);
    self.context = ko.observable();
    self.template = ko.observable(template || '');
    self.bound = false;

    // exit with escape key.
    $(window).on('keyup', function(e) {
      if (e.keyCode == 27) {
        $('.modal-backdrop').click();
      }
    });
  };

  module.prototype.show = function(context) {
    var self = this;

    if (context) {
      self.context(context);
    }

    ko.applyBindings(self, self.modal[0]);
    self.modal.modal('show');
  };

  module.prototype.hide = function() {
    var self = this;

    self.modal.modal('hide');
    if (self.modal.length > 0 && !!ko.dataFor(self.modal[0])) {
      ko.cleanNode(self.modal[0]);
    }
  };

  module.prototype.setTemplate = function(template) {
    var self = this;

    if (self.modal.length > 0 && !!ko.dataFor(self.modal[0])) {
      ko.cleanNode(self.modal[0]);
    }
    self.template( template );
  };

  module.prototype.recenter = function(offset_x, offset_y) {
    var self = this;

    var MARGIN = 10; // pixels around the modal

    var modalContentHeight = (($(window).height() - MARGIN*2) -
        (self.modal.find(".modal-header").outerHeight() + self.modal.find(".modal-header").outerHeight())) - 20;

    self.modal.css("width", ($(window).width() - MARGIN*2)+"px");
    self.modal.find(".modal-content").css("max-height", modalContentHeight+"px").css("height", modalContentHeight+"px");

    var top = ( ($(window).height() - self.modal.outerHeight(false)) / 2 );
    var left = ( ($(window).width() - self.modal.outerWidth(false)) / 2 );
    if (top < 0) {
      top = 0;
    }
    if (left < 0) {
      left = 0;
    }
    top += offset_y || 0;
    left += offset_x || 0;
    self.modal.css({top: top +'px', left:  left+'px'});
  };

  module.prototype.addDecorations = function () {
    $(".popover").remove();

    $("input[name='job_xml']:not(.pathChooser)").addClass("pathChooser").after(hueUtils.getFileBrowseButton($("input[name='job_xml']:not(.pathChooser)")));
    $("input[name='jar_path']").addClass("pathChooser").after(hueUtils.getFileBrowseButton($("input[name='jar_path']")));
    $("input[name='script_path']").addClass("pathChooser").after(hueUtils.getFileBrowseButton($("input[name='script_path']")));
    $("input[name='command']").addClass("pathChooser").after(hueUtils.getFileBrowseButton($("input[name='command']")));

    if (typeof CodeMirror !== 'undefined' && $("textarea[name='xml']").length > 0) {
      $("textarea[name='xml']").hide();
      var xmlEditor = $("<textarea>").attr("id", "tempXml").prependTo($("textarea[name='xml']").parent())[0];
      var codeMirror = CodeMirror(function (elt) {
        xmlEditor.parentNode.replaceChild(elt, xmlEditor);
      }, {
        value:$("textarea[name='xml']").val(),
        lineNumbers:true,
        autoCloseTags:true
      });
      codeMirror.on("update", function () {
        ko.dataFor($("textarea[name='xml']")[0]).xml(codeMirror.getValue());
      });
    }
    $("*[rel=popover]").each(function(){
      if ($(this).find("input").length > 0){
        $(this).popover({
          placement:'right',
          trigger:'hover',
          selector: 'input'
        });
      }
      else {
        $(this).popover({
          placement:'right',
          trigger:'hover'
        });
      }
    });
    $(".propKey").typeahead({
      source:(typeof AUTOCOMPLETE_PROPERTIES != 'undefined') ? AUTOCOMPLETE_PROPERTIES : []
    });
  }

  return module;
};