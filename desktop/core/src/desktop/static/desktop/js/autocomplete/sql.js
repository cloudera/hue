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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,15],$V1=[1,16],$V2=[1,9],$V3=[1,11],$V4=[1,17],$V5=[1,18],$V6=[1,13],$V7=[1,14],$V8=[11,12],$V9=[1,29],$Va=[1,28],$Vb=[4,11,12,39,41,82,86,88,93,97,98,99,100,101,102,115,118,119,140,143],$Vc=[4,7,27,28],$Vd=[4,7,29,30],$Ve=[1,44],$Vf=[2,4,11,12,24,39,41,75,82,115,118,119,136,140,143],$Vg=[1,53],$Vh=[1,54],$Vi=[1,56],$Vj=[1,60],$Vk=[11,12,75],$Vl=[1,65],$Vm=[4,7,11,12,41,75,82,115,118,119],$Vn=[1,69],$Vo=[1,70],$Vp=[1,71],$Vq=[4,5,7,11,12,39,41,52,53,54,75,82,115,118,119],$Vr=[1,82],$Vs=[1,89],$Vt=[1,90],$Vu=[1,91],$Vv=[1,92],$Vw=[1,93],$Vx=[5,7,114,120],$Vy=[2,59],$Vz=[2,60],$VA=[4,7,11,12,23],$VB=[39,41],$VC=[4,11,12,82,115,118,119],$VD=[7,114],$VE=[2,122],$VF=[1,148],$VG=[1,143],$VH=[1,153],$VI=[1,154],$VJ=[1,155],$VK=[4,11,12,41,82,115,118,119],$VL=[1,164],$VM=[2,159],$VN=[1,166],$VO=[1,169],$VP=[4,11,12,41,82,115,118,119,140,143],$VQ=[4,7,11,12,39,41,52,53,54,75,82,115,118,119],$VR=[1,181],$VS=[4,11,12,39,41,82,86,115,118,119,140,143],$VT=[4,11,12,39,41,82,86,88,115,118,119,140,143],$VU=[1,198],$VV=[1,199],$VW=[1,203],$VX=[4,11,12,41,82,115,118,119,136,140,143],$VY=[4,5,7,37,104,105,107,114],$VZ=[4,11,12,39,41,52,53,54,82,86,88,93,97,98,99,100,101,102,115,118,119,140,143],$V_=[1,246],$V$=[4,7,139];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"NoOrPartialToken":6,"REGULAR_IDENTIFIER":7,"InitResults":8,"Sql":9,"SqlStatements":10,";":11,"EOF":12,"SqlStatement":13,"UseStatement":14,"DataManipulation":15,"TableDefinition":16,"QueryExpression":17,"USE":18,"HiveOrImpalaLoad":19,"HiveOrImpalaData":20,"HiveOrImpalaInpath":21,"HdfsPath":22,"INTO":23,"TABLE":24,"<hive>LOAD":25,"<impala>LOAD":26,"<hive>DATA":27,"<impala>DATA":28,"<hive>INPATH":29,"<impala>INPATH":30,"CREATE":31,"TableScope":32,"TableElementList":33,"TableLocation":34,"<hive>EXTERNAL":35,"<impala>EXTERNAL":36,"(":37,"TableElements":38,")":39,"TableElement":40,",":41,"ColumnDefinition":42,"PrimitiveType":43,"ColumnDefinitionError":44,"HiveOrImpalaLocation":45,"<hive>LOCATION":46,"<impala>LOCATION":47,"HDFS_START_QUOTE":48,"HDFS_PATH":49,"HDFS_END_QUOTE":50,"AnyDot":51,".":52,"<impala>.":53,"<hive>.":54,"TINYINT":55,"SMALLINT":56,"INT":57,"BIGINT":58,"BOOLEAN":59,"FLOAT":60,"DOUBLE":61,"STRING":62,"DECIMAL":63,"CHAR":64,"VARCHAR":65,"TIMESTAMP":66,"<hive>BINARY":67,"<hive>DATE":68,"SELECT":69,"CleanUpSelectConditions":70,"SelectList":71,"TableExpression":72,"FromClause":73,"SelectConditionList":74,"FROM":75,"TableReferenceList":76,"SelectCondition":77,"WhereClause":78,"GroupByClause":79,"OrderByClause":80,"LimitClause":81,"WHERE":82,"SearchCondition":83,"BooleanValueExpression":84,"BooleanTerm":85,"OR":86,"BooleanFactor":87,"AND":88,"NOT":89,"BooleanTest":90,"Predicate":91,"CompOp":92,"IS":93,"TruthValue":94,"ParenthesizedBooleanValueExpression":95,"NonParenthesizedValueExpressionPrimary":96,"=":97,"<>":98,"<":99,">":100,"<=":101,">=":102,"SignedInteger":103,"UNSIGNED_INTEGER":104,"-":105,"StringValue":106,"SINGLE_QUOTE":107,"VALUE":108,"ColumnReference":109,"BasicIdentifierChain":110,"InitIdentifierChain":111,"IdentifierChain":112,"Identifier":113,"\"":114,"GROUP":115,"BY":116,"ColumnList":117,"ORDER":118,"LIMIT":119,"*":120,"DerivedColumn":121,"ColumnIdentifier":122,"[":123,"DOUBLE_QUOTE":124,"]":125,"DerivedColumnChain":126,"TableReference":127,"TablePrimaryOrJoinedTable":128,"TablePrimary":129,"JoinedTable":130,"LateralViews":131,"userDefinedTableGeneratingFunction":132,"<hive>explode":133,"<hive>posexplode":134,"LateralView":135,"<hive>LATERAL":136,"VIEW":137,"LateralViewColumnAliases":138,"<hive>AS":139,"JOIN":140,"JoinSpecification":141,"JoinCondition":142,"ON":143,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",7:"REGULAR_IDENTIFIER",11:";",12:"EOF",18:"USE",23:"INTO",24:"TABLE",25:"<hive>LOAD",26:"<impala>LOAD",27:"<hive>DATA",28:"<impala>DATA",29:"<hive>INPATH",30:"<impala>INPATH",31:"CREATE",35:"<hive>EXTERNAL",36:"<impala>EXTERNAL",37:"(",39:")",41:",",46:"<hive>LOCATION",47:"<impala>LOCATION",48:"HDFS_START_QUOTE",49:"HDFS_PATH",50:"HDFS_END_QUOTE",52:".",53:"<impala>.",54:"<hive>.",55:"TINYINT",56:"SMALLINT",57:"INT",58:"BIGINT",59:"BOOLEAN",60:"FLOAT",61:"DOUBLE",62:"STRING",63:"DECIMAL",64:"CHAR",65:"VARCHAR",66:"TIMESTAMP",67:"<hive>BINARY",68:"<hive>DATE",69:"SELECT",75:"FROM",82:"WHERE",86:"OR",88:"AND",89:"NOT",93:"IS",94:"TruthValue",97:"=",98:"<>",99:"<",100:">",101:"<=",102:">=",104:"UNSIGNED_INTEGER",105:"-",107:"SINGLE_QUOTE",108:"VALUE",114:"\"",115:"GROUP",116:"BY",118:"ORDER",119:"LIMIT",120:"*",123:"[",124:"DOUBLE_QUOTE",125:"]",133:"<hive>explode",134:"<hive>posexplode",136:"<hive>LATERAL",137:"VIEW",139:"<hive>AS",140:"JOIN",143:"ON"},
productions_: [0,[3,1],[3,1],[6,2],[6,1],[8,0],[9,4],[9,3],[10,1],[10,3],[13,1],[13,1],[13,1],[13,1],[13,3],[13,2],[13,1],[14,3],[14,2],[14,2],[15,7],[15,6],[15,5],[15,4],[15,3],[15,2],[19,1],[19,1],[20,1],[20,1],[21,1],[21,1],[16,6],[16,5],[16,4],[16,3],[16,6],[16,4],[16,2],[32,1],[32,1],[33,3],[38,1],[38,3],[40,1],[42,2],[42,2],[42,4],[44,0],[34,2],[45,1],[45,1],[22,3],[22,5],[22,4],[22,3],[22,3],[22,2],[51,1],[51,1],[51,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[43,1],[17,4],[17,3],[72,1],[72,2],[70,0],[73,2],[73,2],[74,1],[74,2],[77,1],[77,1],[77,1],[77,1],[77,1],[78,2],[78,2],[83,1],[84,1],[84,3],[85,1],[85,3],[85,3],[87,2],[87,1],[90,1],[90,3],[90,3],[90,3],[90,4],[91,1],[91,1],[92,1],[92,1],[92,1],[92,1],[92,1],[92,1],[95,3],[95,2],[103,1],[103,2],[106,3],[96,1],[96,1],[96,1],[109,1],[110,2],[111,0],[112,1],[112,3],[112,3],[113,1],[113,3],[79,3],[79,2],[80,3],[80,2],[81,2],[81,2],[71,1],[71,2],[71,2],[71,1],[117,1],[117,3],[122,1],[122,6],[122,4],[122,3],[121,1],[121,3],[121,2],[121,3],[121,3],[121,5],[121,5],[121,1],[126,1],[126,3],[76,1],[76,3],[127,1],[128,1],[128,1],[129,1],[129,2],[129,2],[129,3],[129,3],[129,4],[129,3],[132,4],[132,4],[131,1],[131,2],[135,5],[135,4],[135,4],[135,3],[135,2],[138,2],[138,6],[130,4],[130,3],[141,1],[142,2]],
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
         linkTablesPrimaries();
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
case 21:

     suggestKeywords([ 'TABLE' ]);
   
break;
case 22:

     suggestKeywords([ 'INTO' ]);
   
break;
case 24:

     suggestKeywords([ 'INPATH' ]);
   
break;
case 25:

     suggestKeywords([ 'DATA' ]);
   
break;
case 33: case 34: case 35:

      if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
        suggestKeywords(['EXTERNAL'])
      }
    
