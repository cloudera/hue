/**
 * ID Generator
 * Generate a new ID starting from 1.
 * - Accepts a prefix that will be prepended like so: <prefix>:<id number>
 */
var IdGeneratorModule = function($) {
  return function(options) {
    var self = this;
    $.extend(self, options);

    self.counter = 1;

    self.nextId = function() {
      return ((self.prefix) ? self.prefix + ':' : '') + self.counter++;
    };
  };
};
var IdGenerator = IdGeneratorModule($);

var IdGeneratorTable = {
  mapreduce: new IdGenerator({prefix: 'mapreduce'}),
  streaming: new IdGenerator({prefix: 'streaming'}),
  java: new IdGenerator({prefix: 'java'}),
  pig: new IdGenerator({prefix: 'pig'}),
  hive: new IdGenerator({prefix: 'hive'}),
  sqoop: new IdGenerator({prefix: 'sqoop'}),
  shell: new IdGenerator({prefix: 'shell'}),
  ssh: new IdGenerator({prefix: 'ssh'}),
  distcp: new IdGenerator({prefix: 'distcp'}),
  fs: new IdGenerator({prefix: 'fs'}),
  email: new IdGenerator({prefix: 'email'}),
  subworkflow: new IdGenerator({prefix: 'subworkflow'}),
  generic: new IdGenerator({prefix: 'generic'}),
  fork: new IdGenerator({prefix: 'fork'}),
  decision: new IdGenerator({prefix: 'decision'}),
  join: new IdGenerator({prefix: 'join'}),
  decisionend: new IdGenerator({prefix: 'decisionend'}),
  kill: new IdGenerator({prefix: 'kill'})
};