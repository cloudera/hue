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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,16],$V1=[1,17],$V2=[1,9],$V3=[1,11],$V4=[1,20],$V5=[1,21],$V6=[1,19],$V7=[1,14],$V8=[1,15],$V9=[11,12],$Va=[1,33],$Vb=[1,32],$Vc=[4,11,12,41,43,55,96,99,101,106,110,111,112,113,114,127,130,131,157,160],$Vd=[1,45],$Ve=[4,7,29,30],$Vf=[1,53],$Vg=[2,4,11,12,26,41,55,90,96,127,130,131,153,157,160],$Vh=[1,59],$Vi=[1,60],$Vj=[4,7,31,32],$Vk=[4,11,12,35],$Vl=[2,193],$Vm=[1,69],$Vn=[1,70],$Vo=[1,71],$Vp=[4,11,12,35,41,96,127,130,131,157,160],$Vq=[1,78],$Vr=[11,12,90],$Vs=[1,83],$Vt=[4,7,11,12,41,90,96,127,130,131],$Vu=[4,5,7,11,12,41,55,67,68,69,90,96,127,130,131],$Vv=[1,89],$Vw=[1,94],$Vx=[2,194],$Vy=[5,7,126,132,146],$Vz=[2,77],$VA=[2,78],$VB=[4,7,11,12,35,41,96,127,130,131,157,160],$VC=[1,104],$VD=[1,111],$VE=[1,112],$VF=[1,113],$VG=[1,114],$VH=[1,115],$VI=[4,11,12,41,96],$VJ=[41,55],$VK=[4,11,12,96,127,130,131],$VL=[7,126],$VM=[2,140],$VN=[1,179],$VO=[1,174],$VP=[1,184],$VQ=[1,185],$VR=[1,186],$VS=[4,11,12,41,96,127,130,131],$VT=[1,195],$VU=[1,197],$VV=[1,199],$VW=[4,11,12,41,96,127,130,131,157,160],$VX=[4,7,11,12,41,55,67,68,69,90,96,127,130,131],$VY=[4,7,11,12,25],$VZ=[1,221],$V_=[4,11,12,41,55,96,99,127,130,131,157,160],$V$=[4,11,12,41,55,96,99,101,127,130,131,157,160],$V01=[1,238],$V11=[1,239],$V21=[1,243],$V31=[4,11,12,41,96,127,130,131,153,157,160],$V41=[4,5,7,53,116,117,119,126],$V51=[4,11,12,41,43,55,67,68,69,96,99,101,106,110,111,112,113,114,127,130,131,157,160],$V61=[1,289],$V71=[4,7,156];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"NoOrPartialRegularIdentifier":6,"REGULAR_IDENTIFIER":7,"InitResults":8,"Sql":9,"SqlStatements":10,";":11,"EOF":12,"SqlStatement":13,"UseStatement":14,"DataManipulation":15,"TableDefinition":16,"QueryExpression":17,"USE":18,"LoadStatement":19,"UpdateStatement":20,"HiveOrImpalaLoad":21,"HiveOrImpalaData":22,"HiveOrImpalaInpath":23,"HdfsPath":24,"INTO":25,"TABLE":26,"<hive>LOAD":27,"<impala>LOAD":28,"<hive>DATA":29,"<impala>DATA":30,"<hive>INPATH":31,"<impala>INPATH":32,"UPDATE":33,"TargetTable":34,"SET":35,"SetClauseList":36,"WhereClause":37,"TableName":38,"LocalOrSchemaQualifiedName":39,"SetClause":40,",":41,"SetTarget":42,"=":43,"UpdateSource":44,"ValueExpression":45,"BooleanValueExpression":46,"CREATE":47,"TableScope":48,"TableElementList":49,"TableLocation":50,"<hive>EXTERNAL":51,"<impala>EXTERNAL":52,"(":53,"TableElements":54,")":55,"TableElement":56,"ColumnDefinition":57,"PrimitiveType":58,"ColumnDefinitionError":59,"HiveOrImpalaLocation":60,"<hive>LOCATION":61,"<impala>LOCATION":62,"HDFS_START_QUOTE":63,"HDFS_PATH":64,"HDFS_END_QUOTE":65,"AnyDot":66,".":67,"<impala>.":68,"<hive>.":69,"TINYINT":70,"SMALLINT":71,"INT":72,"BIGINT":73,"BOOLEAN":74,"FLOAT":75,"DOUBLE":76,"STRING":77,"DECIMAL":78,"CHAR":79,"VARCHAR":80,"TIMESTAMP":81,"<hive>BINARY":82,"<hive>DATE":83,"SELECT":84,"CleanUpSelectConditions":85,"SelectList":86,"TableExpression":87,"FromClause":88,"SelectConditionList":89,"FROM":90,"TableReferenceList":91,"SelectCondition":92,"GroupByClause":93,"OrderByClause":94,"LimitClause":95,"WHERE":96,"SearchCondition":97,"BooleanTerm":98,"OR":99,"BooleanFactor":100,"AND":101,"NOT":102,"BooleanTest":103,"Predicate":104,"CompOp":105,"IS":106,"TruthValue":107,"ParenthesizedBooleanValueExpression":108,"NonParenthesizedValueExpressionPrimary":109,"<>":110,"<":111,">":112,"<=":113,">=":114,"SignedInteger":115,"UNSIGNED_INTEGER":116,"-":117,"StringValue":118,"SINGLE_QUOTE":119,"VALUE":120,"ColumnReference":121,"BasicIdentifierChain":122,"InitIdentifierChain":123,"IdentifierChain":124,"Identifier":125,"\"":126,"GROUP":127,"BY":128,"ColumnList":129,"ORDER":130,"LIMIT":131,"*":132,"DerivedColumn":133,"ColumnIdentifier":134,"[":135,"DOUBLE_QUOTE":136,"]":137,"DerivedColumnChain":138,"TableReference":139,"TablePrimaryOrJoinedTable":140,"TablePrimary":141,"LateralViewDefinition":142,"JoinedTable":143,"LateralViews":144,"RegularOrBacktickedIdentifier":145,"BACKTICK":146,"RegularOrBackTickedSchemaQualifiedName":147,"PARTIAL_VALUE":148,"userDefinedTableGeneratingFunction":149,"<hive>explode":150,"<hive>posexplode":151,"LateralView":152,"<hive>LATERAL":153,"VIEW":154,"LateralViewColumnAliases":155,"<hive>AS":156,"JOIN":157,"JoinSpecification":158,"JoinCondition":159,"ON":160,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",7:"REGULAR_IDENTIFIER",11:";",12:"EOF",18:"USE",25:"INTO",26:"TABLE",27:"<hive>LOAD",28:"<impala>LOAD",29:"<hive>DATA",30:"<impala>DATA",31:"<hive>INPATH",32:"<impala>INPATH",33:"UPDATE",35:"SET",41:",",43:"=",47:"CREATE",51:"<hive>EXTERNAL",52:"<impala>EXTERNAL",53:"(",55:")",61:"<hive>LOCATION",62:"<impala>LOCATION",63:"HDFS_START_QUOTE",64:"HDFS_PATH",65:"HDFS_END_QUOTE",67:".",68:"<impala>.",69:"<hive>.",70:"TINYINT",71:"SMALLINT",72:"INT",73:"BIGINT",74:"BOOLEAN",75:"FLOAT",76:"DOUBLE",77:"STRING",78:"DECIMAL",79:"CHAR",80:"VARCHAR",81:"TIMESTAMP",82:"<hive>BINARY",83:"<hive>DATE",84:"SELECT",90:"FROM",96:"WHERE",99:"OR",101:"AND",102:"NOT",106:"IS",107:"TruthValue",110:"<>",111:"<",112:">",113:"<=",114:">=",116:"UNSIGNED_INTEGER",117:"-",119:"SINGLE_QUOTE",120:"VALUE",126:"\"",127:"GROUP",128:"BY",130:"ORDER",131:"LIMIT",132:"*",135:"[",136:"DOUBLE_QUOTE",137:"]",146:"BACKTICK",148:"PARTIAL_VALUE",150:"<hive>explode",151:"<hive>posexplode",153:"<hive>LATERAL",154:"VIEW",156:"<hive>AS",157:"JOIN",160:"ON"},
productions_: [0,[3,1],[3,1],[6,2],[6,1],[8,0],[9,4],[9,3],[10,1],[10,3],[13,1],[13,1],[13,1],[13,1],[13,3],[13,2],[13,1],[14,3],[14,2],[14,2],[15,1],[15,1],[19,7],[19,6],[19,5],[19,4],[19,3],[19,2],[21,1],[21,1],[22,1],[22,1],[23,1],[23,1],[20,5],[20,5],[20,4],[20,3],[20,2],[20,2],[34,1],[38,1],[36,1],[36,3],[40,3],[40,2],[40,1],[42,1],[44,1],[45,1],[16,6],[16,5],[16,4],[16,3],[16,6],[16,4],[16,2],[48,1],[48,1],[49,3],[54,1],[54,3],[56,1],[57,2],[57,2],[57,4],[59,0],[50,2],[60,1],[60,1],[24,3],[24,5],[24,4],[24,3],[24,3],[24,2],[66,1],[66,1],[66,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[58,1],[17,4],[17,3],[87,1],[87,2],[85,0],[88,2],[88,2],[89,1],[89,2],[92,1],[92,1],[92,1],[92,1],[92,1],[37,2],[37,2],[97,1],[46,1],[46,3],[98,1],[98,3],[98,3],[100,2],[100,1],[103,1],[103,3],[103,3],[103,3],[103,4],[104,1],[104,1],[105,1],[105,1],[105,1],[105,1],[105,1],[105,1],[108,3],[108,2],[115,1],[115,2],[118,3],[109,1],[109,1],[109,1],[121,1],[122,2],[123,0],[124,1],[124,3],[124,3],[125,1],[125,3],[93,3],[93,2],[94,3],[94,2],[95,2],[95,2],[86,1],[86,2],[86,2],[86,1],[129,1],[129,3],[134,1],[134,6],[134,4],[134,3],[133,1],[133,3],[133,2],[133,3],[133,3],[133,5],[133,5],[133,1],[138,1],[138,3],[91,1],[91,3],[139,1],[140,1],[140,1],[140,1],[142,2],[142,3],[141,1],[145,1],[145,3],[147,3],[147,5],[147,5],[147,7],[147,6],[147,4],[147,5],[147,2],[147,3],[147,3],[39,1],[39,2],[39,1],[39,2],[149,4],[149,4],[144,1],[144,2],[152,5],[152,4],[152,4],[152,3],[152,2],[155,2],[155,6],[143,4],[143,3],[158,1],[159,2]],
performAction: function anonymous(yytext, yyleng, yylineno, yy, yystate /* action[1] */, $$ /* vstack */, _$ /* lstack */) {
/* this == yyval */

var $0 = $$.length - 1;
switch (yystate) {
case 5:

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
case 6: case 7:

     prioritizeSuggestions();
     return parser.yy.result;
   
break;
case 15: case 16:

     suggestDdlAndDmlKeywords();
   
break;
case 17: case 19:

     suggestDatabases();
   
break;
case 18:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
case 23:

     suggestKeywords([ 'TABLE' ]);
   
break;
case 24:

     suggestKeywords([ 'INTO' ]);
   
break;
case 26:

     suggestKeywords([ 'INPATH' ]);
   
break;
case 27:

     suggestKeywords([ 'DATA' ]);
   
break;
case 34: case 36: case 93:

     linkTablePrimaries();
   
break;
case 35:

     suggestKeywords([ 'WHERE' ]);
   
break;
case 37:

     suggestKeywords([ 'SET' ]);
   
break;
case 39: case 99:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 41:

     // TODO: Replace with TablePrimary?
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 45:

     suggestKeywords([ '=' ]);
   
break;
case 46: case 108:

     suggestColumns();
   
break;
case 51: case 52: case 53:

      if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
        suggestKeywords(['EXTERNAL'])
      }
    
break;
case 54:

     if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
       suggestKeywords(['LOCATION'])
     }
   
break;
case 56:

      if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
        suggestKeywords(['EXTERNAL', 'TABLE'])
      } else {
        suggestKeywords(['TABLE'])
      }
    
