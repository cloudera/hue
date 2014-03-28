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

var Query = function (vm, query) {
  var self = this;

  self.q = ko.observable(query.q);
  self.fq = query.fq
  
  self.selectFacet = function(facet_json) {
	self.fq[facet_json.cat] = facet_json.value;
	vm.search();
  }

  self.unselectFacet = function(facet_json) {
	delete self.fq[facet_json.cat];
    vm.search();
  }
};

var FieldFacet = function(vm, props) {
  self.id = props.id;  
  self.label = props.name;
  self.field = props.name;
  self.type = "field";
}

// FieldListFacet
// RangeFacet


var Collection = function (vm, collection) {
  var self = this;

  self.id = collection.id;
  self.name = collection.name;
  self.template = ko.mapping.fromJS(collection.template);
  self.template.fields.subscribe(function() {
	vm.search();
  });
  self.template.template.subscribe(function() {
    vm.search();
  });
  self.facets = ko.mapping.fromJS(collection.facets);

  self.fields = ko.observableArray(collection.fields);

  self.addFacet = function(facet_json) {
    self.facets.push(ko.mapping.fromJS({
	   "uuid": "f6618a5c-bbba-2886-1886-bbcaf01409ca",
        "verbatim": "", "isVerbatim": false, "label": facet_json.name, 
	    "field": facet_json.name, "type": "field"
    }));
  }  
  
  self.addDynamicFields = function() {
	$.post("/search/index/" + self.id + "/fields/dynamic", {		
	  }, function (data){
		if (data.status == 0) {
		  $.each(data.dynamic_fields, function(index, field) {
            self.fields.push(field);
		  });
		}
	  }).fail(function(xhr, textStatus, errorThrown) {}
	);
  }
    
  // Init
  self.addDynamicFields();
};


var SearchViewModel = function (collection_json, query_json) {
  var self = this;

  // Models
  self.collection = new Collection(self, collection_json);
  self.query = new Query(self, query_json);
  
  // UI
  self.response = ko.observable({});
  self.results = ko.observableArray([]);
  self.norm_facets = ko.computed(function () {
    return self.response().normalized_facets;
  });
  
  self.selectedFacet = ko.observable();

  self.search = function () {
	$(".jHueNotify").hide();
    $.post("/search/search", {
        collection: ko.mapping.toJSON(self.collection),
        query: ko.mapping.toJSON(self.query),
      }, function (data) {
       self.response(data); // If error we should probably update only the facets
   	   self.results.removeAll(); 
   	   if (data.error) {
   		 $(document).trigger("error", data.error);
   	   } else {
   	     if (self.collection.template.isGridLayout()) {
 	       // Table view
 	       $.each(data.response.docs, function (index, item) {
 	    	 var row = [];
 	    	 $.each(self.collection.template.fields(), function (index, column) {
 	    	   row.push(item[column]); // TODO: if null + some escaping
 	    	 });
 	    	 self.results.push(row);
 	       });
   	     } else {
   	   	   // Template view
   	       var _mustacheTmpl = fixTemplateDotsAndFunctionNames(self.collection.template.template());
           $.each(data.response.docs, function (index, item) {
             addTemplateFunctions(item);
             self.results.push(Mustache.render(_mustacheTmpl, item));
           });
         }
   	   }
     }).fail(function(xhr, textStatus, errorThrown) {    	
       $(document).trigger("error", xhr.responseText);
     });
  };
    
  self.selectSingleFacet = function(normalized_facet_json) {
	$.each(self.collection.facets(), function(index, facet) {
      if (facet.field() == normalized_facet_json.field) {
        self.selectedFacet(facet);
      }
	});	  
  }
  
  self.removeFacet = function(facet_json) {
	$.each(self.collection.facets(), function(index, item) {
	  if (item.field() == facet_json.field) {
		self.collection.facets.remove(item);
	   }
	});
	self.search();
  }
};
