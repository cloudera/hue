// Put this file in the parent directory of the runner folder. Also rename the file to Configuration.js

(function(context){

var Configuration = context.Configuration = {};

// Runner name
Configuration.name = 'Hue';


// Presets - combine the sets and the source to a preset to easily run a test
Configuration.presets = {
	
	'PartialUpdate': {
		sets: ['PartialUpdate'],
		source: ['PartialUpdate']
	}
	
};

// An object with default presets
Configuration.defaultPresets = {
	browser: 'PartialUpdate',
	nodejs: 'PartialUpdate',
	jstd: 'PartialUpdate'
};


/*
 * An object with sets. Each item in the object should have an path key', '
 * that specifies where the spec files are and an array with all the files
 * without the .js extension relative to the given path
 */
Configuration.sets = {

	'PartialUpdate': {
		path: 'hue/',
		files: ['PartialUpdate']
	}

};


/*
 * An object with the source files. Each item should have an path key,
 * that specifies where the source files are and an array with all the files
 * without the .js extension relative to the given path
 */
Configuration.source = {

	'PartialUpdate': {
		path: '../',
		files: [
			'clientcide/Source/Core/dbug',
			'core/Source/Core/Core',
			'core/Source/Native/Array',
			'core/Source/Native/String',
			'core/Source/Native/Function',
			'core/Source/Native/Number',
			'core/Source/Native/Hash',
			'core/Source/Class/Class',
			'core/Source/Class/Class.Extras',
			'core/Source/Core/Browser',
			'core/Source/Element/Element',
			'core/Source/Element/Element.Dimensions',
			'core/Source/Utilities/Selectors',
			'more/Source/Core/More',
			'more/Source/Element/Elements.From',
			'more/Source/Native/Array.Extras',
			'../../../desktop/core/static/js/Source/JFrameRenderers/PartialUpdate'
		]
	}

};

})(typeof exports != 'undefined' ? exports : this);
