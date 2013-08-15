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

var utils = {
  //take an element with mustache templates as content and re-render
  renderElement:function(element,data) {
    element.html(Mustache.render(element.html(), data));
  },
  renderElements:function(selector,data) {
    if(selector == null || typeof(selector) == "undefined")
      selector = '';
    $(selector).each(function() {
      utils._renderElement(this);
    });
  },
  renderPage:function(page_selector,data) {
    return utils.renderElements('.' + PAGE_TEMPLATE_PREFIX + page_selector,data);
  },
  setTitle:function(title) {
    $('.page-title').text(title);
    return this;
  },
  getTitle:function() {
    return $('.page-title').text();
  }
}


function hashToArray(hash) {
  var keys = Object.keys(hash);
  var output = [];
  for(var i=0;i<keys.length;i++) {
    output.push({'key':keys[i],'value':hash[keys[i]]});
  }
  return output;
}

function stringHashColor(str) {
  var r = 0, g = 0, b = 0, a = 0;
  for(var i=0;i<str.length;i++) {
    var c = str.charCodeAt(i);
    a += c;
    r += Math.floor(Math.abs(Math.sin(c)) * a);
    g += Math.floor(Math.abs(Math.cos(c)) * a);
    b += Math.floor(Math.abs(Math.tan(c)) * a);
  }
    return 'rgb('+(r%190)+','+(g%190)+','+(b%190)+')'; //always keep values under 180, to keep it darker
}

function scrollTo(posY) {
  $('html, body').animate({scrollTop: posY - 120}, 400);
}

function lockClickOrigin(func, origin) {
  return function(target, ev) {
    if(origin != ev.target)
      return function(){};
    return func(target, ev);
  };
}

function confirm(title, text, callback) {
  var modal = $('#confirm-modal');
  ko.cleanNode(modal[0]);
  modal.attr('data-bind','template: {name: "confirm_template"}');
  ko.applyBindings({
    title: title,
    text: text
  }, modal[0]);
  modal.find('.confirm-submit').click(callback);
  modal.modal('show');
}

function launchModal(modal, data) {
  var element = $('#'+modal);
  ko.cleanNode(element[0]);
  element.attr('data-bind','template: {name: "' + modal + '_template"}');
  ko.applyBindings(data, element[0]);
  element.is('.ajaxSubmit') ? element.submit(bindSubmit) : '';
  switch(modal) {
    case 'cell_edit_modal':
      if(data.mime.split('/')[0] == 'text') {
        var target = document.getElementById('codemirror_target');
        var mime = data.mime;
        if(mime == "text/json") {
          mime = {name: "javascript", json: true};
        }
            var cm = CodeMirror.fromTextArea(target, {
              mode: mime,
              tabMode: 'indent',
              lineNumbers: true
            });
            setTimeout(function(){cm.refresh()}, 401); //CM invis bug workaround
            element.find('input[type=submit]').click(function() {
              cm.save();
            });
          }
          app.focusModel(data.content);
      data.content.history.reload();

      var path = '/hbase/api/putUpload/"' + app.cluster() + '"/"' + app.views.tabledata.name() + '"/"' + data.content.parent.row + '"/"' + data.content.name + '"';
      var uploader = new qq.FileUploaderBasic({
        button: document.getElementById("file-upload-btn"),
        action: path,
        fileFieldLabel: 'hbase_file',
        multiple: false,
        onComplete:function (id, fileName, response) {
          data.content.reload();
        }
      });
      break;
  }
  element.modal('show');
logGA(modal.slice(0, modal.indexOf('_modal') != -1 ? modal.indexOf('_modal') : modal.length));
}

function parseXML(xml) {
  var parser, xmlDoc;
  if (window.DOMParser) {
     parser = new DOMParser();
      xmlDoc = parser.parseFromString(xml,"text/xml");
  }
  else {
    xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
    xmlDoc.async = false;
    xmlDoc.loadXML(xml);
    }
    return new XMLSerializer().serializeToString(xmlDoc);
}

function detectMimeType(data) {
  var MIME_TESTS = {
    'text/plain':function(data){return !data;},
    'type/int':function(data){return !isNaN(parseInt(data));},
    'text/json':function(data) {
      try {
        return JSON.parse(data);
      }
      catch(err){}
    },
    'text/xml':function(data) {
      return parseXML(data).indexOf('parsererror') == -1;
    }
  }
  var keys = Object.keys(MIME_TESTS);
  for(var i=0;i<keys.length;i++) {
    if(MIME_TESTS[keys[i]](data))
      return keys[i];
  }
  //images
  var types = ['image/png','image/gif','image/jpg','application/pdf']
  var b64 = ['iVBORw','R0lG','/9j/','JVBERi']
  try {
    var decoded = atob(data).toLowerCase().trim();
    for(var i=0;i<types.length;i++) {
      var location = decoded.indexOf(types[i].split('/')[1]);
      if(location >= 0 && location<10) //stupid guess
        return types[i];
    }
  }
  catch(error) {
  }
  for(var i=0;i<types.length;i++) {
    if(data.indexOf(b64[i]) >= 0 && data.indexOf(b64[i]) <= 10)
      return types[i];
  }
  return 'type/null';
}

