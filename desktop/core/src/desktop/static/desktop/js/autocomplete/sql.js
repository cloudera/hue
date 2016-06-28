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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,8],$V1=[1,19],$V2=[1,50],$V3=[1,51],$V4=[1,52],$V5=[1,18],$V6=[1,55],$V7=[1,56],$V8=[1,53],$V9=[1,54],$Va=[1,25],$Vb=[1,17],$Vc=[1,28],$Vd=[1,49],$Ve=[1,47],$Vf=[6,7],$Vg=[6,7,12,29,35,42,43,44,45,46,47,110,111,112,144,159,210,214,216,219,231,232,248,251],$Vh=[1,65],$Vi=[1,66],$Vj=[1,68],$Vk=[1,69],$Vl=[1,70],$Vm=[1,71],$Vn=[1,72],$Vo=[1,118],$Vp=[1,119],$Vq=[1,129],$Vr=[1,132],$Vs=[12,29,38,39,40,49,50,71,72],$Vt=[12,29,136],$Vu=[12,29,63,64],$Vv=[1,148],$Vw=[6,7,12],$Vx=[1,155],$Vy=[2,6,7,12,29,33,35,36,38,39,40,53,54,77,91,94,95,100,105,110,111,112,136,144,159,210,231,232,244,248,251,253,282,283],$Vz=[38,39,40],$VA=[6,7,12,29,128,136],$VB=[6,7,12,29,115,128,136],$VC=[6,7,12,29,136],$VD=[2,105],$VE=[1,157],$VF=[1,164],$VG=[1,166],$VH=[1,167],$VI=[1,172],$VJ=[1,173],$VK=[12,29,253],$VL=[1,184],$VM=[1,186],$VN=[6,7,251],$VO=[1,198],$VP=[6,7,12,29,105,253],$VQ=[2,113],$VR=[1,212],$VS=[1,213],$VT=[12,29,38,39,40],$VU=[12,29,94,95],$VV=[12,29,282],$VW=[6,7,12,29,251],$VX=[12,29,284,287],$VY=[6,7,12,29,36,77,105,253],$VZ=[12,29,79,80],$V_=[6,7,29,296],$V$=[2,166],$V01=[1,225],$V11=[1,226],$V21=[1,227],$V31=[6,7,29,110,111,112,144,210,231,232,248,251,296],$V41=[1,235],$V51=[1,236],$V61=[6,7,35],$V71=[1,247],$V81=[6,7,12,29,35,110,111,112,144,210,231,232],$V91=[6,7,12,13,29,31,32,33,35,42,43,44,45,46,47,110,111,112,144,159,210,214,216,219,231,232,248,251],$Va1=[2,151],$Vb1=[1,252],$Vc1=[1,253],$Vd1=[1,257],$Ve1=[1,263],$Vf1=[1,264],$Vg1=[2,149],$Vh1=[6,7,12,29,115,274,289],$Vi1=[1,275],$Vj1=[2,29],$Vk1=[6,7,33],$Vl1=[6,7,12,29,253],$Vm1=[1,302],$Vn1=[1,303],$Vo1=[2,100],$Vp1=[2,450],$Vq1=[1,310],$Vr1=[1,311],$Vs1=[1,319],$Vt1=[1,323],$Vu1=[1,328],$Vv1=[2,167],$Vw1=[1,332],$Vx1=[12,13,136,228,233],$Vy1=[2,27],$Vz1=[2,28],$VA1=[6,7,12,29,110,111,112,115,144,210,231,232,248,251,274,289,296],$VB1=[6,7,31,32,33],$VC1=[2,142],$VD1=[2,155],$VE1=[1,339],$VF1=[1,349],$VG1=[1,354],$VH1=[1,355],$VI1=[1,356],$VJ1=[1,350],$VK1=[1,352],$VL1=[1,353],$VM1=[1,369],$VN1=[1,374],$VO1=[1,375],$VP1=[88,89,102,108],$VQ1=[1,381],$VR1=[2,193],$VS1=[6,7,29,110,111,112,144,210,231,232,248,251],$VT1=[1,415],$VU1=[6,7,29,144,210],$VV1=[1,438],$VW1=[2,6,7,12,29,35,110,111,112,115,144,210,231,232,248,251,274,289,296],$VX1=[6,7,12,29,31,32,33,105,253],$VY1=[6,7,29,110,111,112,210,231,232],$VZ1=[12,228],$V_1=[2,293],$V$1=[1,468],$V02=[1,469],$V12=[1,458],$V22=[1,463],$V32=[12,29,229],$V42=[6,7,29,110,111,112,144,210,231,232],$V52=[1,478],$V62=[1,480],$V72=[1,482],$V82=[6,7,12,29,31,32,33,35,110,111,112,144,159,210,231,232],$V92=[1,491],$Va2=[1,492],$Vb2=[144,159],$Vc2=[1,518],$Vd2=[1,519],$Ve2=[1,517],$Vf2=[1,538],$Vg2=[6,7,144,159],$Vh2=[2,6,7,12,29,56,57,85,86,156,197],$Vi2=[1,562],$Vj2=[6,7,29,110,111,112,144,159,210,214,231,232,248,251],$Vk2=[6,7,29,110,111,112,144,159,210,214,216,231,232,248,251],$Vl2=[6,7,29,42,43,44,45,46,47,110,111,112,144,159,210,214,216,219,231,232,248,251],$Vm2=[1,579],$Vn2=[1,583],$Vo2=[6,7,29,110,111,112,144,210,231,232,244,248,251],$Vp2=[2,29,56,57,85,86,156],$Vq2=[12,13,29,102,103,105,158,228],$Vr2=[6,7,29,31,32,33,42,43,44,45,46,47,110,111,112,144,159,210,214,216,219,231,232,248,251],$Vs2=[1,659],$Vt2=[1,665],$Vu2=[1,666],$Vv2=[12,29,247];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"InitResults":3,"Sql":4,"SqlStatements":5,";":6,"EOF":7,"SqlStatement":8,"DataDefinition":9,"DataManipulation":10,"SelectStatement":11,"REGULAR_IDENTIFIER":12,"PARTIAL_CURSOR":13,"AnyCursor":14,"CreateStatement":15,"DescribeStatement":16,"DropStatement":17,"ShowStatement":18,"UseStatement":19,"LoadStatement":20,"UpdateStatement":21,"AggregateOrAnalytic":22,"<impala>AGGREGATE":23,"<impala>ANALYTIC":24,"AnyCreate":25,"CREATE":26,"<hive>CREATE":27,"<impala>CREATE":28,"CURSOR":29,"AnyDot":30,".":31,"<impala>.":32,"<hive>.":33,"AnyFromOrIn":34,"FROM":35,"<hive>IN":36,"AnyTable":37,"TABLE":38,"<hive>TABLE":39,"<impala>TABLE":40,"ComparisonOperators":41,"=":42,"<>":43,"<=":44,">=":45,"<":46,">":47,"DatabaseOrSchema":48,"DATABASE":49,"SCHEMA":50,"FromOrIn":51,"HiveIndexOrIndexes":52,"<hive>INDEX":53,"<hive>INDEXES":54,"HiveOrImpalaComment":55,"<hive>COMMENT":56,"<impala>COMMENT":57,"HiveOrImpalaCreate":58,"HiveOrImpalaCurrent":59,"<hive>CURRENT":60,"<impala>CURRENT":61,"HiveOrImpalaData":62,"<hive>DATA":63,"<impala>DATA":64,"HiveOrImpalaDatabasesOrSchemas":65,"<hive>DATABASES":66,"<hive>SCHEMAS":67,"<impala>DATABASES":68,"<impala>SCHEMAS":69,"HiveOrImpalaExternal":70,"<hive>EXTERNAL":71,"<impala>EXTERNAL":72,"HiveOrImpalaLoad":73,"<hive>LOAD":74,"<impala>LOAD":75,"HiveOrImpalaIn":76,"<impala>IN":77,"HiveOrImpalaInpath":78,"<hive>INPATH":79,"<impala>INPATH":80,"HiveOrImpalaLeftSquareBracket":81,"<hive>[":82,"<impala>[":83,"HiveOrImpalaLocation":84,"<hive>LOCATION":85,"<impala>LOCATION":86,"HiveOrImpalaRightSquareBracket":87,"<hive>]":88,"<impala>]":89,"HiveOrImpalaRole":90,"<hive>ROLE":91,"<impala>ROLE":92,"HiveOrImpalaRoles":93,"<hive>ROLES":94,"<impala>ROLES":95,"HiveOrImpalaTables":96,"<hive>TABLES":97,"<impala>TABLES":98,"HiveRoleOrUser":99,"<hive>USER":100,"SignedInteger":101,"UNSIGNED_INTEGER":102,"-":103,"SingleQuotedValue":104,"SINGLE_QUOTE":105,"VALUE":106,"DoubleQuotedValue":107,"DOUBLE_QUOTE":108,"AnyGroup":109,"GROUP":110,"<hive>GROUP":111,"<impala>GROUP":112,"OptionalAggregateOrAnalytic":113,"OptionalExtended":114,"<hive>EXTENDED":115,"OptionalExtendedOrFormatted":116,"<hive>FORMATTED":117,"OptionalFormatted":118,"<impala>FORMATTED":119,"OptionallyFormattedIndex":120,"PartialIdentifierOrCursor":121,"OptionalFromDatabase":122,"DatabaseIdentifier":123,"OptionalHiveCascadeOrRestrict":124,"<hive>CASCADE":125,"<hive>RESTRICT":126,"OptionalIfExists":127,"IF":128,"EXISTS":129,"OptionalIfNotExists":130,"NOT":131,"OptionalInDatabase":132,"ConfigurationName":133,"PartialIdentifierOrPartialCursor":134,"PartialRegularOrBacktickedIdentifier":135,"BACKTICK":136,"PARTIAL_VALUE":137,"SchemaQualifiedTableIdentifier":138,"RegularOrBacktickedIdentifier":139,"ImprovedDerivedColumnChain":140,"OptionalMapOrArrayKey":141,"PartitionSpecList":142,"PartitionSpec":143,",":144,"CleanRegularOrBackTickedSchemaQualifiedName":145,"RegularOrBackTickedSchemaQualifiedName":146,"ColumnIdentifier":147,"LocalOrSchemaQualifiedName":148,"DerivedColumnChain":149,"TableDefinition":150,"DatabaseDefinition":151,"Comment":152,"HivePropertyAssignmentList":153,"HivePropertyAssignment":154,"HiveDbProperties":155,"<hive>WITH":156,"DBPROPERTIES":157,"(":158,")":159,"DatabaseDefinitionOptionals":160,"DatabaseDefinitionOptional":161,"HdfsLocation":162,"CleanUpDatabaseConditions":163,"TableScope":164,"TableElementList":165,"TableElements":166,"TableElement":167,"ColumnDefinition":168,"PrimitiveType":169,"ColumnDefinitionError":170,"TINYINT":171,"SMALLINT":172,"INT":173,"BIGINT":174,"BOOLEAN":175,"FLOAT":176,"DOUBLE":177,"STRING":178,"DECIMAL":179,"CHAR":180,"VARCHAR":181,"TIMESTAMP":182,"<hive>BINARY":183,"<hive>DATE":184,"HdfsPath":185,"HDFS_START_QUOTE":186,"HDFS_PATH":187,"HDFS_END_QUOTE":188,"HiveDescribeStatement":189,"ImpalaDescribeStatement":190,"<hive>DESCRIBE":191,"<impala>DESCRIBE":192,"DROP":193,"DropDatabaseStatement":194,"DropTableStatement":195,"TablePrimary":196,"INTO":197,"SELECT":198,"CleanUpSelectConditions":199,"SelectList":200,"TableExpression":201,"FromClause":202,"SelectConditionList":203,"TableReferenceList":204,"SelectCondition":205,"WhereClause":206,"GroupByClause":207,"OrderByClause":208,"LimitClause":209,"WHERE":210,"SearchCondition":211,"BooleanValueExpression":212,"BooleanTerm":213,"OR":214,"BooleanFactor":215,"AND":216,"BooleanTest":217,"Predicate":218,"IS":219,"TruthValue":220,"ParenthesizedBooleanValueExpression":221,"NonParenthesizedValueExpressionPrimary":222,"ColumnReference":223,"BasicIdentifierChain":224,"InitIdentifierChain":225,"IdentifierChain":226,"Identifier":227,"\"":228,"BY":229,"ColumnList":230,"ORDER":231,"LIMIT":232,"*":233,"DerivedColumn":234,"TableReference":235,"TablePrimaryOrJoinedTable":236,"LateralViewDefinition":237,"JoinedTable":238,"LateralViews":239,"userDefinedTableGeneratingFunction":240,"<hive>explode":241,"<hive>posexplode":242,"LateralView":243,"<hive>LATERAL":244,"VIEW":245,"LateralViewColumnAliases":246,"<hive>AS":247,"JOIN":248,"JoinSpecification":249,"JoinCondition":250,"ON":251,"SHOW":252,"LIKE":253,"ShowColumnStatement":254,"ShowColumnsStatement":255,"ShowCompactionsStatement":256,"ShowConfStatement":257,"ShowCreateTableStatement":258,"ShowCurrentStatement":259,"ShowDatabasesStatement":260,"ShowFunctionsStatement":261,"ShowGrantStatement":262,"ShowIndexStatement":263,"ShowLocksStatement":264,"ShowPartitionsStatement":265,"ShowRoleStatement":266,"ShowRolesStatement":267,"ShowTableStatement":268,"ShowTablesStatement":269,"ShowTblPropertiesStatement":270,"ShowTransactionsStatement":271,"<impala>COLUMN":272,"<impala>STATS":273,"if":274,"partial":275,"identifierChain":276,"length":277,"<hive>COLUMNS":278,"<hive>COMPACTIONS":279,"<hive>CONF":280,"<hive>FUNCTIONS":281,"<impala>FUNCTIONS":282,"SingleQuoteValue":283,"<hive>GRANT":284,"OptionalPrincipalName":285,"<hive>ALL":286,"<impala>GRANT":287,"<hive>LOCKS":288,"<hive>PARTITION":289,"<hive>PARTITIONS":290,"<impala>PARTITIONS":291,"<hive>TBLPROPERTIES":292,"<hive>TRANSACTIONS":293,"UPDATE":294,"TargetTable":295,"SET":296,"SetClauseList":297,"TableName":298,"SetClause":299,"SetTarget":300,"UpdateSource":301,"ValueExpression":302,"USE":303,"$accept":0,"$end":1},
terminals_: {2:"error",6:";",7:"EOF",12:"REGULAR_IDENTIFIER",13:"PARTIAL_CURSOR",23:"<impala>AGGREGATE",24:"<impala>ANALYTIC",26:"CREATE",27:"<hive>CREATE",28:"<impala>CREATE",29:"CURSOR",31:".",32:"<impala>.",33:"<hive>.",35:"FROM",36:"<hive>IN",38:"TABLE",39:"<hive>TABLE",40:"<impala>TABLE",42:"=",43:"<>",44:"<=",45:">=",46:"<",47:">",49:"DATABASE",50:"SCHEMA",53:"<hive>INDEX",54:"<hive>INDEXES",56:"<hive>COMMENT",57:"<impala>COMMENT",60:"<hive>CURRENT",61:"<impala>CURRENT",63:"<hive>DATA",64:"<impala>DATA",66:"<hive>DATABASES",67:"<hive>SCHEMAS",68:"<impala>DATABASES",69:"<impala>SCHEMAS",71:"<hive>EXTERNAL",72:"<impala>EXTERNAL",74:"<hive>LOAD",75:"<impala>LOAD",77:"<impala>IN",79:"<hive>INPATH",80:"<impala>INPATH",82:"<hive>[",83:"<impala>[",85:"<hive>LOCATION",86:"<impala>LOCATION",88:"<hive>]",89:"<impala>]",91:"<hive>ROLE",92:"<impala>ROLE",94:"<hive>ROLES",95:"<impala>ROLES",97:"<hive>TABLES",98:"<impala>TABLES",100:"<hive>USER",102:"UNSIGNED_INTEGER",103:"-",105:"SINGLE_QUOTE",106:"VALUE",108:"DOUBLE_QUOTE",110:"GROUP",111:"<hive>GROUP",112:"<impala>GROUP",115:"<hive>EXTENDED",117:"<hive>FORMATTED",119:"<impala>FORMATTED",125:"<hive>CASCADE",126:"<hive>RESTRICT",128:"IF",129:"EXISTS",131:"NOT",136:"BACKTICK",137:"PARTIAL_VALUE",144:",",156:"<hive>WITH",157:"DBPROPERTIES",158:"(",159:")",171:"TINYINT",172:"SMALLINT",173:"INT",174:"BIGINT",175:"BOOLEAN",176:"FLOAT",177:"DOUBLE",178:"STRING",179:"DECIMAL",180:"CHAR",181:"VARCHAR",182:"TIMESTAMP",183:"<hive>BINARY",184:"<hive>DATE",186:"HDFS_START_QUOTE",187:"HDFS_PATH",188:"HDFS_END_QUOTE",191:"<hive>DESCRIBE",192:"<impala>DESCRIBE",193:"DROP",197:"INTO",198:"SELECT",210:"WHERE",214:"OR",216:"AND",219:"IS",220:"TruthValue",228:"\"",229:"BY",231:"ORDER",232:"LIMIT",233:"*",241:"<hive>explode",242:"<hive>posexplode",244:"<hive>LATERAL",245:"VIEW",247:"<hive>AS",248:"JOIN",251:"ON",252:"SHOW",253:"LIKE",272:"<impala>COLUMN",273:"<impala>STATS",274:"if",275:"partial",276:"identifierChain",277:"length",278:"<hive>COLUMNS",279:"<hive>COMPACTIONS",280:"<hive>CONF",281:"<hive>FUNCTIONS",282:"<impala>FUNCTIONS",283:"SingleQuoteValue",284:"<hive>GRANT",286:"<hive>ALL",287:"<impala>GRANT",288:"<hive>LOCKS",289:"<hive>PARTITION",290:"<hive>PARTITIONS",291:"<impala>PARTITIONS",292:"<hive>TBLPROPERTIES",293:"<hive>TRANSACTIONS",294:"UPDATE",296:"SET",303:"USE"},
productions_: [0,[3,0],[4,4],[4,3],[5,1],[5,3],[8,1],[8,1],[8,1],[8,3],[8,2],[8,1],[9,1],[9,1],[9,1],[9,1],[9,1],[10,1],[10,1],[22,1],[22,1],[25,1],[25,1],[25,1],[14,1],[14,1],[30,1],[30,1],[30,1],[34,1],[34,1],[37,1],[37,1],[37,1],[41,1],[41,1],[41,1],[41,1],[41,1],[41,1],[48,1],[48,1],[51,1],[51,1],[52,1],[52,1],[55,1],[55,1],[58,1],[58,1],[59,1],[59,1],[62,1],[62,1],[65,1],[65,1],[65,1],[65,1],[70,1],[70,1],[73,1],[73,1],[76,1],[76,1],[78,1],[78,1],[81,1],[81,1],[84,1],[84,1],[87,1],[87,1],[90,1],[90,1],[93,1],[93,1],[96,1],[96,1],[99,1],[99,1],[101,1],[101,2],[104,3],[107,3],[109,1],[109,1],[109,1],[113,0],[113,1],[114,0],[114,1],[116,0],[116,1],[116,1],[118,0],[118,1],[120,2],[120,2],[120,2],[120,1],[122,0],[122,2],[124,0],[124,1],[124,1],[127,0],[127,2],[127,2],[130,0],[130,1],[130,2],[130,3],[130,3],[132,0],[132,2],[133,1],[133,1],[133,3],[133,3],[133,3],[121,2],[121,1],[134,2],[134,1],[135,2],[135,2],[138,1],[138,1],[138,1],[138,3],[138,3],[138,3],[138,3],[123,1],[123,1],[123,1],[140,1],[140,1],[140,2],[140,3],[140,3],[140,4],[141,0],[141,3],[141,3],[141,2],[142,1],[142,3],[143,3],[145,1],[145,1],[147,1],[147,4],[147,4],[147,3],[139,1],[139,3],[146,3],[146,5],[146,5],[146,7],[146,6],[146,3],[146,5],[146,2],[146,3],[148,1],[148,2],[148,1],[148,2],[149,1],[149,3],[15,1],[15,1],[15,2],[152,2],[152,3],[152,4],[153,1],[153,3],[154,3],[154,7],[155,5],[155,2],[155,2],[160,1],[160,2],[160,3],[161,1],[161,1],[161,1],[163,0],[151,3],[151,4],[151,5],[151,7],[151,7],[150,6],[150,5],[150,4],[150,3],[150,6],[150,4],[164,1],[165,3],[166,1],[166,3],[167,1],[168,2],[168,2],[168,4],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[169,1],[170,0],[162,2],[185,3],[185,5],[185,4],[185,3],[185,3],[185,2],[16,1],[16,1],[189,3],[189,4],[190,3],[17,2],[17,1],[17,1],[194,3],[194,4],[194,5],[194,5],[195,3],[195,4],[195,4],[195,5],[20,7],[20,6],[20,5],[20,4],[20,3],[20,2],[11,4],[11,3],[201,1],[201,2],[199,0],[202,2],[202,2],[203,1],[203,2],[205,1],[205,1],[205,1],[205,1],[205,1],[206,2],[206,2],[211,1],[212,1],[212,3],[213,1],[213,3],[213,3],[215,2],[215,1],[217,1],[217,3],[217,3],[217,3],[217,4],[218,1],[218,1],[221,3],[221,2],[222,1],[222,1],[222,1],[223,1],[224,2],[225,0],[226,1],[226,3],[226,3],[227,1],[227,2],[227,3],[207,3],[207,2],[208,3],[208,2],[209,2],[209,2],[200,1],[200,2],[200,2],[200,1],[230,1],[230,3],[234,1],[234,3],[234,2],[234,3],[234,3],[234,5],[234,5],[234,1],[204,1],[204,3],[235,1],[236,1],[236,1],[236,1],[237,2],[237,3],[196,1],[240,4],[240,4],[240,4],[240,4],[239,1],[239,2],[243,5],[243,4],[243,5],[243,4],[243,3],[243,2],[246,2],[246,6],[238,4],[238,4],[238,3],[249,1],[250,2],[18,2],[18,3],[18,4],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[254,3],[254,4],[254,8],[255,3],[255,4],[255,4],[255,5],[255,6],[255,4],[255,5],[255,6],[255,6],[255,6],[256,2],[257,3],[258,3],[258,4],[258,4],[258,4],[259,3],[259,3],[259,3],[260,3],[260,4],[260,3],[261,2],[261,3],[261,3],[261,4],[261,4],[261,5],[261,6],[261,6],[261,6],[261,6],[262,3],[262,5],[262,5],[262,5],[262,6],[262,6],[262,6],[262,3],[285,0],[285,1],[285,1],[285,2],[263,2],[263,3],[263,4],[263,4],[263,4],[263,5],[263,6],[263,6],[263,6],[263,6],[264,3],[264,3],[264,4],[264,4],[264,7],[264,8],[264,8],[264,4],[264,4],[265,3],[265,7],[265,4],[265,5],[265,3],[265,7],[266,3],[266,5],[266,4],[266,5],[266,5],[266,4],[266,5],[266,5],[267,2],[268,3],[268,4],[268,5],[268,6],[268,6],[268,6],[268,7],[268,8],[268,8],[268,8],[268,8],[268,3],[268,4],[268,8],[269,3],[269,4],[269,4],[269,5],[270,3],[271,2],[21,5],[21,5],[21,4],[21,3],[21,2],[21,2],[295,1],[298,1],[297,1],[297,3],[299,3],[299,2],[299,1],[300,1],[301,1],[302,1],[19,2],[19,2]],
performAction: function anonymous(yytext, yyleng, yylineno, yy, yystate /* action[1] */, $$ /* vstack */, _$ /* lstack */) {
/* this == yyval */

var $0 = $$.length - 1;
switch (yystate) {
case 1:

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
case 2: case 3:

     prioritizeSuggestions();
     return parser.yy.result;
   
break;
case 10: case 11:

     suggestDdlAndDmlKeywords();
   
break;
case 83:

     this.$ = $$[$0-1];
   
break;
case 97:

     suggestKeywords(['INDEX', 'INDEXES']);
   
break;
case 98:

     suggestKeywords(['FORMATTED']);
   
break;
case 106: case 111:

     suggestKeywords(['EXISTS']);
   
break;
case 109:

     suggestKeywords(['IF NOT EXISTS']);
   
break;
case 110:

     suggestKeywords(['NOT EXISTS']);
   
break;
case 126: case 127:

     suggestTables();
     suggestDatabases({ appendDot: true });
     this.$ = { cursorOrPartialIdentifier: true }
   
break;
case 129:

     suggestDatabases();
     this.$ = { table: $$[$0-2] }
   
break;
case 130: case 131:

     suggestTables({ database: $$[$0-2] });
     this.$ = { database: $$[$0-2] }
   
break;
case 132:

     this.$ = { database: $$[$0-2], table: $$[$0] }
     addTablePrimary()
   
break;
case 133: case 134:

     this.$ = { cursorOrPartialIdentifier: true }
     suggestDatabases();
   
break;
case 136: case 137:

     this.$ = { identifierChain: [], partial: true };
   
break;
case 138:

     if (typeof $$[$0].key !== 'undefined') {
       this.$ = { identifierChain: [{ name: $$[$0-1], key: $$[$0].key }], partial: false };
     } else {
       this.$ = { identifierChain: [{ name: $$[$0-1] }], partial: false };
     }
   
break;
case 139: case 140:

     this.$ = { identifierChain: $$[$0-2].identifierChain, partial: true };
   
break;
case 141:

     if (typeof $$[$0].key !== 'undefined') {
       this.$ = { identifierChain: $$[$0-3].identifierChain.concat({ name: $$[$0-1], key: $$[$0].key }), partial: false };
     } else {
       this.$ = { identifierChain: $$[$0-3].identifierChain.concat({ name: $$[$0-1] }), partial: false };
     }
   
break;
case 142:
 this.$ = {} 
break;
case 143:

     this.$ = { key: '"' + $$[$0-1] + '"' }
   
break;
case 144:

     this.$ = { key: $$[$0-1] }
   
break;
case 145:

     this.$ = { key: null }
   
break;
case 149: case 166:

     this.$ = { identifierChain: [ { name: $$[$0] } ] }
   
break;
case 150: case 285: case 288: case 291:

     this.$ = $$[$0];
   
break;
case 151:

     this.$ = { name: $$[$0] }
   
break;
case 152:

     this.$ = { name: $$[$0-3], key: '"' + $$[$0-1] + '"' }
   
break;
case 153:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 154:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 156:

     this.$ = $$[$0-2];
   
break;
case 157:

     this.$ = { identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] }
   
break;
case 158:

     this.$ = { identifierChain: [ { name: $$[$0-3] }, { name: $$[$0] } ] }
   
break;
case 159:

     this.$ = { identifierChain: [ { name: $$[$0-4] }, { name: $$[$0-1] } ] }
   
break;
case 160:

     this.$ = { identifierChain: [ { name: $$[$0-5] }, { name: $$[$0-1] } ] }
   
break;
case 161:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-4] } ] };
   
