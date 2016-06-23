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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,18],$V1=[1,19],$V2=[1,9],$V3=[1,11],$V4=[1,22],$V5=[1,23],$V6=[1,21],$V7=[1,16],$V8=[1,17],$V9=[12,13],$Va=[1,34],$Vb=[1,33],$Vc=[4,7,12,13,42,44,68,114,120,123,125,129,133,134,135,136,137,149,152,153,178,181],$Vd=[1,50],$Ve=[4,7,30,31],$Vf=[7,12,13],$Vg=[1,61],$Vh=[2,4,7,12,13,27,42,68,114,120,149,152,153,174,178,181],$Vi=[2,4],$Vj=[4,7,12,13,55],$Vk=[1,68],$Vl=[4,7,32,33],$Vm=[4,12,13,36],$Vn=[2,228],$Vo=[1,77],$Vp=[1,78],$Vq=[1,79],$Vr=[4,12,13,36,42,120,149,152,153,178,181],$Vs=[1,86],$Vt=[12,13,114],$Vu=[1,94],$Vv=[4,7,12,13,42,114,120,149,152,153],$Vw=[4,5,7,12,13,42,44,68,91,92,93,114,120,123,125,129,133,134,135,136,137,149,152,153,178,181],$Vx=[2,194],$Vy=[1,98],$Vz=[1,100],$VA=[1,105],$VB=[2,229],$VC=[1,109],$VD=[5,7,148,154,167],$VE=[2,112],$VF=[2,113],$VG=[4,7,12,13,36,42,120,149,152,153,178,181],$VH=[1,116],$VI=[2,80],$VJ=[1,127],$VK=[1,128],$VL=[1,129],$VM=[1,130],$VN=[1,131],$VO=[1,145],$VP=[4,12,13,42,120],$VQ=[1,159],$VR=[2,4,7,12,13,36,42,114,120,149,152,153,178,181],$VS=[1,165],$VT=[1,166],$VU=[42,68],$VV=[1,191],$VW=[1,192],$VX=[1,193],$VY=[4,12,13,120,149,152,153],$VZ=[7,148],$V_=[2,175],$V$=[1,200],$V01=[1,212],$V11=[1,205],$V21=[1,210],$V31=[1,211],$V41=[4,12,13,42,120,149,152,153],$V51=[1,221],$V61=[1,223],$V71=[1,225],$V81=[4,12,13,42,120,149,152,153,178,181],$V91=[4,7,12,13,42,68,91,92,93,114,120,149,152,153],$Va1=[2,4,7,12,13,26,65,83,84,85,86],$Vb1=[2,4,65,83,84,85,86],$Vc1=[1,253],$Vd1=[4,12,13,42,68,120,123,149,152,153,178,181],$Ve1=[4,12,13,42,68,120,123,125,149,152,153,178,181],$Vf1=[4,12,13,42,44,68,120,123,125,129,133,134,135,136,137,149,152,153,178,181],$Vg1=[1,271],$Vh1=[1,275],$Vi1=[4,12,13,42,120,149,152,153,174,178,181],$Vj1=[4,5,7,60,67,139,140,148],$Vk1=[4,12,13,42,44,68,91,92,93,120,123,125,129,133,134,135,136,137,149,152,153,178,181],$Vl1=[1,321],$Vm1=[1,322],$Vn1=[1,331],$Vo1=[4,7,177];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"PartialIdentifierOrCursor":6,"REGULAR_IDENTIFIER":7,"PartialIdentifierOrPartialCursor":8,"InitResults":9,"Sql":10,"SqlStatements":11,";":12,"EOF":13,"SqlStatement":14,"UseStatement":15,"DataManipulation":16,"DataDefinition":17,"QueryExpression":18,"USE":19,"LoadStatement":20,"UpdateStatement":21,"HiveOrImpalaLoad":22,"HiveOrImpalaData":23,"HiveOrImpalaInpath":24,"HdfsPath":25,"INTO":26,"TABLE":27,"<hive>LOAD":28,"<impala>LOAD":29,"<hive>DATA":30,"<impala>DATA":31,"<hive>INPATH":32,"<impala>INPATH":33,"UPDATE":34,"TargetTable":35,"SET":36,"SetClauseList":37,"WhereClause":38,"TableName":39,"LocalOrSchemaQualifiedName":40,"SetClause":41,",":42,"SetTarget":43,"=":44,"UpdateSource":45,"ValueExpression":46,"BooleanValueExpression":47,"TableDefinition":48,"DatabaseDefinition":49,"CREATE":50,"DatabaseOrSchema":51,"DATABASE":52,"SCHEMA":53,"OptionalIfNotExists":54,"IF":55,"NOT":56,"EXISTS":57,"Comment":58,"HiveOrImpalaComment":59,"SINGLE_QUOTE":60,"VALUE":61,"HivePropertyAssignmentList":62,"HivePropertyAssignment":63,"HiveDbProperties":64,"<hive>WITH":65,"DBPROPERTIES":66,"(":67,")":68,"DatabaseDefinitionOptionals":69,"DatabaseDefinitionOptional":70,"HdfsLocation":71,"CleanUpDatabaseConditions":72,"TableScope":73,"TableElementList":74,"<hive>EXTERNAL":75,"<impala>EXTERNAL":76,"TableElements":77,"TableElement":78,"ColumnDefinition":79,"PrimitiveType":80,"ColumnDefinitionError":81,"HiveOrImpalaLocation":82,"<hive>LOCATION":83,"<impala>LOCATION":84,"<hive>COMMENT":85,"<impala>COMMENT":86,"HDFS_START_QUOTE":87,"HDFS_PATH":88,"HDFS_END_QUOTE":89,"AnyDot":90,".":91,"<impala>.":92,"<hive>.":93,"TINYINT":94,"SMALLINT":95,"INT":96,"BIGINT":97,"BOOLEAN":98,"FLOAT":99,"DOUBLE":100,"STRING":101,"DECIMAL":102,"CHAR":103,"VARCHAR":104,"TIMESTAMP":105,"<hive>BINARY":106,"<hive>DATE":107,"SELECT":108,"CleanUpSelectConditions":109,"SelectList":110,"TableExpression":111,"FromClause":112,"SelectConditionList":113,"FROM":114,"TableReferenceList":115,"SelectCondition":116,"GroupByClause":117,"OrderByClause":118,"LimitClause":119,"WHERE":120,"SearchCondition":121,"BooleanTerm":122,"OR":123,"BooleanFactor":124,"AND":125,"BooleanTest":126,"Predicate":127,"CompOp":128,"IS":129,"TruthValue":130,"ParenthesizedBooleanValueExpression":131,"NonParenthesizedValueExpressionPrimary":132,"<>":133,"<=":134,">=":135,"<":136,">":137,"SignedInteger":138,"UNSIGNED_INTEGER":139,"-":140,"StringValue":141,"ColumnReference":142,"BasicIdentifierChain":143,"InitIdentifierChain":144,"IdentifierChain":145,"Identifier":146,"ColumnIdentifier":147,"\"":148,"GROUP":149,"BY":150,"ColumnList":151,"ORDER":152,"LIMIT":153,"*":154,"DerivedColumn":155,"[":156,"DOUBLE_QUOTE":157,"]":158,"DerivedColumnChain":159,"TableReference":160,"TablePrimaryOrJoinedTable":161,"TablePrimary":162,"LateralViewDefinition":163,"JoinedTable":164,"LateralViews":165,"RegularOrBacktickedIdentifier":166,"BACKTICK":167,"RegularOrBackTickedSchemaQualifiedName":168,"PARTIAL_VALUE":169,"userDefinedTableGeneratingFunction":170,"<hive>explode":171,"<hive>posexplode":172,"LateralView":173,"<hive>LATERAL":174,"VIEW":175,"LateralViewColumnAliases":176,"<hive>AS":177,"JOIN":178,"JoinSpecification":179,"JoinCondition":180,"ON":181,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",7:"REGULAR_IDENTIFIER",12:";",13:"EOF",19:"USE",26:"INTO",27:"TABLE",28:"<hive>LOAD",29:"<impala>LOAD",30:"<hive>DATA",31:"<impala>DATA",32:"<hive>INPATH",33:"<impala>INPATH",34:"UPDATE",36:"SET",42:",",44:"=",50:"CREATE",52:"DATABASE",53:"SCHEMA",55:"IF",56:"NOT",57:"EXISTS",60:"SINGLE_QUOTE",61:"VALUE",65:"<hive>WITH",66:"DBPROPERTIES",67:"(",68:")",75:"<hive>EXTERNAL",76:"<impala>EXTERNAL",83:"<hive>LOCATION",84:"<impala>LOCATION",85:"<hive>COMMENT",86:"<impala>COMMENT",87:"HDFS_START_QUOTE",88:"HDFS_PATH",89:"HDFS_END_QUOTE",91:".",92:"<impala>.",93:"<hive>.",94:"TINYINT",95:"SMALLINT",96:"INT",97:"BIGINT",98:"BOOLEAN",99:"FLOAT",100:"DOUBLE",101:"STRING",102:"DECIMAL",103:"CHAR",104:"VARCHAR",105:"TIMESTAMP",106:"<hive>BINARY",107:"<hive>DATE",108:"SELECT",114:"FROM",120:"WHERE",123:"OR",125:"AND",129:"IS",130:"TruthValue",133:"<>",134:"<=",135:">=",136:"<",137:">",139:"UNSIGNED_INTEGER",140:"-",148:"\"",149:"GROUP",150:"BY",152:"ORDER",153:"LIMIT",154:"*",156:"[",157:"DOUBLE_QUOTE",158:"]",167:"BACKTICK",169:"PARTIAL_VALUE",171:"<hive>explode",172:"<hive>posexplode",174:"<hive>LATERAL",175:"VIEW",177:"<hive>AS",178:"JOIN",181:"ON"},
productions_: [0,[3,1],[3,1],[6,2],[6,1],[8,2],[8,1],[9,0],[10,4],[10,3],[11,1],[11,3],[14,1],[14,1],[14,1],[14,1],[14,3],[14,2],[14,1],[15,3],[15,2],[15,2],[16,1],[16,1],[20,7],[20,6],[20,5],[20,4],[20,3],[20,2],[22,1],[22,1],[23,1],[23,1],[24,1],[24,1],[21,5],[21,5],[21,4],[21,3],[21,2],[21,2],[35,1],[39,1],[37,1],[37,3],[41,3],[41,2],[41,1],[43,1],[45,1],[46,1],[17,1],[17,1],[17,2],[51,1],[51,1],[54,0],[54,2],[54,3],[54,3],[54,1],[58,2],[58,3],[58,4],[62,1],[62,3],[63,3],[63,7],[64,5],[64,2],[64,2],[69,1],[69,2],[69,3],[70,1],[70,1],[70,1],[72,0],[49,3],[49,4],[49,5],[49,7],[49,7],[48,6],[48,5],[48,4],[48,3],[48,6],[48,4],[73,1],[73,1],[74,3],[77,1],[77,3],[78,1],[79,2],[79,2],[79,4],[81,0],[71,2],[82,1],[82,1],[59,1],[59,1],[25,3],[25,5],[25,4],[25,3],[25,3],[25,2],[90,1],[90,1],[90,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[80,1],[18,4],[18,3],[111,1],[111,2],[109,0],[112,2],[112,2],[113,1],[113,2],[116,1],[116,1],[116,1],[116,1],[116,1],[38,2],[38,2],[121,1],[47,1],[47,3],[122,1],[122,3],[122,3],[124,2],[124,1],[126,1],[126,3],[126,3],[126,3],[126,4],[127,1],[127,1],[128,1],[128,1],[128,1],[128,1],[128,1],[128,1],[131,3],[131,2],[138,1],[138,2],[141,3],[132,1],[132,1],[132,1],[142,1],[143,2],[144,0],[145,1],[145,3],[145,3],[146,1],[146,2],[146,3],[117,3],[117,2],[118,3],[118,2],[119,2],[119,2],[110,1],[110,2],[110,2],[110,1],[151,1],[151,3],[147,1],[147,6],[147,4],[147,3],[155,1],[155,3],[155,2],[155,3],[155,3],[155,5],[155,5],[155,1],[159,1],[159,3],[115,1],[115,3],[160,1],[161,1],[161,1],[161,1],[163,2],[163,3],[162,1],[166,1],[166,3],[168,3],[168,5],[168,5],[168,7],[168,6],[168,3],[168,5],[168,2],[168,3],[40,1],[40,2],[40,1],[40,2],[170,4],[170,4],[170,4],[170,4],[165,1],[165,2],[173,5],[173,4],[173,5],[173,4],[173,3],[173,2],[176,2],[176,6],[164,4],[164,4],[164,3],[179,1],[180,2]],
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
case 17: case 18:

     suggestDdlAndDmlKeywords();
   
break;
case 19: case 21:

     suggestDatabases();
   
break;
case 20:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
case 25:

     suggestKeywords([ 'TABLE' ]);
   
break;
case 26:

     suggestKeywords([ 'INTO' ]);
   
break;
case 28:

     suggestKeywords([ 'INPATH' ]);
   
break;
case 29:

     suggestKeywords([ 'DATA' ]);
   
break;
case 36: case 38: case 128:

     linkTablePrimaries();
   
break;
case 37:

     suggestKeywords([ 'WHERE' ]);
   
break;
case 39:

     suggestKeywords([ 'SET' ]);
   
break;
case 41: case 134:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 43:

     // TODO: Replace with TablePrimary?
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 47:

     suggestKeywords([ '=' ]);
   
break;
case 48: case 143: case 180:

     suggestColumns();
   
break;
case 54:

     if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
       suggestKeywords(['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
   
break;
case 58:

     suggestKeywords(['NOT EXISTS']);
   
break;
case 59:

     suggestKeywords(['EXISTS']);
   
break;
case 61:

     suggestKeywords(['IF NOT EXISTS']);
   
break;
case 71:

     suggestKeywords(['DBPROPERTIES']);
   
break;
case 75:

     parser.yy.afterComment = true;
   
break;
case 76:

     parser.yy.afterHdfsLocation = true;
   
break;
case 77:

     parser.yy.afterHiveDbProperties = true;
   
break;
case 78:

     delete parser.yy.afterComment;
     delete parser.yy.afterHdfsLocation;
     delete parser.yy.afterHiveDbProperties;
   
break;
case 81:

     if (parser.yy.dialect === 'hive') {
       suggestKeywords(['COMMENT', 'LOCATION', 'WITH DBPROPERTIES']);
     } else if (parser.yy.dialect === 'impala') {
       suggestKeywords(['COMMENT', 'LOCATION']);
     }
   
break;
case 83:

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
case 85: case 86: case 87:

      if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
        suggestKeywords(['EXTERNAL']);
      }
    
break;
case 88:

     if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
       suggestKeywords(['LOCATION']);
     }
   
break;
case 97: case 99:

     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   
break;
case 106:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 107:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 108:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 109:

     suggestHdfs({ path: '' });
   
break;
case 110:

      suggestHdfs({ path: '' });
    
break;
case 132:

     delete parser.yy.afterGroupBy;
     delete parser.yy.afterLimit;
     delete parser.yy.afterOrderBy;
     delete parser.yy.afterWhere;
   
break;
case 137:

     parser.yy.afterWhere = true;
   
break;
case 138:

     parser.yy.afterGroupBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 139:

     parser.yy.afterOrderBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 140:

     parser.yy.afterLimit = true;
     delete parser.yy.result.suggestStar;
   
break;
case 141:

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
case 148:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 154:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 158: case 170: case 173:

     this.$ = $$[$0];
   
break;
case 166:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 174:

     this.$ = parser.yy.identifierChain;
     delete parser.yy.identifierChain;
   
break;
case 175:

     parser.yy.identifierChain = [];
   
break;
case 177:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 179:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 181:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 183: case 185:

     suggestKeywords(['BY']);
   
break;
case 187:

     suggestNumbers([1, 5, 10]);
   
break;
case 189: case 190:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 194:

     this.$ = { name: $$[$0] }
   
break;
case 195:

     this.$ = { name: $$[$0-5], key: '"' + $$[$0-2] + '"' }
   
break;
case 196:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 197:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 199:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 200:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 202:

      delete parser.yy.derivedColumnChain;
   
break;
case 203: case 204:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 205:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 206:

     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 207:

     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 211:

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
case 212:

     addTablePrimary($$[$0]);
   
break;
case 214:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], lateralViews: $$[$0] }
   
