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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,17],$V1=[1,18],$V2=[1,8],$V3=[1,47],$V4=[1,48],$V5=[1,20],$V6=[1,49],$V7=[1,50],$V8=[1,51],$V9=[1,24],$Va=[1,46],$Vb=[1,27],$Vc=[1,16],$Vd=[12,13],$Ve=[4,7,12,13,40,42,108,134,147,153,226,229,231,235,239,240,241,242,243,256,257,260,261,282],$Vf=[1,61],$Vg=[1,60],$Vh=[1,65],$Vi=[1,68],$Vj=[1,75],$Vk=[1,76],$Vl=[1,77],$Vm=[1,78],$Vn=[1,79],$Vo=[1,123],$Vp=[1,124],$Vq=[4,7,28,29],$Vr=[4,7,54,55,56,69,70,183,184],$Vs=[1,136],$Vt=[4,7,30,31],$Vu=[1,141],$Vv=[2,4,7,12,13,40,54,55,56,76,107,108,109,116,117,127,129,134,140,141,147,153,154,155,163,170,226,256,257,260,261,272,278,282],$Vw=[2,4],$Vx=[4,12,13,34],$Vy=[2,426],$Vz=[1,148],$VA=[1,146],$VB=[1,147],$VC=[4,12,13,34,40,134,153,226,256,257,260,261,282],$VD=[7,12,13],$VE=[54,55,56],$VF=[4,7,12,13,71,272],$VG=[4,7,12,13,272],$VH=[2,77],$VI=[1,159],$VJ=[1,166],$VK=[1,168],$VL=[1,169],$VM=[1,174],$VN=[1,175],$VO=[4,7,76],$VP=[1,186],$VQ=[1,188],$VR=[12,13,134],$VS=[1,202],$VT=[4,7,12,13,76,170],$VU=[2,242],$VV=[1,216],$VW=[1,217],$VX=[4,7,54,55,56],$VY=[4,7,116,117],$VZ=[4,7,127],$V_=[4,7,134],$V$=[4,7,132,136],$V01=[4,7,12,13,76,109,163,170],$V11=[12,13,108],$V21=[1,223],$V31=[4,7,12,13,40,108,153,226,256,257,260,261],$V41=[4,5,7,12,13,40,42,107,108,134,147,153,199,200,226,229,231,235,239,240,241,242,243,256,257,260,261,282],$V51=[2,392],$V61=[1,227],$V71=[1,229],$V81=[1,234],$V91=[2,427],$Va1=[1,238],$Vb1=[5,7,254,262,272],$Vc1=[2,306],$Vd1=[2,307],$Ve1=[4,7,12,13,34,40,98,134,143,144,153,226,256,257,260,261,282],$Vf1=[1,243],$Vg1=[1,249],$Vh1=[1,250],$Vi1=[2,129],$Vj1=[4,7,12,13,98,143,144],$Vk1=[1,261],$Vl1=[12,13,107],$Vm1=[4,7,12,13,76],$Vn1=[1,288],$Vo1=[1,289],$Vp1=[2,233],$Vq1=[2,219],$Vr1=[1,296],$Vs1=[1,297],$Vt1=[4,7,272],$Vu1=[1,312],$Vv1=[1,319],$Vw1=[1,313],$Vx1=[1,317],$Vy1=[1,318],$Vz1=[1,315],$VA1=[1,316],$VB1=[1,332],$VC1=[4,12,13,40,226],$VD1=[1,346],$VE1=[2,4,7,12,13,34,40,98,108,134,143,144,153,226,256,257,260,261,282],$VF1=[1,354],$VG1=[2,274],$VH1=[4,7,12,13,63,64,76,108,109,170],$VI1=[2,415],$VJ1=[4,12,13,40,134,153,226,256,257,260,261,282],$VK1=[1,389],$VL1=[4,12,13,153,226,256,257,260,261],$VM1=[7,254],$VN1=[2,370],$VO1=[1,415],$VP1=[1,410],$VQ1=[1,420],$VR1=[1,421],$VS1=[4,7,258],$VT1=[4,12,13,40,153,226,256,257,260,261],$VU1=[1,430],$VV1=[1,432],$VW1=[1,434],$VX1=[4,7,12,13,40,107,108,147,153,199,200,226,256,257,260,261],$VY1=[2,4,7,12,13,24,175,191,192,193,194],$VZ1=[1,456],$V_1=[1,457],$V$1=[40,147],$V02=[1,482],$V12=[1,483],$V22=[1,484],$V32=[1,504],$V42=[12,13,40,147],$V52=[1,512],$V62=[4,12,13,40,134,147,153,226,229,256,257,260,261,282],$V72=[4,12,13,40,134,147,153,226,229,231,256,257,260,261,282],$V82=[4,12,13,40,42,134,147,153,226,229,231,235,239,240,241,242,243,256,257,260,261,282],$V92=[1,529],$Va2=[1,533],$Vb2=[4,12,13,40,134,153,226,256,257,260,261,278,282],$Vc2=[2,4,175,191,192,193,194],$Vd2=[4,5,7,145,170,245,246,254],$Ve2=[4,12,13,40,42,107,134,147,153,199,200,226,229,231,235,239,240,241,242,243,256,257,260,261,282],$Vf2=[1,609],$Vg2=[1,615],$Vh2=[1,616],$Vi2=[4,7,281];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"PartialIdentifierOrCursor":6,"REGULAR_IDENTIFIER":7,"PartialIdentifierOrPartialCursor":8,"InitResults":9,"Sql":10,"SqlStatements":11,";":12,"EOF":13,"SqlStatement":14,"DataManipulation":15,"DataDefinition":16,"QueryExpression":17,"LoadStatement":18,"UpdateStatement":19,"HiveOrImpalaLoad":20,"HiveOrImpalaData":21,"HiveOrImpalaInpath":22,"HdfsPath":23,"INTO":24,"AnyTable":25,"<hive>LOAD":26,"<impala>LOAD":27,"<hive>DATA":28,"<impala>DATA":29,"<hive>INPATH":30,"<impala>INPATH":31,"UPDATE":32,"TargetTable":33,"SET":34,"SetClauseList":35,"WhereClause":36,"TableName":37,"LocalOrSchemaQualifiedName":38,"SetClause":39,",":40,"SetTarget":41,"=":42,"UpdateSource":43,"ValueExpression":44,"BooleanValueExpression":45,"CreateStatement":46,"DropStatement":47,"ShowStatement":48,"UseStatement":49,"AnyCreate":50,"CREATE":51,"<hive>CREATE":52,"<impala>CREATE":53,"TABLE":54,"<hive>TABLE":55,"<impala>TABLE":56,"TableDefinition":57,"DatabaseDefinition":58,"DROP":59,"DropDatabaseStatement":60,"DropTableStatement":61,"OptionalHiveCascadeOrRestrict":62,"<hive>CASCADE":63,"<hive>RESTRICT":64,"DatabaseOrSchema":65,"OptionalIfExists":66,"RegularOrBacktickedIdentifier":67,"TablePrimary":68,"DATABASE":69,"SCHEMA":70,"IF":71,"EXISTS":72,"USE":73,"SHOW":74,"CleanRegularOrBackTickedSchemaQualifiedName":75,"LIKE":76,"SingleQuotedValue":77,"ShowColumnStatement":78,"ShowColumnsStatement":79,"ShowCompactionsStatement":80,"ShowConfStatement":81,"ShowCreateTableStatement":82,"ShowCurrentStatement":83,"ShowDatabasesStatement":84,"ShowFunctionsStatement":85,"ShowGrantStatement":86,"ShowIndexStatement":87,"ShowLocksStatement":88,"ShowPartitionsStatement":89,"ShowRoleStatement":90,"ShowRolesStatement":91,"ShowTableStatement":92,"ShowTablesStatement":93,"ShowTblPropertiesStatement":94,"ShowTransactionsStatement":95,"<impala>COLUMN":96,"<impala>STATS":97,"if":98,"partial":99,"identifierChain":100,"length":101,"<hive>COLUMNS":102,"AnyFromOrIn":103,"<hive>COMPACTIONS":104,"<hive>CONF":105,"ConfigurationName":106,"<hive>.":107,"FROM":108,"<hive>IN":109,"HiveOrImpalaCreate":110,"RegularOrBackTickedSchemaQualifiedName":111,"HiveOrImpalaCurrent":112,"HiveOrImpalaRoles":113,"<hive>CURRENT":114,"<impala>CURRENT":115,"<hive>ROLES":116,"<impala>ROLES":117,"HiveOrImpalaDatabasesOrSchemas":118,"<impala>DATABASES":119,"<hive>DATABASES":120,"<hive>SCHEMAS":121,"<impala>SCHEMAS":122,"<hive>FUNCTIONS":123,"DoubleQuotedValue":124,"AggregateOrAnalytic":125,"OptionalAggregateOrAnalytic":126,"<impala>FUNCTIONS":127,"OptionalInDatabase":128,"SingleQuoteValue":129,"<impala>AGGREGATE":130,"<impala>ANALYTIC":131,"<hive>GRANT":132,"OptionalPrincipalName":133,"ON":134,"<hive>ALL":135,"<impala>GRANT":136,"<hive>FORMATTED":137,"OptionallyFormattedIndex":138,"IndexOrIndexes":139,"<hive>INDEX":140,"<hive>INDEXES":141,"<hive>LOCKS":142,"<hive>EXTENDED":143,"<hive>PARTITION":144,"(":145,"PartitionSpecList":146,")":147,"PartitionSpec":148,"<hive>PARTITIONS":149,"<impala>PARTITIONS":150,"HiveOrImpalaRole":151,"HiveRoleOrUser":152,"<impala>GROUP":153,"<hive>ROLE":154,"<hive>USER":155,"<impala>ROLE":156,"OptionalFromDatabase":157,"FromOrIn":158,"HiveOrImpalaTables":159,"HiveOrImpalaIn":160,"<hive>TABLES":161,"<impala>TABLES":162,"<impala>IN":163,"<hive>TBLPROPERTIES":164,"<hive>TRANSACTIONS":165,"OptionalIfNotExists":166,"NOT":167,"Comment":168,"HiveOrImpalaComment":169,"SINGLE_QUOTE":170,"VALUE":171,"HivePropertyAssignmentList":172,"HivePropertyAssignment":173,"HiveDbProperties":174,"<hive>WITH":175,"DBPROPERTIES":176,"DatabaseDefinitionOptionals":177,"DatabaseDefinitionOptional":178,"HdfsLocation":179,"CleanUpDatabaseConditions":180,"TableScope":181,"TableElementList":182,"<hive>EXTERNAL":183,"<impala>EXTERNAL":184,"TableElements":185,"TableElement":186,"ColumnDefinition":187,"PrimitiveType":188,"ColumnDefinitionError":189,"HiveOrImpalaLocation":190,"<hive>LOCATION":191,"<impala>LOCATION":192,"<hive>COMMENT":193,"<impala>COMMENT":194,"HDFS_START_QUOTE":195,"HDFS_PATH":196,"HDFS_END_QUOTE":197,"AnyDot":198,".":199,"<impala>.":200,"TINYINT":201,"SMALLINT":202,"INT":203,"BIGINT":204,"BOOLEAN":205,"FLOAT":206,"DOUBLE":207,"STRING":208,"DECIMAL":209,"CHAR":210,"VARCHAR":211,"TIMESTAMP":212,"<hive>BINARY":213,"<hive>DATE":214,"SELECT":215,"CleanUpSelectConditions":216,"SelectList":217,"TableExpression":218,"FromClause":219,"SelectConditionList":220,"TableReferenceList":221,"SelectCondition":222,"GroupByClause":223,"OrderByClause":224,"LimitClause":225,"WHERE":226,"SearchCondition":227,"BooleanTerm":228,"OR":229,"BooleanFactor":230,"AND":231,"BooleanTest":232,"Predicate":233,"CompOp":234,"IS":235,"TruthValue":236,"ParenthesizedBooleanValueExpression":237,"NonParenthesizedValueExpressionPrimary":238,"<>":239,"<=":240,">=":241,"<":242,">":243,"SignedInteger":244,"UNSIGNED_INTEGER":245,"-":246,"DOUBLE_QUOTE":247,"ColumnReference":248,"BasicIdentifierChain":249,"InitIdentifierChain":250,"IdentifierChain":251,"Identifier":252,"ColumnIdentifier":253,"\"":254,"AnyGroup":255,"GROUP":256,"<hive>GROUP":257,"BY":258,"ColumnList":259,"ORDER":260,"LIMIT":261,"*":262,"DerivedColumn":263,"[":264,"]":265,"DerivedColumnChain":266,"TableReference":267,"TablePrimaryOrJoinedTable":268,"LateralViewDefinition":269,"JoinedTable":270,"LateralViews":271,"BACKTICK":272,"PARTIAL_VALUE":273,"userDefinedTableGeneratingFunction":274,"<hive>explode":275,"<hive>posexplode":276,"LateralView":277,"<hive>LATERAL":278,"VIEW":279,"LateralViewColumnAliases":280,"<hive>AS":281,"JOIN":282,"JoinSpecification":283,"JoinCondition":284,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",7:"REGULAR_IDENTIFIER",12:";",13:"EOF",24:"INTO",26:"<hive>LOAD",27:"<impala>LOAD",28:"<hive>DATA",29:"<impala>DATA",30:"<hive>INPATH",31:"<impala>INPATH",32:"UPDATE",34:"SET",40:",",42:"=",51:"CREATE",52:"<hive>CREATE",53:"<impala>CREATE",54:"TABLE",55:"<hive>TABLE",56:"<impala>TABLE",59:"DROP",63:"<hive>CASCADE",64:"<hive>RESTRICT",69:"DATABASE",70:"SCHEMA",71:"IF",72:"EXISTS",73:"USE",74:"SHOW",76:"LIKE",96:"<impala>COLUMN",97:"<impala>STATS",98:"if",99:"partial",100:"identifierChain",101:"length",102:"<hive>COLUMNS",104:"<hive>COMPACTIONS",105:"<hive>CONF",107:"<hive>.",108:"FROM",109:"<hive>IN",114:"<hive>CURRENT",115:"<impala>CURRENT",116:"<hive>ROLES",117:"<impala>ROLES",119:"<impala>DATABASES",120:"<hive>DATABASES",121:"<hive>SCHEMAS",122:"<impala>SCHEMAS",123:"<hive>FUNCTIONS",127:"<impala>FUNCTIONS",129:"SingleQuoteValue",130:"<impala>AGGREGATE",131:"<impala>ANALYTIC",132:"<hive>GRANT",134:"ON",135:"<hive>ALL",136:"<impala>GRANT",137:"<hive>FORMATTED",140:"<hive>INDEX",141:"<hive>INDEXES",142:"<hive>LOCKS",143:"<hive>EXTENDED",144:"<hive>PARTITION",145:"(",147:")",149:"<hive>PARTITIONS",150:"<impala>PARTITIONS",153:"<impala>GROUP",154:"<hive>ROLE",155:"<hive>USER",156:"<impala>ROLE",161:"<hive>TABLES",162:"<impala>TABLES",163:"<impala>IN",164:"<hive>TBLPROPERTIES",165:"<hive>TRANSACTIONS",167:"NOT",170:"SINGLE_QUOTE",171:"VALUE",175:"<hive>WITH",176:"DBPROPERTIES",183:"<hive>EXTERNAL",184:"<impala>EXTERNAL",191:"<hive>LOCATION",192:"<impala>LOCATION",193:"<hive>COMMENT",194:"<impala>COMMENT",195:"HDFS_START_QUOTE",196:"HDFS_PATH",197:"HDFS_END_QUOTE",199:".",200:"<impala>.",201:"TINYINT",202:"SMALLINT",203:"INT",204:"BIGINT",205:"BOOLEAN",206:"FLOAT",207:"DOUBLE",208:"STRING",209:"DECIMAL",210:"CHAR",211:"VARCHAR",212:"TIMESTAMP",213:"<hive>BINARY",214:"<hive>DATE",215:"SELECT",226:"WHERE",229:"OR",231:"AND",235:"IS",236:"TruthValue",239:"<>",240:"<=",241:">=",242:"<",243:">",245:"UNSIGNED_INTEGER",246:"-",247:"DOUBLE_QUOTE",254:"\"",256:"GROUP",257:"<hive>GROUP",258:"BY",260:"ORDER",261:"LIMIT",262:"*",264:"[",265:"]",272:"BACKTICK",273:"PARTIAL_VALUE",275:"<hive>explode",276:"<hive>posexplode",278:"<hive>LATERAL",279:"VIEW",281:"<hive>AS",282:"JOIN"},
productions_: [0,[3,1],[3,1],[6,2],[6,1],[8,2],[8,1],[9,0],[10,4],[10,3],[11,1],[11,3],[14,1],[14,1],[14,1],[14,3],[14,2],[14,1],[15,1],[15,1],[18,7],[18,6],[18,5],[18,4],[18,3],[18,2],[20,1],[20,1],[21,1],[21,1],[22,1],[22,1],[19,5],[19,5],[19,4],[19,3],[19,2],[19,2],[33,1],[37,1],[35,1],[35,3],[39,3],[39,2],[39,1],[41,1],[43,1],[44,1],[16,1],[16,1],[16,1],[16,1],[50,1],[50,1],[50,1],[25,1],[25,1],[25,1],[46,1],[46,1],[46,2],[47,2],[47,1],[47,1],[62,0],[62,1],[62,1],[60,3],[60,4],[60,5],[60,5],[61,3],[61,4],[61,4],[61,5],[65,1],[65,1],[66,0],[66,2],[66,2],[49,2],[49,2],[48,2],[48,3],[48,4],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[48,1],[78,3],[78,4],[78,8],[79,3],[79,4],[79,4],[79,5],[79,6],[79,4],[79,5],[79,6],[79,6],[79,6],[80,2],[81,3],[106,1],[106,1],[106,3],[106,3],[106,3],[103,1],[103,1],[82,3],[82,4],[82,4],[82,4],[75,1],[75,1],[110,1],[110,1],[83,3],[83,3],[83,3],[112,1],[112,1],[113,1],[113,1],[84,3],[84,4],[84,3],[118,1],[118,1],[118,1],[118,1],[85,2],[85,3],[85,3],[85,4],[85,4],[85,5],[85,6],[85,6],[85,6],[85,6],[126,0],[126,1],[125,1],[125,1],[86,3],[86,5],[86,5],[86,5],[86,6],[86,6],[86,6],[86,3],[133,0],[133,1],[133,1],[133,2],[87,3],[87,3],[87,4],[87,4],[87,4],[87,5],[87,6],[87,6],[87,6],[87,6],[138,2],[138,2],[138,1],[139,1],[139,1],[88,3],[88,3],[88,4],[88,4],[88,7],[88,8],[88,8],[88,4],[88,4],[146,1],[146,3],[148,3],[89,3],[89,7],[89,4],[89,5],[89,3],[89,7],[90,3],[90,5],[90,4],[90,5],[90,5],[90,4],[90,5],[90,5],[152,1],[152,1],[151,1],[151,1],[91,2],[92,3],[92,4],[92,5],[92,6],[92,6],[92,6],[92,7],[92,8],[92,8],[92,8],[92,8],[92,3],[92,4],[92,8],[157,0],[157,2],[157,2],[158,1],[158,1],[93,3],[93,4],[93,4],[93,5],[128,0],[128,2],[128,2],[159,1],[159,1],[160,1],[160,1],[94,3],[95,2],[166,0],[166,2],[166,3],[166,3],[166,1],[168,2],[168,3],[168,4],[172,1],[172,3],[173,3],[173,7],[174,5],[174,2],[174,2],[177,1],[177,2],[177,3],[178,1],[178,1],[178,1],[180,0],[58,3],[58,4],[58,5],[58,7],[58,7],[57,6],[57,5],[57,4],[57,3],[57,6],[57,4],[181,1],[181,1],[182,3],[185,1],[185,3],[186,1],[187,2],[187,2],[187,4],[189,0],[179,2],[190,1],[190,1],[169,1],[169,1],[23,3],[23,5],[23,4],[23,3],[23,3],[23,2],[198,1],[198,1],[198,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[188,1],[17,4],[17,3],[218,1],[218,2],[216,0],[219,2],[219,2],[220,1],[220,2],[222,1],[222,1],[222,1],[222,1],[222,1],[36,2],[36,2],[227,1],[45,1],[45,3],[228,1],[228,3],[228,3],[230,2],[230,1],[232,1],[232,3],[232,3],[232,3],[232,4],[233,1],[233,1],[234,1],[234,1],[234,1],[234,1],[234,1],[234,1],[237,3],[237,2],[244,1],[244,2],[77,3],[124,3],[238,1],[238,1],[238,1],[248,1],[249,2],[250,0],[251,1],[251,3],[251,3],[252,1],[252,2],[252,3],[255,1],[255,1],[255,1],[223,3],[223,2],[224,3],[224,2],[225,2],[225,2],[217,1],[217,2],[217,2],[217,1],[259,1],[259,3],[253,1],[253,4],[253,4],[253,3],[263,1],[263,3],[263,2],[263,3],[263,3],[263,5],[263,5],[263,1],[266,1],[266,3],[221,1],[221,3],[267,1],[268,1],[268,1],[268,1],[269,2],[269,3],[68,1],[67,1],[67,3],[111,3],[111,5],[111,5],[111,7],[111,6],[111,3],[111,5],[111,2],[111,3],[38,1],[38,2],[38,1],[38,2],[274,4],[274,4],[274,4],[274,4],[271,1],[271,2],[277,5],[277,4],[277,5],[277,4],[277,3],[277,2],[280,2],[280,6],[270,4],[270,4],[270,3],[283,1],[284,2]],
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
case 32: case 34: case 322:

     linkTablePrimaries();
   
break;
case 33:

     suggestKeywords([ 'WHERE' ]);
   
break;
case 35:

     suggestKeywords([ 'SET' ]);
   
break;
case 37: case 328:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 39:

     // TODO: Replace with TablePrimary?
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 43:

     suggestKeywords([ '=' ]);
   
break;
case 44: case 337: case 375:

     suggestColumns();
   
break;
case 60:

     if (isHive() || isImpala()) {
       suggestKeywords(['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
   
break;
case 61:

     if (isHive()) {
       suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'MACRO', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
     } else {
       suggestKeywords(['ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   
break;
case 68:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   
break;
case 69:

     if (isHive()) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   
break;
case 72:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 73:

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
case 74:

     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   
break;
case 77:
 this.$ = false 
break;
case 78: case 253:

     suggestKeywords(['EXISTS']);
   
break;
case 80:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
case 81: case 114: case 180: case 195:

     suggestDatabases();
   
break;
case 82:

     if (isHive()) {
       suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
     } else {
       suggestKeywords(['COLUMNS', 'DATABASES', 'TABLES']);
     }
   
break;
case 83:

     if (isImpala()) {
       suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'PARTITIONS', 'TABLE STATS']);
     }
   
break;
case 84:

     if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'DATABASES', 'FUNCTIONS', 'SCHEMAS', 'TABLES']);
     } else if (isHive()) {
       suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
     }
   
break;
case 103: case 230:

     suggestKeywords(['STATS']);
   
break;
case 104: case 126: case 200: case 204: case 231:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 105: case 232:

     suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
   
break;
case 106: case 107: case 112: case 113: case 178: case 179:

     suggestKeywords(['FROM', 'IN']);
   
break;
case 108: case 109: case 110: case 165: case 175: case 249:

     suggestTables();
   
break;
case 125: case 128: case 167:

     suggestKeywords(['TABLE']);
   
break;
case 127:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name);
     }
   