break;
case 162:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-2] } ] };
   
break;
case 163:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-3] } ] };
   
break;
case 164:

     this.$ = { partial: true, identifierChain: [ ] };
   
break;
case 165:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ] }
   
break;
case 167:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] };
   
break;
case 169:

     this.$ = { identifierChain: $$[$0-1].identifierChain, alias: $$[$0] }
   
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
case 174:

     if (isHive() || isImpala()) {
       suggestKeywords(['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
   
break;
case 184:

     suggestKeywords(['DBPROPERTIES']);
   
break;
case 188:

     parser.yy.afterComment = true;
   
break;
case 189:

     parser.yy.afterHdfsLocation = true;
   
break;
case 190:

     parser.yy.afterHiveDbProperties = true;
   
break;
case 191:

     delete parser.yy.afterComment;
     delete parser.yy.afterHdfsLocation;
     delete parser.yy.afterHiveDbProperties;
   
break;
case 194:

     if (isHive()) {
       suggestKeywords(['COMMENT', 'LOCATION', 'WITH DBPROPERTIES']);
     } else if (isImpala()) {
       suggestKeywords(['COMMENT', 'LOCATION']);
     }
   
break;
case 196:

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
case 198: case 199: case 200:

      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    
break;
case 201:

     if (isHive() || isImpala()) {
       suggestKeywords(['LOCATION']);
     }
   
break;
case 209: case 225:

     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   
break;
case 228:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 229:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 230:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 231:

     suggestHdfs({ path: '' });
   
break;
case 232:

      suggestHdfs({ path: '' });
    
break;
case 235:

      if ($$[$0].partial && $$[$0].identifierChain.length > 0) {
        var table =  $$[$0].identifierChain.shift().name;
        suggestColumns({
          table: table,
          identifierChain: $$[$0].identifierChain
        });
      } else if ($$[$0].partial) {
        if (!$$[$0-1]) {
          suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'SCHEMA']);
        }
        suggestTables();
      }
    
break;
case 236:

     if ($$[$0].cursorOrPartialIdentifier && !$$[$0-1]) {
       suggestKeywords(['EXTENDED']);
     }
   
break;
case 237:

      if ($$[$0].cursorOrPartialIdentifier && !$$[$0-1]) {
        suggestKeywords(['FORMATTED']);
      }
    
break;
case 238:

     if (isHive()) {
       suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'MACRO', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
     } else {
       suggestKeywords(['ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   
break;
case 242:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   
break;
case 243:

     if (isHive()) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   
break;
case 246:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 247:

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
case 248:

     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   
break;
case 250:

     suggestKeywords([ 'TABLE' ]);
   
break;
case 251:

     suggestKeywords([ 'INTO' ]);
   
break;
case 253:

     suggestKeywords([ 'INPATH' ]);
   
break;
case 254:

     suggestKeywords([ 'DATA' ]);
   
break;
case 255: case 470: case 472:

     linkTablePrimaries();
   
break;
case 259:

     delete parser.yy.afterGroupBy;
     delete parser.yy.afterLimit;
     delete parser.yy.afterOrderBy;
     delete parser.yy.afterWhere;
   
break;
case 261: case 475:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 264:

     parser.yy.afterWhere = true;
   
break;
case 265:

     parser.yy.afterGroupBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 266:

     parser.yy.afterOrderBy = true;
     delete parser.yy.result.suggestStar;
   
break;
case 267:

     parser.yy.afterLimit = true;
     delete parser.yy.result.suggestStar;
   
break;
case 268:

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
case 270: case 298: case 482:

     suggestColumns();
   
break;
case 275:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 281:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 287:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 292:

     this.$ = parser.yy.identifierChain;
     delete parser.yy.identifierChain;
   
break;
case 293:

     parser.yy.identifierChain = [];
   
break;
case 295:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 297:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 299:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 301: case 303:

     suggestKeywords(['BY']);
   
break;
case 305:

     suggestNumbers([1, 5, 10]);
   
break;
case 307: case 308:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 313:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 314:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 316:

      delete parser.yy.derivedColumnChain;
   
break;
case 317: case 318:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 319:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 323:

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
case 324:

     addTablePrimary($$[$0]);
   
break;
case 326:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], lateralViews: $$[$0] }
   
break;
case 327:

     this.$ = { identifierChain: [ { name: $$[$0-2] } ], alias: $$[$0-1], lateralViews: $$[$0] };
   
break;
case 329:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 331:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 333:

     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 334:

     parser.yy.currentViews.push($$[$0]);
     this.$ = parser.yy.currentViews;
   
break;
case 335:

     this.$ = { udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }
   
break;
case 336:

      this.$ = { udtf: $$[$0-1], columnAliases: $$[$0] }
    
break;
case 337: case 338:

     suggestKeywords(['AS']);
   
break;
case 339:

     suggestKeywords(['explode', 'posexplode']);
   
break;
case 340:

     suggestKeywords(['VIEW']);
   
break;
case 341:

     this.$ = [ $$[$0] ]
   
break;
case 342:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 344: case 417: case 419:

     suggestKeywords(['ON']);
   
break;
case 345:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
case 348:

     if (isHive()) {
       suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
     } else {
       suggestKeywords(['COLUMNS', 'DATABASES', 'TABLES']);
     }
   
break;
case 349:

     if (isImpala()) {
       suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'PARTITIONS', 'TABLE STATS']);
     }
   