break;
case 215:

     this.$ = { identifierChain: [ { name: $$[$0-2] } ], alias: $$[$0-1], lateralViews: $$[$0] };
   
break;
case 218:

     this.$ = $$[$0-2];
   
break;
case 219:

     this.$ = { identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] }
   
break;
case 220:

     this.$ = { identifierChain: [ { name: $$[$0-3] }, { name: $$[$0] } ] }
   
break;
case 221:

     this.$ = { identifierChain: [ { name: $$[$0-4] }, { name: $$[$0-1] } ] }
   
break;
case 222:

     this.$ = { identifierChain: [ { name: $$[$0-5] }, { name: $$[$0-1] } ] }
   
break;
case 223:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-4] } ] };
   
break;
case 224:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-2] } ] };
   
break;
case 225:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-3] } ] };
   
break;
case 226:

     this.$ = { partial: true, identifierChain: [ ] };
   
break;
case 227:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ] }
   
break;
case 228:

     this.$ = { identifierChain: [ { name: $$[$0] } ] }
   
break;
case 229:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] };
   
break;
case 231:

     this.$ = { identifierChain: $$[$0-1].identifierChain, alias: $$[$0] }
   
break;
case 232:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 234:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 236:

     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 237:

     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 238:

     this.$ = { udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }
   