break;
case 129: case 426:

     this.$ = { identifierChain: [ { name: $$[$0] } ] }
   
break;
case 130: case 352: case 365: case 368:

     this.$ = $$[$0];
   
break;
case 133:

     suggestKeywords([ 'ROLES' ]);
   
break;
case 134:

     suggestKeywords([ 'CURRENT' ]);
   
break;
case 140: case 228:

     suggestKeywords(['LIKE']);
   
break;
case 149: case 154:

     suggestKeywords(['FUNCTIONS']);
   
break;
case 151: case 155:

     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   
break;
case 152: case 239:

     if (!$$[$0-1]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 156:

     if (!$$[$0-2]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 157: case 233: case 242:

     this.$ = false;
   
break;
case 158: case 171: case 172: case 234: case 244:

     this.$ = true;
   
break;
case 161:

     if ($$[$0]) {
       suggestKeywords(['ON']);
     }
   
break;
case 163:

     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   
break;
case 168:

     suggestKeywords(['ROLE']);
   
break;
case 173:

     suggestKeywords(['INDEX', 'INDEXES']);
   
break;
case 174: case 176: case 445:

     suggestKeywords(['ON']);
   
break;
case 181:

     suggestTablesOrColumns($$[$0]);
   
break;
case 184:

     suggestKeywords(['FORMATTED']);
   
break;
case 188:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
     suggestKeywords(['DATABASE', 'SCHEMA']);
   
break;
case 189:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name)
     }
   
