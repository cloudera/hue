/*
 * TotalStorage
 *
 * Copyright (c) 2012 Jared Novack & Upstatement (upstatement.com)
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 * Total Storage is the conceptual the love child of jStorage by Andris Reinman,
 * and Cookie by Klaus Hartl -- though this is not connected to either project.
 *
 * @name $.totalStorage
 * @cat Plugins/Cookie
 * @author Jared Novack/jared@upstatement.com
 * @version 1.1.2
 * @url http://upstatement.com/blog/2012/01/jquery-local-storage-done-right-and-easy/
 */

(function(c,h){var d="undefined"===typeof window.localStorage?h:window.localStorage,e;e="undefined"==typeof d||"undefined"==typeof window.JSON?!1:!0;c.totalStorage=function(b,a){return c.totalStorage.impl.init(b,a)};c.totalStorage.setItem=function(b,a){return c.totalStorage.impl.setItem(b,a)};c.totalStorage.getItem=function(b){return c.totalStorage.impl.getItem(b)};c.totalStorage.getAll=function(){return c.totalStorage.impl.getAll()};c.totalStorage.deleteItem=function(b){return c.totalStorage.impl.deleteItem(b)};
c.totalStorage.impl={init:function(b,a){return"undefined"!=typeof a?this.setItem(b,a):this.getItem(b)},setItem:function(b,a){if(!e)try{return c.cookie(b,a),a}catch(g){console.log("Local Storage not supported by this browser. Install the cookie plugin on your site to take advantage of the same functionality. You can get it at https://github.com/carhartl/jquery-cookie")}var f=JSON.stringify(a);d.setItem(b,f);return this.parseResult(f)},getItem:function(b){if(!e)try{return this.parseResult(c.cookie(b))}catch(a){return null}b=
d.getItem(b);return this.parseResult(b)},deleteItem:function(b){if(!e)try{return c.cookie(b,null),!0}catch(a){return!1}d.removeItem(b);return!0},getAll:function(){var b=[];if(e)for(var a in d)a.length&&b.push({key:a,value:this.parseResult(d.getItem(a))});else try{var g=document.cookie.split(";");for(a=0;a<g.length;a++){var f=g[a].split("=")[0];b.push({key:f,value:this.parseResult(c.cookie(f))})}}catch(h){return null}return b},parseResult:function(b){var a;try{a=JSON.parse(b),"undefined"==typeof a&&
(a=b),"true"==a&&(a=!0),"false"==a&&(a=!1),parseFloat(a)==a&&"object"!=typeof a&&(a=parseFloat(a))}catch(c){a=b}return a}}})(jQuery);
