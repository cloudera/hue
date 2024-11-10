ace.define("ace/snippets/hive",["require","exports","module"], function(require, exports, module) {
"use strict";

exports.snippetText = "snippet tbl\n\
	create table ${1:table_name} (\n\
		${2:columns}\n\
	);\n\
snippet s*\n\
	select * from ${1:table_name}\n\
snippet showcolumns\n\
	SHOW COLUMNS (FROM|IN) table_name [(FROM|IN) db_name];\n\
snippet showcompactions\n\
	SHOW COMPACTIONS;\n\
snippet showconf\n\
	SHOW CONF <configuration_name>;\n\
snippet showcreate\n\
	SHOW CREATE TABLE ([db_name.]table_name|view_name);\n\
snippet showcurrentroles\n\
	SHOW CURRENT ROLES;\n\
snippet showdatabases\n\
	SHOW (DATABASES|SCHEMAS) [LIKE 'identifier_with_wildcards'];\n\
snippet showdblocks\n\
	SHOW LOCKS (DATABASE|SCHEMA) database_name;\n\
snippet showfunctions\n\
	SHOW FUNCTIONS \"a.*\";\n\
snippet showgrant\n\
	SHOW GRANT;\n\
snippet showindex\n\
	SHOW [FORMATTED] (INDEX|INDEXES) ON ${1:table_with_index} [(FROM|IN) ${2:db_name}];\n\
snippet showlocks\n\
	SHOW LOCKS ${1:table_name} PARTITION (${2:partition_spec}) EXTENDED;\n\
snippet showpartitions\n\
	SHOW PARTITIONS ${1:table_name} PARTITION(ds='2010-03-03', hr='12');\n\
snippet showprincipals\n\
	SHOW PRINCIPALS;\n\
snippet showrolegrant\n\
	SHOW ROLE GRANT;\n\
snippet showroles\n\
	SHOW ROLES;\n\
snippet showtableextended\n\
	SHOW TABLE EXTENDED [IN|FROM ${1:database_name}] LIKE 'identifier_with_wildcards' [PARTITION(${2:partition_spec})];\n\
snippet showtables\n\
	SHOW TABLES [IN ${1:database_name}] ['identifier_with_wildcards'];\n\
snippet showtblproperties\n\
	SHOW TBLPROPERTIES ${1:table_name};\n\
snippet showtransactions\n\
	SHOW TRANSACTIONS;\n\
";
exports.scope = "hive";

});
