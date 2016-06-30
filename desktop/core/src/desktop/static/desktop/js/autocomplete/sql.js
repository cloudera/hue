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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,8],$V1=[1,19],$V2=[1,50],$V3=[1,51],$V4=[1,52],$V5=[1,18],$V6=[1,55],$V7=[1,56],$V8=[1,53],$V9=[1,54],$Va=[1,25],$Vb=[1,17],$Vc=[1,28],$Vd=[1,49],$Ve=[1,47],$Vf=[6,7],$Vg=[1,67],$Vh=[2,6,7,29,35,36,42,43,44,45,46,47,77,113,114,115,133,147,162,212,216,217,220,222,226,234],$Vi=[1,73],$Vj=[1,74],$Vk=[1,75],$Vl=[1,76],$Vm=[1,77],$Vn=[1,123],$Vo=[1,124],$Vp=[1,135],$Vq=[1,137],$Vr=[29,38,39,40,49,50,71,72],$Vs=[12,29,139],$Vt=[29,63,64],$Vu=[1,151],$Vv=[29,35],$Vw=[1,153],$Vx=[2,6,7,29,35,147,162,216,217],$Vy=[1,156],$Vz=[1,157],$VA=[1,158],$VB=[2,6,7,13,29,31,32,33,35,36,42,43,44,45,46,47,77,113,114,115,133,147,162,212,216,217,220,222,226,234,255,257,258,260,261,263,264],$VC=[1,160],$VD=[1,161],$VE=[6,7,12],$VF=[38,39,40],$VG=[6,7,12,29,130,139],$VH=[6,7,12,29,118,130,139],$VI=[6,7,12,29,139],$VJ=[2,107],$VK=[1,169],$VL=[1,176],$VM=[1,178],$VN=[1,179],$VO=[1,184],$VP=[1,185],$VQ=[29,291],$VR=[1,196],$VS=[1,198],$VT=[6,7,266],$VU=[6,7,29,105,291],$VV=[2,115],$VW=[1,223],$VX=[1,224],$VY=[29,38,39,40],$VZ=[29,94,95],$V_=[29,320],$V$=[6,7,29,266],$V01=[29,322,325],$V11=[6,7,29,36,77,105,291],$V21=[29,79,80],$V31=[6,7,29,334],$V41=[2,162],$V51=[1,238],$V61=[6,7,12,29,118,312,327,334],$V71=[1,244],$V81=[1,242],$V91=[1,245],$Va1=[2,6,7,162],$Vb1=[2,6,7,29,113,114,115,162,216,217],$Vc1=[1,258],$Vd1=[1,265],$Ve1=[1,271],$Vf1=[1,274],$Vg1=[12,13,139,246,247],$Vh1=[2,27],$Vi1=[2,28],$Vj1=[1,278],$Vk1=[1,279],$Vl1=[88,89,102,108],$Vm1=[1,283],$Vn1=[1,289],$Vo1=[6,7,29,118,312,327],$Vp1=[2,29],$Vq1=[6,7,33],$Vr1=[6,7,29,291],$Vs1=[1,326],$Vt1=[1,327],$Vu1=[1,334],$Vv1=[1,335],$Vw1=[2,102],$Vx1=[1,346],$Vy1=[1,351],$Vz1=[1,350],$VA1=[6,7,31,32,33],$VB1=[2,137],$VC1=[6,7,29,31,32,33,105,291],$VD1=[2,6,7,12,29,31,32,33,35,36,82,83,105,110,111,113,114,115,127,128,139,147,162,212,216,217,255,257,258,260,261,263,264,266,287,291],$VE1=[1,359],$VF1=[2,6,7,12,29,110,111,113,114,115,139,147,162,212,216,217,255,257,258,260,261,263,264,266,287],$VG1=[2,6,7,29,162,216,217],$VH1=[12,246],$VI1=[2,306],$VJ1=[1,389],$VK1=[1,390],$VL1=[1,374],$VM1=[1,384],$VN1=[2,6,7,29,113,114,115,147,162,212,216,217],$VO1=[2,340],$VP1=[1,395],$VQ1=[1,396],$VR1=[1,397],$VS1=[1,398],$VT1=[1,399],$VU1=[1,400],$VV1=[2,6,7,29,113,114,115,147,162,212,216,217,255,257,258,260,261,263,264,266,287],$VW1=[2,385],$VX1=[1,405],$VY1=[1,406],$VZ1=[2,6,7,29,113,114,115,147,162,212,216,217,255,257,258,260,261,263,264,266],$V_1=[2,6,7,12,29,31,32,33,35,110,111,113,114,115,118,139,147,162,212,216,217,255,257,258,260,261,263,264,266,287,312,327,334],$V$1=[2,6,7,29,31,32,33,35,147,162,216,217],$V02=[1,419],$V12=[2,187],$V22=[1,452],$V32=[6,7,29,147,212],$V42=[2,6,7,29,162,217],$V52=[29,214],$V62=[1,490],$V72=[2,6,7,29,113,114,115,147,162,212,216,217,220],$V82=[2,6,7,29,113,114,115,147,162,212,216,217,220,222],$V92=[2,6,7,29,113,114,115,147,162,212,216,217,220,222,226],$Va2=[2,282],$Vb2=[1,504],$Vc2=[2,6,7,29,36,42,43,44,45,46,47,77,113,114,115,133,147,162,212,216,217,220,222,226,234],$Vd2=[2,6,7,29,36,42,43,44,45,46,47,77,113,114,115,133,147,162,212,216,217,220,222,226,234,255,257,258,260,261,263,264],$Ve2=[1,511],$Vf2=[29,255],$Vg2=[2,353],$Vh2=[1,516],$Vi2=[12,139],$Vj2=[1,541],$Vk2=[1,542],$Vl2=[147,162],$Vm2=[1,568],$Vn2=[1,569],$Vo2=[1,567],$Vp2=[1,588],$Vq2=[6,7,147,162],$Vr2=[2,6,7,29,56,57,85,86,159,200],$Vs2=[2,6,7,29,162],$Vt2=[12,13,29,102,103,105,161,246],$Vu2=[2,6,7,29,31,32,33,36,42,43,44,45,46,47,77,113,114,115,133,147,162,212,216,217,220,222,226,234,255,257,258,260,261,263,264],$Vv2=[2,29,56,57,85,86,159],$Vw2=[1,681],$Vx2=[2,6,7,29,113,114,115,147,162,212,216,217,255,257,258,260,261,263,264],$Vy2=[2,6,7,12,29,110,111,113,114,115,139,147,162,212,216,217,220,222,226,255,257,258,260,261,263,264,266],$Vz2=[1,705],$VA2=[1,706],$VB2=[1,714],$VC2=[1,715],$VD2=[1,716],$VE2=[2,6,7,29,113,114,115,147,162,212,216,217,222,255,257,258,260,261,263,264],$VF2=[1,722],$VG2=[12,29,111];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"InitResults":3,"Sql":4,"SqlStatements":5,";":6,"EOF":7,"SqlStatement":8,"DataDefinition":9,"DataManipulation":10,"QuerySpecification":11,"REGULAR_IDENTIFIER":12,"PARTIAL_CURSOR":13,"AnyCursor":14,"CreateStatement":15,"DescribeStatement":16,"DropStatement":17,"ShowStatement":18,"UseStatement":19,"LoadStatement":20,"UpdateStatement":21,"AggregateOrAnalytic":22,"<impala>AGGREGATE":23,"<impala>ANALYTIC":24,"AnyCreate":25,"CREATE":26,"<hive>CREATE":27,"<impala>CREATE":28,"CURSOR":29,"AnyDot":30,".":31,"<impala>.":32,"<hive>.":33,"AnyFromOrIn":34,"FROM":35,"<hive>IN":36,"AnyTable":37,"TABLE":38,"<hive>TABLE":39,"<impala>TABLE":40,"ComparisonOperators":41,"=":42,"<>":43,"<=":44,">=":45,"<":46,">":47,"DatabaseOrSchema":48,"DATABASE":49,"SCHEMA":50,"FromOrIn":51,"HiveIndexOrIndexes":52,"<hive>INDEX":53,"<hive>INDEXES":54,"HiveOrImpalaComment":55,"<hive>COMMENT":56,"<impala>COMMENT":57,"HiveOrImpalaCreate":58,"HiveOrImpalaCurrent":59,"<hive>CURRENT":60,"<impala>CURRENT":61,"HiveOrImpalaData":62,"<hive>DATA":63,"<impala>DATA":64,"HiveOrImpalaDatabasesOrSchemas":65,"<hive>DATABASES":66,"<hive>SCHEMAS":67,"<impala>DATABASES":68,"<impala>SCHEMAS":69,"HiveOrImpalaExternal":70,"<hive>EXTERNAL":71,"<impala>EXTERNAL":72,"HiveOrImpalaLoad":73,"<hive>LOAD":74,"<impala>LOAD":75,"HiveOrImpalaIn":76,"<impala>IN":77,"HiveOrImpalaInpath":78,"<hive>INPATH":79,"<impala>INPATH":80,"HiveOrImpalaLeftSquareBracket":81,"<hive>[":82,"<impala>[":83,"HiveOrImpalaLocation":84,"<hive>LOCATION":85,"<impala>LOCATION":86,"HiveOrImpalaRightSquareBracket":87,"<hive>]":88,"<impala>]":89,"HiveOrImpalaRole":90,"<hive>ROLE":91,"<impala>ROLE":92,"HiveOrImpalaRoles":93,"<hive>ROLES":94,"<impala>ROLES":95,"HiveOrImpalaTables":96,"<hive>TABLES":97,"<impala>TABLES":98,"HiveRoleOrUser":99,"<hive>USER":100,"SignedInteger":101,"UNSIGNED_INTEGER":102,"-":103,"SingleQuotedValue":104,"SINGLE_QUOTE":105,"VALUE":106,"DoubleQuotedValue":107,"DOUBLE_QUOTE":108,"AnyAs":109,"AS":110,"<hive>AS":111,"AnyGroup":112,"GROUP":113,"<hive>GROUP":114,"<impala>GROUP":115,"OptionalAggregateOrAnalytic":116,"OptionalExtended":117,"<hive>EXTENDED":118,"OptionalExtendedOrFormatted":119,"<hive>FORMATTED":120,"OptionalFormatted":121,"<impala>FORMATTED":122,"OptionallyFormattedIndex":123,"OptionalFromDatabase":124,"DatabaseIdentifier":125,"OptionalHiveCascadeOrRestrict":126,"<hive>CASCADE":127,"<hive>RESTRICT":128,"OptionalIfExists":129,"IF":130,"EXISTS":131,"OptionalIfNotExists":132,"NOT":133,"OptionalInDatabase":134,"ConfigurationName":135,"PartialBacktickedOrCursor":136,"PartialBacktickedIdentifier":137,"PartialBacktickedOrPartialCursor":138,"BACKTICK":139,"PARTIAL_VALUE":140,"SchemaQualifiedTableIdentifier":141,"RegularOrBacktickedIdentifier":142,"ImprovedDerivedColumnChain":143,"OptionalMapOrArrayKey":144,"PartitionSpecList":145,"PartitionSpec":146,",":147,"CleanRegularOrBackTickedSchemaQualifiedName":148,"RegularOrBackTickedSchemaQualifiedName":149,"ColumnIdentifier":150,"LocalOrSchemaQualifiedName":151,"DerivedColumnChain":152,"TableDefinition":153,"DatabaseDefinition":154,"Comment":155,"HivePropertyAssignmentList":156,"HivePropertyAssignment":157,"HiveDbProperties":158,"<hive>WITH":159,"DBPROPERTIES":160,"(":161,")":162,"DatabaseDefinitionOptionals":163,"DatabaseDefinitionOptional":164,"HdfsLocation":165,"CleanUpDatabaseConditions":166,"TableScope":167,"TableElementList":168,"TableElements":169,"TableElement":170,"ColumnDefinition":171,"PrimitiveType":172,"ColumnDefinitionError":173,"TINYINT":174,"SMALLINT":175,"INT":176,"BIGINT":177,"BOOLEAN":178,"FLOAT":179,"DOUBLE":180,"STRING":181,"DECIMAL":182,"CHAR":183,"VARCHAR":184,"TIMESTAMP":185,"<hive>BINARY":186,"<hive>DATE":187,"HdfsPath":188,"HDFS_START_QUOTE":189,"HDFS_PATH":190,"HDFS_END_QUOTE":191,"HiveDescribeStatement":192,"ImpalaDescribeStatement":193,"<hive>DESCRIBE":194,"<impala>DESCRIBE":195,"DROP":196,"DropDatabaseStatement":197,"DropTableStatement":198,"TablePrimary":199,"INTO":200,"SELECT":201,"SelectList":202,"TableExpression":203,"FromClause":204,"SelectConditions":205,"TableReferenceList":206,"OptionalWhereClause":207,"OptionalGroupByClause":208,"OptionalOrderByClause":209,"OptionalLimitClause":210,"WhereClause":211,"WHERE":212,"SearchCondition":213,"BY":214,"ColumnList":215,"ORDER":216,"LIMIT":217,"BooleanValueExpression":218,"BooleanTerm":219,"OR":220,"BooleanFactor":221,"AND":222,"BooleanTest":223,"BooleanPrimary":224,"OptionalIsNotTruthValue":225,"IS":226,"OptionalNot":227,"TruthValue":228,"Predicate":229,"BooleanPredicand":230,"ComparisonPredicate":231,"InPredicate":232,"AnyIn":233,"IN":234,"ParenthesizedBooleanValueExpression":235,"NonParenthesizedValueExpressionPrimary":236,"CommonValueExpression":237,"InPredicatePartTwo":238,"InPredicateValue":239,"TableSubquery":240,"ColumnReference":241,"BasicIdentifierChain":242,"InitIdentifierChain":243,"IdentifierChain":244,"Identifier":245,"\"":246,"*":247,"DerivedColumn":248,"TableReference":249,"TablePrimaryOrJoinedTable":250,"ImprovedTablePrimary":251,"JoinedTable":252,"Joins":253,"JoinTypes":254,"JOIN":255,"JoinCondition":256,"<hive>CROSS":257,"FULL":258,"OptionalOuter":259,"<impala>INNER":260,"LEFT":261,"SEMI":262,"RIGHT":263,"<impala>RIGHT":264,"OUTER":265,"ON":266,"JoinEqualityExpression":267,"ParenthesizedJoinEqualityExpression":268,"EqualityExpression":269,"TableOrQueryName":270,"OptionalCorrelationName":271,"OptionalLateralViews":272,"DerivedTable":273,"PushQueryState":274,"PopQueryState":275,"Subquery":276,"QueryExpression":277,"QueryExpressionBody":278,"NonJoinQueryExpression":279,"NonJoinQueryTerm":280,"NonJoinQueryPrimary":281,"SimpleTable":282,"LateralView":283,"UserDefinedTableGeneratingFunction":284,"<hive>explode":285,"<hive>posexplode":286,"<hive>LATERAL":287,"VIEW":288,"LateralViewColumnAliases":289,"SHOW":290,"LIKE":291,"ShowColumnStatement":292,"ShowColumnsStatement":293,"ShowCompactionsStatement":294,"ShowConfStatement":295,"ShowCreateTableStatement":296,"ShowCurrentStatement":297,"ShowDatabasesStatement":298,"ShowFunctionsStatement":299,"ShowGrantStatement":300,"ShowIndexStatement":301,"ShowLocksStatement":302,"ShowPartitionsStatement":303,"ShowRoleStatement":304,"ShowRolesStatement":305,"ShowTableStatement":306,"ShowTablesStatement":307,"ShowTblPropertiesStatement":308,"ShowTransactionsStatement":309,"<impala>COLUMN":310,"<impala>STATS":311,"if":312,"partial":313,"identifierChain":314,"length":315,"<hive>COLUMNS":316,"<hive>COMPACTIONS":317,"<hive>CONF":318,"<hive>FUNCTIONS":319,"<impala>FUNCTIONS":320,"SingleQuoteValue":321,"<hive>GRANT":322,"OptionalPrincipalName":323,"<hive>ALL":324,"<impala>GRANT":325,"<hive>LOCKS":326,"<hive>PARTITION":327,"<hive>PARTITIONS":328,"<impala>PARTITIONS":329,"<hive>TBLPROPERTIES":330,"<hive>TRANSACTIONS":331,"UPDATE":332,"TargetTable":333,"SET":334,"SetClauseList":335,"TableName":336,"SetClause":337,"SetTarget":338,"UpdateSource":339,"ValueExpression":340,"USE":341,"$accept":0,"$end":1},
terminals_: {2:"error",6:";",7:"EOF",12:"REGULAR_IDENTIFIER",13:"PARTIAL_CURSOR",23:"<impala>AGGREGATE",24:"<impala>ANALYTIC",26:"CREATE",27:"<hive>CREATE",28:"<impala>CREATE",29:"CURSOR",31:".",32:"<impala>.",33:"<hive>.",35:"FROM",36:"<hive>IN",38:"TABLE",39:"<hive>TABLE",40:"<impala>TABLE",42:"=",43:"<>",44:"<=",45:">=",46:"<",47:">",49:"DATABASE",50:"SCHEMA",53:"<hive>INDEX",54:"<hive>INDEXES",56:"<hive>COMMENT",57:"<impala>COMMENT",60:"<hive>CURRENT",61:"<impala>CURRENT",63:"<hive>DATA",64:"<impala>DATA",66:"<hive>DATABASES",67:"<hive>SCHEMAS",68:"<impala>DATABASES",69:"<impala>SCHEMAS",71:"<hive>EXTERNAL",72:"<impala>EXTERNAL",74:"<hive>LOAD",75:"<impala>LOAD",77:"<impala>IN",79:"<hive>INPATH",80:"<impala>INPATH",82:"<hive>[",83:"<impala>[",85:"<hive>LOCATION",86:"<impala>LOCATION",88:"<hive>]",89:"<impala>]",91:"<hive>ROLE",92:"<impala>ROLE",94:"<hive>ROLES",95:"<impala>ROLES",97:"<hive>TABLES",98:"<impala>TABLES",100:"<hive>USER",102:"UNSIGNED_INTEGER",103:"-",105:"SINGLE_QUOTE",106:"VALUE",108:"DOUBLE_QUOTE",110:"AS",111:"<hive>AS",113:"GROUP",114:"<hive>GROUP",115:"<impala>GROUP",118:"<hive>EXTENDED",120:"<hive>FORMATTED",122:"<impala>FORMATTED",127:"<hive>CASCADE",128:"<hive>RESTRICT",130:"IF",131:"EXISTS",133:"NOT",139:"BACKTICK",140:"PARTIAL_VALUE",147:",",159:"<hive>WITH",160:"DBPROPERTIES",161:"(",162:")",174:"TINYINT",175:"SMALLINT",176:"INT",177:"BIGINT",178:"BOOLEAN",179:"FLOAT",180:"DOUBLE",181:"STRING",182:"DECIMAL",183:"CHAR",184:"VARCHAR",185:"TIMESTAMP",186:"<hive>BINARY",187:"<hive>DATE",189:"HDFS_START_QUOTE",190:"HDFS_PATH",191:"HDFS_END_QUOTE",194:"<hive>DESCRIBE",195:"<impala>DESCRIBE",196:"DROP",200:"INTO",201:"SELECT",212:"WHERE",214:"BY",216:"ORDER",217:"LIMIT",220:"OR",222:"AND",226:"IS",228:"TruthValue",234:"IN",246:"\"",247:"*",255:"JOIN",257:"<hive>CROSS",258:"FULL",260:"<impala>INNER",261:"LEFT",262:"SEMI",263:"RIGHT",264:"<impala>RIGHT",265:"OUTER",266:"ON",285:"<hive>explode",286:"<hive>posexplode",287:"<hive>LATERAL",288:"VIEW",290:"SHOW",291:"LIKE",310:"<impala>COLUMN",311:"<impala>STATS",312:"if",313:"partial",314:"identifierChain",315:"length",316:"<hive>COLUMNS",317:"<hive>COMPACTIONS",318:"<hive>CONF",319:"<hive>FUNCTIONS",320:"<impala>FUNCTIONS",321:"SingleQuoteValue",322:"<hive>GRANT",324:"<hive>ALL",325:"<impala>GRANT",326:"<hive>LOCKS",327:"<hive>PARTITION",328:"<hive>PARTITIONS",329:"<impala>PARTITIONS",330:"<hive>TBLPROPERTIES",331:"<hive>TRANSACTIONS",332:"UPDATE",334:"SET",341:"USE"},
productions_: [0,[3,0],[4,4],[4,3],[5,1],[5,3],[8,1],[8,1],[8,1],[8,3],[8,2],[8,1],[9,1],[9,1],[9,1],[9,1],[9,1],[10,1],[10,1],[22,1],[22,1],[25,1],[25,1],[25,1],[14,1],[14,1],[30,1],[30,1],[30,1],[34,1],[34,1],[37,1],[37,1],[37,1],[41,1],[41,1],[41,1],[41,1],[41,1],[41,1],[48,1],[48,1],[51,1],[51,1],[52,1],[52,1],[55,1],[55,1],[58,1],[58,1],[59,1],[59,1],[62,1],[62,1],[65,1],[65,1],[65,1],[65,1],[70,1],[70,1],[73,1],[73,1],[76,1],[76,1],[78,1],[78,1],[81,1],[81,1],[84,1],[84,1],[87,1],[87,1],[90,1],[90,1],[93,1],[93,1],[96,1],[96,1],[99,1],[99,1],[101,1],[101,2],[104,3],[107,3],[109,1],[109,1],[112,1],[112,1],[112,1],[116,0],[116,1],[117,0],[117,1],[119,0],[119,1],[119,1],[121,0],[121,1],[123,2],[123,2],[123,2],[123,1],[124,0],[124,2],[126,0],[126,1],[126,1],[129,0],[129,2],[129,2],[132,0],[132,1],[132,2],[132,3],[132,3],[134,0],[134,2],[135,1],[135,1],[135,3],[135,3],[136,1],[136,1],[138,1],[138,1],[137,2],[141,1],[141,1],[141,3],[141,3],[141,3],[125,1],[125,1],[143,1],[143,2],[143,3],[143,4],[144,0],[144,3],[144,3],[144,2],[145,1],[145,3],[146,3],[148,1],[148,1],[150,1],[150,4],[150,4],[150,3],[142,1],[142,3],[149,3],[149,5],[149,5],[149,7],[149,5],[149,3],[149,1],[149,3],[151,1],[151,2],[151,1],[151,2],[152,1],[152,3],[15,1],[15,1],[15,2],[155,2],[155,3],[155,4],[156,1],[156,3],[157,3],[157,7],[158,5],[158,2],[158,2],[163,1],[163,2],[163,3],[164,1],[164,1],[164,1],[166,0],[154,3],[154,4],[154,5],[154,7],[154,7],[153,6],[153,5],[153,4],[153,3],[153,6],[153,4],[167,1],[168,3],[169,1],[169,3],[170,1],[171,2],[171,2],[171,4],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[173,0],[165,2],[188,3],[188,5],[188,4],[188,3],[188,3],[188,2],[16,1],[16,1],[192,3],[192,4],[193,3],[193,3],[17,2],[17,1],[17,1],[197,3],[197,4],[197,5],[197,5],[198,3],[198,4],[198,4],[198,5],[20,7],[20,6],[20,5],[20,4],[20,3],[20,2],[11,3],[11,3],[11,3],[203,2],[203,3],[204,2],[205,4],[211,2],[211,2],[207,0],[207,2],[207,2],[208,0],[208,3],[208,2],[209,0],[209,3],[209,2],[210,0],[210,2],[210,2],[213,1],[218,1],[218,3],[219,1],[219,3],[219,3],[221,2],[221,1],[223,2],[225,0],[225,3],[227,0],[227,1],[224,1],[224,1],[229,1],[229,1],[233,1],[233,1],[233,1],[231,3],[231,3],[230,1],[230,1],[230,1],[237,1],[237,1],[232,2],[238,3],[239,1],[235,3],[235,2],[236,1],[241,1],[242,2],[243,0],[244,1],[244,3],[244,3],[245,1],[245,2],[245,3],[202,1],[202,1],[215,1],[215,3],[215,3],[248,1],[248,3],[248,2],[248,3],[248,3],[248,5],[248,5],[248,1],[206,1],[206,3],[249,1],[249,1],[250,1],[250,1],[252,2],[253,4],[253,4],[253,3],[253,3],[253,4],[253,5],[253,4],[254,0],[254,1],[254,2],[254,3],[254,1],[254,3],[254,2],[254,2],[254,2],[254,3],[254,3],[254,2],[254,2],[259,0],[259,1],[256,2],[256,2],[268,3],[268,3],[267,1],[267,3],[269,3],[269,1],[269,3],[269,3],[269,1],[269,1],[199,1],[251,3],[251,2],[270,1],[273,1],[274,0],[275,0],[240,5],[240,4],[276,1],[276,1],[276,1],[277,1],[278,1],[279,1],[280,1],[281,1],[282,1],[271,0],[271,1],[271,1],[271,2],[271,2],[272,0],[272,2],[284,4],[284,4],[284,4],[284,4],[283,5],[283,4],[283,5],[283,4],[283,3],[283,2],[289,2],[289,6],[18,2],[18,3],[18,4],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[292,3],[292,4],[292,8],[293,3],[293,4],[293,4],[293,5],[293,6],[293,4],[293,5],[293,6],[293,6],[293,6],[294,2],[295,3],[296,3],[296,4],[296,4],[296,4],[297,3],[297,3],[297,3],[298,3],[298,4],[298,3],[299,2],[299,3],[299,3],[299,4],[299,4],[299,5],[299,6],[299,6],[299,6],[299,6],[300,3],[300,5],[300,5],[300,5],[300,6],[300,6],[300,6],[300,3],[323,0],[323,1],[323,1],[323,2],[301,2],[301,3],[301,4],[301,4],[301,4],[301,5],[301,6],[301,6],[301,6],[301,6],[302,3],[302,3],[302,4],[302,4],[302,7],[302,8],[302,8],[302,4],[302,4],[303,3],[303,7],[303,4],[303,5],[303,3],[303,7],[304,3],[304,5],[304,4],[304,5],[304,5],[304,4],[304,5],[304,5],[305,2],[306,3],[306,4],[306,5],[306,6],[306,6],[306,6],[306,7],[306,8],[306,8],[306,8],[306,8],[306,3],[306,4],[306,8],[307,3],[307,4],[307,4],[307,5],[308,3],[309,2],[21,5],[21,5],[21,4],[21,3],[21,2],[21,2],[333,1],[336,1],[335,1],[335,3],[337,3],[337,2],[337,1],[338,1],[339,1],[340,1],[19,2],[19,2]],
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
     delete parser.yy.keepColumns;

     parser.parseError = function (message, error) {
       if (typeof parser.yy.result.suggestColumns !== 'undefined') {
         linkTablePrimaries();
       }
       parser.yy.result.error = error;
       return message;
     }
   
