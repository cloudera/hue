/*
---
description: Automatically turns multi select inputs into an instance of ART.SideBySideSelect.
provides: [Behavior.SideBySideSelect]
requires: [Widgets/Behavior, /ART.SideBySideSelect]
script: Behavior.SideBySideSelect.js
...
*/

Behavior.addGlobalFilters({

	SideBySideSelect: function(element, events) {
		if (element.get('tag') != 'select' && element.get('multiple')){
			dbug.warn("Side_by_side_select element %o does not contain multiple=true.", element);
			return;
		}
		var parent = element.get('parentWidget');
		var sbs = new ART.SideBySideSelect(element);

		//inject our new widget into the DOM and the widget tree (if there is a parent widget)
		if (parent) sbs.inject(parent, element, 'after');
		else widget.inject(element, element, 'after');

		this.markForCleanup(element, function(){
			sbs.destroy();
		});
	}

});