function renderUseradminErrors(errors) {
  $('.control-group').removeClass('error');
  $('.errorlist').remove();
  if (errors && errors.length > 0) {
    errors.forEach(function (e, idx) {
      var $el = $('#' + e.id);
      $el.closest('.control-group').addClass('error');
      var html = '<span class="help-inline"><ul class="errorlist">';
      e.message.forEach(function (message) {
        html += '<li>' + hueUtils.escapeOutput(message) + '</li>';
      });
      html += '</ul></span>';
      $el.after(html);
      if (idx === 0) {
        $('.page-content').animate({
          scrollTop: $el.offset().top
        }, 200);
      }
    });
  }
}