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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,8],$V1=[1,19],$V2=[1,50],$V3=[1,51],$V4=[1,52],$V5=[1,18],$V6=[1,55],$V7=[1,56],$V8=[1,53],$V9=[1,54],$Va=[1,25],$Vb=[1,17],$Vc=[1,28],$Vd=[1,49],$Ve=[1,47],$Vf=[6,7],$Vg=[1,66],$Vh=[6,7,29,35,42,43,44,45,46,47,113,114,115,147,162,212,216,217,220,222,225],$Vi=[1,72],$Vj=[1,73],$Vk=[1,74],$Vl=[1,75],$Vm=[1,76],$Vn=[1,122],$Vo=[1,123],$Vp=[1,134],$Vq=[1,136],$Vr=[29,38,39,40,49,50,71,72],$Vs=[12,29,139],$Vt=[29,63,64],$Vu=[6,7,35],$Vv=[1,151],$Vw=[6,7,29,35,147,216,217],$Vx=[1,155],$Vy=[1,156],$Vz=[1,157],$VA=[6,7,13,29,31,32,33,35,42,43,44,45,46,47,113,114,115,147,162,212,216,217,220,222,225,243,245,246,248,249,251,252],$VB=[1,159],$VC=[1,160],$VD=[6,7,12],$VE=[38,39,40],$VF=[6,7,12,29,130,139],$VG=[6,7,12,29,118,130,139],$VH=[6,7,12,29,139],$VI=[2,107],$VJ=[1,168],$VK=[1,175],$VL=[1,177],$VM=[1,178],$VN=[1,183],$VO=[1,184],$VP=[29,268],$VQ=[1,195],$VR=[1,197],$VS=[6,7,254],$VT=[6,7,29,105,268],$VU=[2,115],$VV=[1,222],$VW=[1,223],$VX=[29,38,39,40],$VY=[29,94,95],$VZ=[29,297],$V_=[6,7,29,254],$V$=[29,299,302],$V01=[6,7,29,36,77,105,268],$V11=[29,79,80],$V21=[6,7,29,311],$V31=[1,237],$V41=[6,7,12,29,118,289,304,311],$V51=[1,243],$V61=[1,241],$V71=[1,244],$V81=[6,7,29,113,114,115,216,217],$V91=[1,257],$Va1=[1,265],$Vb1=[1,268],$Vc1=[12,13,139,234,235],$Vd1=[2,27],$Ve1=[2,28],$Vf1=[1,272],$Vg1=[1,273],$Vh1=[88,89,102,108],$Vi1=[1,277],$Vj1=[1,283],$Vk1=[6,7,29,118,289,304],$Vl1=[2,29],$Vm1=[6,7,33],$Vn1=[6,7,29,268],$Vo1=[1,320],$Vp1=[1,321],$Vq1=[1,328],$Vr1=[1,329],$Vs1=[2,102],$Vt1=[1,340],$Vu1=[1,345],$Vv1=[1,344],$Vw1=[6,7,31,32,33],$Vx1=[2,137],$Vy1=[6,7,29,31,32,33,105,268],$Vz1=[6,7,12,29,31,32,33,35,36,82,83,105,110,111,113,114,115,127,128,139,147,212,216,217,243,245,246,248,249,251,252,254,264,268],$VA1=[1,353],$VB1=[6,7,12,29,110,111,113,114,115,139,147,212,216,217,243,245,246,248,249,251,252,254,264],$VC1=[6,7,29,216,217],$VD1=[12,234],$VE1=[2,292],$VF1=[1,378],$VG1=[1,379],$VH1=[1,368],$VI1=[1,373],$VJ1=[6,7,29,113,114,115,147,212,216,217],$VK1=[2,327],$VL1=[1,384],$VM1=[1,385],$VN1=[1,386],$VO1=[1,387],$VP1=[1,388],$VQ1=[1,389],$VR1=[6,7,29,113,114,115,147,212,216,217,243,245,246,248,249,251,252,254,264],$VS1=[2,6,7,12,29,31,32,33,35,110,111,113,114,115,118,139,147,212,216,217,243,245,246,248,249,251,252,254,264,289,304,311],$VT1=[6,7,29,31,32,33,35,147,162,216,217],$VU1=[1,406],$VV1=[2,187],$VW1=[6,7,29],$VX1=[1,439],$VY1=[6,7,29,147,212],$VZ1=[6,7,29,217],$V_1=[29,214],$V$1=[1,477],$V02=[6,7,29,113,114,115,147,162,212,216,217,220],$V12=[6,7,29,113,114,115,147,162,212,216,217,220,222],$V22=[6,7,29,42,43,44,45,46,47,113,114,115,147,162,212,216,217,220,222,225],$V32=[6,7,29,42,43,44,45,46,47,113,114,115,147,162,212,216,217,220,222,225,243,245,246,248,249,251,252],$V42=[1,494],$V52=[29,243],$V62=[2,340],$V72=[1,499],$V82=[12,139],$V92=[1,514],$Va2=[1,515],$Vb2=[147,162],$Vc2=[1,541],$Vd2=[1,542],$Ve2=[1,540],$Vf2=[1,561],$Vg2=[6,7,147,162],$Vh2=[2,6,7,29,56,57,85,86,159,200],$Vi2=[12,13,29,102,103,105,161,234],$Vj2=[6,7,29,31,32,33,42,43,44,45,46,47,113,114,115,147,162,212,216,217,220,222,225,243,245,246,248,249,251,252],$Vk2=[2,29,56,57,85,86,159],$Vl2=[1,647],$Vm2=[6,7,29,113,114,115,147,212,216,217,243,245,246,248,249,251,252],$Vn2=[1,670],$Vo2=[1,671],$Vp2=[1,679],$Vq2=[1,680],$Vr2=[1,681],$Vs2=[6,7,29,113,114,115,147,162,212,216,217,222,243,245,246,248,249,251,252],$Vt2=[1,687],$Vu2=[12,29,111];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"InitResults":3,"Sql":4,"SqlStatements":5,";":6,"EOF":7,"SqlStatement":8,"DataDefinition":9,"DataManipulation":10,"SelectStatement":11,"REGULAR_IDENTIFIER":12,"PARTIAL_CURSOR":13,"AnyCursor":14,"CreateStatement":15,"DescribeStatement":16,"DropStatement":17,"ShowStatement":18,"UseStatement":19,"LoadStatement":20,"UpdateStatement":21,"AggregateOrAnalytic":22,"<impala>AGGREGATE":23,"<impala>ANALYTIC":24,"AnyCreate":25,"CREATE":26,"<hive>CREATE":27,"<impala>CREATE":28,"CURSOR":29,"AnyDot":30,".":31,"<impala>.":32,"<hive>.":33,"AnyFromOrIn":34,"FROM":35,"<hive>IN":36,"AnyTable":37,"TABLE":38,"<hive>TABLE":39,"<impala>TABLE":40,"ComparisonOperators":41,"=":42,"<>":43,"<=":44,">=":45,"<":46,">":47,"DatabaseOrSchema":48,"DATABASE":49,"SCHEMA":50,"FromOrIn":51,"HiveIndexOrIndexes":52,"<hive>INDEX":53,"<hive>INDEXES":54,"HiveOrImpalaComment":55,"<hive>COMMENT":56,"<impala>COMMENT":57,"HiveOrImpalaCreate":58,"HiveOrImpalaCurrent":59,"<hive>CURRENT":60,"<impala>CURRENT":61,"HiveOrImpalaData":62,"<hive>DATA":63,"<impala>DATA":64,"HiveOrImpalaDatabasesOrSchemas":65,"<hive>DATABASES":66,"<hive>SCHEMAS":67,"<impala>DATABASES":68,"<impala>SCHEMAS":69,"HiveOrImpalaExternal":70,"<hive>EXTERNAL":71,"<impala>EXTERNAL":72,"HiveOrImpalaLoad":73,"<hive>LOAD":74,"<impala>LOAD":75,"HiveOrImpalaIn":76,"<impala>IN":77,"HiveOrImpalaInpath":78,"<hive>INPATH":79,"<impala>INPATH":80,"HiveOrImpalaLeftSquareBracket":81,"<hive>[":82,"<impala>[":83,"HiveOrImpalaLocation":84,"<hive>LOCATION":85,"<impala>LOCATION":86,"HiveOrImpalaRightSquareBracket":87,"<hive>]":88,"<impala>]":89,"HiveOrImpalaRole":90,"<hive>ROLE":91,"<impala>ROLE":92,"HiveOrImpalaRoles":93,"<hive>ROLES":94,"<impala>ROLES":95,"HiveOrImpalaTables":96,"<hive>TABLES":97,"<impala>TABLES":98,"HiveRoleOrUser":99,"<hive>USER":100,"SignedInteger":101,"UNSIGNED_INTEGER":102,"-":103,"SingleQuotedValue":104,"SINGLE_QUOTE":105,"VALUE":106,"DoubleQuotedValue":107,"DOUBLE_QUOTE":108,"AnyAs":109,"AS":110,"<hive>AS":111,"AnyGroup":112,"GROUP":113,"<hive>GROUP":114,"<impala>GROUP":115,"OptionalAggregateOrAnalytic":116,"OptionalExtended":117,"<hive>EXTENDED":118,"OptionalExtendedOrFormatted":119,"<hive>FORMATTED":120,"OptionalFormatted":121,"<impala>FORMATTED":122,"OptionallyFormattedIndex":123,"OptionalFromDatabase":124,"DatabaseIdentifier":125,"OptionalHiveCascadeOrRestrict":126,"<hive>CASCADE":127,"<hive>RESTRICT":128,"OptionalIfExists":129,"IF":130,"EXISTS":131,"OptionalIfNotExists":132,"NOT":133,"OptionalInDatabase":134,"ConfigurationName":135,"PartialBacktickedOrCursor":136,"PartialBacktickedIdentifier":137,"PartialBacktickedOrPartialCursor":138,"BACKTICK":139,"PARTIAL_VALUE":140,"SchemaQualifiedTableIdentifier":141,"RegularOrBacktickedIdentifier":142,"ImprovedDerivedColumnChain":143,"OptionalMapOrArrayKey":144,"PartitionSpecList":145,"PartitionSpec":146,",":147,"CleanRegularOrBackTickedSchemaQualifiedName":148,"RegularOrBackTickedSchemaQualifiedName":149,"ColumnIdentifier":150,"LocalOrSchemaQualifiedName":151,"DerivedColumnChain":152,"TableDefinition":153,"DatabaseDefinition":154,"Comment":155,"HivePropertyAssignmentList":156,"HivePropertyAssignment":157,"HiveDbProperties":158,"<hive>WITH":159,"DBPROPERTIES":160,"(":161,")":162,"DatabaseDefinitionOptionals":163,"DatabaseDefinitionOptional":164,"HdfsLocation":165,"CleanUpDatabaseConditions":166,"TableScope":167,"TableElementList":168,"TableElements":169,"TableElement":170,"ColumnDefinition":171,"PrimitiveType":172,"ColumnDefinitionError":173,"TINYINT":174,"SMALLINT":175,"INT":176,"BIGINT":177,"BOOLEAN":178,"FLOAT":179,"DOUBLE":180,"STRING":181,"DECIMAL":182,"CHAR":183,"VARCHAR":184,"TIMESTAMP":185,"<hive>BINARY":186,"<hive>DATE":187,"HdfsPath":188,"HDFS_START_QUOTE":189,"HDFS_PATH":190,"HDFS_END_QUOTE":191,"HiveDescribeStatement":192,"ImpalaDescribeStatement":193,"<hive>DESCRIBE":194,"<impala>DESCRIBE":195,"DROP":196,"DropDatabaseStatement":197,"DropTableStatement":198,"TablePrimary":199,"INTO":200,"SELECT":201,"SelectList":202,"TableExpression":203,"FromClause":204,"SelectConditions":205,"TableReferenceList":206,"OptionalWhereClause":207,"OptionalGroupByClause":208,"OptionalOrderByClause":209,"OptionalLimitClause":210,"WhereClause":211,"WHERE":212,"SearchCondition":213,"BY":214,"ColumnList":215,"ORDER":216,"LIMIT":217,"BooleanValueExpression":218,"BooleanTerm":219,"OR":220,"BooleanFactor":221,"AND":222,"BooleanTest":223,"Predicate":224,"IS":225,"TruthValue":226,"ParenthesizedBooleanValueExpression":227,"NonParenthesizedValueExpressionPrimary":228,"ColumnReference":229,"BasicIdentifierChain":230,"InitIdentifierChain":231,"IdentifierChain":232,"Identifier":233,"\"":234,"*":235,"DerivedColumn":236,"TableReference":237,"TablePrimaryOrJoinedTable":238,"ImprovedTablePrimary":239,"JoinedTable":240,"Joins":241,"JoinTypes":242,"JOIN":243,"JoinCondition":244,"<hive>CROSS":245,"FULL":246,"OptionalOuter":247,"<impala>INNER":248,"LEFT":249,"SEMI":250,"RIGHT":251,"<impala>RIGHT":252,"OUTER":253,"ON":254,"JoinEqualityExpression":255,"ParenthesizedJoinEqualityExpression":256,"EqualityExpression":257,"OptionalCorrelationName":258,"OptionalLateralViews":259,"LateralView":260,"UserDefinedTableGeneratingFunction":261,"<hive>explode":262,"<hive>posexplode":263,"<hive>LATERAL":264,"VIEW":265,"LateralViewColumnAliases":266,"SHOW":267,"LIKE":268,"ShowColumnStatement":269,"ShowColumnsStatement":270,"ShowCompactionsStatement":271,"ShowConfStatement":272,"ShowCreateTableStatement":273,"ShowCurrentStatement":274,"ShowDatabasesStatement":275,"ShowFunctionsStatement":276,"ShowGrantStatement":277,"ShowIndexStatement":278,"ShowLocksStatement":279,"ShowPartitionsStatement":280,"ShowRoleStatement":281,"ShowRolesStatement":282,"ShowTableStatement":283,"ShowTablesStatement":284,"ShowTblPropertiesStatement":285,"ShowTransactionsStatement":286,"<impala>COLUMN":287,"<impala>STATS":288,"if":289,"partial":290,"identifierChain":291,"length":292,"<hive>COLUMNS":293,"<hive>COMPACTIONS":294,"<hive>CONF":295,"<hive>FUNCTIONS":296,"<impala>FUNCTIONS":297,"SingleQuoteValue":298,"<hive>GRANT":299,"OptionalPrincipalName":300,"<hive>ALL":301,"<impala>GRANT":302,"<hive>LOCKS":303,"<hive>PARTITION":304,"<hive>PARTITIONS":305,"<impala>PARTITIONS":306,"<hive>TBLPROPERTIES":307,"<hive>TRANSACTIONS":308,"UPDATE":309,"TargetTable":310,"SET":311,"SetClauseList":312,"TableName":313,"SetClause":314,"SetTarget":315,"UpdateSource":316,"ValueExpression":317,"USE":318,"$accept":0,"$end":1},
terminals_: {2:"error",6:";",7:"EOF",12:"REGULAR_IDENTIFIER",13:"PARTIAL_CURSOR",23:"<impala>AGGREGATE",24:"<impala>ANALYTIC",26:"CREATE",27:"<hive>CREATE",28:"<impala>CREATE",29:"CURSOR",31:".",32:"<impala>.",33:"<hive>.",35:"FROM",36:"<hive>IN",38:"TABLE",39:"<hive>TABLE",40:"<impala>TABLE",42:"=",43:"<>",44:"<=",45:">=",46:"<",47:">",49:"DATABASE",50:"SCHEMA",53:"<hive>INDEX",54:"<hive>INDEXES",56:"<hive>COMMENT",57:"<impala>COMMENT",60:"<hive>CURRENT",61:"<impala>CURRENT",63:"<hive>DATA",64:"<impala>DATA",66:"<hive>DATABASES",67:"<hive>SCHEMAS",68:"<impala>DATABASES",69:"<impala>SCHEMAS",71:"<hive>EXTERNAL",72:"<impala>EXTERNAL",74:"<hive>LOAD",75:"<impala>LOAD",77:"<impala>IN",79:"<hive>INPATH",80:"<impala>INPATH",82:"<hive>[",83:"<impala>[",85:"<hive>LOCATION",86:"<impala>LOCATION",88:"<hive>]",89:"<impala>]",91:"<hive>ROLE",92:"<impala>ROLE",94:"<hive>ROLES",95:"<impala>ROLES",97:"<hive>TABLES",98:"<impala>TABLES",100:"<hive>USER",102:"UNSIGNED_INTEGER",103:"-",105:"SINGLE_QUOTE",106:"VALUE",108:"DOUBLE_QUOTE",110:"AS",111:"<hive>AS",113:"GROUP",114:"<hive>GROUP",115:"<impala>GROUP",118:"<hive>EXTENDED",120:"<hive>FORMATTED",122:"<impala>FORMATTED",127:"<hive>CASCADE",128:"<hive>RESTRICT",130:"IF",131:"EXISTS",133:"NOT",139:"BACKTICK",140:"PARTIAL_VALUE",147:",",159:"<hive>WITH",160:"DBPROPERTIES",161:"(",162:")",174:"TINYINT",175:"SMALLINT",176:"INT",177:"BIGINT",178:"BOOLEAN",179:"FLOAT",180:"DOUBLE",181:"STRING",182:"DECIMAL",183:"CHAR",184:"VARCHAR",185:"TIMESTAMP",186:"<hive>BINARY",187:"<hive>DATE",189:"HDFS_START_QUOTE",190:"HDFS_PATH",191:"HDFS_END_QUOTE",194:"<hive>DESCRIBE",195:"<impala>DESCRIBE",196:"DROP",200:"INTO",201:"SELECT",212:"WHERE",214:"BY",216:"ORDER",217:"LIMIT",220:"OR",222:"AND",225:"IS",226:"TruthValue",234:"\"",235:"*",243:"JOIN",245:"<hive>CROSS",246:"FULL",248:"<impala>INNER",249:"LEFT",250:"SEMI",251:"RIGHT",252:"<impala>RIGHT",253:"OUTER",254:"ON",262:"<hive>explode",263:"<hive>posexplode",264:"<hive>LATERAL",265:"VIEW",267:"SHOW",268:"LIKE",287:"<impala>COLUMN",288:"<impala>STATS",289:"if",290:"partial",291:"identifierChain",292:"length",293:"<hive>COLUMNS",294:"<hive>COMPACTIONS",295:"<hive>CONF",296:"<hive>FUNCTIONS",297:"<impala>FUNCTIONS",298:"SingleQuoteValue",299:"<hive>GRANT",301:"<hive>ALL",302:"<impala>GRANT",303:"<hive>LOCKS",304:"<hive>PARTITION",305:"<hive>PARTITIONS",306:"<impala>PARTITIONS",307:"<hive>TBLPROPERTIES",308:"<hive>TRANSACTIONS",309:"UPDATE",311:"SET",318:"USE"},
productions_: [0,[3,0],[4,4],[4,3],[5,1],[5,3],[8,1],[8,1],[8,1],[8,3],[8,2],[8,1],[9,1],[9,1],[9,1],[9,1],[9,1],[10,1],[10,1],[22,1],[22,1],[25,1],[25,1],[25,1],[14,1],[14,1],[30,1],[30,1],[30,1],[34,1],[34,1],[37,1],[37,1],[37,1],[41,1],[41,1],[41,1],[41,1],[41,1],[41,1],[48,1],[48,1],[51,1],[51,1],[52,1],[52,1],[55,1],[55,1],[58,1],[58,1],[59,1],[59,1],[62,1],[62,1],[65,1],[65,1],[65,1],[65,1],[70,1],[70,1],[73,1],[73,1],[76,1],[76,1],[78,1],[78,1],[81,1],[81,1],[84,1],[84,1],[87,1],[87,1],[90,1],[90,1],[93,1],[93,1],[96,1],[96,1],[99,1],[99,1],[101,1],[101,2],[104,3],[107,3],[109,1],[109,1],[112,1],[112,1],[112,1],[116,0],[116,1],[117,0],[117,1],[119,0],[119,1],[119,1],[121,0],[121,1],[123,2],[123,2],[123,2],[123,1],[124,0],[124,2],[126,0],[126,1],[126,1],[129,0],[129,2],[129,2],[132,0],[132,1],[132,2],[132,3],[132,3],[134,0],[134,2],[135,1],[135,1],[135,3],[135,3],[136,1],[136,1],[138,1],[138,1],[137,2],[141,1],[141,1],[141,3],[141,3],[141,3],[125,1],[125,1],[143,1],[143,2],[143,3],[143,4],[144,0],[144,3],[144,3],[144,2],[145,1],[145,3],[146,3],[148,1],[148,1],[150,1],[150,4],[150,4],[150,3],[142,1],[142,3],[149,3],[149,5],[149,5],[149,7],[149,5],[149,3],[149,1],[149,3],[151,1],[151,2],[151,1],[151,2],[152,1],[152,3],[15,1],[15,1],[15,2],[155,2],[155,3],[155,4],[156,1],[156,3],[157,3],[157,7],[158,5],[158,2],[158,2],[163,1],[163,2],[163,3],[164,1],[164,1],[164,1],[166,0],[154,3],[154,4],[154,5],[154,7],[154,7],[153,6],[153,5],[153,4],[153,3],[153,6],[153,4],[167,1],[168,3],[169,1],[169,3],[170,1],[171,2],[171,2],[171,4],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[172,1],[173,0],[165,2],[188,3],[188,5],[188,4],[188,3],[188,3],[188,2],[16,1],[16,1],[192,3],[192,4],[193,3],[193,3],[17,2],[17,1],[17,1],[197,3],[197,4],[197,5],[197,5],[198,3],[198,4],[198,4],[198,5],[20,7],[20,6],[20,5],[20,4],[20,3],[20,2],[11,3],[11,2],[203,2],[203,3],[204,2],[205,4],[211,2],[211,2],[207,0],[207,2],[207,2],[208,0],[208,3],[208,2],[209,0],[209,3],[209,2],[210,0],[210,2],[210,2],[213,1],[218,1],[218,3],[219,1],[219,3],[219,3],[221,2],[221,1],[223,1],[223,3],[223,3],[223,3],[223,4],[224,1],[224,1],[227,3],[227,2],[228,1],[228,1],[228,1],[229,1],[230,2],[231,0],[232,1],[232,3],[232,3],[233,1],[233,2],[233,3],[202,1],[202,2],[202,2],[202,1],[215,1],[215,3],[236,1],[236,3],[236,2],[236,3],[236,3],[236,5],[236,5],[236,1],[206,1],[206,3],[237,1],[237,1],[238,1],[238,1],[240,2],[241,4],[241,4],[241,3],[241,3],[241,4],[241,5],[241,4],[242,0],[242,1],[242,2],[242,3],[242,1],[242,3],[242,2],[242,2],[242,2],[242,3],[242,3],[242,2],[242,2],[247,0],[247,1],[244,2],[244,2],[256,3],[256,2],[255,1],[255,3],[257,3],[257,1],[257,3],[257,3],[257,1],[257,1],[199,1],[239,3],[258,0],[258,1],[258,1],[258,2],[258,2],[259,0],[259,2],[261,4],[261,4],[261,4],[261,4],[260,5],[260,4],[260,5],[260,4],[260,3],[260,2],[266,2],[266,6],[18,2],[18,3],[18,4],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[18,1],[269,3],[269,4],[269,8],[270,3],[270,4],[270,4],[270,5],[270,6],[270,4],[270,5],[270,6],[270,6],[270,6],[271,2],[272,3],[273,3],[273,4],[273,4],[273,4],[274,3],[274,3],[274,3],[275,3],[275,4],[275,3],[276,2],[276,3],[276,3],[276,4],[276,4],[276,5],[276,6],[276,6],[276,6],[276,6],[277,3],[277,5],[277,5],[277,5],[277,6],[277,6],[277,6],[277,3],[300,0],[300,1],[300,1],[300,2],[278,2],[278,3],[278,4],[278,4],[278,4],[278,5],[278,6],[278,6],[278,6],[278,6],[279,3],[279,3],[279,4],[279,4],[279,7],[279,8],[279,8],[279,4],[279,4],[280,3],[280,7],[280,4],[280,5],[280,3],[280,7],[281,3],[281,5],[281,4],[281,5],[281,5],[281,4],[281,5],[281,5],[282,2],[283,3],[283,4],[283,5],[283,6],[283,6],[283,6],[283,7],[283,8],[283,8],[283,8],[283,8],[283,3],[283,4],[283,8],[284,3],[284,4],[284,4],[284,5],[285,3],[286,2],[21,5],[21,5],[21,4],[21,3],[21,2],[21,2],[310,1],[313,1],[312,1],[312,3],[314,3],[314,2],[314,1],[315,1],[316,1],[317,1],[19,2],[19,2]],
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
case 126: case 502:

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
case 145: case 284: case 287: case 290:

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
case 250: case 497: case 499:

     linkTablePrimaries();
   
