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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,16],$V1=[1,17],$V2=[1,9],$V3=[1,11],$V4=[1,20],$V5=[1,21],$V6=[1,19],$V7=[1,14],$V8=[1,15],$V9=[12,13],$Va=[1,33],$Vb=[1,32],$Vc=[4,7,12,13,42,44,56,91,97,100,102,107,111,112,113,114,115,129,132,133,158,161],$Vd=[1,45],$Ve=[4,7,30,31],$Vf=[1,53],$Vg=[2,4,12,13,27,42,56,91,97,129,132,133,154,158,161],$Vh=[1,60],$Vi=[4,7,32,33],$Vj=[4,12,13,36],$Vk=[2,195],$Vl=[1,69],$Vm=[1,70],$Vn=[1,71],$Vo=[4,12,13,36,42,97,129,132,133,158,161],$Vp=[1,78],$Vq=[12,13,91],$Vr=[1,83],$Vs=[4,7,12,13,42,91,97,129,132,133],$Vt=[4,5,7,12,13,42,44,56,68,69,70,91,97,100,102,107,111,112,113,114,115,129,132,133,158,161],$Vu=[2,161],$Vv=[1,87],$Vw=[1,89],$Vx=[1,94],$Vy=[2,196],$Vz=[1,98],$VA=[5,7,128,134,147],$VB=[2,79],$VC=[2,80],$VD=[4,7,12,13,36,42,97,129,132,133,158,161],$VE=[1,105],$VF=[1,112],$VG=[1,113],$VH=[1,114],$VI=[1,115],$VJ=[1,116],$VK=[1,130],$VL=[4,12,13,42,97],$VM=[1,144],$VN=[2,4,7,12,13,36,42,91,97,129,132,133,158,161],$VO=[42,56],$VP=[4,12,13,97,129,132,133],$VQ=[7,128],$VR=[2,142],$VS=[1,181],$VT=[1,176],$VU=[1,186],$VV=[1,187],$VW=[1,188],$VX=[4,12,13,42,97,129,132,133],$VY=[1,197],$VZ=[1,199],$V_=[1,201],$V$=[4,12,13,42,97,129,132,133,158,161],$V01=[4,7,12,13,42,56,68,69,70,91,97,129,132,133],$V11=[4,7,12,13,26],$V21=[1,223],$V31=[4,12,13,42,56,97,100,129,132,133,158,161],$V41=[4,12,13,42,56,97,100,102,129,132,133,158,161],$V51=[4,12,13,42,44,56,97,100,102,107,111,112,113,114,115,129,132,133,158,161],$V61=[1,241],$V71=[1,245],$V81=[4,12,13,42,97,129,132,133,154,158,161],$V91=[4,5,7,54,117,118,120,128],$Va1=[4,12,13,42,44,56,68,69,70,97,100,102,107,111,112,113,114,115,129,132,133,158,161],$Vb1=[1,293],$Vc1=[4,7,157];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"PartialIdentifierOrCursor":6,"REGULAR_IDENTIFIER":7,"PartialIdentifierOrPartialCursor":8,"InitResults":9,"Sql":10,"SqlStatements":11,";":12,"EOF":13,"SqlStatement":14,"UseStatement":15,"DataManipulation":16,"TableDefinition":17,"QueryExpression":18,"USE":19,"LoadStatement":20,"UpdateStatement":21,"HiveOrImpalaLoad":22,"HiveOrImpalaData":23,"HiveOrImpalaInpath":24,"HdfsPath":25,"INTO":26,"TABLE":27,"<hive>LOAD":28,"<impala>LOAD":29,"<hive>DATA":30,"<impala>DATA":31,"<hive>INPATH":32,"<impala>INPATH":33,"UPDATE":34,"TargetTable":35,"SET":36,"SetClauseList":37,"WhereClause":38,"TableName":39,"LocalOrSchemaQualifiedName":40,"SetClause":41,",":42,"SetTarget":43,"=":44,"UpdateSource":45,"ValueExpression":46,"BooleanValueExpression":47,"CREATE":48,"TableScope":49,"TableElementList":50,"TableLocation":51,"<hive>EXTERNAL":52,"<impala>EXTERNAL":53,"(":54,"TableElements":55,")":56,"TableElement":57,"ColumnDefinition":58,"PrimitiveType":59,"ColumnDefinitionError":60,"HiveOrImpalaLocation":61,"<hive>LOCATION":62,"<impala>LOCATION":63,"HDFS_START_QUOTE":64,"HDFS_PATH":65,"HDFS_END_QUOTE":66,"AnyDot":67,".":68,"<impala>.":69,"<hive>.":70,"TINYINT":71,"SMALLINT":72,"INT":73,"BIGINT":74,"BOOLEAN":75,"FLOAT":76,"DOUBLE":77,"STRING":78,"DECIMAL":79,"CHAR":80,"VARCHAR":81,"TIMESTAMP":82,"<hive>BINARY":83,"<hive>DATE":84,"SELECT":85,"CleanUpSelectConditions":86,"SelectList":87,"TableExpression":88,"FromClause":89,"SelectConditionList":90,"FROM":91,"TableReferenceList":92,"SelectCondition":93,"GroupByClause":94,"OrderByClause":95,"LimitClause":96,"WHERE":97,"SearchCondition":98,"BooleanTerm":99,"OR":100,"BooleanFactor":101,"AND":102,"NOT":103,"BooleanTest":104,"Predicate":105,"CompOp":106,"IS":107,"TruthValue":108,"ParenthesizedBooleanValueExpression":109,"NonParenthesizedValueExpressionPrimary":110,"<>":111,"<=":112,">=":113,"<":114,">":115,"SignedInteger":116,"UNSIGNED_INTEGER":117,"-":118,"StringValue":119,"SINGLE_QUOTE":120,"VALUE":121,"ColumnReference":122,"BasicIdentifierChain":123,"InitIdentifierChain":124,"IdentifierChain":125,"Identifier":126,"ColumnIdentifier":127,"\"":128,"GROUP":129,"BY":130,"ColumnList":131,"ORDER":132,"LIMIT":133,"*":134,"DerivedColumn":135,"[":136,"DOUBLE_QUOTE":137,"]":138,"DerivedColumnChain":139,"TableReference":140,"TablePrimaryOrJoinedTable":141,"TablePrimary":142,"LateralViewDefinition":143,"JoinedTable":144,"LateralViews":145,"RegularOrBacktickedIdentifier":146,"BACKTICK":147,"RegularOrBackTickedSchemaQualifiedName":148,"PARTIAL_VALUE":149,"userDefinedTableGeneratingFunction":150,"<hive>explode":151,"<hive>posexplode":152,"LateralView":153,"<hive>LATERAL":154,"VIEW":155,"LateralViewColumnAliases":156,"<hive>AS":157,"JOIN":158,"JoinSpecification":159,"JoinCondition":160,"ON":161,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",7:"REGULAR_IDENTIFIER",12:";",13:"EOF",19:"USE",26:"INTO",27:"TABLE",28:"<hive>LOAD",29:"<impala>LOAD",30:"<hive>DATA",31:"<impala>DATA",32:"<hive>INPATH",33:"<impala>INPATH",34:"UPDATE",36:"SET",42:",",44:"=",48:"CREATE",52:"<hive>EXTERNAL",53:"<impala>EXTERNAL",54:"(",56:")",62:"<hive>LOCATION",63:"<impala>LOCATION",64:"HDFS_START_QUOTE",65:"HDFS_PATH",66:"HDFS_END_QUOTE",68:".",69:"<impala>.",70:"<hive>.",71:"TINYINT",72:"SMALLINT",73:"INT",74:"BIGINT",75:"BOOLEAN",76:"FLOAT",77:"DOUBLE",78:"STRING",79:"DECIMAL",80:"CHAR",81:"VARCHAR",82:"TIMESTAMP",83:"<hive>BINARY",84:"<hive>DATE",85:"SELECT",91:"FROM",97:"WHERE",100:"OR",102:"AND",103:"NOT",107:"IS",108:"TruthValue",111:"<>",112:"<=",113:">=",114:"<",115:">",117:"UNSIGNED_INTEGER",118:"-",120:"SINGLE_QUOTE",121:"VALUE",128:"\"",129:"GROUP",130:"BY",132:"ORDER",133:"LIMIT",134:"*",136:"[",137:"DOUBLE_QUOTE",138:"]",147:"BACKTICK",149:"PARTIAL_VALUE",151:"<hive>explode",152:"<hive>posexplode",154:"<hive>LATERAL",155:"VIEW",157:"<hive>AS",158:"JOIN",161:"ON"},
productions_: [0,[3,1],[3,1],[6,2],[6,1],[8,2],[8,1],[9,0],[10,4],[10,3],[11,1],[11,3],[14,1],[14,1],[14,1],[14,1],[14,3],[14,2],[14,1],[15,3],[15,2],[15,2],[16,1],[16,1],[20,7],[20,6],[20,5],[20,4],[20,3],[20,2],[22,1],[22,1],[23,1],[23,1],[24,1],[24,1],[21,5],[21,5],[21,4],[21,3],[21,2],[21,2],[35,1],[39,1],[37,1],[37,3],[41,3],[41,2],[41,1],[43,1],[45,1],[46,1],[17,6],[17,5],[17,4],[17,3],[17,6],[17,4],[17,2],[49,1],[49,1],[50,3],[55,1],[55,3],[57,1],[58,2],[58,2],[58,4],[60,0],[51,2],[61,1],[61,1],[25,3],[25,5],[25,4],[25,3],[25,3],[25,2],[67,1],[67,1],[67,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[59,1],[18,4],[18,3],[88,1],[88,2],[86,0],[89,2],[89,2],[90,1],[90,2],[93,1],[93,1],[93,1],[93,1],[93,1],[38,2],[38,2],[98,1],[47,1],[47,3],[99,1],[99,3],[99,3],[101,2],[101,1],[104,1],[104,3],[104,3],[104,3],[104,4],[105,1],[105,1],[106,1],[106,1],[106,1],[106,1],[106,1],[106,1],[109,3],[109,2],[116,1],[116,2],[119,3],[110,1],[110,1],[110,1],[122,1],[123,2],[124,0],[125,1],[125,3],[125,3],[126,1],[126,2],[126,3],[94,3],[94,2],[95,3],[95,2],[96,2],[96,2],[87,1],[87,2],[87,2],[87,1],[131,1],[131,3],[127,1],[127,6],[127,4],[127,3],[135,1],[135,3],[135,2],[135,3],[135,3],[135,5],[135,5],[135,1],[139,1],[139,3],[92,1],[92,3],[140,1],[141,1],[141,1],[141,1],[143,2],[143,3],[142,1],[146,1],[146,3],[148,3],[148,5],[148,5],[148,7],[148,6],[148,3],[148,5],[148,2],[148,3],[40,1],[40,2],[40,1],[40,2],[150,4],[150,4],[150,4],[150,4],[145,1],[145,2],[153,5],[153,4],[153,5],[153,4],[153,3],[153,2],[156,2],[156,6],[144,4],[144,4],[144,3],[159,1],[160,2]],
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
case 36: case 38: case 95:

     linkTablePrimaries();
   
break;
case 37:

     suggestKeywords([ 'WHERE' ]);
   
break;
case 39:

     suggestKeywords([ 'SET' ]);
   
break;
case 41: case 101:

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
case 48: case 110: case 147:

     suggestColumns();
   
break;
case 53: case 54: case 55:

      if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
        suggestKeywords(['EXTERNAL'])
      }
    
