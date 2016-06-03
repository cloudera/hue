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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,15],$V1=[1,16],$V2=[1,9],$V3=[1,11],$V4=[1,17],$V5=[1,18],$V6=[1,13],$V7=[1,14],$V8=[9,10],$V9=[1,36],$Va=[1,37],$Vb=[4,9,10,38,40,79,83,85,90,94,95,96,97,98,99,106,109,110,132,135],$Vc=[26,27],$Vd=[28,29],$Ve=[9,10,72],$Vf=[1,49],$Vg=[4,9,10,40,72,79,106,109,110],$Vh=[1,54],$Vi=[1,55],$Vj=[1,56],$Vk=[4,5,9,10,38,40,50,51,52,72,79,106,109,110],$Vl=[1,59],$Vm=[1,67],$Vn=[1,68],$Vo=[1,69],$Vp=[1,70],$Vq=[1,71],$Vr=[5,16,105,112],$Vs=[2,45],$Vt=[2,46],$Vu=[4,9,10,79,106,109,110],$Vv=[16,105],$Vw=[2,103],$Vx=[1,104],$Vy=[1,99],$Vz=[2,140],$VA=[1,117],$VB=[1,120],$VC=[4,9,10,40,79,106,109,110],$VD=[1,121],$VE=[4,9,10,40,79,106,109,110,132,135],$VF=[4,9,10,38,40,50,51,52,72,79,106,109,110],$VG=[9,10,22],$VH=[1,138],$VI=[1,139],$VJ=[4,9,10,38,40,79,83,106,109,110,132,135],$VK=[4,9,10,38,40,79,83,85,106,109,110,132,135],$VL=[1,154],$VM=[1,155],$VN=[1,159],$VO=[4,9,10,40,79,106,109,110,128,132,135],$VP=[38,40],$VQ=[4,5,16,36,105],$VR=[4,9,10,38,40,50,51,52,79,83,85,90,94,95,96,97,98,99,106,109,110,132,135],$VS=[1,218],$VT=[16,131];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"InitResults":6,"Sql":7,"SqlStatements":8,";":9,"EOF":10,"SqlStatement":11,"UseStatement":12,"DataManipulation":13,"TableDefinition":14,"QueryExpression":15,"REGULAR_IDENTIFIER":16,"USE":17,"HiveOrImpalaLoad":18,"HiveOrImpalaData":19,"HiveOrImpalaInpath":20,"HdfsPath":21,"INTO":22,"TABLE":23,"<hive>LOAD":24,"<impala>LOAD":25,"<hive>DATA":26,"<impala>DATA":27,"<hive>INPATH":28,"<impala>INPATH":29,"CREATE":30,"TableScope":31,"TableElementList":32,"TableLocation":33,"<hive>EXTERNAL":34,"<impala>EXTERNAL":35,"(":36,"TableElements":37,")":38,"TableElement":39,",":40,"ColumnDefinition":41,"PrimitiveType":42,"HiveOrImpalaLocation":43,"<hive>LOCATION":44,"<impala>LOCATION":45,"HDFS_START_QUOTE":46,"HDFS_PATH":47,"HDFS_END_QUOTE":48,"AnyDot":49,".":50,"<impala>.":51,"<hive>.":52,"TINYINT":53,"SMALLINT":54,"INT":55,"BIGINT":56,"BOOLEAN":57,"FLOAT":58,"DOUBLE":59,"STRING":60,"DECIMAL":61,"CHAR":62,"VARCHAR":63,"TIMESTAMP":64,"<hive>BINARY":65,"<hive>DATE":66,"SELECT":67,"SelectList":68,"TableExpression":69,"FromClause":70,"SelectConditionList":71,"FROM":72,"TableReferenceList":73,"SelectCondition":74,"WhereClause":75,"GroupByClause":76,"OrderByClause":77,"LimitClause":78,"WHERE":79,"SearchCondition":80,"BooleanValueExpression":81,"BooleanTerm":82,"OR":83,"BooleanFactor":84,"AND":85,"NOT":86,"BooleanTest":87,"Predicate":88,"CompOp":89,"IS":90,"TruthValue":91,"ParenthesizedBooleanValueExpression":92,"NonParenthesizedValueExpressionPrimary":93,"=":94,"<>":95,"<":96,">":97,"<=":98,">=":99,"ColumnReference":100,"BasicIdentifierChain":101,"InitIdentifierChain":102,"IdentifierChain":103,"Identifier":104,"\"":105,"GROUP":106,"BY":107,"ColumnList":108,"ORDER":109,"LIMIT":110,"UNSIGNED_INTEGER":111,"*":112,"DerivedColumn":113,"ColumnIdentifier":114,"[":115,"DOUBLE_QUOTE":116,"]":117,"DerivedColumnChain":118,"TableReference":119,"TablePrimaryOrJoinedTable":120,"TablePrimary":121,"JoinedTable":122,"LateralViews":123,"userDefinedTableGeneratingFunction":124,"<hive>explode":125,"<hive>posexplode":126,"LateralView":127,"<hive>LATERAL":128,"VIEW":129,"LateralViewColumnAliases":130,"<hive>AS":131,"JOIN":132,"JoinSpecification":133,"JoinCondition":134,"ON":135,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",9:";",10:"EOF",16:"REGULAR_IDENTIFIER",17:"USE",22:"INTO",23:"TABLE",24:"<hive>LOAD",25:"<impala>LOAD",26:"<hive>DATA",27:"<impala>DATA",28:"<hive>INPATH",29:"<impala>INPATH",30:"CREATE",34:"<hive>EXTERNAL",35:"<impala>EXTERNAL",36:"(",38:")",40:",",44:"<hive>LOCATION",45:"<impala>LOCATION",46:"HDFS_START_QUOTE",47:"HDFS_PATH",48:"HDFS_END_QUOTE",50:".",51:"<impala>.",52:"<hive>.",53:"TINYINT",54:"SMALLINT",55:"INT",56:"BIGINT",57:"BOOLEAN",58:"FLOAT",59:"DOUBLE",60:"STRING",61:"DECIMAL",62:"CHAR",63:"VARCHAR",64:"TIMESTAMP",65:"<hive>BINARY",66:"<hive>DATE",67:"SELECT",72:"FROM",79:"WHERE",83:"OR",85:"AND",86:"NOT",90:"IS",91:"TruthValue",94:"=",95:"<>",96:"<",97:">",98:"<=",99:">=",105:"\"",106:"GROUP",107:"BY",109:"ORDER",110:"LIMIT",111:"UNSIGNED_INTEGER",112:"*",115:"[",116:"DOUBLE_QUOTE",117:"]",125:"<hive>explode",126:"<hive>posexplode",128:"<hive>LATERAL",129:"VIEW",131:"<hive>AS",132:"JOIN",135:"ON"},
productions_: [0,[3,1],[3,1],[6,0],[7,4],[7,3],[8,1],[8,3],[11,1],[11,1],[11,1],[11,1],[11,3],[11,2],[11,1],[12,3],[12,2],[12,2],[13,7],[13,4],[18,1],[18,1],[19,1],[19,1],[20,1],[20,1],[14,6],[14,2],[31,1],[31,1],[32,3],[37,1],[37,3],[39,1],[41,2],[33,2],[43,1],[43,1],[21,3],[21,5],[21,4],[21,3],[21,3],[21,2],[49,1],[49,1],[49,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[15,3],[15,2],[69,1],[69,2],[70,2],[70,3],[70,2],[71,1],[71,2],[74,1],[74,1],[74,1],[74,1],[74,1],[75,2],[75,2],[80,1],[81,1],[81,3],[82,1],[82,3],[82,3],[84,2],[84,1],[87,1],[87,3],[87,3],[87,3],[87,4],[88,1],[88,1],[89,1],[89,1],[89,1],[89,1],[89,1],[89,1],[92,3],[92,2],[93,1],[100,1],[101,2],[102,0],[103,1],[103,3],[103,3],[104,1],[104,3],[76,3],[76,2],[77,3],[77,2],[78,2],[78,2],[68,1],[68,3],[68,2],[68,1],[108,1],[108,3],[114,1],[114,6],[114,4],[114,3],[113,1],[113,3],[113,2],[113,3],[113,3],[113,5],[113,5],[113,1],[118,1],[118,3],[73,1],[73,3],[119,1],[120,1],[120,1],[121,1],[121,2],[121,2],[121,3],[121,3],[121,4],[121,3],[124,4],[124,4],[123,1],[123,2],[127,5],[127,4],[130,2],[130,6],[122,4],[122,3],[133,1],[134,2]],
performAction: function anonymous(yytext, yyleng, yylineno, yy, yystate /* action[1] */, $$ /* vstack */, _$ /* lstack */) {
/* this == yyval */

var $0 = $$.length - 1;
switch (yystate) {
case 3:

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
case 4: case 5:

     prioritizeSuggestions();
     return parser.yy.result;
   
break;
case 13: case 14:

     suggestKeywords(['SELECT', 'USE']);
   
break;
case 15: case 17:

     suggestDatabases();
   
break;
case 16:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
case 39:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 40:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 41:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 42:

     suggestHdfs({ path: '/' });
   
break;
case 43:

      suggestHdfs({ path: '/' });
    
break;
case 61:

     linkTablesPrimaries();
   
break;
case 66:

      suggestTables();
      suggestDatabases({ appendDot: true });
    
break;
case 67:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 71: case 72: case 73:

     delete parser.yy.result.suggestStar;
   
break;
case 74:

     suggestKeywords(['WHERE', 'GROUP BY', 'LIMIT']);
   
break;
case 76:

     suggestColumns();
   
break;
case 81:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 87:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 91: case 100: case 101:

     this.$ = $$[$0];
   
break;
case 99:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 102:

     this.$ = parser.yy.identifierChain
     delete parser.yy.identifierChain;
   
break;
case 103:

     parser.yy.identifierChain = [];
   
break;
case 105:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 107:

     parser.yy.identifierChain.push({ name: $$[$0] });
   
break;
case 108:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 110: case 112:

     suggestKeywords(['BY']);
   
break;
case 114:

     suggestNumbers([5, 10, 15]);
   
break;
case 116: case 117:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 121:

     this.$ = { name: $$[$0] }
   
break;
case 122:

     this.$ = { name: $$[$0-5], key: '"' + $$[$0-2] + '"' }
   
break;
case 123:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 124:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 126:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 127:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 129:

      delete parser.yy.derivedColumnChain;
   
break;
case 130: case 131:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 132:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 133:

     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 134:

     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 140:

     addTablePrimary({ identifierChain: [ { name: $$[$0] } ] });
   
break;
case 141:

     addTablePrimary({ identifierChain: [ { name: $$[$0-1] } ], lateralViews: $$[$0] } );
   
break;
case 142:

     addTablePrimary({ identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] });
   
break;
case 143:

     addTablePrimary({ identifierChain: [ { name: $$[$0-2] } ], alias: $$[$0-1], lateralViews: $$[$0] } );
   
break;
case 144:

     addTablePrimary({ identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] });
   
break;
case 145:

     addTablePrimary({ identifierChain: [ { name: $$[$0-3] }, { name: $$[$0-1] } ], alias: $$[$0] });
   
break;
case 146:

     suggestTablesOrColumns($$[$0-2]);
   
break;
case 147:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 148:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 149:

     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 150:

     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 151:

     this.$ = { udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }
   
break;
case 152:

      this.$ = { udtf: $$[$0-1], columnAliases: $$[$0] }
    
break;
case 153:

     this.$ = [ $$[$0] ]
   
break;
case 154:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 156:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,16,17,24,25,30,67],[2,3],{7:1,6:2}),{1:[3]},{3:10,4:$V0,5:$V1,8:3,11:4,12:5,13:6,14:7,15:8,16:$V2,17:$V3,18:12,24:$V4,25:$V5,30:$V6,67:$V7},{9:[1,19],10:[1,20]},o($V8,[2,6]),o($V8,[2,8]),o($V8,[2,9]),o($V8,[2,10]),o($V8,[2,11]),{5:[1,21]},o($V8,[2,14]),{4:[1,23],16:[1,22]},{19:24,26:[1,25],27:[1,26]},{23:[1,28],31:27,34:[1,29],35:[1,30]},{4:$V9,16:$Va,68:31,108:32,112:[1,33],113:34,114:35},o($Vb,[2,1]),o($Vb,[2,2]),o($Vc,[2,20]),o($Vc,[2,21]),{3:10,4:$V0,5:$V1,10:[1,38],11:39,12:5,13:6,14:7,15:8,16:$V2,17:$V3,18:12,24:$V4,25:$V5,30:$V6,67:$V7},{1:[2,5]},o($V8,[2,13],{16:[1,40]}),o($V8,[2,16],{5:[1,41]}),o($V8,[2,17]),{20:42,28:[1,43],29:[1,44]},o($Vd,[2,22]),o($Vd,[2,23]),{23:[1,45]},o($V8,[2,27]),{23:[2,28]},{23:[2,29]},o($V8,[2,62],{69:46,70:47,72:[1,48]}),o($Ve,[2,115],{40:$Vf}),o($Ve,[2,118],{4:[1,51],16:[1,50]}),o($Vg,[2,119]),o($Vg,[2,125],{49:52,5:[1,53],50:$Vh,51:$Vi,52:$Vj}),o($Vg,[2,132]),o($Vk,[2,121],{115:[1,57]}),{1:[2,4]},o($V8,[2,7]),o($V8,[2,12]),o($V8,[2,15]),{21:58,46:$Vl},{46:[2,24]},{46:[2,25]},{16:[1,60]},o($V8,[2,61]),o($V8,[2,63],{71:61,74:62,75:63,76:64,77:65,78:66,4:$Vm,79:$Vn,106:$Vo,109:$Vp,110:$Vq}),{4:[1,74],16:[1,73],73:72,119:75,120:76,121:77,122:78},{4:$V9,16:$Va,113:79,114:35},{5:[1,80]},o($Ve,[2,117]),{5:[1,81],16:$Va,112:[1,82],114:84,118:83},o($Vg,[2,127]),o($Vr,[2,44]),o($Vr,$Vs),o($Vr,$Vt),{111:[1,86],116:[1,85],117:[1,87]},o($V8,[2,19],{22:[1,88]}),{5:[1,90],47:[1,89]},{32:91,36:[1,92]},o($V8,[2,64],{75:63,76:64,77:65,78:66,74:93,4:$Vm,79:$Vn,106:$Vo,109:$Vp,110:$Vq}),o($Vu,[2,68]),o($Vu,[2,70]),o($Vu,[2,71]),o($Vu,[2,72]),o($Vu,[2,73]),o($Vu,[2,74]),o($Vv,$Vw,{80:94,81:96,82:97,84:98,87:100,88:101,92:102,93:103,100:105,101:106,102:107,4:[1,95],36:$Vx,86:$Vy}),{4:[1,109],107:[1,108]},{4:[1,111],107:[1,110]},{4:[1,113],111:[1,112]},o($Vu,[2,65],{40:[1,114]}),o([4,9,10,40,79,106,109,110,132],$Vz,{123:116,49:118,127:119,5:[1,115],16:$VA,50:$Vh,51:$Vi,52:$Vj,128:$VB}),o($Vu,[2,67]),o($VC,[2,135],{132:$VD}),o($VE,[2,137]),o($VE,[2,138]),o($VE,[2,139]),o($Vg,[2,120]),o($Ve,[2,116]),o($Vg,[2,126]),o($Vg,[2,128]),o($Vg,[2,129],{49:124,50:$Vh,51:[1,122],52:[1,123]}),o($VF,[2,133]),{16:[1,125]},{117:[1,126]},o($Vk,[2,124]),{23:[1,127]},{5:[1,129],48:[1,128]},o($VG,[2,43],{48:[1,130]}),{33:131,43:132,44:[1,133],45:[1,134]},{16:$VH,37:135,39:136,41:137},o($Vu,[2,69]),o($Vu,[2,75]),o($Vu,[2,76]),o($VE,[2,77],{83:$VI}),o($VJ,[2,78]),o($VJ,[2,80],{85:[1,140]}),o($Vv,$Vw,{88:101,92:102,93:103,100:105,101:106,102:107,87:141,36:$Vx}),o($VK,[2,84]),o($VK,[2,85],{89:142,90:[1,143],94:[1,144],95:[1,145],96:[1,146],97:[1,147],98:[1,148],99:[1,149]}),o($Vb,[2,90]),o($Vb,[2,91]),o($Vv,$Vw,{82:97,84:98,87:100,88:101,92:102,93:103,100:105,101:106,102:107,81:150,3:151,4:$V0,5:$V1,36:$Vx,86:$Vy}),o($Vb,[2,100]),o($Vb,[2,101]),{16:$VL,103:152,104:153,105:$VM},{4:$V9,16:$Va,108:156,113:34,114:35},o($Vu,[2,110]),{4:$V9,16:$Va,108:157,113:34,114:35},o($Vu,[2,112]),o($Vu,[2,113]),o($Vu,[2,114]),{16:$VN,119:158,120:76,121:77,122:78},o($Vu,[2,66]),o($VE,[2,141],{127:160,128:$VB}),o($VE,[2,142],{127:119,123:161,128:$VB}),{5:[1,163],16:[1,162]},o($VO,[2,149]),{129:[1,164]},{4:[1,166],16:$VN,119:165,120:76,121:77,122:78},{5:[1,167],16:$Vs},{5:[1,168],16:$Vt},{16:$Va,114:169},{116:[1,170]},o($Vk,[2,123]),{16:[1,171]},o($VG,[2,38]),o($VG,[2,41],{47:[1,172],48:[1,173]}),o($VG,[2,42]),o($V8,[2,26]),{21:174,46:$Vl},{46:[2,36]},{46:[2,37]},{38:[1,175],40:[1,176]},o($VP,[2,31]),o($VP,[2,33]),{42:177,53:[1,178],54:[1,179],55:[1,180],56:[1,181],57:[1,182],58:[1,183],59:[1,184],60:[1,185],61:[1,186],62:[1,187],63:[1,188],64:[1,189],65:[1,190],66:[1,191]},o($Vv,$Vw,{84:98,87:100,88:101,92:102,93:103,100:105,101:106,102:107,82:192,36:$Vx,86:$Vy}),o($Vv,$Vw,{84:98,87:100,88:101,92:102,93:103,100:105,101:106,102:107,82:194,4:[1,193],36:$Vx,86:$Vy}),o($VK,[2,83]),o($Vv,$Vw,{92:102,93:103,100:105,101:106,102:107,88:195,3:196,4:$V0,5:$V1,36:$Vx}),{86:[1,198],91:[1,197]},o($VQ,[2,92]),o($VQ,[2,93]),o($VQ,[2,94]),o($VQ,[2,95]),o($VQ,[2,96]),o($VQ,[2,97]),{38:[1,199],83:$VI},o($Vb,[2,99]),o($Vb,[2,102],{49:200,50:$Vh,51:$Vi,52:$Vj}),o($VR,[2,104]),o($VR,[2,107]),{16:[1,201]},o($Vu,[2,109],{40:$Vf}),o($Vu,[2,111],{40:$Vf}),o($VC,[2,136],{132:$VD}),o($VE,$Vz,{123:116,49:118,127:119,16:$VA,50:$Vh,51:$Vi,52:$Vj,128:$VB}),o($VO,[2,150]),o($VE,[2,143],{127:160,128:$VB}),o($VE,[2,144],{16:[1,202]}),o($VE,[2,146]),{124:203,125:[1,204],126:[1,205]},{132:$VD,133:206,134:207,135:[1,208]},o($VE,[2,156]),o($Vg,[2,130]),o($Vg,[2,131]),o($VF,[2,134]),{117:[1,209]},o($V8,[2,18]),{48:[1,210]},o($VG,[2,40]),o($V8,[2,35]),o([44,45],[2,30]),{16:$VH,39:211,41:137},o($VP,[2,34]),o($VP,[2,47]),o($VP,[2,48]),o($VP,[2,49]),o($VP,[2,50]),o($VP,[2,51]),o($VP,[2,52]),o($VP,[2,53]),o($VP,[2,54]),o($VP,[2,55]),o($VP,[2,56]),o($VP,[2,57]),o($VP,[2,58]),o($VP,[2,59]),o($VP,[2,60]),o($VJ,[2,79]),o($VJ,[2,81]),o($VJ,[2,82]),o($VK,[2,86]),o($VK,[2,87]),o($VK,[2,88]),{91:[1,212]},o($Vb,[2,98]),{5:[1,213],16:$VL,104:214,105:$VM},{105:[1,215]},o($VE,[2,145]),{16:[1,216],130:217,131:$VS},{36:[1,219]},{36:[1,220]},o($VE,[2,155]),o($VE,[2,157]),o($Vv,$Vw,{81:96,82:97,84:98,87:100,88:101,92:102,93:103,100:105,101:106,102:107,80:221,36:$Vx,86:$Vy}),o($Vk,[2,122]),o($VG,[2,39]),o($VP,[2,32]),o($VK,[2,89]),o($VR,[2,105]),o($VR,[2,106]),o($VR,[2,108]),{130:222,131:$VS},o($VO,[2,152]),{16:[1,223],36:[1,224]},{16:$Va,114:84,118:225},{16:$Va,114:84,118:226},o($VE,[2,158]),o($VO,[2,151]),o($VO,[2,153]),{16:[1,227]},{38:[1,228],49:124,50:$Vh,51:$Vi,52:$Vj},{38:[1,229],49:124,50:$Vh,51:$Vi,52:$Vj},{40:[1,230]},o($VT,[2,147]),o($VT,[2,148]),{16:[1,231]},{38:[1,232]},o($VO,[2,154])],
defaultActions: {20:[2,5],29:[2,28],30:[2,29],38:[2,4],43:[2,24],44:[2,25],133:[2,36],134:[2,37]},
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
    var self = this, stack = [0], tstack = [], vstack = [null], lstack = [], table = this.table, yytext = '', yylineno = 0, yyleng = 0, recovering = 0, TERROR = 2, EOF = 1;
    var args = lstack.slice.call(arguments, 1);
    var lexer = Object.create(this.lexer);
    var sharedState = { yy: {} };
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
    function popStack(n) {
        stack.length = stack.length - 2 * n;
        vstack.length = vstack.length - n;
        lstack.length = lstack.length - n;
    }
    _token_stack:
        var lex = function () {
            var token;
            token = lexer.lex() || EOF;
            if (typeof token !== 'number') {
                token = self.symbols_[token] || token;
            }
            return token;
        };
    var symbol, preErrorSymbol, state, action, a, r, yyval = {}, p, len, newState, expected;
    while (true) {
        state = stack[stack.length - 1];
        if (this.defaultActions[state]) {
            action = this.defaultActions[state];
        } else {
            if (symbol === null || typeof symbol == 'undefined') {
                symbol = lex();
            }
            action = table[state] && table[state][symbol];
        }
                    if (typeof action === 'undefined' || !action.length || !action[0]) {
                var errStr = '';
                expected = [];
                for (p in table[state]) {
                    if (this.terminals_[p] && p > TERROR) {
                        expected.push('\'' + this.terminals_[p] + '\'');
                    }
                }
                if (lexer.showPosition) {
                    errStr = 'Parse error on line ' + (yylineno + 1) + ':\n' + lexer.showPosition() + '\nExpecting ' + expected.join(', ') + ', got \'' + (this.terminals_[symbol] || symbol) + '\'';
                } else {
                    errStr = 'Parse error on line ' + (yylineno + 1) + ': Unexpected ' + (symbol == EOF ? 'end of input' : '\'' + (this.terminals_[symbol] || symbol) + '\'');
                }
                this.parseError(errStr, {
                    text: lexer.match,
                    token: this.terminals_[symbol] || symbol,
                    line: lexer.yylineno,
                    loc: yyloc,
                    expected: expected
                });
            }
        if (action[0] instanceof Array && action.length > 1) {
            throw new Error('Parse Error: multiple actions possible at state: ' + state + ', token: ' + symbol);
        }
        switch (action[0]) {
        case 1:
            stack.push(symbol);
            vstack.push(lexer.yytext);
            lstack.push(lexer.yylloc);
            stack.push(action[1]);
            symbol = null;
            if (!preErrorSymbol) {
                yyleng = lexer.yyleng;
                yytext = lexer.yytext;
                yylineno = lexer.yylineno;
                yyloc = lexer.yylloc;
                if (recovering > 0) {
                    recovering--;
                }
            } else {
                symbol = preErrorSymbol;
                preErrorSymbol = null;
            }
            break;
        case 2:
            len = this.productions_[action[1]][1];
            yyval.$ = vstack[vstack.length - len];
            yyval._$ = {
                first_line: lstack[lstack.length - (len || 1)].first_line,
                last_line: lstack[lstack.length - 1].last_line,
                first_column: lstack[lstack.length - (len || 1)].first_column,
                last_column: lstack[lstack.length - 1].last_column
            };
            if (ranges) {
                yyval._$.range = [
                    lstack[lstack.length - (len || 1)].range[0],
                    lstack[lstack.length - 1].range[1]
                ];
            }
            r = this.performAction.apply(yyval, [
                yytext,
                yyleng,
                yylineno,
                sharedState.yy,
                action[1],
                vstack,
                lstack
            ].concat(args));
            if (typeof r !== 'undefined') {
                return r;
            }
            if (len) {
                stack = stack.slice(0, -1 * len * 2);
                vstack = vstack.slice(0, -1 * len);
                lstack = lstack.slice(0, -1 * len);
            }
            stack.push(this.productions_[action[1]][0]);
            vstack.push(yyval.$);
            lstack.push(yyval._$);
            newState = table[stack[stack.length - 2]][stack[stack.length - 1]];
            stack.push(newState);
            break;
        case 3:
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
case 5: return 85; 
break;
case 6: return 56; 
break;
case 7: return 57; 
break;
case 8: return 107; 
break;
case 9: return 62; 
break;
case 10: return 30; 
break;
case 11: return 61; 
break;
case 12: return 59; 
break;
case 13: return 58; 
break;
case 14: return 72; 
break;
case 15: return 106; 
break;
case 16: return 55; 
break;
case 17: return 22; 
break;
case 18: return 90; 
break;
case 19: return 132; 
break;
case 20: return 86; 
break;
case 21: return 135; 
break;
case 22: return 83; 
break;
case 23: return 109; 
break;
case 24: determineCase(yy_.yytext); return 67; 
break;
case 25: return 54; 
break;
case 26: return 60; 
break;
case 27: return 23; 
break;
case 28: return 64; 
break;
case 29: return 53; 
break;
case 30: determineCase(yy_.yytext); return 17; 
break;
case 31: return 63; 
break;
case 32: return 129; 
break;
case 33: return 79; 
break;
case 34: return 131; 
break;
case 35: return 65; 
break;
case 36: return 26; 
break;
case 37: return 66; 
break;
case 38: return 34; 
break;
case 39: this.begin('hdfs'); return 28; 
break;
case 40: return 128; 
break;
case 41: return 24; 
break;
case 42: this.begin('hdfs'); return 44; 
break;
case 43: return 125; 
break;
case 44: return 126; 
break;
case 45: return 52; 
break;
case 46: return 27; 
break;
case 47: return 35; 
break;
case 48: this.begin('hdfs'); return 29; 
break;
case 49: return 25; 
break;
case 50: this.begin('hdfs'); return 45; 
break;
case 51: return 51; 
break;
case 52: return 111; 
break;
case 53: return 16; 
break;
case 54: parser.yy.cursorFound = true; return 4; 
break;
case 55: parser.yy.cursorFound = true; return 5; 
break;
case 56: return 46; 
break;
case 57: return 47; 
break;
case 58: this.popState(); return 48; 
break;
case 59: return 10; 
break;
case 60: return yy_.yytext; 
break;
case 61: return yy_.yytext; 
break;
case 62: return 115; 
break;
case 63: return 117; 
break;
case 64: return 'SINGLE_QUOTE'; 
break;
case 65: return 116; 
break;
case 66: return 10; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:SELECT\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:AS\b)/i,/^(?:BINARY\b)/i,/^(?:DATA\b)/i,/^(?:DATE\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:DATA\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:[.])/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:\s+['])/i,/^(?:[^'|]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:')/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[54,55,56,57,58,59],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,52,53,60,61,62,63,64,65,66],"inclusive":true},"impala":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,46,47,48,49,50,51,52,53,60,61,62,63,64,65,66],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,52,53,60,61,62,63,64,65,66],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});