break;
case 253:

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
case 255:

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
case 257: case 260: case 297: case 350: case 351: case 352: case 353: case 509:

     suggestColumns();
   
break;
case 262: case 265:

     delete parser.yy.result.suggestStar;
   
break;
case 263: case 266:

     suggestKeywords(['BY']);
   
break;
case 269:

     suggestNumbers([1, 5, 10]);
   
break;
case 274:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 280:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 286:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 291:

     this.$ = parser.yy.identifierChain;
     delete parser.yy.identifierChain;
   
break;
case 292:

     parser.yy.identifierChain = [];
   
break;
case 294:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 296:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 298:

     parser.yy.identifierChain.push({ name: $$[$0-1] });
   
break;
case 300: case 301:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 306:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 307:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 309:

      delete parser.yy.derivedColumnChain;
   
break;
case 310: case 311:

      parser.yy.derivedColumnChain.unshift($$[$0-4]);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    
break;
case 312:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 316:

        suggestTables();
        suggestDatabases({ appendDot: true });
    
break;
case 318:

     parser.yy.unfinishedJoin = false;
   
break;
case 321: case 444: case 446:

     suggestKeywords(['ON']);
   
break;
case 322: case 326: case 397: case 412: case 462: case 466: case 489:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 330: case 336:

     if (!$$[$0-1]) {
       suggestKeywords(['OUTER']);
     }
   
