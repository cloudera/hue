ace.define("ace/snippets/impala",["require","exports","module"], function(require, exports, module) {
"use strict";

exports.snippetText = "snippet tbl\n\
	create table ${1:table} (\n\
		${2:columns}\n\
	);\n\
snippet s*\n\
	select * from ${1:table}\n\
";
exports.scope = "impala";

});