break;
case 2: case 3:

     return parser.yy.result;
   
break;
case 10: case 11:

     suggestDdlAndDmlKeywords();
   
break;
case 82: case 83: case 151:

     this.$ = $$[$0-1];
   
break;
case 99:

     suggestKeywords(['INDEX', 'INDEXES']);
   
break;
case 100:

     suggestKeywords(['FORMATTED']);
   
break;
case 108: case 113:

     suggestKeywords(['EXISTS']);
   
break;
case 111:

     suggestKeywords(['IF NOT EXISTS']);
   
break;
case 112:

     suggestKeywords(['NOT EXISTS']);
   
break;
case 126: case 531:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 127:

     this.$ = { identifierChain: [{ name: $$[$0] }] }
   
break;
case 128:

     suggestDatabases();
     this.$ = { identifierChain: [{ name: $$[$0-2] }] }
   
break;
case 129:

     // In Impala you can have statements like 'SELECT ... FROM testTable t, t.|'
     suggestTablesOrColumns($$[$0-2]);
   
break;
case 130:

     this.$ = { identifierChain: [{ name: $$[$0-2] }, { name: $$[$0] }] }
   
break;
case 131:

     this.$ = { cursorOrPartialIdentifier: true }
     suggestDatabases();
   
break;
case 133:

     this.$ = { identifierChain: [], partial: true };
   