break;
case 332:

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
case 337:

     if (!$$[$0-1]) {
       suggestKeywords(['ANTI', 'SEMI', 'OUTER']);
     } else {
       suggestKeywords(['ANTI', 'SEMI']);
     }
   
break;
case 355:

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
case 357: case 359:

     this.$ = { partial: true }
   
break;
case 358: case 360:

     this.$ = $$[$0]
   
break;
case 362:

     if ($$[$0-1]) {
       this.$ = $$[$0-1].concat($$[$0]);
     } else {
       this.$ = $$[$0];
     }
   
break;
case 363:

     delete parser.yy.derivedColumnChain;
     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 365:

      delete parser.yy.derivedColumnChain;
      this.$ = { function: $$[$0-3], expression: $$[$0-1] }
    
break;
case 367:

     this.$ = [{ udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }]
   
break;
case 368:

      this.$ = [{ udtf: $$[$0-1], columnAliases: $$[$0] }]
    
break;
case 369: case 370:

     this.$ = [];
     suggestKeywords(['AS']);
   
break;
case 371:

     this.$ = [];
     suggestKeywords(['explode', 'posexplode']);
   
break;
case 372:

     this.$ = [];
     suggestKeywords(['VIEW']);
   
break;
case 373:

     this.$ = [ $$[$0] ]
   