break;
case 64: case 66:

     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   
break;
case 71:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 72:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 73:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 74:

     suggestHdfs({ path: '/' });
   
break;
case 75:

      suggestHdfs({ path: '/' });
    
break;
case 97:

     delete parser.yy.afterGroupBy;
     delete parser.yy.afterLimit;
     delete parser.yy.afterOrderBy;
     delete parser.yy.afterWhere;
   
break;
case 102:

     parser.yy.afterWhere = true;
   
break;
case 103:

     parser.yy.afterGroupBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 104:

     parser.yy.afterOrderBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 105:

     parser.yy.afterLimit = true;
     delete parser.yy.result.suggestStar;
   
break;
case 106:

     var keywords = [];
     if (!parser.yy.afterGroupBy) {
       keywords.push('GROUP BY');
     }
     if (parser.yy.dialect === 'hive' && !parser.yy.afterGroupBy && !parser.yy.afterWhere && !parser.yy.afterOrderBy && !parser.yy.afterLimit) {
       keywords.push('LATERAL');
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
case 113:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 119:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 123: case 135: case 138:

     this.$ = $$[$0];
   
break;
case 131:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 139:

     this.$ = parser.yy.identifierChain
     delete parser.yy.identifierChain;
   
break;
case 140:

     parser.yy.identifierChain = [];
   
break;
case 142:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 144:

     parser.yy.identifierChain.push({ name: $$[$0] });
   
break;
case 145:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 147: case 149:

     suggestKeywords(['BY']);
   
break;
case 151:

     suggestNumbers([1, 5, 10]);
   
break;
case 153:

      suggestTables({ prependFrom: true });
      suggestDatabases({ prependFrom: true, appendDot: true });
    
break;
case 154:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 158:

     this.$ = { name: $$[$0] }
   
break;
case 159:

     this.$ = { name: $$[$0-5], key: '"' + $$[$0-2] + '"' }
   
break;
case 160:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 161:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 163:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 164:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 166:

      delete parser.yy.derivedColumnChain;
   
break;
case 167: case 168:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 169:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 170:

     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 171:

     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 175:

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
case 176:

     addTablePrimary($$[$0]);
   
break;
case 178:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], lateralViews: $$[$0] }
   