break;
case 36:

     if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
       suggestKeywords(['LOCATION'])
     }
   
break;
case 38:

      if (parser.yy.dialect === 'hive' || parser.yy.dialect === 'impala') {
        suggestKeywords(['EXTERNAL', 'TABLE'])
      } else {
        suggestKeywords(['TABLE'])
      }
    
break;
case 46: case 48:

     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   
break;
case 53:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 54:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 55:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 56:

     suggestHdfs({ path: '/' });
   
break;
case 57:

      suggestHdfs({ path: '/' });
    
break;
case 75:

     linkTablesPrimaries();
   
break;
case 79:

     delete parser.yy.afterGroupBy;
     delete parser.yy.afterLimit;
     delete parser.yy.afterOrderBy;
     delete parser.yy.afterWhere;
   
break;
case 81:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 84:

     parser.yy.afterWhere = true;
   
break;
case 85:

     parser.yy.afterGroupBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 86:

     parser.yy.afterOrderBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 87:

     parser.yy.afterLimit = true;
     delete parser.yy.result.suggestStar;
   
break;
case 88:

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
case 90:

     suggestColumns();
   
break;
case 95:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 101:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 105: case 117: case 120:

     this.$ = $$[$0];
   
break;
case 113:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 121:

     this.$ = parser.yy.identifierChain
     delete parser.yy.identifierChain;
   
