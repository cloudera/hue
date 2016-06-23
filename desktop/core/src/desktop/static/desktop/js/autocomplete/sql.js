// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

define(function(require){
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,16],$V1=[1,17],$V2=[1,8],$V3=[1,26],$V4=[1,27],$V5=[1,28],$V6=[1,19],$V7=[1,22],$V8=[1,23],$V9=[1,15],$Va=[12,13],$Vb=[4,7,12,13,42,44,79,125,131,134,136,140,144,145,146,147,148,160,163,164,187,190],$Vc=[1,38],$Vd=[1,37],$Ve=[1,42],$Vf=[1,45],$Vg=[1,52],$Vh=[1,53],$Vi=[4,7,30,31],$Vj=[1,68],$Vk=[4,7,32,33],$Vl=[1,73],$Vm=[2,4,7,12,13,27,42,79,125,131,160,163,164,176,183,187,190],$Vn=[2,4],$Vo=[4,12,13,36],$Vp=[2,247],$Vq=[1,78],$Vr=[1,79],$Vs=[1,80],$Vt=[4,12,13,36,42,131,160,163,164,187,190],$Vu=[7,12,13],$Vv=[4,7,12,13,65,176],$Vw=[4,7,12,13,176],$Vx=[2,73],$Vy=[1,91],$Vz=[12,13,125],$VA=[1,98],$VB=[4,7,12,13,42,125,131,160,163,164],$VC=[4,5,7,12,13,42,44,79,102,103,104,125,131,134,136,140,144,145,146,147,148,160,163,164,187,190],$VD=[2,213],$VE=[1,102],$VF=[1,104],$VG=[1,109],$VH=[2,248],$VI=[1,113],$VJ=[5,7,159,165,176],$VK=[2,131],$VL=[2,132],$VM=[4,7,12,13,36,42,131,160,163,164,187,190],$VN=[1,118],$VO=[1,137],$VP=[1,138],$VQ=[1,139],$VR=[1,140],$VS=[1,141],$VT=[1,154],$VU=[4,12,13,42,131],$VV=[1,168],$VW=[2,4,7,12,13,36,42,125,131,160,163,164,187,190],$VX=[1,176],$VY=[2,99],$VZ=[4,7,12,13,57,58],$V_=[4,12,13,42,131,160,163,164,187,190],$V$=[4,12,13,131,160,163,164],$V01=[7,159],$V11=[2,194],$V21=[1,193],$V31=[1,205],$V41=[1,198],$V51=[1,203],$V61=[1,204],$V71=[4,12,13,42,131,160,163,164],$V81=[1,214],$V91=[1,216],$Va1=[1,218],$Vb1=[4,7,12,13,42,79,102,103,104,125,131,160,163,164],$Vc1=[2,4,7,12,13,26,76,94,95,96,97],$Vd1=[1,240],$Ve1=[1,241],$Vf1=[42,79],$Vg1=[1,266],$Vh1=[1,267],$Vi1=[1,268],$Vj1=[1,270],$Vk1=[4,12,13,42,79,131,134,160,163,164,187,190],$Vl1=[4,12,13,42,79,131,134,136,160,163,164,187,190],$Vm1=[4,12,13,42,44,79,131,134,136,140,144,145,146,147,148,160,163,164,187,190],$Vn1=[1,288],$Vo1=[1,292],$Vp1=[4,12,13,42,131,160,163,164,183,187,190],$Vq1=[2,4,76,94,95,96,97],$Vr1=[4,5,7,71,78,150,151,159],$Vs1=[4,12,13,42,44,79,102,103,104,131,134,136,140,144,145,146,147,148,160,163,164,187,190],$Vt1=[1,352],$Vu1=[1,358],$Vv1=[1,359],$Vw1=[4,7,186];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"PartialIdentifierOrCursor":6,"REGULAR_IDENTIFIER":7,"PartialIdentifierOrPartialCursor":8,"InitResults":9,"Sql":10,"SqlStatements":11,";":12,"EOF":13,"SqlStatement":14,"DataManipulation":15,"DataDefinition":16,"QueryExpression":17,"UseStatement":18,"USE":19,"LoadStatement":20,"UpdateStatement":21,"HiveOrImpalaLoad":22,"HiveOrImpalaData":23,"HiveOrImpalaInpath":24,"HdfsPath":25,"INTO":26,"TABLE":27,"<hive>LOAD":28,"<impala>LOAD":29,"<hive>DATA":30,"<impala>DATA":31,"<hive>INPATH":32,"<impala>INPATH":33,"UPDATE":34,"TargetTable":35,"SET":36,"SetClauseList":37,"WhereClause":38,"TableName":39,"LocalOrSchemaQualifiedName":40,"SetClause":41,",":42,"SetTarget":43,"=":44,"UpdateSource":45,"ValueExpression":46,"BooleanValueExpression":47,"CreateStatement":48,"DropStatement":49,"TableDefinition":50,"DatabaseDefinition":51,"CREATE":52,"DROP":53,"DropDatabaseStatement":54,"DropTableStatement":55,"OptionalHiveCascadeOrRestrict":56,"<hive>CASCADE":57,"<hive>RESTRICT":58,"DatabaseOrSchema":59,"OptionalIfExists":60,"RegularOrBacktickedIdentifier":61,"TablePrimary":62,"DATABASE":63,"SCHEMA":64,"IF":65,"EXISTS":66,"OptionalIfNotExists":67,"NOT":68,"Comment":69,"HiveOrImpalaComment":70,"SINGLE_QUOTE":71,"VALUE":72,"HivePropertyAssignmentList":73,"HivePropertyAssignment":74,"HiveDbProperties":75,"<hive>WITH":76,"DBPROPERTIES":77,"(":78,")":79,"DatabaseDefinitionOptionals":80,"DatabaseDefinitionOptional":81,"HdfsLocation":82,"CleanUpDatabaseConditions":83,"TableScope":84,"TableElementList":85,"<hive>EXTERNAL":86,"<impala>EXTERNAL":87,"TableElements":88,"TableElement":89,"ColumnDefinition":90,"PrimitiveType":91,"ColumnDefinitionError":92,"HiveOrImpalaLocation":93,"<hive>LOCATION":94,"<impala>LOCATION":95,"<hive>COMMENT":96,"<impala>COMMENT":97,"HDFS_START_QUOTE":98,"HDFS_PATH":99,"HDFS_END_QUOTE":100,"AnyDot":101,".":102,"<impala>.":103,"<hive>.":104,"TINYINT":105,"SMALLINT":106,"INT":107,"BIGINT":108,"BOOLEAN":109,"FLOAT":110,"DOUBLE":111,"STRING":112,"DECIMAL":113,"CHAR":114,"VARCHAR":115,"TIMESTAMP":116,"<hive>BINARY":117,"<hive>DATE":118,"SELECT":119,"CleanUpSelectConditions":120,"SelectList":121,"TableExpression":122,"FromClause":123,"SelectConditionList":124,"FROM":125,"TableReferenceList":126,"SelectCondition":127,"GroupByClause":128,"OrderByClause":129,"LimitClause":130,"WHERE":131,"SearchCondition":132,"BooleanTerm":133,"OR":134,"BooleanFactor":135,"AND":136,"BooleanTest":137,"Predicate":138,"CompOp":139,"IS":140,"TruthValue":141,"ParenthesizedBooleanValueExpression":142,"NonParenthesizedValueExpressionPrimary":143,"<>":144,"<=":145,">=":146,"<":147,">":148,"SignedInteger":149,"UNSIGNED_INTEGER":150,"-":151,"StringValue":152,"ColumnReference":153,"BasicIdentifierChain":154,"InitIdentifierChain":155,"IdentifierChain":156,"Identifier":157,"ColumnIdentifier":158,"\"":159,"GROUP":160,"BY":161,"ColumnList":162,"ORDER":163,"LIMIT":164,"*":165,"DerivedColumn":166,"[":167,"DOUBLE_QUOTE":168,"]":169,"DerivedColumnChain":170,"TableReference":171,"TablePrimaryOrJoinedTable":172,"LateralViewDefinition":173,"JoinedTable":174,"LateralViews":175,"BACKTICK":176,"RegularOrBackTickedSchemaQualifiedName":177,"PARTIAL_VALUE":178,"userDefinedTableGeneratingFunction":179,"<hive>explode":180,"<hive>posexplode":181,"LateralView":182,"<hive>LATERAL":183,"VIEW":184,"LateralViewColumnAliases":185,"<hive>AS":186,"JOIN":187,"JoinSpecification":188,"JoinCondition":189,"ON":190,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",7:"REGULAR_IDENTIFIER",12:";",13:"EOF",19:"USE",26:"INTO",27:"TABLE",28:"<hive>LOAD",29:"<impala>LOAD",30:"<hive>DATA",31:"<impala>DATA",32:"<hive>INPATH",33:"<impala>INPATH",34:"UPDATE",36:"SET",42:",",44:"=",52:"CREATE",53:"DROP",57:"<hive>CASCADE",58:"<hive>RESTRICT",63:"DATABASE",64:"SCHEMA",65:"IF",66:"EXISTS",68:"NOT",71:"SINGLE_QUOTE",72:"VALUE",76:"<hive>WITH",77:"DBPROPERTIES",78:"(",79:")",86:"<hive>EXTERNAL",87:"<impala>EXTERNAL",94:"<hive>LOCATION",95:"<impala>LOCATION",96:"<hive>COMMENT",97:"<impala>COMMENT",98:"HDFS_START_QUOTE",99:"HDFS_PATH",100:"HDFS_END_QUOTE",102:".",103:"<impala>.",104:"<hive>.",105:"TINYINT",106:"SMALLINT",107:"INT",108:"BIGINT",109:"BOOLEAN",110:"FLOAT",111:"DOUBLE",112:"STRING",113:"DECIMAL",114:"CHAR",115:"VARCHAR",116:"TIMESTAMP",117:"<hive>BINARY",118:"<hive>DATE",119:"SELECT",125:"FROM",131:"WHERE",134:"OR",136:"AND",140:"IS",141:"TruthValue",144:"<>",145:"<=",146:">=",147:"<",148:">",150:"UNSIGNED_INTEGER",151:"-",159:"\"",160:"GROUP",161:"BY",163:"ORDER",164:"LIMIT",165:"*",167:"[",168:"DOUBLE_QUOTE",169:"]",176:"BACKTICK",178:"PARTIAL_VALUE",180:"<hive>explode",181:"<hive>posexplode",183:"<hive>LATERAL",184:"VIEW",186:"<hive>AS",187:"JOIN",190:"ON"},
productions_: [0,[3,1],[3,1],[6,2],[6,1],[8,2],[8,1],[9,0],[10,4],[10,3],[11,1],[11,3],[14,1],[14,1],[14,1],[14,3],[14,2],[14,1],[18,3],[18,2],[18,2],[15,1],[15,1],[20,7],[20,6],[20,5],[20,4],[20,3],[20,2],[22,1],[22,1],[23,1],[23,1],[24,1],[24,1],[21,5],[21,5],[21,4],[21,3],[21,2],[21,2],[35,1],[39,1],[37,1],[37,3],[41,3],[41,2],[41,1],[43,1],[45,1],[46,1],[16,1],[16,1],[16,1],[48,1],[48,1],[48,2],[49,2],[49,1],[49,1],[56,0],[56,1],[56,1],[54,3],[54,4],[54,5],[54,5],[55,3],[55,4],[55,4],[55,5],[59,1],[59,1],[60,0],[60,2],[60,2],[67,0],[67,2],[67,3],[67,3],[67,1],[69,2],[69,3],[69,4],[73,1],[73,3],[74,3],[74,7],[75,5],[75,2],[75,2],[80,1],[80,2],[80,3],[81,1],[81,1],[81,1],[83,0],[51,3],[51,4],[51,5],[51,7],[51,7],[50,6],[50,5],[50,4],[50,3],[50,6],[50,4],[84,1],[84,1],[85,3],[88,1],[88,3],[89,1],[90,2],[90,2],[90,4],[92,0],[82,2],[93,1],[93,1],[70,1],[70,1],[25,3],[25,5],[25,4],[25,3],[25,3],[25,2],[101,1],[101,1],[101,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[91,1],[17,4],[17,3],[122,1],[122,2],[120,0],[123,2],[123,2],[124,1],[124,2],[127,1],[127,1],[127,1],[127,1],[127,1],[38,2],[38,2],[132,1],[47,1],[47,3],[133,1],[133,3],[133,3],[135,2],[135,1],[137,1],[137,3],[137,3],[137,3],[137,4],[138,1],[138,1],[139,1],[139,1],[139,1],[139,1],[139,1],[139,1],[142,3],[142,2],[149,1],[149,2],[152,3],[143,1],[143,1],[143,1],[153,1],[154,2],[155,0],[156,1],[156,3],[156,3],[157,1],[157,2],[157,3],[128,3],[128,2],[129,3],[129,2],[130,2],[130,2],[121,1],[121,2],[121,2],[121,1],[162,1],[162,3],[158,1],[158,6],[158,4],[158,3],[166,1],[166,3],[166,2],[166,3],[166,3],[166,5],[166,5],[166,1],[170,1],[170,3],[126,1],[126,3],[171,1],[172,1],[172,1],[172,1],[173,2],[173,3],[62,1],[61,1],[61,3],[177,3],[177,5],[177,5],[177,7],[177,6],[177,3],[177,5],[177,2],[177,3],[40,1],[40,2],[40,1],[40,2],[179,4],[179,4],[179,4],[179,4],[175,1],[175,2],[182,5],[182,4],[182,5],[182,4],[182,3],[182,2],[185,2],[185,6],[174,4],[174,4],[174,3],[188,1],[189,2]],
performAction: function anonymous(yytext, yyleng, yylineno, yy, yystate /* action[1] */, $$ /* vstack */, _$ /* lstack */) {
/* this == yyval */

var $0 = $$.length - 1;
switch (yystate) {
case 7:

     parser.yy.result = {};
     parser.yy.cursorFound = false;

     // TODO: Move these below before token or use this.$ instead
     delete parser.yy.latestTablePrimaries;
     delete parser.yy.identifierChain;
     delete parser.yy.derivedColumnChain;
     delete parser.yy.currentViews;
     delete parser.yy.keepColumns;

     parser.parseError = function (message, error) {
       if (typeof parser.yy.result.suggestColumns !== 'undefined') {
         linkTablePrimaries();
       }
       prioritizeSuggestions();
       parser.yy.result.error = error;
       return message;
     }
   
break;
case 8: case 9:

     prioritizeSuggestions();
     return parser.yy.result;
   
break;
case 16: case 17:

     suggestDdlAndDmlKeywords();
   
break;
case 18: case 20:

     suggestDatabases();
   
break;
case 19:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
case 24:

     suggestKeywords([ 'TABLE' ]);
   
break;
case 25:

     suggestKeywords([ 'INTO' ]);
   
break;
case 27:

     suggestKeywords([ 'INPATH' ]);
   
break;
case 28:

     suggestKeywords([ 'DATA' ]);
   
break;
case 35: case 37: case 147:

     linkTablePrimaries();
   
break;
case 36:

     suggestKeywords([ 'WHERE' ]);
   
break;
case 38:

     suggestKeywords([ 'SET' ]);
   
break;
case 40: case 153:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 42:

     // TODO: Replace with TablePrimary?
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 46:

     suggestKeywords([ '=' ]);
   
break;
case 47: case 162: case 199:

     suggestColumns();
   
break;
case 56:

     if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
       suggestKeywords(['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
   
break;
case 57:

     if (parser.yy.dialect === 'hive') {
       suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'MACRO', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
     } else if (parser.yy.dialect === 'impala') {
       suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
     } else {
       suggestKeywords(['ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   
break;
case 64:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   
break;
case 65:

     if (parser.yy.dialect === 'hive') {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   
break;
case 68:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 69:

     if (!$$[$0-1] && !$$[$0].partial) {
       suggestKeywords(['IF EXISTS']);
     }
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       } else if ($$[$0-3].identifierChain.length === 0) {
         suggestTables();
         suggestDatabases({ appendDot: true });
       }
     }
   
break;
case 70:

     if (parser.yy.dialect === 'hive') {
       suggestKeywords(['PURGE']);
     }
   
break;
case 73:
 this.$ = false 
break;
case 74: case 78:

     suggestKeywords(['EXISTS']);
   
break;
case 77:

     suggestKeywords(['NOT EXISTS']);
   
break;
case 80:

     suggestKeywords(['IF NOT EXISTS']);
   
break;
case 90:

     suggestKeywords(['DBPROPERTIES']);
   
break;
case 94:

     parser.yy.afterComment = true;
   
break;
case 95:

     parser.yy.afterHdfsLocation = true;
   
break;
case 96:

     parser.yy.afterHiveDbProperties = true;
   
break;
case 97:

     delete parser.yy.afterComment;
     delete parser.yy.afterHdfsLocation;
     delete parser.yy.afterHiveDbProperties;
   
break;
case 100:

     if (parser.yy.dialect === 'hive') {
       suggestKeywords(['COMMENT', 'LOCATION', 'WITH DBPROPERTIES']);
     } else if (parser.yy.dialect === 'impala') {
       suggestKeywords(['COMMENT', 'LOCATION']);
     }
   
break;
case 102:

     var keywords = [];
     if (! parser.yy.afterComment) {
       keywords.push('COMMENT');
     }
     if (! parser.yy.afterHdfsLocation) {
       keywords.push('LOCATION');
     }
     if (! parser.yy.afterHiveDbProperties && parser.yy.dialect === 'hive') {
       keywords.push('WITH DBPROPERTIES');
     }
     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   
break;
case 104: case 105: case 106:

      if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
        suggestKeywords(['EXTERNAL']);
      }
    
break;
case 107:

     if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
       suggestKeywords(['LOCATION']);
     }
   
break;
case 116: case 118:

     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   
break;
case 125:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 126:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 127:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 128:

     suggestHdfs({ path: '' });
   
break;
case 129:

      suggestHdfs({ path: '' });
    
break;
case 151:

     delete parser.yy.afterGroupBy;
     delete parser.yy.afterLimit;
     delete parser.yy.afterOrderBy;
     delete parser.yy.afterWhere;
   
break;
case 156:

     parser.yy.afterWhere = true;
   
break;
case 157:

     parser.yy.afterGroupBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 158:

     parser.yy.afterOrderBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 159:

     parser.yy.afterLimit = true;
     delete parser.yy.result.suggestStar;
   
break;
case 160:

     var keywords = [];
     if (!parser.yy.afterGroupBy) {
       keywords.push('GROUP BY');
     }
     if (!parser.yy.afterGroupBy && !parser.yy.afterWhere && !parser.yy.afterOrderBy && !parser.yy.afterLimit) {
       keywords.push('JOIN');
       if (parser.yy.dialect === 'hive') {
         keywords.push('LATERAL');
       }
     }
     if (!parser.yy.afterLimit) {
       keywords.push('LIMIT');
     }
     if (!parser.yy.afterOrderBy) {
       keywords.push('ORDER BY');
     }
     if (!parser.yy.afterWhere) {
       keywords.push('WHERE');
     }
     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   
break;
case 167:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 173:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 177: case 189: case 192:

     this.$ = $$[$0];
   
break;
case 185:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 193:

     this.$ = parser.yy.identifierChain;
     delete parser.yy.identifierChain;
   
break;
case 194:

     parser.yy.identifierChain = [];
   
break;
case 196:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 198:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 200:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 202: case 204:

     suggestKeywords(['BY']);
   
break;
case 206:

     suggestNumbers([1, 5, 10]);
   
break;
case 208: case 209:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 213:

     this.$ = { name: $$[$0] }
   
break;
case 214:

     this.$ = { name: $$[$0-5], key: '"' + $$[$0-2] + '"' }
   
break;
case 215:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 216:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 218:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 219:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 221:

      delete parser.yy.derivedColumnChain;
   
break;
case 222: case 223:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 224:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 225:

     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 226:

     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 230:

     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       } else if ($$[$0].identifierChain.length === 0) {
         suggestTables();
         suggestDatabases({ appendDot: true });
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 231:

     addTablePrimary($$[$0]);
   
break;
case 233:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], lateralViews: $$[$0] }
   
break;
case 234:

     this.$ = { identifierChain: [ { name: $$[$0-2] } ], alias: $$[$0-1], lateralViews: $$[$0] };
   
break;
case 237:

     this.$ = $$[$0-2];
   
break;
case 238:

     this.$ = { identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] }
   
break;
case 239:

     this.$ = { identifierChain: [ { name: $$[$0-3] }, { name: $$[$0] } ] }
   
break;
case 240:

     this.$ = { identifierChain: [ { name: $$[$0-4] }, { name: $$[$0-1] } ] }
   
break;
case 241:

     this.$ = { identifierChain: [ { name: $$[$0-5] }, { name: $$[$0-1] } ] }
   
break;
case 242:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-4] } ] };
   