break;
case 374:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 375:

     if (isHive()) {
       suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
     } else {
       suggestKeywords(['COLUMNS', 'DATABASES', 'TABLES']);
     }
   
break;
case 376:

     if (isImpala()) {
       suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'PARTITIONS', 'TABLE STATS']);
     }
   
break;
case 377:

     if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'DATABASES', 'FUNCTIONS', 'SCHEMAS', 'TABLES']);
     } else if (isHive()) {
       suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
     }
   
break;
case 396: case 488:

     suggestKeywords(['STATS']);
   
break;
case 398: case 490:

     suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
   
break;
case 399: case 400: case 405: case 406: case 448: case 449:

     suggestKeywords(['FROM', 'IN']);
   
break;
case 401: case 402: case 403: case 435: case 445: case 495:

     suggestTables();
   
break;
case 407: case 450: case 460: case 514:

     suggestDatabases();
   
break;
case 411: case 414: case 437:

     suggestKeywords(['TABLE']);
   
break;
case 413:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name);
     }
   
break;
case 415:

     suggestKeywords([ 'ROLES' ]);
   
break;
case 416:

     suggestKeywords([ 'CURRENT' ]);
   
break;
case 418: case 486:

     suggestKeywords(['LIKE']);
   
break;
case 423: case 428:

     suggestKeywords(['FUNCTIONS']);
   
break;
case 425: case 429:

     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   
break;
case 426: case 492:

     if (!$$[$0-1]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 430:

     if (!$$[$0-2]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 431:

     if ($$[$0]) {
       suggestKeywords(['ON']);
     }
   
break;
case 433:

     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   
break;
case 438:

     suggestKeywords(['ROLE']);
   
break;
case 441: case 442:

     this.$ = true;
   
break;
case 451:

     suggestTablesOrColumns($$[$0]);
   
break;
case 453:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
     suggestKeywords(['DATABASE', 'SCHEMA']);
   
break;
case 454:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name)
     }
   
break;
case 455:

      suggestKeywords(['EXTENDED', 'PARTITION']);
    
break;
case 456:

     if ($$[$0-1].partial && $$[$0-1].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-1].identifierChain[0].name)
     }
   
break;
case 457:

     if ($$[$0-4].partial && $$[$0-4].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
     }
   
break;
case 458: case 477: case 485:

     suggestKeywords(['EXTENDED']);
   
break;
case 459:

     // TODO: Move into CleanRegularOrBackTickedSchemaQualifiedName
     if ($$[$0-5].partial && $$[$0-5].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
     }
   
break;
case 463: case 467:

     suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
   
break;
case 464: case 487:

     suggestKeywords(['PARTITION']);
   
break;
case 468: case 469:

     suggestKeywords(['GRANT']);
   
break;
case 470: case 471:

     suggestKeywords(['ROLE', 'USER']);
   
break;
case 473: case 474:

     suggestKeywords(['GROUP']);
   
break;
case 479:

      if ($$[$0-1]) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    
break;
case 481:

      if (isHive())
        suggestKeywords(['EXTENDED']);
      
break;
case 482:

      suggestKeywords(['LIKE']);
    
break;
case 483:

      suggestKeywords(['PARTITION']);
    
break;
case 498:

     suggestKeywords([ 'WHERE' ]);
   
break;
case 500:

     suggestKeywords([ 'SET' ]);
   
break;
case 504:

     // TODO: Replace with TablePrimary?
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 508:

     suggestKeywords([ '=' ]);
   
