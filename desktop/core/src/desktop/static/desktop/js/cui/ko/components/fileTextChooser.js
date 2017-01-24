// Copyright (c) 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/FileTextChooser
 * @description The status component.
 * Examples:
 *   <cui-file-text-chooser params="valueAccessor: someObservable, ...other options...">
 *
 *  valueAccessor is required and must be an observable.
 *
 *  Other params include:
 *   placeholder: what help text to show in the text area
 *   preValidate: make sure the file upload is working before uploading a big file
 *   isValid: verify the file uploaded is valid
 *   onError: what to trigger on error
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import i18n from 'cloudera-ui/utils/i18n';
import ko from 'knockout';
import _ from '_';

// for radio button state changes
var TEXT_MODE = 'textMode';
var FILE_MODE = 'fileMode';

// arbitrarily chosen flags for updating the file input.
var FILE_ERROR = null;
var accumulator = 0;

/**
 * @constructor
 * @alias module:ko/components/FileTextChooser
 * @param {ko.observable} params.valueAccessor Required. Represents the string value of the chosen file.
 * @param {string} [params.placeholder] optional placeholder for text area.
 * @param {function} [params.preValidate] optional function to call on the reading of the first file blob.
 * @param {function|ko.observable} [params.isValid] optional widget validation function.
 * @param {function} [params.onError] optional function to call on error.
 * @param {ko.observable} [params.editable] optional don't allow file upload.
 * @param {boolean} [params.sensitive] optional.  Don't show the data after upload if sensitive.
 */
class FileTextChooser {
  constructor(params) {
    this.valueAccessor = params.valueAccessor;
    this.name = 'fileInput.' + accumulator++;

    // setup optional parameters.
    this.placeholder = params.placeholder || '';
    this.preValidate = params.preValidate || function() {
      return true;
    };

    this.isValid = params.isValid || function() {
      return true;
    };

    this.onError = params.onError || function() {
      return '';
    };

    this.sensitive = params.sensitive;
    var editable = params.editable || ko.observable(true);

    /**
     * Read-write observable that controls showing the file controls.
     * @type {boolean}
     */
    this.editable = editable;

    /**
     * Read-write observable of the radio mode.
     * This can be TEXT_MODE, or FILE_MODE.
     * @type {string}
     */
    this.radioMode = ko.observable(this.canFileUpload() ?
                                   FILE_MODE :
                                   TEXT_MODE);

    /**
     * Read-write observable that stores the current mode
     *  of this widget: FILE_MODE or TEXT_MODE.
     * @type {string}
     */
    this.mode = ko.pureComputed({
      read: function() {
        // We can only show the text area when not editable
        if (!this.editable()) {
          return TEXT_MODE;
        }

        return this.radioMode();
      },
      write: function(val) {
        if (val === TEXT_MODE) {
          this.setTextMode();
        } else {
          this.setFileMode();
        }
      }
    }, this);

    /**
     * Read-only observable, true if in TEXT_MODE.
     * @type {boolean}
     */
    this.textMode = ko.computed(function() {
      return !this.canFileUpload() || this.mode() === TEXT_MODE;
    }, this);

    /**
     * Read-only observable, true if in FILE_MODE.
     * @type {boolean}
     */
    this.fileMode = ko.computed(function() {
      return this.canFileUpload() && this.mode() === FILE_MODE;
    }, this);

    /**
     * Internal Read-write observable, stores the current selected file name.
     * @type {string}
     * @private
     */
    this._fileName = ko.observable('');

    /**
     * Read-write observable, sets the file name attribute for the file chooser.
     * Also updates the state of the file widget.
     * @type {string}
     */
    this.fileName = ko.computed({
      read: function() {
        return this._fileName() || '';
      },
      write: function(val) {
        this._fileName(val);
      }
    }, this);

    /**
     * Internal Read-write observable, stores the current error message.
     * @type {string}
     * @private
     */
    this.errorMessage = ko.observable(false);

    /**
     * Read-write observable that wraps the valueAccessor passed in.
     * @type {string}
     */
    this.data = ko.pureComputed({
      read: function() {
        return this.valueAccessor();
      },
      write: function(val) {
        this.valueAccessor(val);
        var valid = this.isValid();
        if (val && val.length > 0) {
          this.showError(!valid);
        }
      }
    }, this);
    this.data(this.valueAccessor());

    /**
     * Show file mode by default if we have nothing to show
     */
    this.valueAccessor.subscribe(function(val) {
      if (this.sensitive) {
        return;
      }

      if (_.isEmpty(val)) {
        this.setFileMode();
      } else {
        // show the text if it's not sensitive
        if (!this.sensitive) {
          this.setTextMode();
        }
      }
    }, this);

    this.fileModeHint = i18n.t('ko.components.fileTextChooser.fileModeHint');
    this.textModeHint = i18n.t('ko.components.fileTextChooser.textModeHint');
    this.fileButtonLabel = i18n.t('ko.components.fileTextChooser.fileButtonLabel');

    return this;
  }

