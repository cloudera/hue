
function initSQLPopups() {
    $('div.popup_sql').hide();
    $('a.sql_link').click(function() {
        $(this).nextAll('div.popup_sql:first').toggle();
        return false;
    });
}

function initFloatyThings() {
    if (!$("#fixed-sidebar.withsidebar")) {
        return;
    }

    var docsBodyOffset = $("#docs-body").offset().top;
    var padding = docsBodyOffset -
            ($("#docs-top-navigation-container").offset().top +
            $("#docs-top-navigation-container").height());

    var automatedBreakpoint = $("#docs-container").position().top +
        $("#docs-top-navigation-container").height();

    // this turns on the whole thing, without this
    // we are in graceful degradation assuming no JS
    $("#fixed-sidebar.withsidebar").addClass("preautomated");

    function setScroll() {
        var scrolltop = $(window).scrollTop();
        var fix = scrolltop >= automatedBreakpoint;

        if (fix) {
            $("#fixed-sidebar.withsidebar").css("top", padding);
            $("#fixed-sidebar.withsidebar").css("position", "fixed");
            $("#fixed-sidebar.withsidebar").css("height", '');
        }
        else {
            $("#fixed-sidebar.withsidebar").css("top", 0);
            $("#fixed-sidebar.withsidebar").css(
                "height", $(window).height() - docsBodyOffset + scrolltop);
            $("#fixed-sidebar.withsidebar").css("position", "absolute");
        }
    }
    $(window).scroll(setScroll);
    $(window).resize(setScroll);
    setScroll();
}

function highlightLinks() {
    function bisection(x){
      var low = 0;
      var high = divCollection.length;

      var mid;

      while (low < high) {
        mid = (low + high) >> 1;

        if (x < divCollection[mid]['active']) {
          high = mid;
        } else {
          low = mid + 1;
        }
      }

      return low;
    }

    var divCollection = [];
    var currentIdx = -1;
    var docHeight = $(document).height();
    $("div.section").each(function(index) {
        var active = $(this).offset().top - 20;
        divCollection.push({
            'id': this.id,
            'active': active,
        });
    });

    function setLink() {
        var windowPos = $(window).scrollTop();
        var windowHeight = $(window).height();

        var idx;
        if (windowPos + windowHeight == docHeight) {
            idx = divCollection.length;
        }
        else {
            idx = bisection(windowPos);
        }

        if (idx != currentIdx) {
            var effectiveIdx = Math.max(0, idx - 1);
            currentIdx = idx;

            var ref;
            if (effectiveIdx == 0) {
                ref = '';
            }
            else {
                ref = divCollection[effectiveIdx]['id'];
            }
            $("#docs-sidebar li.current").removeClass('current');
            $("#docs-sidebar li a.reference[href='#" + ref + "']").parents("li").first().addClass('current');
        }
    }
    $(window).scroll(setLink);

    setLink();
}


$(document).ready(function() {
    initSQLPopups();
    if (!$.browser.mobile) {
        initFloatyThings();
        highlightLinks();
    }
});