break;
case 243:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-2] } ] };
   
break;
case 244:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-3] } ] };
   
break;
case 245:

     this.$ = { partial: true, identifierChain: [ ] };
   
break;
case 246:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ] }
   
break;
case 247:

     this.$ = { identifierChain: [ { name: $$[$0] } ] }
   
break;
case 248:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] };
   
break;
case 250:

     this.$ = { identifierChain: $$[$0-1].identifierChain, alias: $$[$0] }
   
break;
case 251:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 253:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 255:

     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 256:

     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 257:

     this.$ = { udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }
   
break;
case 258:

      this.$ = { udtf: $$[$0-1], columnAliases: $$[$0] }
    
break;
case 259: case 260:

     suggestKeywords(['AS']);
   
break;
case 261:

     suggestKeywords(['explode', 'posexplode']);
   
break;
case 262:

     suggestKeywords(['VIEW']);
   
break;
case 263:

     this.$ = [ $$[$0] ]
   
break;
case 264:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 266:

     suggestKeywords(['ON']);
   
break;
case 267:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,7,19,28,29,34,52,53,119],[2,7],{10:1,9:2}),{1:[3]},{3:9,4:$V0,5:$V1,7:$V2,11:3,14:4,15:5,16:6,17:7,18:14,19:$V3,20:10,21:11,22:18,28:$V4,29:$V5,34:$V6,48:12,49:13,50:20,51:21,52:$V7,53:$V8,54:24,55:25,119:$V9},{12:[1,29],13:[1,30]},o($Va,[2,10]),o($Va,[2,12]),o($Va,[2,13]),o($Va,[2,14]),{5:[1,31]},o($Va,[2,17]),o($Va,[2,21]),o($Va,[2,22]),o($Va,[2,51]),o($Va,[2,52]),o($Va,[2,53]),o([4,5,7,165],[2,151],{120:32}),o($Vb,[2,1]),o($Vb,[2,2]),{4:$Vc,6:34,7:$Vd,23:33,30:[1,35],31:[1,36]},{4:$Vc,6:40,7:$Ve,35:39,39:41,40:43,176:$Vf,177:44},o($Va,[2,54]),o($Va,[2,55]),{4:$Vc,6:46,7:$Vd,27:[1,48],59:49,63:$Vg,64:$Vh,84:47,86:[1,50],87:[1,51]},{4:$Vc,6:54,7:$Vd,27:[1,56],59:55,63:$Vg,64:$Vh},o($Va,[2,58]),o($Va,[2,59]),{4:[1,58],7:[1,57]},o($Vi,[2,29]),o($Vi,[2,30]),{3:9,4:$V0,5:$V1,7:$V2,13:[1,59],14:60,15:5,16:6,17:7,18:14,19:$V3,20:10,21:11,22:18,28:$V4,29:$V5,34:$V6,48:12,49:13,50:20,51:21,52:$V7,53:$V8,54:24,55:25,119:$V9},{1:[2,9]},o($Va,[2,16],{7:[1,61]}),{3:67,4:$V0,5:$V1,7:$Vj,121:62,158:66,162:63,165:[1,64],166:65},{4:$Vc,6:70,7:$Vd,24:69,32:[1,71],33:[1,72]},o($Va,[2,28]),o($Vk,[2,31]),o($Vk,[2,32]),{5:$Vl},o($Vm,$Vn),o($Va,[2,39],{4:[1,75],36:[1,74]}),o($Va,[2,40]),o($Vo,[2,41]),o($Vo,$Vp,{101:77,5:$Vl,7:[1,76],102:$Vq,103:$Vr,104:$Vs}),o($Vo,[2,42]),o($Vt,[2,249],{7:[1,81]}),{72:[1,82],178:[1,83]},o($Va,[2,56],{27:[1,84]}),{27:[1,85]},{7:[1,86]},o($Vu,[2,76],{67:87,4:[1,89],65:[1,88]}),{27:[2,109]},{27:[2,110]},o($Vv,[2,71]),o($Vv,[2,72]),o($Va,[2,57]),o($Vw,$Vx,{60:90,65:$Vy}),o($Vw,$Vx,{60:92,65:$Vy}),o($Va,[2,19],{5:[1,93]}),o($Va,[2,20]),{1:[2,8]},o($Va,[2,11]),o($Va,[2,15]),o($Va,[2,148],{122:94,123:95,125:[1,96]}),o($Vz,[2,207],{6:97,4:$Vc,7:$Vd,42:$VA}),o($Vz,[2,210],{6:99,4:$Vc,7:$Vd}),o($VB,[2,211]),o($VB,[2,217],{101:100,5:[1,101],102:$Vq,103:$Vr,104:$Vs}),o($VB,[2,224]),o($VC,$VD,{167:$VE}),{25:103,98:$VF},o($Va,[2,27]),{98:[2,33]},{98:[2,34]},o($Vm,[2,3]),{4:$Vc,6:108,7:$VG,37:105,41:106,43:107},o($Va,[2,38]),o($Vo,$VH),{5:$VI,7:[1,110],8:112,176:[1,111]},o($VJ,[2,130]),o($VJ,$VK),o($VJ,$VL),o($Vt,[2,250]),{176:[1,114]},o($VM,[2,245]),o($Va,[2,106],{7:[1,115]}),{7:[1,116]},{78:$VN,85:117},o($Va,[2,98],{7:[1,119]}),{4:$Vc,6:120,7:$Vd,68:[1,121]},o($Vu,[2,80]),o($Va,[2,63],{6:122,61:123,4:$Vc,7:[1,124],176:[1,125]}),{4:$Vc,6:126,7:$Vd,66:[1,127]},o($Va,[2,67],{177:44,6:128,62:129,40:130,4:$Vc,7:$Ve,176:$Vf}),o($Va,[2,18]),o($Va,[2,147]),o($Va,[2,149],{124:131,127:132,38:133,128:134,129:135,130:136,4:$VO,131:$VP,160:$VQ,163:$VR,164:$VS}),{4:$Vc,6:143,7:[1,145],40:130,62:147,126:142,171:144,172:146,173:148,174:149,176:$Vf,177:44},o($Vz,[2,208]),{3:67,4:$V0,5:$V1,7:$Vj,158:66,166:150},o($Vz,[2,209]),{5:$VI,7:$VT,8:151,158:155,165:[1,152],170:153},o($VB,[2,219]),{150:[1,157],168:[1,156],169:[1,158]},o($Va,[2,26],{6:160,4:$Vc,7:$Vd,26:[1,159]}),{5:[1,162],99:[1,161]},o($Va,[2,37],{38:163,4:[1,164],42:[1,165],131:$VP}),o($VU,[2,43]),{4:[1,167],44:[1,166]},o($VU,[2,47]),o([4,44],[2,48],{5:$Vl}),o($VM,[2,238],{5:$VV}),{72:[1,169]},o($VM,[2,243]),o($VW,[2,6]),o($VM,[2,246],{101:170,102:$Vq,103:$Vr,104:$Vs}),o($Va,[2,105],{85:171,78:$VN}),{78:$VN,85:172},o($Va,[2,108]),{7:$VX,88:173,89:174,90:175},o([76,94,95,96,97],[2,97],{83:178,4:[1,177],12:$VY,13:$VY}),o($Vu,[2,77]),{4:$Vc,6:179,7:$Vd,66:[1,180]},o($Va,[2,64]),o($Va,[2,60],{6:181,56:182,4:$Vc,7:$Vd,57:[1,183],58:[1,184]}),o($VZ,[2,236],{5:$Vl}),{72:[1,185]},o($Vw,[2,74]),o($Vw,[2,75]),o($Va,[2,68]),o($Va,[2,69],{4:[1,186]}),o($V_,[2,235]),o($Va,[2,150],{38:133,128:134,129:135,130:136,127:187,4:$VO,131:$VP,160:$VQ,163:$VR,164:$VS}),o($V$,[2,154]),o($V$,[2,156]),o($V$,[2,157]),o($V$,[2,158]),o($V$,[2,159]),o($V$,[2,160]),o($V01,$V11,{132:188,47:190,133:191,135:192,137:194,138:195,142:196,143:197,153:199,149:200,152:201,154:202,155:206,4:[1,189],68:$V21,71:$V31,78:$V41,150:$V51,151:$V61}),{4:$Vc,6:208,7:$Vd,161:[1,207]},{4:$Vc,6:210,7:$Vd,161:[1,209]},{4:$Vc,6:212,7:$Vd,150:[1,211]},o($V$,[2,152],{42:[1,213]}),o($V$,[2,153]),o($V71,[2,227],{187:$V81}),o([4,12,13,42,131,160,163,164,187],$Vp,{101:77,175:215,182:217,5:$Vl,7:$V91,102:$Vq,103:$Vr,104:$Vs,183:$Va1}),o($V_,[2,229]),o($V_,[2,230]),o($V_,[2,231]),o($V_,[2,232]),o($VB,[2,212]),o($VB,[2,218]),o($VB,[2,220]),o($VB,[2,221],{101:221,102:$Vq,103:[1,219],104:[1,220]}),o($Vb1,$VD,{5:$VV,167:$VE}),o($Vb1,[2,225]),{7:[1,222]},{169:[1,223]},o($VC,[2,216]),{4:$Vc,6:225,7:$Vd,27:[1,224]},o($Va,[2,25]),{5:[1,227],100:[1,226]},o($Vc1,[2,129],{100:[1,228]}),o($Va,[2,35]),o($Va,[2,36]),{4:$Vc,6:108,7:$VG,41:229,43:107},o($V01,$V11,{133:191,135:192,137:194,138:195,142:196,143:197,153:199,149:200,152:201,154:202,155:206,45:230,46:231,47:232,68:$V21,71:$V31,78:$V41,150:$V51,151:$V61}),o($VU,[2,46]),o($VW,[2,5]),{176:[1,233]},{5:[1,236],7:[1,234],176:[1,235]},o($Va,[2,104]),{4:$Vc,6:238,7:$Vd,82:237,93:239,94:$Vd1,95:$Ve1},{42:[1,243],79:[1,242]},o($Vf1,[2,112]),o($Vf1,[2,114]),{4:$Vc,6:245,7:$Vd,91:244,105:[1,246],106:[1,247],107:[1,248],108:[1,249],109:[1,250],110:[1,251],111:[1,252],112:[1,253],113:[1,254],114:[1,255],115:[1,256],116:[1,257],117:[1,258],118:[1,259]},o($Va,[2,100]),{69:262,70:265,75:264,76:$Vg1,80:260,81:261,82:263,93:239,94:$Vd1,95:$Ve1,96:$Vh1,97:$Vi1},o($Vu,[2,78]),o($Vu,[2,79]),o($Va,[2,65]),o($Va,[2,66]),o($Va,[2,61]),o($Va,[2,62]),{176:[1,269]},o($Va,[2,70]),o($V$,[2,155]),o($V$,[2,161]),o($V$,[2,162]),o($V_,[2,163],{134:$Vj1}),o($Vk1,[2,164]),o($Vk1,[2,166],{136:[1,271]}),o($V01,$V11,{138:195,142:196,143:197,153:199,149:200,152:201,154:202,155:206,137:272,71:$V31,78:$V41,150:$V51,151:$V61}),o($Vl1,[2,170]),o($Vl1,[2,171],{139:273,44:[1,275],140:[1,274],144:[1,276],145:[1,277],146:[1,278],147:[1,279],148:[1,280]}),o($Vm1,[2,176]),o($Vm1,[2,177]),o($V01,$V11,{133:191,135:192,137:194,138:195,142:196,143:197,153:199,149:200,152:201,154:202,155:206,47:281,3:282,4:$V0,5:$V1,68:$V21,71:$V31,78:$V41,150:$V51,151:$V61}),o($Vm1,[2,189]),o($Vm1,[2,190]),o($Vm1,[2,191]),o($Vm1,[2,192]),o($Vm1,[2,186]),{150:[1,283]},{72:[1,284]},{7:$Vj,156:285,157:286,158:287,159:$Vn1},{3:67,4:$V0,5:$V1,7:$Vj,158:66,162:289,166:65},o($V$,[2,202]),{3:67,4:$V0,5:$V1,7:$Vj,158:66,162:290,166:65},o($V$,[2,204]),o($V$,[2,205]),o($V$,[2,206]),{7:$Vo1,40:130,62:147,171:291,172:146,173:148,174:149,176:$Vf,177:44},{4:[1,294],7:$Vo1,40:130,62:147,171:293,172:146,173:148,174:149,176:$Vf,177:44},o($V_,[2,233],{182:295,183:$Va1}),o($V_,$VH,{182:217,175:296,183:$Va1}),o($Vp1,[2,255]),{4:$Vc,6:298,7:$Vd,184:[1,297]},{5:[1,299],7:$VK},{5:[1,300],7:$VL},{7:$Vj,158:301},{168:[1,302]},o($VC,[2,215]),{7:[1,303]},o($Va,[2,24]),o($Vc1,[2,124]),o($Vc1,[2,127],{99:[1,304],100:[1,305]}),o($Vc1,[2,128]),o($VU,[2,44]),o($VU,[2,45]),o($VU,[2,49]),o($VU,[2,50],{134:$Vj1}),o($VM,[2,240]),o($VM,[2,239]),{72:[1,306],178:[1,307]},o($VM,[2,244]),o($Va,[2,103]),o($Va,[2,107]),{25:308,98:$VF},{98:[2,120]},{98:[2,121]},o([4,7,12,13,94,95],[2,111]),{7:$VX,89:309,90:175},o($Vf1,[2,115]),o($Vf1,[2,116],{92:310,2:[2,118]}),o($Vf1,[2,133]),o($Vf1,[2,134]),o($Vf1,[2,135]),o($Vf1,[2,136]),o($Vf1,[2,137]),o($Vf1,[2,138]),o($Vf1,[2,139]),o($Vf1,[2,140]),o($Vf1,[2,141]),o($Vf1,[2,142]),o($Vf1,[2,143]),o($Vf1,[2,144]),o($Vf1,[2,145]),o($Vf1,[2,146]),{2:[1,311],4:[1,312]},o($Vn,[2,91],{93:239,69:262,82:263,75:264,70:265,81:313,76:$Vg1,94:$Vd1,95:$Ve1,96:$Vh1,97:$Vi1}),o($Vq1,[2,94]),o($Vq1,[2,95]),o($Vq1,[2,96]),{71:[1,314]},{4:[1,316],77:[1,315]},{71:[2,122]},{71:[2,123]},o($VZ,[2,237]),o($V01,$V11,{135:192,137:194,138:195,142:196,143:197,153:199,149:200,152:201,154:202,155:206,133:317,68:$V21,71:$V31,78:$V41,150:$V51,151:$V61}),o($V01,$V11,{135:192,137:194,138:195,142:196,143:197,153:199,149:200,152:201,154:202,155:206,133:319,4:[1,318],68:$V21,71:$V31,78:$V41,150:$V51,151:$V61}),o($Vl1,[2,169]),o($V01,$V11,{142:196,143:197,153:199,149:200,152:201,154:202,155:206,138:320,3:321,4:$V0,5:$V1,71:$V31,78:$V41,150:$V51,151:$V61}),{68:[1,323],141:[1,322]},o($Vr1,[2,178]),o($Vr1,[2,179]),o($Vr1,[2,180]),o($Vr1,[2,181]),o($Vr1,[2,182]),o($Vr1,[2,183]),{79:[1,324],134:$Vj1},o($Vm1,[2,185]),o($Vm1,[2,187]),{71:[1,325]},o($Vm1,[2,193],{101:326,102:$Vq,103:$Vr,104:$Vs}),o($Vs1,[2,195]),o($Vs1,[2,198],{5:[1,327]}),{7:[1,328]},o($V$,[2,201],{42:$VA}),o($V$,[2,203],{42:$VA}),o($V71,[2,228],{187:$V81}),o($V_,$Vp,{101:77,175:215,182:217,7:$V91,102:$Vq,103:$Vr,104:$Vs,183:$Va1}),{4:[1,330],187:$V81,188:329,189:331,190:[1,332]},o($V_,[2,267]),o($Vp1,[2,256]),o($V_,[2,234],{182:295,183:$Va1}),{4:$Vc,6:334,7:$Vd,179:333,180:[1,335],181:[1,336]},o($Vp1,[2,262]),o($VB,[2,222]),o($VB,[2,223]),o($Vb1,[2,226]),{169:[1,337]},o($Va,[2,23]),{100:[1,338]},o($Vc1,[2,126]),{176:[1,339]},o($VM,[2,242]),o([2,4,12,13,76,94,95,96,97],[2,119]),o($Vf1,[2,113]),{2:[1,340]},o($Va,[2,101]),o($Va,[2,102]),o($Vn,[2,92],{93:239,69:262,82:263,75:264,70:265,81:341,76:$Vg1,94:$Vd1,95:$Ve1,96:$Vh1,97:$Vi1}),o($Vq1,[2,81],{72:[1,342]}),o($Vq1,[2,89],{78:[1,343]}),o($Vq1,[2,90]),o($Vk1,[2,165]),o($Vk1,[2,167]),o($Vk1,[2,168]),o($Vl1,[2,172]),o($Vl1,[2,173]),o($Vl1,[2,174]),{141:[1,344]},o($Vm1,[2,184]),o($Vm1,[2,188]),{5:[1,345],7:$Vj,157:346,158:287,159:$Vn1},o($Vs1,[2,199]),{159:[1,347]},o($V_,[2,265]),o($V_,[2,266]),o($V_,[2,268]),o($V01,$V11,{47:190,133:191,135:192,137:194,138:195,142:196,143:197,153:199,149:200,152:201,154:202,155:206,132:348,68:$V21,71:$V31,78:$V41,150:$V51,151:$V61}),{4:$Vc,6:351,7:[1,349],185:350,186:$Vt1},o($Vp1,[2,261]),{78:[1,353]},{78:[1,354]},o($VC,[2,214]),o($Vc1,[2,125]),o($VM,[2,241]),o($Vf1,[2,117]),o($Vn,[2,93]),o($Vq1,[2,82],{71:[1,355]}),{7:$Vu1,71:$Vv1,73:356,74:357},o($Vl1,[2,175]),o($Vs1,[2,196]),o($Vs1,[2,197]),o($Vs1,[2,200]),o($V_,[2,269]),{4:$Vc,5:$Vl,6:361,7:$Vd,185:360,186:$Vt1},o($Vp1,[2,258]),o($Vp1,[2,260]),{7:[1,362],78:[1,363]},{5:$VI,7:$VT,8:365,158:155,170:364},{5:$VI,7:$VT,8:367,158:155,170:366},o($Vq1,[2,83]),{42:[1,369],79:[1,368]},o($Vf1,[2,84]),{44:[1,370]},{72:[1,371]},o($Vp1,[2,257]),o($Vp1,[2,259]),o($Vp1,[2,263]),{7:[1,372]},{79:[1,373],101:221,102:$Vq,103:$Vr,104:$Vs},{2:[1,374]},{79:[1,375],101:221,102:$Vq,103:$Vr,104:$Vs},{2:[1,376]},o($Vq1,[2,88]),{7:$Vu1,71:$Vv1,74:377},{7:[1,378]},{71:[1,379]},{42:[1,380]},o($Vw1,[2,251]),o($Vw1,[2,252]),o($Vw1,[2,253]),o($Vw1,[2,254]),o($Vf1,[2,85]),o($Vf1,[2,86]),{44:[1,381]},{7:[1,382]},{71:[1,383]},{79:[1,384]},{72:[1,385]},o($Vp1,[2,264]),{71:[1,386]},o($Vf1,[2,87])],
defaultActions: {30:[2,9],50:[2,109],51:[2,110],59:[2,8],71:[2,33],72:[2,34],240:[2,120],241:[2,121],267:[2,122],268:[2,123]},
parseError: function parseError(str, hash) {
    if (hash.recoverable) {
        this.trace(str);
    } else {
        function _parseError (msg, hash) {
            this.message = msg;
            this.hash = hash;
        }
        _parseError.prototype = Error;

        throw new _parseError(str, hash);
    }
},
parse: function parse(input) {
    var self = this,
        stack = [0],
        tstack = [], // token stack
        vstack = [null], // semantic value stack
        lstack = [], // location stack
        table = this.table,
        yytext = '',
        yylineno = 0,
        yyleng = 0,
        recovering = 0,
        TERROR = 2,
        EOF = 1;

    var args = lstack.slice.call(arguments, 1);

    //this.reductionCount = this.shiftCount = 0;

    var lexer = Object.create(this.lexer);
    var sharedState = { yy: {} };
    // copy state
    for (var k in this.yy) {
      if (Object.prototype.hasOwnProperty.call(this.yy, k)) {
        sharedState.yy[k] = this.yy[k];
      }
    }

    lexer.setInput(input, sharedState.yy);
    sharedState.yy.lexer = lexer;
    sharedState.yy.parser = this;
    if (typeof lexer.yylloc == 'undefined') {
        lexer.yylloc = {};
    }
    var yyloc = lexer.yylloc;
    lstack.push(yyloc);

    var ranges = lexer.options && lexer.options.ranges;

    if (typeof sharedState.yy.parseError === 'function') {
        this.parseError = sharedState.yy.parseError;
    } else {
        this.parseError = Object.getPrototypeOf(this).parseError;
    }

    function popStack (n) {
        stack.length = stack.length - 2 * n;
        vstack.length = vstack.length - n;
        lstack.length = lstack.length - n;
    }

_token_stack:
    var lex = function () {
        var token;
        token = lexer.lex() || EOF;
        // if token isn't its numeric value, convert
        if (typeof token !== 'number') {
            token = self.symbols_[token] || token;
        }
        return token;
    }

    var symbol, preErrorSymbol, state, action, a, r, yyval = {}, p, len, newState, expected;
    while (true) {
        // retreive state number from top of stack
        state = stack[stack.length - 1];

        // use default actions if available
        if (this.defaultActions[state]) {
            action = this.defaultActions[state];
        } else {
            if (symbol === null || typeof symbol == 'undefined') {
                symbol = lex();
            }
            // read action for current state and first input
            action = table[state] && table[state][symbol];
        }

_handle_error:
        // handle parse error
        if (typeof action === 'undefined' || !action.length || !action[0]) {
            var error_rule_depth;
            var errStr = '';

            // Return the rule stack depth where the nearest error rule can be found.
            // Return FALSE when no error recovery rule was found.
            function locateNearestErrorRecoveryRule(state) {
                var stack_probe = stack.length - 1;
                var depth = 0;

                // try to recover from error
                for(;;) {
                    // check for error recovery rule in this state
                    if ((TERROR.toString()) in table[state]) {
                        return depth;
                    }
                    if (state === 0 || stack_probe < 2) {
                        return false; // No suitable error recovery rule available.
                    }
                    stack_probe -= 2; // popStack(1): [symbol, action]
                    state = stack[stack_probe];
                    ++depth;
                }
            }

            if (!recovering) {
                // first see if there's any chance at hitting an error recovery rule:
                error_rule_depth = locateNearestErrorRecoveryRule(state);

                // Report error
                expected = [];
                for (p in table[state]) {
                    if (this.terminals_[p] && p > TERROR) {
                        expected.push("'"+this.terminals_[p]+"'");
                    }
                }
                if (lexer.showPosition) {
                    errStr = 'Parse error on line '+(yylineno+1)+":\n"+lexer.showPosition()+"\nExpecting "+expected.join(', ') + ", got '" + (this.terminals_[symbol] || symbol)+ "'";
                } else {
                    errStr = 'Parse error on line '+(yylineno+1)+": Unexpected " +
                                  (symbol == EOF ? "end of input" :
                                              ("'"+(this.terminals_[symbol] || symbol)+"'"));
                }
                this.parseError(errStr, {
                    text: lexer.match,
                    token: this.terminals_[symbol] || symbol,
                    line: lexer.yylineno,
                    loc: yyloc,
                    expected: expected,
                    recoverable: (error_rule_depth !== false)
                });
            } else if (preErrorSymbol !== EOF) {
                error_rule_depth = locateNearestErrorRecoveryRule(state);
            }

            // just recovered from another error
            if (recovering == 3) {
                if (symbol === EOF || preErrorSymbol === EOF) {
                    throw new Error(errStr || 'Parsing halted while starting to recover from another error.');
                }

                // discard current lookahead and grab another
                yyleng = lexer.yyleng;
                yytext = lexer.yytext;
                yylineno = lexer.yylineno;
                yyloc = lexer.yylloc;
                symbol = lex();
            }

            // try to recover from error
            if (error_rule_depth === false) {
                throw new Error(errStr || 'Parsing halted. No suitable error recovery rule available.');
            }
            popStack(error_rule_depth);

            preErrorSymbol = (symbol == TERROR ? null : symbol); // save the lookahead token
            symbol = TERROR;         // insert generic error symbol as new lookahead
            state = stack[stack.length-1];
            action = table[state] && table[state][TERROR];
            recovering = 3; // allow 3 real symbols to be shifted before reporting a new error
        }

        // this shouldn't happen, unless resolve defaults are off
        if (action[0] instanceof Array && action.length > 1) {
            throw new Error('Parse Error: multiple actions possible at state: '+state+', token: '+symbol);
        }

        switch (action[0]) {
            case 1: // shift
                //this.shiftCount++;

                stack.push(symbol);
                vstack.push(lexer.yytext);
                lstack.push(lexer.yylloc);
                stack.push(action[1]); // push state
                symbol = null;
                if (!preErrorSymbol) { // normal execution/no error
                    yyleng = lexer.yyleng;
                    yytext = lexer.yytext;
                    yylineno = lexer.yylineno;
                    yyloc = lexer.yylloc;
                    if (recovering > 0) {
                        recovering--;
                    }
                } else {
                    // error just occurred, resume old lookahead f/ before error
                    symbol = preErrorSymbol;
                    preErrorSymbol = null;
                }
                break;

            case 2:
                // reduce
                //this.reductionCount++;

                len = this.productions_[action[1]][1];

                // perform semantic action
                yyval.$ = vstack[vstack.length-len]; // default to $$ = $1
                // default location, uses first token for firsts, last for lasts
                yyval._$ = {
                    first_line: lstack[lstack.length-(len||1)].first_line,
                    last_line: lstack[lstack.length-1].last_line,
                    first_column: lstack[lstack.length-(len||1)].first_column,
                    last_column: lstack[lstack.length-1].last_column
                };
                if (ranges) {
                  yyval._$.range = [lstack[lstack.length-(len||1)].range[0], lstack[lstack.length-1].range[1]];
                }
                r = this.performAction.apply(yyval, [yytext, yyleng, yylineno, sharedState.yy, action[1], vstack, lstack].concat(args));

                if (typeof r !== 'undefined') {
                    return r;
                }

                // pop off stack
                if (len) {
                    stack = stack.slice(0,-1*len*2);
                    vstack = vstack.slice(0, -1*len);
                    lstack = lstack.slice(0, -1*len);
                }

                stack.push(this.productions_[action[1]][0]);    // push nonterminal (reduce)
                vstack.push(yyval.$);
                lstack.push(yyval._$);
                // goto new state = table[STATE][NONTERMINAL]
                newState = table[stack[stack.length-2]][stack[stack.length-1]];
                stack.push(newState);
                break;

            case 3:
                // accept
                return true;
        }

    }

    return true;
}};


