// Scrollbar Width function
function getScrollBarWidth() {
    var inner = document.createElement('p');
    inner.style.width = "100%";
    inner.style.height = "200px";

    var outer = document.createElement('div');
    outer.style.position = "absolute";
    outer.style.top = "0px";
    outer.style.left = "0px";
    outer.style.visibility = "hidden";
    outer.style.width = "200px";
    outer.style.height = "150px";
    outer.style.overflow = "hidden";
    outer.appendChild(inner);

    document.body.appendChild(outer);
    var w1 = inner.offsetWidth;
    outer.style.overflow = 'scroll';
    var w2 = inner.offsetWidth;
    if (w1 == w2) w2 = outer.clientWidth;

    document.body.removeChild(outer);

    return (w1 - w2);
};

var topics = {};
var hOP = topics.hasOwnProperty;

var huePubSub = {
    subscribe: function(topic, listener, app) {
        if (!hOP.call(topics, topic)) {
            topics[topic] = [];
        }

        var index =
          topics[topic].push({
              listener: listener,
              app: app,
              status: 'running'
          }) - 1;

        return {
            remove: function() {
                delete topics[topic][index];
            }
        };
    },
    removeAll: function(topic) {
        topics[topic] = [];
    },
    subscribeOnce: function(topic, listener, app) {
        var ephemeral = this.subscribe(
          topic,
          function() {
              listener.apply(listener, arguments);
              ephemeral.remove();
          },
          app
        );
    },
    publish: function(topic, info) {
        if (!hOP.call(topics, topic)) {
            return;
        }

        topics[topic].forEach(item => {
            if (item.status === 'running') {
                item.listener(info);
            }
        });
    },
    getTopics: function() {
        return topics;
    },
    pauseAppSubscribers: function(app) {
        if (app) {
            Object.keys(topics).forEach(topicName => {
                topics[topicName].forEach(topic => {
                    if (
                      typeof topic.app !== 'undefined' &&
                      topic.app !== null &&
                      (topic.app === app || topic.app.split('-')[0] === app)
                    ) {
                        topic.status = 'paused';
                    }
                });
            });
        }
    },
    resumeAppSubscribers: function(app) {
        if (app) {
            Object.keys(topics).forEach(topicName => {
                topics[topicName].forEach(topic => {
                    if (
                      typeof topic.app !== 'undefined' &&
                      topic.app !== null &&
                      (topic.app === app || topic.app.split('-')[0] === app)
                    ) {
                        topic.status = 'running';
                    }
                });
            });
        }
    },
    clearAppSubscribers: function(app) {
        if (app) {
            Object.keys(topics).forEach(topicName => {
                topics[topicName] = topics[topicName].filter(obj => {
                    return obj.app !== app;
                });
            });
        }
    }
};