break;
case 513:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
}
},
table: [o([12,13,26,27,28,29,74,75,194,195,196,201,267,309,318],[2,1],{4:1,3:2}),{1:[3]},{5:3,8:4,9:5,10:6,11:7,12:$V0,13:$V1,14:9,15:10,16:11,17:12,18:13,19:14,20:15,21:16,25:22,26:$V2,27:$V3,28:$V4,29:$V5,73:48,74:$V6,75:$V7,153:20,154:21,192:23,193:24,194:$V8,195:$V9,196:$Va,197:26,198:27,201:$Vb,267:$Vc,269:29,270:30,271:31,272:32,273:33,274:34,275:35,276:36,277:37,278:38,279:39,280:40,281:41,282:42,283:43,284:44,285:45,286:46,309:$Vd,318:$Ve},{6:[1,57],7:[1,58]},o($Vf,[2,4]),o($Vf,[2,6]),o($Vf,[2,7]),o($Vf,[2,8]),{13:[1,59]},o($Vf,[2,11]),o($Vf,[2,12]),o($Vf,[2,13]),o($Vf,[2,14]),o($Vf,[2,15]),o($Vf,[2,16]),o($Vf,[2,17]),o($Vf,[2,18]),{12:$Vg,13:$V1,14:65,29:$V5,150:64,202:60,215:61,235:[1,62],236:63},o($Vh,[2,24]),o($Vh,[2,25]),o($Vf,[2,166]),o($Vf,[2,167]),{29:[1,67],37:69,38:$Vi,39:$Vj,40:$Vk,48:70,49:$Vl,50:$Vm,70:71,71:[1,77],72:[1,78],167:68},o($Vf,[2,227]),o($Vf,[2,228]),{29:[1,79],37:81,38:$Vi,39:$Vj,40:$Vk,48:80,49:$Vl,50:$Vm},o($Vf,[2,234]),o($Vf,[2,235]),{22:92,23:[1,114],24:[1,115],27:[1,107],28:[1,108],29:[1,82],39:[1,102],40:[1,103],52:117,53:$Vn,54:$Vo,58:87,59:88,60:[1,109],61:[1,110],65:89,66:[1,111],67:[1,112],68:[1,90],69:[1,113],90:100,91:[1,118],92:[1,119],95:[1,101],96:104,97:[1,120],98:[1,121],116:93,120:[1,116],123:96,287:[1,83],293:[1,84],294:[1,85],295:[1,86],296:[1,91],297:[2,89],299:[1,94],302:[1,95],303:[1,97],305:[1,98],306:[1,99],307:[1,105],308:[1,106]},o($Vf,[2,378]),o($Vf,[2,379]),o($Vf,[2,380]),o($Vf,[2,381]),o($Vf,[2,382]),o($Vf,[2,383]),o($Vf,[2,384]),o($Vf,[2,385]),o($Vf,[2,386]),o($Vf,[2,387]),o($Vf,[2,388]),o($Vf,[2,389]),o($Vf,[2,390]),o($Vf,[2,391]),o($Vf,[2,392]),o($Vf,[2,393]),o($Vf,[2,394]),o($Vf,[2,395]),{12:[1,124],29:[1,125]},{29:[1,127],62:126,63:[1,128],64:[1,129]},{12:$Vp,29:[1,131],137:137,139:$Vq,149:135,151:133,310:130,313:132},o($Vr,[2,21]),o($Vr,[2,22]),o($Vr,[2,23]),o($Vs,[2,93],{119:138,48:139,49:$Vl,50:$Vm,118:[1,140],120:[1,141]}),o($Vs,[2,96],{121:142,122:[1,143]}),o($Vt,[2,60]),o($Vt,[2,61]),{7:[1,144],8:145,9:5,10:6,11:7,12:$V0,13:$V1,14:9,15:10,16:11,17:12,18:13,19:14,20:15,21:16,25:22,26:$V2,27:$V3,28:$V4,29:$V5,73:48,74:$V6,75:$V7,153:20,154:21,192:23,193:24,194:$V8,195:$V9,196:$Va,197:26,198:27,201:$Vb,267:$Vc,269:29,270:30,271:31,272:32,273:33,274:34,275:35,276:36,277:37,278:38,279:39,280:40,281:41,282:42,283:43,284:44,285:45,286:46,309:$Vd,318:$Ve},{1:[2,3]},o($Vf,[2,10],{12:[1,146]}),o($Vf,[2,251],{203:147,204:148,35:[1,149]}),o($Vu,[2,299],{29:[1,150],147:$Vv}),o($Vu,[2,302],{29:[1,152]}),o($Vw,[2,303]),o($Vw,[2,305],{30:153,13:[1,154],31:$Vx,32:$Vy,33:$Vz}),o($Vw,[2,312]),o($VA,[2,146],{81:158,82:$VB,83:$VC}),o($Vf,[2,168],{37:161,38:$Vi,39:$Vj,40:$Vk}),{37:162,38:$Vi,39:$Vj,40:$Vk},{12:[1,163]},o($VD,[2,110],{132:164,29:[1,165],130:[1,166]}),o($VE,[2,197]),o($VF,[2,31]),o($VF,[2,32]),o($VF,[2,33]),o($VG,[2,40]),o($VG,[2,41]),o($VE,[2,58]),o($VE,[2,59]),o($Vf,[2,233]),o($VH,$VI,{129:167,130:$VJ}),o($VH,$VI,{129:169,130:$VJ}),o($Vf,[2,375],{137:137,148:170,93:172,52:174,149:176,12:$VK,53:$Vn,54:$Vo,94:$VL,95:$VM,139:$Vq,268:[1,171],297:[1,173]}),{29:[1,179],288:[1,180]},{29:[1,181],34:182,35:$VN,36:$VO},o($Vf,[2,409]),{12:[1,186],29:[1,187],135:185},{29:[1,188],37:189,38:$Vi,39:$Vj,40:$Vk},{29:[1,190],93:191,94:$VL,95:$VM},{29:[1,192],268:[1,193]},o($VP,[2,56],{104:194,105:$VQ}),o($Vf,[2,421],{107:196,108:$VR}),{29:[1,198],297:[2,90]},{297:[1,199]},o($VS,[2,439],{300:200,12:[1,201],29:[1,202]}),{29:[1,203]},o($Vf,[2,443],{29:[1,204],254:[1,205]}),{12:$VK,29:[1,206],48:208,49:$Vl,50:$Vm,137:137,139:$Vq,148:207,149:176},{12:$VK,29:[1,209],137:137,139:$Vq,148:210,149:176},{12:$VK,29:[1,211],137:137,139:$Vq,148:212,149:176},{29:[1,213],299:[1,214],302:[1,215]},o($Vf,[2,476]),{29:[1,216],118:[1,217]},{29:[1,218],288:[1,219]},o($VT,$VU,{134:220,76:221,36:$VV,77:$VW}),{29:[1,224]},o($Vf,[2,496]),o($VX,[2,48]),o($VX,[2,49]),o($VY,[2,50]),o($VY,[2,51]),o($VP,[2,54]),o($VP,[2,55]),o($VP,[2,57]),o($VZ,[2,19]),o($VZ,[2,20]),{29:[1,226],52:225,53:$Vn,54:$Vo},o($V_,[2,101]),o($V$,[2,72]),o($V$,[2,73]),o($V01,[2,76]),o($V01,[2,77]),o($V_,[2,44]),o($V_,[2,45]),o($Vf,[2,513]),o($Vf,[2,514]),{29:[1,228],78:227,79:[1,229],80:[1,230]},o($Vf,[2,249]),o($V11,[2,52]),o($V11,[2,53]),o($Vf,[2,501],{29:[1,232],311:[1,231]}),o($Vf,[2,502]),o($V21,[2,503]),o($V21,[2,504]),o($V21,[2,160],{30:234,12:[1,233],31:$Vx,32:$Vy,33:$Vz}),o($V21,[2,162],{12:[1,235]}),{106:[1,236],140:$V31},o($V41,[2,158]),{12:$V51,29:$V61,136:239,137:242,139:$V71,142:240,143:238},o($Vs,[2,91],{117:245,118:[1,246]}),o($Vs,[2,94]),o($Vs,[2,95]),{12:$V51,29:[1,248],137:249,139:$V71,141:247,142:250},o($Vs,[2,97]),{1:[2,2]},o($Vf,[2,5]),o($Vf,[2,9]),o($Vf,[2,250]),o($V81,[2,258],{205:251,207:252,212:[1,253]}),{12:$V51,29:$V91,137:249,139:$V71,141:260,142:250,206:254,237:255,238:256,239:258,240:259},o($Vu,[2,300]),{12:$Vg,13:$V1,14:65,29:$V5,150:64,236:261},o($Vu,[2,301]),{12:$Vg,13:$Va1,137:266,138:262,139:$Vb1,150:267,152:264,235:[1,263]},o($Vw,[2,307]),o($Vc1,[2,26]),o($Vc1,$Vd1),o($Vc1,$Ve1),{87:271,88:$Vf1,89:$Vg1,102:[1,270],107:269,108:$VR},o($Vh1,[2,66]),o($Vh1,[2,67]),o($Vf,[2,194],{12:[1,274]}),{12:[1,275]},{161:$Vi1,168:276},o($Vf,[2,186],{12:[1,278]}),o($VD,[2,111]),{29:[1,279],133:[1,280]},o($Vf,[2,236],{142:282,12:$V51,29:[1,281],139:$Vj1}),{29:[1,284],131:[1,285]},o($Vf,[2,240],{149:135,137:137,199:287,151:288,12:$Vp,29:[1,286],139:$Vq}),o($Vf,[2,376]),{104:289,105:$VQ},o($Vf,[2,416]),o([6,7,268],$VU,{76:221,134:290,36:$VV,77:$VW}),o($V_,[2,100]),o($Vk1,[2,144],{30:234,31:$Vx,32:$Vy,33:$Vz}),o($Vk1,[2,145]),o($Vf,[2,74]),o($Vf,[2,75]),o($Vf,[2,396]),{12:$VK,29:[1,291],137:137,139:$Vq,148:292,149:176},o($Vf,[2,399],{142:293,12:$V51,139:$Vj1}),{12:$V51,29:[1,294],139:$Vj1,142:295},o($VH,$Vl1),o($VH,[2,30]),o($Vf,[2,410],{33:[1,296]}),o($Vm1,[2,117]),o($Vm1,[2,118]),o($Vf,[2,411],{137:137,149:176,148:297,12:$VK,139:$Vq}),{12:$VK,29:[1,298],137:137,139:$Vq,148:299,149:176},o($Vf,[2,415]),o($Vf,[2,417]),o($Vf,[2,418]),{104:300,105:$VQ},o($Vf,[2,420]),{106:[1,301]},o($Vf,[2,422]),{106:[1,302]},o($Vf,[2,423],{76:221,134:303,36:$VV,77:$VW,268:$VU}),o($Vn1,$VU,{76:221,134:304,36:$VV,77:$VW}),o($Vf,[2,431],{254:[1,305]}),o($VS,[2,440],{29:[1,306]}),o($VS,[2,441]),o($Vf,[2,438]),o($Vf,[2,444],{142:307,12:$V51,139:$Vj1}),{12:$V51,29:[1,308],139:$Vj1,142:309},o($Vf,[2,453]),o($Vf,[2,454],{29:[1,310],118:[1,311],304:[1,312]}),{12:$V51,29:[1,313],139:$Vj1,142:314},o($Vf,[2,462]),{29:[1,316],289:[1,315],304:[1,317]},o($Vf,[2,466]),{289:[1,318]},o($Vf,[2,468],{99:319,91:$Vo1,100:$Vp1}),{29:[1,322],91:$Vo1,99:323,100:$Vp1},{29:[1,324],115:[1,325]},o($Vf,[2,477],{124:326,51:327,35:$Vq1,36:$Vr1,268:$Vs1}),o($Vn1,$Vs1,{51:327,124:330,35:$Vq1,36:$Vr1}),o($Vf,[2,488]),{12:$VK,29:[1,331],137:137,139:$Vq,148:332,149:176},o($Vf,[2,491],{104:334,29:[1,333],105:$VQ,268:[1,335]}),{12:$V51,29:$V61,125:336,136:337,137:242,139:$V71,142:338},o($Vs,[2,62]),o($Vs,[2,63]),o($Vf,[2,495]),o($V_,[2,98]),o($V_,[2,99]),{188:339,189:$Vt1},o($Vf,[2,248]),{189:[2,64]},{189:[2,65]},{12:$Vu1,29:$Vv1,312:341,314:342,315:343},o($Vf,[2,500]),o($V21,[2,161]),{12:[1,346],13:$Va1,137:266,138:348,139:[1,347]},o($V21,[2,163]),{139:[1,349]},o([2,6,7,12,29,31,32,33,35,105,110,111,113,114,115,118,139,147,212,216,217,243,245,246,248,249,251,252,254,264,268,289,304,311],[2,125]),o($Vf,[2,229],{30:350,31:$Vx,32:$Vy,33:$Vz}),o($Vw1,[2,133]),o($Vw1,$Vx1,{144:351,81:352,82:$VB,83:$VC}),o($Vy1,[2,121]),o($Vy1,[2,122]),o($Vz1,[2,150]),{106:$VA1,140:$V31},{12:$V51,29:$V61,125:354,136:337,137:242,139:$V71,142:338},o($Vs,[2,92]),o($Vf,[2,231]),o($Vf,[2,232]),o($VB1,[2,126],{30:355,31:$Vx,32:$Vy,33:$Vz}),o($VB1,[2,127],{30:356,31:$Vx,32:$Vy,33:$Vz}),o($Vf,[2,252],{29:[1,357]}),o($VC1,[2,261],{208:358,112:359,113:[1,360],114:[1,361],115:[1,362]}),o($VD1,$VE1,{213:363,218:365,219:366,221:367,223:369,224:370,227:371,228:372,229:374,101:375,104:376,230:377,231:380,29:[1,364],102:$VF1,103:$VG1,105:$VQ,133:$VH1,161:$VI1}),o([6,7,29,113,114,115,212,216,217],[2,254],{147:[1,381]}),o($VJ1,[2,313]),o($VJ1,[2,315]),o($VJ1,[2,316]),o($VJ1,[2,317],{241:382,242:383,243:$VK1,245:$VL1,246:$VM1,248:$VN1,249:$VO1,251:$VP1,252:$VQ1}),o($VJ1,[2,318]),o($VR1,[2,356],{258:390,137:391,142:392,109:393,12:$V51,110:[1,394],111:[1,395],139:$V71}),o($Vw,[2,304]),o($Vw,[2,306]),o($Vw,[2,308]),o($Vw,[2,309],{30:398,31:$Vx,32:[1,396],33:[1,397]}),o($VS1,[2,123]),o($VS1,[2,124]),o($VT1,[2,164]),{140:$V31},{87:399,88:$Vf1,89:$Vg1},{87:400,88:$Vf1,89:$Vg1},o($VA,[2,149]),o($VA,[2,70]),o($VA,[2,71]),o($Vf,[2,193],{168:401,161:$Vi1}),{161:$Vi1,168:402},o($Vf,[2,196]),{12:$VU1,169:403,170:404,171:405},o([56,57,85,86,159],[2,185],{166:408,6:$VV1,7:$VV1,29:[1,407]}),o($VD,[2,112]),{29:[1,409],131:[1,410]},o($Vf,[2,237]),o($Vf,[2,104],{126:412,29:[1,411],127:[1,413],128:[1,414]}),{106:$VA1},o($VH,[2,108]),o($VH,[2,109]),o($Vf,[2,241]),o($Vf,[2,242],{29:[1,415]}),o($VW1,[2,354]),o($Vf,[2,377]),o($Vf,[2,425],{268:[1,416]}),o($Vf,[2,397]),{289:[1,417]},o($Vf,[2,400]),o($Vf,[2,401],{34:418,35:$VN,36:$VO}),o($Vf,[2,404],{34:420,29:[1,419],35:$VN,36:$VO}),{12:[1,421],13:[1,422]},o($Vf,[2,414]),o($Vf,[2,412]),o($Vf,[2,413]),o($Vf,[2,419]),{105:[1,423]},{108:[1,424]},{268:[1,425]},o($Vf,[2,424],{29:[1,426],268:[1,427]}),{12:$V51,29:[1,429],37:431,38:$Vi,39:$Vj,40:$Vk,139:$Vj1,142:430,301:[1,428]},o($VS,[2,442]),o($Vf,[2,446]),o($Vf,[2,445],{34:432,35:$VN,36:$VO}),o($Vf,[2,447],{34:434,29:[1,433],35:$VN,36:$VO}),o($Vf,[2,455]),o($Vf,[2,456]),{161:[1,435]},o($Vf,[2,460]),o($Vf,[2,461]),{290:[1,436]},o($Vf,[2,464]),{12:$VX1,145:437,146:438},{290:[1,440]},{12:[1,441]},{12:[2,78]},{12:[2,79]},o($Vf,[2,470],{12:[1,442]}),{12:[1,443]},o($Vf,[2,473],{12:[1,444]}),{12:[1,445]},{268:[1,446]},{12:$V51,29:$V61,125:447,136:337,137:242,139:$V71,142:338},o($Vs,[2,42]),o($Vs,[2,43]),o($Vf,[2,478],{29:[1,448],268:[1,449]}),o($Vf,[2,489]),{289:[1,450]},o($Vf,[2,492]),o($Vf,[2,493]),{104:451,105:$VQ},o($VT,[2,116]),o($VT,[2,131]),o($VT,[2,132]),o($Vf,[2,247],{29:[1,453],200:[1,452]}),{13:[1,455],190:[1,454]},o($Vf,[2,499],{211:456,29:[1,457],147:[1,458],212:[1,459]}),o($VY1,[2,505]),{29:[1,461],42:[1,460]},o($VY1,[2,509]),o([29,42],[2,510]),o($V41,[2,152]),{106:[1,462],140:$V31},o($V41,[2,157]),o($V41,[2,159],{30:463,31:$Vx,32:$Vy,33:$Vz}),{12:$V51,13:$Va1,137:266,138:464,139:$V71,142:465},o($Vw1,[2,134]),{87:468,88:$Vf1,89:$Vg1,102:[1,467],107:466,108:$VR},{139:[1,469]},o($Vf,[2,230]),{12:$V51,139:$Vj1,142:470},{12:$V51,13:$Va1,137:266,138:471,139:$V71,142:472},o($Vf,[2,253]),o($VZ1,[2,264],{209:473,216:[1,474]}),{29:[1,476],214:[1,475]},o($V_1,[2,86]),o($V_1,[2,87]),o($V_1,[2,88]),o($V81,[2,259]),o($V81,[2,260]),o($V81,[2,270],{220:$V$1}),o($V02,[2,271]),o($V02,[2,273],{222:[1,478]}),o($VD1,$VE1,{224:370,227:371,228:372,229:374,101:375,104:376,230:377,231:380,223:479,102:$VF1,103:$VG1,105:$VQ,161:$VI1}),o($V12,[2,277]),o($V12,[2,278],{41:480,42:[1,482],43:[1,483],44:[1,484],45:[1,485],46:[1,486],47:[1,487],225:[1,481]}),o($V22,[2,283]),o($V22,[2,284]),o($VD1,$VE1,{219:366,221:367,223:369,224:370,227:371,228:372,229:374,101:375,104:376,230:377,231:380,218:488,14:489,13:$V1,29:$V5,102:$VF1,103:$VG1,105:$VQ,133:$VH1,161:$VI1}),o($V22,[2,287]),o($V22,[2,288]),o($V22,[2,289]),o($V32,[2,290]),o($V22,[2,80]),{102:[1,490]},{12:$Vg,150:493,232:491,233:492,234:$V42},{12:$V51,29:$V91,137:249,139:$V71,141:260,142:250,237:495,238:256,239:258,240:259},o($VJ1,[2,319],{242:496,243:$VK1,245:$VL1,246:$VM1,248:$VN1,249:$VO1,251:$VP1,252:$VQ1}),{243:[1,497]},{243:[2,328]},o($V52,$V62,{247:498,253:$V72}),{243:[2,331]},o($V52,$V62,{247:500,250:[1,501],253:$V72}),o($V52,$V62,{247:502,253:$V72}),o($V52,$V62,{247:503,250:[1,504],253:$V72}),o($VR1,[2,361],{259:505}),o($VR1,[2,357]),o($VR1,[2,358]),{12:$V51,137:506,139:$V71,142:507},o($V82,[2,84]),o($V82,[2,85]),{12:$Vd1,13:[1,508]},{12:$Ve1,13:[1,509]},{12:$Vg,150:510},o($VA,[2,147]),o($VA,[2,148]),o($Vf,[2,192]),{29:[1,512],84:513,85:$V92,86:$Va2,165:511},{147:[1,517],162:[1,516]},o($Vb2,[2,199]),o($Vb2,[2,201]),{29:[1,519],172:518,174:[1,520],175:[1,521],176:[1,522],177:[1,523],178:[1,524],179:[1,525],180:[1,526],181:[1,527],182:[1,528],183:[1,529],184:[1,530],185:[1,531],186:[1,532],187:[1,533]},o($Vf,[2,188]),{55:539,56:$Vc2,57:$Vd2,84:513,85:$V92,86:$Va2,155:536,158:538,159:$Ve2,163:534,164:535,165:537},o($VD,[2,113]),o($VD,[2,114]),o($Vf,[2,238]),o($Vf,[2,239]),o($Vf,[2,105]),o($Vf,[2,106]),o($Vf,[2,243]),{298:[1,543]},{290:[1,544]},o($Vf,[2,402],{142:545,12:$V51,139:$Vj1}),o($Vf,[2,405],{142:546,12:$V51,139:$Vj1}),{12:$V51,29:[1,547],139:$Vj1,142:548},o($Vm1,[2,119]),o($Vm1,[2,120]),o([6,7,29,42,43,44,45,46,47,113,114,115,147,162,212,216,217,220,222,225,304],[2,82]),o([6,7,88,89],[2,83]),{298:[1,549]},o($Vf,[2,426],{298:[1,550]}),{298:[1,551]},o($Vf,[2,432]),o($Vf,[2,433],{142:552,12:$V51,139:$Vj1}),o($Vf,[2,434]),{12:$V51,29:[1,553],139:$Vj1,142:554},{12:$V51,139:$Vj1,142:555},o($Vf,[2,448],{142:556,12:$V51,139:$Vj1}),{12:$V51,29:[1,557],139:$Vj1,142:558},{12:$VX1,145:559,146:438},{291:[1,560]},o($Vf,[2,465],{147:$Vf2}),o($Vg2,[2,141]),{42:[1,562]},{291:[1,563]},o($Vf,[2,469]),o($Vf,[2,471]),o($Vf,[2,472]),o($Vf,[2,474]),o($Vf,[2,475]),{104:564,105:$VQ},o($Vn1,[2,103]),o($Vf,[2,479],{104:565,105:$VQ}),{104:566,105:$VQ},{290:[1,567]},o($Vf,[2,494]),{29:[1,569],37:568,38:$Vi,39:$Vj,40:$Vk},o($Vf,[2,246]),{13:[1,571],191:[1,570]},o($Vh2,[2,226],{191:[1,572]}),o($Vf,[2,497]),o($Vf,[2,498]),{12:$Vu1,29:$Vv1,314:573,315:343},o($VD1,$VE1,{218:365,219:366,221:367,223:369,224:370,227:371,228:372,229:374,101:375,104:376,230:377,231:380,213:574,29:[1,575],102:$VF1,103:$VG1,105:$VQ,133:$VH1,161:$VI1}),o($VD1,$VE1,{219:366,221:367,223:369,224:370,227:371,228:372,229:374,101:375,104:376,230:377,231:380,316:576,317:577,218:578,102:$VF1,103:$VG1,105:$VQ,133:$VH1,161:$VI1}),o($VY1,[2,508]),{139:[1,579]},{12:[1,580],13:$Va1,137:266,138:582,139:[1,581]},o($Vw1,[2,135]),o($Vw1,$Vx1,{81:352,144:583,82:$VB,83:$VC}),{87:584,88:$Vf1,89:$Vg1},{87:585,88:$Vf1,89:$Vg1},o($Vw1,[2,140]),o($Vz1,[2,151]),o($VB1,[2,128]),o($VB1,[2,129]),o($VB1,[2,130]),o($VW1,[2,267],{210:586,217:[1,587]}),{29:[1,589],214:[1,588]},{12:$Vg,13:$V1,14:65,29:$V5,150:64,215:590,236:63},o($VC1,[2,263]),o($VD1,$VE1,{221:367,223:369,224:370,227:371,228:372,229:374,101:375,104:376,230:377,231:380,219:591,102:$VF1,103:$VG1,105:$VQ,133:$VH1,161:$VI1}),o($VD1,$VE1,{221:367,223:369,224:370,227:371,228:372,229:374,101:375,104:376,230:377,231:380,219:593,29:[1,592],102:$VF1,103:$VG1,105:$VQ,133:$VH1,161:$VI1}),o($V12,[2,276]),o($VD1,$VE1,{227:371,228:372,229:374,101:375,104:376,230:377,231:380,224:594,14:595,13:$V1,29:$V5,102:$VF1,103:$VG1,105:$VQ,161:$VI1}),{133:[1,597],226:[1,596]},o($Vi2,[2,34]),o($Vi2,[2,35]),o($Vi2,[2,36]),o($Vi2,[2,37]),o($Vi2,[2,38]),o($Vi2,[2,39]),{162:[1,598],220:$V$1},o($V22,[2,286]),o($V22,[2,81]),o($V32,[2,291],{30:599,31:$Vx,32:$Vy,33:$Vz}),o($Vj2,[2,293]),o($Vj2,[2,296],{13:[1,600]}),{12:[1,601]},o($VJ1,[2,314]),{243:[1,602]},{2:[1,605],12:$V51,29:[1,604],137:249,139:$V71,141:260,142:250,239:603},{29:[1,606],243:[2,329]},o($V52,[2,341]),{29:[1,607],243:[2,334]},{243:[2,333]},{29:[1,608],243:[2,335]},{29:[1,609],243:[2,339]},{243:[2,338]},o([6,7,29,113,114,115,147,212,216,217,243,245,246,248,249,251,252,254],[2,355],{260:610,264:[1,611]}),o($VR1,[2,359]),o($VR1,[2,360]),o($Vw,[2,310]),o($Vw,[2,311]),o($VT1,[2,165]),o($Vf,[2,191]),o($Vf,[2,195]),{188:612,189:$Vt1},{189:[2,68]},{189:[2,69]},o([6,7,29,85,86],[2,198]),{12:$VU1,170:613,171:405},o($Vb2,[2,202]),o($Vb2,[2,203],{173:614,2:[2,219]}),o($Vb2,[2,205]),o($Vb2,[2,206]),o($Vb2,[2,207]),o($Vb2,[2,208]),o($Vb2,[2,209]),o($Vb2,[2,210]),o($Vb2,[2,211]),o($Vb2,[2,212]),o($Vb2,[2,213]),o($Vb2,[2,214]),o($Vb2,[2,215]),o($Vb2,[2,216]),o($Vb2,[2,217]),o($Vb2,[2,218]),{2:[1,615],29:[1,616]},o($Vl1,[2,179],{84:513,155:536,165:537,158:538,55:539,164:617,56:$Vc2,57:$Vd2,85:$V92,86:$Va2,159:$Ve2}),o($Vk2,[2,182]),o($Vk2,[2,183]),o($Vk2,[2,184]),{105:[1,618]},{29:[1,620],160:[1,619]},{105:[2,46]},{105:[2,47]},o($Vf,[2,429]),{291:[1,621]},o($Vf,[2,403]),o($Vf,[2,406]),o($Vf,[2,407]),o($Vf,[2,408]),o($Vf,[2,428]),o($Vf,[2,430]),o($Vf,[2,427]),o($Vf,[2,437]),o($Vf,[2,435]),o($Vf,[2,436]),o($Vf,[2,451]),o($Vf,[2,449]),o($Vf,[2,450]),o($Vf,[2,452]),{147:$Vf2,162:[1,622]},{292:[1,623]},{12:$VX1,146:624},{104:625,105:$VQ},{292:[1,626]},o($Vf,[2,481],{304:[1,627]}),o($Vf,[2,482],{304:[1,628]}),o($Vf,[2,480],{29:[1,629],304:[1,630]}),{291:[1,631]},{12:[1,632]},o($Vf,[2,245]),o($Vh2,[2,221]),o($Vh2,[2,224],{190:[1,633],191:[1,634]}),o($Vh2,[2,225]),o($VY1,[2,506]),o($Vf,[2,256]),o($Vf,[2,257]),o($VY1,[2,507]),o($VY1,[2,511]),o($VY1,[2,512],{220:$V$1}),o($V41,[2,154]),o($V41,[2,153]),{106:[1,635],140:$V31},o($V41,[2,156]),o($Vw1,[2,136]),o($Vw1,[2,138]),o($Vw1,[2,139]),o($VW1,[2,255]),{29:[1,637],102:[1,636]},{12:$Vg,13:$V1,14:65,29:$V5,150:64,215:638,236:63},o($VZ1,[2,266]),o($VC1,[2,262],{147:$Vv}),o($V02,[2,272]),o($V02,[2,274]),o($V02,[2,275]),o($V12,[2,279]),o($V12,[2,280]),o($V12,[2,281]),{226:[1,639]},o($V22,[2,285]),{12:$Vg,13:[1,640],150:493,233:641,234:$V42},o($Vj2,[2,297]),{234:[1,642]},{12:$V51,29:[1,644],137:249,139:$V71,141:260,142:250,239:643},{29:[1,646],244:645,254:$Vl2},o($Vm2,[2,322]),o($Vm2,[2,323]),{243:[2,330]},{243:[2,332]},{243:[2,336]},{243:[2,337]},o($VR1,[2,362]),{29:[1,649],265:[1,648]},o([2,6,7,29,56,57,85,86,159],[2,220]),o($Vb2,[2,200]),{2:[1,650]},o($Vf,[2,189]),o($Vf,[2,190]),o($Vl1,[2,180],{84:513,155:536,165:537,158:538,55:539,164:651,56:$Vc2,57:$Vd2,85:$V92,86:$Va2,159:$Ve2}),o($Vk2,[2,169],{106:[1,652]}),o($Vk2,[2,177],{161:[1,653]}),o($Vk2,[2,178]),{292:[1,654]},o($Vf,[2,457],{29:[1,655],118:[1,656]}),o($Vf,[2,463]),o($Vg2,[2,142]),o($Vg2,[2,143]),o($Vf,[2,467]),{12:$VX1,145:657,146:438},{12:$VX1,145:658,146:438},o($Vf,[2,483],{146:438,145:659,12:$VX1}),{12:$VX1,145:660,146:438},{292:[1,661]},o($Vf,[2,244]),{191:[1,662]},o($Vh2,[2,223]),{139:[1,663]},o($VW1,[2,268]),o($VW1,[2,269]),o($VZ1,[2,265],{147:$Vv}),o($V12,[2,282]),o($Vj2,[2,294]),o($Vj2,[2,295]),o($Vj2,[2,298]),o($Vm2,[2,324],{244:664,254:$Vl2}),o($Vm2,[2,326]),o($Vm2,[2,320]),o($Vm2,[2,321]),o($VD1,$VE1,{230:377,231:380,255:665,256:666,257:667,229:669,13:$Vn2,29:$Vo2,161:[1,668]}),{29:[1,673],261:672,262:[1,674],263:[1,675]},o($VR1,[2,372]),o($Vb2,[2,204]),o($Vl1,[2,181]),o($Vk2,[2,170],{105:[1,676]}),{12:$Vp2,105:$Vq2,156:677,157:678},o($Vf,[2,398]),o($Vf,[2,458]),o($Vf,[2,459]),o($Vf,[2,485],{147:$Vf2}),o($Vf,[2,486],{147:$Vf2}),o($Vf,[2,487],{147:$Vf2}),o($Vf,[2,484],{147:$Vf2}),o($Vf,[2,490]),o($Vh2,[2,222]),o($V41,[2,155]),o($Vm2,[2,325]),o($Vm2,[2,342],{222:$Vr2}),o($Vm2,[2,343]),o($Vs2,[2,346]),o($VD1,$VE1,{230:377,231:380,257:667,229:669,255:682,13:$Vn2,29:$Vo2}),o($Vs2,[2,349],{42:[1,683]}),o($Vs2,[2,352]),o($Vs2,[2,353]),{12:[1,684],29:[1,686],111:$Vt2,266:685},o($VR1,[2,371]),{161:[1,688]},{161:[1,689]},o($Vk2,[2,171]),{147:[1,691],162:[1,690]},o($Vb2,[2,172]),{42:[1,692]},{106:[1,693]},o($VD1,$VE1,{230:377,231:380,229:669,257:694,13:$Vn2,29:$Vo2}),o($Vm2,[2,345],{162:[1,695],222:$Vr2}),o($VD1,$VE1,{230:377,231:380,229:696,13:[1,698],29:[1,697]}),{29:[1,700],111:$Vt2,266:699},o($VR1,[2,368]),o($VR1,[2,370]),{12:[1,701],161:[1,702]},{12:$Vg,13:$Va1,137:266,138:704,139:$Vb1,150:267,152:703},{12:$Vg,13:$Va1,137:266,138:706,139:$Vb1,150:267,152:705},o($Vk2,[2,176]),{12:$Vp2,105:$Vq2,157:707},{12:[1,708]},{105:[1,709]},o($Vs2,[2,347]),o($Vm2,[2,344]),o($Vs2,[2,348]),o($Vs2,[2,350]),o($Vs2,[2,351]),o($VR1,[2,367]),o($VR1,[2,369]),o($VR1,[2,373]),{12:[1,710]},{30:398,31:$Vx,32:$Vy,33:$Vz,162:[1,711]},{2:[1,712]},{30:398,31:$Vx,32:$Vy,33:$Vz,162:[1,713]},{2:[1,714]},o($Vb2,[2,173]),o($Vb2,[2,174]),{42:[1,715]},{147:[1,716]},o($Vu2,[2,363]),o($Vu2,[2,364]),o($Vu2,[2,365]),o($Vu2,[2,366]),{105:[1,717]},{12:[1,718]},{106:[1,719]},{162:[1,720]},{105:[1,721]},o($VR1,[2,374]),o($Vb2,[2,175])],
defaultActions: {58:[2,3],144:[2,2],229:[2,64],230:[2,65],320:[2,78],321:[2,79],384:[2,328],386:[2,331],501:[2,333],504:[2,338],514:[2,68],515:[2,69],541:[2,46],542:[2,47],606:[2,330],607:[2,332],608:[2,336],609:[2,337]},
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
    } else if (tablePrimary.identifierChain.length == 2) {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.identifierChain[0].name + '.' + tablePrimary.identifierChain[1].name + '.', type: 'table' });
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
case 6: return 301; 
break;
case 7: return 186; 
break;
case 8: return 293; 
break;
case 9: return 56; 
break;
case 10: return 294; 
break;
case 11: return 295; 
break;
case 12: determineCase(yy_.yytext); return 27; 
break;
case 13: return 245; 
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
case 23: return 296; 
break;
case 24: return 299; 
break;
case 25: return 36; 
break;
case 26: return 53; 
break;
case 27: return 54; 
break;
case 28: this.begin('hdfs'); return 79; 
break;
case 29: return 264; 
break;
case 30: return 74; 
break;
case 31: this.begin('hdfs'); return 85; 
break;
case 32: return 303; 
break;
case 33: return '<hive>MACRO'; 
break;
case 34: return 304; 
break;
case 35: return 305; 
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
case 41: return 307; 
break;
case 42: return '<hive>TEMPORARY'; 
break;
case 43: return 308; 
break;
case 44: return 100; 
break;
case 45: return 262; 
break;
case 46: return 263; 
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
case 53: return 287; 
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
case 62: return 297; 
break;
case 63: return 302; 
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
case 69: return 248; 
break;
case 70: return 75; 
break;
case 71: this.begin('hdfs'); return 86; 
break;
case 72: return 306; 
break;
case 73: return 252; 
break;
case 74: return 92; 
break;
case 75: return 95; 
break;
case 76: return 69; 
break;
case 77: return 288; 
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
case 84: return 177; 
break;
case 85: return 178; 
break;
case 86: return 214; 
break;
case 87: return 183; 
break;
case 88: determineCase(yy_.yytext); return 26; 
break;
case 89: return 49; 
break;
case 90: return 182; 
break;
case 91: return 180; 
break;
case 92: determineCase(yy_.yytext); return 196; 
break;
case 93: return 131; 
break;
case 94: return 179; 
break;
case 95: return 35; 
break;
case 96: return 253; 
break;
case 97: return 'INNER'; 
break;
case 98: return 251; 
break;
case 99: return 246; 
break;
case 100: return 113; 
break;
case 101: return 130; 
break;
case 102: return 176; 
break;
case 103: return 200; 
break;
case 104: return 225; 
break;
case 105: return 243; 
break;
case 106: return 249; 
break;
case 107: return 268; 
break;
case 108: return 133; 
break;
case 109: return 254; 
break;
case 110: return 220; 
break;
case 111: return 216; 
break;
case 112: return 'ROLE'; 
break;
case 113: return 50; 
break;
case 114: determineCase(yy_.yytext); return 201; 
break;
case 115: return 250; 
break;
case 116: return 311; 
break;
case 117: determineCase(yy_.yytext); return 267; 
break;
case 118: return 175; 
break;
case 119: return 181; 
break;
case 120: return 38; 
break;
case 121: return 185; 
break;
case 122: return 174; 
break;
case 123: determineCase(yy_.yytext); return 309; 
break;
case 124: determineCase(yy_.yytext); return 318; 
break;
case 125: return 184; 
break;
case 126: return 265; 
break;
case 127: return 212; 
break;
case 128: return 102; 
break;
case 129: return 12; 
break;
case 130: parser.yy.cursorFound = true; return 29; 
break;
case 131: parser.yy.cursorFound = true; return 13; 
break;
case 132: return 189; 
break;
case 133: return 190; 
break;
case 134: this.popState(); return 191; 
break;
case 135: return 7; 
break;
case 136: return yy_.yytext; 
break;
case 137: return yy_.yytext; 
break;
case 138: return '['; 
break;
case 139: return ']'; 
break;
case 140: this.begin('backtickedValue'); return 139; 
break;
case 141: if (yy_.yytext.indexOf('\u2020') !== -1 || yy_.yytext.indexOf('\u2021') !== -1) {
                                        this.popState();
                                        return 140;
                                      }
                                      return 106;
                                    