break;
case 190:

      suggestKeywords(['EXTENDED', 'PARTITION']);
    
break;
case 191:

     if ($$[$0-1].partial && $$[$0-1].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-1].identifierChain[0].name)
     }
   
break;
case 192:

     if ($$[$0-4].partial && $$[$0-4].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
     }
   
break;
case 193: case 219: case 227:

     suggestKeywords(['EXTENDED']);
   
break;
case 194:

     // TODO: Move into CleanRegularOrBackTickedSchemaQualifiedName
     if ($$[$0-5].partial && $$[$0-5].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
     }
   
break;
case 201: case 205:

     suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
   
break;
case 202: case 229:

     suggestKeywords(['PARTITION']);
   
break;
case 206: case 207:

     suggestKeywords(['GRANT']);
   
break;
case 208: case 209:

     suggestKeywords(['ROLE', 'USER']);
   
break;
case 211: case 212:

     suggestKeywords(['GROUP']);
   
break;
case 221:

      if ($$[$0-1]) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    
break;
case 225:

      suggestKeywords(['PARTITION']);
    
break;
case 235: case 243:

     this.$ = true;
     suggestDatabases();
   
break;
case 252:

     suggestKeywords(['NOT EXISTS']);
   
break;
case 255:

     suggestKeywords(['IF NOT EXISTS']);
   
break;
case 265:

     suggestKeywords(['DBPROPERTIES']);
   
break;
case 269:

     parser.yy.afterComment = true;
   
break;
case 270:

     parser.yy.afterHdfsLocation = true;
   
break;
case 271:

     parser.yy.afterHiveDbProperties = true;
   
break;
case 272:

     delete parser.yy.afterComment;
     delete parser.yy.afterHdfsLocation;
     delete parser.yy.afterHiveDbProperties;
   
