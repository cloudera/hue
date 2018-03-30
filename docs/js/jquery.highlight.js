/**
 * highlight 1.0.0
 * Licensed under MIT
 *
 * Copyright (c) 2016 yjteam
 * http://yjteam.co.kr
 *
 * GitHub Repositories
 * https://github.com/yjseo29/highlight.js
 */

if (typeof jQuery === 'undefined') {
  throw new Error('JavaScript requires jQuery')
}

+function ($) {
  'use strict';
  var version = $.fn.jquery.split(' ')[0].split('.')
  if ((version[0] < 2 && version[1] < 9) || (version[0] == 1 && version[1] == 9 && version[2] < 1)) {
    throw new Error('JavaScript requires jQuery version 1.9.1 or higher')
  }
}(jQuery);

+function ($) {
  $.fn.highlight = function (word, options) {
    var option = $.extend({
      background: "#ffff00",
      color: "#000",
      bold: false,
      class: "",
      ignoreCase: true,
      wholeWord: true
    }, options);
    var findCnt = 0;

    if (this.length == 0) {
      throw new Error('Node was not found')
    }

    var $el = $('<span style="color:' + option.color + ';"></span>');
    if (option.bold) {
      $el.css("font-weight", "bold");
    }
    if (option.background != "") {
      $el.css("background", option.background);
    }
    if (option.class != "") {
      $el.addClass(option.class);
    }

    if (option.wholeWord) {
      word = "\\b" + escapeRegExp(word) + "\\b";
    }
    var re = new RegExp(word, option.ignoreCase == true ? 'gi' : 'g');

    this.each(function () {
      var content = $(this).html();

      $(this).html(content.replace(re, function (t) {
        findCnt++;
        $el.text(t);
        return $el.get(0).outerHTML;
      }));

    });
    return findCnt;

    function escapeRegExp(string) {
      return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
    }
  }
}(jQuery);