  /**
   * Returns if the browser supports HTML5 file upload.
   */
  canFileUpload() {
    return !!(window.File && window.FileReader && window.FileList && window.Blob);
  }

  /**
   * Reset things when modes change.
   */
  reset() {
    this.fileName('');
    this.errorMessage(false);
  }

  /**
   * Update the radio button state to text Mode and reset other components.
   */
  setTextMode() {
    this.radioMode(TEXT_MODE);

    // reset the data if sensitive
    if (this.sensitive) {
      this.data('');
    }

    this.reset();
  }

  /**
   * Update the radio button state to file Mode and reset other components.
   */
  setFileMode() {
    this.radioMode(FILE_MODE);
    this.reset();
  }

  /**
   * Show the current error given a custom onError function.
   * @param {boolean} show if we want to show/hide the error message.
   */
  showError(show) {
    if (show) {
      var error = this.onError ? this.onError() : '';
      this.errorMessage(error);
      if (this.fileMode()) {
        this.fileName(FILE_ERROR);
      }
    } else {
      this.errorMessage(false);
    }
  }

  /**
   * Common file extraction logic.  Invoked via knockout change event on a file input.
   * @param {FileTextChooser} self This object.
   * @param {Event} event The change event with the file input.
   */
  extractFile(self, event) {
    var FileReader = window.FileReader;
    var fileInput = event.target;
    var files = fileInput.files;
    if (files.length === 0) {
      return;
    }

    var reader = new FileReader();
    var checked = false; // make sure a bogus file is not sent
    reader.onerror = _.bind(function(event) {
      this.showError(true);
    }, this);

    reader.onprogress = _.bind(function(event) {
      if (checked || !this.preValidate) {
        return;
      }

      checked = true;
      if (!this.preValidate(event.target.result)) {
        // try to abort the event if the file looks wrong.
        event.target.abort();
        event.target.aborted = true;
        this.data('\n');
      }
    }, this);

    reader.onload = _.bind(function(event) {
      if (event.target.aborted) {
        return;
      }

      this.fileName(fileInput.files[0].name);
      this.data(event.target.result);
    }, this);

    // read the file.
    reader.readAsText(files[0]);
  }
}

var template = `
<div class="cui-file-text-chooser" data-bind="css: {'has-error': errorMessage}">
  <div data-bind="visible: editable">
    <label class="radio-inline">
      <input value="fileMode"
             type="radio"
             data-bind="checked: mode, attr: {name: name}"/>
      <span data-bind="text: fileModeHint"></span>
    </label>
    <label class="radio-inline" data-bind="visible: canFileUpload">
      <input value="textMode"
             type="radio"
             data-bind="checked: mode, visible: canFileUpload, attr: {name: name}"/>
      <span data-bind="text: textModeHint"></span>
    </label>
  </div>
  <div class="file-controls cui-flex form-control-static" data-bind="visible: fileMode">
     <input type="file" data-bind="event: {change: extractFile}"/>
     <input type="text" class="form-control" data-bind="textInput: fileName" disabled="disabled"/>

    <button class="btn btn-default" tabindex="-1"
            data-bind="enable: fileMode, text: fileButtonLabel"></button>
  </div>

  <textarea rows="10" cols="80" class="form-control code"
            data-bind="event: {focus: function(){$element.select()}},
                       visible: textMode,
                       textInput: data,
                       enable: textMode && editable,
                       attr: {placeholder: placeholder}" spellcheck="false"></textarea>
  <p class="help-block" data-bind="visible: errorMessage, text: errorMessage"></p>
</div>
`;
componentUtils.addComponent(FileTextChooser, 'cui-file-text-chooser', template);

export default FileTextChooser;