break;
case 122:

     parser.yy.identifierChain = [];
   
break;
case 124:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 126:

     parser.yy.identifierChain.push({ name: $$[$0] });
   
break;
case 127:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 129: case 131:

     suggestKeywords(['BY']);
   
break;
case 133:

     suggestNumbers([1, 5, 10]);
   
break;
case 135:

      suggestTables({ prependFrom: true });
      suggestDatabases({ prependFrom: true, appendDot: true });
    
break;
case 136:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 140:

     this.$ = { name: $$[$0] }
   
break;
case 141:

     this.$ = { name: $$[$0-5], key: '"' + $$[$0-2] + '"' }
   
break;
case 142:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 143:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 145:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 146:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 148:

      delete parser.yy.derivedColumnChain;
   
break;
case 149: case 150:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 151:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 152:

     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 153:

     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 159:

     addTablePrimary({ identifierChain: [ { name: $$[$0] } ] });
   
break;
case 160:

     addTablePrimary({ identifierChain: [ { name: $$[$0-1] } ], lateralViews: $$[$0] } );
   
break;
case 161:

     addTablePrimary({ identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] });
   
break;
case 162:

     addTablePrimary({ identifierChain: [ { name: $$[$0-2] } ], alias: $$[$0-1], lateralViews: $$[$0] } );
   