var prioritizeSuggestions = function () {
   parser.yy.result.lowerCase = parser.yy.lowerCase || false;
   if (typeof parser.yy.result.suggestIdentifiers !== 'undefined' &&  parser.yy.result.suggestIdentifiers.length > 0) {
     if (!parser.yy.keepColumns) {
      delete parser.yy.result.suggestColumns;
     }
     delete parser.yy.result.suggestTables;
     delete parser.yy.result.suggestDatabases;
     return;
   }
   if (typeof parser.yy.result.suggestColumns !== 'undefined') {
     if (typeof parser.yy.result.suggestColumns.table === 'undefined') {
       delete parser.yy.result.suggestColumns;
     } else {
       delete parser.yy.result.suggestTables;
       delete parser.yy.result.suggestDatabases;
     }
     return;
   }
}


/**
 * Impala supports referencing maps and arrays in the the table reference list i.e.
 *
 *  SELECT m['foo'].bar.| FROM someDb.someTable t, t.someMap m;
 *
 * From this the tablePrimaries would look like:
 *
 * [ { alias: 't', identifierChain: [ { name: 'someDb' }, { name: 'someTable' } ] },
 *   { alias: 'm', identifierChain: [ { name: 't' }, { name: 'someMap' } ] } ]
 *
 * with an identifierChain from the select list:
 *
 * [ { name: 'm', key: 'foo' }, { name: 'bar' } ]
 *
 * Calling this would return an expanded identifierChain, given the above it would be:
 *
 * [ { name: 't' }, { name: 'someMap', key: 'foo' }, { name: 'bar' } ]
 */
