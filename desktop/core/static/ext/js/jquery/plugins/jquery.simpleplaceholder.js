/* https://github.com/marcgg/Simple-Placeholder */
/******************************

Simple Placeholder

******************************/

(function($) {
	$.simplePlaceholder = {
		placeholder_class: null,

		hide_placeholder: function(){
			var $this = $(this);
			if($this.val() == $this.attr('placeholder')){
				$this.val("").removeClass($.simplePlaceholder.placeholder_class);
			}
		},

		show_placeholder: function(){
			var $this = $(this);
			if($this.val() == ""){
				$this.val($this.attr('placeholder')).addClass($.simplePlaceholder.placeholder_class);
			}
		},

		prevent_placeholder_submit: function(){
			$(this).find(".simple-placeholder").each(function(e){
				var $this = $(this);
				if($this.val() == $this.attr('placeholder')){
					$this.val('');
				}
			});
			return true;
		}
	};

	$.fn.simplePlaceholder = function(options) {
		if(document.createElement('input').placeholder == undefined){
			var config = {
				placeholder_class : 'placeholding'
			};

			if(options) $.extend(config, options);
			$.simplePlaceholder.placeholder_class = config.placeholder_class;

			this.each(function() {
				var $this = $(this);
				$this.focus($.simplePlaceholder.hide_placeholder);
				$this.blur($.simplePlaceholder.show_placeholder);
				if($this.val() == '') {
					$this.val($this.attr("placeholder"));
					$this.addClass($.simplePlaceholder.placeholder_class);
				}
				$this.addClass("simple-placeholder");
				$(this.form).submit($.simplePlaceholder.prevent_placeholder_submit);
			});
		}

		return this;
	};

})(jQuery);