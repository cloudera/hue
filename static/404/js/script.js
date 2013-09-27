$(document).ready(function () {
  soundManager.setup({
    url:'static/404/swf/',
    flashVersion:9,
    useFlashBlock:false,
    onready:function () {
      var dingSound = soundManager.createSound({
        id:'dingSound',
        url:'static/404/audio/boom.mp3'
      });

      $("html").mousedown(function () {
        dingSound.play();
        $("#bell img").attr("src", "static/404/img/ellie2.png");
      }).mouseup(function () {
            window.setTimeout(function () {
              $("#bell img").attr("src", "static/404/img/ellie1.png");
            }, 300);
          });
    },
    ontimeout:function () {
      alert('Booo.');
    }
  });
});