(function ($, window, document, undefined) {

    var pluginName = "jHueScrollUp",
      defaults = {
          threshold: 100, // it displays it after 100 px of scroll
          scrollLeft: false
      };

    function Plugin(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options);
        this._defaults = defaults;
        this._name = pluginName;
        if ($(element).attr('jHueScrollified') !== 'true') {
            this.setupScrollUp();
        }
        if (this.options.scrollLeft) {
            $(element).jHueScrollLeft(this.options.threshold);
        }
    }

    Plugin.prototype.setOptions = function (options) {
        this.options = $.extend({}, defaults, options);
    };

    Plugin.prototype.setupScrollUp = function () {
        var _this = this,
          link = null;

        if ($("#jHueScrollUpAnchor").length > 0) { // just one scroll up per page
            link = $("#jHueScrollUpAnchor");
            $(document).off("click", "#jHueScrollUpAnchor");
        } else {
            link = $("<a/>").attr("id", "jHueScrollUpAnchor")
              .hide()
              .addClass("hueAnchor hueAnchorScroller")
              .attr("href", "javascript:void(0)")
              .html("<i class='fa fa-fw fa-chevron-up'></i>")
              .appendTo('#body-inner');
        }

        if ($(window).scrollTop() > _this.options.threshold) {
            link.show();
        }
        $(_this.element).attr("jHueScrollified", "true");

        if ($(_this.element).is("body")) {
            setScrollBehavior($(window), $("body, html"));
        } else {
            setScrollBehavior($(_this.element), $(_this.element));
        }

        huePubSub.subscribe('reposition.scroll.anchor.up', function(){
            $('#jHueScrollUpAnchor').css('right', '20px');
            if (!$(_this.element).is('body') && $(_this.element).is(':visible')) {
                var adjustRight = $(window).width() - ($(_this.element).width() + $(_this.element).offset().left);
                if (adjustRight > 0) {
                    $('#jHueScrollUpAnchor').css('right', adjustRight + 'px');
                }
            }
        });


        function setScrollBehavior(scrolled, scrollable) {
            scrolled.scroll(function () {
                if (scrolled.scrollTop() > _this.options.threshold) {
                    if (link.is(":hidden")) {
                        huePubSub.publish('reposition.scroll.anchor.up');
                        link.fadeIn(200, function(){
                            huePubSub.publish('reposition.scroll.anchor.up');
                        });
                    }
                    if ($(_this.element).data("lastScrollTop") == null || $(_this.element).data("lastScrollTop") < scrolled.scrollTop()) {
                        $("#jHueScrollUpAnchor").data("caller", scrollable);
                    }
                    $(_this.element).data("lastScrollTop", scrolled.scrollTop());
                } else {
                    checkForAllScrolls();
                }
            });
            window.setTimeout(function() {
                huePubSub.publish('reposition.scroll.anchor.up');
            }, 0);
        }

        function checkForAllScrolls() {
            var _allOk = true;
            $(document).find("[jHueScrollified='true']").each(function (cnt, item) {
                if ($(item).is("body")) {
                    if ($(window).scrollTop() > _this.options.threshold) {
                        _allOk = false;
                        $("#jHueScrollUpAnchor").data("caller", $("body, html"));
                    }
                } else if ($(item).scrollTop() > _this.options.threshold) {
                    _allOk = false;
                    $("#jHueScrollUpAnchor").data("caller", $(item));
                }
            });
            if (_allOk) {
                link.fadeOut(200);
                $("#jHueScrollUpAnchor").data("caller", null);
            }
        }

        $(document).on("click", "#jHueScrollUpAnchor", function (event) {
            if ($("#jHueScrollUpAnchor").data("caller") != null) {
                $("html, body").animate({ scrollTop: 0 }, 200);
                if ($(document).find("[jHueScrollified='true']").not($("#jHueScrollUpAnchor").data("caller")).is("body") && $(window).scrollTop() > _this.options.threshold) {
                    $("#jHueScrollUpAnchor").data("caller", $("body, html"));
                } else {
                    checkForAllScrolls();
                }
            }
            return false;
        });
    };

    $.fn[pluginName] = function (options) {
        return this.each(function () {
            $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
        });
    };

    $[pluginName] = function (options) {
        new Plugin($("body"), options);
    };

})(jQuery, window, document);

$('body').jHueScrollUp();

function setMenuHeight() {
    $('#sidebar .highlightable').height($('#sidebar').innerHeight() - $('#header-wrapper').height() - 40);
    $('#sidebar .highlightable').perfectScrollbar('update');
}

function fallbackMessage(action) {
    var actionMsg = '';
    var actionKey = (action === 'cut' ? 'X' : 'C');

    if (/iPhone|iPad/i.test(navigator.userAgent)) {
        actionMsg = 'No support :(';
    }
    else if (/Mac/i.test(navigator.userAgent)) {
        actionMsg = 'Press ⌘-' + actionKey + ' to ' + action;
    }
    else {
        actionMsg = 'Press Ctrl-' + actionKey + ' to ' + action;
    }

    return actionMsg;
}

// for the window resize
$(window).resize(function() {
    setMenuHeight();
});

// debouncing function from John Hann
// http://unscriptable.com/index.php/2009/03/20/debouncing-javascript-methods/
(function($, sr) {

    var debounce = function(func, threshold, execAsap) {
        var timeout;

        return function debounced() {
            var obj = this, args = arguments;

            function delayed() {
                if (!execAsap)
                    func.apply(obj, args);
                timeout = null;
            };

            if (timeout)
                clearTimeout(timeout);
            else if (execAsap)
                func.apply(obj, args);

            timeout = setTimeout(delayed, threshold || 100);
        };
    }
    // smartresize
    jQuery.fn[sr] = function(fn) { return fn ? this.bind('resize', debounce(fn)) : this.trigger(sr); };

})(jQuery, 'smartresize');