parser.expandImpalaIdentifierChain = function (tablePrimaries, identifierChain) {
  if (typeof identifierChain === 'undefined' || identifierChain.length === 0) {
    return identifierChain;
  }
  var firstIdentifier = identifierChain[0].name;

  foundPrimary = tablePrimaries.filter(function (tablePrimary) {
    return tablePrimary.alias === firstIdentifier;
  });

  if (foundPrimary.length === 1) {
    var firstPart = foundPrimary[0].identifierChain.concat();
    var secondPart = identifierChain.slice(1);
    if (typeof identifierChain[0].key !== 'undefined') {
      var lastFromFirst = firstPart.pop();
      firstPart.push({
        name: lastFromFirst.name,
        key: identifierChain[0].key
      })
    }
    return firstPart.concat(secondPart);
  }

  return identifierChain;
};

parser.expandLateralViews = function (tablePrimaries, identifierChain) {
  var firstIdentifier = identifierChain[0];
  var identifierChainParts = [];
  tablePrimaries.forEach(function (tablePrimary) {
    if (typeof tablePrimary.lateralViews !== 'undefined') {
      tablePrimary.lateralViews.reverse().forEach(function (lateralView) {
        if (firstIdentifier.name === lateralView.tableAlias && identifierChain.length > 1) {
          identifierChain.shift();
          firstIdentifier = identifierChain[0];
        } else if (firstIdentifier.name === lateralView.tableAlias && identifierChain.length === 1 && typeof parser.yy.result.suggestColumns !== 'undefined') {
          if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
            parser.yy.result.suggestIdentifiers = [];
          }
          lateralView.columnAliases.forEach(function (columnAlias) {
            parser.yy.result.suggestIdentifiers.push({ name: columnAlias, type: 'alias' });
          });
          delete parser.yy.result.suggestColumns;
          return identifierChain;
        }
        if (lateralView.columnAliases.indexOf(firstIdentifier.name) !== -1) {
          if (lateralView.columnAliases.length === 2 && lateralView.udtf.function.toLowerCase() === 'explode' && firstIdentifier.name === lateralView.columnAliases[0]) {
            identifierChain[0] = { name: 'key' };
          } else if (lateralView.columnAliases.length === 2 && lateralView.udtf.function.toLowerCase() === 'explode' && firstIdentifier.name === lateralView.columnAliases[1]) {
            identifierChain[0] = { name: 'value' };
          } else {
            identifierChain[0] = { name: 'item' };
          }
          identifierChain = lateralView.udtf.expression.concat(identifierChain);
          firstIdentifier = identifierChain[0];
        }
      });
    }
  });
  return identifierChain;
};

