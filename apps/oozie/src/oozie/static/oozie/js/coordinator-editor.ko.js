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

var CoordinatorEditorViewModel = (function () {
  var COORDINATOR_MAPPING = {
    ignore: [
      "availableTimezones", "availableSettings", "filteredModalWorkflows"
    ]
  };

  var Coordinator = function (vm, coordinator) {

    var self = this;

    self.id = ko.observable(typeof coordinator.id != "undefined" && coordinator.id != null ? coordinator.id : null);
    self.uuid = ko.observable(typeof coordinator.uuid != "undefined" && coordinator.uuid != null ? coordinator.uuid : hueUtils.UUID());
    self.name = ko.observable(typeof coordinator.name != "undefined" && coordinator.name != null ? coordinator.name : "").extend({ trackChange: true });
    self.isManaged = ko.observable(typeof coordinator.isManaged != "undefined" && coordinator.isManaged != null ? coordinator.isManaged : false);

    self.properties = ko.mapping.fromJS(typeof coordinator.properties != "undefined" && coordinator.properties != null ? coordinator.properties : {});
    self.variables = ko.mapping.fromJS(typeof coordinator.variables != "undefined" && coordinator.variables != null ? coordinator.variables : []);

    self.variablesUI = ko.observableArray(['parameter', 'input_path', 'output_path']);
    self.showAdvancedFrequencyUI = ko.observable(typeof coordinator.showAdvancedFrequencyUI != "undefined" && coordinator.showAdvancedFrequencyUI != null ? coordinator.showAdvancedFrequencyUI : false);
    self.workflowParameters = ko.mapping.fromJS(typeof coordinator.workflowParameters != "undefined" && coordinator.workflowParameters != null ? coordinator.workflowParameters : []);

    self.tracker = new ChangeTracker(self, ko);

    self.isDirty = ko.computed(function () {
      return self.tracker().somethingHasChanged();
    });

    self._get_parameter = function (name) {
      var _param = $.grep(self.properties.parameters(), function (param) {
        return param.name() == name;
      });

      if (_param) {
        return _param[0];
      } else {
        return null;
      }
    }

    self.start_date = self._get_parameter('start_date');
    self.end_date = self._get_parameter('end_date');

    self.properties.startDateUI = ko.observable(typeof self.start_date.value() != "undefined" && self.start_date.value().indexOf("T") > -1 ? self.start_date.value().split("T")[0] : "");
    self.properties.startTimeUI = ko.observable(typeof self.start_date.value() != "undefined" && self.start_date.value().indexOf("T") > -1 ? self.start_date.value().split("T")[1] : "");
    self.properties.endDateUI = ko.observable(typeof self.end_date.value() != "undefined" && self.end_date.value().indexOf("T") > -1 ? self.end_date.value().split("T")[0] : "");
    self.properties.endTimeUI = ko.observable(typeof self.end_date.value() != "undefined" && self.end_date.value().indexOf("T") > -1 ? self.end_date.value().split("T")[1] : "");

    self.properties.startDateUI.subscribe(function (newVal) {
      self.setStartDate();
    });
    self.properties.startTimeUI.subscribe(function (newVal) {
      self.setStartDate();
    });
    self.properties.endDateUI.subscribe(function (newVal) {
      self.setEndDate();
    });
    self.properties.endTimeUI.subscribe(function (newVal) {
      self.setEndDate();
    });

    self.setStartDate = function () {
      self.start_date.value(self.properties.startDateUI() + "T" + self.properties.startTimeUI());
    }
    self.setEndDate = function () {
      self.end_date.value(self.properties.endDateUI() + "T" + self.properties.endTimeUI());
    }

    self.refreshParameters = function() {
      if (!self.properties.workflow()) { return; }

      $.get("/oozie/editor/workflow/parameters/", {
        "uuid": self.properties.workflow(),
        "document": self.properties.document(),
      }, function (data) {
        if (data.status < 0) { return; }

        self.workflowParameters(data.parameters);

        // Remove Uncommon params
        var prev_variables = self.variables.slice();
        var removed_variables = [];
        $.each(prev_variables, function (index, variable) {
          if (data.parameters.filter(function(param) { return param['name'] == variable.workflow_variable(); }).length == 0) {
            self.variables.remove(variable);
            removed_variables.push(variable);
          }
        });

        // Append the new variables, reuse past variables in case of rename
        prev_variables = self.variables.slice();
        if (data.parameters) {
          $.each(data.parameters, function (index, param) {
            if (prev_variables.filter(function (variable) {
                return param['name'] == variable.workflow_variable();
              }).length == 0) {
              var newVar;
              if (removed_variables.length > 0) {
                newVar = removed_variables.shift();
                self.variables.push(newVar);
              } else {
                newVar = self.addVariable();
              }
              newVar.workflow_variable(param['name']);
            }
          });
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }

    self.properties.workflow.subscribe(function (newVal) {
      if (newVal) {
        self.refreshParameters();
      }
    });

    self.properties.cron_advanced.subscribe(function (value) {
      if (value || !vm.isEditing()) {
        coordCron.disable();
      } else {
        coordCron.enable();
      }
    });

    self.addVariable = function () {
      var _var = {
        'workflow_variable': '', // Variable we want to fill in the workflow

        'dataset_type': 'parameter',

        'uuid': hueUtils.UUID(), // Dataset
        'dataset_variable': '', // Aka property or URI
        'show_advanced': false,
        'use_done_flag': false,
        'done_flag': '_SUCCESS',
        'timezone': tzdetect.matches()[0],
        'same_timezone': true,
        'instance_choice': 'default',
        'is_advanced_start_instance': false,
        'start_instance': '0',
        'advanced_start_instance': '${coord:current(0)}',
        'is_advanced_end_instance': false,
        'advanced_end_instance': '${coord:current(0)}',
        'end_instance': '0',
        'same_frequency': true,
        'frequency_number': 1,
        'frequency_unit': 'days',
        'start': moment().format("YYYY-MM-DD[T]HH:mm"),
        'same_start': true,

        'shared_dataset_uuid': '' // If reusing a shared dataset
      };
      var _koVar = ko.mapping.fromJS(_var);
      for (key in _koVar) {
        if (_koVar.hasOwnProperty(key) && ko.isObservable(_koVar[key])) {
          _koVar[key].extend({ trackChange: true });
        }
      }
      self.variables.push(_koVar);
      return _koVar;
    };
  }

  var CoordinatorEditorViewModel = function (coordinator_json, credentials_json, workflows_json, can_edit_json) {
    var self = this;

    if (! coordinator_json['properties']['timezone']) {
      coordinator_json['properties']['timezone'] = tzdetect.matches()[0];
    }
    self.canEdit = ko.mapping.fromJS(can_edit_json);
    self.isEditing = ko.observable(coordinator_json.id == null);
    self.isEditing.subscribe(function (newVal) {
      $(document).trigger("editingToggled");
      self.coordinator.properties.cron_advanced.valueHasMutated();
    });
    self.toggleEditing = function () {
      self.isEditing(!self.isEditing());
    };
    self.isSaving = ko.observable(false);

    self.workflows = ko.mapping.fromJS(workflows_json);
    self.coordinator = new Coordinator(self, coordinator_json);
    self.credentials = ko.mapping.fromJS(credentials_json);

    self.availableTimezones = ko.observableArray(["Africa/Abidjan", "Africa/Accra", "Africa/Addis_Ababa", "Africa/Algiers", "Africa/Asmara", "Africa/Asmera", "Africa/Bamako", "Africa/Bangui", "Africa/Banjul", "Africa/Bissau", "Africa/Blantyre", "Africa/Brazzaville", "Africa/Bujumbura", "Africa/Cairo", "Africa/Casablanca", "Africa/Ceuta", "Africa/Conakry", "Africa/Dakar", "Africa/Dar_es_Salaam", "Africa/Djibouti", "Africa/Douala", "Africa/El_Aaiun", "Africa/Freetown", "Africa/Gaborone", "Africa/Harare", "Africa/Johannesburg", "Africa/Juba", "Africa/Kampala", "Africa/Khartoum", "Africa/Kigali", "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Lome", "Africa/Luanda", "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Malabo", "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Mogadishu", "Africa/Monrovia", "Africa/Nairobi", "Africa/Ndjamena", "Africa/Niamey", "Africa/Nouakchott", "Africa/Ouagadougou", "Africa/Porto-Novo", "Africa/Sao_Tome", "Africa/Timbuktu", "Africa/Tripoli", "Africa/Tunis", "Africa/Windhoek", "America/Adak", "America/Anchorage", "America/Anguilla", "America/Antigua", "America/Araguaina", "America/Argentina/Buenos_Aires", "America/Argentina/Catamarca", "America/Argentina/ComodRivadavia", "America/Argentina/Cordoba", "America/Argentina/Jujuy", "America/Argentina/La_Rioja", "America/Argentina/Mendoza", "America/Argentina/Rio_Gallegos", "America/Argentina/Salta", "America/Argentina/San_Juan", "America/Argentina/San_Luis", "America/Argentina/Tucuman", "America/Argentina/Ushuaia", "America/Aruba", "America/Asuncion", "America/Atikokan", "America/Atka", "America/Bahia", "America/Bahia_Banderas", "America/Barbados", "America/Belem", "America/Belize", "America/Blanc-Sablon", "America/Boa_Vista", "America/Bogota", "America/Boise", "America/Buenos_Aires", "America/Cambridge_Bay", "America/Campo_Grande", "America/Cancun", "America/Caracas", "America/Catamarca", "America/Cayenne", "America/Cayman", "America/Chicago", "America/Chihuahua", "America/Coral_Harbour", "America/Cordoba", "America/Costa_Rica", "America/Creston", "America/Cuiaba", "America/Curacao", "America/Danmarkshavn", "America/Dawson", "America/Dawson_Creek", "America/Denver", "America/Detroit", "America/Dominica", "America/Edmonton", "America/Eirunepe", "America/El_Salvador", "America/Ensenada", "America/Fort_Wayne", "America/Fortaleza", "America/Glace_Bay", "America/Godthab", "America/Goose_Bay", "America/Grand_Turk", "America/Grenada", "America/Guadeloupe", "America/Guatemala", "America/Guayaquil", "America/Guyana", "America/Halifax", "America/Havana", "America/Hermosillo", "America/Indiana/Indianapolis", "America/Indiana/Knox", "America/Indiana/Marengo", "America/Indiana/Petersburg", "America/Indiana/Tell_City", "America/Indiana/Vevay", "America/Indiana/Vincennes", "America/Indiana/Winamac", "America/Indianapolis", "America/Inuvik", "America/Iqaluit", "America/Jamaica", "America/Jujuy", "America/Juneau", "America/Kentucky/Louisville", "America/Kentucky/Monticello", "America/Knox_IN", "America/Kralendijk", "America/La_Paz", "America/Lima", "America/Los_Angeles", "America/Louisville", "America/Lower_Princes", "America/Maceio", "America/Managua", "America/Manaus", "America/Marigot", "America/Martinique", "America/Matamoros", "America/Mazatlan", "America/Mendoza", "America/Menominee", "America/Merida", "America/Metlakatla", "America/Mexico_City", "America/Miquelon", "America/Moncton", "America/Monterrey", "America/Montevideo", "America/Montreal", "America/Montserrat", "America/Nassau", "America/New_York", "America/Nipigon", "America/Nome", "America/Noronha", "America/North_Dakota/Beulah", "America/North_Dakota/Center", "America/North_Dakota/New_Salem", "America/Ojinaga", "America/Panama", "America/Pangnirtung", "America/Paramaribo", "America/Phoenix", "America/Port-au-Prince", "America/Port_of_Spain", "America/Porto_Acre", "America/Porto_Velho", "America/Puerto_Rico", "America/Rainy_River", "America/Rankin_Inlet", "America/Recife", "America/Regina", "America/Resolute", "America/Rio_Branco", "America/Rosario", "America/Santa_Isabel", "America/Santarem", "America/Santiago", "America/Santo_Domingo", "America/Sao_Paulo", "America/Scoresbysund", "America/Shiprock", "America/Sitka", "America/St_Barthelemy", "America/St_Johns", "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent", "America/Swift_Current", "America/Tegucigalpa", "America/Thule", "America/Thunder_Bay", "America/Tijuana", "America/Toronto", "America/Tortola", "America/Vancouver", "America/Virgin", "America/Whitehorse", "America/Winnipeg", "America/Yakutat", "America/Yellowknife", "Antarctica/Casey", "Antarctica/Davis", "Antarctica/DumontDUrville", "Antarctica/Macquarie", "Antarctica/Mawson", "Antarctica/McMurdo", "Antarctica/Palmer", "Antarctica/Rothera", "Antarctica/South_Pole", "Antarctica/Syowa", "Antarctica/Vostok", "Arctic/Longyearbyen", "Asia/Aden", "Asia/Almaty", "Asia/Amman", "Asia/Anadyr", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat", "Asia/Ashkhabad", "Asia/Baghdad", "Asia/Bahrain", "Asia/Baku", "Asia/Bangkok", "Asia/Beijing", "Asia/Beirut", "Asia/Bishkek", "Asia/Brunei", "Asia/Calcutta", "Asia/Choibalsan", "Asia/Chongqing", "Asia/Chungking", "Asia/Colombo", "Asia/Dacca", "Asia/Damascus", "Asia/Dhaka", "Asia/Dili", "Asia/Dubai", "Asia/Dushanbe", "Asia/Gaza", "Asia/Harbin", "Asia/Hebron", "Asia/Ho_Chi_Minh", "Asia/Hong_Kong", "Asia/Hovd", "Asia/Irkutsk", "Asia/Istanbul", "Asia/Jakarta", "Asia/Jayapura", "Asia/Jerusalem", "Asia/Kabul", "Asia/Kamchatka", "Asia/Karachi", "Asia/Kashgar", "Asia/Kathmandu", "Asia/Katmandu", "Asia/Kolkata", "Asia/Krasnoyarsk", "Asia/Kuala_Lumpur", "Asia/Kuching", "Asia/Kuwait", "Asia/Macao", "Asia/Macau", "Asia/Magadan", "Asia/Makassar", "Asia/Manila", "Asia/Muscat", "Asia/Nicosia", "Asia/Novokuznetsk", "Asia/Novosibirsk", "Asia/Omsk", "Asia/Oral", "Asia/Phnom_Penh", "Asia/Pontianak", "Asia/Pyongyang", "Asia/Qatar", "Asia/Qyzylorda", "Asia/Rangoon", "Asia/Riyadh", "Asia/Riyadh87", "Asia/Riyadh88", "Asia/Riyadh89", "Asia/Saigon", "Asia/Sakhalin", "Asia/Samarkand", "Asia/Seoul", "Asia/Shanghai", "Asia/Singapore", "Asia/Taipei", "Asia/Tashkent", "Asia/Tbilisi", "Asia/Tehran", "Asia/Tel_Aviv", "Asia/Thimbu", "Asia/Thimphu", "Asia/Tokyo", "Asia/Ujung_Pandang", "Asia/Ulaanbaatar", "Asia/Ulan_Bator", "Asia/Urumqi", "Asia/Vientiane", "Asia/Vladivostok", "Asia/Yakutsk", "Asia/Yekaterinburg", "Asia/Yerevan", "Atlantic/Azores", "Atlantic/Bermuda", "Atlantic/Canary", "Atlantic/Cape_Verde", "Atlantic/Faeroe", "Atlantic/Faroe", "Atlantic/Jan_Mayen", "Atlantic/Madeira", "Atlantic/Reykjavik", "Atlantic/South_Georgia", "Atlantic/St_Helena", "Atlantic/Stanley", "Australia/ACT", "Australia/Adelaide", "Australia/Brisbane", "Australia/Broken_Hill", "Australia/Canberra", "Australia/Currie", "Australia/Darwin", "Australia/Eucla", "Australia/Hobart", "Australia/LHI", "Australia/Lindeman", "Australia/Lord_Howe", "Australia/Melbourne", "Australia/NSW", "Australia/North", "Australia/Perth", "Australia/Queensland", "Australia/South", "Australia/Sydney", "Australia/Tasmania", "Australia/Victoria", "Australia/West", "Australia/Yancowinna", "Brazil/Acre", "Brazil/DeNoronha", "Brazil/East", "Brazil/West", "CET", "CST6CDT", "Canada/Atlantic", "Canada/Central", "Canada/East-Saskatchewan", "Canada/Eastern", "Canada/Mountain", "Canada/Newfoundland", "Canada/Pacific", "Canada/Saskatchewan", "Canada/Yukon", "Chile/Continental", "Chile/EasterIsland", "Cuba", "EET", "EST", "EST5EDT", "Egypt", "Eire", "Etc/GMT", "Etc/GMT+0", "Etc/GMT+1", "Etc/GMT+10", "Etc/GMT+11", "Etc/GMT+12", "Etc/GMT+2", "Etc/GMT+3", "Etc/GMT+4", "Etc/GMT+5", "Etc/GMT+6", "Etc/GMT+7", "Etc/GMT+8", "Etc/GMT+9", "Etc/GMT-0", "Etc/GMT-1", "Etc/GMT-10", "Etc/GMT-11", "Etc/GMT-12", "Etc/GMT-13", "Etc/GMT-14", "Etc/GMT-2", "Etc/GMT-3", "Etc/GMT-4", "Etc/GMT-5", "Etc/GMT-6", "Etc/GMT-7", "Etc/GMT-8", "Etc/GMT-9", "Etc/GMT0", "Etc/Greenwich", "Etc/UCT", "Etc/UTC", "Etc/Universal", "Etc/Zulu", "Europe/Amsterdam", "Europe/Andorra", "Europe/Athens", "Europe/Belfast", "Europe/Belgrade", "Europe/Berlin", "Europe/Bratislava", "Europe/Brussels", "Europe/Bucharest", "Europe/Budapest", "Europe/Chisinau", "Europe/Copenhagen", "Europe/Dublin", "Europe/Gibraltar", "Europe/Guernsey", "Europe/Helsinki", "Europe/Isle_of_Man", "Europe/Istanbul", "Europe/Jersey", "Europe/Kaliningrad", "Europe/Kiev", "Europe/Lisbon", "Europe/Ljubljana", "Europe/London", "Europe/Luxembourg", "Europe/Madrid", "Europe/Malta", "Europe/Mariehamn", "Europe/Minsk", "Europe/Monaco", "Europe/Moscow", "Europe/Nicosia", "Europe/Oslo", "Europe/Paris", "Europe/Podgorica", "Europe/Prague", "Europe/Riga", "Europe/Rome", "Europe/Samara", "Europe/San_Marino", "Europe/Sarajevo", "Europe/Simferopol", "Europe/Skopje", "Europe/Sofia", "Europe/Stockholm", "Europe/Tallinn", "Europe/Tirane", "Europe/Tiraspol", "Europe/Uzhgorod", "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna", "Europe/Vilnius", "Europe/Volgograd", "Europe/Warsaw", "Europe/Zagreb", "Europe/Zaporozhye", "Europe/Zurich", "Factory", "GB", "GB-Eire", "GMT", "GMT+0", "GMT+1", "GMT+10", "GMT+11", "GMT+12", "GMT+13", "GMT+14", "GMT+2", "GMT+3", "GMT+4", "GMT+5", "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT-0", "GMT-1", "GMT-10", "GMT-11", "GMT-12", "GMT-2", "GMT-3", "GMT-4", "GMT-5", "GMT-6", "GMT-7", "GMT-8", "GMT-9", "GMT0", "Greenwich", "HST", "Hongkong", "Iceland", "Indian/Antananarivo", "Indian/Chagos", "Indian/Christmas", "Indian/Cocos", "Indian/Comoro", "Indian/Kerguelen", "Indian/Mahe", "Indian/Maldives", "Indian/Mauritius", "Indian/Mayotte", "Indian/Reunion", "Iran", "Israel", "Jamaica", "Japan", "Kwajalein", "Libya", "MET", "MST", "MST7MDT", "Mexico/BajaNorte", "Mexico/BajaSur", "Mexico/General", "Mideast/Riyadh87", "Mideast/Riyadh88", "Mideast/Riyadh89", "NZ", "NZ-CHAT", "Navajo", "PRC", "PST8PDT", "Pacific/Apia", "Pacific/Auckland", "Pacific/Chatham", "Pacific/Chuuk", "Pacific/Easter", "Pacific/Efate", "Pacific/Enderbury", "Pacific/Fakaofo", "Pacific/Fiji", "Pacific/Funafuti", "Pacific/Galapagos", "Pacific/Gambier", "Pacific/Guadalcanal", "Pacific/Guam", "Pacific/Honolulu", "Pacific/Johnston", "Pacific/Kiritimati", "Pacific/Kosrae", "Pacific/Kwajalein", "Pacific/Majuro", "Pacific/Marquesas", "Pacific/Midway", "Pacific/Nauru", "Pacific/Niue", "Pacific/Norfolk", "Pacific/Noumea", "Pacific/Pago_Pago", "Pacific/Palau", "Pacific/Pitcairn", "Pacific/Pohnpei", "Pacific/Ponape", "Pacific/Port_Moresby", "Pacific/Rarotonga", "Pacific/Saipan", "Pacific/Samoa", "Pacific/Tahiti", "Pacific/Tarawa", "Pacific/Tongatapu", "Pacific/Truk", "Pacific/Wake", "Pacific/Wallis", "Pacific/Yap", "Poland", "Portugal", "ROC", "ROK", "Singapore", "Turkey", "UCT", "US/Alaska", "US/Aleutian", "US/Arizona", "US/Central", "US/East-Indiana", "US/Eastern", "US/Hawaii", "US/Indiana-Starke", "US/Michigan", "US/Mountain", "US/Pacific", "US/Pacific-New", "US/Samoa", "Universal", "W-SU", "WET", "Zulu"]);
    self.availableSettings = ko.observableArray([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]);

    if (coordinator_json.id == null && self.coordinator.properties.workflow()) {
      self.coordinator.refreshParameters();
    }

    self.workflowModalFilter = ko.observable("");
    self.filteredModalWorkflows = ko.computed(function () {
      var _filter = self.workflowModalFilter().toLowerCase();
      if (!_filter) {
        return self.workflows();
      }
      else {
        return ko.utils.arrayFilter(self.workflows(), function (wf) {
          return wf.name().toLowerCase().indexOf(_filter.toLowerCase()) > -1;
        });
      }
    }, self);

    self.getWorkflowById = function (uuid) {
      var _wfs = ko.utils.arrayFilter(self.workflows(), function (wf) {
        return wf.uuid() == uuid;
      });
      if (_wfs.length > 0) {
        return _wfs[0];
      }
      return null;
    }

    self.save = function (cb) {
      if (!self.isSaving()) {
        self.isSaving(true);
        $(".jHueNotify").remove();
        $.post("/oozie/editor/coordinator/save/", {
          "coordinator": ko.mapping.toJSON(self.coordinator, COORDINATOR_MAPPING)
        }, function (data) {
          if (data.status == 0) {
            if (self.coordinator.id() == null) {
              shareViewModel.setDocUuid(data.uuid);
            }
            self.coordinator.id(data.id);
            self.coordinator.tracker().markCurrentStateAsClean();
            if (typeof cb === 'function') {
              cb(data);
            } else {
              $(document).trigger("info", data.message);
            }
            if (!cb) { // cb from integrated scheduler
              hueUtils.changeURL('/hue/oozie/editor/coordinator/edit/?coordinator=' + data.id);
            }
          }
          else {
            $(document).trigger("error", data.message);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        }).always(function () {
          self.isSaving(false);
        });
      }
    };

    self.gen_xml = function () {
      $(".jHueNotify").remove();
      hueAnalytics.log('oozie/editor/coordinator', 'gen_xml');

      $.post("/oozie/editor/coordinator/gen_xml/", {
        "coordinator": ko.mapping.toJSON(self.coordinator, COORDINATOR_MAPPING)
      }, function (data) {
        if (data.status == 0) {
          console.log(data.xml);
        }
        else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.showSubmitPopup = function () {
      $(".jHueNotify").remove();

      if (!self.coordinator.isDirty()) {
        hueAnalytics.log('oozie/editor/coordinator', 'submit');
        $.get("/oozie/editor/coordinator/submit/" + self.coordinator.id(), {
          format: 'json'
        }, function (data) {
          $(document).trigger("showSubmitPopup", data);
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
      }
    };
  };

  return CoordinatorEditorViewModel;
})();
