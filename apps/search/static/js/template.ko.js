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


var Query = function (importable) {
  var self = this;
  self.type = ko.observable(importable.type);
  self.name = ko.observable(importable.name);
  self.selected = ko.observable(false);
  self.handleSelect = function (row, e) {
    this.selected(!this.selected());
  };
};

var Collection = function (coll) {
  var self = this;

  self.id = ko.observable(coll.id);
  self.name = ko.observable(coll.name);
  self.label = ko.observable(coll.label);
  self.isCoreOnly = ko.observable(coll.isCoreOnly);
  self.absoluteUrl = ko.observable(coll.absoluteUrl);
  self.selected = ko.observable(false);
  self.hovered = ko.observable(false);

  self.handleSelect = function (row, e) {
    this.selected(!this.selected());
  };
  self.toggleHover = function (row, e) {
    this.hovered(!this.hovered());
  };
};

// sorting
// highlithing

//
// Facets (text or chart)
//   field 
//   range

// spacial search
// query facet
// pivot facet



var SearchViewModel = function (result, facets) {
  var self = this;

  // Mock testing
  //var TEMPLATE = {"extracode": "      \n<style type=\"text/css\">\nem {\n  font-weight: bold;\n  background-color: yellow;\n}\n.avatar {\n  margin: 10px;\n}\n.created {\n  margin-top: 10px;\n  color: #CCC;\n}\n.openTweet {\n  float: right;\n  margin: 10px;\n}\n</style>\n      \n    ", "highlighting": ["text"], "properties": {"highlighting_enabled": true}, "template": "\n\n<div class=\"row-fluid\">\n  <div class=\"row-fluid\">\n    <div class=\"row-fluid\">\n      <div class=\"span1\">\n        <img src=\"http://twitter.com/api/users/profile_image/{{user_screen_name}}\" class=\"avatar\">\n        </div>\n        <div class=\"span11\">\n          <b>{{user_name}}</b>\n          <br>\n            <a href=\"https://twitter.com/{{user_screen_name}}/status/{{id}}\" target=\"_blank\">\n              {{text}}\n            </a>\n            <br>\n              <div class=\"created\">{{#fromnow}}{{created_at}}{{/fromnow}}</div>\n            </div>\n          </div>\n          <br>\n          </div>\n        </div>\n        \n        "}
  //var FACETS = {"dates": [], "fields": [{"uuid": "f6618a5c-bbba-2886-1886-bbcaf01409ca", "verbatim": "", "isVerbatim": false, "label": "Location", "field": "user_location", "type": "field"}], "charts": [{"end": "2014-02-28T12:00:00Z", "uuid": "4883871c-0cea-8547-de60-7166d498098a", "verbatim": "", "start": "2014-02-28T12:00:00Z-10DAYS", "isVerbatim": false, "label": "Posted", "field": "created_at", "gap": "+5MINUTES", "type": "chart"}], "properties": {"sort": "count", "mincount": 1, "isEnabled": true, "limit": 10}, "ranges": [{"end": "1000", "uuid": "5533165a-0b1c-21b6-4ede-9d2fc301ed6b", "verbatim": "", "start": 0, "isVerbatim": false, "label": "Followers count", "field": "user_followers_count", "gap": "100", "type": "range"}, {"end": "10000", "uuid": "d5e66f3d-ca7d-67d7-05c7-33ec499cc106", "verbatim": "", "start": 0, "isVerbatim": false, "label": "Tweet count", "field": "user_statuses_count", "gap": "1000", "type": "range"}], "order": ["f6618a5c-bbba-2886-1886-bbcaf01409ca", "5533165a-0b1c-21b6-4ede-9d2fc301ed6b", "d5e66f3d-ca7d-67d7-05c7-33ec499cc106"]}
  
  var TEMPLATE = {"extracode": "", "highlighting": ["text"], "properties": {"highlighting_enabled": true},
		          "template": "{{user_screen_name}} {{user_name}} {{text}}", "isGridLayout": true, "fields": ["user_screen_name", "user_name", "text"]
  };
  var FACETS = {"dates": [], "fields": [
                   {
                	   "uuid": "f6618a5c-bbba-2886-1886-bbcaf01409ca", "verbatim": "", "isVerbatim": false, "label": "Location", 
                	    "field": "user_location", "type": "field"
                   }
                 ],
                 "charts": [], "properties": {"sort": "count", "mincount": 1, "isEnabled": true, "limit": 10}, "ranges": [], "order": []
  };  

  
  // Collection customization
  var collection = 10000004;
  self.template = ko.mapping.fromJS(TEMPLATE); //result.template;
  self.template.fields.subscribe(function() {
	self.search();
  });
  self.template.template.subscribe(function() {
    self.search();
  });
  self.facets = ko.mapping.fromJS(FACETS.fields); //facets.fields

  self.fields = ko.observableArray(["user_screen_name", "user_name", "text", "created_at", "user_statuses_count", "id"]); // ad dynamic ajaxifoed
  
  // Query URL  
  self.q = ko.observable('');
  self.qFacets = {}
  
  // Query results
  self.response = ko.observable({});
  self.results = ko.observableArray([]);
  self.norm_facets = ko.computed(function () {
    return self.response().normalized_facets;
  });
  
  // Forms
  self.selectedFacet = ko.observable();
  
  self.search = function () {
    $.post("/search/query2?format=json", {
        collection: collection,
        q: ko.toJSON(self.q),
        facets: ko.toJSON(self.facets),
        fq: ko.utils.stringifyJson(self.qFacets),
        template:  ko.mapping.toJSON(self.template),
      }, function (data) {
       self.response(data);
   	   self.results.removeAll(); 
   	   if (data.error) {
   		 $(document).trigger("error", data.error);   
   	   } else {
   	     if (self.template.isGridLayout()) {
 	       // Table view
 	       $.each(data.response.docs, function (index, item) {
 	    	 var row = [];
 	    	 $.each(self.template.fields(), function (index, column) {
 	    	   row.push(item[column]); // todo if is null
 	    	 });
 	    	 self.results.push(row);
 	       });
   	     } else {
   	   	   // Template view
   	       var _mustacheTmpl = fixTemplateDotsAndFunctionNames(self.template.template());
           $.each(data.response.docs, function (index, item) {
             addTemplateFunctions(item);
             self.results.push(Mustache.render(_mustacheTmpl, item));
           });
         }
   	   }
     }).fail(function(xhr, textStatus, errorThrown) {    	
       $(document).trigger("error", xhr.responseText); // cleanup all "alert jHueNotify alert-error" before
     });
  };
  
  self.addFacet = function(facet_json) {
    self.facets.push(ko.mapping.fromJS({
	   "uuid": "f6618a5c-bbba-2886-1886-bbcaf01409ca", "verbatim": "", "isVerbatim": false, "label": "Location", 
	    "field": facet_json.name, "type": "field"
    }));
  }
  
  self.selectSingleFacet = function(normalized_facet_json) {
	$.each(self.facets(), function(index, facet) {
      if (facet.field() == normalized_facet_json.field) {
        self.selectedFacet(facet);
      }
	});	  
  }
  
  self.removeFacet = function(facet_json) {
	 $.each(self.facets(), function(index, item) {
		if (item.field() == facet_json.field) {
		  self.facets.remove(item);
		}
	 });
	 self.search();
  }
  
  self.selectFacet = function(facet_json) {
	self.qFacets[facet_json.cat] = facet_json.value;
	self.search();
  }

  self.unselectFacet = function(facet_json) {
	delete self.qFacets[facet_json.cat];
    self.search();
  }
};