break;
case 56:

     if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
       suggestKeywords(['LOCATION'])
     }
   
break;
case 58:

      if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
        suggestKeywords(['EXTERNAL', 'TABLE'])
      } else {
        suggestKeywords(['TABLE'])
      }
    
break;
case 66: case 68:

     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   
break;
case 73:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 74:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 75:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 76:

     suggestHdfs({ path: '/' });
   
break;
case 77:

      suggestHdfs({ path: '/' });
    
break;
case 99:

     delete parser.yy.afterGroupBy;
     delete parser.yy.afterLimit;
     delete parser.yy.afterOrderBy;
     delete parser.yy.afterWhere;
   
break;
case 104:

     parser.yy.afterWhere = true;
   
break;
case 105:

     parser.yy.afterGroupBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 106:

     parser.yy.afterOrderBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 107:

     parser.yy.afterLimit = true;
     delete parser.yy.result.suggestStar;
   
break;
case 108:

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
case 115:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 121:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 125: case 137: case 140:

     this.$ = $$[$0];
   
break;
case 133:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 141:

     this.$ = parser.yy.identifierChain
     delete parser.yy.identifierChain;
   
break;
case 142:

     parser.yy.identifierChain = [];
   
break;
case 144:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 146:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 148:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 150: case 152:

     suggestKeywords(['BY']);
   