break;
case 350:

     if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'DATABASES', 'FUNCTIONS', 'SCHEMAS', 'TABLES']);
     } else if (isHive()) {
       suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
     }
   
break;
case 369: case 461:

     suggestKeywords(['STATS']);
   
break;
case 370: case 385: case 435: case 439: case 462:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 371: case 463:

     suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
   
break;
case 372: case 373: case 378: case 379: case 421: case 422:

     suggestKeywords(['FROM', 'IN']);
   
break;
case 374: case 375: case 376: case 408: case 418: case 468:

     suggestTables();
   
break;
case 380: case 423: case 433: case 487:

     suggestDatabases();
   
break;
case 384: case 387: case 410:

     suggestKeywords(['TABLE']);
   
break;
case 386:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name);
     }
   
break;
case 388:

     suggestKeywords([ 'ROLES' ]);
   
break;
case 389:

     suggestKeywords([ 'CURRENT' ]);
   
break;
case 391: case 459:

     suggestKeywords(['LIKE']);
   
break;
case 396: case 401:

     suggestKeywords(['FUNCTIONS']);
   
break;
case 398: case 402:

     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   
break;
case 399: case 465:

     if (!$$[$0-1]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 403:

     if (!$$[$0-2]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 404:

     if ($$[$0]) {
       suggestKeywords(['ON']);
     }
   
break;
case 406:

     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   
break;
case 411:

     suggestKeywords(['ROLE']);
   
break;
case 414: case 415:

     this.$ = true;
   
break;
case 424:

     suggestTablesOrColumns($$[$0]);
   
break;
case 426:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
     suggestKeywords(['DATABASE', 'SCHEMA']);
   
break;
case 427:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name)
     }
   
