ace.define("ace/snippets/pig",["require","exports","module"], function(require, exports, module) {
"use strict";

exports.snippetText = "snippet loadpigstorage\n\
	A = LOAD '${1:what}' USING PigStorage() AS (\n\
		${2:var_name}:${3:var_type}\n\
	);\n\
snippet loadhcat\n\
	A = LOAD '${1:table}' USING org.apache.hcatalog.pig.HCatLoader();\n\
snippet loadhbase\n\
	A = LOAD 'hbase://${1:table}' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('${2:columnlist}');\n\
";
exports.scope = "pig";

});