break;
case 179:

     this.$ = { identifierChain: [ { name: $$[$0-2] } ], alias: $$[$0-1], lateralViews: $$[$0] };
   
break;
case 182:

     this.$ = $$[$0-2];
   
break;
case 183:

     this.$ = { identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] }
   
break;
case 184:

     this.$ = { identifierChain: [ { name: $$[$0-3] }, { name: $$[$0] } ] }
   
break;
case 185:

     this.$ = { identifierChain: [ { name: $$[$0-4] }, { name: $$[$0-1] } ] }
   
break;
case 186:

     this.$ = { identifierChain: [ { name: $$[$0-5] }, { name: $$[$0-1] } ] }
   
break;
case 187:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-4] } ] };
   
break;
case 188: case 189:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-3] } ] };
   
break;
case 190:

     this.$ = { partial: true, identifierChain: [ ] };
   
break;
case 191:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-2] } ] };
   
break;
case 192:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ] }
   
break;
case 193:

     this.$ = { identifierChain: [ { name: $$[$0] } ] }
   
break;
case 194:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] };
   
break;
case 196:

     this.$ = { identifierChain: $$[$0-1].identifierChain, alias: $$[$0] }
   
break;
case 197:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 198:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 199:

     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 200:

     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 201:

     this.$ = { udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }
   
