/* =============================================================
 * bootstrap-better-typeahead.js v1.0.0 by Philipp Nolte
 * https://github.com/ptnplanet/Bootstrap-Better-Typeahead
 * =============================================================
 * This plugin makes use of twitter bootstrap typeahead
 * http://twitter.github.com/bootstrap/javascript.html#typeahead
 *
 * Bootstrap is licensed under the Apache License, Version 2.0
 * http://www.apache.org/licenses/LICENSE-2.0
 * ============================================================ */
 
 !function(e){"use strict";var t={lookup:function(t){var n;return this.query=this.$element.val()||"",this.query.length<this.options.minLength?this.shown?this.hide():this:(n=e.isFunction(this.source)?this.source(this.query,e.proxy(this.process,this)):this.source,n?this.process(n):this)},process:function(t){var n=this;return t=e.grep(t,function(e){return n.matcher(e)}),t=this.sorter(t),t.length?(this.query.length&&(t=t.slice(0,this.options.items)),this.render(t).show()):this.shown?this.hide():this},render:function(t){var n=this;return t=e(t).map(function(t,r){return t=e(n.options.item).attr("data-value",r),t.find("a").html(n.highlighter(r)),t[0]}),this.query.length>0&&t.first().addClass("active"),this.$menu.html(t),this},keydown:function(t){this.suppressKeyPressRepeat=~e.inArray(t.keyCode,[40,38,9,13,27]);if(t.keyCode===9){if(!this.shown)return;this.select()}else this.move(t)},keyup:function(e){switch(e.keyCode){case 40:case 38:case 16:case 17:case 18:break;case 13:if(!this.shown)return;this.select();break;case 27:if(!this.shown)return;this.hide();break;default:this.lookup()}e.stopPropagation(),e.preventDefault()},focus:function(e){this.focused=!0,this.mousedover||this.lookup(e)}};e.extend(e.fn.typeahead.Constructor.prototype,t)}(window.jQuery);