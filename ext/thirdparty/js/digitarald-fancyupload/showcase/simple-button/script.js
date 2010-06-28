/**
 * FancyUpload Showcase
 *
 * @license		MIT License
 * @author		Harald Kirschner <mail [at] digitarald [dot] de>
 * @copyright	Authors
 */

window.addEvent('domready', function() {

	var link = $('select-0');

	var linkIdle = link.get('html');

	function linkUpdate() {
		var l = swf.fileList.length;
		if (!l) {
			link.title = null;
			link.set('html', linkIdle);
			return;
		}

		var rate = Swiff.Uploader.formatUnit(swf.rate, 'bps');
		var size = Swiff.Uploader.formatUnit(swf.size, 'b');
		var bytesLoaded = Swiff.Uploader.formatUnit(swf.bytesLoaded, 'b');

		link.set('html', l + ' Upload' + ((l != 1) ? 's' : '') + ' (' + swf.percentLoaded + '%)');
		link.title = bytesLoaded + ' of ' +  rate + ' with ' + bytesLoaded;
	}

	/**
	 * Uploader instance
	 */

	var swf = new Swiff.Uploader({
		path: '../../source/Swiff.Uploader.swf',
		url: '../script.php',
		verbose: true,
		queued: false,
		target: link,
		instantStart: true,
		onSelectSuccess: function() {
			if (Browser.Platform.linux) window.alert('Warning: Due to a misbehaviour of Adobe Flash Player on Linux,\nthe browser will probably freeze during the upload process.\nSince you are prepared now, the upload will start right away ...');
		},
		onQueue: linkUpdate,
		onFileComplete: function(file) {
			if (file.response.error) alert('Upload failed, please try again (' + file.response.error + ' ' + file.response.code + ').');
			console.log('Server response:', file.response);
			file.remove();
		}
	});

	/**
	 * Button state
	 */
	link.addEvents({
		click: function() {
			return false;
		},
		mouseenter: function() {
			this.addClass('hover');
			swf.reposition();
		},
		mouseleave: function() {
			this.removeClass('hover');
			this.blur();
		},
		mousedown: function() {
			this.focus();
		}
	});

});