break;
case 275:

     if (isHive()) {
       suggestKeywords(['COMMENT', 'LOCATION', 'WITH DBPROPERTIES']);
     } else if (isImpala()) {
       suggestKeywords(['COMMENT', 'LOCATION']);
     }
   
break;
case 277:

     var keywords = [];
     if (! parser.yy.afterComment) {
       keywords.push('COMMENT');
     }
     if (! parser.yy.afterHdfsLocation) {
       keywords.push('LOCATION');
     }
     if (! parser.yy.afterHiveDbProperties && isHive()) {
       keywords.push('WITH DBPROPERTIES');
     }
     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   
break;
case 279: case 280: case 281:

      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    
break;
case 282:

     if (isHive() || isImpala()) {
       suggestKeywords(['LOCATION']);
     }
   
break;
case 291: case 293:

     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   
break;
case 300:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 301:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 302:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 303:

     suggestHdfs({ path: '' });
   
break;
case 304:

      suggestHdfs({ path: '' });
    
break;
case 326:

     delete parser.yy.afterGroupBy;
     delete parser.yy.afterLimit;
     delete parser.yy.afterOrderBy;
     delete parser.yy.afterWhere;
   
break;
case 331:

     parser.yy.afterWhere = true;
   
break;
case 332:

     parser.yy.afterGroupBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 333:

     parser.yy.afterOrderBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 334:

     parser.yy.afterLimit = true;
     delete parser.yy.result.suggestStar;
   
break;
case 335:

     var keywords = [];
     if (!parser.yy.afterGroupBy) {
       keywords.push('GROUP BY');
     }
     if (!parser.yy.afterGroupBy && !parser.yy.afterWhere && !parser.yy.afterOrderBy && !parser.yy.afterLimit) {
       keywords.push('JOIN');
       if (isHive()) {
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
case 342:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 348:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 360:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 364:

     this.$ = $$[$0-1];
   
break;
case 369:

     this.$ = parser.yy.identifierChain;
     delete parser.yy.identifierChain;
   
break;
case 370:

     parser.yy.identifierChain = [];
   
break;
case 372:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 374:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 376:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 381: case 383:

     suggestKeywords(['BY']);
   
break;
case 385:

     suggestNumbers([1, 5, 10]);
   
break;
case 387: case 388:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 392:

     this.$ = { name: $$[$0] }
   
break;
case 393:

     this.$ = { name: $$[$0-3], key: '"' + $$[$0-1] + '"' }
   
break;
case 394:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 395:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 397:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 398:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 400:

      delete parser.yy.derivedColumnChain;
   
break;
case 401: case 402:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 403:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 404:

     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 405:

     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 409:

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
case 410:

     addTablePrimary($$[$0]);
   
break;
case 412:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], lateralViews: $$[$0] }
   
break;
case 413:

     this.$ = { identifierChain: [ { name: $$[$0-2] } ], alias: $$[$0-1], lateralViews: $$[$0] };
   
break;
case 416:

     this.$ = $$[$0-2];
   
break;
case 417:

     this.$ = { identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] }
   
break;
case 418:

     this.$ = { identifierChain: [ { name: $$[$0-3] }, { name: $$[$0] } ] }
   
break;
case 419:

     this.$ = { identifierChain: [ { name: $$[$0-4] }, { name: $$[$0-1] } ] }
   
break;
case 420:

     this.$ = { identifierChain: [ { name: $$[$0-5] }, { name: $$[$0-1] } ] }
   
break;
case 421:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-4] } ] };
   
break;
case 422:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-2] } ] };
   
break;
case 423:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-3] } ] };
   
break;
case 424:

     this.$ = { partial: true, identifierChain: [ ] };
   
break;
case 425:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ] }
   
break;
case 427:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] };
   
break;
case 429:

     this.$ = { identifierChain: $$[$0-1].identifierChain, alias: $$[$0] }
   
break;
case 430:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 432:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 434:

     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 435:

     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 436:

     this.$ = { udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }
   
break;
case 437:

      this.$ = { udtf: $$[$0-1], columnAliases: $$[$0] }
    
break;
case 438: case 439:

     suggestKeywords(['AS']);
   
break;
case 440:

     suggestKeywords(['explode', 'posexplode']);
   
break;
case 441:

     suggestKeywords(['VIEW']);
   
break;
case 442:

     this.$ = [ $$[$0] ]
   