break;
case 428:

      suggestKeywords(['EXTENDED', 'PARTITION']);
    
break;
case 429:

     if ($$[$0-1].partial && $$[$0-1].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-1].identifierChain[0].name)
     }
   
break;
case 430:

     if ($$[$0-4].partial && $$[$0-4].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
     }
   
break;
case 431: case 450: case 458:

     suggestKeywords(['EXTENDED']);
   
break;
case 432:

     // TODO: Move into CleanRegularOrBackTickedSchemaQualifiedName
     if ($$[$0-5].partial && $$[$0-5].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
     }
   
break;
case 436: case 440:

     suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
   
break;
case 437: case 460:

     suggestKeywords(['PARTITION']);
   
break;
case 441: case 442:

     suggestKeywords(['GRANT']);
   
break;
case 443: case 444:

     suggestKeywords(['ROLE', 'USER']);
   
break;
case 446: case 447:

     suggestKeywords(['GROUP']);
   
break;
case 452:

      if ($$[$0-1]) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    
break;
case 456:

      suggestKeywords(['PARTITION']);
    
break;
case 471:

     suggestKeywords([ 'WHERE' ]);
   
break;
case 473:

     suggestKeywords([ 'SET' ]);
   
break;
case 477:

     // TODO: Replace with TablePrimary?
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 481:

     suggestKeywords([ '=' ]);
   