jQuery(document).ready(function() {
    jQuery('#sidebar .category-icon').on('click', function() {
        $( this ).toggleClass("fa-angle-down fa-angle-right") ;
        $( this ).parent().parent().children('ul').toggle() ;
        return false;
    });

    var sidebarStatus = searchStatus = 'open';
    $('#sidebar .highlightable').perfectScrollbar();
    setMenuHeight();

    jQuery('#overlay').on('click', function() {
        jQuery(document.body).toggleClass('sidebar-hidden');
        sidebarStatus = (jQuery(document.body).hasClass('sidebar-hidden') ? 'closed' : 'open');

        return false;
    });

    jQuery('[data-sidebar-toggle]').on('click', function() {
        jQuery(document.body).toggleClass('sidebar-hidden');
        sidebarStatus = (jQuery(document.body).hasClass('sidebar-hidden') ? 'closed' : 'open');

        return false;
    });
    jQuery('[data-clear-history-toggle]').on('click', function() {
        sessionStorage.clear();
        location.reload();
        return false;
    });
    jQuery('[data-search-toggle]').on('click', function() {
        if (sidebarStatus == 'closed') {
            jQuery('[data-sidebar-toggle]').trigger('click');
            jQuery(document.body).removeClass('searchbox-hidden');
            searchStatus = 'open';

            return false;
        }

        jQuery(document.body).toggleClass('searchbox-hidden');
        searchStatus = (jQuery(document.body).hasClass('searchbox-hidden') ? 'closed' : 'open');

        return false;
    });

    var ajax;
    jQuery('[data-search-input]').on('input', function() {
        var input = jQuery(this),
            value = input.val(),
            items = jQuery('[data-nav-id]');
        items.removeClass('search-match');
        if (!value.length) {
            $('ul.topics').removeClass('searched');
            items.css('display', 'block');
            sessionStorage.removeItem('search-value');
            $(".highlightable").unhighlight({ element: 'mark' })
            return;
        }

        sessionStorage.setItem('search-value', value);
        $(".highlightable").unhighlight({ element: 'mark' }).highlight(value, { element: 'mark' });

        if (ajax && ajax.abort) ajax.abort();

        jQuery('[data-search-clear]').on('click', function() {
            jQuery('[data-search-input]').val('').trigger('input');
            sessionStorage.removeItem('search-input');
            $(".highlightable").unhighlight({ element: 'mark' })
        });
    });

    $.expr[":"].contains = $.expr.createPseudo(function(arg) {
        return function( elem ) {
            return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
        };
    });

    if (sessionStorage.getItem('search-value')) {
        var searchValue = sessionStorage.getItem('search-value')
        $(document.body).removeClass('searchbox-hidden');
        $('[data-search-input]').val(searchValue);
        $('[data-search-input]').trigger('input');
        var searchedElem = $('#body-inner').find(':contains(' + searchValue + ')').get(0);
        if (searchedElem) {
            searchedElem.scrollIntoView(true);
            var scrolledY = window.scrollY;
            if(scrolledY){
                window.scroll(0, scrolledY - 125);
            }
        }
    }

    // clipboard
    var clipInit = false;
    $('code').each(function() {
        var code = $(this),
            text = code.text();

        if (text.length > 5) {
            if (!clipInit) {
                var text, clip = new Clipboard('.copy-to-clipboard', {
                    text: function(trigger) {
                        text = $(trigger).prev('code').text();
                        return text.replace(/^\$\s/gm, '');
                    }
                });

                var inPre;
                clip.on('success', function(e) {
                    e.clearSelection();
                    inPre = $(e.trigger).parent().prop('tagName') == 'PRE';
                    $(e.trigger).attr('aria-label', 'Copied to clipboard!').addClass('tooltipped tooltipped-' + (inPre ? 'w' : 's'));
                });

                clip.on('error', function(e) {
                    inPre = $(e.trigger).parent().prop('tagName') == 'PRE';
                    $(e.trigger).attr('aria-label', fallbackMessage(e.action)).addClass('tooltipped tooltipped-' + (inPre ? 'w' : 's'));
                    $(document).one('copy', function(){
                        $(e.trigger).attr('aria-label', 'Copied to clipboard!').addClass('tooltipped tooltipped-' + (inPre ? 'w' : 's'));
                    });
                });

                clipInit = true;
            }

            code.after('<span class="copy-to-clipboard" title="Copy to clipboard" />');
            code.next('.copy-to-clipboard').on('mouseleave', function() {
                $(this).attr('aria-label', null).removeClass('tooltipped tooltipped-s tooltipped-w');
            });
        }
    });

    // allow keyboard control for prev/next links
    jQuery(function() {
        jQuery('.nav-prev').click(function(){
            location.href = jQuery(this).attr('href');
        });
        jQuery('.nav-next').click(function() {
            location.href = jQuery(this).attr('href');
        });
    });

    jQuery('input, textarea').keydown(function (e) {
         //  left and right arrow keys
         if (e.which == '37' || e.which == '39') {
             e.stopPropagation();
         }
     });
    
    jQuery(document).keydown(function(e) {
      // prev links - left arrow key
      if(e.which == '37') {
        jQuery('.nav.nav-prev').click();
      }

      // next links - right arrow key
      if(e.which == '39') {
        jQuery('.nav.nav-next').click();
      }
    });

    $('#top-bar a:not(:has(img)):not(.btn)').addClass('highlight');
    $('#body-inner a:not(:has(img)):not(.btn):not(a[rel="footnote"])').addClass('highlight');

    var touchsupport = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (navigator.msMaxTouchPoints > 0)
    if (!touchsupport){ // browser doesn't support touch
        $('#toc-menu').hover(function() {
            $('.progress').stop(true, false, true).fadeToggle(100);
        });

        $('.progress').hover(function() {
            $('.progress').stop(true, false, true).fadeToggle(100);
        });
    }
    if (touchsupport){ // browser does support touch
        $('#toc-menu').click(function() {
            $('.progress').stop(true, false, true).fadeToggle(100);
        });
        $('.progress').click(function() {
            $('.progress').stop(true, false, true).fadeToggle(100);
        });
    }

    /** 
    * Fix anchor scrolling that hides behind top nav bar
    * Courtesy of https://stackoverflow.com/a/13067009/28106
    *
    * We could use pure css for this if only heading anchors were
    * involved, but this works for any anchor, including footnotes
    **/
    (function (document, history, location) {
        var HISTORY_SUPPORT = !!(history && history.pushState);

        var anchorScrolls = {
            ANCHOR_REGEX: /^#[^ ]+$/,
            OFFSET_HEIGHT_PX: 50,

            /**
             * Establish events, and fix initial scroll position if a hash is provided.
             */
            init: function () {
                this.scrollToCurrent();
                $(window).on('hashchange', $.proxy(this, 'scrollToCurrent'));
                $('body').on('click', 'a', $.proxy(this, 'delegateAnchors'));
            },

            /**
             * Return the offset amount to deduct from the normal scroll position.
             * Modify as appropriate to allow for dynamic calculations
             */
            getFixedOffset: function () {
                return this.OFFSET_HEIGHT_PX;
            },

            /**
             * If the provided href is an anchor which resolves to an element on the
             * page, scroll to it.
             * @param  {String} href
             * @return {Boolean} - Was the href an anchor.
             */
            scrollIfAnchor: function (href, pushToHistory) {
                var match, anchorOffset;

                if (!this.ANCHOR_REGEX.test(href)) {
                    return false;
                }

                match = document.getElementById(href.slice(1));

                if (match) {
                    anchorOffset = $(match).offset().top - this.getFixedOffset();
                    $('html, body').animate({ scrollTop: anchorOffset });

                    // Add the state to history as-per normal anchor links
                    if (HISTORY_SUPPORT && pushToHistory) {
                        history.pushState({}, document.title, location.pathname + href);
                    }
                }

                return !!match;
            },

            /**
             * Attempt to scroll to the current location's hash.
             */
            scrollToCurrent: function (e) {
                if (this.scrollIfAnchor(window.location.hash) && e) {
                    e.preventDefault();
                }
            },

            /**
             * If the click event's target was an anchor, fix the scroll position.
             */
            delegateAnchors: function (e) {
                var elem = e.target;

                if (this.scrollIfAnchor(elem.getAttribute('href'), true)) {
                    e.preventDefault();
                }
            }
        };

        $(document).ready($.proxy(anchorScrolls, 'init'));
    })(window.document, window.history, window.location);
    
});

