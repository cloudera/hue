HUE-7738 [editor] Add function listing in autocomplete API

This is a first pass before v1. See the documentation for usage.

Note:
- only Hive can provide detailed function info
- by default Hive only provides function names

Still need to add:

Both:
- add other fields when possible, e.g. return type, signature, binary
type, is persistent
- show aggregate functions;
- show analytic functions;

Hive:
- DESCRIBE FUNCTION EXTENDED trunc

Impala
- include _impala_builtins per default
- include the active database

Other SQL
- TODO: either errors or try to return columns
- MySql e.g. show function status (or better check with SqlAlchemy)
