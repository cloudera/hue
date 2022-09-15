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

/**
 * Provides file, archive, property, param
 * arg, argument, EnvVar, prepares, delete,
 * mkdir, touch, chmod, move, and touchz
 * field operations.
 */
const NodeFields = {
  removeFile: function (data, event) {
    const self = this;
    self.files.remove(data);
    $(document).trigger('remove.file.workflow', [data]);
  },
  addFile: function (data, event) {
    const self = this;
    const prop = { name: ko.observable(''), dummy: ko.observable('') };
    prop.name.subscribe(value => {
      self.files.valueHasMutated();
    });
    self.files.push(prop);
    $(document).trigger('add.file.workflow', [data]);
  },
  removeArchive: function (data, event) {
    const self = this;
    self.archives.remove(data);
    $(document).trigger('remove.archive.workflow', [data]);
  },
  addArchive: function (data, event) {
    const self = this;
    const prop = { name: ko.observable(''), dummy: ko.observable('') };
    prop.name.subscribe(value => {
      self.archives.valueHasMutated(;
    });
    self.archives.push(prop);
    $(document).trigger('add.archive.workflow', [data]);
  },
  removeProperty: function (data, event) {
    const self = this;
    self.job_properties.remove(data);
    $(document).trigger('remove.property.workflow', [data]);
  },
  addProperty: function (data, event) {
    const self = this;
    const prop = { name: ko.observable(''), value: ko.observable('') };
    prop.name.subscribe(value => {
      self.job_properties.valueHasMutated();
    });
    prop.value.subscribe(value => {
      self.job_properties.valueHasMutated();
    });
    self.job_properties.push(prop);
    $(document).trigger('add.property.workflow', [data]);
  },
  addParam: function (data, event) {
    const self = this;
    const prop = { value: ko.observable(''), type: ko.observable('param') };
    prop.value.subscribe(value => {
      self.params.valueHasMutated();
    });
    prop.type.subscribe(value => {
      self.params.valueHasMutated();
    });
    self.params.push(prop);
    $(document).trigger('add.param.workflow', [data]);
  },
  addArgument: function (data, event) {
    const self = this;
    const prop = { value: ko.observable(''), type: ko.observable('argument') };
    prop.value.subscribe(value => {
      self.params.valueHasMutated();
    });
    prop.type.subscribe(value => {
      self.params.valueHasMutated();
    });
    self.params.push(prop);
    $(document).trigger('add.argument.workflow', [data]);
  },
  addArg: function (data, event) {
    const self = this;
    const prop = { value: ko.observable(''), type: ko.observable('arg') };
    prop.value.subscribe(value => {
      self.params.valueHasMutated();
    });
    prop.type.subscribe(value => {
      self.params.valueHasMutated();
    });
    self.params.push(prop);
    $(document).trigger('add.arg.workflow', [data]);
  },
  addEnvVar: function (data, event) {
    const self = this;
    const prop = { value: ko.observable(''), type: ko.observable('env-var') };
    prop.value.subscribe(value => {
      self.params.valueHasMutated();
    });
    prop.type.subscribe(value => {
      self.params.valueHasMutated();
    });
    self.params.push(prop);
    $(document).trigger('add.envvar.workflow', [data]);
  },
  removeParam: function (data, event) {
    const self = this;
    self.params.remove(data);
    $(document).trigger('remove.param.workflow', [data]);
  },
  addPrepareDelete: function (data, event) {
    const self = this;
    const prop = { value: ko.observable(''), type: ko.observable('delete') };
    prop.value.subscribe(value => {
      self.prepares.valueHasMutated();
    });
    prop.type.subscribe(value => {
      self.prepares.valueHasMutated();
    });
    self.prepares.push(prop);
    $(document).trigger('add.prepare_delete.workflow', [data]);
  },
  addPrepareMkdir: function (data, event) {
    const self = this;
    const prop = { value: ko.observable(''), type: ko.observable('mkdir') };
    prop.value.subscribe(value => {
      self.prepares.valueHasMutated();
    });
    prop.type.subscribe(value => {
      self.prepares.valueHasMutated();
    });
    self.prepares.push(prop);
    $(document).trigger('add.prepare_mkdir.workflow', [data]);
  },
  removePrepare: function (data, event) {
    const self = this;
    self.prepares.remove(data);
    $(document).trigger('remove.prepare.workflow', [data]);
  },
  addDelete: function (data, event) {
    const self = this;
    const prop = { name: ko.observable('') };
    prop.name.subscribe(value => {
      self.deletes.valueHasMutated();
    });
    self.deletes.push(prop);
    $(document).trigger('add.delete.workflow', [data]);
  },
  removeDelete: function (data, event) {
    const self = this;
    self.deletes.remove(data);
    $(document).trigger('remove.delete.workflow', [data]);
  },
  addMkdir: function (data, event) {
    const self = this;
    const prop = { name: ko.observable('') };
    prop.name.subscribe(value => {
      self.mkdirs.valueHasMutated();
    });
    self.mkdirs.push(prop);
    $(document).trigger('add.mkdir.workflow', [data]);
  },
  removeMkdir: function (data, event) {
    const self = this;
    self.mkdirs.remove(data);
    $(document).trigger('remove.mkdir.workflow', [data]);
  },
  addMove: function (data, event) {
    const self = this;
    const prop = { source: ko.observable(''), destination: ko.observable('') };
    prop.source.subscribe(value => {
      self.moves.valueHasMutated();
    });
    prop.destination.subscribe(value => {
      self.moves.valueHasMutated();
    });
    self.moves.push(prop);
    $(document).trigger('add.move.workflow', [data]);
  },
  removeMove: function (data, event) {
    const self = this;
    self.moves.remove(data);
    $(document).trigger('remove.move.workflow', [data]);
  },
  addChmod: function (data, event) {
    const self = this;
    const prop = {
      path: ko.observable(''),
      permissions: ko.observable(''),
      recursive: ko.observable('')
    };
    prop.path.subscribe(value => {
      self.chmods.valueHasMutated();
    });
    prop.permissions.subscribe(value => {
      self.chmods.valueHasMutated();
    });
    prop.recursive.subscribe(value => {
      self.chmods.valueHasMutated();
    });
    self.chmods.push(prop);
    $(document).trigger('add.chmod.workflow', [data]);
  },
  removeChmod: function (data, event) {
    const self = this;
    self.chmods.remove(data);
    $(document).trigger('remove.chmod.workflow', [data]);
  },
  addTouchz: function (data, event) {
    const self = this;
    const prop = { name: ko.observable('') };
    prop.name.subscribe(value => {
      self.touchzs.valueHasMutated();
    });
    self.touchzs.push(prop);
    $(document).trigger('add.touchz.workflow', [data]);
  },
  removeTouchz: function (data, event) {
    const self = this;
    self.touchzs.remove(data);
    $(document).trigger('remove.touchz.workflow', [data]);
  }
};