break;
case 486:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
}
},
table: [o([12,13,26,27,28,29,74,75,191,192,193,198,252,294,303],[2,1],{4:1,3:2}),{1:[3]},{5:3,8:4,9:5,10:6,11:7,12:$V0,13:$V1,14:9,15:10,16:11,17:12,18:13,19:14,20:15,21:16,25:22,26:$V2,27:$V3,28:$V4,29:$V5,73:48,74:$V6,75:$V7,150:20,151:21,189:23,190:24,191:$V8,192:$V9,193:$Va,194:26,195:27,198:$Vb,252:$Vc,254:29,255:30,256:31,257:32,258:33,259:34,260:35,261:36,262:37,263:38,264:39,265:40,266:41,267:42,268:43,269:44,270:45,271:46,294:$Vd,303:$Ve},{6:[1,57],7:[1,58]},o($Vf,[2,4]),o($Vf,[2,6]),o($Vf,[2,7]),o($Vf,[2,8]),{13:[1,59]},o($Vf,[2,11]),o($Vf,[2,12]),o($Vf,[2,13]),o($Vf,[2,14]),o($Vf,[2,15]),o($Vf,[2,16]),o($Vf,[2,17]),o($Vf,[2,18]),o([12,13,29,233],[2,259],{199:60}),o($Vg,[2,24]),o($Vg,[2,25]),o($Vf,[2,172]),o($Vf,[2,173]),{12:$Vh,29:$Vi,37:63,38:$Vj,39:$Vk,40:$Vl,48:64,49:$Vm,50:$Vn,70:67,71:[1,73],72:[1,74],121:61,164:62},o($Vf,[2,233]),o($Vf,[2,234]),{12:$Vh,29:$Vi,37:77,38:$Vj,39:$Vk,40:$Vl,48:76,49:$Vm,50:$Vn,121:75},o($Vf,[2,239]),o($Vf,[2,240]),{12:$Vh,22:88,23:[1,110],24:[1,111],27:[1,103],28:[1,104],29:$Vi,39:[1,98],40:[1,99],52:113,53:$Vo,54:$Vp,58:83,59:84,60:[1,105],61:[1,106],65:85,66:[1,107],67:[1,108],68:[1,86],69:[1,109],90:96,91:[1,114],92:[1,115],95:[1,97],96:100,97:[1,116],98:[1,117],113:89,117:[1,112],120:92,121:78,272:[1,79],278:[1,80],279:[1,81],280:[1,82],281:[1,87],282:[2,87],284:[1,90],287:[1,91],288:[1,93],290:[1,94],291:[1,95],292:[1,101],293:[1,102]},o($Vf,[2,351]),o($Vf,[2,352]),o($Vf,[2,353]),o($Vf,[2,354]),o($Vf,[2,355]),o($Vf,[2,356]),o($Vf,[2,357]),o($Vf,[2,358]),o($Vf,[2,359]),o($Vf,[2,360]),o($Vf,[2,361]),o($Vf,[2,362]),o($Vf,[2,363]),o($Vf,[2,364]),o($Vf,[2,365]),o($Vf,[2,366]),o($Vf,[2,367]),o($Vf,[2,368]),{12:[1,120],29:$Vi,121:121},{12:$Vh,29:$Vi,62:122,63:[1,124],64:[1,125],121:123},{12:$Vq,29:$Vi,121:127,136:$Vr,146:131,148:130,295:126,298:128},o($Vs,[2,21]),o($Vs,[2,22]),o($Vs,[2,23]),o($Vt,[2,91],{116:133,48:134,49:$Vm,50:$Vn,115:[1,135],117:[1,136]}),o($Vt,[2,94],{118:137,119:[1,138]}),o($Vu,[2,60]),o($Vu,[2,61]),{7:[1,139],8:140,9:5,10:6,11:7,12:$V0,13:$V1,14:9,15:10,16:11,17:12,18:13,19:14,20:15,21:16,25:22,26:$V2,27:$V3,28:$V4,29:$V5,73:48,74:$V6,75:$V7,150:20,151:21,189:23,190:24,191:$V8,192:$V9,193:$Va,194:26,195:27,198:$Vb,252:$Vc,254:29,255:30,256:31,257:32,258:33,259:34,260:35,261:36,262:37,263:38,264:39,265:40,266:41,267:42,268:43,269:44,270:45,271:46,294:$Vd,303:$Ve},{1:[2,3]},o($Vf,[2,10],{12:[1,141]}),{12:$Vv,13:$V1,14:147,29:$V5,147:146,200:142,230:143,233:[1,144],234:145},o($Vf,[2,174],{37:149,38:$Vj,39:$Vk,40:$Vl}),{37:150,38:$Vj,39:$Vk,40:$Vl},{12:[1,151]},o($Vw,[2,108],{130:152,29:[1,153],128:[1,154]}),{13:$Vx},o($Vy,[2,121]),o($Vz,[2,203]),o($VA,[2,31]),o($VA,[2,32]),o($VA,[2,33]),o($VB,[2,40]),o($VB,[2,41]),o($Vz,[2,58]),o($Vz,[2,59]),o($Vf,[2,238]),o($VC,$VD,{127:156,128:$VE}),o($VC,$VD,{127:158,128:$VE}),o($Vf,[2,348],{145:159,93:161,52:163,146:165,12:$VF,53:$Vo,54:$Vp,94:$VG,95:$VH,136:$Vr,253:[1,160],282:[1,162]}),{12:$Vh,29:$Vi,121:168,273:[1,169]},{12:$Vh,29:$Vi,34:171,35:$VI,36:$VJ,121:170},o($Vf,[2,382]),{12:[1,175],29:$Vi,121:176,133:174},{12:$Vh,29:$Vi,37:178,38:$Vj,39:$Vk,40:$Vl,121:177},{12:$Vh,29:$Vi,93:180,94:$VG,95:$VH,121:179},{12:$Vh,29:$Vi,121:181,253:[1,182]},o($VK,[2,56],{104:183,105:$VL}),o($Vf,[2,394],{107:185,108:$VM}),{12:$Vh,29:$Vi,121:187,282:[2,88]},{282:[1,188]},o($VN,[2,412],{285:189,121:191,12:[1,190],29:$Vi}),{12:$Vh,29:$Vi,121:192},o($Vf,[2,416],{121:193,12:$Vh,29:$Vi,251:[1,194]}),{12:$VO,29:$Vi,48:197,49:$Vm,50:$Vn,121:195,136:$Vr,145:196,146:165},{12:$VO,29:$Vi,121:199,136:$Vr,145:200,146:165},{12:$VO,29:$Vi,121:201,136:$Vr,145:202,146:165},{12:$Vh,29:$Vi,121:203,284:[1,204],287:[1,205]},o($Vf,[2,449]),{12:$Vh,29:$Vi,115:[1,207],121:206},{12:$Vh,29:$Vi,121:208,273:[1,209]},o($VP,$VQ,{132:210,76:211,36:$VR,77:$VS}),{12:$Vh,29:$Vi,121:214},o($Vf,[2,469]),o($VT,[2,48]),o($VT,[2,49]),o($VU,[2,50]),o($VU,[2,51]),o($VK,[2,54]),o($VK,[2,55]),o($VK,[2,57]),o($VV,[2,19]),o($VV,[2,20]),{12:$Vh,29:$Vi,52:215,53:$Vo,54:$Vp,121:216},o($VW,[2,99]),o($VX,[2,72]),o($VX,[2,73]),o($VY,[2,76]),o($VY,[2,77]),o($VW,[2,44]),o($VW,[2,45]),o($Vf,[2,486],{13:$Vx}),o($Vf,[2,487]),{12:$Vh,29:$Vi,78:217,79:[1,219],80:[1,220],121:218},o($Vf,[2,254]),o($VZ,[2,52]),o($VZ,[2,53]),o($Vf,[2,474],{29:[1,222],296:[1,221]}),o($Vf,[2,475]),o($V_,[2,476]),o($V_,$V$,{30:224,12:[1,223],13:$Vx,31:$V01,32:$V11,33:$V21}),o($V_,[2,477]),o($V31,[2,168],{12:[1,228]}),{106:[1,229],137:[1,230]},{12:$V41,29:[1,232],135:233,136:$V51,139:234,140:231},o($Vt,[2,89],{114:237,115:[1,238]}),o($Vt,[2,92]),o($Vt,[2,93]),{12:$V41,29:[1,240],135:241,136:$V51,138:239,139:242},o($Vt,[2,95]),{1:[2,2]},o($Vf,[2,5]),o($Vf,[2,9]),o($Vf,[2,256],{201:243,202:244,35:[1,245]}),o($V61,[2,306],{121:246,12:$Vh,29:$Vi,144:$V71}),o($V61,[2,309],{121:248,12:$Vh,29:$Vi}),o($V81,[2,310]),o($V81,[2,312],{30:249,13:[1,250],31:$V01,32:$V11,33:$V21}),o($V81,[2,319]),o($V91,$Va1,{81:251,82:$Vb1,83:$Vc1}),o($Vf,[2,200],{12:[1,254]}),{12:[1,255]},{158:$Vd1,165:256},o($Vf,[2,192],{12:[1,258]}),o($Vw,[2,109]),{12:$Vh,29:$Vi,121:259,131:[1,260]},o($Vy,[2,120]),o($Vf,[2,241],{121:261,139:262,12:$Ve1,29:$Vi,136:$Vf1}),{12:$Vh,29:$Vi,121:265,129:[1,266]},o($Vf,[2,245],{146:131,121:267,196:268,148:269,12:$Vq,29:$Vi,136:$Vr}),o($Vf,[2,349]),{104:270,105:$VL},o($Vf,[2,389]),o([6,7,253],$VQ,{76:211,132:271,36:$VR,77:$VS}),o($VW,[2,98]),o($Vf,$Vg1,{30:224,31:$V01,32:$V11,33:$V21}),o($Vh1,[2,150]),o($Vf,[2,74]),o($Vf,[2,75]),o($Vf,[2,369]),{12:$VO,29:$Vi,121:272,136:$Vr,145:273,146:165},o($Vf,[2,372],{139:274,12:$Vi1,136:$Vf1}),{12:$Ve1,29:$Vi,121:276,136:$Vf1,139:277},o($VC,$Vj1),o($VC,[2,30]),o($Vf,[2,383],{33:[1,278]}),o($Vk1,[2,115],{13:$Vx}),o($Vk1,[2,116]),o($Vf,[2,384],{146:165,145:279,12:$VF,136:$Vr}),{12:$VO,29:$Vi,121:280,136:$Vr,145:281,146:165},o($Vf,[2,388]),o($Vf,[2,390]),o($Vf,[2,391]),{104:282,105:$VL},o($Vf,[2,393]),{106:[1,283]},o($Vf,[2,395]),{106:[1,284]},o($Vf,[2,396],{76:211,132:285,36:$VR,77:$VS,253:$VQ}),o($Vl1,$VQ,{76:211,132:286,36:$VR,77:$VS}),o($Vf,[2,404],{251:[1,287]}),o($VN,[2,413],{13:$Vx,29:[1,288]}),o($VN,[2,414]),o($Vf,[2,411]),o($Vf,[2,417],{139:289,12:$Vi1,136:$Vf1}),{12:$Ve1,29:$Vi,121:290,136:$Vf1,139:291},o($Vf,[2,426]),o($Vf,[2,427],{121:292,12:$Vh,29:$Vi,115:[1,293],289:[1,294]}),{12:$Ve1,29:$Vi,121:295,136:$Vf1,139:296},o($Vh1,$Vg1,{30:224,13:$Vx,31:$V01,32:$V11,33:$V21}),o($Vf,[2,435]),{12:$Vh,29:$Vi,121:298,274:[1,297],289:[1,299]},o($Vf,[2,439]),{274:[1,300]},o($Vf,[2,441],{99:301,91:$Vm1,100:$Vn1}),{12:$Vh,29:$Vi,91:$Vm1,99:305,100:$Vn1,121:304},{12:$Vh,29:$Vi,112:[1,307],121:306},o($VK,$Vo1,{122:308,51:309,6:$Vp1,7:$Vp1,35:$Vq1,36:$Vr1}),o($Vl1,$Vo1,{51:309,122:312,35:$Vq1,36:$Vr1}),o($Vf,[2,461]),{12:$VO,29:$Vi,121:313,136:$Vr,145:314,146:165},o($Vf,[2,464],{121:315,104:316,12:$Vh,29:$Vi,105:$VL,253:[1,317]}),{12:$V41,29:$Vs1,123:318,135:320,136:$V51,139:321},o($Vt,[2,62]),o($Vt,[2,63]),o($Vf,[2,468]),o($VW,[2,96]),o($VW,[2,97]),{185:322,186:$Vt1},o($Vf,[2,253]),{186:[2,64]},{186:[2,65]},{12:$Vu1,29:$Vi,121:327,297:324,299:325,300:326},o($Vf,[2,473]),o($V_,$Vv1),{12:[1,329],13:$Vw1,134:331,136:[1,330]},o($Vx1,[2,26]),o($Vx1,$Vy1),o($Vx1,$Vz1),o($V31,[2,169]),{136:[1,333]},o($VA1,[2,164]),o($Vf,[2,235],{30:334,31:$V01,32:$V11,33:$V21}),o($VB1,[2,136]),o($VB1,[2,137]),o($VB1,$VC1,{141:335,81:336,82:$Vb1,83:$Vc1}),o([6,7,12,29,31,32,33,82,83,105,253],$VD1,{13:[1,337]}),{106:$VE1,137:[1,338]},{12:$V41,29:$Vs1,123:340,135:320,136:$V51,139:321},o($Vt,[2,90]),o($Vf,[2,237]),o($Vf,[2,126]),o($Vf,[2,127],{30:341,31:$V01,32:$V11,33:$V21}),o($Vf,[2,128],{30:342,31:$V01,32:$V11,33:$V21}),o($Vf,[2,255]),o($Vf,[2,257],{203:343,205:344,206:345,207:346,208:347,209:348,109:351,29:$VF1,110:$VG1,111:$VH1,112:$VI1,210:$VJ1,231:$VK1,232:$VL1}),{12:[1,360],29:$Vi,121:358,136:$Vr,146:131,148:269,196:362,204:357,235:359,236:361,237:363,238:364},o($V61,[2,307]),{12:$Vv,13:$V1,14:147,29:$V5,147:146,234:365},o($V61,[2,308]),{12:$VM1,13:$Vw1,134:366,147:370,149:368,233:[1,367]},o($V81,[2,314]),{87:373,88:$VN1,89:$VO1,102:[1,372],107:371,108:$VM},o($VP1,[2,66]),o($VP1,[2,67]),o($Vf,[2,199],{165:376,158:$Vd1}),{158:$Vd1,165:377},o($Vf,[2,202]),{12:$VQ1,166:378,167:379,168:380},o([56,57,85,86,156],[2,191],{163:383,6:$VR1,7:$VR1,29:[1,382]}),o($Vw,[2,110]),{12:$Vh,29:$Vi,121:384,129:[1,385]},o($Vf,[2,242]),o($Vf,[2,102],{121:386,124:387,12:$Vh,29:$Vi,125:[1,388],126:[1,389]}),o([6,7,12,29,35,36,125,126],$VD1,{13:$Vx}),{106:$VE1},o($VC,[2,106]),o($VC,[2,107]),o($Vf,[2,246]),o($Vf,[2,247],{29:[1,390]}),o($VS1,[2,328]),o($Vf,[2,350]),o($Vf,[2,398],{253:[1,391]}),o($Vf,[2,370]),{274:[1,392]},o($Vf,[2,373]),o($Vf,$VD1),o($Vf,[2,374],{34:393,35:$VI,36:$VJ}),o($Vf,[2,377],{121:394,34:395,12:$Vh,29:$Vi,35:$VI,36:$VJ}),{12:[1,396],13:[1,398],29:$Vi,121:397},o($Vf,[2,387]),o($Vf,[2,385]),o($Vf,[2,386]),o($Vf,[2,392]),{105:[1,399]},{108:[1,400]},{253:[1,401]},o($Vf,[2,397],{121:402,12:$Vh,29:$Vi,253:[1,403]}),{12:$Ve1,29:$Vi,37:407,38:$Vj,39:$Vk,40:$Vl,121:405,136:$Vf1,139:406,286:[1,404]},o($VN,[2,415]),o($Vf,[2,419]),o($Vf,[2,418],{34:408,35:$VI,36:$VJ}),o($Vf,[2,420],{121:409,34:410,12:$Vh,29:$Vi,35:$VI,36:$VJ}),o($Vf,[2,428]),o($Vf,[2,429]),{158:[1,411]},o($Vf,[2,433]),o($Vf,[2,434]),{275:[1,412]},o($Vf,[2,437]),{12:$VT1,142:413,143:414},{275:[1,416]},{12:[1,417]},{12:[2,78]},{12:[2,79]},o($Vf,[2,443],{12:[1,418]}),{12:[1,419]},o($Vf,[2,446],{12:[1,420]}),{12:[1,421]},{12:$Vh,29:$Vi,121:423,253:[1,422]},{12:$V41,29:$Vs1,123:424,135:320,136:$V51,139:321},o($Vt,[2,42]),o($Vt,[2,43]),o($Vf,[2,451],{121:425,12:$Vh,29:$Vi,253:[1,426]}),o($Vf,[2,462]),{274:[1,427]},o($Vf,[2,465]),o($Vf,[2,466]),{104:428,105:$VL},o($VP,[2,114]),o($VP,[2,133]),o($VP,[2,134]),o($VP,[2,135]),o($Vf,[2,252],{121:430,12:$Vh,29:$Vi,197:[1,429]}),{13:[1,432],187:[1,431]},o($Vf,[2,472],{206:433,29:[1,434],144:[1,435],210:$VJ1}),o($VU1,[2,478]),{29:[1,437],42:[1,436]},o($VU1,[2,482]),o([29,42],[2,483],{13:$Vx}),o($VA1,[2,157],{13:$VV1}),{106:[1,439]},o($VA1,[2,162]),o($VW1,[2,123]),o($VA1,[2,165],{30:440,31:$V01,32:$V11,33:$V21}),{12:$V41,13:[1,441],135:442,136:$V51,139:443},o($VB1,[2,138]),{87:446,88:$VN1,89:$VO1,102:[1,445],107:444,108:$VM},o($VX1,[2,124]),o($VX1,[2,125]),{136:[1,447]},o($Vf,[2,236]),{12:$Vi1,136:$Vf1,139:448},{12:$V41,13:[1,449],135:450,136:$V51,139:451},o($Vf,[2,258],{206:345,207:346,208:347,209:348,109:351,205:452,29:$VF1,110:$VG1,111:$VH1,112:$VI1,210:$VJ1,231:$VK1,232:$VL1}),o($VY1,[2,262]),o($VY1,[2,264]),o($VY1,[2,265]),o($VY1,[2,266]),o($VY1,[2,267]),o($VY1,[2,268]),o($VZ1,$V_1,{211:453,212:455,213:456,215:457,217:459,218:460,221:461,222:462,223:464,101:465,104:466,224:467,225:470,29:[1,454],102:$V$1,103:$V02,105:$VL,131:$V12,158:$V22}),{12:$Vh,29:$Vi,121:472,229:[1,471]},{12:$Vh,29:$Vi,121:474,229:[1,473]},{12:$Vh,29:$Vi,102:[1,475],121:476},o($V32,[2,84]),o($V32,[2,85]),o($V32,[2,86]),o($VY1,[2,260],{144:[1,477]}),o($VY1,[2,261]),o($V42,[2,320],{248:$V52}),o([6,7,29,110,111,112,144,210,231,232,248],$V$,{30:224,239:479,243:481,12:$V62,13:$Vx,31:$V01,32:$V11,33:$V21,244:$V72}),o($VS1,[2,322]),o($VS1,[2,323]),o($VS1,[2,324]),o($VS1,[2,325]),o($V81,[2,311]),o($V81,[2,313]),o($V81,[2,315]),o($V81,[2,316],{30:485,31:$V01,32:[1,483],33:[1,484]}),o($V82,$Va1,{81:251,13:$VV1,82:$Vb1,83:$Vc1}),o($V82,[2,170]),{87:486,88:$VN1,89:$VO1},{87:487,88:$VN1,89:$VO1},o($V91,[2,154]),o($V91,[2,70]),o($V91,[2,71]),o($Vf,[2,198]),{12:$Vh,29:$Vi,84:490,85:$V92,86:$Va2,121:489,162:488},{144:[1,494],159:[1,493]},o($Vb2,[2,205]),o($Vb2,[2,207]),{12:$Vh,29:$Vi,121:496,169:495,171:[1,497],172:[1,498],173:[1,499],174:[1,500],175:[1,501],176:[1,502],177:[1,503],178:[1,504],179:[1,505],180:[1,506],181:[1,507],182:[1,508],183:[1,509],184:[1,510]},o($Vf,[2,194]),{55:516,56:$Vc2,57:$Vd2,84:490,85:$V92,86:$Va2,152:513,155:515,156:$Ve2,160:511,161:512,162:514},o($Vw,[2,111]),o($Vw,[2,112]),o($Vf,[2,243]),o($Vf,[2,244]),o($Vf,[2,103]),o($Vf,[2,104]),o($Vf,[2,248]),{283:[1,520]},{275:[1,521]},o($Vf,[2,375],{139:522,12:$Vi1,136:$Vf1}),o($Vf,[2,378],{139:523,12:$Vi1,136:$Vf1}),{12:$Ve1,29:$Vi,121:524,136:$Vf1,139:525},o($Vk1,[2,117],{13:$Vx}),o($Vk1,[2,118]),o($Vk1,[2,119]),o([6,7,12,29,42,43,44,45,46,47,110,111,112,144,159,210,214,216,219,231,232,248,251,289],[2,82]),o([6,7,88,89],[2,83]),{283:[1,526]},o($Vf,[2,399],{283:[1,527]}),{283:[1,528]},o($Vf,[2,405]),o($Vf,[2,406],{139:529,12:$Vi1,136:$Vf1}),o($Vf,[2,407]),{12:$Ve1,29:$Vi,121:530,136:$Vf1,139:531},{12:$Vi1,136:$Vf1,139:532},o($Vf,[2,421],{139:533,12:$Vi1,136:$Vf1}),{12:$Ve1,29:$Vi,121:534,136:$Vf1,139:535},{12:$VT1,142:536,143:414},{276:[1,537]},o($Vf,[2,438],{144:$Vf2}),o($Vg2,[2,146]),{42:[1,539]},{276:[1,540]},o($Vf,[2,442]),o($Vf,[2,444]),o($Vf,[2,445]),o($Vf,[2,447]),o($Vf,[2,448]),{104:541,105:$VL},{104:542,105:$VL},o($Vl1,[2,101]),o($Vf,[2,452],{104:543,105:$VL}),{104:544,105:$VL},{275:[1,545]},o($Vf,[2,467]),{12:$Vh,29:$Vi,37:546,38:$Vj,39:$Vk,40:$Vl,121:547},o($Vf,[2,251]),{13:[1,549],188:[1,548]},o($Vh2,[2,232],{188:[1,550]}),o($Vf,[2,470]),o($Vf,[2,471]),{12:$Vu1,29:$Vi,121:327,299:551,300:326},o($VZ1,$V_1,{213:456,215:457,217:459,218:460,221:461,222:462,223:464,101:465,104:466,224:467,225:470,301:552,302:553,212:554,102:$V$1,103:$V02,105:$VL,131:$V12,158:$V22}),o($VU1,[2,481]),o($VW1,[2,122]),{136:[1,555]},{12:[1,556],13:[1,558],136:[1,557]},o($VB1,[2,139]),o($VB1,[2,140]),o($VB1,$VC1,{81:336,141:559,82:$Vb1,83:$Vc1}),{87:560,88:$VN1,89:$VO1},{87:561,88:$VN1,89:$VO1},o($VB1,[2,145]),o([6,7,12,29,31,32,33,35,36,82,83,105,125,126,253],[2,156]),o($Vf,[2,129]),o($Vf,[2,130]),o($Vf,[2,131]),o($Vf,[2,132]),o($VY1,[2,263]),o($VY1,[2,269]),o($VY1,[2,270]),o($VS1,[2,271],{214:$Vi2}),o($Vj2,[2,272]),o($Vj2,[2,274],{216:[1,563]}),o($VZ1,$V_1,{218:460,221:461,222:462,223:464,101:465,104:466,224:467,225:470,217:564,102:$V$1,103:$V02,105:$VL,158:$V22}),o($Vk2,[2,278]),o($Vk2,[2,279],{41:565,42:[1,567],43:[1,568],44:[1,569],45:[1,570],46:[1,571],47:[1,572],219:[1,566]}),o($Vl2,[2,284]),o($Vl2,[2,285]),o($VZ1,$V_1,{213:456,215:457,217:459,218:460,221:461,222:462,223:464,101:465,104:466,224:467,225:470,212:573,14:574,13:$V1,29:$V5,102:$V$1,103:$V02,105:$VL,131:$V12,158:$V22}),o($Vl2,[2,288]),o($Vl2,[2,289]),o($Vl2,[2,290]),o($Vl2,[2,291]),o($Vl2,[2,80]),{102:[1,575]},{12:$Vv,147:578,226:576,227:577,228:$Vm2},{12:$Vv,13:$V1,14:147,29:$V5,147:146,230:580,234:145},o($VY1,[2,301]),{12:$Vv,13:$V1,14:147,29:$V5,147:146,230:581,234:145},o($VY1,[2,303]),o($VY1,[2,304]),o($VY1,[2,305]),{12:$Vn2,136:$Vr,146:131,148:269,196:362,235:582,236:361,237:363,238:364},{12:$Vn2,29:[1,585],136:$Vr,146:131,148:269,196:362,235:584,236:361,237:363,238:364},o($VS1,[2,326],{243:586,244:$V72}),o($VS1,$Vv1,{243:481,239:587,244:$V72}),o($Vo2,[2,333]),{12:$Vh,29:$Vi,121:589,245:[1,588]},{12:$Vy1,13:[1,590]},{12:$Vz1,13:[1,591]},{12:$Vv,147:592},o($V91,[2,152]),o($V91,[2,153]),o($Vf,[2,197]),o($Vf,[2,201]),{185:593,186:$Vt1},{186:[2,68]},{186:[2,69]},o([6,7,12,29,85,86],[2,204]),{12:$VQ1,167:594,168:380},o($Vb2,[2,208]),o($Vb2,[2,209],{170:595,2:[2,225]}),o($Vb2,[2,211]),o($Vb2,[2,212]),o($Vb2,[2,213]),o($Vb2,[2,214]),o($Vb2,[2,215]),o($Vb2,[2,216]),o($Vb2,[2,217]),o($Vb2,[2,218]),o($Vb2,[2,219]),o($Vb2,[2,220]),o($Vb2,[2,221]),o($Vb2,[2,222]),o($Vb2,[2,223]),o($Vb2,[2,224]),{2:[1,596],29:[1,597]},o($Vj1,[2,185],{84:490,152:513,162:514,155:515,55:516,161:598,56:$Vc2,57:$Vd2,85:$V92,86:$Va2,156:$Ve2}),o($Vp2,[2,188]),o($Vp2,[2,189]),o($Vp2,[2,190]),{105:[1,599]},{29:[1,601],157:[1,600]},{105:[2,46]},{105:[2,47]},o($Vf,[2,402]),{276:[1,602]},o($Vf,[2,376]),o($Vf,[2,379]),o($Vf,[2,380]),o($Vf,[2,381]),o($Vf,[2,401]),o($Vf,[2,403]),o($Vf,[2,400]),o($Vf,[2,410]),o($Vf,[2,408]),o($Vf,[2,409]),o($Vf,[2,424]),o($Vf,[2,422]),o($Vf,[2,423]),o($Vf,[2,425]),{144:$Vf2,159:[1,603]},{277:[1,604]},{12:$VT1,143:605},{104:606,105:$VL},{277:[1,607]},o($Vf,[2,454],{289:[1,608]}),o($Vf,[2,455]),{289:[1,609]},o($Vf,[2,453],{121:610,12:$Vh,29:$Vi,289:[1,611]}),{276:[1,612]},{12:[1,613]},o($Vf,[2,250]),o($Vh2,[2,227]),o($Vh2,[2,230],{187:[1,614],188:[1,615]}),o($Vh2,[2,231]),o($VU1,[2,479]),o($VU1,[2,480]),o($VU1,[2,484]),o($VU1,[2,485],{214:$Vi2}),o($VA1,[2,159]),o($VA1,[2,158]),{106:[1,616],137:[1,617]},o($VA1,[2,163]),o($VB1,[2,141]),o($VB1,[2,143]),o($VB1,[2,144]),o($VZ1,$V_1,{215:457,217:459,218:460,221:461,222:462,223:464,101:465,104:466,224:467,225:470,213:618,102:$V$1,103:$V02,105:$VL,131:$V12,158:$V22}),o($VZ1,$V_1,{215:457,217:459,218:460,221:461,222:462,223:464,101:465,104:466,224:467,225:470,213:620,29:[1,619],102:$V$1,103:$V02,105:$VL,131:$V12,158:$V22}),o($Vk2,[2,277]),o($VZ1,$V_1,{221:461,222:462,223:464,101:465,104:466,224:467,225:470,218:621,14:622,13:$V1,29:$V5,102:$V$1,103:$V02,105:$VL,158:$V22}),{131:[1,624],220:[1,623]},o($Vq2,[2,34]),o($Vq2,[2,35]),o($Vq2,[2,36]),o($Vq2,[2,37]),o($Vq2,[2,38]),o($Vq2,[2,39]),{159:[1,625],214:$Vi2},o($Vl2,[2,287]),o($Vl2,[2,81]),o($Vl2,[2,292],{30:626,31:$V01,32:$V11,33:$V21}),o($Vr2,[2,294]),o($Vr2,[2,297],{13:[1,627]}),{12:[1,628]},o($VY1,[2,300],{144:$V71}),o($VY1,[2,302],{144:$V71}),o($V42,[2,321],{248:$V52}),o($VS1,$V$,{30:224,239:479,243:481,12:$V62,31:$V01,32:$V11,33:$V21,244:$V72}),{29:[1,630],248:$V52,249:629,250:631,251:[1,632]},o($VS1,[2,345]),o($Vo2,[2,334]),o($VS1,[2,327],{243:586,244:$V72}),{12:$Vh,29:$Vi,121:634,240:633,241:[1,635],242:[1,636]},o($Vo2,[2,340]),o($V81,[2,317]),o($V81,[2,318]),o($V82,[2,171]),o([2,6,7,29,56,57,85,86,156],[2,226]),o($Vb2,[2,206]),{2:[1,637]},o($Vf,[2,195]),o($Vf,[2,196]),o($Vj1,[2,186],{84:490,152:513,162:514,155:515,55:516,161:638,56:$Vc2,57:$Vd2,85:$V92,86:$Va2,156:$Ve2}),o($Vp2,[2,175],{106:[1,639]}),o($Vp2,[2,183],{158:[1,640]}),o($Vp2,[2,184]),{277:[1,641]},o($Vf,[2,430],{121:642,12:$Vh,29:$Vi,115:[1,643]}),o($Vf,[2,436]),o($Vg2,[2,147]),o($Vg2,[2,148]),o($Vf,[2,440]),{12:$VT1,142:644,143:414},{12:$VT1,142:645,143:414},o($Vf,[2,456],{143:414,142:646,12:$VT1}),{12:$VT1,142:647,143:414},{277:[1,648]},o($Vf,[2,249]),{188:[1,649]},o($Vh2,[2,229]),{136:[1,650]},o($VA1,[2,161]),o($Vj2,[2,273]),o($Vj2,[2,275]),o($Vj2,[2,276]),o($Vk2,[2,280]),o($Vk2,[2,281]),o($Vk2,[2,282]),{220:[1,651]},o($Vl2,[2,286]),{12:$Vv,13:[1,652],147:578,227:653,228:$Vm2},o($Vr2,[2,298]),{228:[1,654]},o($VS1,[2,343]),o($VS1,[2,344]),o($VS1,[2,346]),o($VZ1,$V_1,{212:455,213:456,215:457,217:459,218:460,221:461,222:462,223:464,101:465,104:466,224:467,225:470,211:655,102:$V$1,103:$V02,105:$VL,131:$V12,158:$V22}),{12:[1,656],29:$Vi,121:658,246:657,247:$Vs2},o($Vo2,[2,339]),{158:[1,660]},{158:[1,661]},o($Vb2,[2,210]),o($Vj1,[2,187]),o($Vp2,[2,176],{105:[1,662]}),{12:$Vt2,105:$Vu2,153:663,154:664},o($Vf,[2,371]),o($Vf,[2,431]),o($Vf,[2,432]),o($Vf,[2,458],{144:$Vf2}),o($Vf,[2,459],{144:$Vf2}),o($Vf,[2,460],{144:$Vf2}),o($Vf,[2,457],{144:$Vf2}),o($Vf,[2,463]),o($Vh2,[2,228]),o($VA1,[2,160]),o($Vk2,[2,283]),o($Vr2,[2,295]),o($Vr2,[2,296]),o($Vr2,[2,299]),o($VS1,[2,347]),{12:$Vh,13:$Vx,29:$Vi,121:668,246:667,247:$Vs2},o($Vo2,[2,336]),o($Vo2,[2,338]),{12:[1,669],158:[1,670]},{12:$VM1,13:$Vw1,134:672,147:370,149:671},{12:$VM1,13:$Vw1,134:674,147:370,149:673},o($Vp2,[2,177]),{144:[1,676],159:[1,675]},o($Vb2,[2,178]),{42:[1,677]},{106:[1,678]},o($Vo2,[2,335]),o($Vo2,[2,337]),o($Vo2,[2,341]),{12:[1,679]},{30:485,31:$V01,32:$V11,33:$V21,159:[1,680]},{2:[1,681]},{30:485,31:$V01,32:$V11,33:$V21,159:[1,682]},{2:[1,683]},o($Vp2,[2,182]),{12:$Vt2,105:$Vu2,154:684},{12:[1,685]},{105:[1,686]},{144:[1,687]},o($Vv2,[2,329]),o($Vv2,[2,330]),o($Vv2,[2,331]),o($Vv2,[2,332]),o($Vb2,[2,179]),o($Vb2,[2,180]),{42:[1,688]},{12:[1,689]},{105:[1,690]},{159:[1,691]},{106:[1,692]},o($Vo2,[2,342]),{105:[1,693]},o($Vb2,[2,181])],
defaultActions: {58:[2,3],139:[2,2],219:[2,64],220:[2,65],302:[2,78],303:[2,79],491:[2,68],492:[2,69],518:[2,46],519:[2,47]},
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
      if (typeof parser.yy.result.suggestColumns.identifierChain !== 'undefined' && parser.yy.result.suggestColumns.identifierChain.length === 0) {
        delete parser.yy.result.suggestColumns.identifierChain;
      }
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
case 3: parser.yy.cursorFound = true; return 29; 
break;
case 4: parser.yy.cursorFound = true; return 13; 
break;
case 5: return 247; 
break;
case 6: return 286; 
break;
case 7: return 183; 
break;
case 8: return 278; 
break;
case 9: return 56; 
break;
case 10: return 279; 
break;
case 11: return 280; 
break;
case 12: determineCase(yy_.yytext); return 27; 
break;
case 13: return 60; 
break;
case 14: return 63; 
break;
case 15: return 66; 
break;
case 16: return 184; 
break;
case 17: determineCase(yy_.yytext); return 191; 
break;
case 18: return 115; 
break;
case 19: return 71; 
break;
case 20: return 117; 
break;
case 21: return '<hive>FUNCTION'; 
break;
case 22: return 281; 
break;
case 23: return 284; 
break;
case 24: return 36; 
break;
case 25: return 53; 
break;
case 26: return 54; 
break;
case 27: this.begin('hdfs'); return 79; 
break;
case 28: return 244; 
break;
case 29: return 74; 
break;
case 30: this.begin('hdfs'); return 85; 
break;
case 31: return 288; 
break;
case 32: return '<hive>MACRO'; 
break;
case 33: return 289; 
break;
case 34: return 290; 
break;
case 35: return 91; 
break;
case 36: return 94; 
break;
case 37: return 67; 
break;
case 38: return 39; 
break;
case 39: return 97; 
break;
case 40: return 292; 
break;
case 41: return '<hive>TEMPORARY'; 
break;
case 42: return 293; 
break;
case 43: return 100; 
break;
case 44: return 241; 
break;
case 45: return 242; 
break;
case 46: return 33; 
break;
case 47: return 82; 
break;
case 48: return 88; 
break;
case 49: return 23; 
break;
case 50: return 24; 
break;
case 51: return 272; 
break;
case 52: return 57; 
break;
case 53: determineCase(yy_.yytext); return 28; 
break;
case 54: return 61; 
break;
case 55: return 64; 
break;
case 56: return 68; 
break;
case 57: determineCase(yy_.yytext); return 192; 
break;
case 58: return 119; 
break;
case 59: return '<impala>FUNCTION'; 
break;
case 60: return 282; 
break;
case 61: return 287; 
break;
case 62: return 112; 
break;
case 63: return 72; 
break;
case 64: return '<impala>INCREMENTAL'; 
break;
case 65: this.begin('hdfs'); return 80; 
break;
case 66: return 77; 
break;
case 67: return 75; 
break;
case 68: this.begin('hdfs'); return 86; 
break;
case 69: return 291; 
break;
case 70: return 92; 
break;
case 71: return 95; 
break;
case 72: return 69; 
break;
case 73: return 273; 
break;
case 74: return 40; 
break;
case 75: return 98; 
break;
case 76: return 32; 
break;
case 77: return 83; 
break;
case 78: return 89; 
break;
case 79: return 216; 
break;
case 80: return 174; 
break;
case 81: return 175; 
break;
case 82: return 229; 
break;
case 83: return 180; 
break;
case 84: determineCase(yy_.yytext); return 26; 
break;
case 85: return 49; 
break;
case 86: return 179; 
break;
case 87: return 177; 
break;
case 88: determineCase(yy_.yytext); return 193; 
break;
case 89: return 129; 
break;
case 90: return 176; 
break;
case 91: return 35; 
break;
case 92: return 110; 
break;
case 93: return 128; 
break;
case 94: return 173; 
break;
case 95: return 197; 
break;
case 96: return 219; 
break;
case 97: return 248; 
break;
case 98: return 253; 
break;
case 99: return 131; 
break;
case 100: return 251; 
break;
case 101: return 214; 
break;
case 102: return 231; 
break;
case 103: return 'ROLE'; 
break;
case 104: return 50; 
break;
case 105: determineCase(yy_.yytext); return 198; 
break;
case 106: return 296; 
break;
case 107: determineCase(yy_.yytext); return 252; 
break;
case 108: return 172; 
break;
case 109: return 178; 
break;
case 110: return 38; 
break;
case 111: return 182; 
break;
case 112: return 171; 
break;
case 113: determineCase(yy_.yytext); return 294; 
break;
case 114: determineCase(yy_.yytext); return 303; 
break;
case 115: return 181; 
break;
case 116: return 245; 
break;
case 117: return 210; 
break;
case 118: return 102; 
break;
case 119: return 12; 
break;
case 120: parser.yy.cursorFound = true; return 29; 
break;
case 121: parser.yy.cursorFound = true; return 13; 
break;
case 122: return 186; 
break;
case 123: return 187; 
break;
case 124: this.popState(); return 188; 
break;
case 125: return 7; 
break;
case 126: return yy_.yytext; 
break;
case 127: return yy_.yytext; 
break;
case 128: return '['; 
break;
case 129: return ']'; 
break;
case 130: this.begin('backtickedValue'); return 136; 
break;
case 131: if (yy_.yytext.indexOf('\u2020') !== -1 || yy_.yytext.indexOf('\u2021') !== -1) {
                                        this.popState();
                                        return 137;
                                      }
                                      return 106;
                                    