jQuery(window).on('load', function() {

    function adjustForScrollbar() {
        if ((parseInt(jQuery('#body-inner').height()) + 83) >= jQuery('#body').height()) {
            jQuery('.nav.nav-next').css({ 'margin-right': getScrollBarWidth() });
        } else {
            jQuery('.nav.nav-next').css({ 'margin-right': 0 });
        }
    }

    // adjust sidebar for scrollbar
    adjustForScrollbar();

    jQuery(window).smartresize(function() {
        adjustForScrollbar();
    });

    // store this page in session
    sessionStorage.setItem(jQuery('body').data('url'), 1);

    // loop through the sessionStorage and see if something should be marked as visited
    for (var url in sessionStorage) {
        if (sessionStorage.getItem(url) == 1) jQuery('[data-nav-id="' + url + '"]').addClass('visited');
    }


    $(".highlightable").highlight(sessionStorage.getItem('search-value'), { element: 'mark' });
});

$(function() {
    $('a[rel="lightbox"]').featherlight({
        root: 'section#body'
    });
});

jQuery.extend({
    highlight: function(node, re, nodeName, className) {
        if (node.nodeType === 3) {
            var match = node.data.match(re);
            if (match) {
                var highlight = document.createElement(nodeName || 'span');
                highlight.className = className || 'highlight';
                var wordNode = node.splitText(match.index);
                wordNode.splitText(match[0].length);
                var wordClone = wordNode.cloneNode(true);
                highlight.appendChild(wordClone);
                wordNode.parentNode.replaceChild(highlight, wordNode);
                return 1; //skip added node in parent
            }
        } else if ((node.nodeType === 1 && node.childNodes) && // only element nodes that have children
            !/(script|style)/i.test(node.tagName) && // ignore script and style nodes
            !(node.tagName === nodeName.toUpperCase() && node.className === className)) { // skip if already highlighted
            for (var i = 0; i < node.childNodes.length; i++) {
                i += jQuery.highlight(node.childNodes[i], re, nodeName, className);
            }
        }
        return 0;
    }
});

