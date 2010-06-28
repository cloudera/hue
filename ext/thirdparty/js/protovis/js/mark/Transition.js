/**
 * TODO
 *
 * @param [ms] {number} optional time interval during which to interpolate
 * smoothly to new display.
 */
pv.Mark.prototype.render = function(ms) {

  /* */
  if (this.scene) stop(this.scene);

  /* */
  this.bind();

  /* */
  if (ms) {

    /* */
    var after = this.scene, before = clone(after);
    this.build();
    var delta = compare(before, after);

    /* */
    var t = 0;
    for (var i = 0; i < delta.length; i++) {
      delta[i](t);
    }

    /* */
    after.timer = setInterval(function() {
        t = Math.min(1, t + 0.08);
        for (var i = 0; i < delta.length; i++) {
          delta[i](t);
        }
        pv.Scene.updateAll(after);
        if (t == 1) stop(after);
      }, 20);

  } else {
    this.build();
    pv.Scene.updateAll(this.scene);
  }
};

/** TODO */
function stop(scene) {
  if (scene.timer) {
    clearInterval(scene.timer);
    delete scene.timer;
  } else {
    for (var i = 0; i < scene.length; i++) {
      if (scene[i].children) {
        for (var j = 0; j < scene[i].children.length; j++) {
          stop(scene[i].children[j]);
        }
      }
    }
  }
}

/** TODO */
function clone(scene) {
  var c = new Array(scene.length);
  for (var i = 0; i < scene.length; i++) {
    var o = c[i] = {}, s = scene[i];
    for (var property in scene.mark.properties) {
      o[property] = s[property];
    }
    if (s.children) {
      o.children = new Array(s.children.length);
      for (var j = 0; j < s.children.length; j++) {
        o.children[j] = clone(s.children[j]);
      }
    }
  }
  return c;
}

/** TODO */
function ramp(c1, c2, s, property) {
  var ramp = pv.ramp(c1, c2);
  return function(t) { s[property] = ramp.value(t); };
}

/** TODO */
function compare(before, after) {
  var delta = [];
  for (var i = 0; i < before.length; i++) { // TODO length mismatch
    var s1 = before[i], s2 = after[i];
    for (var property in s1) {
      var p1 = s1[property], p2 = s2[property];
      if ((p1 == undefined) || (p2 == undefined)) continue;
      switch (property) { // TODO more types, more generic?
      case "textStyle":
      case "strokeStyle":
      case "fillStyle": {
        var c1 = pv.color(p1), c2 = pv.color(p2);
        if ((c1.color != c2.color) || (c1.opacity != c2.opacity)) {
          delta.push(ramp(c1, c2, s2, property));
        }
        break;
      }
      }
    }
    if (s1.children) {
      for (var j = 0; j < s1.children.length; j++) { // TODO length mismatch
        Array.prototype.push.apply(delta, compare(s1.children[j], s2.children[j]));
      }
    }
  }
  return delta;
}
