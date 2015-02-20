/*
 Licensed to Cloudera, Inc. under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  Cloudera, Inc. licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
*/

describe("Designs", function(){
  var viewModel;

  function getSampleDesign(id, name, node_type, is_shared, is_trashed, is_editable){
    return {
      "is_shared": is_shared,
      "node_type": node_type, 
      "last_modified": 1366678126.0, 
      "name": name, 
      "owner": "hdfs", 
      "editable": is_editable, 
      "id": id, 
      "is_trashed": is_trashed, 
      "description": ""
    };
  }


  var models = [
    getSampleDesign(1, 'test1', 'mapreduce', true, false, true),
    getSampleDesign(2, 'test2', 'java', true, false, true),
    getSampleDesign(3, 'test3', 'shell', true, false, true),
  ];

  beforeEach(function(){
    viewModel = new Designs({models: models});
    ko.applyBindings(viewModel);
  });

  describe("When clicking select all", function(){

    it("should select all designs and deselect them all", function(){
      viewModel.selectAll();
      expect(viewModel.selectedDesignObjects().length).toEqual(viewModel.designs().length);
      viewModel.deselectAll();
      expect(viewModel.selectedDesignObjects().length).toEqual(0);
      viewModel.toggleSelectAll();
      expect(viewModel.selectedDesignObjects().length).toEqual(viewModel.designs().length);
      viewModel.toggleSelectAll();
      expect(viewModel.selectedDesignObjects().length).toEqual(0);
    });

  });

  describe("When selecting a design", function(){

    it("should return a selectedDesign", function(){
      viewModel.designs()[0].selected(true);
      expect(viewModel.selectedDesign().name).toEqual(viewModel.designs()[0].design().name);
    });

  });
});