break;
case 154:

     suggestNumbers([1, 5, 10]);
   
break;
case 156: case 157:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 161:

     this.$ = { name: $$[$0] }
   
break;
case 162:

     this.$ = { name: $$[$0-5], key: '"' + $$[$0-2] + '"' }
   
break;
case 163:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 164:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 166:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 167:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 169:

      delete parser.yy.derivedColumnChain;
   
break;
case 170: case 171:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 172:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 173:

     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 174:

     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 178:

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
case 179:

     addTablePrimary($$[$0]);
   
break;
case 181:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], lateralViews: $$[$0] }
   
break;
case 182:

     this.$ = { identifierChain: [ { name: $$[$0-2] } ], alias: $$[$0-1], lateralViews: $$[$0] };
   
break;
case 185:

     this.$ = $$[$0-2];
   
break;
case 186:

     this.$ = { identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] }
   
break;
case 187:

     this.$ = { identifierChain: [ { name: $$[$0-3] }, { name: $$[$0] } ] }
   
break;
case 188:

     this.$ = { identifierChain: [ { name: $$[$0-4] }, { name: $$[$0-1] } ] }
   
break;
case 189:

     this.$ = { identifierChain: [ { name: $$[$0-5] }, { name: $$[$0-1] } ] }
   
break;
case 190:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-4] } ] };
   