break;
case 239:

      this.$ = { udtf: $$[$0-1], columnAliases: $$[$0] }
    
break;
case 240: case 241:

     suggestKeywords(['AS']);
   
break;
case 242:

     suggestKeywords(['explode', 'posexplode']);
   
break;
case 243:

     suggestKeywords(['VIEW']);
   
break;
case 244:

     this.$ = [ $$[$0] ]
   
break;
case 245:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 247:

     suggestKeywords(['ON']);
   
break;
case 248:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,7,19,28,29,34,50,108],[2,7],{10:1,9:2}),{1:[3]},{3:10,4:$V0,5:$V1,7:$V2,11:3,14:4,15:5,16:6,17:7,18:8,19:$V3,20:12,21:13,22:20,28:$V4,29:$V5,34:$V6,48:14,49:15,50:$V7,108:$V8},{12:[1,24],13:[1,25]},o($V9,[2,10]),o($V9,[2,12]),o($V9,[2,13]),o($V9,[2,14]),o($V9,[2,15]),{5:[1,26]},o($V9,[2,18]),{4:[1,28],7:[1,27]},o($V9,[2,22]),o($V9,[2,23]),o($V9,[2,52]),o($V9,[2,53]),{4:$Va,6:29,7:$Vb,27:[1,31],51:32,52:[1,37],53:[1,38],73:30,75:[1,35],76:[1,36]},o([4,5,7,154],[2,132],{109:39}),o($Vc,[2,1]),o($Vc,[2,2]),{4:$Va,6:41,7:$Vb,23:40,30:[1,42],31:[1,43]},{4:$Va,6:45,7:[1,47],35:44,39:46,40:48,167:$Vd,168:49},o($Ve,[2,30]),o($Ve,[2,31]),{3:10,4:$V0,5:$V1,7:$V2,13:[1,51],14:52,15:5,16:6,17:7,18:8,19:$V3,20:12,21:13,22:20,28:$V4,29:$V5,34:$V6,48:14,49:15,50:$V7,108:$V8},{1:[2,9]},o($V9,[2,17],{7:[1,53]}),o($V9,[2,20],{5:[1,54]}),o($V9,[2,21]),o($V9,[2,54],{27:[1,55]}),{27:[1,56]},{7:[1,57]},o($Vf,[2,57],{54:58,4:[1,60],55:[1,59]}),{5:$Vg},o($Vh,$Vi),{27:[2,90]},{27:[2,91]},o($Vj,[2,55]),o($Vj,[2,56]),{3:67,4:$V0,5:$V1,7:$Vk,110:62,147:66,151:63,154:[1,64],155:65},{4:$Va,6:70,7:$Vb,24:69,32:[1,71],33:[1,72]},o($V9,[2,29]),o($Vl,[2,32]),o($Vl,[2,33]),o($V9,[2,40],{4:[1,74],36:[1,73]}),o($V9,[2,41]),o($Vm,[2,42]),o($Vm,$Vn,{90:76,5:$Vg,7:[1,75],91:$Vo,92:$Vp,93:$Vq}),o($Vm,[2,43]),o($Vr,[2,230],{7:[1,80]}),{61:[1,81],169:[1,82]},{1:[2,8]},o($V9,[2,11]),o($V9,[2,16]),o($V9,[2,19]),o($V9,[2,87],{7:[1,83]}),{7:[1,84]},{67:$Vs,74:85},o($V9,[2,79],{7:[1,87]}),{4:$Va,6:88,7:$Vb,56:[1,89]},o($Vf,[2,61]),o($Vh,[2,3]),o($V9,[2,129],{111:90,112:91,114:[1,92]}),o($Vt,[2,188],{6:93,4:$Va,7:$Vb,42:$Vu}),o($Vt,[2,191],{6:95,4:$Va,7:$Vb}),o($Vv,[2,192]),o($Vv,[2,198],{90:96,5:[1,97],91:$Vo,92:$Vp,93:$Vq}),o($Vv,[2,205]),o($Vw,$Vx,{156:$Vy}),{25:99,87:$Vz},o($V9,[2,28]),{87:[2,34]},{87:[2,35]},{4:$Va,6:104,7:$VA,37:101,41:102,43:103},o($V9,[2,39]),o($Vm,$VB),{5:$VC,7:[1,106],8:108,167:[1,107]},o($VD,[2,111]),o($VD,$VE),o($VD,$VF),o($Vr,[2,231]),{167:[1,110]},o($VG,[2,226]),o($V9,[2,86],{74:111,67:$Vs}),{67:$Vs,74:112},o($V9,[2,89]),{7:$VH,77:113,78:114,79:115},o([65,83,84,85,86],[2,78],{72:118,4:[1,117],12:$VI,13:$VI}),o($Vf,[2,58]),{4:$Va,6:119,7:$Vb,57:[1,120]},o($V9,[2,128]),o($V9,[2,130],{113:121,116:122,38:123,117:124,118:125,119:126,4:$VJ,120:$VK,149:$VL,152:$VM,153:$VN}),{4:$Va,6:133,7:[1,135],40:140,115:132,160:134,161:136,162:137,163:138,164:139,167:$Vd,168:49},o($Vt,[2,189]),{3:67,4:$V0,5:$V1,7:$Vk,147:66,155:141},o($Vt,[2,190]),{5:$VC,7:$VO,8:142,147:146,154:[1,143],159:144},o($Vv,[2,200]),{139:[1,148],157:[1,147],158:[1,149]},o($V9,[2,27],{6:151,4:$Va,7:$Vb,26:[1,150]}),{5:[1,153],88:[1,152]},o($V9,[2,38],{38:154,4:[1,155],42:[1,156],120:$VK}),o($VP,[2,44]),{4:[1,158],44:[1,157]},o($VP,[2,48]),o([4,44],[2,49],{5:$Vg}),o($VG,[2,219],{5:$VQ}),{61:[1,160]},o($VG,[2,224]),o($VR,[2,6]),o($VG,[2,227],{90:161,91:$Vo,92:$Vp,93:$Vq}),o($V9,[2,85]),{4:$Va,6:163,7:$Vb,71:162,82:164,83:$VS,84:$VT},{42:[1,168],68:[1,167]},o($VU,[2,93]),o($VU,[2,95]),{4:$Va,6:170,7:$Vb,80:169,94:[1,171],95:[1,172],96:[1,173],97:[1,174],98:[1,175],99:[1,176],100:[1,177],101:[1,178],102:[1,179],103:[1,180],104:[1,181],105:[1,182],106:[1,183],107:[1,184]},o($V9,[2,81]),{58:187,59:190,64:189,65:$VV,69:185,70:186,71:188,82:164,83:$VS,84:$VT,85:$VW,86:$VX},o($Vf,[2,59]),o($Vf,[2,60]),o($V9,[2,131],{38:123,117:124,118:125,119:126,116:194,4:$VJ,120:$VK,149:$VL,152:$VM,153:$VN}),o($VY,[2,135]),o($VY,[2,137]),o($VY,[2,138]),o($VY,[2,139]),o($VY,[2,140]),o($VY,[2,141]),o($VZ,$V_,{121:195,47:197,122:198,124:199,126:201,127:202,131:203,132:204,142:206,138:207,141:208,143:209,144:213,4:[1,196],56:$V$,60:$V01,67:$V11,139:$V21,140:$V31}),{4:$Va,6:215,7:$Vb,150:[1,214]},{4:$Va,6:217,7:$Vb,150:[1,216]},{4:$Va,6:219,7:$Vb,139:[1,218]},o($VY,[2,133],{42:[1,220]}),o($VY,[2,134]),o($V41,[2,208],{178:$V51}),o([4,12,13,42,120,149,152,153,178],$Vn,{90:76,165:222,173:224,5:$Vg,7:$V61,91:$Vo,92:$Vp,93:$Vq,174:$V71}),o($V81,[2,210]),o($V81,[2,211]),o($V81,[2,212]),o($V81,[2,213]),o($V81,[2,216]),o($Vv,[2,193]),o($Vv,[2,199]),o($Vv,[2,201]),o($Vv,[2,202],{90:228,91:$Vo,92:[1,226],93:[1,227]}),o($V91,$Vx,{5:$VQ,156:$Vy}),o($V91,[2,206]),{7:[1,229]},{158:[1,230]},o($Vw,[2,197]),{4:$Va,6:232,7:$Vb,27:[1,231]},o($V9,[2,26]),{5:[1,234],89:[1,233]},o($Va1,[2,110],{89:[1,235]}),o($V9,[2,36]),o($V9,[2,37]),{4:$Va,6:104,7:$VA,41:236,43:103},o($VZ,$V_,{122:198,124:199,126:201,127:202,131:203,132:204,142:206,138:207,141:208,143:209,144:213,45:237,46:238,47:239,56:$V$,60:$V01,67:$V11,139:$V21,140:$V31}),o($VP,[2,47]),o($VR,[2,5]),{167:[1,240]},{5:[1,243],7:[1,241],167:[1,242]},o($V9,[2,84]),o($V9,[2,88]),{25:244,87:$Vz},{87:[2,101]},{87:[2,102]},o([4,7,12,13,83,84],[2,92]),{7:$VH,78:245,79:115},o($VU,[2,96]),o($VU,[2,97],{81:246,2:[2,99]}),o($VU,[2,114]),o($VU,[2,115]),o($VU,[2,116]),o($VU,[2,117]),o($VU,[2,118]),o($VU,[2,119]),o($VU,[2,120]),o($VU,[2,121]),o($VU,[2,122]),o($VU,[2,123]),o($VU,[2,124]),o($VU,[2,125]),o($VU,[2,126]),o($VU,[2,127]),{2:[1,247],4:[1,248]},o($Vi,[2,72],{82:164,58:187,71:188,64:189,59:190,70:249,65:$VV,83:$VS,84:$VT,85:$VW,86:$VX}),o($Vb1,[2,75]),o($Vb1,[2,76]),o($Vb1,[2,77]),{60:[1,250]},{4:[1,252],66:[1,251]},{60:[2,103]},{60:[2,104]},o($VY,[2,136]),o($VY,[2,142]),o($VY,[2,143]),o($V81,[2,144],{123:$Vc1}),o($Vd1,[2,145]),o($Vd1,[2,147],{125:[1,254]}),o($VZ,$V_,{127:202,131:203,132:204,142:206,138:207,141:208,143:209,144:213,126:255,60:$V01,67:$V11,139:$V21,140:$V31}),o($Ve1,[2,151]),o($Ve1,[2,152],{128:256,44:[1,258],129:[1,257],133:[1,259],134:[1,260],135:[1,261],136:[1,262],137:[1,263]}),o($Vf1,[2,157]),o($Vf1,[2,158]),o($VZ,$V_,{122:198,124:199,126:201,127:202,131:203,132:204,142:206,138:207,141:208,143:209,144:213,47:264,3:265,4:$V0,5:$V1,56:$V$,60:$V01,67:$V11,139:$V21,140:$V31}),o($Vf1,[2,170]),o($Vf1,[2,171]),o($Vf1,[2,172]),o($Vf1,[2,173]),o($Vf1,[2,167]),{139:[1,266]},{61:[1,267]},{7:$Vk,145:268,146:269,147:270,148:$Vg1},{3:67,4:$V0,5:$V1,7:$Vk,147:66,151:272,155:65},o($VY,[2,183]),{3:67,4:$V0,5:$V1,7:$Vk,147:66,151:273,155:65},o($VY,[2,185]),o($VY,[2,186]),o($VY,[2,187]),{7:$Vh1,40:140,160:274,161:136,162:137,163:138,164:139,167:$Vd,168:49},{4:[1,277],7:$Vh1,40:140,160:276,161:136,162:137,163:138,164:139,167:$Vd,168:49},o($V81,[2,214],{173:278,174:$V71}),o($V81,$VB,{173:224,165:279,174:$V71}),o($Vi1,[2,236]),{4:$Va,6:281,7:$Vb,175:[1,280]},{5:[1,282],7:$VE},{5:[1,283],7:$VF},{7:$Vk,147:284},{157:[1,285]},o($Vw,[2,196]),{7:[1,286]},o($V9,[2,25]),o($Va1,[2,105]),o($Va1,[2,108],{88:[1,287],89:[1,288]}),o($Va1,[2,109]),o($VP,[2,45]),o($VP,[2,46]),o($VP,[2,50]),o($VP,[2,51],{123:$Vc1}),o($VG,[2,221]),o($VG,[2,220]),{61:[1,289],169:[1,290]},o($VG,[2,225]),o([2,4,12,13,65,83,84,85,86],[2,100]),o($VU,[2,94]),{2:[1,291]},o($V9,[2,82]),o($V9,[2,83]),o($Vi,[2,73],{82:164,58:187,71:188,64:189,59:190,70:292,65:$VV,83:$VS,84:$VT,85:$VW,86:$VX}),o($Vb1,[2,62],{61:[1,293]}),o($Vb1,[2,70],{67:[1,294]}),o($Vb1,[2,71]),o($VZ,$V_,{124:199,126:201,127:202,131:203,132:204,142:206,138:207,141:208,143:209,144:213,122:295,56:$V$,60:$V01,67:$V11,139:$V21,140:$V31}),o($VZ,$V_,{124:199,126:201,127:202,131:203,132:204,142:206,138:207,141:208,143:209,144:213,122:297,4:[1,296],56:$V$,60:$V01,67:$V11,139:$V21,140:$V31}),o($Ve1,[2,150]),o($VZ,$V_,{131:203,132:204,142:206,138:207,141:208,143:209,144:213,127:298,3:299,4:$V0,5:$V1,60:$V01,67:$V11,139:$V21,140:$V31}),{56:[1,301],130:[1,300]},o($Vj1,[2,159]),o($Vj1,[2,160]),o($Vj1,[2,161]),o($Vj1,[2,162]),o($Vj1,[2,163]),o($Vj1,[2,164]),{68:[1,302],123:$Vc1},o($Vf1,[2,166]),o($Vf1,[2,168]),{60:[1,303]},o($Vf1,[2,174],{90:304,91:$Vo,92:$Vp,93:$Vq}),o($Vk1,[2,176]),o($Vk1,[2,179],{5:[1,305]}),{7:[1,306]},o($VY,[2,182],{42:$Vu}),o($VY,[2,184],{42:$Vu}),o($V41,[2,209],{178:$V51}),o($V81,$Vn,{90:76,165:222,173:224,7:$V61,91:$Vo,92:$Vp,93:$Vq,174:$V71}),{4:[1,308],178:$V51,179:307,180:309,181:[1,310]},o($V81,[2,248]),o($Vi1,[2,237]),o($V81,[2,215],{173:278,174:$V71}),{4:$Va,6:312,7:$Vb,170:311,171:[1,313],172:[1,314]},o($Vi1,[2,243]),o($Vv,[2,203]),o($Vv,[2,204]),o($V91,[2,207]),{158:[1,315]},o($V9,[2,24]),{89:[1,316]},o($Va1,[2,107]),{167:[1,317]},o($VG,[2,223]),o($VU,[2,98]),o($Vi,[2,74]),o($Vb1,[2,63],{60:[1,318]}),{7:$Vl1,60:$Vm1,62:319,63:320},o($Vd1,[2,146]),o($Vd1,[2,148]),o($Vd1,[2,149]),o($Ve1,[2,153]),o($Ve1,[2,154]),o($Ve1,[2,155]),{130:[1,323]},o($Vf1,[2,165]),o($Vf1,[2,169]),{5:[1,324],7:$Vk,146:325,147:270,148:$Vg1},o($Vk1,[2,180]),{148:[1,326]},o($V81,[2,246]),o($V81,[2,247]),o($V81,[2,249]),o($VZ,$V_,{47:197,122:198,124:199,126:201,127:202,131:203,132:204,142:206,138:207,141:208,143:209,144:213,121:327,56:$V$,60:$V01,67:$V11,139:$V21,140:$V31}),{4:$Va,6:330,7:[1,328],176:329,177:$Vn1},o($Vi1,[2,242]),{67:[1,332]},{67:[1,333]},o($Vw,[2,195]),o($Va1,[2,106]),o($VG,[2,222]),o($Vb1,[2,64]),{42:[1,335],68:[1,334]},o($VU,[2,65]),{44:[1,336]},{61:[1,337]},o($Ve1,[2,156]),o($Vk1,[2,177]),o($Vk1,[2,178]),o($Vk1,[2,181]),o($V81,[2,250]),{4:$Va,5:$Vg,6:339,7:$Vb,176:338,177:$Vn1},o($Vi1,[2,239]),o($Vi1,[2,241]),{7:[1,340],67:[1,341]},{5:$VC,7:$VO,8:343,147:146,159:342},{5:$VC,7:$VO,8:345,147:146,159:344},o($Vb1,[2,69]),{7:$Vl1,60:$Vm1,63:346},{7:[1,347]},{60:[1,348]},o($Vi1,[2,238]),o($Vi1,[2,240]),o($Vi1,[2,244]),{7:[1,349]},{68:[1,350],90:228,91:$Vo,92:$Vp,93:$Vq},{2:[1,351]},{68:[1,352],90:228,91:$Vo,92:$Vp,93:$Vq},{2:[1,353]},o($VU,[2,66]),o($VU,[2,67]),{44:[1,354]},{42:[1,355]},o($Vo1,[2,232]),o($Vo1,[2,233]),o($Vo1,[2,234]),o($Vo1,[2,235]),{60:[1,356]},{7:[1,357]},{61:[1,358]},{68:[1,359]},{60:[1,360]},o($Vi1,[2,245]),o($VU,[2,68])],
defaultActions: {25:[2,9],35:[2,90],36:[2,91],51:[2,8],71:[2,34],72:[2,35],165:[2,101],166:[2,102],192:[2,103],193:[2,104]},
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
case 5: return 125; 
break;
case 6: return 97; 
break;
case 7: return 98; 
break;
case 8: return 150; 
break;
case 9: return 103; 
break;
case 10: return 50; 
break;
case 11: return 52; 
break;
case 12: return 102; 
break;
case 13: return 100; 
break;
case 14: return 57; 
break;
case 15: return 99; 
break;
case 16: return 114; 
break;
case 17: return 149; 
break;
case 18: return 55; 
break;
case 19: return 96; 
break;
case 20: return 26; 
break;
case 21: return 129; 
break;
case 22: return 178; 
break;
case 23: return 56; 
break;
case 24: return 181; 
break;
case 25: return 123; 
break;
case 26: return 152; 
break;
case 27: return 53; 
break;
case 28: determineCase(yy_.yytext); return 108; 
break;
case 29: return 36; 
break;
case 30: return 95; 
break;
case 31: return 101; 
break;
case 32: return 27; 
break;
case 33: return 105; 
break;
case 34: return 94; 
break;
case 35: determineCase(yy_.yytext); return 34; 
break;
case 36: determineCase(yy_.yytext); return 19; 
break;
case 37: return 104; 
break;
case 38: return 175; 
break;
case 39: return 120; 
break;
case 40: return 177; 
break;
case 41: return 106; 
break;
case 42: return 85; 
break;
case 43: return 30; 
break;
case 44: return 107; 
break;
case 45: return 75; 
break;
case 46: this.begin('hdfs'); return 32; 
break;
case 47: return 174; 
break;
case 48: return 28; 
break;
case 49: this.begin('hdfs'); return 83; 
break;
case 50: return 171; 
break;
case 51: return 172; 
break;
case 52: return 93; 
break;
case 53: return 86; 
break;
case 54: return 31; 
break;
case 55: return 76; 
break;
case 56: this.begin('hdfs'); return 33; 
break;
case 57: return 29; 
break;
case 58: this.begin('hdfs'); return 84; 
break;
case 59: return 92; 
break;
case 60: return 139; 
break;
case 61: return 7; 
break;
case 62: parser.yy.cursorFound = true; return 4; 
break;
case 63: parser.yy.cursorFound = true; return 5; 
break;
case 64: return 87; 
break;
case 65: return 88; 
break;
case 66: this.popState(); return 89; 
break;
case 67: return 13; 
break;
case 68: return yy_.yytext; 
break;
case 69: return yy_.yytext; 
break;
case 70: return 156; 
break;
case 71: return 158; 
break;
case 72: this.begin('backtickedValue'); return 167; 
break;
case 73: if (yy_.yytext.indexOf('CURSOR|') !== -1) {
                                        this.popState();
                                        return 169;
                                      }
                                      return 61;
                                    
break;
case 74: this.popState(); return 167; 
break;
case 75: this.begin('singleQuotedValue'); return 60; 
break;
case 76: return 61; 
break;
case 77: this.popState(); return 60; 
break;
case 78: return 157; 
break;
case 79: return 13; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DATABASE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:EXISTS\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:IF\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:SCHEMA\b)/i,/^(?:SELECT\b)/i,/^(?:SET\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:AS\b)/i,/^(?:BINARY\b)/i,/^(?:COMMENT\b)/i,/^(?:DATA\b)/i,/^(?:DATE\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:COMMENT\b)/i,/^(?:DATA\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:[.])/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:\s+['])/i,/^(?:[^'|]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>]+)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[62,63,64,65,66,67],"inclusive":false},"singleQuotedValue":{"rules":[76,77],"inclusive":false},"backtickedValue":{"rules":[73,74],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,60,61,68,69,70,71,72,75,78,79],"inclusive":true},"impala":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,53,54,55,56,57,58,59,60,61,68,69,70,71,72,75,78,79],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,60,61,68,69,70,71,72,75,78,79],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});