break;
case 134:

     if (typeof $$[$0].key !== 'undefined') {
       this.$ = { identifierChain: [{ name: $$[$0-1], key: $$[$0].key }], partial: false };
     } else {
       this.$ = { identifierChain: [{ name: $$[$0-1] }], partial: false };
     }
   
break;
case 135:

     this.$ = { identifierChain: $$[$0-2].identifierChain, partial: true };
   
break;
case 136:

     if (typeof $$[$0].key !== 'undefined') {
       this.$ = { identifierChain: $$[$0-3].identifierChain.concat({ name: $$[$0-1], key: $$[$0].key }), partial: false };
     } else {
       this.$ = { identifierChain: $$[$0-3].identifierChain.concat({ name: $$[$0-1] }), partial: false };
     }
   
break;
case 137:
 this.$ = {} 
break;
case 138:

     this.$ = { key: '"' + $$[$0-1] + '"' }
   
break;
case 139:

     this.$ = { key: $$[$0-1] }
   
break;
case 140:

     this.$ = { key: null }
   
break;
case 144: case 160:

     this.$ = { identifierChain: [ { name: $$[$0] } ] }
   
break;
case 145: case 303: case 304:

     this.$ = $$[$0];
   
break;
case 146:

     this.$ = { name: $$[$0] }
   
break;
case 147:

     this.$ = { name: $$[$0-3], key: '"' + $$[$0-1] + '"' }
   
break;
case 148:

     this.$ = { name: $$[$0-3], key: parseInt($$[$0-1]) }
   
break;
case 149:

     this.$ = { name: $$[$0-2], key: null }
   
break;
case 152:

     this.$ = { identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] }
   
break;
case 153:

     this.$ = { identifierChain: [ { name: $$[$0-3] }, { name: $$[$0] } ] }
   
break;
case 154:

     this.$ = { identifierChain: [ { name: $$[$0-4] }, { name: $$[$0-1] } ] }
   
break;
case 155:

     this.$ = { identifierChain: [ { name: $$[$0-5] }, { name: $$[$0-1] } ] }
   
break;
case 156:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-3] } ] };
   
break;
case 157:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-2] } ] };
   
break;
case 158:

     this.$ = { partial: true, identifierChain: [ ] };
   
break;
case 159:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ] }
   
break;
case 161:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] };
   
break;
case 163:

     this.$ = { identifierChain: $$[$0-1].identifierChain, alias: $$[$0] }
   
break;
case 164:

     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 165:

     parser.yy.derivedColumnChain.push($$[$0]);
     this.$ = parser.yy.derivedColumnChain;
   