var linkSuggestion = function (suggestion, isColumnSuggestion) {
  var identifierChain = suggestion.identifierChain;
  var tablePrimaries = parser.yy.latestTablePrimaries;
  // Impala can have references to maps or array, i.e. FROM table t, t.map m
  // We need to replace those in the identifierChain
  if (parser.yy.dialect === 'impala') {
    identifierChain = parser.expandImpalaIdentifierChain(tablePrimaries, identifierChain);
    suggestion.identifierChain = identifierChain;
  }

  // Expand exploded views in the identifier chain
  if (parser.yy.dialect === 'hive') {
    if (identifierChain.length === 0) {
      if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
        parser.yy.result.suggestIdentifiers = [];
      }
      tablePrimaries.forEach(function (tablePrimary) {
        if (typeof tablePrimary.lateralViews !== 'undefined') {
          tablePrimary.lateralViews.forEach(function (lateralView) {
            if (typeof lateralView.tableAlias !== 'undefined') {
              parser.yy.result.suggestIdentifiers.push({ name: lateralView.tableAlias + '.', type: 'alias' });
              parser.yy.keepColumns = true;
            }
            lateralView.columnAliases.forEach(function (columnAlias) {
              parser.yy.result.suggestIdentifiers.push({ name: columnAlias, type: 'alias' });
              parser.yy.keepColumns = true;
            });
          });
        }
      });
    } else {
      identifierChain = parser.expandLateralViews(tablePrimaries, identifierChain);
      suggestion.identifierChain = identifierChain;
    }
  }

  // IdentifierChain contains a possibly started identifier or empty, example: a.b.c = ['a', 'b', 'c']
  // Reduce the tablePrimaries to the one that matches the first identifier if found
  if (identifierChain.length > 0) {
    var foundTable = tablePrimaries.filter(function (tablePrimary) {
      return identifierChain[0].name === tablePrimary.alias;
    });

    if (foundTable.length === 0) {
      foundTable = tablePrimaries.filter(function (tablePrimary) {
        return identifierChain[0].name === tablePrimary.identifierChain[0].name;
      })
    }

    if (foundTable.length === 1) {
      tablePrimaries = foundTable;
      identifierChain.shift();
    }
  }

  if (identifierChain.length == 0) {
    delete suggestion.identifierChain;
  }

  if (tablePrimaries.length === 1) {
    if (tablePrimaries[0].identifierChain.length == 2) {
      suggestion.database = tablePrimaries[0].identifierChain[0].name;
      suggestion.table = tablePrimaries[0].identifierChain[1].name;
    } else {
      suggestion.table = tablePrimaries[0].identifierChain[0].name;
    }
  } else if (tablePrimaries.length > 1 && isColumnSuggestion) {
    // Table identifier is required for column completion
    delete parser.yy.result.suggestColumns;
    suggestTablePrimariesAsIdentifiers();
  }
}