break;
case 163:

     addTablePrimary({ identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] });
   
break;
case 164:

     addTablePrimary({ identifierChain: [ { name: $$[$0-3] }, { name: $$[$0-1] } ], alias: $$[$0] });
   
break;
case 165:

     suggestTablesOrColumns($$[$0-2]);
   
break;
case 166:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 167:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 168:

     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 169:

     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 170:

     this.$ = { udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }
   
break;
case 171:

      this.$ = { udtf: $$[$0-1], columnAliases: $$[$0] }
    
break;
case 172:

     suggestKeywords(['AS']);
   
break;
case 173:

     suggestKeywords(['explode', 'posexplode']);
   
break;
case 174:

     suggestKeywords(['VIEW']);
   
break;
case 175:

     this.$ = [ $$[$0] ]
   
break;
case 176:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 178:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,7,18,25,26,31,69],[2,5],{9:1,8:2}),{1:[3]},{3:10,4:$V0,5:$V1,7:$V2,10:3,13:4,14:5,15:6,16:7,17:8,18:$V3,19:12,25:$V4,26:$V5,31:$V6,69:$V7},{11:[1,19],12:[1,20]},o($V8,[2,8]),o($V8,[2,10]),o($V8,[2,11]),o($V8,[2,12]),o($V8,[2,13]),{5:[1,21]},o($V8,[2,16]),{4:[1,23],7:[1,22]},{4:$V9,6:25,7:$Va,20:24,27:[1,26],28:[1,27]},{4:$V9,6:31,7:$Va,24:[1,32],32:30,35:[1,33],36:[1,34]},o([4,7,120],[2,79],{70:35}),o($Vb,[2,1]),o($Vb,[2,2]),o($Vc,[2,26]),o($Vc,[2,27]),{3:10,4:$V0,5:$V1,7:$V2,12:[1,36],13:37,14:5,15:6,16:7,17:8,18:$V3,19:12,25:$V4,26:$V5,31:$V6,69:$V7},{1:[2,7]},o($V8,[2,15],{7:[1,38]}),o($V8,[2,18],{5:[1,39]}),o($V8,[2,19]),{4:$V9,6:41,7:$Va,21:40,29:[1,42],30:[1,43]},o($V8,[2,25]),o($Vd,[2,28]),o($Vd,[2,29]),{5:$Ve},o($Vf,[2,4]),{24:[1,45]},o($V8,[2,38],{24:[1,46]}),{7:[1,47]},{24:[2,39]},{24:[2,40]},{4:$Vg,7:$Vh,71:48,117:49,120:[1,50],121:51,122:52},{1:[2,6]},o($V8,[2,9]),o($V8,[2,14]),o($V8,[2,17]),{22:55,48:$Vi},o($V8,[2,24]),{48:[2,30]},{48:[2,31]},o($Vf,[2,3]),{7:[1,57]},o($V8,[2,35],{7:[1,58]}),{33:59,37:$Vj},o($V8,[2,76],{72:61,73:62,75:[1,63]}),o($Vk,[2,134],{6:64,4:$V9,7:$Va,41:$Vl}),o($Vk,[2,137],{6:66,4:$V9,7:$Va}),o($Vm,[2,138]),o($Vm,[2,144],{51:67,5:[1,68],52:$Vn,53:$Vo,54:$Vp}),o($Vm,[2,151]),o($Vq,[2,140],{123:[1,72]}),o($V8,[2,23],{6:74,4:$V9,7:$Va,23:[1,73]}),{5:[1,76],49:[1,75]},{33:77,37:$Vj},o($V8,[2,34],{33:78,37:$Vj}),o($V8,[2,37]),{7:$Vr,38:79,40:80,42:81},o($V8,[2,75]),o($V8,[2,77],{74:83,77:84,78:85,79:86,80:87,81:88,4:$Vs,82:$Vt,115:$Vu,118:$Vv,119:$Vw}),{4:$V9,6:95,7:[1,97],76:94,127:96,128:98,129:99,130:100},o($Vk,[2,135]),{4:$Vg,7:$Vh,121:101,122:52},o($Vk,[2,136]),{5:[1,102],7:$Vh,120:[1,103],122:105,126:104},o($Vm,[2,146]),o($Vx,[2,58]),o($Vx,$Vy),o($Vx,$Vz),{104:[1,107],124:[1,106],125:[1,108]},{4:$V9,6:110,7:$Va,24:[1,109]},o($V8,[2,22]),{5:[1,112],50:[1,111]},o($VA,[2,57],{50:[1,113]}),{4:$V9,6:115,7:$Va,34:114,45:116,46:[1,117],47:[1,118]},o($V8,[2,33]),{39:[1,119],41:[1,120]},o($VB,[2,42]),o($VB,[2,44]),{4:$V9,6:122,7:$Va,43:121,55:[1,123],56:[1,124],57:[1,125],58:[1,126],59:[1,127],60:[1,128],61:[1,129],62:[1,130],63:[1,131],64:[1,132],65:[1,133],66:[1,134],67:[1,135],68:[1,136]},o($V8,[2,78],{78:85,79:86,80:87,81:88,77:137,4:$Vs,82:$Vt,115:$Vu,118:$Vv,119:$Vw}),o($VC,[2,82]),o($VC,[2,84]),o($VC,[2,85]),o($VC,[2,86]),o($VC,[2,87]),o($VC,[2,88]),o($VD,$VE,{83:138,84:140,85:141,87:142,90:144,91:145,95:146,96:147,109:149,103:150,106:151,110:152,111:156,4:[1,139],37:$VF,89:$VG,104:$VH,105:$VI,107:$VJ}),{4:$V9,6:158,7:$Va,116:[1,157]},{4:$V9,6:160,7:$Va,116:[1,159]},{4:$V9,6:162,7:$Va,104:[1,161]},o($VC,[2,80],{41:[1,163]}),o($VC,[2,81]),o($VK,[2,154],{140:$VL}),o([4,11,12,41,82,115,118,119,140],$VM,{131:165,51:167,135:168,5:$Ve,7:$VN,52:$Vn,53:$Vo,54:$Vp,136:$VO}),o($VP,[2,156]),o($VP,[2,157]),o($VP,[2,158]),o($Vm,[2,139]),o($Vm,[2,145]),o($Vm,[2,147]),o($Vm,[2,148],{51:172,52:$Vn,53:[1,170],54:[1,171]}),o($VQ,[2,152]),{7:[1,173]},{125:[1,174]},o($Vq,[2,143]),{7:[1,175]},o($V8,[2,21]),o($VA,[2,52]),o($VA,[2,55],{49:[1,176],50:[1,177]}),o($VA,[2,56]),o($V8,[2,32]),o($V8,[2,36]),{22:178,48:$Vi},{48:[2,50]},{48:[2,51]},o([4,7,11,12,46,47],[2,41]),{7:$Vr,40:179,42:81},o($VB,[2,45]),o($VB,[2,46],{44:180,2:[2,48]}),o($VB,[2,61]),o($VB,[2,62]),o($VB,[2,63]),o($VB,[2,64]),o($VB,[2,65]),o($VB,[2,66]),o($VB,[2,67]),o($VB,[2,68]),o($VB,[2,69]),o($VB,[2,70]),o($VB,[2,71]),o($VB,[2,72]),o($VB,[2,73]),o($VB,[2,74]),o($VC,[2,83]),o($VC,[2,89]),o($VC,[2,90]),o($VP,[2,91],{86:$VR}),o($VS,[2,92]),o($VS,[2,94],{88:[1,182]}),o($VD,$VE,{91:145,95:146,96:147,109:149,103:150,106:151,110:152,111:156,90:183,37:$VF,104:$VH,105:$VI,107:$VJ}),o($VT,[2,98]),o($VT,[2,99],{92:184,93:[1,185],97:[1,186],98:[1,187],99:[1,188],100:[1,189],101:[1,190],102:[1,191]}),o($Vb,[2,104]),o($Vb,[2,105]),o($VD,$VE,{85:141,87:142,90:144,91:145,95:146,96:147,109:149,103:150,106:151,110:152,111:156,84:192,3:193,4:$V0,5:$V1,37:$VF,89:$VG,104:$VH,105:$VI,107:$VJ}),o($Vb,[2,117]),o($Vb,[2,118]),o($Vb,[2,119]),o($Vb,[2,120]),o($Vb,[2,114]),{104:[1,194]},{108:[1,195]},{7:$VU,112:196,113:197,114:$VV},{4:$Vg,7:$Vh,117:200,121:51,122:52},o($VC,[2,129]),{4:$Vg,7:$Vh,117:201,121:51,122:52},o($VC,[2,131]),o($VC,[2,132]),o($VC,[2,133]),{7:$VW,127:202,128:98,129:99,130:100},{4:[1,205],7:$VW,127:204,128:98,129:99,130:100},o($VP,[2,160],{135:206,136:$VO}),o($VP,[2,161],{135:168,131:207,136:$VO}),{5:[1,209],7:[1,208]},o($VX,[2,168]),{4:$V9,6:211,7:$Va,137:[1,210]},{5:[1,212],7:$Vy},{5:[1,213],7:$Vz},{7:$Vh,122:214},{124:[1,215]},o($Vq,[2,142]),o($V8,[2,20]),{50:[1,216]},o($VA,[2,54]),o($V8,[2,49]),o($VB,[2,43]),{2:[1,217]},o($VD,$VE,{87:142,90:144,91:145,95:146,96:147,109:149,103:150,106:151,110:152,111:156,85:218,37:$VF,89:$VG,104:$VH,105:$VI,107:$VJ}),o($VD,$VE,{87:142,90:144,91:145,95:146,96:147,109:149,103:150,106:151,110:152,111:156,85:220,4:[1,219],37:$VF,89:$VG,104:$VH,105:$VI,107:$VJ}),o($VT,[2,97]),o($VD,$VE,{95:146,96:147,109:149,103:150,106:151,110:152,111:156,91:221,3:222,4:$V0,5:$V1,37:$VF,104:$VH,105:$VI,107:$VJ}),{89:[1,224],94:[1,223]},o($VY,[2,106]),o($VY,[2,107]),o($VY,[2,108]),o($VY,[2,109]),o($VY,[2,110]),o($VY,[2,111]),{39:[1,225],86:$VR},o($Vb,[2,113]),o($Vb,[2,115]),{107:[1,226]},o($Vb,[2,121],{51:227,52:$Vn,53:$Vo,54:$Vp}),o($VZ,[2,123]),o($VZ,[2,126]),{7:[1,228]},o($VC,[2,128],{41:$Vl}),o($VC,[2,130],{41:$Vl}),o($VK,[2,155],{140:$VL}),o($VP,$VM,{131:165,51:167,135:168,7:$VN,52:$Vn,53:$Vo,54:$Vp,136:$VO}),{140:$VL,141:229,142:230,143:[1,231]},o($VP,[2,178]),o($VX,[2,169]),o($VP,[2,162],{135:206,136:$VO}),o($VP,[2,163],{7:[1,232]}),o($VP,[2,165]),{4:$V9,6:234,7:$Va,132:233,133:[1,235],134:[1,236]},o($VX,[2,174]),o($Vm,[2,149]),o($Vm,[2,150]),o($VQ,[2,153]),{125:[1,237]},o($VA,[2,53]),o($VB,[2,47]),o($VS,[2,93]),o($VS,[2,95]),o($VS,[2,96]),o($VT,[2,100]),o($VT,[2,101]),o($VT,[2,102]),{94:[1,238]},o($Vb,[2,112]),o($Vb,[2,116]),{5:[1,239],7:$VU,113:240,114:$VV},{114:[1,241]},o($VP,[2,177]),o($VP,[2,179]),o($VD,$VE,{84:140,85:141,87:142,90:144,91:145,95:146,96:147,109:149,103:150,106:151,110:152,111:156,83:242,37:$VF,89:$VG,104:$VH,105:$VI,107:$VJ}),o($VP,[2,164]),{4:$V9,6:245,7:[1,243],138:244,139:$V_},o($VX,[2,173]),{37:[1,247]},{37:[1,248]},o($Vq,[2,141]),o($VT,[2,103]),o($VZ,[2,124]),o($VZ,[2,125]),o($VZ,[2,127]),o($VP,[2,180]),{5:$Ve,138:249,139:$V_},o($VX,[2,171]),o($VX,[2,172]),{7:[1,250],37:[1,251]},{7:$Vh,122:105,126:252},{7:$Vh,122:105,126:253},o($VX,[2,170]),o($VX,[2,175]),{7:[1,254]},{39:[1,255],51:172,52:$Vn,53:$Vo,54:$Vp},{39:[1,256],51:172,52:$Vn,53:$Vo,54:$Vp},{41:[1,257]},o($V$,[2,166]),o($V$,[2,167]),{7:[1,258]},{39:[1,259]},o($VX,[2,176])],
defaultActions: {20:[2,7],33:[2,39],34:[2,40],36:[2,6],42:[2,30],43:[2,31],117:[2,50],118:[2,51]},
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