break;
case 168:

     if (isHive() || isImpala()) {
       suggestKeywords(['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
   
break;
case 178:

     suggestKeywords(['DBPROPERTIES']);
   
break;
case 182:

     parser.yy.afterComment = true;
   
break;
case 183:

     parser.yy.afterHdfsLocation = true;
   
break;
case 184:

     parser.yy.afterHiveDbProperties = true;
   
break;
case 185:

     delete parser.yy.afterComment;
     delete parser.yy.afterHdfsLocation;
     delete parser.yy.afterHiveDbProperties;
   
break;
case 188:

     if (isHive()) {
       suggestKeywords(['COMMENT', 'LOCATION', 'WITH DBPROPERTIES']);
     } else if (isImpala()) {
       suggestKeywords(['COMMENT', 'LOCATION']);
     }
   
break;
case 190:

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
case 192: case 193: case 194:

      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    
break;
case 195:

     if (isHive() || isImpala()) {
       suggestKeywords(['LOCATION']);
     }
   
break;
case 203: case 219:

     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   
break;
case 222:

      suggestHdfs({ path: $$[$0-3] });
    
break;
case 223:

     suggestHdfs({ path: $$[$0-2] });
   
break;
case 224:

      suggestHdfs({ path: $$[$0-1] });
    
break;
case 225:

     suggestHdfs({ path: '' });
   
break;
case 226:

      suggestHdfs({ path: '' });
    
break;
case 229:

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
case 230:

     if ($$[$0].cursorOrPartialIdentifier && !$$[$0-1]) {
       suggestKeywords(['EXTENDED']);
     }
   
break;
case 231:

      if ($$[$0].cursorOrPartialIdentifier && !$$[$0-1]) {
        suggestKeywords(['FORMATTED']);
      }
    
break;
case 232:

      if (!$$[$0-1]) {
        suggestKeywords(['FORMATTED']);
      }
      suggestTables();
      suggestDatabases({ appendDot: true });
      this.$ = { cursorOrPartialIdentifier: true }
    
break;
case 233:

     if (isHive()) {
       suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'MACRO', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
     } else {
       suggestKeywords(['ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   
break;
case 237:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   
break;
case 238:

     if (isHive()) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   
break;
case 241:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 242:

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
case 243:

     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   
break;
case 245:

     suggestKeywords([ 'TABLE' ]);
   
break;
case 246:

     suggestKeywords([ 'INTO' ]);
   
break;
case 248:

     suggestKeywords([ 'INPATH' ]);
   
break;
case 249:

     suggestKeywords([ 'DATA' ]);
   
break;
case 250: case 251: case 526: case 528:

     linkTablePrimaries();
   
break;
case 252:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 254:

     if ($$[$0-1]) {
       if ($$[$0-1].empty) {
         if (isHive()) {
           suggestKeywords(['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']);
         } else if (isImpala()) {
           suggestKeywords(['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT ANTI JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT ANTI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'RIGHT SEMI JOIN', 'WHERE']);
         } else {
           suggestKeywords(['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']);
         }
       } else if ($$[$0-1].keywords) {
         suggestKeywords($$[$0-1].keywords);
       }
     }
   
break;
case 256:

     if (!$$[$0-3] && !$$[$0-2] && !$$[$0-1] && !$$[$0]) {
       this.$ = { empty: true }
     } else if ($$[$0-3] && !$$[$0-2] && !$$[$0-1] && !$$[$0]) {
       this.$ = { keywords: ['GROUP BY', 'LIMIT', 'ORDER BY'] }
     } else if ($$[$0-2] && !$$[$0-1] && !$$[$0]) {
       this.$ = { keywords: ['ORDER BY', 'LIMIT'] }
     } else if ($$[$0-1] && !$$[$0]) {
       this.$ = { keywords: ['LIMIT'] }
     }
   
break;
case 258: case 261: case 311: case 363: case 364: case 365: case 366: case 538:

     suggestColumns();
   
break;
case 263: case 266:

     delete parser.yy.result.suggestStar;
   
break;
case 264: case 267:

     suggestKeywords(['BY']);
   
break;
case 270:

     suggestNumbers([1, 5, 10]);
   
break;
case 275:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 292:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 302:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 305:

     this.$ = parser.yy.identifierChain;
     delete parser.yy.identifierChain;
   
break;
case 306:

     parser.yy.identifierChain = [];
   
break;
case 308:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 310:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 312:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 319:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 320:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 322:

      delete parser.yy.derivedColumnChain;
   
break;
case 323: case 324:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 325:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 329:

        suggestTables();
        suggestDatabases({ appendDot: true });
    
break;
case 331:

     parser.yy.unfinishedJoin = false;
   
break;
case 334: case 473: case 475:

     suggestKeywords(['ON']);
   
break;
case 335: case 339: case 426: case 441: case 491: case 495: case 518:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 343: case 349:

     if (!$$[$0-1]) {
       suggestKeywords(['OUTER']);
     }
   
break;
case 345:

     var keywords = [];
     if (isImpala()) {
       keywords.push('ANTI');
       keywords.push('SEMI');
     }
     if (isHive()) {
       keywords.push('SEMI');
     }
     if (!$$[$0-1]) {
       keywords.push('OUTER');
     }
     suggestKeywords(keywords);
   
break;
case 350:

     if (!$$[$0-1]) {
       suggestKeywords(['ANTI', 'SEMI', 'OUTER']);
     } else {
       suggestKeywords(['ANTI', 'SEMI']);
     }
   
break;
case 368:

     if ($$[$0-2].identifierChain) {
       if ($$[$0-1] && !$$[$0-1].partial) {
         $$[$0-2].alias = $$[$0-1]
       }
       if ($$[$0] && $$[$0].length > 0) {
         $$[$0-2].lateralViews = $$[$0];
       }
       addTablePrimary($$[$0-2]);
     }
   
break;
case 369:

     if ($$[$0] && !$$[$0].partial) {
       // TODO: Potentially add columns for SELECT bla.| FROM (SELECT * FROM foo) AS bla;
       addTablePrimary({ subqueryAlias: $$[$0] });
     }
   
break;
case 372:

     if (typeof parser.yy.primariesStack === 'undefined') {
       parser.yy.primariesStack = [];
     }
     if (typeof parser.yy.resultStack === 'undefined') {
       parser.yy.resultStack = [];
     }
     parser.yy.primariesStack.push(parser.yy.latestTablePrimaries);
     parser.yy.resultStack.push(parser.yy.result);

     parser.yy.result = {};
     parser.yy.latestTablePrimaries = [];
   
break;
case 373:

     if (Object.keys(parser.yy.result).length === 0) {
       parser.yy.result = parser.yy.resultStack.pop();
       parser.yy.latestTablePrimaries = parser.yy.primariesStack.pop();
     }
   
break;
case 377:

     suggestKeywords(['SELECT']);
   
break;
case 378:

      suggestKeywords(['SELECT']);
    
break;
case 386: case 388:

     this.$ = { partial: true }
   
break;
case 387: case 389:

     this.$ = $$[$0]
   
break;
case 391:

     if ($$[$0-1]) {
       this.$ = $$[$0-1].concat($$[$0]);
     } else {
       this.$ = $$[$0];
     }
   
break;
case 392:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 394:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 396:

     this.$ = [{ udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }]
   
break;
case 397:

      this.$ = [{ udtf: $$[$0-1], columnAliases: $$[$0] }]
    
break;
case 398: case 399:

     this.$ = [];
     suggestKeywords(['AS']);
   
break;
case 400:

     this.$ = [];
     suggestKeywords(['explode', 'posexplode']);
   
break;
case 401:

     this.$ = [];
     suggestKeywords(['VIEW']);
   
break;
case 402:

     this.$ = [ $$[$0] ]
   
break;
case 403:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 404:

     if (isHive()) {
       suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
     } else {
       suggestKeywords(['COLUMNS', 'DATABASES', 'TABLES']);
     }
   
break;
case 405:

     if (isImpala()) {
       suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'PARTITIONS', 'TABLE STATS']);
     }
   
break;
case 406:

     if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'DATABASES', 'FUNCTIONS', 'SCHEMAS', 'TABLES']);
     } else if (isHive()) {
       suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
     }
   
break;
case 425: case 517:

     suggestKeywords(['STATS']);
   
break;
case 427: case 519:

     suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
   
break;
case 428: case 429: case 434: case 435: case 477: case 478:

     suggestKeywords(['FROM', 'IN']);
   
break;
case 430: case 431: case 432: case 464: case 474: case 524:

     suggestTables();
   
break;
case 436: case 479: case 489: case 543:

     suggestDatabases();
   
break;
case 440: case 443: case 466:

     suggestKeywords(['TABLE']);
   
break;
case 442:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name);
     }
   
break;
case 444:

     suggestKeywords([ 'ROLES' ]);
   
break;
case 445:

     suggestKeywords([ 'CURRENT' ]);
   
break;
case 447: case 515:

     suggestKeywords(['LIKE']);
   
break;
case 452: case 457:

     suggestKeywords(['FUNCTIONS']);
   
break;
case 454: case 458:

     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   
break;
case 455: case 521:

     if (!$$[$0-1]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 459:

     if (!$$[$0-2]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 460:

     if ($$[$0]) {
       suggestKeywords(['ON']);
     }
   
break;
case 462:

     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   
break;
case 467:

     suggestKeywords(['ROLE']);
   
break;
case 470: case 471:

     this.$ = true;
   
break;
case 480:

     suggestTablesOrColumns($$[$0]);
   
break;
case 482:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
     suggestKeywords(['DATABASE', 'SCHEMA']);
   
break;
case 483:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name)
     }
   
break;
case 484:

      suggestKeywords(['EXTENDED', 'PARTITION']);
    
break;
case 485:

     if ($$[$0-1].partial && $$[$0-1].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-1].identifierChain[0].name)
     }
   
break;
case 486:

     if ($$[$0-4].partial && $$[$0-4].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
     }
   
break;
case 487: case 506: case 514:

     suggestKeywords(['EXTENDED']);
   
break;
case 488:

     // TODO: Move into CleanRegularOrBackTickedSchemaQualifiedName
     if ($$[$0-5].partial && $$[$0-5].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
     }
   
break;
case 492: case 496:

     suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
   
break;
case 493: case 516:

     suggestKeywords(['PARTITION']);
   
break;
case 497: case 498:

     suggestKeywords(['GRANT']);
   
break;
case 499: case 500:

     suggestKeywords(['ROLE', 'USER']);
   
break;
case 502: case 503:

     suggestKeywords(['GROUP']);
   
break;
case 508:

      if ($$[$0-1]) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    
break;
case 510:

      if (isHive())
        suggestKeywords(['EXTENDED']);
      
break;
case 511:

      suggestKeywords(['LIKE']);
    
break;
case 512:

      suggestKeywords(['PARTITION']);
    
break;
case 527:

     suggestKeywords([ 'WHERE' ]);
   
break;
case 529:

     suggestKeywords([ 'SET' ]);
   
break;
case 533:

     // TODO: Replace with TablePrimary?
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 537:

     suggestKeywords([ '=' ]);
   