var suggestTablePrimariesAsIdentifiers = function () {
  if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
    parser.yy.result.suggestIdentifiers = [];
  }
  parser.yy.latestTablePrimaries.forEach(function (tablePrimary) {
    if (typeof tablePrimary.alias !== 'undefined') {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.alias + '.', type: 'alias' });
    } else {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.identifierChain[0].name + '.', type: 'table' });
    }
  });
}

var linkTablePrimaries = function () {
   if (!parser.yy.cursorFound) {
     return;
   }
   if (typeof parser.yy.result.suggestColumns !== 'undefined') {
     linkSuggestion(parser.yy.result.suggestColumns, true);
   }
   if (typeof parser.yy.result.suggestValues !== 'undefined') {
     linkSuggestion(parser.yy.result.suggestValues, false);
     if (parser.yy.latestTablePrimaries.length > 1) {
       suggestTablePrimariesAsIdentifiers();
     }
   }
}

var addTablePrimary = function (ref) {
  if (typeof parser.yy.latestTablePrimaries === 'undefined') {
    parser.yy.latestTablePrimaries = [];
  }
  parser.yy.latestTablePrimaries.push(ref);
}

var suggestNumbers = function (numbers) {
  parser.yy.result.suggestNumbers = numbers;
}

var suggestDdlAndDmlKeywords = function () {
  var keywords = ['ALTER', 'CREATE', 'DELETE', 'DESCRIBE', 'DROP', 'EXPLAIN', 'INSERT', 'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE'];

  if (parser.yy.dialect == 'hive') {
    keywords = keywords.concat(['ANALYZE', 'EXPORT', 'IMPORT', 'LOAD', 'MSCK']);
  }

  if (parser.yy.dialect == 'impala') {
    keywords = keywords.concat(['COMPUTE', 'INVALIDATE', 'LOAD', 'REFRESH']);
  }
  keywords.sort();

  suggestKeywords(keywords);
}