var linkTablesPrimaries = function () {
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
case 5: return 88; 
break;
case 6: return 58; 
break;
case 7: return 59; 
break;
case 8: return 116; 
break;
case 9: return 64; 
break;
case 10: return 31; 
break;
case 11: return 63; 
break;
case 12: return 61; 
break;
case 13: return 60; 
break;
case 14: return 75; 
break;
case 15: return 115; 
break;
case 16: return 57; 
break;
case 17: return 23; 
break;
case 18: return 93; 
break;
case 19: return 140; 
break;
case 20: return 89; 
break;
case 21: return 143; 
break;
case 22: return 86; 
break;
case 23: return 118; 
break;
case 24: determineCase(yy_.yytext); return 69; 
break;
case 25: return 56; 
break;
case 26: return 62; 
break;
case 27: return 24; 
break;
case 28: return 66; 
break;
case 29: return 55; 
break;
case 30: determineCase(yy_.yytext); return 18; 
break;
case 31: return 65; 
break;
case 32: return 137; 
break;
case 33: return 82; 
break;
case 34: return 139; 
break;
case 35: return 67; 
break;
case 36: return 27; 
break;
case 37: return 68; 
break;
case 38: return 35; 
break;
case 39: this.begin('hdfs'); return 29; 
break;
case 40: return 136; 
break;
case 41: return 25; 
break;
case 42: this.begin('hdfs'); return 46; 
break;
case 43: return 133; 
break;
case 44: return 134; 
break;
case 45: return 54; 
break;
case 46: return 28; 
break;
case 47: return 36; 
break;
case 48: this.begin('hdfs'); return 30; 
break;
case 49: return 26; 
break;
case 50: this.begin('hdfs'); return 47; 
break;
case 51: return 53; 
break;
case 52: return 104; 
break;
case 53: return 7; 
break;
case 54: parser.yy.cursorFound = true; return 4; 
break;
case 55: parser.yy.cursorFound = true; return 5; 
break;
case 56: return 48; 
break;
case 57: return 49; 
break;
case 58: this.popState(); return 50; 
break;
case 59: return 12; 
break;
case 60: return 108; 
break;
case 61: this.popState(); return 107; 
break;
case 62: return yy_.yytext; 
break;
case 63: return yy_.yytext; 
break;
case 64: return 123; 
break;
case 65: return 125; 
break;
case 66: this.begin('stringValue'); return 107; 
break;
case 67: return 124; 
break;
case 68: return 12; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:SELECT\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:AS\b)/i,/^(?:BINARY\b)/i,/^(?:DATA\b)/i,/^(?:DATE\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:DATA\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:[.])/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:\s+['])/i,/^(?:[^'|]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:')/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[54,55,56,57,58,59],"inclusive":false},"stringValue":{"rules":[60,61],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,52,53,62,63,64,65,66,67,68],"inclusive":true},"impala":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,46,47,48,49,50,51,52,53,62,63,64,65,66,67,68],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,52,53,62,63,64,65,66,67,68],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});