break;
case 443:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 446:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,7,26,27,32,51,52,53,59,73,74,215],[2,7],{10:1,9:2}),{1:[3]},{3:9,4:$V0,5:$V1,7:$V2,11:3,14:4,15:5,16:6,17:7,18:10,19:11,20:19,26:$V3,27:$V4,32:$V5,46:12,47:13,48:14,49:15,50:23,51:$V6,52:$V7,53:$V8,57:21,58:22,59:$V9,60:25,61:26,73:$Va,74:$Vb,78:28,79:29,80:30,81:31,82:32,83:33,84:34,85:35,86:36,87:37,88:38,89:39,90:40,91:41,92:42,93:43,94:44,95:45,215:$Vc},{12:[1,52],13:[1,53]},o($Vd,[2,10]),o($Vd,[2,12]),o($Vd,[2,13]),o($Vd,[2,14]),{5:[1,54]},o($Vd,[2,17]),o($Vd,[2,18]),o($Vd,[2,19]),o($Vd,[2,48]),o($Vd,[2,49]),o($Vd,[2,50]),o($Vd,[2,51]),o([4,5,7,262],[2,326],{216:55}),o($Ve,[2,1]),o($Ve,[2,2]),{4:$Vf,6:57,7:$Vg,21:56,28:[1,58],29:[1,59]},{4:$Vf,6:63,7:$Vh,33:62,37:64,38:66,111:67,272:$Vi},o($Vd,[2,58]),o($Vd,[2,59]),{4:$Vf,6:69,7:$Vg,25:71,54:$Vj,55:$Vk,56:$Vl,65:72,69:$Vm,70:$Vn,181:70,183:[1,73],184:[1,74]},{4:$Vf,6:80,7:$Vg,25:82,54:$Vj,55:$Vk,56:$Vl,65:81,69:$Vm,70:$Vn},o($Vd,[2,62]),o($Vd,[2,63]),{4:$Vf,6:83,7:$Vg,52:[1,109],53:[1,110],55:[1,104],56:[1,105],96:[1,84],102:[1,85],104:[1,86],105:[1,87],110:88,112:89,114:[1,111],115:[1,112],117:[1,103],118:90,119:[1,91],120:[1,113],121:[1,114],122:[1,115],123:[1,92],125:93,126:94,127:[2,157],130:[1,116],131:[1,117],132:[1,95],136:[1,96],137:[1,97],138:98,139:118,140:$Vo,141:$Vp,142:[1,99],149:[1,100],150:[1,101],151:102,154:[1,119],156:[1,120],159:106,161:[1,121],162:[1,122],164:[1,107],165:[1,108]},o($Vd,[2,85]),o($Vd,[2,86]),o($Vd,[2,87]),o($Vd,[2,88]),o($Vd,[2,89]),o($Vd,[2,90]),o($Vd,[2,91]),o($Vd,[2,92]),o($Vd,[2,93]),o($Vd,[2,94]),o($Vd,[2,95]),o($Vd,[2,96]),o($Vd,[2,97]),o($Vd,[2,98]),o($Vd,[2,99]),o($Vd,[2,100]),o($Vd,[2,101]),o($Vd,[2,102]),{4:$Vf,6:126,7:[1,125]},o($Vq,[2,26]),o($Vq,[2,27]),o($Vr,[2,52]),o($Vr,[2,53]),o($Vr,[2,54]),{3:9,4:$V0,5:$V1,7:$V2,13:[1,127],14:128,15:5,16:6,17:7,18:10,19:11,20:19,26:$V3,27:$V4,32:$V5,46:12,47:13,48:14,49:15,50:23,51:$V6,52:$V7,53:$V8,57:21,58:22,59:$V9,60:25,61:26,73:$Va,74:$Vb,78:28,79:29,80:30,81:31,82:32,83:33,84:34,85:35,86:36,87:37,88:38,89:39,90:40,91:41,92:42,93:43,94:44,95:45,215:$Vc},{1:[2,9]},o($Vd,[2,16],{7:[1,129]}),{3:135,4:$V0,5:$V1,7:$Vs,217:130,253:134,259:131,262:[1,132],263:133},{4:$Vf,6:138,7:$Vg,22:137,30:[1,139],31:[1,140]},o($Vd,[2,25]),o($Vt,[2,28]),o($Vt,[2,29]),{5:$Vu},o($Vv,$Vw),o($Vd,[2,36],{4:[1,143],34:[1,142]}),o($Vd,[2,37]),o($Vx,[2,38]),o($Vx,$Vy,{198:145,5:$Vu,7:[1,144],107:$Vz,199:$VA,200:$VB}),o($Vx,[2,39]),o($VC,[2,428],{7:[1,149]}),{171:[1,150],273:[1,151]},o($Vd,[2,60],{25:152,54:$Vj,55:$Vk,56:$Vl}),{25:153,54:$Vj,55:$Vk,56:$Vl},{7:[1,154]},o($VD,[2,251],{166:155,4:[1,157],71:[1,156]}),o($VE,[2,284]),o($VE,[2,285]),o($VF,[2,55]),o($VF,[2,56]),o($VF,[2,57]),o($VF,[2,75]),o($VF,[2,76]),o($Vd,[2,61]),o($VG,$VH,{66:158,71:$VI}),o($VG,$VH,{66:160,71:$VI}),o($Vd,[2,82],{75:161,113:163,139:165,111:167,7:$VJ,76:[1,162],116:$VK,117:$VL,127:[1,164],140:$Vo,141:$Vp,272:$Vi}),{4:$Vf,6:170,7:$Vg,97:[1,171]},{4:$Vf,6:172,7:$Vg,103:173,108:$VM,109:$VN},o($Vd,[2,116]),{4:$Vf,6:178,7:[1,177],106:176},{4:$Vf,6:179,7:$Vg,25:180,54:$Vj,55:$Vk,56:$Vl},{4:$Vf,6:181,7:$Vg,113:182,116:$VK,117:$VL},{4:$Vf,6:183,7:$Vg,76:[1,184]},o($VO,[2,145],{77:185,170:$VP}),o($Vd,[2,147],{124:187,247:$VQ}),{4:$Vf,6:189,7:$Vg,127:[2,158]},{127:[1,190]},o($VR,[2,169],{133:191,6:193,4:$Vf,7:[1,192]}),{4:$Vf,6:194,7:$Vg},{4:$Vf,6:195,7:$Vg,139:196,140:$Vo,141:$Vp},{4:$Vf,6:197,7:$Vg,134:[1,198]},{4:$Vf,6:199,7:$VS,65:201,69:$Vm,70:$Vn,75:200,111:167,272:$Vi},{4:$Vf,6:203,7:$VS,75:204,111:167,272:$Vi},{4:$Vf,6:205,7:$VS,75:206,111:167,272:$Vi},{4:$Vf,6:207,7:$Vg,132:[1,208],136:[1,209]},o($Vd,[2,218]),{4:$Vf,6:210,7:$Vg,143:[1,211]},{4:$Vf,6:212,7:$Vg,97:[1,213]},o($VT,$VU,{128:214,160:215,109:$VV,163:$VW}),{4:$Vf,6:218,7:$Vg},o($Vd,[2,250]),o($VX,[2,131]),o($VX,[2,132]),o($VY,[2,136]),o($VY,[2,137]),o($VO,[2,143]),o($VO,[2,144]),o($VO,[2,146]),o($VZ,[2,159]),o($VZ,[2,160]),o($V_,[2,185]),o($V$,[2,216]),o($V$,[2,217]),o($V01,[2,245]),o($V01,[2,246]),o($V_,[2,186]),o($V_,[2,187]),o($Vd,[2,80],{5:$Vu}),o($Vd,[2,81]),{1:[2,8]},o($Vd,[2,11]),o($Vd,[2,15]),o($Vd,[2,323],{218:219,219:220,108:[1,221]}),o($V11,[2,386],{6:222,4:$Vf,7:$Vg,40:$V21}),o($V11,[2,389],{6:224,4:$Vf,7:$Vg}),o($V31,[2,390]),o($V31,[2,396],{198:225,5:[1,226],107:$Vz,199:$VA,200:$VB}),o($V31,[2,403]),o($V41,$V51,{264:$V61}),{23:228,195:$V71},o($Vd,[2,24]),{195:[2,30]},{195:[2,31]},o($Vv,[2,3]),{4:$Vf,6:233,7:$V81,35:230,39:231,41:232},o($Vd,[2,35]),o($Vx,$V91),{5:$Va1,7:[1,235],8:237,272:[1,236]},o($Vb1,[2,305]),o($Vb1,$Vc1),o($Vb1,$Vd1),o($VC,[2,429]),{272:[1,239]},o($Ve1,[2,424]),o($Vd,[2,281],{7:[1,240]}),{7:[1,241]},{145:$Vf1,182:242},o($Vd,[2,273],{7:[1,244]}),{4:$Vf,6:245,7:$Vg,167:[1,246]},o($VD,[2,255]),o($Vd,[2,67],{6:247,67:248,4:$Vf,7:$Vg1,272:$Vh1}),{4:$Vf,6:251,7:$Vg,72:[1,252]},o($Vd,[2,71],{111:67,6:253,68:254,38:255,4:$Vf,7:$Vh,272:$Vi}),o($Vd,[2,83]),{77:256,170:$VP},o($Vd,[2,134]),o([12,13,76],$VU,{160:215,128:257,109:$VV,163:$VW}),o($V_,[2,184]),o($Vd,$Vi1,{198:145,107:$Vz,199:$VA,200:$VB}),o($Vj1,[2,130]),o($Vd,[2,138]),o($Vd,[2,139]),o($Vd,[2,103]),{4:$Vf,6:258,7:$VS,75:259,111:167,272:$Vi},o($Vd,[2,106],{67:260,7:$Vk1,272:$Vh1}),{4:$Vf,6:262,7:$Vg1,67:263,272:$Vh1},o($VG,[2,123]),o($VG,[2,124]),o($Vd,[2,117],{107:[1,264]}),o($Vl1,[2,118],{5:$Vu}),o($Vl1,[2,119]),o($Vd,[2,125],{111:167,75:265,7:$VJ,272:$Vi}),{4:$Vf,6:266,7:$VS,75:267,111:167,272:$Vi},o($Vd,[2,133]),o($Vd,[2,135]),o($Vd,[2,140]),{77:268,170:$VP},o($Vd,[2,142]),{171:[1,269]},o($Vd,[2,148]),{171:[1,270]},o($Vd,[2,149],{160:215,128:271,76:$VU,109:$VV,163:$VW}),o($Vm1,$VU,{160:215,128:272,109:$VV,163:$VW}),o($Vd,[2,161],{134:[1,273]}),o($VR,[2,170],{4:[1,274],5:$Vu}),o($VR,[2,171]),o($Vd,[2,168]),o($Vd,[2,173]),o($V_,[2,183]),o($Vd,[2,174],{67:275,7:$Vk1,272:$Vh1}),{4:$Vf,6:276,7:$Vg1,67:277,272:$Vh1},o($Vd,[2,188]),o($Vd,[2,189],{6:278,4:$Vf,7:$Vg,143:[1,279],144:[1,280]}),{4:$Vf,6:281,7:$Vg1,67:282,272:$Vh1},o($Vj1,$Vi1,{198:145,5:$Vu,107:$Vz,199:$VA,200:$VB}),o($Vd,[2,200]),{4:$Vf,6:284,7:$Vg,98:[1,283],144:[1,285]},o($Vd,[2,204]),{98:[1,286]},o($Vd,[2,206],{152:287,154:$Vn1,155:$Vo1}),{4:$Vf,6:290,7:$Vg,152:291,154:$Vn1,155:$Vo1},{4:$Vf,6:292,7:$Vg,153:[1,293]},o($VO,$Vp1,{157:294,158:295,12:$Vq1,13:$Vq1,108:$Vr1,109:$Vs1}),o($Vm1,$Vp1,{158:295,157:298,108:$Vr1,109:$Vs1}),o($Vd,[2,230]),{4:$Vf,6:299,7:$VS,75:300,111:167,272:$Vi},o($Vd,[2,238],{6:301,77:302,4:$Vf,7:$Vg,76:[1,303],170:$VP}),{4:$Vf,6:304,7:$Vg1,67:305,272:$Vh1},o($Vt1,[2,247]),o($Vt1,[2,248]),o($Vd,[2,249]),o($Vd,[2,322]),o($Vd,[2,324],{220:306,222:307,36:308,223:309,224:310,225:311,255:314,4:$Vu1,153:$Vv1,226:$Vw1,256:$Vx1,257:$Vy1,260:$Vz1,261:$VA1}),{4:$Vf,6:321,7:[1,323],38:255,68:325,111:67,221:320,267:322,268:324,269:326,270:327,272:$Vi},o($V11,[2,387]),{3:135,4:$V0,5:$V1,7:$Vs,253:134,263:328},o($V11,[2,388]),{5:$Va1,7:$VB1,8:329,253:333,262:[1,330],266:331},o($V31,[2,398]),{124:334,245:[1,335],247:$VQ,265:[1,336]},o($Vd,[2,23],{6:338,4:$Vf,7:$Vg,24:[1,337]}),{5:[1,340],196:[1,339]},o($Vd,[2,34],{36:341,4:[1,342],40:[1,343],226:$Vw1}),o($VC1,[2,40]),{4:[1,345],42:[1,344]},o($VC1,[2,44]),o([4,42],[2,45],{5:$Vu}),o($Ve1,[2,417],{5:$VD1}),{171:[1,347]},o($Ve1,[2,422]),o($VE1,[2,6]),o($Ve1,[2,425],{198:348,107:$Vz,199:$VA,200:$VB}),o($Vd,[2,280],{182:349,145:$Vf1}),{145:$Vf1,182:350},o($Vd,[2,283]),{7:$VF1,185:351,186:352,187:353},o([175,191,192,193,194],[2,272],{180:356,4:[1,355],12:$VG1,13:$VG1}),o($VD,[2,252]),{4:$Vf,6:357,7:$Vg,72:[1,358]},o($Vd,[2,68]),o($Vd,[2,64],{6:359,62:360,4:$Vf,7:$Vg,63:[1,361],64:[1,362]}),o($VH1,$VI1,{5:$Vu}),{171:[1,363]},o($VG,[2,78]),o($VG,[2,79]),o($Vd,[2,72]),o($Vd,[2,73],{4:[1,364]}),o($VJ1,[2,414]),o($Vd,[2,84]),o($Vd,[2,151],{76:[1,365]}),o($Vd,[2,104]),{98:[1,366]},o($Vd,[2,107]),o($Vd,$VI1),o($Vd,[2,108],{103:367,108:$VM,109:$VN}),o($Vd,[2,111],{6:368,103:369,4:$Vf,7:$Vg,108:$VM,109:$VN}),{4:$Vf,5:[1,372],6:371,7:[1,370]},o($Vd,[2,128]),o($Vd,[2,126]),o($Vd,[2,127]),o($Vd,[2,141]),{170:[1,373]},{247:[1,374]},{76:[1,375]},o($Vd,[2,150],{6:376,4:$Vf,7:$Vg,76:[1,377]}),{4:$Vf,6:379,7:$Vg1,25:381,54:$Vj,55:$Vk,56:$Vl,67:380,135:[1,378],272:$Vh1},o($VR,[2,172]),o($Vd,[2,176]),o($Vd,[2,175],{103:382,108:$VM,109:$VN}),o($Vd,[2,177],{6:383,103:384,4:$Vf,7:$Vg,108:$VM,109:$VN}),o($Vd,[2,190]),o($Vd,[2,191]),{145:[1,385]},o($Vd,[2,195]),o($Vd,[2,196]),{99:[1,386]},o($Vd,[2,202]),{7:$VK1,146:387,148:388},{99:[1,390]},{7:[1,391]},{7:[2,214]},{7:[2,215]},o($Vd,[2,208],{7:[1,392]}),{7:[1,393]},o($Vd,[2,211],{7:[1,394]}),{7:[1,395]},{4:$Vf,6:397,7:$Vg,76:[1,396]},{4:$Vf,6:399,7:$Vg1,67:398,272:$Vh1},o($Vt1,[2,236]),o($Vt1,[2,237]),o($Vd,[2,220],{6:400,4:$Vf,7:$Vg,76:[1,401]}),o($Vd,[2,231]),{98:[1,402]},o($Vd,[2,239]),o($Vd,[2,240]),{77:403,170:$VP},o($VT,[2,243]),o($VT,[2,244]),o($Vd,[2,325],{36:308,223:309,224:310,225:311,255:314,222:404,4:$Vu1,153:$Vv1,226:$Vw1,256:$Vx1,257:$Vy1,260:$Vz1,261:$VA1}),o($VL1,[2,329]),o($VL1,[2,331]),o($VL1,[2,332]),o($VL1,[2,333]),o($VL1,[2,334]),o($VL1,[2,335]),o($VM1,$VN1,{227:405,45:407,228:408,230:409,232:411,233:412,237:413,238:414,248:416,244:417,77:418,249:419,250:422,4:[1,406],145:$VO1,167:$VP1,170:$VP,245:$VQ1,246:$VR1}),{4:$Vf,6:424,7:$Vg,258:[1,423]},{4:$Vf,6:426,7:$Vg,258:[1,425]},{4:$Vf,6:428,7:$Vg,245:[1,427]},o($VS1,[2,377]),o($VS1,[2,378]),o($VS1,[2,379]),o($VL1,[2,327],{40:[1,429]}),o($VL1,[2,328]),o($VT1,[2,406],{282:$VU1}),o([4,12,13,40,153,226,256,257,260,261,282],$Vy,{198:145,271:431,277:433,5:$Vu,7:$VV1,107:$Vz,199:$VA,200:$VB,278:$VW1}),o($VJ1,[2,408]),o($VJ1,[2,409]),o($VJ1,[2,410]),o($VJ1,[2,411]),o($V31,[2,391]),o($V31,[2,397]),o($V31,[2,399]),o($V31,[2,400],{198:437,107:[1,436],199:$VA,200:[1,435]}),o($VX1,$V51,{5:$VD1,264:$V61}),o($VX1,[2,404]),{265:[1,438]},{265:[1,439]},o($V41,[2,395]),{4:$Vf,6:441,7:$Vg,25:440,54:$Vj,55:$Vk,56:$Vl},o($Vd,[2,22]),{5:[1,443],197:[1,442]},o($VY1,[2,304],{197:[1,444]}),o($Vd,[2,32]),o($Vd,[2,33]),{4:$Vf,6:233,7:$V81,39:445,41:232},o($VM1,$VN1,{228:408,230:409,232:411,233:412,237:413,238:414,248:416,244:417,77:418,249:419,250:422,43:446,44:447,45:448,145:$VO1,167:$VP1,170:$VP,245:$VQ1,246:$VR1}),o($VC1,[2,43]),o($VE1,[2,5]),{272:[1,449]},{5:[1,452],7:[1,450],272:[1,451]},o($Vd,[2,279]),{4:$Vf,6:454,7:$Vg,179:453,190:455,191:$VZ1,192:$V_1},{40:[1,459],147:[1,458]},o($V$1,[2,287]),o($V$1,[2,289]),{4:$Vf,6:461,7:$Vg,188:460,201:[1,462],202:[1,463],203:[1,464],204:[1,465],205:[1,466],206:[1,467],207:[1,468],208:[1,469],209:[1,470],210:[1,471],211:[1,472],212:[1,473],213:[1,474],214:[1,475]},o($Vd,[2,275]),{168:478,169:481,174:480,175:$V02,177:476,178:477,179:479,190:455,191:$VZ1,192:$V_1,193:$V12,194:$V22},o($VD,[2,253]),o($VD,[2,254]),o($Vd,[2,69]),o($Vd,[2,70]),o($Vd,[2,65]),o($Vd,[2,66]),{272:[1,485]},o($Vd,[2,74]),{129:[1,486]},{99:[1,487]},o($Vd,[2,109],{67:488,7:$Vk1,272:$Vh1}),o($Vd,[2,112],{67:489,7:$Vk1,272:$Vh1}),{4:$Vf,6:490,7:$Vg1,67:491,272:$Vh1},o($Vl1,[2,120],{5:$Vu}),o($Vl1,[2,121]),o($Vl1,[2,122]),o([4,7,12,13,40,42,134,144,147,153,226,229,231,235,239,240,241,242,243,256,257,260,261,282],[2,363]),o([12,13,265],[2,364]),{129:[1,492]},o($Vd,[2,152],{129:[1,493]}),{129:[1,494]},o($Vd,[2,162]),o($Vd,[2,163],{67:495,7:$Vk1,272:$Vh1}),o($Vd,[2,164]),{4:$Vf,6:496,7:$Vg1,67:497,272:$Vh1},{7:$Vk1,67:498,272:$Vh1},o($Vd,[2,178],{67:499,7:$Vk1,272:$Vh1}),{4:$Vf,6:500,7:$Vg1,67:501,272:$Vh1},{7:$VK1,146:502,148:388},{100:[1,503]},o($Vd,[2,203],{40:$V32}),o($V42,[2,197]),{42:[1,505]},{100:[1,506]},o($Vd,[2,207]),o($Vd,[2,209]),o($Vd,[2,210]),o($Vd,[2,212]),o($Vd,[2,213]),{77:507,170:$VP},{77:508,170:$VP},o($Vm1,[2,234]),o($Vm1,[2,235]),o($Vd,[2,221],{77:509,170:$VP}),{77:510,170:$VP},{99:[1,511]},o($Vd,[2,241]),o($VL1,[2,330]),o($VL1,[2,336]),o($VL1,[2,337]),o($VJ1,[2,338],{229:$V52}),o($V62,[2,339]),o($V62,[2,341],{231:[1,513]}),o($VM1,$VN1,{233:412,237:413,238:414,248:416,244:417,77:418,249:419,250:422,232:514,145:$VO1,170:$VP,245:$VQ1,246:$VR1}),o($V72,[2,345]),o($V72,[2,346],{234:515,42:[1,517],235:[1,516],239:[1,518],240:[1,519],241:[1,520],242:[1,521],243:[1,522]}),o($V82,[2,351]),o($V82,[2,352]),o($VM1,$VN1,{228:408,230:409,232:411,233:412,237:413,238:414,248:416,244:417,77:418,249:419,250:422,45:523,3:524,4:$V0,5:$V1,145:$VO1,167:$VP1,170:$VP,245:$VQ1,246:$VR1}),o($V82,[2,365]),o($V82,[2,366]),o($V82,[2,367]),o($V82,[2,368]),o($V82,[2,361]),{245:[1,525]},{7:$Vs,251:526,252:527,253:528,254:$V92},{3:135,4:$V0,5:$V1,7:$Vs,253:134,259:530,263:133},o($VL1,[2,381]),{3:135,4:$V0,5:$V1,7:$Vs,253:134,259:531,263:133},o($VL1,[2,383]),o($VL1,[2,384]),o($VL1,[2,385]),{7:$Va2,38:255,68:325,111:67,267:532,268:324,269:326,270:327,272:$Vi},{4:[1,535],7:$Va2,38:255,68:325,111:67,267:534,268:324,269:326,270:327,272:$Vi},o($VJ1,[2,412],{277:536,278:$VW1}),o($VJ1,$V91,{277:433,271:537,278:$VW1}),o($Vb2,[2,434]),{4:$Vf,6:539,7:$Vg,279:[1,538]},{5:[1,540],7:$Vc1},{5:[1,541],7:$Vd1},{7:$Vs,253:542},o($V41,[2,393]),o($V41,[2,394]),{7:[1,543]},o($Vd,[2,21]),o($VY1,[2,299]),o($VY1,[2,302],{196:[1,544],197:[1,545]}),o($VY1,[2,303]),o($VC1,[2,41]),o($VC1,[2,42]),o($VC1,[2,46]),o($VC1,[2,47],{229:$V52}),o($Ve1,[2,419]),o($Ve1,[2,418]),{171:[1,546],273:[1,547]},o($Ve1,[2,423]),o($Vd,[2,278]),o($Vd,[2,282]),{23:548,195:$V71},{195:[2,295]},{195:[2,296]},o([4,7,12,13,191,192],[2,286]),{7:$VF1,186:549,187:353},o($V$1,[2,290]),o($V$1,[2,291],{189:550,2:[2,293]}),o($V$1,[2,308]),o($V$1,[2,309]),o($V$1,[2,310]),o($V$1,[2,311]),o($V$1,[2,312]),o($V$1,[2,313]),o($V$1,[2,314]),o($V$1,[2,315]),o($V$1,[2,316]),o($V$1,[2,317]),o($V$1,[2,318]),o($V$1,[2,319]),o($V$1,[2,320]),o($V$1,[2,321]),{2:[1,551],4:[1,552]},o($Vw,[2,266],{190:455,168:478,179:479,174:480,169:481,178:553,175:$V02,191:$VZ1,192:$V_1,193:$V12,194:$V22}),o($Vc2,[2,269]),o($Vc2,[2,270]),o($Vc2,[2,271]),{170:[1,554]},{4:[1,556],176:[1,555]},{170:[2,297]},{170:[2,298]},o($VH1,[2,416]),o($Vd,[2,155]),{100:[1,557]},o($Vd,[2,110]),o($Vd,[2,113]),o($Vd,[2,114]),o($Vd,[2,115]),o($Vd,[2,154]),o($Vd,[2,156]),o($Vd,[2,153]),o($Vd,[2,167]),o($Vd,[2,165]),o($Vd,[2,166]),o($Vd,[2,181]),o($Vd,[2,179]),o($Vd,[2,180]),o($Vd,[2,182]),{40:$V32,147:[1,558]},{101:[1,559]},{7:$VK1,148:560},{77:561,170:$VP},{101:[1,562]},o($Vd,[2,223],{144:[1,563]}),o($Vd,[2,224]),{144:[1,564]},o($Vd,[2,222],{6:565,4:$Vf,7:$Vg,144:[1,566]}),{100:[1,567]},o($VM1,$VN1,{230:409,232:411,233:412,237:413,238:414,248:416,244:417,77:418,249:419,250:422,228:568,145:$VO1,167:$VP1,170:$VP,245:$VQ1,246:$VR1}),o($VM1,$VN1,{230:409,232:411,233:412,237:413,238:414,248:416,244:417,77:418,249:419,250:422,228:570,4:[1,569],145:$VO1,167:$VP1,170:$VP,245:$VQ1,246:$VR1}),o($V72,[2,344]),o($VM1,$VN1,{237:413,238:414,248:416,244:417,77:418,249:419,250:422,233:571,3:572,4:$V0,5:$V1,145:$VO1,170:$VP,245:$VQ1,246:$VR1}),{167:[1,574],236:[1,573]},o($Vd2,[2,353]),o($Vd2,[2,354]),o($Vd2,[2,355]),o($Vd2,[2,356]),o($Vd2,[2,357]),o($Vd2,[2,358]),{147:[1,575],229:$V52},o($V82,[2,360]),o($V82,[2,362]),o($V82,[2,369],{198:576,107:$Vz,199:$VA,200:$VB}),o($Ve2,[2,371]),o($Ve2,[2,374],{5:[1,577]}),{7:[1,578]},o($VL1,[2,380],{40:$V21}),o($VL1,[2,382],{40:$V21}),o($VT1,[2,407],{282:$VU1}),o($VJ1,$Vy,{198:145,271:431,277:433,7:$VV1,107:$Vz,199:$VA,200:$VB,278:$VW1}),{4:[1,580],134:[1,582],282:$VU1,283:579,284:581},o($VJ1,[2,446]),o($Vb2,[2,435]),o($VJ1,[2,413],{277:536,278:$VW1}),{4:$Vf,6:584,7:$Vg,274:583,275:[1,585],276:[1,586]},o($Vb2,[2,441]),o($V31,[2,401]),o($V31,[2,402]),o($VX1,[2,405]),o($Vd,[2,20]),{197:[1,587]},o($VY1,[2,301]),{272:[1,588]},o($Ve1,[2,421]),o([2,4,12,13,175,191,192,193,194],[2,294]),o($V$1,[2,288]),{2:[1,589]},o($Vd,[2,276]),o($Vd,[2,277]),o($Vw,[2,267],{190:455,168:478,179:479,174:480,169:481,178:590,175:$V02,191:$VZ1,192:$V_1,193:$V12,194:$V22}),o($Vc2,[2,256],{171:[1,591]}),o($Vc2,[2,264],{145:[1,592]}),o($Vc2,[2,265]),{101:[1,593]},o($Vd,[2,192],{6:594,4:$Vf,7:$Vg,143:[1,595]}),o($Vd,[2,201]),o($V42,[2,198]),o($V42,[2,199]),o($Vd,[2,205]),{7:$VK1,146:596,148:388},{7:$VK1,146:597,148:388},o($Vd,[2,225],{148:388,146:598,7:$VK1}),{7:$VK1,146:599,148:388},{101:[1,600]},o($V62,[2,340]),o($V62,[2,342]),o($V62,[2,343]),o($V72,[2,347]),o($V72,[2,348]),o($V72,[2,349]),{236:[1,601]},o($V82,[2,359]),{5:[1,602],7:$Vs,252:603,253:528,254:$V92},o($Ve2,[2,375]),{254:[1,604]},o($VJ1,[2,444]),o($VJ1,[2,445]),o($VJ1,[2,447]),o($VM1,$VN1,{45:407,228:408,230:409,232:411,233:412,237:413,238:414,248:416,244:417,77:418,249:419,250:422,227:605,145:$VO1,167:$VP1,170:$VP,245:$VQ1,246:$VR1}),{4:$Vf,6:608,7:[1,606],280:607,281:$Vf2},o($Vb2,[2,440]),{145:[1,610]},{145:[1,611]},o($VY1,[2,300]),o($Ve1,[2,420]),o($V$1,[2,292]),o($Vw,[2,268]),o($Vc2,[2,257],{170:[1,612]}),{7:$Vg2,170:$Vh2,172:613,173:614},o($Vd,[2,105]),o($Vd,[2,193]),o($Vd,[2,194]),o($Vd,[2,227],{40:$V32}),o($Vd,[2,228],{40:$V32}),o($Vd,[2,229],{40:$V32}),o($Vd,[2,226],{40:$V32}),o($Vd,[2,232]),o($V72,[2,350]),o($Ve2,[2,372]),o($Ve2,[2,373]),o($Ve2,[2,376]),o($VJ1,[2,448]),{4:$Vf,5:$Vu,6:618,7:$Vg,280:617,281:$Vf2},o($Vb2,[2,437]),o($Vb2,[2,439]),{7:[1,619],145:[1,620]},{5:$Va1,7:$VB1,8:622,253:333,266:621},{5:$Va1,7:$VB1,8:624,253:333,266:623},o($Vc2,[2,258]),{40:[1,626],147:[1,625]},o($V$1,[2,259]),{42:[1,627]},{171:[1,628]},o($Vb2,[2,436]),o($Vb2,[2,438]),o($Vb2,[2,442]),{7:[1,629]},{107:$Vz,147:[1,630],198:437,199:$VA,200:$VB},{2:[1,631]},{107:$Vz,147:[1,632],198:437,199:$VA,200:$VB},{2:[1,633]},o($Vc2,[2,263]),{7:$Vg2,170:$Vh2,173:634},{7:[1,635]},{170:[1,636]},{40:[1,637]},o($Vi2,[2,430]),o($Vi2,[2,431]),o($Vi2,[2,432]),o($Vi2,[2,433]),o($V$1,[2,260]),o($V$1,[2,261]),{42:[1,638]},{7:[1,639]},{170:[1,640]},{147:[1,641]},{171:[1,642]},o($Vb2,[2,443]),{170:[1,643]},o($V$1,[2,262])],
defaultActions: {53:[2,9],127:[2,8],139:[2,30],140:[2,31],288:[2,214],289:[2,215],456:[2,295],457:[2,296],483:[2,297],484:[2,298]},
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