var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords;
}

var suggestTablesOrColumns = function (identifier) {
  if (typeof parser.yy.latestTablePrimaries == 'undefined') {
    suggestTables({ database: identifier });
    return;
  }
  var tableRef = parser.yy.latestTablePrimaries.filter(function (tablePrimary) {
    return tablePrimary.alias === identifier;
  });
  if (tableRef.length > 0) {
    suggestColumns({ identifierChain: [ { name: identifier } ] });
  } else {
    suggestTables({ database: identifier });
  }
}

var suggestColumns = function (details) {
  parser.yy.result.suggestColumns = details || { identifierChain: [] };
}

var suggestTables = function (details) {
  parser.yy.result.suggestTables = details || {};
}

var suggestDatabases = function (details) {
  parser.yy.result.suggestDatabases = details || {};
}

var suggestHdfs = function (details) {
  parser.yy.result.suggestHdfs = details || {}
}

var suggestValues = function (details) {
  parser.yy.result.suggestValues = details || { identifierChain: [] }
}

var determineCase = function (text) {
  parser.yy.lowerCase = text.toLowerCase() === text;
};

var lexerModified = false;

/**
 * Main parser function
 */
parser.parseSql = function(beforeCursor, afterCursor, dialect) {
  parser.yy.activeDialect = dialect;
  parser.yy.result = {};
  parser.yy.lowerCase = false;

  // Hack to set the inital state of the lexer without first having to hit a token
  // has to be done as the first token found can be dependant on dialect
  if (!lexerModified && typeof dialect !== 'undefined') {
    var originalSetInput = parser.lexer.setInput;
    parser.lexer.setInput = function (input) {
      var lexer = originalSetInput.bind(parser.lexer)(input);
      if (typeof parser.yy.activeDialect !== 'undefined') {
        lexer.begin(parser.yy.activeDialect)
      }
    }
    lexerModified = true;
  }

  var result;
  parser.yy.dialect = dialect;
  try {
    // Add |CURSOR| or |PARTIAL_CURSOR| to represent the different cursor states in the lexer
    result = parser.parse(beforeCursor + (beforeCursor.length == 0 || /.*\s+$/.test(beforeCursor) ? ' |CURSOR| ' : '|PARTIAL_CURSOR|') + afterCursor);
  } catch (err) {
    // On any error try to at least return any existing result
    if (typeof parser.yy.result === 'undefined') {
      throw err;
    }
    result = parser.yy.result;
  }

  if (typeof result.error !== 'undefined' && typeof result.error.expected !== 'undefined') {
    // Remove any expected tokens from other dialects, jison doesn't remove tokens from other lexer states.
    var actualExpected = [];
    result.error.expected.forEach(function (expected) {
      var match = expected.match(/\<([a-z]+)\>(.*)/);
      if (match !== null) {
        if (typeof parser.yy.dialect !== 'undefined' && parser.yy.dialect === match[1]) {
          actualExpected.push(match[2]);
        }
      } else {
        actualExpected.push(expected);
      }
    });
    result.error.expected = actualExpected;
  }

  if (typeof result.error !== 'undefined' && result.error.recoverable) {
    delete result.error;
  }

  return result;
}

