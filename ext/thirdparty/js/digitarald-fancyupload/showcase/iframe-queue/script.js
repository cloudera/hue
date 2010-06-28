/**
 * FancyUpload Showcase
 *
 * @license		MIT License
 * @author		Harald Kirschner <mail [at] digitarald [dot] de>
 * @copyright	Authors
 */

window.addEvent('domready', function() {

	// reusing elements
	var list = $('file-list-0');

	var select = $('select-0');
	var selectMore = $('select-more-0');

	var alertStatus = function(message, cls) {
		new Element('div', {
			'class': cls,
			html: message,
			events: {
				click: function() {
					this.destroy();
				}
			}
		}).inject(selectMore, 'after');
	}

	// custom File class for individual files
	var File = new Class({

		Extends: Uploader.File,

		render: function() {

			this.addEvents({
				'start': this.onStart,
				'stop': this.onStop,
				'remove': this.onRemove,
				'complete': this.onComplete
			});

			this.ui = {};
			
			this.ui.element = new Element('li', {'class': 'file'});
			this.ui.title = new Element('span', {'class': 'file-title', text: this.name});

			this.ui.title.addEvent('click', this.base.start.bind(this.base));

			this.ui.cancel = new Element('a', {'class': 'file-cancel', text: 'Cancel', href: '#'});
			this.ui.cancel.addEvent('click', function() {
				this.remove();
				return false;
			}.bind(this));

			this.ui.element.adopt(
				this.ui.title,
				this.ui.cancel
			).inject(list).highlight();
			
			this.base.reposition();

			return this.parent();
		},

		onStart: function() {
			this.ui.element.addClass('file-running');
		},

		onStop: function() {
			this.remove();
		},
		
		onRemove: function() {
			// stop removes the file entry
			this.ui = this.ui.element.destroy();
		},

		onComplete: function() {
			// clean up
			this.ui.element.removeClass('file-running');
			
			this.ui.cancel = this.ui.cancel.destroy();

			new Element('input', {type: 'checkbox', 'checked': true})
				.inject(this.ui.element.highlight('#e6efc2'), 'top');

			// todo fun stuff
		}

	});

	/**
	 * Uploader instance
	 */

	var up = new Uploader({
		url: '../script.php',
		data: {
			response: 'xml'
		},
		verbose: true,
		queued: true,
		target: $('select-0'),
		instantStart: true,
		fileClass: File,
		onSelectSuccess: function() {
			if (this.fileList.length > 0) {
				select.setStyle('display', 'none');
				selectMore.setStyle('display', 'inline');
				this.target = selectMore;
				this.reposition();
			}
		},
		onFileRemove: function() {
			if (this.fileList.length == 0) {
				select.setStyle('display', 'inline');
				selectMore.setStyle('display', 'none');
				this.target = select;
				this.reposition();
			}
		}
	});

	/**
	 * Button state
	 */
	Elements.addEvents([select, selectMore], {
		click: function() {
			return false;
		},
		mouseenter: function() {
			this.addClass('hover');
			up.reposition();
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
