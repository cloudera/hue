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

import $ from 'jquery';
import KnockoutObservable from '@types/knockout';

type ComplexValueAccessor = () => {
  value?: KnockoutObservable<string>;
  displayJustLastBit?: boolean;
};

const getFileBrowseButton = (
  inputElement: JQuery<HTMLInputElement>,
  selectFolder: string,
  valueAccessor: KnockoutObservable<string> | ComplexValueAccessor,
  stripHdfsPrefix: boolean,
  allBindingsAccessor: KnockoutAllBindingsAccessor,
  isAddon: boolean,
  isNestedModal: boolean,
  linkMarkup: boolean
): JQuery => {
  let button: JQuery;
  if (isAddon) {
    button = $('<span>').addClass('add-on muted pointer filechooser-clickable').text('..');
  } else if (linkMarkup) {
    button = $('<a>').addClass('btn').addClass('fileChooserBtn filechooser-clickable').text('..');
  } else {
    button = $('<button>')
      .addClass('btn')
      .addClass('fileChooserBtn filechooser-clickable')
      .text('..');
  }
  button.on('click', e => {
    e.preventDefault();
    if (!isNestedModal) {
      $('body').addClass('modal-open');
    }

    function callFileChooser() {
      let initialPath: string =
        (<string>inputElement.val()).trim() !== '' ? <string>inputElement.val() || '' : '/';
      if (
        (allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.skipInitialPathIfEmpty &&
          inputElement.val() === '') ||
        (allBindingsAccessor && allBindingsAccessor().filechooserPrefixSeparator)
      ) {
        initialPath = '';
      }
      if (inputElement.data('fullPath')) {
        initialPath = inputElement.data('fullPath');
      }
      if (initialPath.indexOf('hdfs://') > -1) {
        initialPath = initialPath.substring(7);
      }

      let supportSelectFolder = !!selectFolder;
      if (
        allBindingsAccessor &&
        typeof allBindingsAccessor().filechooserOptions !== 'undefined' &&
        typeof allBindingsAccessor().filechooserOptions.selectFolder !== 'undefined'
      ) {
        supportSelectFolder = allBindingsAccessor().filechooserOptions.selectFolder;
      }

      $('#filechooser').jHueFileChooser({
        suppressErrors: true,
        selectFolder: supportSelectFolder,
        onFolderChoose: filePath => {
          handleChoice(filePath, stripHdfsPrefix);
          if (selectFolder) {
            $('#chooseFile').modal('hide');
            if (!isNestedModal) {
              $('.modal-backdrop').remove();
            }
          }
        },
        onFileChoose: filePath => {
          handleChoice(filePath, stripHdfsPrefix);
          $('#chooseFile').modal('hide');
          if (!isNestedModal) {
            $('.modal-backdrop').remove();
          }
        },
        createFolder:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.createFolder,
        uploadFile:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.uploadFile,
        initialPath: initialPath,
        errorRedirectPath: '',
        forceRefresh: true,
        showExtraHome:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.showExtraHome,
        extraHomeProperties:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.extraHomeProperties
            ? allBindingsAccessor().filechooserOptions.extraHomeProperties
            : {},
        filterExtensions:
          allBindingsAccessor && allBindingsAccessor().filechooserFilter
            ? allBindingsAccessor().filechooserFilter
            : '',
        displayOnlyFolders:
          allBindingsAccessor &&
          allBindingsAccessor().filechooserOptions &&
          allBindingsAccessor().filechooserOptions.displayOnlyFolders
      });
      $('#chooseFile').modal('show');
      if (!isNestedModal) {
        $('#chooseFile').on('hidden', () => {
          $('body').removeClass('modal-open');
          $('.modal-backdrop').remove();
        });
      }
    }

    // check if it's a relative path
    callFileChooser();

    const handleChoice = (filePath: string, stripHdfsPrefix: boolean) => {
      if (allBindingsAccessor && allBindingsAccessor().filechooserPrefixSeparator) {
        filePath =
          (<string>inputElement.val()).split(allBindingsAccessor().filechooserPrefixSeparator)[0] +
          '=' +
          filePath;
      }
      if (
        allBindingsAccessor &&
        allBindingsAccessor().filechooserOptions &&
        allBindingsAccessor().filechooserOptions.deploymentDir
      ) {
        inputElement.data('fullPath', filePath);
        inputElement.attr('data-original-title', filePath);
        if (filePath.indexOf(allBindingsAccessor().filechooserOptions.deploymentDir) === 0) {
          filePath = filePath.substr(
            allBindingsAccessor().filechooserOptions.deploymentDir.length + 1
          );
        }
      }
      if (stripHdfsPrefix) {
        inputElement.val(filePath);
      } else {
        inputElement.val('hdfs://' + filePath);
      }
      inputElement.trigger('change');
      if (valueAccessor) {
        if (
          typeof valueAccessor() === 'function' ||
          typeof (<ComplexValueAccessor>valueAccessor)().value === 'function'
        ) {
          const complex = (<ComplexValueAccessor>valueAccessor)();
          if (complex.value) {
            complex.value(<string>inputElement.val());
            if (complex.displayJustLastBit) {
              inputElement.data('fullPath', <string>inputElement.val());
              inputElement.attr('data-original-title', <string>inputElement.val());
              const value = <string>inputElement.val();
              inputElement.val(value.split('/')[value.split('/').length - 1]);
            }
            return;
          }
        }
        (<KnockoutObservable<string>>valueAccessor())(<string>inputElement.val());
      }
    };
  });
  if (allBindingsAccessor && allBindingsAccessor().filechooserDisabled) {
    button.addClass('disabled').attr('disabled', 'disabled');
  }
  return button;
};

export default getFileBrowseButton;