break;
case 191:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-2] } ] };
   
break;
case 192:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-3] } ] };
   
break;
case 193:

     this.$ = { partial: true, identifierChain: [ ] };
   
break;
case 194:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ] }
   
break;
case 195:

     this.$ = { identifierChain: [ { name: $$[$0] } ] }
   
break;
case 196:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] };
   
break;
case 198:

     this.$ = { identifierChain: $$[$0-1].identifierChain, alias: $$[$0] }
   
break;
case 199:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 201:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 203:

     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 204:

     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 205:

     this.$ = { udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }
   
break;
case 206:

      this.$ = { udtf: $$[$0-1], columnAliases: $$[$0] }
    
break;
case 207: case 208:

     suggestKeywords(['AS']);
   
break;
case 209:

     suggestKeywords(['explode', 'posexplode']);
   
break;
case 210:

     suggestKeywords(['VIEW']);
   
break;
case 211:

     this.$ = [ $$[$0] ]
   
break;
case 212:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 214:

     suggestKeywords(['ON']);
   
break;
case 215:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,7,19,28,29,34,48,85],[2,7],{10:1,9:2}),{1:[3]},{3:10,4:$V0,5:$V1,7:$V2,11:3,14:4,15:5,16:6,17:7,18:8,19:$V3,20:12,21:13,22:18,28:$V4,29:$V5,34:$V6,48:$V7,85:$V8},{12:[1,22],13:[1,23]},o($V9,[2,10]),o($V9,[2,12]),o($V9,[2,13]),o($V9,[2,14]),o($V9,[2,15]),{5:[1,24]},o($V9,[2,18]),{4:[1,26],7:[1,25]},o($V9,[2,22]),o($V9,[2,23]),{4:$Va,6:28,7:$Vb,27:[1,29],49:27,52:[1,30],53:[1,31]},o([4,5,7,134],[2,99],{86:34}),o($Vc,[2,1]),o($Vc,[2,2]),{4:$Va,6:36,7:$Vb,23:35,30:[1,37],31:[1,38]},{4:$Va,6:40,7:[1,42],35:39,39:41,40:43,147:$Vd,148:44},o($Ve,[2,30]),o($Ve,[2,31]),{3:10,4:$V0,5:$V1,7:$V2,13:[1,46],14:47,15:5,16:6,17:7,18:8,19:$V3,20:12,21:13,22:18,28:$V4,29:$V5,34:$V6,48:$V7,85:$V8},{1:[2,9]},o($V9,[2,17],{7:[1,48]}),o($V9,[2,20],{5:[1,49]}),o($V9,[2,21]),{27:[1,50]},o($V9,[2,58],{27:[1,51]}),{7:[1,52]},{27:[2,59]},{27:[2,60]},{5:$Vf},o($Vg,[2,4]),{3:59,4:$V0,5:$V1,7:$Vh,87:54,127:58,131:55,134:[1,56],135:57},{4:$Va,6:62,7:$Vb,24:61,32:[1,63],33:[1,64]},o($V9,[2,29]),o($Vi,[2,32]),o($Vi,[2,33]),o($V9,[2,40],{4:[1,66],36:[1,65]}),o($V9,[2,41]),o($Vj,[2,42]),o($Vj,$Vk,{67:68,5:$Vf,7:[1,67],68:$Vl,69:$Vm,70:$Vn}),o($Vj,[2,43]),o($Vo,[2,197],{7:[1,72]}),{121:[1,73],149:[1,74]},{1:[2,8]},o($V9,[2,11]),o($V9,[2,16]),o($V9,[2,19]),{7:[1,75]},o($V9,[2,55],{7:[1,76]}),{50:77,54:$Vp},o($Vg,[2,3]),o($V9,[2,96],{88:79,89:80,91:[1,81]}),o($Vq,[2,155],{6:82,4:$Va,7:$Vb,42:$Vr}),o($Vq,[2,158],{6:84,4:$Va,7:$Vb}),o($Vs,[2,159]),o($Vs,[2,165],{67:85,5:[1,86],68:$Vl,69:$Vm,70:$Vn}),o($Vs,[2,172]),o($Vt,$Vu,{136:$Vv}),{25:88,64:$Vw},o($V9,[2,28]),{64:[2,34]},{64:[2,35]},{4:$Va,6:93,7:$Vx,37:90,41:91,43:92},o($V9,[2,39]),o($Vj,$Vy),{5:$Vz,7:[1,95],8:97,147:[1,96]},o($VA,[2,78]),o($VA,$VB),o($VA,$VC),o($Vo,[2,198]),{147:[1,99]},o($VD,[2,193]),{50:100,54:$Vp},o($V9,[2,54],{50:101,54:$Vp}),o($V9,[2,57]),{7:$VE,55:102,57:103,58:104},o($V9,[2,95]),o($V9,[2,97],{90:106,93:107,38:108,94:109,95:110,96:111,4:$VF,97:$VG,129:$VH,132:$VI,133:$VJ}),{4:$Va,6:118,7:[1,120],40:125,92:117,140:119,141:121,142:122,143:123,144:124,147:$Vd,148:44},o($Vq,[2,156]),{3:59,4:$V0,5:$V1,7:$Vh,127:58,135:126},o($Vq,[2,157]),{5:$Vz,7:$VK,8:127,127:131,134:[1,128],139:129},o($Vs,[2,167]),{117:[1,133],137:[1,132],138:[1,134]},o($V9,[2,27],{6:136,4:$Va,7:$Vb,26:[1,135]}),{5:[1,138],65:[1,137]},o($V9,[2,38],{38:139,4:[1,140],42:[1,141],97:$VG}),o($VL,[2,44]),{4:[1,143],44:[1,142]},o($VL,[2,48]),o([4,44],[2,49],{5:$Vf}),o($VD,[2,186],{5:$VM}),{121:[1,145]},o($VD,[2,191]),o($VN,[2,6]),o($VD,[2,194],{67:146,68:$Vl,69:$Vm,70:$Vn}),{4:$Va,6:148,7:$Vb,51:147,61:149,62:[1,150],63:[1,151]},o($V9,[2,53]),{42:[1,153],56:[1,152]},o($VO,[2,62]),o($VO,[2,64]),{4:$Va,6:155,7:$Vb,59:154,71:[1,156],72:[1,157],73:[1,158],74:[1,159],75:[1,160],76:[1,161],77:[1,162],78:[1,163],79:[1,164],80:[1,165],81:[1,166],82:[1,167],83:[1,168],84:[1,169]},o($V9,[2,98],{38:108,94:109,95:110,96:111,93:170,4:$VF,97:$VG,129:$VH,132:$VI,133:$VJ}),o($VP,[2,102]),o($VP,[2,104]),o($VP,[2,105]),o($VP,[2,106]),o($VP,[2,107]),o($VP,[2,108]),o($VQ,$VR,{98:171,47:173,99:174,101:175,104:177,105:178,109:179,110:180,122:182,116:183,119:184,123:185,124:189,4:[1,172],54:$VS,103:$VT,117:$VU,118:$VV,120:$VW}),{4:$Va,6:191,7:$Vb,130:[1,190]},{4:$Va,6:193,7:$Vb,130:[1,192]},{4:$Va,6:195,7:$Vb,117:[1,194]},o($VP,[2,100],{42:[1,196]}),o($VP,[2,101]),o($VX,[2,175],{158:$VY}),o([4,12,13,42,97,129,132,133,158],$Vk,{67:68,145:198,153:200,5:$Vf,7:$VZ,68:$Vl,69:$Vm,70:$Vn,154:$V_}),o($V$,[2,177]),o($V$,[2,178]),o($V$,[2,179]),o($V$,[2,180]),o($V$,[2,183]),o($Vs,[2,160]),o($Vs,[2,166]),o($Vs,[2,168]),o($Vs,[2,169],{67:204,68:$Vl,69:[1,202],70:[1,203]}),o($V01,$Vu,{5:$VM,136:$Vv}),o($V01,[2,173]),{7:[1,205]},{138:[1,206]},o($Vt,[2,164]),{4:$Va,6:208,7:$Vb,27:[1,207]},o($V9,[2,26]),{5:[1,210],66:[1,209]},o($V11,[2,77],{66:[1,211]}),o($V9,[2,36]),o($V9,[2,37]),{4:$Va,6:93,7:$Vx,41:212,43:92},o($VQ,$VR,{99:174,101:175,104:177,105:178,109:179,110:180,122:182,116:183,119:184,123:185,124:189,45:213,46:214,47:215,54:$VS,103:$VT,117:$VU,118:$VV,120:$VW}),o($VL,[2,47]),o($VN,[2,5]),{147:[1,216]},{5:[1,219],7:[1,217],147:[1,218]},o($V9,[2,52]),o($V9,[2,56]),{25:220,64:$Vw},{64:[2,70]},{64:[2,71]},o([4,7,12,13,62,63],[2,61]),{7:$VE,57:221,58:104},o($VO,[2,65]),o($VO,[2,66],{60:222,2:[2,68]}),o($VO,[2,81]),o($VO,[2,82]),o($VO,[2,83]),o($VO,[2,84]),o($VO,[2,85]),o($VO,[2,86]),o($VO,[2,87]),o($VO,[2,88]),o($VO,[2,89]),o($VO,[2,90]),o($VO,[2,91]),o($VO,[2,92]),o($VO,[2,93]),o($VO,[2,94]),o($VP,[2,103]),o($VP,[2,109]),o($VP,[2,110]),o($V$,[2,111],{100:$V21}),o($V31,[2,112]),o($V31,[2,114],{102:[1,224]}),o($VQ,$VR,{105:178,109:179,110:180,122:182,116:183,119:184,123:185,124:189,104:225,54:$VS,117:$VU,118:$VV,120:$VW}),o($V41,[2,118]),o($V41,[2,119],{106:226,44:[1,228],107:[1,227],111:[1,229],112:[1,230],113:[1,231],114:[1,232],115:[1,233]}),o($V51,[2,124]),o($V51,[2,125]),o($VQ,$VR,{99:174,101:175,104:177,105:178,109:179,110:180,122:182,116:183,119:184,123:185,124:189,47:234,3:235,4:$V0,5:$V1,54:$VS,103:$VT,117:$VU,118:$VV,120:$VW}),o($V51,[2,137]),o($V51,[2,138]),o($V51,[2,139]),o($V51,[2,140]),o($V51,[2,134]),{117:[1,236]},{121:[1,237]},{7:$Vh,125:238,126:239,127:240,128:$V61},{3:59,4:$V0,5:$V1,7:$Vh,127:58,131:242,135:57},o($VP,[2,150]),{3:59,4:$V0,5:$V1,7:$Vh,127:58,131:243,135:57},o($VP,[2,152]),o($VP,[2,153]),o($VP,[2,154]),{7:$V71,40:125,140:244,141:121,142:122,143:123,144:124,147:$Vd,148:44},{4:[1,247],7:$V71,40:125,140:246,141:121,142:122,143:123,144:124,147:$Vd,148:44},o($V$,[2,181],{153:248,154:$V_}),o($V$,$Vy,{153:200,145:249,154:$V_}),o($V81,[2,203]),{4:$Va,6:251,7:$Vb,155:[1,250]},{5:[1,252],7:$VB},{5:[1,253],7:$VC},{7:$Vh,127:254},{137:[1,255]},o($Vt,[2,163]),{7:[1,256]},o($V9,[2,25]),o($V11,[2,72]),o($V11,[2,75],{65:[1,257],66:[1,258]}),o($V11,[2,76]),o($VL,[2,45]),o($VL,[2,46]),o($VL,[2,50]),o($VL,[2,51],{100:$V21}),o($VD,[2,188]),o($VD,[2,187]),{121:[1,259],149:[1,260]},o($VD,[2,192]),o($V9,[2,69]),o($VO,[2,63]),{2:[1,261]},o($VQ,$VR,{101:175,104:177,105:178,109:179,110:180,122:182,116:183,119:184,123:185,124:189,99:262,54:$VS,103:$VT,117:$VU,118:$VV,120:$VW}),o($VQ,$VR,{101:175,104:177,105:178,109:179,110:180,122:182,116:183,119:184,123:185,124:189,99:264,4:[1,263],54:$VS,103:$VT,117:$VU,118:$VV,120:$VW}),o($V41,[2,117]),o($VQ,$VR,{109:179,110:180,122:182,116:183,119:184,123:185,124:189,105:265,3:266,4:$V0,5:$V1,54:$VS,117:$VU,118:$VV,120:$VW}),{103:[1,268],108:[1,267]},o($V91,[2,126]),o($V91,[2,127]),o($V91,[2,128]),o($V91,[2,129]),o($V91,[2,130]),o($V91,[2,131]),{56:[1,269],100:$V21},o($V51,[2,133]),o($V51,[2,135]),{120:[1,270]},o($V51,[2,141],{67:271,68:$Vl,69:$Vm,70:$Vn}),o($Va1,[2,143]),o($Va1,[2,146],{5:[1,272]}),{7:[1,273]},o($VP,[2,149],{42:$Vr}),o($VP,[2,151],{42:$Vr}),o($VX,[2,176],{158:$VY}),o($V$,$Vk,{67:68,145:198,153:200,7:$VZ,68:$Vl,69:$Vm,70:$Vn,154:$V_}),{4:[1,275],158:$VY,159:274,160:276,161:[1,277]},o($V$,[2,215]),o($V81,[2,204]),o($V$,[2,182],{153:248,154:$V_}),{4:$Va,6:279,7:$Vb,150:278,151:[1,280],152:[1,281]},o($V81,[2,210]),o($Vs,[2,170]),o($Vs,[2,171]),o($V01,[2,174]),{138:[1,282]},o($V9,[2,24]),{66:[1,283]},o($V11,[2,74]),{147:[1,284]},o($VD,[2,190]),o($VO,[2,67]),o($V31,[2,113]),o($V31,[2,115]),o($V31,[2,116]),o($V41,[2,120]),o($V41,[2,121]),o($V41,[2,122]),{108:[1,285]},o($V51,[2,132]),o($V51,[2,136]),{5:[1,286],7:$Vh,126:287,127:240,128:$V61},o($Va1,[2,147]),{128:[1,288]},o($V$,[2,213]),o($V$,[2,214]),o($V$,[2,216]),o($VQ,$VR,{47:173,99:174,101:175,104:177,105:178,109:179,110:180,122:182,116:183,119:184,123:185,124:189,98:289,54:$VS,103:$VT,117:$VU,118:$VV,120:$VW}),{4:$Va,6:292,7:[1,290],156:291,157:$Vb1},o($V81,[2,209]),{54:[1,294]},{54:[1,295]},o($Vt,[2,162]),o($V11,[2,73]),o($VD,[2,189]),o($V41,[2,123]),o($Va1,[2,144]),o($Va1,[2,145]),o($Va1,[2,148]),o($V$,[2,217]),{4:$Va,5:$Vf,6:297,7:$Vb,156:296,157:$Vb1},o($V81,[2,206]),o($V81,[2,208]),{7:[1,298],54:[1,299]},{5:$Vz,7:$VK,8:301,127:131,139:300},{5:$Vz,7:$VK,8:303,127:131,139:302},o($V81,[2,205]),o($V81,[2,207]),o($V81,[2,211]),{7:[1,304]},{56:[1,305],67:204,68:$Vl,69:$Vm,70:$Vn},{2:[1,306]},{56:[1,307],67:204,68:$Vl,69:$Vm,70:$Vn},{2:[1,308]},{42:[1,309]},o($Vc1,[2,199]),o($Vc1,[2,200]),o($Vc1,[2,201]),o($Vc1,[2,202]),{7:[1,310]},{56:[1,311]},o($V81,[2,212])],
defaultActions: {23:[2,9],30:[2,59],31:[2,60],46:[2,8],63:[2,34],64:[2,35],150:[2,70],151:[2,71]},
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
case 5: return 102; 
break;
case 6: return 74; 
break;
case 7: return 75; 
break;
case 8: return 130; 
break;
case 9: return 80; 
break;
case 10: return 48; 
break;
case 11: return 79; 
break;
case 12: return 77; 
break;
case 13: return 76; 
break;
case 14: return 91; 
break;
case 15: return 129; 
break;
case 16: return 73; 
break;
case 17: return 26; 
break;
case 18: return 107; 
break;
case 19: return 158; 
break;
case 20: return 103; 
break;
case 21: return 161; 
break;
case 22: return 100; 
break;
case 23: return 132; 
break;
case 24: determineCase(yy_.yytext); return 85; 
break;
case 25: return 36; 
break;
case 26: return 72; 
break;
case 27: return 78; 
break;
case 28: return 27; 
break;
case 29: return 82; 
break;
case 30: return 71; 
break;
case 31: determineCase(yy_.yytext); return 34; 
break;
case 32: determineCase(yy_.yytext); return 19; 
break;
case 33: return 81; 
break;
case 34: return 155; 
break;
case 35: return 97; 
break;
case 36: return 157; 
break;
case 37: return 83; 
break;
case 38: return 30; 
break;
case 39: return 84; 
break;
case 40: return 52; 
break;
case 41: this.begin('hdfs'); return 32; 
break;
case 42: return 154; 
break;
case 43: return 28; 
break;
case 44: this.begin('hdfs'); return 62; 
break;
case 45: return 151; 
break;
case 46: return 152; 
break;
case 47: return 70; 
break;
case 48: return 31; 
break;
case 49: return 53; 
break;
case 50: this.begin('hdfs'); return 33; 
break;
case 51: return 29; 
break;
case 52: this.begin('hdfs'); return 63; 
break;
case 53: return 69; 
break;
case 54: return 117; 
break;
case 55: return 7; 
break;
case 56: parser.yy.cursorFound = true; return 4; 
break;
case 57: parser.yy.cursorFound = true; return 5; 
break;
case 58: return 64; 
break;
case 59: return 65; 
break;
case 60: this.popState(); return 66; 
break;
case 61: return 13; 
break;
case 62: return yy_.yytext; 
break;
case 63: return yy_.yytext; 
break;
case 64: return 136; 
break;
case 65: return 138; 
break;
case 66: this.begin('backtickedValue'); return 147; 
break;
case 67: if (yy_.yytext.indexOf('CURSOR|') !== -1) {
                                        this.popState();
                                        return 149;
                                      }
                                      return 121;
                                    
break;
case 68: this.popState(); return 147; 
break;
case 69: this.begin('singleQuotedValue'); return 120; 
break;
case 70: return 121; 
break;
case 71: this.popState(); return 120; 
break;
case 72: return 137; 
break;
case 73: return 13; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:SELECT\b)/i,/^(?:SET\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:AS\b)/i,/^(?:BINARY\b)/i,/^(?:DATA\b)/i,/^(?:DATE\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:DATA\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:[.])/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:\s+['])/i,/^(?:[^'|]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>]+)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[56,57,58,59,60,61],"inclusive":false},"singleQuotedValue":{"rules":[70,71],"inclusive":false},"backtickedValue":{"rules":[67,68],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,54,55,62,63,64,65,66,69,72,73],"inclusive":true},"impala":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,48,49,50,51,52,53,54,55,62,63,64,65,66,69,72,73],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,54,55,62,63,64,65,66,69,72,73],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});