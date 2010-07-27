/*
---
description: Adds a tab interface (TabSwapper instance) for elements with .css-tab_ui. Matched with tab elements that are .ccs-tabs and sections that are .ccs-tab_sections.
provides: [Behavior.Tabs]
requires: [Widgets/Behavior, clientcide/TabSwapper]
script: Behavior.Tabs.js

...
*/

Behavior.addGlobalFilters({

	Tabs: function(element, methods) {
		var tabs = element.getElements(element.get('data', 'tabs-selector') || '.tabs>li');
		var sections = element.getElements(element.get('data', 'sections-selector') || '.tab_sections>li');
		if (tabs.length != sections.length || tabs.length == 0) {
			methods.error('warning; sections and sections are not of equal number. tabs: %o, sections: %o', tabs, sections);
			return;
		}
		var ts = new TabSwapper({
			tabs: tabs,
			sections: sections,
			smooth: true,
			smoothSize: true
		});
		element.store('TabSwapper', ts);
	}

});