break;
case 542:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
}
},
table: [o([12,13,26,27,28,29,74,75,194,195,196,201,290,332,341],[2,1],{4:1,3:2}),{1:[3]},{5:3,8:4,9:5,10:6,11:7,12:$V0,13:$V1,14:9,15:10,16:11,17:12,18:13,19:14,20:15,21:16,25:22,26:$V2,27:$V3,28:$V4,29:$V5,73:48,74:$V6,75:$V7,153:20,154:21,192:23,193:24,194:$V8,195:$V9,196:$Va,197:26,198:27,201:$Vb,290:$Vc,292:29,293:30,294:31,295:32,296:33,297:34,298:35,299:36,300:37,301:38,302:39,303:40,304:41,305:42,306:43,307:44,308:45,309:46,332:$Vd,341:$Ve},{6:[1,57],7:[1,58]},o($Vf,[2,4]),o($Vf,[2,6]),o($Vf,[2,7]),o($Vf,[2,8]),{13:[1,59]},o($Vf,[2,11]),o($Vf,[2,12]),o($Vf,[2,13]),o($Vf,[2,14]),o($Vf,[2,15]),o($Vf,[2,16]),o($Vf,[2,17]),o($Vf,[2,18]),{2:[1,61],12:$Vg,13:$V1,14:66,29:$V5,150:65,202:60,215:62,247:[1,63],248:64},o($Vh,[2,24]),o($Vh,[2,25]),o($Vf,[2,166]),o($Vf,[2,167]),{29:[1,68],37:70,38:$Vi,39:$Vj,40:$Vk,48:71,49:$Vl,50:$Vm,70:72,71:[1,78],72:[1,79],167:69},o($Vf,[2,227]),o($Vf,[2,228]),{29:[1,80],37:82,38:$Vi,39:$Vj,40:$Vk,48:81,49:$Vl,50:$Vm},o($Vf,[2,234]),o($Vf,[2,235]),{22:93,23:[1,115],24:[1,116],27:[1,108],28:[1,109],29:[1,83],39:[1,103],40:[1,104],52:118,53:$Vn,54:$Vo,58:88,59:89,60:[1,110],61:[1,111],65:90,66:[1,112],67:[1,113],68:[1,91],69:[1,114],90:101,91:[1,119],92:[1,120],95:[1,102],96:105,97:[1,121],98:[1,122],116:94,120:[1,117],123:97,310:[1,84],316:[1,85],317:[1,86],318:[1,87],319:[1,92],320:[2,89],322:[1,95],325:[1,96],326:[1,98],328:[1,99],329:[1,100],330:[1,106],331:[1,107]},o($Vf,[2,407]),o($Vf,[2,408]),o($Vf,[2,409]),o($Vf,[2,410]),o($Vf,[2,411]),o($Vf,[2,412]),o($Vf,[2,413]),o($Vf,[2,414]),o($Vf,[2,415]),o($Vf,[2,416]),o($Vf,[2,417]),o($Vf,[2,418]),o($Vf,[2,419]),o($Vf,[2,420]),o($Vf,[2,421]),o($Vf,[2,422]),o($Vf,[2,423]),o($Vf,[2,424]),{12:[1,125],29:[1,126]},{29:[1,128],62:127,63:[1,129],64:[1,130]},{12:$Vp,29:[1,132],137:138,139:$Vq,149:136,151:134,333:131,336:133},o($Vr,[2,21]),o($Vr,[2,22]),o($Vr,[2,23]),o($Vs,[2,93],{119:139,48:140,49:$Vl,50:$Vm,118:[1,141],120:[1,142]}),o($Vs,[2,96],{121:143,122:[1,144]}),o($Vt,[2,60]),o($Vt,[2,61]),{7:[1,145],8:146,9:5,10:6,11:7,12:$V0,13:$V1,14:9,15:10,16:11,17:12,18:13,19:14,20:15,21:16,25:22,26:$V2,27:$V3,28:$V4,29:$V5,73:48,74:$V6,75:$V7,153:20,154:21,192:23,193:24,194:$V8,195:$V9,196:$Va,197:26,198:27,201:$Vb,290:$Vc,292:29,293:30,294:31,295:32,296:33,297:34,298:35,299:36,300:37,301:38,302:39,303:40,304:41,305:42,306:43,307:44,308:45,309:46,332:$Vd,341:$Ve},{1:[2,3]},o($Vf,[2,10],{12:[1,147]}),{29:[1,149],35:$Vu,203:148,204:150},{35:$Vu,203:152,204:150},o($Vv,[2,313],{147:$Vw}),o($Vv,[2,314]),o($Vx,[2,315]),o($Vx,[2,318],{30:154,13:[1,155],31:$Vy,32:$Vz,33:$VA}),o($Vx,[2,325]),o($VB,[2,146],{81:159,82:$VC,83:$VD}),o($Vf,[2,168],{37:162,38:$Vi,39:$Vj,40:$Vk}),{37:163,38:$Vi,39:$Vj,40:$Vk},{12:[1,164]},o($VE,[2,110],{132:165,29:[1,166],130:[1,167]}),o($VF,[2,197]),o($VG,[2,31]),o($VG,[2,32]),o($VG,[2,33]),o($VH,[2,40]),o($VH,[2,41]),o($VF,[2,58]),o($VF,[2,59]),o($Vf,[2,233]),o($VI,$VJ,{129:168,130:$VK}),o($VI,$VJ,{129:170,130:$VK}),o($Vf,[2,404],{137:138,148:171,93:173,52:175,149:177,12:$VL,53:$Vn,54:$Vo,94:$VM,95:$VN,139:$Vq,291:[1,172],320:[1,174]}),{29:[1,180],311:[1,181]},{29:[1,182],34:183,35:$VO,36:$VP},o($Vf,[2,438]),{12:[1,187],29:[1,188],135:186},{29:[1,189],37:190,38:$Vi,39:$Vj,40:$Vk},{29:[1,191],93:192,94:$VM,95:$VN},{29:[1,193],291:[1,194]},o($VQ,[2,56],{104:195,105:$VR}),o($Vf,[2,450],{107:197,108:$VS}),{29:[1,199],320:[2,90]},{320:[1,200]},o($VT,[2,468],{323:201,12:[1,202],29:[1,203]}),{29:[1,204]},o($Vf,[2,472],{29:[1,205],266:[1,206]}),{12:$VL,29:[1,207],48:209,49:$Vl,50:$Vm,137:138,139:$Vq,148:208,149:177},{12:$VL,29:[1,210],137:138,139:$Vq,148:211,149:177},{12:$VL,29:[1,212],137:138,139:$Vq,148:213,149:177},{29:[1,214],322:[1,215],325:[1,216]},o($Vf,[2,505]),{29:[1,217],118:[1,218]},{29:[1,219],311:[1,220]},o($VU,$VV,{134:221,76:222,36:$VW,77:$VX}),{29:[1,225]},o($Vf,[2,525]),o($VY,[2,48]),o($VY,[2,49]),o($VZ,[2,50]),o($VZ,[2,51]),o($VQ,[2,54]),o($VQ,[2,55]),o($VQ,[2,57]),o($V_,[2,19]),o($V_,[2,20]),{29:[1,227],52:226,53:$Vn,54:$Vo},o($V$,[2,101]),o($V01,[2,72]),o($V01,[2,73]),o($V11,[2,76]),o($V11,[2,77]),o($V$,[2,44]),o($V$,[2,45]),o($Vf,[2,542]),o($Vf,[2,543]),{29:[1,229],78:228,79:[1,230],80:[1,231]},o($Vf,[2,249]),o($V21,[2,52]),o($V21,[2,53]),o($Vf,[2,530],{29:[1,233],334:[1,232]}),o($Vf,[2,531]),o($V31,[2,532]),o($V31,[2,533]),o($V31,[2,160],{30:235,12:[1,234],31:$Vy,32:$Vz,33:$VA}),o($V31,$V41,{12:[1,236]}),{106:[1,237],140:$V51},o($V61,[2,158]),{12:$V71,29:$V81,136:240,137:243,139:$V91,142:241,143:239},o($Vs,[2,91],{117:246,118:[1,247]}),o($Vs,[2,94]),o($Vs,[2,95]),{12:$V71,29:[1,249],137:250,139:$V91,141:248,142:251},o($Vs,[2,97]),{1:[2,2]},o($Vf,[2,5]),o($Vf,[2,9]),o($Va1,[2,250]),o($Va1,[2,252]),o($Vb1,[2,259],{205:252,207:253,212:[1,254]}),{12:$V71,29:$Vc1,137:250,139:$V91,141:263,142:251,161:$Vd1,206:255,240:264,249:256,250:257,251:259,252:260,270:261,273:262},o($Va1,[2,251]),{2:[1,267],12:$Vg,13:$V1,14:66,29:$V5,150:65,248:266},{12:$Vg,13:$Ve1,137:272,138:268,139:$Vf1,150:273,152:270,247:[1,269]},o($Vx,[2,320]),o($Vg1,[2,26]),o($Vg1,$Vh1),o($Vg1,$Vi1),{87:277,88:$Vj1,89:$Vk1,102:[1,276],107:275,108:$VS},o($Vl1,[2,66]),o($Vl1,[2,67]),o($Vf,[2,194],{12:[1,280]}),{12:[1,281]},{161:$Vm1,168:282},o($Vf,[2,186],{12:[1,284]}),o($VE,[2,111]),{29:[1,285],133:[1,286]},o($Vf,[2,236],{142:288,12:$V71,29:[1,287],139:$Vn1}),{29:[1,290],131:[1,291]},o($Vf,[2,240],{149:136,137:138,199:293,151:294,12:$Vp,29:[1,292],139:$Vq}),o($Vf,[2,405]),{104:295,105:$VR},o($Vf,[2,445]),o([6,7,291],$VV,{76:222,134:296,36:$VW,77:$VX}),o($V$,[2,100]),o($Vo1,[2,144],{30:235,31:$Vy,32:$Vz,33:$VA}),o($Vo1,[2,145]),o($Vf,[2,74]),o($Vf,[2,75]),o($Vf,[2,425]),{12:$VL,29:[1,297],137:138,139:$Vq,148:298,149:177},o($Vf,[2,428],{142:299,12:$V71,139:$Vn1}),{12:$V71,29:[1,300],139:$Vn1,142:301},o($VI,$Vp1),o($VI,[2,30]),o($Vf,[2,439],{33:[1,302]}),o($Vq1,[2,117]),o($Vq1,[2,118]),o($Vf,[2,440],{137:138,149:177,148:303,12:$VL,139:$Vq}),{12:$VL,29:[1,304],137:138,139:$Vq,148:305,149:177},o($Vf,[2,444]),o($Vf,[2,446]),o($Vf,[2,447]),{104:306,105:$VR},o($Vf,[2,449]),{106:[1,307]},o($Vf,[2,451]),{106:[1,308]},o($Vf,[2,452],{76:222,134:309,36:$VW,77:$VX,291:$VV}),o($Vr1,$VV,{76:222,134:310,36:$VW,77:$VX}),o($Vf,[2,460],{266:[1,311]}),o($VT,[2,469],{29:[1,312]}),o($VT,[2,470]),o($Vf,[2,467]),o($Vf,[2,473],{142:313,12:$V71,139:$Vn1}),{12:$V71,29:[1,314],139:$Vn1,142:315},o($Vf,[2,482]),o($Vf,[2,483],{29:[1,316],118:[1,317],327:[1,318]}),{12:$V71,29:[1,319],139:$Vn1,142:320},o($Vf,[2,491]),{29:[1,322],312:[1,321],327:[1,323]},o($Vf,[2,495]),{312:[1,324]},o($Vf,[2,497],{99:325,91:$Vs1,100:$Vt1}),{29:[1,328],91:$Vs1,99:329,100:$Vt1},{29:[1,330],115:[1,331]},o($Vf,[2,506],{124:332,51:333,35:$Vu1,36:$Vv1,291:$Vw1}),o($Vr1,$Vw1,{51:333,124:336,35:$Vu1,36:$Vv1}),o($Vf,[2,517]),{12:$VL,29:[1,337],137:138,139:$Vq,148:338,149:177},o($Vf,[2,520],{104:340,29:[1,339],105:$VR,291:[1,341]}),{12:$V71,29:$V81,125:342,136:343,137:243,139:$V91,142:344},o($Vs,[2,62]),o($Vs,[2,63]),o($Vf,[2,524]),o($V$,[2,98]),o($V$,[2,99]),{188:345,189:$Vx1},o($Vf,[2,248]),{189:[2,64]},{189:[2,65]},{12:$Vy1,29:$Vz1,335:347,337:348,338:349},o($Vf,[2,529]),o($V31,[2,161]),{12:[1,352],13:$Ve1,137:272,138:354,139:[1,353]},o($V31,[2,163]),{139:[1,355]},o([2,6,7,12,29,31,32,33,35,105,110,111,113,114,115,118,139,147,162,212,216,217,255,257,258,260,261,263,264,266,287,291,312,327,334],[2,125]),o($Vf,[2,229],{30:356,31:$Vy,32:$Vz,33:$VA}),o($VA1,[2,133]),o($VA1,$VB1,{144:357,81:358,82:$VC,83:$VD}),o($VC1,[2,121]),o($VC1,[2,122]),o($VD1,[2,150]),{106:$VE1,140:$V51},{12:$V71,29:$V81,125:360,136:343,137:243,139:$V91,142:344},o($Vs,[2,92]),o($Vf,[2,231]),o($Vf,[2,232]),o($VF1,[2,126],{30:361,31:$Vy,32:$Vz,33:$VA}),o($VF1,[2,127],{30:362,31:$Vy,32:$Vz,33:$VA}),o($Va1,[2,253],{29:[1,363]}),o($VG1,[2,262],{208:364,112:365,113:[1,366],114:[1,367],115:[1,368]}),o($VH1,$VI1,{213:369,218:371,219:372,221:373,223:375,224:376,229:377,230:378,231:379,232:380,235:381,236:382,237:383,241:385,101:386,104:387,242:388,243:391,29:[1,370],102:$VJ1,103:$VK1,105:$VR,133:$VL1,161:$VM1}),o([2,6,7,29,113,114,115,162,212,216,217],[2,255],{147:[1,392]}),o($VN1,[2,326]),o($VN1,[2,328]),o($VN1,[2,329]),o($VN1,[2,330],{253:393,254:394,255:$VO1,257:$VP1,258:$VQ1,260:$VR1,261:$VS1,263:$VT1,264:$VU1}),o($VN1,[2,331]),o($VV1,$VW1,{271:401,137:402,142:403,109:404,12:$V71,110:$VX1,111:$VY1,139:$V91}),o($VZ1,$VW1,{137:402,142:403,109:404,271:407,12:$V71,110:$VX1,111:$VY1,139:$V91}),o($VF1,[2,370]),o([2,6,7,12,29,110,111,113,114,115,139,147,162,212,216,217,255,257,258,260,261,263,264,266],[2,371]),o([13,29,201],[2,372],{274:408}),o($Vx,[2,316]),o($Vx,[2,317]),o($Vx,[2,319]),o($Vx,[2,321]),o($Vx,[2,322],{30:411,31:$Vy,32:[1,409],33:[1,410]}),o($V_1,[2,123]),o($V_1,[2,124]),o($V$1,[2,164]),{140:$V51},{87:412,88:$Vj1,89:$Vk1},{87:413,88:$Vj1,89:$Vk1},o($VB,[2,149]),o($VB,[2,70]),o($VB,[2,71]),o($Vf,[2,193],{168:414,161:$Vm1}),{161:$Vm1,168:415},o($Vf,[2,196]),{12:$V02,169:416,170:417,171:418},o([56,57,85,86,159],[2,185],{166:421,6:$V12,7:$V12,29:[1,420]}),o($VE,[2,112]),{29:[1,422],131:[1,423]},o($Vf,[2,237]),o($Vf,[2,104],{126:425,29:[1,424],127:[1,426],128:[1,427]}),{106:$VE1},o($VI,[2,108]),o($VI,[2,109]),o($Vf,[2,241]),o($Vf,[2,242],{29:[1,428]}),o([6,7,29],[2,367]),o($Vf,[2,406]),o($Vf,[2,454],{291:[1,429]}),o($Vf,[2,426]),{312:[1,430]},o($Vf,[2,429]),o($Vf,[2,430],{34:431,35:$VO,36:$VP}),o($Vf,[2,433],{34:433,29:[1,432],35:$VO,36:$VP}),{12:[1,434],13:[1,435]},o($Vf,[2,443]),o($Vf,[2,441]),o($Vf,[2,442]),o($Vf,[2,448]),{105:[1,436]},{108:[1,437]},{291:[1,438]},o($Vf,[2,453],{29:[1,439],291:[1,440]}),{12:$V71,29:[1,442],37:444,38:$Vi,39:$Vj,40:$Vk,139:$Vn1,142:443,324:[1,441]},o($VT,[2,471]),o($Vf,[2,475]),o($Vf,[2,474],{34:445,35:$VO,36:$VP}),o($Vf,[2,476],{34:447,29:[1,446],35:$VO,36:$VP}),o($Vf,[2,484]),o($Vf,[2,485]),{161:[1,448]},o($Vf,[2,489]),o($Vf,[2,490]),{313:[1,449]},o($Vf,[2,493]),{12:$V22,145:450,146:451},{313:[1,453]},{12:[1,454]},{12:[2,78]},{12:[2,79]},o($Vf,[2,499],{12:[1,455]}),{12:[1,456]},o($Vf,[2,502],{12:[1,457]}),{12:[1,458]},{291:[1,459]},{12:$V71,29:$V81,125:460,136:343,137:243,139:$V91,142:344},o($Vs,[2,42]),o($Vs,[2,43]),o($Vf,[2,507],{29:[1,461],291:[1,462]}),o($Vf,[2,518]),{312:[1,463]},o($Vf,[2,521]),o($Vf,[2,522]),{104:464,105:$VR},o($VU,[2,116]),o($VU,[2,131]),o($VU,[2,132]),o($Vf,[2,247],{29:[1,466],200:[1,465]}),{13:[1,468],190:[1,467]},o($Vf,[2,528],{211:469,29:[1,470],147:[1,471],212:[1,472]}),o($V32,[2,534]),{29:[1,474],42:[1,473]},o($V32,[2,538]),o([29,42],[2,539]),o($V61,[2,152]),{106:[1,475],140:$V51},o($V61,[2,157]),o($V61,[2,159],{30:476,31:$Vy,32:$Vz,33:$VA}),{12:$V71,13:$Ve1,137:272,138:477,139:$V91,142:478},o($VA1,[2,134]),{87:481,88:$Vj1,89:$Vk1,102:[1,480],107:479,108:$VS},{139:[1,482]},o($Vf,[2,230]),{12:$V71,139:$Vn1,142:483},{12:$V71,13:$Ve1,137:272,138:484,139:$V91,142:485},o($Va1,[2,254]),o($V42,[2,265],{209:486,216:[1,487]}),{29:[1,489],214:[1,488]},o($V52,[2,86]),o($V52,[2,87]),o($V52,[2,88]),o($Vb1,[2,260]),o($Vb1,[2,261]),o($Vb1,[2,271],{220:$V62}),o($V72,[2,272]),o($V72,[2,274],{222:[1,491]}),o($VH1,$VI1,{224:376,229:377,230:378,231:379,232:380,235:381,236:382,237:383,241:385,101:386,104:387,242:388,243:391,223:492,102:$VJ1,103:$VK1,105:$VR,161:$VM1}),o($V82,[2,278]),o($V82,[2,280],{225:493,226:[1,494]}),o($V92,[2,284]),o($V92,[2,285],{41:495,238:496,227:503,36:$Va2,77:$Va2,234:$Va2,42:[1,497],43:[1,498],44:[1,499],45:[1,500],46:[1,501],47:[1,502],133:$Vb2}),o($V92,[2,286]),o($V92,[2,287]),o($Vc2,[2,293]),o($Vc2,[2,294]),o($Vc2,[2,295]),o($VH1,$VI1,{219:372,221:373,223:375,224:376,229:377,230:378,231:379,232:380,235:381,236:382,237:383,241:385,101:386,104:387,242:388,243:391,218:505,14:506,13:$V1,29:$V5,102:$VJ1,103:$VK1,105:$VR,133:$VL1,161:$VM1}),o($Vc2,[2,303]),o($Vc2,[2,296]),o($Vc2,[2,297]),o($Vd2,[2,304]),o($Vc2,[2,80]),{102:[1,507]},{12:$Vg,150:510,244:508,245:509,246:$Ve2},{12:$V71,29:$Vc1,137:250,139:$V91,141:263,142:251,161:$Vd1,240:264,249:512,250:257,251:259,252:260,270:261,273:262},o($VN1,[2,332],{254:513,255:$VO1,257:$VP1,258:$VQ1,260:$VR1,261:$VS1,263:$VT1,264:$VU1}),{255:[1,514]},{255:[2,341]},o($Vf2,$Vg2,{259:515,265:$Vh2}),{255:[2,344]},o($Vf2,$Vg2,{259:517,262:[1,518],265:$Vh2}),o($Vf2,$Vg2,{259:519,265:$Vh2}),o($Vf2,$Vg2,{259:520,262:[1,521],265:$Vh2}),o($VV1,[2,390],{272:522}),o($VV1,[2,386]),o($VV1,[2,387]),{12:$V71,137:523,139:$V91,142:524},o($Vi2,[2,84]),o($Vi2,[2,85]),o($VZ1,[2,369]),{11:534,13:[1,528],29:[1,527],201:$Vb,276:525,277:526,278:529,279:530,280:531,281:532,282:533},{12:$Vh1,13:[1,535]},{12:$Vi1,13:[1,536]},{12:$Vg,150:537},o($VB,[2,147]),o($VB,[2,148]),o($Vf,[2,192]),{29:[1,539],84:540,85:$Vj2,86:$Vk2,165:538},{147:[1,544],162:[1,543]},o($Vl2,[2,199]),o($Vl2,[2,201]),{29:[1,546],172:545,174:[1,547],175:[1,548],176:[1,549],177:[1,550],178:[1,551],179:[1,552],180:[1,553],181:[1,554],182:[1,555],183:[1,556],184:[1,557],185:[1,558],186:[1,559],187:[1,560]},o($Vf,[2,188]),{55:566,56:$Vm2,57:$Vn2,84:540,85:$Vj2,86:$Vk2,155:563,158:565,159:$Vo2,163:561,164:562,165:564},o($VE,[2,113]),o($VE,[2,114]),o($Vf,[2,238]),o($Vf,[2,239]),o($Vf,[2,105]),o($Vf,[2,106]),o($Vf,[2,243]),{321:[1,570]},{313:[1,571]},o($Vf,[2,431],{142:572,12:$V71,139:$Vn1}),o($Vf,[2,434],{142:573,12:$V71,139:$Vn1}),{12:$V71,29:[1,574],139:$Vn1,142:575},o($Vq1,[2,119]),o($Vq1,[2,120]),o([2,6,7,29,36,42,43,44,45,46,47,77,113,114,115,133,147,162,212,216,217,220,222,226,234,327],[2,82]),o([6,7,88,89],[2,83]),{321:[1,576]},o($Vf,[2,455],{321:[1,577]}),{321:[1,578]},o($Vf,[2,461]),o($Vf,[2,462],{142:579,12:$V71,139:$Vn1}),o($Vf,[2,463]),{12:$V71,29:[1,580],139:$Vn1,142:581},{12:$V71,139:$Vn1,142:582},o($Vf,[2,477],{142:583,12:$V71,139:$Vn1}),{12:$V71,29:[1,584],139:$Vn1,142:585},{12:$V22,145:586,146:451},{314:[1,587]},o($Vf,[2,494],{147:$Vp2}),o($Vq2,[2,141]),{42:[1,589]},{314:[1,590]},o($Vf,[2,498]),o($Vf,[2,500]),o($Vf,[2,501]),o($Vf,[2,503]),o($Vf,[2,504]),{104:591,105:$VR},o($Vr1,[2,103]),o($Vf,[2,508],{104:592,105:$VR}),{104:593,105:$VR},{313:[1,594]},o($Vf,[2,523]),{29:[1,596],37:595,38:$Vi,39:$Vj,40:$Vk},o($Vf,[2,246]),{13:[1,598],191:[1,597]},o($Vr2,[2,226],{191:[1,599]}),o($Vf,[2,526]),o($Vf,[2,527]),{12:$Vy1,29:$Vz1,337:600,338:349},o($VH1,$VI1,{218:371,219:372,221:373,223:375,224:376,229:377,230:378,231:379,232:380,235:381,236:382,237:383,241:385,101:386,104:387,242:388,243:391,213:601,29:[1,602],102:$VJ1,103:$VK1,105:$VR,133:$VL1,161:$VM1}),o($VH1,$VI1,{219:372,221:373,223:375,224:376,229:377,230:378,231:379,232:380,235:381,236:382,237:383,241:385,101:386,104:387,242:388,243:391,339:603,340:604,218:605,102:$VJ1,103:$VK1,105:$VR,133:$VL1,161:$VM1}),o($V32,[2,537]),{139:[1,606]},{12:[1,607],13:$Ve1,137:272,138:609,139:[1,608]},o($VA1,[2,135]),o($VA1,$VB1,{81:358,144:610,82:$VC,83:$VD}),{87:611,88:$Vj1,89:$Vk1},{87:612,88:$Vj1,89:$Vk1},o($VA1,[2,140]),o($VD1,[2,151]),o($VF1,[2,128]),o($VF1,[2,129]),o($VF1,[2,130]),o($Vs2,[2,268],{210:613,217:[1,614]}),{29:[1,616],214:[1,615]},{12:$Vg,13:$V1,14:66,29:$V5,150:65,215:617,248:64},o($VG1,[2,264]),o($VH1,$VI1,{221:373,223:375,224:376,229:377,230:378,231:379,232:380,235:381,236:382,237:383,241:385,101:386,104:387,242:388,243:391,219:618,102:$VJ1,103:$VK1,105:$VR,133:$VL1,161:$VM1}),o($VH1,$VI1,{221:373,223:375,224:376,229:377,230:378,231:379,232:380,235:381,236:382,237:383,241:385,101:386,104:387,242:388,243:391,219:620,29:[1,619],102:$VJ1,103:$VK1,105:$VR,133:$VL1,161:$VM1}),o($V82,[2,277]),o($V82,[2,279]),{133:$Vb2,227:621,228:$Va2},o($VH1,$VI1,{235:381,236:382,237:383,241:385,101:386,104:387,242:388,243:391,230:622,14:623,13:$V1,29:$V5,102:$VJ1,103:$VK1,105:$VR,161:$VM1}),o($V92,[2,298]),o($Vt2,[2,34]),o($Vt2,[2,35]),o($Vt2,[2,36]),o($Vt2,[2,37]),o($Vt2,[2,38]),o($Vt2,[2,39]),{36:[1,626],77:[1,627],233:624,234:[1,625]},o([36,77,228,234],[2,283]),{162:[1,628],220:$V62},o($Vc2,[2,302]),o($Vc2,[2,81]),o($Vd2,[2,305],{30:629,31:$Vy,32:$Vz,33:$VA}),o($Vu2,[2,307]),o($Vu2,[2,310],{13:[1,630]}),{12:[1,631]},o($VN1,[2,327]),{255:[1,632]},{2:[1,635],12:$V71,29:[1,634],137:250,139:$V91,141:263,142:251,161:$Vd1,240:264,251:633,270:261,273:262},{29:[1,636],255:[2,342]},o($Vf2,[2,354]),{29:[1,637],255:[2,347]},{255:[2,346]},{29:[1,638],255:[2,348]},{29:[1,639],255:[2,352]},{255:[2,351]},o($VZ1,[2,368],{283:640,287:[1,641]}),o($VV1,[2,388]),o($VV1,[2,389]),{2:[1,643],162:[2,373],275:642},o($V41,[2,376]),o($V41,[2,377]),o($V41,[2,378]),o($V41,[2,379]),o($V41,[2,380]),o($V41,[2,381]),o($V41,[2,382]),o($V41,[2,383]),o($V41,[2,384]),o($Vx,[2,323]),o($Vx,[2,324]),o($V$1,[2,165]),o($Vf,[2,191]),o($Vf,[2,195]),{188:644,189:$Vx1},{189:[2,68]},{189:[2,69]},o([6,7,29,85,86],[2,198]),{12:$V02,170:645,171:418},o($Vl2,[2,202]),o($Vl2,[2,203],{173:646,2:[2,219]}),o($Vl2,[2,205]),o($Vl2,[2,206]),o($Vl2,[2,207]),o($Vl2,[2,208]),o($Vl2,[2,209]),o($Vl2,[2,210]),o($Vl2,[2,211]),o($Vl2,[2,212]),o($Vl2,[2,213]),o($Vl2,[2,214]),o($Vl2,[2,215]),o($Vl2,[2,216]),o($Vl2,[2,217]),o($Vl2,[2,218]),{2:[1,647],29:[1,648]},o($Vp1,[2,179],{84:540,155:563,165:564,158:565,55:566,164:649,56:$Vm2,57:$Vn2,85:$Vj2,86:$Vk2,159:$Vo2}),o($Vv2,[2,182]),o($Vv2,[2,183]),o($Vv2,[2,184]),{105:[1,650]},{29:[1,652],160:[1,651]},{105:[2,46]},{105:[2,47]},o($Vf,[2,458]),{314:[1,653]},o($Vf,[2,432]),o($Vf,[2,435]),o($Vf,[2,436]),o($Vf,[2,437]),o($Vf,[2,457]),o($Vf,[2,459]),o($Vf,[2,456]),o($Vf,[2,466]),o($Vf,[2,464]),o($Vf,[2,465]),o($Vf,[2,480]),o($Vf,[2,478]),o($Vf,[2,479]),o($Vf,[2,481]),{147:$Vp2,162:[1,654]},{315:[1,655]},{12:$V22,146:656},{104:657,105:$VR},{315:[1,658]},o($Vf,[2,510],{327:[1,659]}),o($Vf,[2,511],{327:[1,660]}),o($Vf,[2,509],{29:[1,661],327:[1,662]}),{314:[1,663]},{12:[1,664]},o($Vf,[2,245]),o($Vr2,[2,221]),o($Vr2,[2,224],{190:[1,665],191:[1,666]}),o($Vr2,[2,225]),o($V32,[2,535]),o($Vf,[2,257]),o($Vf,[2,258]),o($V32,[2,536]),o($V32,[2,540]),o($V32,[2,541],{220:$V62}),o($V61,[2,154]),o($V61,[2,153]),{106:[1,667],140:$V51},o($V61,[2,156]),o($VA1,[2,136]),o($VA1,[2,138]),o($VA1,[2,139]),o($Vs2,[2,256]),{29:[1,669],102:[1,668]},{12:$Vg,13:$V1,14:66,29:$V5,150:65,215:670,248:64},o($V42,[2,267]),o($VG1,[2,263],{147:$Vw}),o($V72,[2,273]),o($V72,[2,275]),o($V72,[2,276]),{228:[1,671]},o($V92,[2,291]),o($V92,[2,292]),{161:$Vd1,239:672,240:673},{161:[2,288]},{161:[2,289]},{161:[2,290]},o($Vc2,[2,301]),{12:$Vg,13:[1,674],150:510,245:675,246:$Ve2},o($Vu2,[2,311]),{246:[1,676]},{12:$V71,29:[1,678],137:250,139:$V91,141:263,142:251,161:$Vd1,240:264,251:677,270:261,273:262},{29:[1,680],256:679,266:$Vw2},o($Vx2,[2,335]),o($Vx2,[2,336]),{255:[2,343]},{255:[2,345]},{255:[2,349]},{255:[2,350]},o($VV1,[2,391]),{29:[1,683],288:[1,682]},{162:[1,684]},o($Vy2,[2,375]),o([2,6,7,29,56,57,85,86,159],[2,220]),o($Vl2,[2,200]),{2:[1,685]},o($Vf,[2,189]),o($Vf,[2,190]),o($Vp1,[2,180],{84:540,155:563,165:564,158:565,55:566,164:686,56:$Vm2,57:$Vn2,85:$Vj2,86:$Vk2,159:$Vo2}),o($Vv2,[2,169],{106:[1,687]}),o($Vv2,[2,177],{161:[1,688]}),o($Vv2,[2,178]),{315:[1,689]},o($Vf,[2,486],{29:[1,690],118:[1,691]}),o($Vf,[2,492]),o($Vq2,[2,142]),o($Vq2,[2,143]),o($Vf,[2,496]),{12:$V22,145:692,146:451},{12:$V22,145:693,146:451},o($Vf,[2,512],{146:451,145:694,12:$V22}),{12:$V22,145:695,146:451},{315:[1,696]},o($Vf,[2,244]),{191:[1,697]},o($Vr2,[2,223]),{139:[1,698]},o($Vs2,[2,269]),o($Vs2,[2,270]),o($V42,[2,266],{147:$Vw}),o($V82,[2,281]),o($V92,[2,299]),o($V92,[2,300]),o($Vu2,[2,308]),o($Vu2,[2,309]),o($Vu2,[2,312]),o($Vx2,[2,337],{256:699,266:$Vw2}),o($Vx2,[2,339]),o($Vx2,[2,333]),o($Vx2,[2,334]),o($VH1,$VI1,{242:388,243:391,267:700,268:701,269:702,241:704,13:$Vz2,29:$VA2,161:[1,703]}),{29:[1,708],284:707,285:[1,709],286:[1,710]},o($VV1,[2,401]),o($Vy2,[2,374]),o($Vl2,[2,204]),o($Vp1,[2,181]),o($Vv2,[2,170],{105:[1,711]}),{12:$VB2,105:$VC2,156:712,157:713},o($Vf,[2,427]),o($Vf,[2,487]),o($Vf,[2,488]),o($Vf,[2,514],{147:$Vp2}),o($Vf,[2,515],{147:$Vp2}),o($Vf,[2,516],{147:$Vp2}),o($Vf,[2,513],{147:$Vp2}),o($Vf,[2,519]),o($Vr2,[2,222]),o($V61,[2,155]),o($Vx2,[2,338]),o($Vx2,[2,355],{222:$VD2}),o($Vx2,[2,356]),o($VE2,[2,359]),o($VH1,$VI1,{242:388,243:391,269:702,241:704,267:717,13:$Vz2,29:$VA2}),o($VE2,[2,362],{42:[1,718]}),o($VE2,[2,365]),o($VE2,[2,366]),{12:[1,719],29:[1,721],111:$VF2,289:720},o($VV1,[2,400]),{161:[1,723]},{161:[1,724]},o($Vv2,[2,171]),{147:[1,726],162:[1,725]},o($Vl2,[2,172]),{42:[1,727]},{106:[1,728]},o($VH1,$VI1,{242:388,243:391,241:704,269:729,13:$Vz2,29:$VA2}),{2:[1,731],162:[1,730],222:$VD2},o($VH1,$VI1,{242:388,243:391,241:732,13:[1,734],29:[1,733]}),{29:[1,736],111:$VF2,289:735},o($VV1,[2,397]),o($VV1,[2,399]),{12:[1,737],161:[1,738]},{12:$Vg,13:$Ve1,137:272,138:740,139:$Vf1,150:273,152:739},{12:$Vg,13:$Ve1,137:272,138:742,139:$Vf1,150:273,152:741},o($Vv2,[2,176]),{12:$VB2,105:$VC2,157:743},{12:[1,744]},{105:[1,745]},o($VE2,[2,360]),o($Vx2,[2,357]),o($Vx2,[2,358]),o($VE2,[2,361]),o($VE2,[2,363]),o($VE2,[2,364]),o($VV1,[2,396]),o($VV1,[2,398]),o($VV1,[2,402]),{12:[1,746]},{30:411,31:$Vy,32:$Vz,33:$VA,162:[1,747]},{2:[1,748]},{30:411,31:$Vy,32:$Vz,33:$VA,162:[1,749]},{2:[1,750]},o($Vl2,[2,173]),o($Vl2,[2,174]),{42:[1,751]},{147:[1,752]},o($VG2,[2,392]),o($VG2,[2,393]),o($VG2,[2,394]),o($VG2,[2,395]),{105:[1,753]},{12:[1,754]},{106:[1,755]},{162:[1,756]},{105:[1,757]},o($VV1,[2,403]),o($Vl2,[2,175])],
defaultActions: {58:[2,3],145:[2,2],230:[2,64],231:[2,65],326:[2,78],327:[2,79],395:[2,341],397:[2,344],518:[2,346],521:[2,351],541:[2,68],542:[2,69],568:[2,46],569:[2,47],625:[2,288],626:[2,289],627:[2,290],636:[2,343],637:[2,345],638:[2,349],639:[2,350]},
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

