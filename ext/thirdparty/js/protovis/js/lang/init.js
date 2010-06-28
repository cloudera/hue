/*
 * Parses the Protovis specifications on load, allowing the use of JavaScript
 * 1.8 function expressions on browsers that only support JavaScript 1.6.
 *
 * @see pv.parse
 */
pv.listen(window, "load", function() {
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var s = scripts[i];
      if (s.type == "text/javascript+protovis") {
        try {
          pv.Panel.$dom = s;
          window.eval(pv.parse(s.textContent || s.innerHTML)); // IE
        } catch (e) {
          pv.error(e);
        }
        delete pv.Panel.$dom;
      }
    }
  });
