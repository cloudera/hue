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


//// Helper methods
var format = (function(){
  // Date.format follows python datetime formatting.
  // @see http://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
  var WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                  'Thursday', 'Friday', 'Saturday'];
  var MONTH = ['January', 'February', 'March', 'April',
               'May', 'June', 'July', 'August',
               'September', 'October', 'November', 'December'];
  return function(format) {
    var self = this;

    // 'esc' declares whether or not we found an escape character.
    var esc = false;
    var str = '';
    for (var i = 0; i < format.length; ++i) {
      if (esc) {
        // Escape character followed by these characters
        // is a formatting option.
        switch(format[i]) {
          case 'a':
            str += WEEKDAYS[self.getDay()].substring(0,3);
          break;
          case 'A':
            str += WEEKDAYS[self.getDay()];
          break;
          case 'b':
            str += MONTH[self.getMonth()].substring(0,3);
          break;
          case 'B':
            str += MONTH[self.getMonth()];
          break;
          case 'c':
            str += self.toLocaleString();
          break;
          case 'd':
            var tmp = '00' + self.getDate();
            str += tmp.substring(tmp.length - 2, tmp.length);
          break;
          case 'f':
            // TODO: Microsecond as a decimal number [0,999999], zero-padded on the left
          break;
          case 'H':
            var tmp = '00' + self.getHours();
            str += tmp.substring(tmp.length - 2, tmp.length);
          break;
          case 'I':
            var hour = self.getHours() % 12;
            var tmp = '00' + ((hour == 0) ? '12' : hour);
            str += tmp.substring(tmp.length - 2, tmp.length);
          break;
          case 'j':
            // TODO: Day of the year as a decimal number [001,366].
          break;
          case 'm':
            var tmp = '00' + (self.getMonth() + 1);
            str += tmp.substring(tmp.length - 2, tmp.length);
          case 'M':
            var tmp = '00' + self.getMinutes();
            str += tmp.substring(tmp.length - 2, tmp.length);
          break;
          case 'p':
            str += (self.getHours() > 11) ? 'PM' : 'AM';
          break;
          case 'S':
            var tmp = '00' + self.getSeconds();
            str += tmp.substring(tmp.length - 2, tmp.length);
          break;
          case 'U':
            // TODO: Week number of the year [0,53]. Sunday starts.
          break;
          case 'w':
            str += self.getDay();
          break;
          case 'W':
            // TODO: Week number of the year [0,53]. Monday starts.
          break;
          case 'x':
            str += self.toLocaleDateString();
          break;
          case 'X':
            str += self.toLocaleTimeString();
          break;
          case 'y':
            str += self.getFullYear() % 100;
          break;
          case 'Y':
            str += self.getFullYear();
          break;
          case 'z':
            // TODO: UTC offset in the form +HHMM or -HHMM (empty string if the the object is naive)
          break;
          case 'Z':
            // Time zone name (empty string if the object is naive).
          break;
          case '%':
            str += '%'
          break
          default:
            // Bad escape.
            str += '%' + format[i];
          break;
        }
        esc = false;
      } else {
        switch(format[i]) {
          case '%':
            esc = true;
          break;
          default:
            str += format[i];
          break;
        }
      }
    }

    return str;
  };
})();
Date.prototype.format = format;

function showSection(section) {
  $('.section').hide();
  $('#' + section).show();
  $(window).scrollTop(0);
  addFileBrowseButton();
}

function addFileBrowseButton() {
  // Filechooser.
  $(".pathChooserKo").each(function(){
    var self = $(this);
    if (!self.siblings().hasClass('chooserBtn')) {
      self.after(hueUtils.getFileBrowseButton(self, true, true, false, true));
    }
  });

  $(".pathFileChooserKo").each(function(){
    var self = $(this);
    if (!self.siblings().hasClass('chooserBtn')) {
      self.after(hueUtils.getFileBrowseButton(self, false, true, true, false));
    }
  });

  $(".pathFolderChooserKo").each(function(){
    var self = $(this);
    if (!self.siblings().hasClass('chooserBtn')) {
      self.after(hueUtils.getFileBrowseButton(self, true, false, false, true));
    }
  });
}

//// Event handling.
var events = [
  'add.file.workflow',
  'add.property.workflow',
  'add.archive.workflow',
  'add.arg.workflow',
  'add.argument.workflow',
  'add.envvar.workflow',
  'add.param.workflow',
  'add.prepare_delete.workflow',
  'add.prepare_mkdir.workflow',
  'add.delete.workflow',
  'add.mkdir.workflow',
  'add.chmod.workflow',
  'add.move.workflow',
  'add.touchz.workflow',
  'add.parameter.workflow',
  'remove.file.workflow',
  'remove.property.workflow',
  'remove.archive.workflow',
  'remove.arg.workflow',
  'remove.argument.workflow',
  'remove.envvar.workflow',
  'remove.param.workflow',
  'remove.prepare_delete.workflow',
  'remove.prepare_mkdir.workflow',
  'remove.delete.workflow',
  'remove.mkdir.workflow',
  'remove.chmod.workflow',
  'remove.move.workflow',
  'remove.touchz.workflow',
  'remove.parameter.workflow',
  'error.design'
];
$.each(events, function(index, event) {
  $(document).bind(event, addFileBrowseButton);
  $(document).bind(event, function() {
    $(".propKey").typeahead({
      source:(typeof AUTOCOMPLETE_PROPERTIES != 'undefined') ? AUTOCOMPLETE_PROPERTIES : []
    });
  });
});

$(document).bind('error.design', addFileBrowseButton);