parser.identifyPartials = function (beforeCursor, afterCursor) {
  var beforeMatch = beforeCursor.match(/[a-zA-Z_]*$/);
  var afterMatch = afterCursor.match(/^[a-zA-Z_]*/);
  return { left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0}
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

  identifierChain.concat();
  tablePrimaries.concat();

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
    if (typeof tablePrimaries[0].identifierChain !== 'undefined') {
      if (tablePrimaries[0].identifierChain.length == 2) {
        suggestion.database = tablePrimaries[0].identifierChain[0].name;
        suggestion.table = tablePrimaries[0].identifierChain[1].name;
      } else {
        suggestion.table = tablePrimaries[0].identifierChain[0].name;
      }
    } else if (typeof tablePrimaries[0].subqueryAlias !== 'undefined') {
      suggestTablePrimariesAsIdentifiers();
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
    } else if (typeof tablePrimary.identifierChain !== 'undefined' && tablePrimary.identifierChain.length == 2) {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.identifierChain[0].name + '.' + tablePrimary.identifierChain[1].name + '.', type: 'table' });
    } else if (typeof tablePrimary.identifierChain !== 'undefined') {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.identifierChain[0].name + '.', type: 'table' });
    } else if (typeof tablePrimary.subqueryAlias !== 'undefined') {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.subqueryAlias + '.', type: 'subquery' });
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

  var partialLengths = parser.identifyPartials(beforeCursor, afterCursor);

  if (partialLengths.left > 0) {
    beforeCursor = beforeCursor.substring(0, beforeCursor.length - partialLengths.left);
  }

  if (partialLengths.right > 0) {
    afterCursor = afterCursor.substring(partialLengths.right);
  }

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
  prioritizeSuggestions();

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
case 5: return 111; 
break;
case 6: return 324; 
break;
case 7: return 186; 
break;
case 8: return 316; 
break;
case 9: return 56; 
break;
case 10: return 317; 
break;
case 11: return 318; 
break;
case 12: determineCase(yy_.yytext); return 27; 
break;
case 13: return 257; 
break;
case 14: return 60; 
break;
case 15: return 63; 
break;
case 16: return 66; 
break;
case 17: return 187; 
break;
case 18: determineCase(yy_.yytext); return 194; 
break;
case 19: return 118; 
break;
case 20: return 71; 
break;
case 21: return 120; 
break;
case 22: return '<hive>FUNCTION'; 
break;
case 23: return 319; 
break;
case 24: return 322; 
break;
case 25: return 36; 
break;
case 26: return 53; 
break;
case 27: return 54; 
break;
case 28: this.begin('hdfs'); return 79; 
break;
case 29: return 287; 
break;
case 30: return 74; 
break;
case 31: this.begin('hdfs'); return 85; 
break;
case 32: return 326; 
break;
case 33: return '<hive>MACRO'; 
break;
case 34: return 327; 
break;
case 35: return 328; 
break;
case 36: return 91; 
break;
case 37: return 94; 
break;
case 38: return 67; 
break;
case 39: return 39; 
break;
case 40: return 97; 
break;
case 41: return 330; 
break;
case 42: return '<hive>TEMPORARY'; 
break;
case 43: return 331; 
break;
case 44: return 100; 
break;
case 45: return 285; 
break;
case 46: return 286; 
break;
case 47: return 33; 
break;
case 48: return 82; 
break;
case 49: return 88; 
break;
case 50: return 23; 
break;
case 51: return 24; 
break;
case 52: return '<impala>ANTI'; 
break;
case 53: return 310; 
break;
case 54: return 57; 
break;
case 55: determineCase(yy_.yytext); return 28; 
break;
case 56: return 61; 
break;
case 57: return 64; 
break;
case 58: return 68; 
break;
case 59: determineCase(yy_.yytext); return 195; 
break;
case 60: return 122; 
break;
case 61: return '<impala>FUNCTION'; 
break;
case 62: return 320; 
break;
case 63: return 325; 
break;
case 64: return 115; 
break;
case 65: return 72; 
break;
case 66: return '<impala>INCREMENTAL'; 
break;
case 67: this.begin('hdfs'); return 80; 
break;
case 68: return 77; 
break;
case 69: return 260; 
break;
case 70: return 75; 
break;
case 71: this.begin('hdfs'); return 86; 
break;
case 72: return 329; 
break;
case 73: return 264; 
break;
case 74: return 92; 
break;
case 75: return 95; 
break;
case 76: return 69; 
break;
case 77: return 311; 
break;
case 78: return 40; 
break;
case 79: return 98; 
break;
case 80: return 32; 
break;
case 81: return 83; 
break;
case 82: return 89; 
break;
case 83: return 222; 
break;
case 84: return 110; 
break;
case 85: return 177; 
break;
case 86: return 178; 
break;
case 87: return 214; 
break;
case 88: return 183; 
break;
case 89: determineCase(yy_.yytext); return 26; 
break;
case 90: return 49; 
break;
case 91: return 182; 
break;
case 92: return 180; 
break;
case 93: determineCase(yy_.yytext); return 196; 
break;
case 94: return 131; 
break;
case 95: return 179; 
break;
case 96: return 35; 
break;
case 97: return 265; 
break;
case 98: return 'INNER'; 
break;
case 99: return 263; 
break;
case 100: return 258; 
break;
case 101: return 113; 
break;
case 102: return 130; 
break;
case 103: return 176; 
break;
case 104: return 200; 
break;
case 105: return 226; 
break;
case 106: return 234; 
break;
case 107: return 255; 
break;
case 108: return 261; 
break;
case 109: return 291; 
break;
case 110: return 133; 
break;
case 111: return 'NOT_IN'; 
break;
case 112: return 266; 
break;
case 113: return 220; 
break;
case 114: return 216; 
break;
case 115: return 'ROLE'; 
break;
case 116: return 50; 
break;
case 117: determineCase(yy_.yytext); return 201; 
break;
case 118: return 262; 
break;
case 119: return 334; 
break;
case 120: determineCase(yy_.yytext); return 290; 
break;
case 121: return 175; 
break;
case 122: return 181; 
break;
case 123: return 38; 
break;
case 124: return 185; 
break;
case 125: return 174; 
break;
case 126: determineCase(yy_.yytext); return 332; 
break;
case 127: determineCase(yy_.yytext); return 341; 
break;
case 128: return 184; 
break;
case 129: return 288; 
break;
case 130: return 212; 
break;
case 131: return 102; 
break;
case 132: return 12; 
break;
case 133: parser.yy.cursorFound = true; return 29; 
break;
case 134: parser.yy.cursorFound = true; return 13; 
break;
case 135: return 189; 
break;
case 136: return 190; 
break;
case 137: this.popState(); return 191; 
break;
case 138: return 7; 
break;
case 139: return yy_.yytext; 
break;
case 140: return yy_.yytext; 
break;
case 141: return '['; 
break;
case 142: return ']'; 
break;
case 143: this.begin('backtickedValue'); return 139; 
break;
case 144: if (yy_.yytext.indexOf('\u2020') !== -1 || yy_.yytext.indexOf('\u2021') !== -1) {
                                        this.popState();
                                        return 140;
                                      }
                                      return 106;
                                    
