Previous Version {#big-important-note}
-------------------

If you missed the link above, the previous FancyUpload for [MooTools 1.11](http://mootools.net) is still [available](/project/fancyupload/1-0/) including example code and minor updates. It is not maintained anymore.

Features {#features}
-------------------

* Select and upload multiple files
* Filter files by type in the select dialog
* A lot of possible Events to add your own behaviour
* Show and filter useful file information before the upload starts
* Limit uploads by file count, type or size
* Platform and *server independent*, just needs Flash 9+ (*> 95% penetration*)
* Graceful Degradation, since the element is replaced after the Flash is loaded successfully
* Cancel running uploads, add files during upload
* Everything is optional, documented and easy editable
* New in 2.0
	* Get the server response after upload for showing additional informations or previewing the image, etc.
	* Shows the current upload speed and the time left
	* Send additional request data via GET or POST variables
	* Set the filename for the upload request
* New in 3.0 (Completely rewritten API)
	* Fully Flash 9 and 10 compatible and an additional IFrame-based uploader
	* Browse-button can be an invisible overlay or an interactive image sprite
	* Event based Flash communication, future-proof und more stable
	* File-specific options for setting url, data and method, intelligently merged
	* Append cookies automatically to the request data
	* Relative URLs are converted automatically


Compatibility {#compatibility}
-------------------

Fully compatible with all [A-Grade Browsers][] ([Internet Explorer 6+](http://www.microsoft.com/windows/products/winfamily/ie/default.mspx),
[Opera 9](http://www.opera.com/), [Firefox 1.5+](http://www.mozilla.com/en-US/firefox/) and [Safari 3+](http://www.apple.com/safari/))
with [Adobe Flash 9 and 10](http://www.adobe.com/products/flashplayer/) player.

How to use {#how-to}
-------------------

The [available showcases](#showcases) show off documented code snippets with various use cases.

Documentation {#docs}
-------------------

### Class: Swiff.Uploader

#### Extends:

- [Swiff](http://mootools.net/docs/core/Utilities/Swiff)

#### Syntax:

	var uploader = new Swiff.Uploader([options]);

#### Arguments:

1. options - (*object*, optional) See options below.  Also inherited are all the options from [Swiff](http://mootools.net/docs/core/Utilities/Swiff).

### Returns:

* (*object|false*) - New Swiff.Uploader instance.

#### Options:

* path - (*string*: defaults to "Swiff.Uploader.swf") The relative or absolute path to the Flash movie (*Swiff.Uploader.swf*) on the server
* height: (*number*: defaults to 30) Only needed if you use *buttonImage*, otherwise its handled positioned over the *target*.
* width: (*number*: defaults to 100) Only needed if you use *buttonImage*, otherwise its handled positioned over the *target*. 
* typeFilter: (*object|string*: defaults to null) Key/value pairs are used as filters for the dialog. Possible pair would be `'Images (*.jpg, *.jpeg, *.gif, *.png)': '*.jpg; *.jpeg; *.gif; *.png'`.
* multiple: (*boolean*: defaults to true) If true, the browse-dialog allows multiple-file selection.
* queued: (*number*: defaults to 1) Maximum of currently running files. If this is false, all files are uploaded at once.
* verbose: (*boolean*: defaults to false) Debug mode, logs messages and all events from Flash during development (using *console.info*).
* target: (*element*: defaults to null) If given, the browse-element is overlayed with a transparent movie. The Events *click/mouseenter/mouseleave/disabled* are fired as events on *target*.
* zIndex: (*number*: defaults to 9999) Only used if a *target* is given, this sets the z-index for the overlay.
* buttonImage: (*string*: defaults to null) Sprite for the upload button, has to have 4 states vertically aligned: Normal, hovered, clicked and disabled. Make sure to adapt the options *width* and *height*.
* policyFile: (*string*: defaults to null) Location the cross-domain policy file. See [Flash Security.loadPolicyFile](http://livedocs.adobe.com/flash/9.0/ActionScriptLangRefV3/flash/system/Security.html#loadPolicyFile%28%29).
* url: (*string*: defaults to null) URL to the server-side script (relative URLs are changed automatically to absolute paths). 
* method: (*string*: defaults to 'post') If the method is 'get', *data* is appended as query-string to the URL. The upload will always be a POST request.
* data: (*object|string*: defaults to null) Key/data values that are sent with the upload requests.
* mergeData: (*boolean*: defaults to true) If true, the *data* option from uploader and file is merged (prioritised file data).
* fieldName: (*string*: defaults to "Filedata") The key of the uploaded file on your server, similar to *name* in a file-input. Linux Flash ignores it, better avoid it.
* fileSizeMin: (*number*: defaults to 1) Validates the minimal size of a selected file *byte*.
* fileSizeMax: (*number*: defaults to 0) Validates the maximal size of a selected file (official limit is 100 MB for FileReference, I tested up to 2 GB) 
* allowDuplicates: (*boolean*: defaults to false) Validates that no duplicate files are added.
* timeLimit: (*number*: default 30, 0 for linux) Timeout in seconds. If the upload is without progress, it is cancelled and event `complete` gets fired (with error string `timeout`). Occurs usually when the server sends an empty response (also on redirects).
* fileList: (*boolean*: defaults to false) Validates that no duplicate files are added.
* fileListMax: (*number*: defaults to 0) Validates the overall file count.
* fileListSizeMax: (*number*: defaults to 0) Validates the overall file size in *byte*.
* instantStart: (*boolean*: defaults to false) If true, the upload starts right after a successful file selection.
* appendCookieData: (*boolean|string*: defaults to false) If this is not false, the cookies of the browser are merged into the given options *data*. If a string is given, it is used as key for the *data*. 
* fileClass: (*class*: defaults to *Swiff.Uploader.File*) An instance of this class is created for every selected file.

The options *url*, *method*, *data* and *mergeData* are also available in `Swiff.Uploader.File`.
If you don't set them per-file, they default to the options in your `Swiff.Uploader` instance.
To change them during runtime, simply use `setOptions` and it does all the magic for you.

#### Events:

* load - (*function*) Function to execute when the Flash movie is initialised.
* fail - (*function*) Function to execute when the loading is prevented. First argument is the error type and can be:
	* `flash`  - Flash is not installed or the Flash version did not meet the requirements.
	* `blocked` - The user has to enable the movie manually because of Flashblock, no refresh required.
	* `empty` - The Flash movie failed to load, check if the file exists and the `path` is correct.
	* `hidden` - Adblock Plus blocks hides the movie, the user has enable it and refresh.
* start - (*function*) Function to execute when the upload starts.
* queue - (*function*) Function to execute when the queue statistics are updated.
* complete - (*function*) Function to execute when all files are uploaded (or stopped).
* browse - (*function*) Function to execute when the browse-dialog opens.
* disabledBrowse - (*function*) Function to execute when the user tries to open the browse-dialog, but the uploader is disabled.
* cancel - (*function*) Function to execute when the user closes the browse-dialog without a selection.
* select - (*function*) Function to execute when the user selected files in the dialog. Preferred events are *selectSuccess* and *selectFail*!
	1. successFiles - (*array|null*) Raw file data for successfully added files.
	2. failFiles - (*array|null*) Raw file data for invalid files that were not added.
* selectSuccess - (*function*) Function to execute when files were selected and validated successfully.
	1. successFiles - (*array|null*) Added file instances (see option *fileClass*).
* selectFail - (*function*) Function to execute when files were selected and failed validation.
	1. failFiles - (*array|null*) Dismissed file instances (see option *fileClass*).
* reposition - (*function*) Function to execute when `reposition` method is called on uploader (usually on window-resize).
* beforeStart - (*function*) Function to execute when `start` method is called on uploader.
* beforeStop - (*function*) Function to execute when `stop` method is called on uploader.
* beforeRemove - (*function*) Function to execute when `remove` method is called on uploader.
* buttonEnter - (*function*) Function to execute when the mouse enters the browse button.
* buttonLeave - (*function*) Function to execute when the mouse leave the browse button.
* buttonDown - (*function*) Function to execute when the mouse clicks the browse button. 
* buttonDisable - (*function*) Function to execute when the script disables the browse button. 
* fileStart - (*function*) Function to execute when flash initialised the upload for a file. 
* fileStop - (*function*) Function to execute when a file got stopped manually.
* fileRequeue - (*function*) Function to execute when a file got added back to the queue after being stopped or completed.
* fileOpen - (*function*) Function to execute when the file is accessed before for upload.
* fileProgress - (*function*) Function to execute when the upload reports progress.
* fileComplete - (*function*) Function to execute when a file is uploaded or failed with an error.
* fileRemove - (*function*) Function to execute when a file got removed.

Every Event starting with `file` is also called on the `Swiff.Uploader.File` class, without prepended `file`. 

#### Swiff.Uploader Method: start

Starts the upload process. Also available in `Swiff.Uploader.File`.

#### Swiff.Uploader Method: stop

Stops all running files. Also available in `Swiff.Uploader.File`.

#### Swiff.Uploader Method: remove

Remove all files from the list. Also available in `Swiff.Uploader.File`.

#### Swiff.Uploader Method: reposition

Updates the position for the movie overlay, if you use option `target`.

##### Arguments:

1. coordinates - (*object*, optional) New coordinates (*left/top/width/height*), automatically detected from the current *target*.

#### Swiff.Uploader Method: setEnabled

Enables or disables the browse button.

##### Arguments:

1. status - (*boolean*, optional) Toggles the current status if no value if provided, otherwise updates the status to the given value.

#### Swiff.Uploader Property: target

The *target* Element from the options, override it if you switch your browser button.

#### Swiff.Uploader Property: uploading

The number of running uploads.

#### Swiff.Uploader Property: size

The overall size of all files in the list in *byte*.

#### Swiff.Uploader Property: bytesLoaded

The overall loaded size of running and completed files in the list in *byte*. 

#### Swiff.Uploader Property: bytesLoaded

The overall loaded percentage of running and completed files in the list.

#### Swiff.Uploader Property: rate

The overall rate of running files in the list in *bytes/second*.

### Class: Swiff.Uploader.File

Mirrors several methods and events from the documentation above. Custom
file classes usually extends it and are given to `Swiff.Uploader` via the
*fileClass* option.

FAQ, Tips, Tricks, Quirks {#faq}
-------------------

How do I access the uploaded files?

:	Every upload, even with multiple files, results in one request. Access the uploaded file via

	- PHP: $_FILES['Filedata']
	- Perl: $main::cgi->param('Filedata'); ... [example](http://forum.mootools.net/viewtopic.php?id=2726#post-14326)
	- Rails: params[:Filedata] ... [example](http://forum.mootools.net/viewtopic.php?id=2726&p=6#post-22330)
	- ASP: [Fancy Upload and Classic ASP](http://bennewton.us/2007/07/22/fancy-upload-and-classic-asp/)
	
	*Filedata* is the default value for the option `fieldName`, so you can change it. The submitted `content-type` header is always `application/octet-stream`, so don't trust it when you validate the file.

Flash-request forgets cookies and session ID

:	See option `appendCookieData`. Flash FileReference is not an intelligent upload class, the request will not have the browser cookies, Flash saves his own cookies. When you have sessions, append them as get-data to the the URL (e.g. "upload.php?SESSID=123456789abcdef"). Of course your session-name can be different.

Are cross-domain uploads possible?

:	> For uploading and downloading operations, a SWF file can access files only within its own domain, including any domains that are specified by a cross-domain policy file. If the SWF that is initiating the upload or download doesn't come from the same domain as the file server, you must put a policy file on the file server.
	[More on security and link to cross-domain policies](http://livedocs.adobe.com/flash/8/main/wwhelp/wwhimpl/common/html/wwhelp.htm?context=LiveDocs_Parts&file=00001590.html)

FancyUpload does not load, the input element gets not replaced

:	Check in [Firebug](http://www.getfirebug.com/) in *Net/Flash* that the SWF file loads correctly. If not double check your given options.

Uploads fail with 404 error code

:	Check your URL and better *use an absolute upload URL*.
	
	IE takes the upload url *relative* to the swf, all other browsers relative to the html/current file. So the best solution is an absolute path for the option url or rather the form action. *If you have problems with failed upload and 404 error codes, try an absolute url*, in your form-action or url option when creating your FancyUpload instance.

Uploads fail with 406/403 error

:	From the swfupload documentation (it applies to all Flash scripts depending on `FileReference`):
	
	> If you are using Apache with mod_security this will not work, you need to put the following in your .htaccess file to disable mod_security:
	> 
	> 	SecFilterEngine Off
	> 	SecFilterScanPOST Off
	>
	> Disabling mod_security isn't allowed on some shared hosts, and only do this if you know what you are doing.
	> This is due to a bug in the way that flash sends the headers back to the server according to the Flash 8 documentation

Uploads fail with 403/500 error

:	Check your server config, there must be something wrong. Also see 404, double check the upload URL.

Uploads and Basic Authentication

:	Flash does not care about authenticated Browsers. Firefix/Win/Flash 9 can handle it, IE too, Mac can't handle it.
	Anyways, Flash will ask for its own access username and password.

Requirements {#requirements}
-------------------

**It does not depend on any server-side architecture or language.**

### MooTools JavaScript Framework 1.2

You can include MooTools via [Google AJAX Libraries API](http://code.google.com/apis/ajaxlibs/documentation/#mootools),
follow the link for more information and why it can be good for your site.

#### [Required MooTools Core components](http://mootools.net/core/):

- Element.Events
- Element.Dimensions
- Fx.Tween
- Fx.Transitions 
- Selectors
- JSON
- Swiff
- DomReady (_facultative_)

**Don't use compressed code during development to simplify debugging.**

Download {#download}
-------------------

Complete ActionScript/JavaScript source, documentation and showcases are available at [github](http://github.com/), in my [fancyupload repository](https://github.com/digitarald/digitarald-fancyupload).

### Packages

* [**Working FancyUpload Installation**](http://cloud.github.com/downloads/digitarald/digitarald-fancyupload/working-fancyupload-photoqueue.zip) - The package that everybody waited for, a working FancyUpload to unpack and start play.
* [**Sources including Showcases**](http://cloud.github.com/downloads/digitarald/digitarald-fancyupload/fancyupload-complete-source.zip) - The source and all showcases from this page in one package, the package for *web craftsmen* ;).

### Single Files

* [Swiff.Uploader.js](/project/fancyupload/3-0/source/Swiff.Uploader.js) - Flash based uploader, energizer for all possible upload interfaces
* [Swiff.Uploader.swf](/project/fancyupload/3-0/source/Swiff.Uploader.swf) - The movie used by the uploader class. *Use right-click/save-as!*
* [FancyUpload2.js](/project/fancyupload/3-0/source/FancyUpload2.js) - The famous & fancy interface, converted to the new 3.0 API.
* [Uploader.js](/project/fancyupload/3-0/source/Swiff.Uploader.js) - IFrame based class with the same API, but without progress.
* [Fx.ProgressBar.js](/project/fancyupload/3-0/source/Fx.ProgressBar.js) - Class to create and animate progress-bars.
* The [images](http://github.com/digitarald/digitarald-fancyupload/tree/master/assets) from the [showcases](#showcases) are also [downloadable](http://github.com/digitarald/digitarald-fancyupload/tree/master/assets).

**You** can contribute by reporting problems and bugs in the [issue tracker](http://github.com/digitarald/digitarald-fancyupload/issues) on github or in the [support forum](/forums/) to discuss it.

References {#references}
-------------------

- [MooTools Forum](http://forum.mootools.net): ["Fancy Upload by digitarald"](http://forum.mootools.net/viewtopic.php?id=2726) with 15 pages
- [Jason: Flash Upload Progress for Rails with FancyUpload for mootools](http://edseek.com/archives/2007/07/15/flash-upload-progress-for-rails-with-fancyupload-for-mootools/)
- [FileReference (flash.net.FileReference) - Version 9](http://livedocs.adobe.com/flash/9.0/ActionScriptLangRefV3/flash/net/FileReference.html)
- [Ben Newton: Fancy Upload and Classic ASP](http://bennewton.us/2007/07/22/fancy-upload-and-classic-asp/)
