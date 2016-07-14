## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
  from desktop.views import commonheader, commonfooter, commonshare, commonimportexport
  from django.utils.translation import ugettext as _
%>
<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_("Solr Indexes"), "search", user, "60px") | n,unicode }


<div class="container-fluid">
  <div class="card card-small">
  <h1 class="card-heading simple">${ _('Solr Indexer') }</h1>
  </div>
</div>


<!-- ko template: 'create-index-wizard' --><!-- /ko -->

<script type="text/html" id="create-index-wizard">
  <div class="snippet-settings" data-bind="visible: createWizard.show" style="
  text-align: center;">

    <div class="control-group" data-bind="css: { error: createWizard.isNameAvailable() === false, success: createWizard.isNameAvailable()}">
      <label for="collectionName" class="control-label">${ _('Name') }</label>
      <div class="controls">
        <input type="text" class="form-control" id = "collectionName" data-bind="value: createWizard.fileFormat().name, valueUpdate: 'afterkeydown'">
        <span class="help-block" data-bind="visible: createWizard.isNameAvailable() === true">${ _('Collection name available') }</span>
        <span class="help-block" data-bind="visible: createWizard.isNameAvailable() === false && createWizard.fileFormat().name().length > 0">${_('This collection already exists') }</span>
        <span class="help-block" data-bind="visible: createWizard.isNameAvailable() === false && createWizard.fileFormat().name().length == 0">${_('This collection needs a name') }</span>
      </div>
    </div>

    <div class="control-group">
      <label for="path" class="control-label">${ _('Path') }</label>
      <div class="controls">
        <input type="text" class="form-control" id = "path" data-bind="value: createWizard.fileFormat().path">
        <a style="margin-bottom:10px" href="javascript:void(0)" class="btn" data-bind="click: createWizard.guessFormat">${_('Guess Format')}</a>
      </div>
    </div>


    <div data-bind="visible: createWizard.fileFormat().show">
      <div data-bind="with: createWizard.fileFormat().format">
          <h3>${_('File Type')}: <select data-bind="options: $root.createWizard.fileTypes, value: type"></select>
          </h3>

          <!-- ko template: {name: 'format-settings-'+type()}--><!-- /ko -->
        </div>

        <h3>${_('Fields')}</h3>
        <div data-bind="foreach: createWizard.fileFormat().columns">
          <div data-bind="template: { name:'field-template',data:$data}"></div>
        </div>

        <h3>${_('Preview')}</h3>
        <table style="margin:auto;text-align:left">
          <thead>
            <tr data-bind="foreach: createWizard.fileFormat().columns">
              <!-- ko template: 'field-preview-header-template' --><!-- /ko -->
            </tr>
          </thead>
          <tbody data-bind="foreach: createWizard.sample">
            <tr data-bind="foreach: $data">
              <!-- ko if: $index() < $root.createWizard.fileFormat().columns().length -->
                <td data-bind="visible: $root.createWizard.fileFormat().columns()[$index()].keep, text: $data">
                </td>

                <!-- ko with: $root.createWizard.fileFormat().columns()[$index()] -->
                  <!-- ko template: 'output-generated-field-data-template' --> <!-- /ko -->
                <!-- /ko -->
              <!-- /ko -->
            </tr>
          </tbody>
        </table>

        <br><hr><br>

        <a href="javascript:void(0)" class="btn" data-bind="visible: !createWizard.indexingStarted() , click: createWizard.indexFile, css: {disabled : !createWizard.readyToIndex()}">${_('Index File!')}</a>

        <h4 class="error" data-bind="visible: !createWizard.isNameAvailable() && createWizard.fileFormat().name().length > 0">${_('Collection needs a unique name')}</h4>
        <h4 class="error" data-bind="visible: !createWizard.isNameAvailable() && createWizard.fileFormat().name().length == 0">${_('Collection needs a name')}</h4>


        <a href="javascript:void(0)" class="btn btn-success" data-bind="visible: createWizard.jobId, attr: {href: '/oozie/list_oozie_workflow/' + createWizard.jobId() }" target="_blank" title="${ _('Open') }">
          ${_('View Indexing Status')}
        </a>

      </div>

    <br/>
  </div>