break;
case 145: this.popState(); return 139; 
break;
case 146: this.begin('singleQuotedValue'); return 105; 
break;
case 147: return 106; 
break;
case 148: this.popState(); return 105; 
break;
case 149: this.begin('doubleQuotedValue'); return 108; 
break;
case 150: return 106; 
break;
case 151: this.popState(); return 108; 
break;
case 152: return 7; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:AS\b)/i,/^(?:ALL\b)/i,/^(?:BINARY\b)/i,/^(?:COLUMNS\b)/i,/^(?:COMMENT\b)/i,/^(?:COMPACTIONS\b)/i,/^(?:CONF\b)/i,/^(?:CREATE\b)/i,/^(?:CROSS\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DATE\b)/i,/^(?:DESCRIBE\b)/i,/^(?:EXTENDED\b)/i,/^(?:EXTERNAL\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:IN\b)/i,/^(?:INDEX\b)/i,/^(?:INDEXES\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:LOCKS\b)/i,/^(?:MACRO\b)/i,/^(?:PARTITION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:TBLPROPERTIES\b)/i,/^(?:TEMPORARY\b)/i,/^(?:TRANSACTIONS\b)/i,/^(?:USER\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:AGGREGATE\b)/i,/^(?:ANALYTIC\b)/i,/^(?:ANTI\b)/i,/^(?:COLUMN\b)/i,/^(?:COMMENT\b)/i,/^(?:CREATE\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DESCRIBE\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:GROUP\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INCREMENTAL\b)/i,/^(?:INPATH\b)/i,/^(?:IN\b)/i,/^(?:INNER\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:RIGHT\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:STATS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:[.])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:AND\b)/i,/^(?:AS\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DATABASE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:DROP\b)/i,/^(?:EXISTS\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:OUTER\b)/i,/^(?:INNER\b)/i,/^(?:RIGHT\b)/i,/^(?:FULL\b)/i,/^(?:GROUP\b)/i,/^(?:IF\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:IN\b)/i,/^(?:JOIN\b)/i,/^(?:LEFT\b)/i,/^(?:LIKE\b)/i,/^(?:NOT\b)/i,/^(?:NOT IN\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:ROLE\b)/i,/^(?:SCHEMA\b)/i,/^(?:SELECT\b)/i,/^(?:SEMI\b)/i,/^(?:SET\b)/i,/^(?:SHOW\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:\s+['])/i,/^(?:[^'\u2020\u2021]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>]+)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:[^"]+)/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[133,134,135,136,137,138],"inclusive":false},"doubleQuotedValue":{"rules":[150,151],"inclusive":false},"singleQuotedValue":{"rules":[147,148],"inclusive":false},"backtickedValue":{"rules":[144,145],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,139,140,141,142,143,146,149,152],"inclusive":true},"impala":{"rules":[0,1,2,3,4,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,139,140,141,142,143,146,149,152],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,139,140,141,142,143,146,149,152],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});