jQuery.fn.unhighlight = function(options) {
    var settings = {
        className: 'highlight',
        element: 'span'
    };
    jQuery.extend(settings, options);

    return this.find(settings.element + "." + settings.className).each(function() {
        var parent = this.parentNode;
        parent.replaceChild(this.firstChild, this);
        parent.normalize();
    }).end();
};

jQuery.fn.highlight = function(words, options) {
    var settings = {
        className: 'highlight',
        element: 'span',
        caseSensitive: false,
        wordsOnly: false
    };
    jQuery.extend(settings, options);

    if (!words) { return; }

    if (words.constructor === String) {
        words = [words];
    }
    words = jQuery.grep(words, function(word, i) {
        return word != '';
    });
    words = jQuery.map(words, function(word, i) {
        return word.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
    });
    if (words.length == 0) { return this; }
    ;

    var flag = settings.caseSensitive ? "" : "i";
    var pattern = "(" + words.join("|") + ")";
    if (settings.wordsOnly) {
        pattern = "\\b" + pattern + "\\b";
    }
    var re = new RegExp(pattern, flag);

    return this.each(function() {
        jQuery.highlight(this, re, settings.element, settings.className);
    });
};

$(window).on('DOMContentLoaded load resize scroll', function () {
  function isElementInViewport (el) {

    var rect     = el.getBoundingClientRect(),
        vWidth   = window.innerWidth || doc.documentElement.clientWidth,
        vHeight  = window.innerHeight || doc.documentElement.clientHeight,
        efp      = function (x, y) { return document.elementFromPoint(x, y) };

    // Return false if it's not in the viewport
    if (rect.right < 0 || rect.bottom < 0
            || rect.left > vWidth || rect.top > vHeight)
        return false;

    // Return true if any of its four corners are visible
    return (
          el.contains(efp(rect.left,  rect.top))
      ||  el.contains(efp(rect.right, rect.top))
      ||  el.contains(efp(rect.right, rect.bottom))
      ||  el.contains(efp(rect.left,  rect.bottom))
    );
  }
  var visible = 0;
  $('#body-inner h1, #body-inner h2, #body-inner h3, #body-inner h4, #body-inner h5, #body-inner h6').each(function (i,e) {
    if(isElementInViewport(e)) {
      visible = $(e).attr('id');
      if (visible) {
        return false;
      }
    }
  });

  if(visible){
    $('.toc ul li a').removeClass('active');
    $('.toc ul li a[href="#'+visible+'"]').addClass('active');
  }
});
