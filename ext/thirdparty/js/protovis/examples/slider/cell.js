/** Depends on globals: rule, w, h, mode. */
function cell() {
  var d = pv.range(h).map(function() {
          return pv.range(w).map(function() { return 0; });
        }),
      r = pv.range(8).map(function(i) {
          return rule >> i & 1;
        });
  if (start == "point") {
    d[0][w >> 1] = 1;
  } else {
    for (var x = 0; x < w; x++) {
      d[0][x] = cell.random(x);
    }
  }
  for (var y = 1; y < h; y++) {
    var p = d[y - 1], c = d[y];
    for (var x = 0; x < w; x++) {
      c[x] = r[p[x - 1] << 2 | p[x] << 1 | p[x + 1]];
    }
  }
  return d;
}

cell.$random = {};

/** Caches random output to make exploration deterministic. */
cell.random = function(i) {
  return i in cell.$random ? cell.$random[i]
      : (cell.$random[i] = Math.random() < .5 ? 0 : 1);
};
