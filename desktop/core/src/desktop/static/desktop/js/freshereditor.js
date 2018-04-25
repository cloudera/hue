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

(function() {
  (function($) {
    var methods;
    methods = {
      edit: function(isEditing) {
        return this.each(function() {
          return $(this).attr("contentEditable", isEditing || false);
        });
      },
      save: function(callback) {
        return this.each(function() {
          return callback($(this).attr('id'), $(this).html());
        });
      },
      createlink: function() {
        var urlPrompt;
        urlPrompt = prompt("Enter URL:", "http://");
        return document.execCommand("createlink", false, urlPrompt);
      },
      insertimage: function() {
        var urlPrompt;
        urlPrompt = prompt("Enter Image URL:", "http://");
        return document.execCommand("insertimage", false, urlPrompt);
      },
      formatblock: function(block) {
        return document.execCommand("formatblock", null, block);
      },
      init: function(opts) {
        var $toolbar, button, command, commands, excludes, font, font_list, fontnames, fontsize, fontsizes, group, groups, options, shortcuts, size_list, _i, _j, _k, _l, _len, _len2, _len3, _len4;
        options = opts || {};
        groups = [
          [
            {
              name: 'bold',
              label: "<span style='font-weight:bold;'>B</span>",
              title: 'Bold (Ctrl+B)',
              classname: 'toolbar_bold'
            }, {
            name: 'italic',
            label: "<span style='font-style:italic;'>I</span>",
            title: 'Italic (Ctrl+I)',
            classname: 'toolbar_italic'
          }, {
            name: 'underline',
            label: "<span style='text-decoration:underline!important;'>U</span>",
            title: 'Underline (Ctrl+U)',
            classname: 'toolbar_underline'
          }, {
            name: 'strikethrough',
            label: "<span style='text-shadow:none;text-decoration:line-through;'>ABC</span>",
            title: 'Strikethrough',
            classname: 'toolbar_strikethrough'
          }, {
            name: 'removeFormat',
            label: "<i class='fa fa-minus'></i>",
            title: 'Remove Formating (Ctrl+M)',
            classname: 'toolbar_remove'
          }
          ], [
            {
              name: 'fontname',
              label: "F <span class='caret'></span>",
              title: 'Select font name',
              classname: 'toolbar_fontname dropdown-toggle',
              dropdown: true
            }
          ], [
            {
              name: 'FontSize',
              label: "<span style='font:bold 16px;'>A</span><span style='font-size:8px;'>A</span> <span class='caret'></span>",
              title: 'Select font size',
              classname: 'toolbar_fontsize dropdown-toggle',
              dropdown: true
            }
          ], [
            {
              name: 'forecolor',
              label: "<div style='color:#ff0000;'>A <span class='caret'></span></div>",
              title: 'Select font color',
              classname: 'toolbar_forecolor dropdown-toggle',
              dropdown: true
            }
          ], [
            {
              name: 'backcolor',
              label: "<div style='display:inline-block;margin:3px;margin-top:4px;width:15px;height:12px;background-color:#0B7FAD;'></div> <span class='caret'></span>",
              title: 'Select background color',
              classname: 'toolbar_bgcolor dropdown-toggle',
              dropdown: true
            }
          ], [
            {
              name: 'justifyleft',
              label: "<i class='fa fa-align-left' style='margin-top:2px;'></i>",
              title: 'Left justify',
              classname: 'toolbar_justifyleft'
            }, {
              name: 'justifycenter',
              label: "<i class='fa fa-align-center' style='margin-top:2px;'></i>",
              title: 'Center justify',
              classname: 'toolbar_justifycenter'
            }, {
              name: 'justifyright',
              label: "<i class='fa fa-align-right' style='margin-top:2px;'></i>",
              title: 'Right justify',
              classname: 'toolbar_justifyright'
            }, {
              name: 'justifyfull',
              label: "<i class='fa fa-align-justify' style='margin-top:2px;'></i>",
              title: 'Full justify',
              classname: 'toolbar_justifyfull'
            }
          ], [
            {
              name: 'createlink',
              label: "<i style='margin-top:2px;' class='fa fa-external-link'></i>",
              title: 'Link to a web page (Ctrl+L)',
              userinput: "yes",
              classname: 'toolbar_link'
            }, {
              name: 'insertimage',
              label: "<i style='margin-top:2px;' class='fa fa-picture-o'></i>",
              title: 'Insert an image (Ctrl+G)',
              userinput: "yes",
              classname: 'toolbar_image'
            }, {
              name: 'insertorderedlist',
              label: "<i class='fa fa-list-alt' style='margin-top:2px;'></i>",
              title: 'Insert ordered list',
              classname: 'toolbar_ol'
            }, {
              name: 'insertunorderedlist',
              label: "<i class='fa fa-list' style='margin-top:2px;'></i>",
              title: 'Insert unordered list',
              classname: 'toolbar_ul'
            }
          ], [
            {
              name: 'insertparagraph',
              label: 'P',
              title: 'Insert a paragraph (Ctrl+Alt+0)',
              classname: 'toolbar_p',
              block: 'p'
            }, {
              name: 'insertheading1',
              label: 'H1',
              title: "Heading 1 (Ctrl+Alt+1)",
              classname: 'toolbar_h1',
              block: 'h1'
            }, {
              name: 'insertheading2',
              label: 'H2',
              title: "Heading 2 (Ctrl+Alt+2)",
              classname: 'toolbar_h2',
              block: 'h2'
            }, {
              name: 'insertheading3',
              label: 'H3',
              title: "Heading 3 (Ctrl+Alt+3)",
              classname: 'toolbar_h3',
              block: 'h3'
            }, {
              name: 'insertheading4',
              label: 'H4',
              title: "Heading 4 (Ctrl+Alt+4)",
              classname: 'toolbar_h4',
              block: 'h4'
            }
          ], [
            {
              name: 'blockquote',
              label: "<i style='margin-top:2px;' class='fa fa-comment'></i>",
              title: 'Blockquote (Ctrl+Q)',
              classname: 'toolbar_blockquote',
              block: 'blockquote'
            }, {
              name: 'code',
              label: '{&nbsp;}',
              title: 'Code (Ctrl+Alt+K)',
              classname: 'toolbar_code',
              block: 'pre'
            }, {
              name: 'superscript',
              label: 'x<sup>2</sup>',
              title: 'Superscript',
              classname: 'toolbar_superscript'
            }, {
              name: 'subscript',
              label: 'x<sub>2</sub>',
              title: 'Subscript',
              classname: 'toolbar_subscript'
            }
          ]
        ];
        if (options.toolbar_selector != null) {
          $toolbar = $(options.toolbar_selector);
        } else {
          $(this).before("<div id='editor-toolbar'></div>");
          $toolbar = $('#editor-toolbar');
        }
        $toolbar.addClass('fresheditor-toolbar');
        $toolbar.append("<div class='btn-toolbar'></div>");
        excludes = options.excludes || [];
        for (_i = 0, _len = groups.length; _i < _len; _i++) {
          commands = groups[_i];
          group = '';
          for (_j = 0, _len2 = commands.length; _j < _len2; _j++) {
            command = commands[_j];
            if (jQuery.inArray(command.name, excludes) < 0) {
              button = "<a href='#' class='btn toolbar-btn toolbar-cmd " + command.classname + "' title='" + command.title + "' command='" + command.name + "'";
              if (command.userinput != null) {
                button += " userinput='" + command.userinput + "'";
              }
              if (command.block != null) {
                button += " block='" + command.block + "'";
              }
              if (command.dropdown) {
                button += " data-toggle='dropdown'";
              }
              button += ">" + command.label + "</a>";
              group += button;
            }
          }
          $('.btn-toolbar', $toolbar).append("<div class='btn-group'>" + group + "</div>");
        }
        $("[data-toggle='dropdown']").removeClass('toolbar-cmd');
        if (jQuery.inArray('fontname', excludes) < 0) {
          fontnames = ["Arial", "Arial Black", "Comic Sans MS", "Courier New", "Georgia", "Helvetica", "Sans Serif", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"];
          font_list = '';
          for (_k = 0, _len3 = fontnames.length; _k < _len3; _k++) {
            font = fontnames[_k];
            font_list += "<li><a href='#' class='fontname-option' style='font-family:" + font + ";'>" + font + "</a></li>";
          }
          $('.toolbar_fontname').after("<ul class='dropdown-menu'>" + font_list + "</ul>");
          $('.fontname-option').on('click', function() {
            document.execCommand("fontname", false, $(this).text());
            $(this).closest('.btn-group').removeClass('open');
            return false;
          });
        }
        if (jQuery.inArray('FontSize', excludes) < 0) {
          fontsizes = [
            {
              size: 1,
              point: 8
            }, {
              size: 2,
              point: 10
            }, {
              size: 3,
              point: 12
            }, {
              size: 4,
              point: 14
            }, {
              size: 5,
              point: 18
            }, {
              size: 6,
              point: 24
            }, {
              size: 7,
              point: 36
            }
          ];
          size_list = '';
          for (_l = 0, _len4 = fontsizes.length; _l < _len4; _l++) {
            fontsize = fontsizes[_l];
            size_list += "<li><a href='#' class='font-option fontsize-option' style='font-size:" + fontsize.point + "px;' fontsize='" + fontsize.size + "'>" + fontsize.size + "(" + fontsize.point + "pt)</a></li>";
          }
          $('.toolbar_fontsize').after("<ul class='dropdown-menu'>" + size_list + "</ul>");
          $('a.fontsize-option').on('click', function() {
            console.log($(this).attr('fontsize'));
            document.execCommand("FontSize", false, $(this).attr('fontsize'));
            $(this).closest('.btn-group').removeClass('open');
            return false;
          });
        }

        function getColorChart(id) {
          return '<table id="' + id + '" class="hue-colorchart">' +
              '<tbody><tr><td bgcolor="#FBEFEF"></td><td bgcolor="#FBF2EF"></td><td bgcolor="#FBF5EF"></td><td bgcolor="#FBF8EF"></td><td bgcolor="#FBFBEF"></td><td bgcolor="#F8FBEF"></td><td bgcolor="#F5FBEF"></td><td bgcolor="#F2FBEF"></td><td bgcolor="#EFFBEF"></td><td bgcolor="#EFFBF2"></td><td bgcolor="#EFFBF5"></td><td bgcolor="#EFFBF8"></td><td bgcolor="#EFFBFB"></td><td bgcolor="#EFF8FB"></td><td bgcolor="#EFF5FB"></td><td bgcolor="#EFF2FB"></td><td bgcolor="#EFEFFB"></td><td bgcolor="#F2EFFB"></td><td bgcolor="#F5EFFB"></td><td bgcolor="#F8EFFB"></td><td bgcolor="#FBEFFB"></td><td bgcolor="#FBEFF8"></td><td bgcolor="#FBEFF5"></td><td bgcolor="#FBEFF2"></td><td bgcolor="#FFFFFF"></td></tr>' +
              '<tr><td bgcolor="#F8E0E0"></td><td bgcolor="#F8E6E0"></td><td bgcolor="#F8ECE0"></td><td bgcolor="#F7F2E0"></td><td bgcolor="#F7F8E0"></td><td bgcolor="#F1F8E0"></td><td bgcolor="#ECF8E0"></td><td bgcolor="#E6F8E0"></td><td bgcolor="#E0F8E0"></td><td bgcolor="#E0F8E6"></td><td bgcolor="#E0F8EC"></td><td bgcolor="#E0F8F1"></td><td bgcolor="#E0F8F7"></td><td bgcolor="#E0F2F7"></td><td bgcolor="#E0ECF8"></td><td bgcolor="#E0E6F8"></td><td bgcolor="#E0E0F8"></td><td bgcolor="#E6E0F8"></td><td bgcolor="#ECE0F8"></td><td bgcolor="#F2E0F7"></td><td bgcolor="#F8E0F7"></td><td bgcolor="#F8E0F1"></td><td bgcolor="#F8E0EC"></td><td bgcolor="#F8E0E6"></td><td bgcolor="#FAFAFA"></td></tr>' +
              '<tr><td bgcolor="#F6CECE"></td><td bgcolor="#F6D8CE"></td><td bgcolor="#F6E3CE"></td><td bgcolor="#F5ECCE"></td><td bgcolor="#F5F6CE"></td><td bgcolor="#ECF6CE"></td><td bgcolor="#E3F6CE"></td><td bgcolor="#D8F6CE"></td><td bgcolor="#CEF6CE"></td><td bgcolor="#CEF6D8"></td><td bgcolor="#CEF6E3"></td><td bgcolor="#CEF6EC"></td><td bgcolor="#CEF6F5"></td><td bgcolor="#CEECF5"></td><td bgcolor="#CEE3F6"></td><td bgcolor="#CED8F6"></td><td bgcolor="#CECEF6"></td><td bgcolor="#D8CEF6"></td><td bgcolor="#E3CEF6"></td><td bgcolor="#ECCEF5"></td><td bgcolor="#F6CEF5"></td><td bgcolor="#F6CEEC"></td><td bgcolor="#F6CEE3"></td><td bgcolor="#F6CED8"></td><td bgcolor="#F2F2F2"></td></tr>' +
              '<tr><td bgcolor="#F5A9A9"></td><td bgcolor="#F5BCA9"></td><td bgcolor="#F5D0A9"></td><td bgcolor="#F3E2A9"></td><td bgcolor="#F2F5A9"></td><td bgcolor="#E1F5A9"></td><td bgcolor="#D0F5A9"></td><td bgcolor="#BCF5A9"></td><td bgcolor="#A9F5A9"></td><td bgcolor="#A9F5BC"></td><td bgcolor="#A9F5D0"></td><td bgcolor="#A9F5E1"></td><td bgcolor="#A9F5F2"></td><td bgcolor="#A9E2F3"></td><td bgcolor="#A9D0F5"></td><td bgcolor="#A9BCF5"></td><td bgcolor="#A9A9F5"></td><td bgcolor="#BCA9F5"></td><td bgcolor="#D0A9F5"></td><td bgcolor="#E2A9F3"></td><td bgcolor="#F5A9F2"></td><td bgcolor="#F5A9E1"></td><td bgcolor="#F5A9D0"></td><td bgcolor="#F5A9BC"></td><td bgcolor="#E6E6E6"></td></tr>' +
              '<tr><td bgcolor="#F78181"></td><td bgcolor="#F79F81"></td><td bgcolor="#F7BE81"></td><td bgcolor="#F5DA81"></td><td bgcolor="#F3F781"></td><td bgcolor="#D8F781"></td><td bgcolor="#BEF781"></td><td bgcolor="#9FF781"></td><td bgcolor="#81F781"></td><td bgcolor="#81F79F"></td><td bgcolor="#81F7BE"></td><td bgcolor="#81F7D8"></td><td bgcolor="#81F7F3"></td><td bgcolor="#81DAF5"></td><td bgcolor="#81BEF7"></td><td bgcolor="#819FF7"></td><td bgcolor="#8181F7"></td><td bgcolor="#9F81F7"></td><td bgcolor="#BE81F7"></td><td bgcolor="#DA81F5"></td><td bgcolor="#F781F3"></td><td bgcolor="#F781D8"></td><td bgcolor="#F781BE"></td><td bgcolor="#F7819F"></td><td bgcolor="#D8D8D8"></td></tr>' +
              '<tr><td bgcolor="#FA5858"></td><td bgcolor="#FA8258"></td><td bgcolor="#FAAC58"></td><td bgcolor="#F7D358"></td><td bgcolor="#F4FA58"></td><td bgcolor="#D0FA58"></td><td bgcolor="#ACFA58"></td><td bgcolor="#82FA58"></td><td bgcolor="#58FA58"></td><td bgcolor="#58FA82"></td><td bgcolor="#58FAAC"></td><td bgcolor="#58FAD0"></td><td bgcolor="#58FAF4"></td><td bgcolor="#58D3F7"></td><td bgcolor="#58ACFA"></td><td bgcolor="#5882FA"></td><td bgcolor="#5858FA"></td><td bgcolor="#8258FA"></td><td bgcolor="#AC58FA"></td><td bgcolor="#D358F7"></td><td bgcolor="#FA58F4"></td><td bgcolor="#FA58D0"></td><td bgcolor="#FA58AC"></td><td bgcolor="#FA5882"></td><td bgcolor="#BDBDBD"></td></tr>' +
              '<tr><td bgcolor="#FE2E2E"></td><td bgcolor="#FE642E"></td><td bgcolor="#FE9A2E"></td><td bgcolor="#FACC2E"></td><td bgcolor="#F7FE2E"></td><td bgcolor="#C8FE2E"></td><td bgcolor="#9AFE2E"></td><td bgcolor="#64FE2E"></td><td bgcolor="#2EFE2E"></td><td bgcolor="#2EFE64"></td><td bgcolor="#2EFE9A"></td><td bgcolor="#2EFEC8"></td><td bgcolor="#2EFEF7"></td><td bgcolor="#2ECCFA"></td><td bgcolor="#2E9AFE"></td><td bgcolor="#2E64FE"></td><td bgcolor="#2E2EFE"></td><td bgcolor="#642EFE"></td><td bgcolor="#9A2EFE"></td><td bgcolor="#CC2EFA"></td><td bgcolor="#FE2EF7"></td><td bgcolor="#FE2EC8"></td><td bgcolor="#FE2E9A"></td><td bgcolor="#FE2E64"></td><td bgcolor="#A4A4A4"></td></tr>' +
              '<tr><td bgcolor="#FF0000"></td><td bgcolor="#FF4000"></td><td bgcolor="#FF8000"></td><td bgcolor="#FFBF00"></td><td bgcolor="#FFFF00"></td><td bgcolor="#BFFF00"></td><td bgcolor="#80FF00"></td><td bgcolor="#40FF00"></td><td bgcolor="#00FF00"></td><td bgcolor="#00FF40"></td><td bgcolor="#00FF80"></td><td bgcolor="#00FFBF"></td><td bgcolor="#00FFFF"></td><td bgcolor="#00BFFF"></td><td bgcolor="#0080FF"></td><td bgcolor="#0040FF"></td><td bgcolor="#0000FF"></td><td bgcolor="#4000FF"></td><td bgcolor="#8000FF"></td><td bgcolor="#BF00FF"></td><td bgcolor="#FF00FF"></td><td bgcolor="#FF00BF"></td><td bgcolor="#FF0080"></td><td bgcolor="#FF0040"></td><td bgcolor="#848484"></td></tr>' +
              '<tr><td bgcolor="#DF0101"></td><td bgcolor="#DF3A01"></td><td bgcolor="#DF7401"></td><td bgcolor="#DBA901"></td><td bgcolor="#D7DF01"></td><td bgcolor="#A5DF00"></td><td bgcolor="#74DF00"></td><td bgcolor="#3ADF00"></td><td bgcolor="#01DF01"></td><td bgcolor="#01DF3A"></td><td bgcolor="#01DF74"></td><td bgcolor="#01DFA5"></td><td bgcolor="#01DFD7"></td><td bgcolor="#01A9DB"></td><td bgcolor="#0174DF"></td><td bgcolor="#013ADF"></td><td bgcolor="#0101DF"></td><td bgcolor="#3A01DF"></td><td bgcolor="#7401DF"></td><td bgcolor="#A901DB"></td><td bgcolor="#DF01D7"></td><td bgcolor="#DF01A5"></td><td bgcolor="#DF0174"></td><td bgcolor="#DF013A"></td><td bgcolor="#6E6E6E"></td></tr>' +
              '<tr><td bgcolor="#B40404"></td><td bgcolor="#B43104"></td><td bgcolor="#B45F04"></td><td bgcolor="#B18904"></td><td bgcolor="#AEB404"></td><td bgcolor="#86B404"></td><td bgcolor="#5FB404"></td><td bgcolor="#31B404"></td><td bgcolor="#04B404"></td><td bgcolor="#04B431"></td><td bgcolor="#04B45F"></td><td bgcolor="#04B486"></td><td bgcolor="#04B4AE"></td><td bgcolor="#0489B1"></td><td bgcolor="#045FB4"></td><td bgcolor="#0431B4"></td><td bgcolor="#0404B4"></td><td bgcolor="#3104B4"></td><td bgcolor="#5F04B4"></td><td bgcolor="#8904B1"></td><td bgcolor="#B404AE"></td><td bgcolor="#B40486"></td><td bgcolor="#B4045F"></td><td bgcolor="#B40431"></td><td bgcolor="#585858"></td></tr>' +
              '<tr><td bgcolor="#8A0808"></td><td bgcolor="#8A2908"></td><td bgcolor="#8A4B08"></td><td bgcolor="#886A08"></td><td bgcolor="#868A08"></td><td bgcolor="#688A08"></td><td bgcolor="#4B8A08"></td><td bgcolor="#298A08"></td><td bgcolor="#088A08"></td><td bgcolor="#088A29"></td><td bgcolor="#088A4B"></td><td bgcolor="#088A68"></td><td bgcolor="#088A85"></td><td bgcolor="#086A87"></td><td bgcolor="#084B8A"></td><td bgcolor="#08298A"></td><td bgcolor="#08088A"></td><td bgcolor="#29088A"></td><td bgcolor="#4B088A"></td><td bgcolor="#6A0888"></td><td bgcolor="#8A0886"></td><td bgcolor="#8A0868"></td><td bgcolor="#8A084B"></td><td bgcolor="#8A0829"></td><td bgcolor="#424242"></td></tr>' +
              '<tr><td bgcolor="#610B0B"></td><td bgcolor="#61210B"></td><td bgcolor="#61380B"></td><td bgcolor="#5F4C0B"></td><td bgcolor="#5E610B"></td><td bgcolor="#4B610B"></td><td bgcolor="#38610B"></td><td bgcolor="#21610B"></td><td bgcolor="#0B610B"></td><td bgcolor="#0B6121"></td><td bgcolor="#0B6138"></td><td bgcolor="#0B614B"></td><td bgcolor="#0B615E"></td><td bgcolor="#0B4C5F"></td><td bgcolor="#0B3861"></td><td bgcolor="#0B2161"></td><td bgcolor="#0B0B61"></td><td bgcolor="#210B61"></td><td bgcolor="#380B61"></td><td bgcolor="#4C0B5F"></td><td bgcolor="#610B5E"></td><td bgcolor="#610B4B"></td><td bgcolor="#610B38"></td><td bgcolor="#610B21"></td><td bgcolor="#2E2E2E"></td></tr>' +
              '<tr><td bgcolor="#3B0B0B"></td><td bgcolor="#3B170B"></td><td bgcolor="#3B240B"></td><td bgcolor="#3A2F0B"></td><td bgcolor="#393B0B"></td><td bgcolor="#2E3B0B"></td><td bgcolor="#243B0B"></td><td bgcolor="#173B0B"></td><td bgcolor="#0B3B0B"></td><td bgcolor="#0B3B17"></td><td bgcolor="#0B3B24"></td><td bgcolor="#0B3B2E"></td><td bgcolor="#0B3B39"></td><td bgcolor="#0B2F3A"></td><td bgcolor="#0B243B"></td><td bgcolor="#0B173B"></td><td bgcolor="#0B0B3B"></td><td bgcolor="#170B3B"></td><td bgcolor="#240B3B"></td><td bgcolor="#2F0B3A"></td><td bgcolor="#3B0B39"></td><td bgcolor="#3B0B2E"></td><td bgcolor="#3B0B24"></td><td bgcolor="#3B0B17"></td><td bgcolor="#1C1C1C"></td></tr>' +
              '<tr><td bgcolor="#2A0A0A"></td><td bgcolor="#2A120A"></td><td bgcolor="#2A1B0A"></td><td bgcolor="#29220A"></td><td bgcolor="#292A0A"></td><td bgcolor="#222A0A"></td><td bgcolor="#1B2A0A"></td><td bgcolor="#122A0A"></td><td bgcolor="#0A2A0A"></td><td bgcolor="#0A2A12"></td><td bgcolor="#0A2A1B"></td><td bgcolor="#0A2A22"></td><td bgcolor="#0A2A29"></td><td bgcolor="#0A2229"></td><td bgcolor="#0A1B2A"></td><td bgcolor="#0A122A"></td><td bgcolor="#0A0A2A"></td><td bgcolor="#120A2A"></td><td bgcolor="#1B0A2A"></td><td bgcolor="#220A29"></td><td bgcolor="#2A0A29"></td><td bgcolor="#2A0A22"></td><td bgcolor="#2A0A1B"></td><td bgcolor="#2A0A12"></td><td bgcolor="#151515"></td></tr>' +
              '<tr><td bgcolor="#190707"></td><td bgcolor="#190B07"></td><td bgcolor="#191007"></td><td bgcolor="#181407"></td><td bgcolor="#181907"></td><td bgcolor="#141907"></td><td bgcolor="#101907"></td><td bgcolor="#0B1907"></td><td bgcolor="#071907"></td><td bgcolor="#07190B"></td><td bgcolor="#071910"></td><td bgcolor="#071914"></td><td bgcolor="#071918"></td><td bgcolor="#071418"></td><td bgcolor="#071019"></td><td bgcolor="#070B19"></td><td bgcolor="#070719"></td><td bgcolor="#0B0719"></td><td bgcolor="#100719"></td><td bgcolor="#140718"></td><td bgcolor="#190718"></td><td bgcolor="#190714"></td><td bgcolor="#190710"></td><td bgcolor="#19070B"></td><td bgcolor="#000000"></td></tr>' +
              '</tbody></table>';
        }

        if (jQuery.inArray('forecolor', excludes) < 0) {
          $("a.toolbar_forecolor").after("<ul class='dropdown-menu colorpanel'><input type='text' id='forecolor-input' value='#000000' style='margin-bottom: 0px' /><div id='forecolor-preview' style='height:20px; margin: 4px; cursor: pointer'></div>" + getColorChart("forecolor-chart") + "</ul>");
          $("#forecolor-chart td").on("mouseover", function () {
            $("#forecolor-preview").css("background-color", $(this).attr("bgcolor")).data("color", $(this).attr("bgcolor"));
            $("#forecolor-input").val($(this).attr("bgcolor"));
          });
          $("#forecolor-chart td").on("mousedown", function () {
            var color = $(this).attr("bgcolor");
            document.execCommand("forecolor", false, color);
            $(this).closest(".btn-group").removeClass("open");
            $(".toolbar_forecolor div").css({
              "color": color
            });
          });
          $("#forecolor-input").on("click", function (e) {
            e.stopImmediatePropagation();
            e.preventDefault();
          });
          $("#forecolor-input").on("keyup", function (e) {
            e.stopImmediatePropagation();
            e.preventDefault();
            $("#forecolor-preview").css("background-color", $("#forecolor-input").val()).data("color", $("#forecolor-input").val());
          });
          $("#forecolor-preview").on("mousedown", function () {
            var color = $(this).data("color");
            document.execCommand("forecolor", false, color);
            $(this).closest(".btn-group").removeClass("open");
            $(".toolbar_forecolor div").css({
              "color": color
            });
          });
        }
        if (jQuery.inArray('backcolor', excludes) < 0) {
          $("a.toolbar_bgcolor").after("<ul class='dropdown-menu colorpanel'><input type='text' id='bgcolor-input' value='#000000' style='margin-bottom: 0px' /><div id='bgcolor-preview' style='height:20px; margin: 4px; cursor: pointer'></div>" + getColorChart("bgcolor-chart") + "</ul>");
          $("#bgcolor-chart td").on("mouseover", function () {
            $("#bgcolor-preview").css("background-color", $(this).attr("bgcolor")).data("color", $(this).attr("bgcolor"));
            $("#bgcolor-input").val($(this).attr("bgcolor"));
          });
          $("#bgcolor-chart td").on("mousedown", function () {
            var color = $(this).attr("bgcolor");
            document.execCommand("backcolor", false, color);
            $(this).closest(".btn-group").removeClass("open");
            $(".toolbar_bgcolor div").css({
              "background-color": color
            });
          });
          $("#bgcolor-input").on("click", function (e) {
            e.stopImmediatePropagation();
            e.preventDefault();
          });
          $("#bgcolor-input").on("keyup", function (e) {
            e.stopImmediatePropagation();
            e.preventDefault();
            $("#bgcolor-preview").css("background-color", $("#bgcolor-input").val()).data("color", $("#bgcolor-input").val());
          });
          $("#bgcolor-preview").on("mousedown", function () {
            var color = $(this).data("color");
            document.execCommand("backcolor", false, color);
            $(this).closest(".btn-group").removeClass("open");
            $(".toolbar_bgcolor div").css({
              "background-color": color
            });
          });
        }
        $(this).on('focus', function() {
          var $this;
          $this = $(this);
          $this.data('before', $this.html());
          return $this;
        }).on('blur keyup paste', function() {
              var $this;
              $this = $(this);
              if ($this.data('before') !== $this.html()) {
                $this.data('before', $this.html());
                $this.trigger('change');
              }
              return $this;
            });
        $("a.toolbar-cmd").on('click', function() {
          var ceNode, cmd, dummy, range;
          cmd = $(this).attr('command');
          if ($(this).attr('userinput') === 'yes') {
            methods[cmd].apply(this);
          } else if ($(this).attr('block')) {
            methods['formatblock'].apply(this, ["<" + ($(this).attr('block')) + ">"]);
          } else {
            if ((cmd === 'justifyright') || (cmd === 'justifyleft') || (cmd === 'justifycenter') || (cmd === 'justifyfull')) {
              try {
                document.execCommand(cmd, false, null);
              } catch (e) {
                if (e && e.result === 2147500037) {
                  range = window.getSelection().getRangeAt(0);
                  dummy = document.createElement('br');
                  ceNode = range.startContainer.parentNode;
                  while ((ceNode != null) && ceNode.contentEditable !== 'true') {
                    ceNode = ceNode.parentNode;
                  }
                  if (!ceNode) {
                    throw 'Selected node is not editable!';
                  }
                  ceNode.insertBefore(dummy, ceNode.childNodes[0]);
                  document.execCommand(cmd, false, null);
                  dummy.parentNode.removeChild(dummy);
                } else if (console && console.log) {
                  console.log(e);
                }
              }
            } else {
              if (typeof cmd != "undefined"){
                document.execCommand(cmd, false, null);
              }
            }
          }
          return false;
        });
        shortcuts = [
          {
            keys: 'Ctrl+l',
            method: function() {
              return methods.createlink.apply(this);
            }
          }, {
            keys: 'Ctrl+g',
            method: function() {
              return methods.insertimage.apply(this);
            }
          }, {
            keys: 'Ctrl+Alt+U',
            method: function() {
              return document.execCommand('insertunorderedlist', false, null);
            }
          }, {
            keys: 'Ctrl+Alt+O',
            method: function() {
              return document.execCommand('insertorderedlist', false, null);
            }
          }, {
            keys: 'Ctrl+q',
            method: function() {
              return methods.formatblock.apply(this, ["<blockquote>"]);
            }
          }, {
            keys: 'Ctrl+Alt+k',
            method: function() {
              return methods.formatblock.apply(this, ["<pre>"]);
            }
          }, {
            keys: 'Ctrl+.',
            method: function() {
              return document.execCommand('superscript', false, null);
            }
          }, {
            keys: 'Ctrl+Shift+.',
            method: function() {
              return document.execCommand('subscript', false, null);
            }
          }, {
            keys: 'Ctrl+Alt+0',
            method: function() {
              return methods.formatblock.apply(this, ["p"]);
            }
          }, {
            keys: 'Ctrl+b',
            method: function() {
              return document.execCommand('bold', false, null);
            }
          }, {
            keys: 'Ctrl+i',
            method: function() {
              return document.execCommand('italic', false, null);
            }
          }, {
            keys: 'Ctrl+Alt+1',
            method: function() {
              return methods.formatblock.apply(this, ["H1"]);
            }
          }, {
            keys: 'Ctrl+Alt+2',
            method: function() {
              return methods.formatblock.apply(this, ["H2"]);
            }
          }, {
            keys: 'Ctrl+Alt+3',
            method: function() {
              return methods.formatblock.apply(this, ["H3"]);
            }
          }, {
            keys: 'Ctrl+Alt+4',
            method: function() {
              return methods.formatblock.apply(this, ["H4"]);
            }
          }, {
            keys: 'Ctrl+m',
            method: function() {
              return document.execCommand("removeFormat", false, null);
            }
          }, {
            keys: 'Ctrl+u',
            method: function() {
              return document.execCommand('underline', false, null);
            }
          }, {
            keys: 'tab',
            method: function() {
              return document.execCommand('indent', false, null);
            }
          }, {
            keys: 'Ctrl+tab',
            method: function() {
              return document.execCommand('indent', false, null);
            }
          }, {
            keys: 'Shift+tab',
            method: function() {
              return document.execCommand('outdent', false, null);
            }
          }
        ];
        $.each(shortcuts, function(index, elem) {
          return shortcut.add(elem.keys, function() {
            elem.method();
            return false;
          }, {
            'type': 'keydown',
            'propagate': false
          });
        });
        return this.each(function() {
          var $this, data, tooltip;
          $this = $(this);
          data = $this.data('fresheditor');
          tooltip = $('<div/>', {
            text: $this.attr('title')
          });
          if (!data) {
            return $(this).data('fresheditor', {
              target: $this,
              tooltip: tooltip
            });
          }
        });
      }
    };
    return $.fn.freshereditor = function(method) {
      if (methods[method]) {
        methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
      } else if (typeof method === 'object' || !method) {
        methods.init.apply(this, arguments);
      } else {
        $.error('Method ' + method + ' does not exist on jQuery.contentEditable');
      }
    };
  })(jQuery);
}).call(this);