break;
case 132: this.popState(); return 136; 
break;
case 133: this.begin('singleQuotedValue'); return 105; 
break;
case 134: return 106; 
break;
case 135: this.popState(); return 105; 
break;
case 136: this.begin('doubleQuotedValue'); return 108; 
break;
case 137: return 106; 
break;
case 138: this.popState(); return 108; 
break;
case 139: return 7; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:AS\b)/i,/^(?:ALL\b)/i,/^(?:BINARY\b)/i,/^(?:COLUMNS\b)/i,/^(?:COMMENT\b)/i,/^(?:COMPACTIONS\b)/i,/^(?:CONF\b)/i,/^(?:CREATE\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DATE\b)/i,/^(?:DESCRIBE\b)/i,/^(?:EXTENDED\b)/i,/^(?:EXTERNAL\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:IN\b)/i,/^(?:INDEX\b)/i,/^(?:INDEXES\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:LOCKS\b)/i,/^(?:MACRO\b)/i,/^(?:PARTITION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:TBLPROPERTIES\b)/i,/^(?:TEMPORARY\b)/i,/^(?:TRANSACTIONS\b)/i,/^(?:USER\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:AGGREGATE\b)/i,/^(?:ANALYTIC\b)/i,/^(?:COLUMN\b)/i,/^(?:COMMENT\b)/i,/^(?:CREATE\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DESCRIBE\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:GROUP\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INCREMENTAL\b)/i,/^(?:INPATH\b)/i,/^(?:IN\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:STATS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:[.])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DATABASE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:DROP\b)/i,/^(?:EXISTS\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:IF\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:LIKE\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:ROLE\b)/i,/^(?:SCHEMA\b)/i,/^(?:SELECT\b)/i,/^(?:SET\b)/i,/^(?:SHOW\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:\s+['])/i,/^(?:[^'\u2020\u2021]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>]+)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:[^"]+)/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[120,121,122,123,124,125],"inclusive":false},"doubleQuotedValue":{"rules":[137,138],"inclusive":false},"singleQuotedValue":{"rules":[134,135],"inclusive":false},"backtickedValue":{"rules":[131,132],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,126,127,128,129,130,133,136,139],"inclusive":true},"impala":{"rules":[0,1,2,3,4,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,126,127,128,129,130,133,136,139],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,126,127,128,129,130,133,136,139],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});