var isHive = function () {
  return parser.yy.dialect === 'hive';
}

var isImpala = function () {
  return parser.yy.dialect === 'impala';
}


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
  if (isImpala()) {
    identifierChain = parser.expandImpalaIdentifierChain(tablePrimaries, identifierChain);
    suggestion.identifierChain = identifierChain;
  }

  // Expand exploded views in the identifier chain
  if (isHive()) {
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
      if (parser.yy.result.suggestIdentifiers.length === 0) {
        delete parser.yy.result.suggestIdentifiers;
      }
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

    var dbAndTable = false;
    if (foundTable.length === 0) {
      foundTable = tablePrimaries.filter(function (tablePrimary) {
        if (identifierChain[0].name === tablePrimary.identifierChain[0].name) {
          if (identifierChain.length > 1 && tablePrimary.identifierChain.length > 1) {
            dbAndTable = identifierChain[1].name === tablePrimary.identifierChain[1].name;
          }
          return true;
        }
        return false;
      })
    }

    if (foundTable.length === 1) {
      tablePrimaries = foundTable;
      identifierChain.shift();
      if (dbAndTable) {
        identifierChain.shift();
      }
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
  if (parser.yy.result.suggestIdentifiers.length === 0) {
    delete parser.yy.result.suggestIdentifiers;
  }
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
  if (dialect === 'generic') {
    dialect = undefined;
  }
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
    result = parser.parse(beforeCursor + (beforeCursor.length == 0 || /.*\s+$/.test(beforeCursor) ? ' \u2020 ' : '\u2021') + afterCursor);
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
case 5: return 281; 
break;
case 6: return 135; 
break;
case 7: return 213; 
break;
case 8: return 102; 
break;
case 9: return 193; 
break;
case 10: return 104; 
break;
case 11: return 105; 
break;
case 12: determineCase(yy_.yytext); return 52; 
break;
case 13: return 114; 
break;
case 14: return 28; 
break;
case 15: return 120; 
break;
case 16: return 214; 
break;
case 17: return 143; 
break;
case 18: return 183; 
break;
case 19: return 137; 
break;
case 20: return '<hive>FUNCTION'; 
break;
case 21: return 123; 
break;
case 22: return 132; 
break;
case 23: return 109; 
break;
case 24: return 140; 
break;
case 25: return 141; 
break;
case 26: this.begin('hdfs'); return 30; 
break;
case 27: return 278; 
break;
case 28: return 26; 
break;
case 29: this.begin('hdfs'); return 191; 
break;
case 30: return 142; 
break;
case 31: return '<hive>MACRO'; 
break;
case 32: return 144; 
break;
case 33: return 149; 
break;
case 34: return 154; 
break;
case 35: return 116; 
break;
case 36: return 121; 
break;
case 37: return 55; 
break;
case 38: return 161; 
break;
case 39: return 164; 
break;
case 40: return '<hive>TEMPORARY'; 
break;
case 41: return 165; 
break;
case 42: return 155; 
break;
case 43: return 275; 
break;
case 44: return 276; 
break;
case 45: return 107; 
break;
case 46: return 130; 
break;
case 47: return 131; 
break;
case 48: return 96; 
break;
case 49: return 194; 
break;
case 50: determineCase(yy_.yytext); return 53; 
break;
case 51: return 115; 
break;
case 52: return 29; 
break;
case 53: return 119; 
break;
case 54: return '<impala>FUNCTION'; 
break;
case 55: return 127; 
break;
case 56: return 136; 
break;
case 57: return 153; 
break;
case 58: return 184; 
break;
case 59: return '<impala>INCREMENTAL'; 
break;
case 60: this.begin('hdfs'); return 31; 
break;
case 61: return 163; 
break;
case 62: return 27; 
break;
case 63: this.begin('hdfs'); return 192; 
break;
case 64: return 150; 
break;
case 65: return 156; 
break;
case 66: return 117; 
break;
case 67: return 122; 
break;
case 68: return 97; 
break;
case 69: return 56; 
break;
case 70: return 162; 
break;
case 71: return 200; 
break;
case 72: return 231; 
break;
case 73: return 204; 
break;
case 74: return 205; 
break;
case 75: return 258; 
break;
case 76: return 210; 
break;
case 77: determineCase(yy_.yytext); return 51; 
break;
case 78: return 69; 
break;
case 79: return 209; 
break;
case 80: return 207; 
break;
case 81: determineCase(yy_.yytext); return 59; 
break;
case 82: return 72; 
break;
case 83: return 206; 
break;
case 84: return 108; 
break;
case 85: return 256; 
break;
case 86: return 71; 
break;
case 87: return 203; 
break;
case 88: return 24; 
break;
case 89: return 235; 
break;
case 90: return 282; 
break;
case 91: return 76; 
break;
case 92: return 167; 
break;
case 93: return 134; 
break;
case 94: return 229; 
break;
case 95: return 260; 
break;
case 96: return 'ROLE'; 
break;
case 97: return 70; 
break;
case 98: determineCase(yy_.yytext); return 215; 
break;
case 99: return 34; 
break;
case 100: determineCase(yy_.yytext); return 74; 
break;
case 101: return 202; 
break;
case 102: return 208; 
break;
case 103: return 54; 
break;
case 104: return 212; 
break;
case 105: return 201; 
break;
case 106: determineCase(yy_.yytext); return 32; 
break;
case 107: determineCase(yy_.yytext); return 73; 
break;
case 108: return 211; 
break;
case 109: return 279; 
break;
case 110: return 226; 
break;
case 111: return 245; 
break;
case 112: return 7; 
break;
case 113: parser.yy.cursorFound = true; return 4; 
break;
case 114: parser.yy.cursorFound = true; return 5; 
break;
case 115: return 195; 
break;
case 116: return 196; 
break;
case 117: this.popState(); return 197; 
break;
case 118: return 13; 
break;
case 119: return yy_.yytext; 
break;
case 120: return yy_.yytext; 
break;
case 121: return 264; 
break;
case 122: return 265; 
break;
case 123: this.begin('backtickedValue'); return 272; 
break;
case 124: if (yy_.yytext.indexOf('\u2020') !== -1 || yy_.yytext.indexOf('\u2021') !== -1) {
                                        this.popState();
                                        return 273;
                                      }
                                      return 171;
                                    
break;
case 125: this.popState(); return 272; 
break;
case 126: this.begin('singleQuotedValue'); return 170; 
break;
case 127: return 171; 
break;
case 128: this.popState(); return 170; 
break;
case 129: this.begin('doubleQuotedValue'); return 247; 
break;
case 130: return 171; 
break;
case 131: this.popState(); return 247; 
break;
case 132: return 13; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:AS\b)/i,/^(?:ALL\b)/i,/^(?:BINARY\b)/i,/^(?:COLUMNS\b)/i,/^(?:COMMENT\b)/i,/^(?:COMPACTIONS\b)/i,/^(?:CONF\b)/i,/^(?:CREATE\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DATE\b)/i,/^(?:EXTENDED\b)/i,/^(?:EXTERNAL\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:IN\b)/i,/^(?:INDEX\b)/i,/^(?:INDEXES\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:LOCKS\b)/i,/^(?:MACRO\b)/i,/^(?:PARTITION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:TBLPROPERTIES\b)/i,/^(?:TEMPORARY\b)/i,/^(?:TRANSACTIONS\b)/i,/^(?:USER\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:AGGREGATE\b)/i,/^(?:ANALYTIC\b)/i,/^(?:COLUMN\b)/i,/^(?:COMMENT\b)/i,/^(?:CREATE\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:GROUP\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INCREMENTAL\b)/i,/^(?:INPATH\b)/i,/^(?:IN\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:STATS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:[.])/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DATABASE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:DROP\b)/i,/^(?:EXISTS\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:IF\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:LIKE\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:ROLE\b)/i,/^(?:SCHEMA\b)/i,/^(?:SELECT\b)/i,/^(?:SET\b)/i,/^(?:SHOW\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:\s+['])/i,/^(?:[^'\u2020\u2021]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>]+)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:[^"]+)/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[113,114,115,116,117,118],"inclusive":false},"doubleQuotedValue":{"rules":[130,131],"inclusive":false},"singleQuotedValue":{"rules":[127,128],"inclusive":false},"backtickedValue":{"rules":[124,125],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,119,120,121,122,123,126,129,132],"inclusive":true},"impala":{"rules":[0,1,2,3,4,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,119,120,121,122,123,126,129,132],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,119,120,121,122,123,126,129,132],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});