</script>

<script type="text/html" id="format-settings-hue">
</script>

<script type="text/html" id="format-settings-csv">
  <h4>${_('Has Header')}:</h4>
  <input type="checkbox" data-bind="checked: hasHeader">
  <h4>${_('Quote Character')}:</h4>
  <input data-bind="value: quoteChar">
  <h4>${_('Record Separator')}:</h4>
  <input data-bind="value: recordSeparator">
  <h4>${_('Field Separator')}:</h4>
  <input data-bind="value: fieldSeparator">
</script>

<script type="text/html" id="field-template">
  <div>
    <span>${_('Keep')}</span><input type="checkbox" data-bind="checked: keep">
    <span>${_('Required')}</span><input type="checkbox" data-bind="checked: required">
    <input type="text" data-bind="value: name"></input> - <select data-bind="options: $root.createWizard.fieldTypes, value: type"></select>
    <button class="btn" data-bind="click: $root.createWizard.addOperation">${_('Add Operation')}</button>
  </div>
  <div data-bind="foreach: operations">
    <div data-bind="template: { name:'operation-template',data:{operation: $data, list: $parent.operations}}"></div>
  </div>
</script>

<script type="text/html" id="operation-template">
  <div><select data-bind="options: $root.createWizard.operationTypes.map(function(o){return o.name});, value: operation.type"></select>
  <!-- ko template: "operation-args-template" --><!-- /ko -->
    <!-- ko if: operation.settings().outputType() == "custom_fields" -->
      <input type="number" data-bind="value: operation.numExpectedFields">
    <!-- /ko -->
    <button class="btn" data-bind="click: function(){$root.createWizard.removeOperation(operation, list)}">${_('remove')}</button>
    <div style="padding-left:50px" data-bind="foreach: operation.fields">
      <div data-bind="template: { name:'field-template',data:$data}"></div>
    </div>

  </div>
</script>

<script type="text/html" id="field-preview-header-template">

  <th data-bind="visible: keep, text: name" style="padding-right:60px"></th>
  <!-- ko foreach: operations -->
    <!--ko foreach: fields -->
      <!-- ko template: 'field-preview-header-template' --><!-- /ko -->
    <!-- /ko -->
  <!--/ko -->
</script>


<script type="text/html" id="output-generated-field-data-template">
  <!-- ko foreach: operations -->
    <!--ko foreach: fields -->
      <td data-bind="visible: keep">[[${_('generated')}]]</td>
      <!-- ko template: 'output-generated-field-data-template' --><!-- /ko -->
    <!-- /ko -->
  <!--/ko -->
</script>

<script type="text/html" id="operation-args-template">
  <!-- ko foreach: {data: operation.settings().getArguments(), as: 'argument'} -->
    <!-- ko template: {name: 'operation-arg-'+argument.type, data:{operation: $parent.operation, argVal: $parent.operation.settings()[argument.name]}}--><!-- /ko -->
  <!-- /ko -->

</script>

<script type="text/html" id="operation-arg-text">
  <input type="text" data-bind="attr: {placeholder: argument.name}, value: argVal">
</script>

<script type="text/html" id="operation-arg-checkbox">
  <h4 data-bind="text: argument.name"></h4>
  <input type="checkbox" data-bind="checked: argVal">
</script>

<script type="text/html" id="operation-arg-mapping">
  <!-- ko foreach: argVal-->
    <div>
      <input type="text" data-bind="value: key, attr: {placeholder: 'key'}">
      <input type="text" data-bind="value: value, attr: {placeholder: 'value'}">
      <button class="btn" data-bind="click: function(){$parent.operation.settings().mapping.remove($data)}">${_('Remove Pair')}</button>
    </div>
  <!-- /ko -->
  <button class="btn" data-bind="click: operation.addPair">${_('Add Pair')}</button>
  <br>
