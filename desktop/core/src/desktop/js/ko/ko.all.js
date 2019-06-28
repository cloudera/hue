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

import ko from 'knockout';
import 'ko/ko.init';
import komapping from 'knockout.mapping';
import 'knockout-switch-case';
import 'knockout-sortable';
import 'knockout.validation';

import 'ext/ko.editable.custom';
import 'ext/ko.selectize.custom';

// import 'ko/bindings/charts/plotly/ko.plotly'; // The Plotly chart replacement
import 'ko/bindings/charts/mapchart/ko.mapChart';
import 'ko/bindings/charts/ko.barChart';
import 'ko/bindings/charts/ko.leafletMapChart';
import 'ko/bindings/charts/ko.lineChart';
import 'ko/bindings/charts/ko.partitionChart';
import 'ko/bindings/charts/ko.pieChart';
import 'ko/bindings/charts/ko.scatterChart';
import 'ko/bindings/charts/ko.timelineChart';

import 'ko/bindings/ko.aceEditor';
import 'ko/bindings/ko.aceResizer';
import 'ko/bindings/ko.appAwareTemplateContextMenu';
import 'ko/bindings/ko.assistFileDraggable';
import 'ko/bindings/ko.assistFileDroppable';
import 'ko/bindings/ko.assistVerticalResizer';
import 'ko/bindings/ko.attachViewModelToElementData';
import 'ko/bindings/ko.augmentHtml';
import 'ko/bindings/ko.autocomplete';
import 'ko/bindings/ko.autogrowInput';
import 'ko/bindings/ko.blurHide';
import 'ko/bindings/ko.bytesize';
import 'ko/bindings/ko.chosen';
import 'ko/bindings/ko.clearable';
import 'ko/bindings/ko.clickForAceFocus';
import 'ko/bindings/ko.clickToCopy';
import 'ko/bindings/ko.codemirror';
import 'ko/bindings/ko.contextMenu';
import 'ko/bindings/ko.contextSubMenu';
import 'ko/bindings/ko.datalist';
import 'ko/bindings/ko.datepicker';
import 'ko/bindings/ko.dateRangePicker';
import 'ko/bindings/ko.dblClick';
import 'ko/bindings/ko.delayedOverflow';
import 'ko/bindings/ko.dockable';
import 'ko/bindings/ko.documentChooser';
import 'ko/bindings/ko.documentContextPopover';
import 'ko/bindings/ko.draggableText';
import 'ko/bindings/ko.dropdown';
import 'ko/bindings/ko.dropzone';
import 'ko/bindings/ko.duration';
import 'ko/bindings/ko.ellipsis';
import 'ko/bindings/ko.fadeVisible';
import 'ko/bindings/ko.fetchMore';
import 'ko/bindings/ko.fileChooser';
import 'ko/bindings/ko.foreachVisible';
import 'ko/bindings/ko.fresherEditor';
import 'ko/bindings/ko.hdfsAutocomplete';
import 'ko/bindings/ko.hdfsTree';
import 'ko/bindings/ko.highlight';
import 'ko/bindings/ko.hiveChooser';
import 'ko/bindings/ko.html';
import 'ko/bindings/ko.hueach';
import 'ko/bindings/ko.hueCheckAll';
import 'ko/bindings/ko.hueCheckbox';
import 'ko/bindings/ko.hueChecked';
import 'ko/bindings/ko.hueLink';
import 'ko/bindings/ko.hueSpinner';
import 'ko/bindings/ko.impalaDagre';
import 'ko/bindings/ko.jHueRowSelector';
import 'ko/bindings/ko.logResizer';
import 'ko/bindings/ko.logScroller';
import 'ko/bindings/ko.medium';
import 'ko/bindings/ko.moment';
import 'ko/bindings/ko.momentFromNow';
import 'ko/bindings/ko.multiCheck';
import 'ko/bindings/ko.multiCheckForeachVisible';
import 'ko/bindings/ko.multiClick';
import 'ko/bindings/ko.multiLineEllipsis';
import 'ko/bindings/ko.numberFormat';
import 'ko/bindings/ko.numericTextInput';
import 'ko/bindings/ko.onClickOutside';
import 'ko/bindings/ko.oneClickSelect';
import 'ko/bindings/ko.parseArguments';
import 'ko/bindings/ko.publish';
import 'ko/bindings/ko.readOnlyAce';
import 'ko/bindings/ko.resizable';
import 'ko/bindings/ko.select2';
import 'ko/bindings/ko.simplesize';
import 'ko/bindings/ko.slider';
import 'ko/bindings/ko.slideVisible';
import 'ko/bindings/ko.solrChooser';
import 'ko/bindings/ko.spinEdit';
import 'ko/bindings/ko.splitDraggable';
import 'ko/bindings/ko.splitFlexDraggable';
import 'ko/bindings/ko.sqlContextPopover';
import 'ko/bindings/ko.storageContextPopover';
import 'ko/bindings/ko.stretchDown';
import 'ko/bindings/ko.tagEditor';
import 'ko/bindings/ko.tagsNotAllowed';
import 'ko/bindings/ko.templateContextMenu';
import 'ko/bindings/ko.templatePopover';
import 'ko/bindings/ko.textSqueezer';
import 'ko/bindings/ko.timepicker';
import 'ko/bindings/ko.toggle';
import 'ko/bindings/ko.toggleOverflow';
import 'ko/bindings/ko.tooltip';
import 'ko/bindings/ko.truncatedText';
import 'ko/bindings/ko.typeahead';
import 'ko/bindings/ko.verticalSlide';
import 'ko/bindings/ko.visibleOnHover';

import 'ko/components/assist/ko.assistAdlsPanel';
import 'ko/components/assist/ko.assistDbPanel';
import 'ko/components/assist/ko.assistDocumentsPanel';
import 'ko/components/assist/ko.assistGitPanel';
import 'ko/components/assist/ko.assistHBasePanel';
import 'ko/components/assist/ko.assistHdfsPanel';
import 'ko/components/assist/ko.assistPanel';
import 'ko/components/assist/ko.assistS3Panel';
import 'ko/components/contextPopover/ko.contextPopover';
import 'ko/components/simpleAceEditor/ko.simpleAceEditor';
import 'ko/components/ko.appSwitcher';
import 'ko/components/ko.catalogEntriesList';
import 'ko/components/ko.contextSelector';
import 'ko/components/ko.createDirectoryModal';
import 'ko/components/ko.deleteDocModal';
import 'ko/components/ko.dropDown';
import 'ko/components/ko.dwSidebar';
import 'ko/components/ko.executionAnalysis';
import 'ko/components/ko.favoriteApp';
import 'ko/components/ko.fieldSamples';
import 'ko/components/ko.globalSearch';
import 'ko/components/ko.historyPanel';
import 'ko/components/ko.inlineAutocomplete';
import 'ko/components/ko.jobBrowserLinks';
import 'ko/components/ko.multiClusterSidebar';
import 'ko/components/ko.navProperties';
import 'ko/components/ko.navTags';
import 'ko/components/ko.performanceGraph';
import 'ko/components/ko.pollingCatalogEntriesList';
import 'ko/components/ko.sentryPrivileges';
import 'ko/components/ko.sqlColumnsTable';

import 'ko/extenders/ko.maxLength';
import 'ko/extenders/ko.numeric';
import 'ko/extenders/ko.toJson';

import 'ko/observables/ko.observableArrayDefault';
import 'ko/observables/ko.observableDefault';

window.ko = ko;
window.ko.mapping = komapping;

export default ko;