/*
 Hive Select syntax from https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Select

 [WITH CommonTableExpression (, CommonTableExpression)*]    (Note: Only available starting with Hive 0.13.0)
 SELECT [ALL | DISTINCT] select_expr, select_expr, ...
 FROM table_reference
 [WHERE where_condition]
 [GROUP BY col_list]
 [CLUSTER BY col_list
   | [DISTRIBUTE BY col_list] [SORT BY col_list]
 ]
 [LIMIT number]
*/
/* generated by jison-lex 0.3.4 */
var lexer = (function(){
var lexer = ({

EOF:1,

parseError:function parseError(str, hash) {
        if (this.yy.parser) {
            this.yy.parser.parseError(str, hash);
        } else {
            throw new Error(str);
        }
    },

// resets the lexer, sets new input
setInput:function (input, yy) {
        this.yy = yy || this.yy || {};
        this._input = input;
        this._more = this._backtrack = this.done = false;
        this.yylineno = this.yyleng = 0;
        this.yytext = this.matched = this.match = '';
        this.conditionStack = ['INITIAL'];
        this.yylloc = {
            first_line: 1,
            first_column: 0,
            last_line: 1,
            last_column: 0
        };
        if (this.options.ranges) {
            this.yylloc.range = [0,0];
        }
        this.offset = 0;
        return this;
    },

// consumes and returns one char from the input
input:function () {
        var ch = this._input[0];
        this.yytext += ch;
        this.yyleng++;
        this.offset++;
        this.match += ch;
        this.matched += ch;
        var lines = ch.match(/(?:\r\n?|\n).*/g);
        if (lines) {
            this.yylineno++;
            this.yylloc.last_line++;
        } else {
            this.yylloc.last_column++;
        }
        if (this.options.ranges) {
            this.yylloc.range[1]++;
        }

        this._input = this._input.slice(1);
        return ch;
    },

// unshifts one char (or a string) into the input
unput:function (ch) {
        var len = ch.length;
        var lines = ch.split(/(?:\r\n?|\n)/g);

        this._input = ch + this._input;
        this.yytext = this.yytext.substr(0, this.yytext.length - len);
        //this.yyleng -= len;
        this.offset -= len;
        var oldLines = this.match.split(/(?:\r\n?|\n)/g);
        this.match = this.match.substr(0, this.match.length - 1);
        this.matched = this.matched.substr(0, this.matched.length - 1);

        if (lines.length - 1) {
            this.yylineno -= lines.length - 1;
        }
        var r = this.yylloc.range;

        this.yylloc = {
            first_line: this.yylloc.first_line,
            last_line: this.yylineno + 1,
            first_column: this.yylloc.first_column,
            last_column: lines ?
                (lines.length === oldLines.length ? this.yylloc.first_column : 0)
                 + oldLines[oldLines.length - lines.length].length - lines[0].length :
              this.yylloc.first_column - len
        };

        if (this.options.ranges) {
            this.yylloc.range = [r[0], r[0] + this.yyleng - len];
        }
        this.yyleng = this.yytext.length;
        return this;
    },

// When called from action, caches matched text and appends it on next action
more:function () {
        this._more = true;
        return this;
    },

// When called from action, signals the lexer that this rule fails to match the input, so the next matching rule (regex) should be tested instead.
reject:function () {
        if (this.options.backtrack_lexer) {
            this._backtrack = true;
        } else {
            return this.parseError('Lexical error on line ' + (this.yylineno + 1) + '. You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).\n' + this.showPosition(), {
                text: "",
                token: null,
                line: this.yylineno
            });

        }
        return this;
    },

// retain first n characters of the match
less:function (n) {
        this.unput(this.match.slice(n));
    },

// displays already matched input, i.e. for error messages
pastInput:function () {
        var past = this.matched.substr(0, this.matched.length - this.match.length);
        return (past.length > 20 ? '...':'') + past.substr(-20).replace(/\n/g, "");
    },

// displays upcoming input, i.e. for error messages
upcomingInput:function () {
        var next = this.match;
        if (next.length < 20) {
            next += this._input.substr(0, 20-next.length);
        }
        return (next.substr(0,20) + (next.length > 20 ? '...' : '')).replace(/\n/g, "");
    },

// displays the character position where the lexing error occurred, i.e. for error messages
showPosition:function () {
        var pre = this.pastInput();
        var c = new Array(pre.length + 1).join("-");
        return pre + this.upcomingInput() + "\n" + c + "^";
    },

// test the lexed token: return FALSE when not a match, otherwise return token
test_match:function (match, indexed_rule) {
        var token,
            lines,
            backup;

        if (this.options.backtrack_lexer) {
            // save context
            backup = {
                yylineno: this.yylineno,
                yylloc: {
                    first_line: this.yylloc.first_line,
                    last_line: this.last_line,
                    first_column: this.yylloc.first_column,
                    last_column: this.yylloc.last_column
                },
                yytext: this.yytext,
                match: this.match,
                matches: this.matches,
                matched: this.matched,
                yyleng: this.yyleng,
                offset: this.offset,
                _more: this._more,
                _input: this._input,
                yy: this.yy,
                conditionStack: this.conditionStack.slice(0),
                done: this.done
            };
            if (this.options.ranges) {
                backup.yylloc.range = this.yylloc.range.slice(0);
            }
        }

        lines = match[0].match(/(?:\r\n?|\n).*/g);
        if (lines) {
            this.yylineno += lines.length;
        }
        this.yylloc = {
            first_line: this.yylloc.last_line,
            last_line: this.yylineno + 1,
            first_column: this.yylloc.last_column,
            last_column: lines ?
                         lines[lines.length - 1].length - lines[lines.length - 1].match(/\r?\n?/)[0].length :
                         this.yylloc.last_column + match[0].length
        };
        this.yytext += match[0];
        this.match += match[0];
        this.matches = match;
        this.yyleng = this.yytext.length;
        if (this.options.ranges) {
            this.yylloc.range = [this.offset, this.offset += this.yyleng];
        }
        this._more = false;
        this._backtrack = false;
        this._input = this._input.slice(match[0].length);
        this.matched += match[0];
        token = this.performAction.call(this, this.yy, this, indexed_rule, this.conditionStack[this.conditionStack.length - 1]);
        if (this.done && this._input) {
            this.done = false;
        }
        if (token) {
            return token;
        } else if (this._backtrack) {
            // recover context
            for (var k in backup) {
                this[k] = backup[k];
            }
            return false; // rule action called reject() implying the next rule should be tested instead.
        }
        return false;
    },

// return next match in input
next:function () {
        if (this.done) {
            return this.EOF;
        }
        if (!this._input) {
            this.done = true;
        }

        var token,
            match,
            tempMatch,
            index;
        if (!this._more) {
            this.yytext = '';
            this.match = '';
        }
        var rules = this._currentRules();
        for (var i = 0; i < rules.length; i++) {
            tempMatch = this._input.match(this.rules[rules[i]]);
            if (tempMatch && (!match || tempMatch[0].length > match[0].length)) {
                match = tempMatch;
                index = i;
                if (this.options.backtrack_lexer) {
                    token = this.test_match(tempMatch, rules[i]);
                    if (token !== false) {
                        return token;
                    } else if (this._backtrack) {
                        match = false;
                        continue; // rule action called reject() implying a rule MISmatch.
                    } else {
                        // else: this is a lexer rule which consumes input without producing a token (e.g. whitespace)
                        return false;
                    }
                } else if (!this.options.flex) {
                    break;
                }
            }
        }
        if (match) {
            token = this.test_match(match, rules[index]);
            if (token !== false) {
                return token;
            }
            // else: this is a lexer rule which consumes input without producing a token (e.g. whitespace)
            return false;
        }
        if (this._input === "") {
            return this.EOF;
        } else {
            return this.parseError('Lexical error on line ' + (this.yylineno + 1) + '. Unrecognized text.\n' + this.showPosition(), {
                text: "",
                token: null,
                line: this.yylineno
            });
        }
    },

// return next match that has a token
lex:function lex() {
        var r = this.next();
        if (r) {
            return r;
        } else {
            return this.lex();
        }
    },

// activates a new lexer condition state (pushes the new lexer condition state onto the condition stack)
begin:function begin(condition) {
        this.conditionStack.push(condition);
    },

// pop the previously active lexer condition state off the condition stack
popState:function popState() {
        var n = this.conditionStack.length - 1;
        if (n > 0) {
            return this.conditionStack.pop();
        } else {
            return this.conditionStack[0];
        }
    },

// produce the lexer rule set which is active for the currently active lexer condition state
_currentRules:function _currentRules() {
        if (this.conditionStack.length && this.conditionStack[this.conditionStack.length - 1]) {
            return this.conditions[this.conditionStack[this.conditionStack.length - 1]].rules;
        } else {
            return this.conditions["INITIAL"].rules;
        }
    },

// return the currently active lexer condition state; when an index argument is provided it produces the N-th previous condition state, if available
topState:function topState(n) {
        n = this.conditionStack.length - 1 - Math.abs(n || 0);
        if (n >= 0) {
            return this.conditionStack[n];
        } else {
            return "INITIAL";
        }
    },

// alias for begin(condition)
pushState:function pushState(condition) {
        this.begin(condition);
    },

// return the number of states currently on the stack
stateStackSize:function stateStackSize() {
        return this.conditionStack.length;
    },
options: {"case-insensitive":true},
performAction: function anonymous(yy,yy_,$avoiding_name_collisions,YY_START) {
var YYSTATE=YY_START;
switch($avoiding_name_collisions) {
case 0: /* skip whitespace */ 
break;
case 1: /* skip comments */ 
break;
case 2: /* skip comments */ 
break;
case 3: parser.yy.cursorFound = true; return 4; 
break;
case 4: parser.yy.cursorFound = true; return 5; 
break;
case 5: return 136; 
break;
case 6: return 108; 
break;
case 7: return 109; 
break;
case 8: return 161; 
break;
case 9: return 114; 
break;
case 10: determineCase(yy_.yytext); return 52; 
break;
case 11: return 63; 
break;
case 12: return 113; 
break;
case 13: return 111; 
break;
case 14: determineCase(yy_.yytext); return 53; 
break;
case 15: return 66; 
break;
case 16: return 110; 
break;
case 17: return 125; 
break;
case 18: return 160; 
break;
case 19: return 65; 
break;
case 20: return 107; 
break;
case 21: return 26; 
break;
case 22: return 140; 
break;
case 23: return 187; 
break;
case 24: return 68; 
break;
case 25: return 190; 
break;
case 26: return 134; 
break;
case 27: return 163; 
break;
case 28: return 'ROLE'; 
break;
case 29: return 64; 
break;
case 30: determineCase(yy_.yytext); return 119; 
break;
case 31: return 36; 
break;
case 32: return 106; 
break;
case 33: return 112; 
break;
case 34: return 27; 
break;
case 35: return 116; 
break;
case 36: return 105; 
break;
case 37: determineCase(yy_.yytext); return 34; 
break;
case 38: determineCase(yy_.yytext); return 19; 
break;
case 39: return 115; 
break;
case 40: return 184; 
break;
case 41: return 131; 
break;
case 42: return 186; 
break;
case 43: return 117; 
break;
case 44: return 96; 
break;
case 45: return 30; 
break;
case 46: return 118; 
break;
case 47: return 86; 
break;
case 48: return '<hive>FUNCTION'; 
break;
case 49: return '<hive>INDEX'; 
break;
case 50: this.begin('hdfs'); return 32; 
break;
case 51: return 183; 
break;
case 52: return 28; 
break;
case 53: this.begin('hdfs'); return 94; 
break;
case 54: return '<hive>MACRO'; 
break;
case 55: return '<hive>TEMPORARY'; 
break;
case 56: return 180; 
break;
case 57: return 181; 
break;
case 58: return 104; 
break;
case 59: return '<impala>AGGREGATE'; 
break;
case 60: return 97; 
break;
case 61: return 31; 
break;
case 62: return '<impala>FUNCTION'; 
break;
case 63: return 87; 
break;
case 64: return '<impala>INCREMENTAL'; 
break;
case 65: this.begin('hdfs'); return 33; 
break;
case 66: return 29; 
break;
case 67: this.begin('hdfs'); return 95; 
break;
case 68: return '<impala>STATS'; 
break;
case 69: return 103; 
break;
case 70: return 150; 
break;
case 71: return 7; 
break;
case 72: parser.yy.cursorFound = true; return 4; 
break;
case 73: parser.yy.cursorFound = true; return 5; 
break;
case 74: return 98; 
break;
case 75: return 99; 
break;
case 76: this.popState(); return 100; 
break;
case 77: return 13; 
break;
case 78: return yy_.yytext; 
break;
case 79: return yy_.yytext; 
break;
case 80: return 167; 
break;
case 81: return 169; 
break;
case 82: this.begin('backtickedValue'); return 176; 
break;
case 83: if (yy_.yytext.indexOf('CURSOR|') !== -1) {
                                        this.popState();
                                        return 178;
                                      }
                                      return 72;
                                    
break;
case 84: this.popState(); return 176; 
break;
case 85: this.begin('singleQuotedValue'); return 71; 
break;
case 86: return 72; 
break;
case 87: this.popState(); return 71; 
break;
case 88: return 168; 
break;
case 89: return 13; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DATABASE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:DROP\b)/i,/^(?:EXISTS\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:IF\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:ROLE\b)/i,/^(?:SCHEMA\b)/i,/^(?:SELECT\b)/i,/^(?:SET\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:AS\b)/i,/^(?:BINARY\b)/i,/^(?:COMMENT\b)/i,/^(?:DATA\b)/i,/^(?:DATE\b)/i,/^(?:EXTERNAL\b)/i,/^(?:FUNCTION\b)/i,/^(?:INDEX\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:MACRO\b)/i,/^(?:TEMPORARY\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:AGGREGATE\b)/i,/^(?:COMMENT\b)/i,/^(?:DATA\b)/i,/^(?:FUNCTION\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INCREMENTAL\b)/i,/^(?:INPATH\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:STATS\b)/i,/^(?:[.])/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:\s+['])/i,/^(?:[^'|]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>]+)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[72,73,74,75,76,77],"inclusive":false},"singleQuotedValue":{"rules":[86,87],"inclusive":false},"backtickedValue":{"rules":[83,84],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,70,71,78,79,80,81,82,85,88,89],"inclusive":true},"impala":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,59,60,61,62,63,64,65,66,67,68,69,70,71,78,79,80,81,82,85,88,89],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,70,71,78,79,80,81,82,85,88,89],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});