</script>

<div class="hueOverlay" data-bind="visible: isLoading">
  <!--[if lte IE 9]>
    <img src="${ static('desktop/art/spinner-big.gif') }" />
  <![endif]-->
  <!--[if !IE]> -->
    <i class="fa fa-spinner fa-spin"></i>
  <!-- <![endif]-->
</div>


<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/knockout-mapping.min.js') }" type="text/javascript" charset="utf-8"></script>


<script type="text/javascript" charset="utf-8">
var fieldNum = 0;

var getNewFieldName = function(){
  fieldNum++;
  return "new_field_" + fieldNum
}

  var createDefaultField = function(){
    return {
      name: ko.observable(getNewFieldName()),
      type: ko.observable("string"),
      keep: ko.observable(true),
      required: ko.observable(true),
      operations: ko.observableArray([])
    }
  };

  var Operation = function(type){
    var self = this;

    var createArgumentValue = function(arg){
      if(arg.type == "mapping"){
        return ko.observableArray([]);
      }
      else if(arg.type =="checkbox"){
        return ko.observable(false);
      }
      else{
        return ko.observable("");
      }
    }

    var constructSettings = function(type){
      var settings = {};

      var operation = viewModel.createWizard.operationTypes.find(function(currOperation){
        return currOperation.name == type;
      });

      for(var i = 0; i < operation.args.length; i++){
        argVal = createArgumentValue(operation.args[i]);

        if(operation.args[i].type == "checkbox" && operation.outputType == "checkbox_fields"){
          argVal.subscribe(function(newVal){
            if(newVal){
              self.fields.push(createDefaultField());
            }
            else{
              self.fields.pop();
            }
          });
        }

        settings[operation.args[i].name] = argVal;
      }

      settings.getArguments = function(){
        return operation.args
      };

      settings.outputType= function(){
        return operation.outputType;
      }

      return settings;
    };

    var init = function(){
      self.fields([]);
      self.numExpectedFields(0);

      self.numExpectedFields.subscribe(function(numExpectedFields){
        if(numExpectedFields < self.fields().length){
          self.fields(self.fields().slice(0,numExpectedFields));
        }
        else if (numExpectedFields > self.fields().length){
          difference = numExpectedFields - self.fields().length;

          for(var i = 0; i < difference; i++){
            self.fields.push(createDefaultField());
          }
        }
      });

      self.settings(constructSettings(self.type()));
    }

    self.type = ko.observable(type);
    self.fields = ko.observableArray();
    self.numExpectedFields = ko.observable();
    self.settings = ko.observable();

    init();

    self.type.subscribe(function(newType){
      init();
    });

    self.addPair = function(){
      self.settings().mapping.push({key: ko.observable(""), value: ko.observable("")});
    }
  }

  var getFileFormat = function(type){
    if(type == "csv"){
      return new CsvFileType();
    }
    else if(type == "hue"){
      return new HueFileType();
    }
  }

  var FileType = function(){
    var self = this;

    self.loadFromObj = function(args){
      for (var attr in args){
        self[attr] = ko.mapping.fromJS(args[attr]);
      }
    }
  }

  var HueFileType = function(args){
    var self = new FileType();

    self.type = ko.observable("hue");

    if(args) self.loadFromObj(args);

    return self;
  }

  var CsvFileType = function(args){
    var self = new FileType();

    self.quoteChar = ko.observable('"');
    self.recordSeparator = ko.observable("\\n");
    self.type = ko.observable("csv");
    self.hasHeader = ko.observable(false);
    self.fieldSeparator = ko.observable(',');

    if(args) self.loadFromObj(args);

    self.quoteChar.subscribe(viewModel.createWizard.guessFieldTypes);
    self.recordSeparator.subscribe(viewModel.createWizard.guessFieldTypes);
    self.hasHeader.subscribe(viewModel.createWizard.guessFieldTypes);
    self.fieldSeparator.subscribe(viewModel.createWizard.guessFieldTypes);

    return self;
  }

  var File_Format = function (vm) {
    var self = this;


    self.name = ko.observable('');
    self.show = ko.observable(false);

    self.path = ko.observable('/tmp/test.csv');
    self.format = ko.observable();
    self.columns = ko.observableArray();
  };

  var CreateWizard = function (vm) {
    var self = this;
    var guessFieldTypesXhr;

    self.operationTypes = ${operators_json | n};

    self.fieldTypes = ko.observableArray(${fields_json | n});
    self.fileTypes = ["csv","hue"];


    self.show = ko.observable(true);
    self.showCreate = ko.observable(false);

    self.fileFormat = ko.observable(new File_Format(vm));

    self.sample = ko.observableArray();

    self.jobId = ko.observable(null);

    self.indexingStarted = ko.observable(false);

    self.isNameAvailable = ko.computed(function(){
      var name = self.fileFormat().name();
      return viewModel && viewModel.collectionNameAvailable(name) && name.length > 0;
    });

    self.readyToIndex = ko.computed(function(){
      var validFields = self.fileFormat().columns().length

      return self.isNameAvailable() && validFields;
    });

    self.fileFormat().format.subscribe(function(){
      self.guessFieldTypes();

      if(self.fileFormat().format().type){
        self.fileFormat().format().type.subscribe(function(newType){
          self.fileFormat().format(getFileFormat(newType));
        });
      }
    });

    self.guessFormat = function() {
      viewModel.isLoading(true);
      $.post("${ url('indexer:guess_format') }", {
        "fileFormat": ko.mapping.toJSON(self.fileFormat)
      }, function(resp) {

        self.fileFormat().format(new CsvFileType(resp));

        self.fileFormat().show(true);

        viewModel.isLoading(false);
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);

        viewModel.isLoading(false);
      });
    }

    self.guessFieldTypes = function(){
      if(guessFieldTypesXhr) guessFieldTypesXhr.abort();
      guessFieldTypesXhr = $.post("${ url('indexer:guess_field_types') }",{
        "fileFormat": ko.mapping.toJSON(self.fileFormat)
      }, function(resp){
        resp.columns.forEach(function(entry, i, arr){
          arr[i] = ko.mapping.fromJS(entry);
        });
        self.fileFormat().columns(resp.columns);

        self.sample(resp.sample);
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);

        viewModel.isLoading(false);
      });;
    };

    self.indexFile = function() {
      if(!self.readyToIndex()) return;

      self.indexingStarted(true);

      viewModel.isLoading(true);

      $.post("${ url('indexer:index_file') }", {
        "fileFormat": ko.mapping.toJSON(self.fileFormat)
      }, function(resp) {
        self.showCreate(true);
        self.jobId(resp.jobId);
        viewModel.isLoading(false);
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
        viewModel.isLoading(false);
      });
    }

    self.removeOperation = function(operation, operationList){
      operationList.remove(operation);
    }

    self.addOperation = function(field){
      field.operations.push(new Operation("split"));
    }
  };

  var Editor = function () {
    var self = this;

    self.collections = ${ indexes_json | n }.filter(function(index){
      return index.type == 'collection';
    });;

    self.createWizard = new CreateWizard(self);
    self.isLoading = ko.observable(false);

    self.collectionNameAvailable = function(name){
      var matchingCollections = self.collections.filter(function(collection){
        return collection.name == name;
      });

      return matchingCollections.length == 0;
    }

  };

  var viewModel;

  $(document).ready(function () {
    viewModel = new Editor();
    ko.applyBindings(viewModel);
  });
</script>


${ commonfooter(request, messages) | n,unicode }