function convertTimestamp(timestamp) {
  var date = new Date(parseInt(timestamp));
  return date.toLocaleString();
}

function formatTimestamp(timestamp) {
  var date = new Date(parseInt(timestamp));
  return date.toUTCString();
}

function resetElements() {
  $(window).unbind('scroll');
  $(window).scroll(function(e) {
    $(".subnav.sticky").each(function() {
      var padder = $(this).data('padder'), top = $(this).position().top + (padder ? window.scrollY : 0);
      if(padder && top <= padder.position().top) {
        $(this).removeClass('subnav-fixed').data('padder').remove();
        $(this).removeData('padder');
      }
      else if(!padder && top <= window.scrollY + $('.navbar').outerHeight()) {
        $(this).addClass('subnav-fixed').data('padder',$('<div></div>').insertBefore($(this)).css('height',$(this).outerHeight()));
      }
    });
  });
  resetSearch();
};

function resetSearch() {
  app.views.tabledata.searchQuery('');
  app.search.cur_input('');
};

function prepForTransport(value) {
  value = value.replace(/\"/g,'\\\"').replace(/\//g,'\\/');
  if(isNaN(parseInt(value)) && value.trim() != '')
    value = '"' + value + '"';
  return encodeURIComponent(value);
};

function logGA(postfix) {
  function doLog() {
    trackOnGA('hbase/' + postfix);
  }
  if(postfix == null)
    postfix = "";
  if (typeof trackOnGA == 'function') {
    doLog();
  } else {
    setTimeout(doLog, 10);
  }
};

function table_search(value) {
  routie(app.cluster() + '/' + app.views.tabledata.name() +'/query/' + value);
};

function getEditablePosition(contentEditable, trimWhitespaceNodes) {
  var el = contentEditable;
  if(window.getSelection().getRangeAt(0).startContainer == el) //raw reference for FF fix
    return 0;
  var index = window.getSelection().getRangeAt(0).startOffset; //ff
  var cur_node = window.getSelection().getRangeAt(0).startContainer; //ff
  while(cur_node != null && cur_node != el) {
    var cur_sib = cur_node.previousSibling || cur_node.previousElementSibling;
    while(cur_sib != null) {
      var val = $(cur_sib).text() || cur_sib.nodeValue;
      if(typeof val !== "undefined" && val != null) {
        index += trimWhitespaceNodes ? val.length : val.length;
      }
      cur_sib = cur_sib.previousSibling;
    }
    cur_node = cur_node.parentNode;
  }
  return index;
};

function setCursor(node, pos, trimWhitespaceNodes){
  var sel = window.getSelection();
  var range = document.createRange();
  node = function selectNode(node) {
    var nodes = node.childNodes;
    if(pos > 0) {
      for(var i=0; i<nodes.length; i++) {
        var val = trimWhitespaceNodes ? nodes[i].nodeValue.trim() : nodes[i].nodeValue;
        if(val) {
          if(val.length >= pos) {
            return nodes[i];
          } else {
            pos -= val.length;
          }
        }
        var n = selectNode(nodes[i]);
        if (n) return n;
      }
    }
    return false;
  }(node);
  try {
    range.setStart(node, pos);
    range.setEnd(node, pos);
    range.collapse(true);
    sel.removeAllRanges();
    sel.addRange(range);
    return range;
  } catch (err) { }
}

function pullFromRenderer(str, renderer) {
  try {
    return str.match(renderer.select)[0].match(renderer.tag)[0];
  } catch (e){
    return "";
  }
}

window.selectIndex = null;
var fallback = typeof window.getSelection === "undefined";
ko.bindingHandlers.editableText = {
  init: function(element, valueAccessor, allBindingsAccessor) {
    $(element).on('keydown', function() {
      setTimeout(function() {
        var modelValue = valueAccessor();
        var elementValue = $(element).text();
        if (ko.isWriteableObservable(modelValue) && elementValue != modelValue()) {
          if(!fallback)
            window.selectIndex = getEditablePosition(element); //firefox does some tricky predictive stuff here
          modelValue(elementValue);
        }
        else { //handle non-observable one-way binding
            var allBindings = allBindingsAccessor();
            if (allBindings['_ko_property_writers'] && allBindings['_ko_property_writers'].htmlValue) allBindings['_ko_property_writers'].htmlValue(elementValue);
        }}, 1);
      });
  },
  update: function(element, valueAccessor) {
    var value = ko.utils.unwrapObservable(valueAccessor()) || "";
    if(value.trim() == "" && !app.search.focused()) {
      app.search.doBlur();
    } else {
      if(!fallback) {
        element.innerHTML = app.search.render(value, searchRenderers);
        if(window.selectIndex != null) {
          setCursor(element, window.selectIndex);
        }
      }
    }
  }
};