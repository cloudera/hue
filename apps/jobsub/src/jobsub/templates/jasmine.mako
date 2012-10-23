<%inherit file="common_jasmine.mako"/>

<%block name="specs">
    <script src="/static/ext/js/moment.min.js"></script>
    <script src="static/js/jobsub.ko.js"></script>
    <script src="static/jasmine/jobsubSpec.js"></script>
</%block>


<%block name="fixtures">
  <div style="display:none">
    <button class="btn" data-bind="click: submitDesign, enable: selectedDesigns().length == 1 && selectedDesigns()[0].canSubmit"><i class="icon-play"></i> Submit</button>
    <button class="btn" data-bind="click: editDesign, enable: selectedDesigns().length == 1 && selectedDesigns()[0].canSubmit"><i class="icon-pencil"></i> Edit</button>
    <button class="btn" data-bind="click: deleteDesign, enable: selectedDesigns().length == 1 && selectedDesigns()[0].canDelete"><i class="icon-trash"></i> Delete</button>
    <button class="btn" data-bind="click: cloneDesign, enable: selectedDesigns().length == 1"><i class="icon-share"></i> Clone</button>

    <div id="selectAll" data-bind="click: selectAll, css: {hueCheckbox: true, 'icon-ok': allSelected}"></div>
    <table id="designTable" class="table table-condensed datatables">
      <tbody id="designs" data-bind="template: {name: 'designTemplate', foreach: designs}">

      </tbody>
    </table>
    <script id="designTemplate" type="text/html">
      <tr style="cursor: pointer">
        <td class="center" data-bind="click: handleSelect" style="cursor: default">
          <div data-bind="visible: name != '..', css: {hueCheckbox: name != '..', 'icon-ok': selected}"></div>
        </td>
        <td data-bind="click: $root.editDesign, text: owner"></td>
        <td data-bind="click: $root.editDesign, text: name"></td>
        <td data-bind="click: $root.editDesign, text: type"></td>
        <td data-bind="click: $root.editDesign, text: description"></td>
        <td data-bind="click: $root.editDesign, text: lastModified, attr: { 'data-sort-value': lastModifiedMillis }" style="white-space: nowrap;"></td>
      </tr>
    </script>
  </div>
</%block>