break;
case 202:

      this.$ = { udtf: $$[$0-1], columnAliases: $$[$0] }
    
break;
case 203:

     suggestKeywords(['AS']);
   
break;
case 204:

     suggestKeywords(['explode', 'posexplode']);
   
break;
case 205:

     suggestKeywords(['VIEW']);
   
break;
case 206:

     this.$ = [ $$[$0] ]
   
break;
case 207:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 209:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,7,18,27,28,33,47,84],[2,5],{9:1,8:2}),{1:[3]},{3:10,4:$V0,5:$V1,7:$V2,10:3,13:4,14:5,15:6,16:7,17:8,18:$V3,19:12,20:13,21:18,27:$V4,28:$V5,33:$V6,47:$V7,84:$V8},{11:[1,22],12:[1,23]},o($V9,[2,8]),o($V9,[2,10]),o($V9,[2,11]),o($V9,[2,12]),o($V9,[2,13]),{5:[1,24]},o($V9,[2,16]),{4:[1,26],7:[1,25]},o($V9,[2,20]),o($V9,[2,21]),{4:$Va,6:28,7:$Vb,26:[1,29],48:27,51:[1,30],52:[1,31]},o([4,7,132],[2,97],{85:34}),o($Vc,[2,1]),o($Vc,[2,2]),{4:$Va,6:36,7:$Vb,22:35,29:[1,37],30:[1,38]},{4:$Va,6:40,7:[1,42],34:39,38:41,39:43,146:$Vd,147:44},o($Ve,[2,28]),o($Ve,[2,29]),{3:10,4:$V0,5:$V1,7:$V2,12:[1,46],13:47,14:5,15:6,16:7,17:8,18:$V3,19:12,20:13,21:18,27:$V4,28:$V5,33:$V6,47:$V7,84:$V8},{1:[2,7]},o($V9,[2,15],{7:[1,48]}),o($V9,[2,18],{5:[1,49]}),o($V9,[2,19]),{26:[1,50]},o($V9,[2,56],{26:[1,51]}),{7:[1,52]},{26:[2,57]},{26:[2,58]},{5:$Vf},o($Vg,[2,4]),{4:$Vh,7:$Vi,86:54,129:55,132:[1,56],133:57,134:58},{4:$Va,6:62,7:$Vb,23:61,31:[1,63],32:[1,64]},o($V9,[2,27]),o($Vj,[2,30]),o($Vj,[2,31]),o($V9,[2,38],{4:[1,66],35:[1,65]}),o($V9,[2,39]),o($Vk,[2,40]),o($Vk,$Vl,{66:68,5:$Vf,7:[1,67],67:$Vm,68:$Vn,69:$Vo}),o($Vk,[2,41]),o($Vp,[2,195],{7:[1,72]}),{120:[1,73],148:[1,74]},{1:[2,6]},o($V9,[2,9]),o($V9,[2,14]),o($V9,[2,17]),{7:[1,75]},o($V9,[2,53],{7:[1,76]}),{49:77,53:$Vq},o($Vg,[2,3]),o($V9,[2,94],{87:79,88:80,90:[1,81]}),o($Vr,[2,152],{6:82,4:$Va,7:$Vb,41:$Vs}),o($Vr,[2,155],{6:84,4:$Va,7:$Vb}),o($Vt,[2,156]),o($Vt,[2,162],{66:85,5:[1,86],67:$Vm,68:$Vn,69:$Vo}),o($Vt,[2,169]),o($Vu,[2,158],{135:[1,87]}),{24:88,63:$Vv},o($V9,[2,26]),{63:[2,32]},{63:[2,33]},{4:$Va,6:93,7:$Vw,36:90,40:91,42:92},o($V9,[2,37]),o($Vk,$Vx),{5:[1,97],7:[1,95],146:[1,96]},o($Vy,[2,76]),o($Vy,$Vz),o($Vy,$VA),o($Vp,[2,196]),{146:[1,98]},o($VB,[2,190]),{49:99,53:$Vq},o($V9,[2,52],{49:100,53:$Vq}),o($V9,[2,55]),{7:$VC,54:101,56:102,57:103},o($V9,[2,93]),o($V9,[2,95],{89:105,92:106,37:107,93:108,94:109,95:110,4:$VD,96:$VE,127:$VF,130:$VG,131:$VH}),{4:$Va,6:117,7:[1,119],39:124,91:116,139:118,140:120,141:121,142:122,143:123,146:$Vd,147:44},o($Vr,[2,153]),{4:$Vh,7:$Vi,133:125,134:58},o($Vr,[2,154]),{5:[1,126],7:$Vi,132:[1,127],134:129,138:128},o($Vt,[2,164]),{116:[1,131],136:[1,130],137:[1,132]},o($V9,[2,25],{6:134,4:$Va,7:$Vb,25:[1,133]}),{5:[1,136],64:[1,135]},o($V9,[2,36],{37:137,4:[1,138],41:[1,139],96:$VE}),o($VI,[2,42]),{4:[1,141],43:[1,140]},o($VI,[2,46]),o([4,43],[2,47],{5:$Vf}),o($VB,[2,183],{5:[1,142]}),{120:[1,143]},o($VB,[2,191]),o($VB,[2,192],{66:144,67:$Vm,68:$Vn,69:$Vo}),{4:$Va,6:146,7:$Vb,50:145,60:147,61:[1,148],62:[1,149]},o($V9,[2,51]),{41:[1,151],55:[1,150]},o($VJ,[2,60]),o($VJ,[2,62]),{4:$Va,6:153,7:$Vb,58:152,70:[1,154],71:[1,155],72:[1,156],73:[1,157],74:[1,158],75:[1,159],76:[1,160],77:[1,161],78:[1,162],79:[1,163],80:[1,164],81:[1,165],82:[1,166],83:[1,167]},o($V9,[2,96],{37:107,93:108,94:109,95:110,92:168,4:$VD,96:$VE,127:$VF,130:$VG,131:$VH}),o($VK,[2,100]),o($VK,[2,102]),o($VK,[2,103]),o($VK,[2,104]),o($VK,[2,105]),o($VK,[2,106]),o($VL,$VM,{97:169,46:171,98:172,100:173,103:175,104:176,108:177,109:178,121:180,115:181,118:182,122:183,123:187,4:[1,170],53:$VN,102:$VO,116:$VP,117:$VQ,119:$VR}),{4:$Va,6:189,7:$Vb,128:[1,188]},{4:$Va,6:191,7:$Vb,128:[1,190]},{4:$Va,6:193,7:$Vb,116:[1,192]},o($VK,[2,98],{41:[1,194]}),o($VK,[2,99]),o($VS,[2,172],{157:$VT}),o([4,11,12,41,96,127,130,131,157],$Vl,{66:68,144:196,152:198,5:$Vf,7:$VU,67:$Vm,68:$Vn,69:$Vo,153:$VV}),o($VW,[2,174]),o($VW,[2,175]),o($VW,[2,176]),o($VW,[2,177]),o($VW,[2,180]),o($Vt,[2,157]),o($Vt,[2,163]),o($Vt,[2,165]),o($Vt,[2,166],{66:202,67:$Vm,68:[1,200],69:[1,201]}),o($VX,[2,170]),{7:[1,203]},{137:[1,204]},o($Vu,[2,161]),{4:$Va,6:206,7:$Vb,26:[1,205]},o($V9,[2,24]),{5:[1,208],65:[1,207]},o($VY,[2,75],{65:[1,209]}),o($V9,[2,34]),o($V9,[2,35]),{4:$Va,6:93,7:$Vw,40:210,42:92},o($VL,$VM,{98:172,100:173,103:175,104:176,108:177,109:178,121:180,115:181,118:182,122:183,123:187,44:211,45:212,46:213,53:$VN,102:$VO,116:$VP,117:$VQ,119:$VR}),o($VI,[2,45]),o($VB,[2,188]),{146:[1,214]},{5:[1,217],7:[1,215],146:[1,216]},o($V9,[2,50]),o($V9,[2,54]),{24:218,63:$Vv},{63:[2,68]},{63:[2,69]},o([4,7,11,12,61,62],[2,59]),{7:$VC,56:219,57:103},o($VJ,[2,63]),o($VJ,[2,64],{59:220,2:[2,66]}),o($VJ,[2,79]),o($VJ,[2,80]),o($VJ,[2,81]),o($VJ,[2,82]),o($VJ,[2,83]),o($VJ,[2,84]),o($VJ,[2,85]),o($VJ,[2,86]),o($VJ,[2,87]),o($VJ,[2,88]),o($VJ,[2,89]),o($VJ,[2,90]),o($VJ,[2,91]),o($VJ,[2,92]),o($VK,[2,101]),o($VK,[2,107]),o($VK,[2,108]),o($VW,[2,109],{99:$VZ}),o($V_,[2,110]),o($V_,[2,112],{101:[1,222]}),o($VL,$VM,{104:176,108:177,109:178,121:180,115:181,118:182,122:183,123:187,103:223,53:$VN,116:$VP,117:$VQ,119:$VR}),o($V$,[2,116]),o($V$,[2,117],{105:224,43:[1,226],106:[1,225],110:[1,227],111:[1,228],112:[1,229],113:[1,230],114:[1,231]}),o($Vc,[2,122]),o($Vc,[2,123]),o($VL,$VM,{98:172,100:173,103:175,104:176,108:177,109:178,121:180,115:181,118:182,122:183,123:187,46:232,3:233,4:$V0,5:$V1,53:$VN,102:$VO,116:$VP,117:$VQ,119:$VR}),o($Vc,[2,135]),o($Vc,[2,136]),o($Vc,[2,137]),o($Vc,[2,138]),o($Vc,[2,132]),{116:[1,234]},{120:[1,235]},{7:$V01,124:236,125:237,126:$V11},{4:$Vh,7:$Vi,129:240,133:57,134:58},o($VK,[2,147]),{4:$Vh,7:$Vi,129:241,133:57,134:58},o($VK,[2,149]),o($VK,[2,150]),o($VK,[2,151]),{7:$V21,39:124,139:242,140:120,141:121,142:122,143:123,146:$Vd,147:44},{4:[1,245],7:$V21,39:124,139:244,140:120,141:121,142:122,143:123,146:$Vd,147:44},o($VW,[2,178],{152:246,153:$VV}),o($VW,$Vx,{152:198,144:247,153:$VV}),o($V31,[2,199]),{4:$Va,6:249,7:$Vb,154:[1,248]},{5:[1,250],7:$Vz},{5:[1,251],7:$VA},{7:$Vi,134:252},{136:[1,253]},o($Vu,[2,160]),{7:[1,254]},o($V9,[2,23]),o($VY,[2,70]),o($VY,[2,73],{64:[1,255],65:[1,256]}),o($VY,[2,74]),o($VI,[2,43]),o($VI,[2,44]),o($VI,[2,48]),o($VI,[2,49],{99:$VZ}),o($VB,[2,185]),o($VB,[2,184]),{120:[1,257],148:[1,258]},o($VB,[2,189]),o($V9,[2,67]),o($VJ,[2,61]),{2:[1,259]},o($VL,$VM,{100:173,103:175,104:176,108:177,109:178,121:180,115:181,118:182,122:183,123:187,98:260,53:$VN,102:$VO,116:$VP,117:$VQ,119:$VR}),o($VL,$VM,{100:173,103:175,104:176,108:177,109:178,121:180,115:181,118:182,122:183,123:187,98:262,4:[1,261],53:$VN,102:$VO,116:$VP,117:$VQ,119:$VR}),o($V$,[2,115]),o($VL,$VM,{108:177,109:178,121:180,115:181,118:182,122:183,123:187,104:263,3:264,4:$V0,5:$V1,53:$VN,116:$VP,117:$VQ,119:$VR}),{102:[1,266],107:[1,265]},o($V41,[2,124]),o($V41,[2,125]),o($V41,[2,126]),o($V41,[2,127]),o($V41,[2,128]),o($V41,[2,129]),{55:[1,267],99:$VZ},o($Vc,[2,131]),o($Vc,[2,133]),{119:[1,268]},o($Vc,[2,139],{66:269,67:$Vm,68:$Vn,69:$Vo}),o($V51,[2,141]),o($V51,[2,144]),{7:[1,270]},o($VK,[2,146],{41:$Vs}),o($VK,[2,148],{41:$Vs}),o($VS,[2,173],{157:$VT}),o($VW,$Vl,{66:68,144:196,152:198,7:$VU,67:$Vm,68:$Vn,69:$Vo,153:$VV}),{157:$VT,158:271,159:272,160:[1,273]},o($VW,[2,209]),o($V31,[2,200]),o($VW,[2,179],{152:246,153:$VV}),{4:$Va,6:275,7:$Vb,149:274,150:[1,276],151:[1,277]},o($V31,[2,205]),o($Vt,[2,167]),o($Vt,[2,168]),o($VX,[2,171]),{137:[1,278]},o($V9,[2,22]),{65:[1,279]},o($VY,[2,72]),{146:[1,280]},o($VB,[2,187]),o($VJ,[2,65]),o($V_,[2,111]),o($V_,[2,113]),o($V_,[2,114]),o($V$,[2,118]),o($V$,[2,119]),o($V$,[2,120]),{107:[1,281]},o($Vc,[2,130]),o($Vc,[2,134]),{5:[1,282],7:$V01,125:283,126:$V11},{126:[1,284]},o($VW,[2,208]),o($VW,[2,210]),o($VL,$VM,{46:171,98:172,100:173,103:175,104:176,108:177,109:178,121:180,115:181,118:182,122:183,123:187,97:285,53:$VN,102:$VO,116:$VP,117:$VQ,119:$VR}),{4:$Va,6:288,7:[1,286],155:287,156:$V61},o($V31,[2,204]),{53:[1,290]},{53:[1,291]},o($Vu,[2,159]),o($VY,[2,71]),o($VB,[2,186]),o($V$,[2,121]),o($V51,[2,142]),o($V51,[2,143]),o($V51,[2,145]),o($VW,[2,211]),{5:$Vf,155:292,156:$V61},o($V31,[2,202]),o($V31,[2,203]),{7:[1,293],53:[1,294]},{7:$Vi,134:129,138:295},{7:$Vi,134:129,138:296},o($V31,[2,201]),o($V31,[2,206]),{7:[1,297]},{55:[1,298],66:202,67:$Vm,68:$Vn,69:$Vo},{55:[1,299],66:202,67:$Vm,68:$Vn,69:$Vo},{41:[1,300]},o($V71,[2,197]),o($V71,[2,198]),{7:[1,301]},{55:[1,302]},o($V31,[2,207])],
defaultActions: {23:[2,7],30:[2,57],31:[2,58],46:[2,6],63:[2,32],64:[2,33],148:[2,68],149:[2,69]},
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
    result = parser.parse(beforeCursor + (beforeCursor.length == 0 || beforeCursor.indexOf(' ', beforeCursor.length - 1) !== -1 ? ' |CURSOR| ' : '|PARTIAL_CURSOR|') + afterCursor);
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
case 5: return 101; 
break;
case 6: return 73; 
break;
case 7: return 74; 
break;
case 8: return 128; 
break;
case 9: return 79; 
break;
case 10: return 47; 
break;
case 11: return 78; 
break;
case 12: return 76; 
break;
case 13: return 75; 
break;
case 14: return 90; 
break;
case 15: return 127; 
break;
case 16: return 72; 
break;
case 17: return 25; 
break;
case 18: return 106; 
break;
case 19: return 157; 
break;
case 20: return 102; 
break;
case 21: return 160; 
break;
case 22: return 99; 
break;
case 23: return 130; 
break;
case 24: determineCase(yy_.yytext); return 84; 
break;
case 25: return 35; 
break;
case 26: return 71; 
break;
case 27: return 77; 
break;
case 28: return 26; 
break;
case 29: return 81; 
break;
case 30: return 70; 
break;
case 31: determineCase(yy_.yytext); return 33; 
break;
case 32: determineCase(yy_.yytext); return 18; 
break;
case 33: return 80; 
break;
case 34: return 154; 
break;
case 35: return 96; 
break;
case 36: return 156; 
break;
case 37: return 82; 
break;
case 38: return 29; 
break;
case 39: return 83; 
break;
case 40: return 51; 
break;
case 41: this.begin('hdfs'); return 31; 
break;
case 42: return 153; 
break;
case 43: return 27; 
break;
case 44: this.begin('hdfs'); return 61; 
break;
case 45: return 150; 
break;
case 46: return 151; 
break;
case 47: return 69; 
break;
case 48: return 30; 
break;
case 49: return 52; 
break;
case 50: this.begin('hdfs'); return 32; 
break;
case 51: return 28; 
break;
case 52: this.begin('hdfs'); return 62; 
break;
case 53: return 68; 
break;
case 54: return 116; 
break;
case 55: return 7; 
break;
case 56: parser.yy.cursorFound = true; return 4; 
break;
case 57: parser.yy.cursorFound = true; return 5; 
break;
case 58: return 63; 
break;
case 59: return 64; 
break;
case 60: this.popState(); return 65; 
break;
case 61: return 12; 
break;
case 62: return yy_.yytext; 
break;
case 63: return yy_.yytext; 
break;
case 64: return 135; 
break;
case 65: return 137; 
break;
case 66: this.begin('backtickedValue'); return 146; 
break;
case 67: if (yy_.yytext.indexOf('CURSOR|') !== -1) {
                                        this.popState();
                                        return 148;
                                      }
                                      return 120;
                                    
break;
case 68: this.popState(); return 146; 
break;
case 69: this.begin('singleQuotedValue'); return 119; 
break;
case 70: return 120; 
break;
case 71: this.popState(); return 119; 
break;
case 72: return 136; 
break;
case 73: return 12; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:SELECT\b)/i,/^(?:SET\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:AS\b)/i,/^(?:BINARY\b)/i,/^(?:DATA\b)/i,/^(?:DATE\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:DATA\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:[.])/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:\s+['])/i,/^(?:[^'|]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[56,57,58,59,60,61],"inclusive":false},"singleQuotedValue":{"rules":[70,71],"inclusive":false},"backtickedValue":{"rules":[67,68],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,54,55,62,63,64,65,66,69,72,73],"inclusive":true},"impala":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,48,49,50,51,52,53,54,55,62,63,64,65,66,69,72,73],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,54,55,62,63,64,65,66,69,72,73],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});