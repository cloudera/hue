Singleton: Depender {#Depender}
==========================

Loads dependencies from MooTools script repositories via the [Depender Sever][].

### Implements:

* [Events][], [Options][]

Depender Method: setOptions {#Depender:setOptions}
--------------------------------------------------

This is the setOptions method from [Options][]. As Depender is not a class, you must call this method directly to configure it.

### Options

* target - (*mixed*) A DOM Element or its ID - the target where the scripts are to be injected. Defaults to *document.head*.
* builder - (*string*) The url to the server app (e.g. */depender/build.php*). If you load Depender itself via the the builder, this is set automatically for you. If this is not set, Depender will not function.

### Events

* onRequire - (*function*) callback executed whenever new requirements are passed in to be loaded. Passed the object that is passed to the [require][] method.
* requirementLoaded - (*function*) callback executed when a requirement is loaded. Passed a list of the currently loaded scripts and the object that is passed to the [require][] method.
* scriptLoaded - (*function*) callback executed whenever a script loads (i.e. at the same time as requirementLoaded; this is here for compatibility with the [stand alone Depender][]). Passed an object with the following properties:
** script: the scripts loaded (a comma delimited string), 
** totalLoaded: the % loaded of total dependencies, 
** currentLoaded: the % of the current batch (so if you required a script, then immediately required, say, two more while the first was still loaded, when the first script loaded this number would be "33" (%) because there are two left; note that the server is here to do this work for you; so it's more efficient to just do one request for the three requirements if possible), 
** loaded: and an array of all the loaded scripts.

### See also

You might also consider the [stand alone Depender][], which is written entirely with JavaScript and manages all the dependencies without a server side component. It's slower, because it must request every script file individually, but has the benefit of not requiring your server to do anything other than serve up static files. Note that the stand alone version must be on the same domain as the scripts, while the server side version need not be.

Usage
-----

First, you must install the [Depender Server][]. Once installed, your application should include MooTools using the builder, specifying any scripts your app requires at startup, and also flagging that you want to include the depender client. Here are some examples:

	<!-- include all of MooTools Core plus the Depender client -->
	<script src="/depender/build.php?requireLibs=mootools-core&client=true"></script>
	<!-- OR, just include the portion of MooTools Core required to run the Depender client -->
	<script src="/depender/build.php?client=true"></script>
	<!-- Here's an example where some requirements are named specifically, in addition to the client -->
	<script src="/depender/build.php?client=true&require=Fx.Reveal,Request.JSONP,URI"></script>

Each of the above script includes above will include at least portions of MooTools Core and the *Depender.Client.js* file. After this script is loaded, you can then require additional scripts as you see fit. (See [Depender:require](#Depender:require) for details.)

Depender method: require {#Depender:require}
--------------------------------------------

Loads required scripts and executes a callback when they are ready. Note that this method works almost identically to the [require method in the stand alone Depender](/more/Core/Depender#Depender:require). It's missing the *onStep* callback (because the Depender client lets the server concatenate the response, there's only ever one step for a request), but otherwise it's identical. Consequently it should be relatively easy to switch between the two.

### Syntax

	Depender.require(options);

### Arguments

1. options - (*object*) a key/value set of options

### Options

* scripts - (*mixed*) an *array* of script names (*strings*) to load. If you have only one script required, it can be a *string*.
* sources - (*mixed*) an *array* of source names (*strings*) to load. If you have only one source required, it can be a *string*. The source name should map to the names defined in your configuration for the [Depender Server][]. So if your configuration names the MooTools Core "core" then you could list "core" in this option to load that entire library.
* callback - (*function*) callback executed when the requirements are loaded.
* compression - (*string*) to override the default configuration. i.e. "yui", "jsmin" or "none"

### Returns

* *object* - This instance of [Depender][].

Example Usage {#Depender:Example}
---------------------------------

	Depender.setOptions({
		onRequire: function(requiredScripts) {
			//this will happen every time a new requirement is requested
			$('loadingSpinner').setStyle('display', 'none');
		},
		onRequirementLoaded: function(loadedScripts) {
			//this will happen every time a requirement is returned
			//note that there may still be others loading
			$('loadingSpinner').setStyle('display', 'none');
		}
	}).include({
		//add these resources
		core: {
			scripts: "/core/Source"
		},
		more: {
			scripts: "/more/Source"
		},
		myproject: {
			scripts: "/Source"
		}
	}).require({
		scripts: ['DatePicker', 'Logger.Extended'], //array or single string for one item
		sources: 'core', //include ALL of core; this can be an array or a single string for one item
		callback: function() {
			//your startup code that needs DatePicker and Logger.Extended
			//this method will only run once, even if you require more
			//scripts later
		},
		onStep: function(data){
			//function executed every time a dependency of this specific requirement is loaded
			//data is:
			//{
			//	percent: 1-100 percentage loaded of THIS requirement
			//	scripts: array of all available scripts
			//}
		}
	});
	//later, you need to load more dependencies...
	Depender.require({
		scripts: 'Fx.Reveal', //array or single string for one item
		callback: function(){
			//if, for some reason, Fx.Reveal is available already,
			//or it is loaded before the requirements for the previous
			//require statements are met, then this function will load,
			//meaning that it may run before the methods above
			//UNLESS you set the *serial* option to *true*
			$('someElement').reveal();
		}
	});



[Events]: http://mootools.net/docs/core/Class/Class.Extras#Events
[Options]: http://mootools.net/docs/core/Class/Class.Extras#Options
[Request]: http://mootools.net/docs/core/Request/Request
[require]: #Depender:require
[Depender]: http://github.com/anutron/mootools-depender/tree/
[stand alone Depender]: http://mootools.net/docs/more/Core/Depender