break;
case 142: this.popState(); return 139; 
break;
case 143: this.begin('singleQuotedValue'); return 105; 
break;
case 144: return 106; 
break;
case 145: this.popState(); return 105; 
break;
case 146: this.begin('doubleQuotedValue'); return 108; 
break;
case 147: return 106; 
break;
case 148: this.popState(); return 108; 
break;
case 149: return 7; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:AS\b)/i,/^(?:ALL\b)/i,/^(?:BINARY\b)/i,/^(?:COLUMNS\b)/i,/^(?:COMMENT\b)/i,/^(?:COMPACTIONS\b)/i,/^(?:CONF\b)/i,/^(?:CREATE\b)/i,/^(?:CROSS\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DATE\b)/i,/^(?:DESCRIBE\b)/i,/^(?:EXTENDED\b)/i,/^(?:EXTERNAL\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:IN\b)/i,/^(?:INDEX\b)/i,/^(?:INDEXES\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:LOCKS\b)/i,/^(?:MACRO\b)/i,/^(?:PARTITION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:TBLPROPERTIES\b)/i,/^(?:TEMPORARY\b)/i,/^(?:TRANSACTIONS\b)/i,/^(?:USER\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:AGGREGATE\b)/i,/^(?:ANALYTIC\b)/i,/^(?:ANTI\b)/i,/^(?:COLUMN\b)/i,/^(?:COMMENT\b)/i,/^(?:CREATE\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DESCRIBE\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:GROUP\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INCREMENTAL\b)/i,/^(?:INPATH\b)/i,/^(?:IN\b)/i,/^(?:INNER\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:RIGHT\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:STATS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:[.])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DATABASE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:DROP\b)/i,/^(?:EXISTS\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:OUTER\b)/i,/^(?:INNER\b)/i,/^(?:RIGHT\b)/i,/^(?:FULL\b)/i,/^(?:GROUP\b)/i,/^(?:IF\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:LEFT\b)/i,/^(?:LIKE\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:ROLE\b)/i,/^(?:SCHEMA\b)/i,/^(?:SELECT\b)/i,/^(?:SEMI\b)/i,/^(?:SET\b)/i,/^(?:SHOW\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:\s+['])/i,/^(?:[^'\u2020\u2021]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>]+)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:[^"]+)/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[130,131,132,133,134,135],"inclusive":false},"doubleQuotedValue":{"rules":[147,148],"inclusive":false},"singleQuotedValue":{"rules":[144,145],"inclusive":false},"backtickedValue":{"rules":[141,142],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,136,137,138,139,140,143,146,149],"inclusive":true},"impala":{"rules":[0,1,2,3,4,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,136,137,138,139,140,143,146,149],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,136,137,138,139,140,143,146,149],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});