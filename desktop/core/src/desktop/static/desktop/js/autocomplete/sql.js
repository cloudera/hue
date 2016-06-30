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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,9],$V1=[1,20],$V2=[1,52],$V3=[1,53],$V4=[1,54],$V5=[1,19],$V6=[1,57],$V7=[1,58],$V8=[1,55],$V9=[1,56],$Va=[1,26],$Vb=[1,18],$Vc=[1,29],$Vd=[1,51],$Ve=[1,49],$Vf=[6,7],$Vg=[1,75],$Vh=[1,76],$Vi=[1,67],$Vj=[2,6,7,30,36,37,43,44,45,46,47,48,78,114,115,116,138,152,170,230,239,249,250,251,254,258,261,268,282],$Vk=[2,25],$Vl=[1,82],$Vm=[1,83],$Vn=[1,84],$Vo=[1,85],$Vp=[1,86],$Vq=[1,133],$Vr=[1,134],$Vs=[1,147],$Vt=[30,39,40,41,50,51,72,73],$Vu=[13,30,145],$Vv=[30,64,65],$Vw=[6,7,170],$Vx=[2,260],$Vy=[1,163],$Vz=[2,6,7,170],$VA=[1,166],$VB=[6,7,30,36,170],$VC=[2,6,7,36,170],$VD=[2,407],$VE=[6,7,30,36,152,170],$VF=[2,533],$VG=[1,180],$VH=[1,181],$VI=[1,179],$VJ=[2,6,7,13,30,36,103,111,112,145,152,170,239,249,250,251,254],$VK=[2,420],$VL=[1,185],$VM=[1,186],$VN=[1,187],$VO=[2,6,7,13,14,30,32,33,34,36,37,43,44,45,46,47,48,78,103,111,112,114,115,116,138,145,152,170,230,239,249,250,251,254,258,261,268,282,317,322,323,325,326,328,329],$VP=[2,6,7,13,14,30,32,33,34,36,37,43,44,45,46,47,48,78,83,84,103,106,111,112,114,115,116,131,132,138,145,152,170,230,239,249,250,251,254,258,261,268,282,317,322,323,325,326,328,329,331,366,370],$VQ=[1,192],$VR=[6,7,13],$VS=[39,40,41],$VT=[6,7,13,30,134,145,169],$VU=[6,7,13,30,119,134,145],$VV=[6,7,13,30,145],$VW=[2,109],$VX=[1,202],$VY=[6,7,13,30,145,169],$VZ=[1,210],$V_=[1,212],$V$=[1,213],$V01=[1,218],$V11=[1,219],$V21=[30,370],$V31=[1,230],$V41=[1,232],$V51=[6,7,331],$V61=[6,7,30,106,370],$V71=[2,117],$V81=[1,259],$V91=[1,260],$Va1=[30,39,40,41],$Vb1=[30,95,96],$Vc1=[30,400],$Vd1=[6,7,30,331],$Ve1=[30,402,406],$Vf1=[6,7,30,37,78,106,370],$Vg1=[30,80,81],$Vh1=[6,7,30,415],$Vi1=[1,274],$Vj1=[6,7,13,30,119,392,408,415],$Vk1=[2,6,7,30,114,115,116,170,239,254],$Vl1=[2,285],$Vm1=[1,292],$Vn1=[2,6,7,114,115,116,170,239,254],$Vo1=[1,295],$Vp1=[1,315],$Vq1=[1,322],$Vr1=[1,323],$Vs1=[2,6,7,36,152,170],$Vt1=[2,6,7,30,36,152,170],$Vu1=[2,6,7,30,36,114,115,116,152,170,230,239,254,317,322,323,325,326,328,329,331,366],$Vv1=[2,6,7,36,114,115,116,152,170,230,239,254,317,322,323,325,326,328,329,331],$Vw1=[1,335],$Vx1=[1,332],$Vy1=[13,14,109,145,301],$Vz1=[2,28],$VA1=[2,29],$VB1=[1,340],$VC1=[1,341],$VD1=[89,90,103,109],$VE1=[1,346],$VF1=[6,7,370],$VG1=[6,7,30,119,392,408],$VH1=[2,30],$VI1=[6,7,34],$VJ1=[6,7,30,370],$VK1=[1,393],$VL1=[1,394],$VM1=[1,401],$VN1=[1,402],$VO1=[2,103],$VP1=[1,415],$VQ1=[1,418],$VR1=[1,423],$VS1=[1,422],$VT1=[2,6,7,13,30,32,33,34,36,103,111,112,145,152,170,239,249,250,251,254],$VU1=[2,6,7,13,30,111,112,114,115,116,145,152,170,230,239,254,317,322,323,325,326,328,329,331,366],$VV1=[2,129],$VW1=[2,6,7,13,111,112,114,115,116,145,152,170,230,239,254,317,322,323,325,326,328,329,331,366],$VX1=[2,273],$VY1=[2,6,7,30,170,239,254],$VZ1=[2,289],$V_1=[1,440],$V$1=[1,441],$V02=[1,442],$V12=[2,6,7,170,239,254],$V22=[1,478],$V32=[1,479],$V42=[1,454],$V52=[1,472],$V62=[1,488],$V72=[1,490],$V82=[2,277],$V92=[2,6,7,114,115,116,170,230,239,254],$Va2=[2,6,7,30,114,115,116,152,170,230,239,254],$Vb2=[2,6,7,114,115,116,152,170,230,239,254],$Vc2=[2,434],$Vd2=[2,462],$Ve2=[1,500],$Vf2=[1,501],$Vg2=[1,502],$Vh2=[1,503],$Vi2=[1,504],$Vj2=[1,505],$Vk2=[1,508],$Vl2=[1,509],$Vm2=[1,510],$Vn2=[1,511],$Vo2=[2,6,7,30,114,115,116,152,170,230,239,254,317,322,323,325,326,328,329,331,366],$Vp2=[2,6,7,30,114,115,116,152,170,230,239,254,317,322,323,325,326,328,329,331],$Vq2=[2,6,7,114,115,116,152,170,230,239,254,317,322,323,325,326,328,329,331,366],$Vr2=[2,6,7,114,115,116,152,170,230,239,254,317,322,323,325,326,328,329,331],$Vs2=[2,512],$Vt2=[2,422],$Vu2=[1,528],$Vv2=[1,529],$Vw2=[2,6,7,13,36,111,112,145,152,170,239,249,250,251,254],$Vx2=[2,6,7,13,30,36,111,112,114,115,116,119,145,152,170,230,239,249,250,251,254,317,322,323,325,326,328,329,331,366,392,408,415],$Vy2=[1,538],$Vz2=[2,30,86,87,167],$VA2=[2,187],$VB2=[2,106],$VC2=[1,549],$VD2=[1,550],$VE2=[1,578],$VF2=[6,7,30,152,230],$VG2=[2,6,7,30,170,254],$VH2=[2,303],$VI2=[2,6,7,170,254],$VJ2=[1,614],$VK2=[30,233],$VL2=[2,331],$VM2=[1,619],$VN2=[1,620],$VO2=[2,6,7,30,114,115,116,152,170,230,239,254,258],$VP2=[2,338],$VQ2=[2,6,7,30,114,115,116,152,170,230,239,254,258,261],$VR2=[2,350],$VS2=[1,626],$VT2=[2,6,7,30,114,115,116,152,170,230,239,254,258,261,268],$VU2=[2,357],$VV2=[1,640],$VW2=[1,631],$VX2=[1,632],$VY2=[1,633],$VZ2=[1,634],$V_2=[1,635],$V$2=[1,636],$V03=[1,641],$V13=[1,639],$V23=[1,645],$V33=[2,6,7,30,37,43,44,45,46,47,48,78,114,115,116,138,152,170,230,239,254,258,261,268,282],$V43=[2,6,7,30,37,43,44,45,46,47,48,78,114,115,116,138,152,170,230,239,254,258,261,268,282,317,322,323,325,326,328,329],$V53=[2,394],$V63=[2,6,7,30,32,33,34,37,43,44,45,46,47,48,78,114,115,116,138,152,170,230,239,254,258,261,268,282,317,322,323,325,326,328,329],$V73=[2,401],$V83=[1,653],$V93=[2,438],$Va3=[2,6,7,114,115,116,152,170,230,239,254,317,322,323,325,326,328,329],$Vb3=[30,317],$Vc3=[2,475],$Vd3=[1,668],$Ve3=[1,669],$Vf3=[1,672],$Vg3=[2,539],$Vh3=[13,145],$Vi3=[1,708],$Vj3=[1,709],$Vk3=[152,170],$Vl3=[2,30,167],$Vm3=[1,752],$Vn3=[6,7,152,170],$Vo3=[2,6,7,30,167,210],$Vp3=[2,6,7,30,170],$Vq3=[2,328],$Vr3=[1,778],$Vs3=[1,789],$Vt3=[271,272],$Vu3=[13,14,30,103,104,106,109,145,169],$Vv3=[30,169],$Vw3=[1,814],$Vx3=[2,464],$Vy3=[2,467],$Vz3=[2,468],$VA3=[2,470],$VB3=[2,502],$VC3=[1,835],$VD3=[2,513],$VE3=[2,170],$VF3=[1,865],$VG3=[2,290],$VH3=[2,6,7,13,30,103,145,152,170,239,254],$VI3=[2,6,7,13,30,103,145,152,170,239,249,250,251,254],$VJ3=[2,6,7,30,114,115,116,152,170,230,239,254,317,322,323,325,326,328,329],$VK3=[2,441],$VL3=[1,892],$VM3=[1,894],$VN3=[2,6,7,13,30,111,112,114,115,116,145,152,170,230,239,254,258,261,268,317,322,323,325,326,328,329,331],$VO3=[2,304],$VP3=[2,6,7,30,152,170,254],$VQ3=[2,6,7,30,152,170,251,254],$VR3=[2,321],$VS3=[1,922],$VT3=[1,923],$VU3=[2,6,7,152,170,251,254],$VV3=[1,926],$VW3=[2,443],$VX3=[1,948],$VY3=[2,324],$VZ3=[2,6,7,152,170,254],$V_3=[1,967],$V$3=[2,6,7,152,170,239,254],$V04=[2,480],$V14=[1,971],$V24=[1,973],$V34=[1,972],$V44=[2,6,7,30,114,115,116,152,170,230,239,254,261,317,322,323,325,326,328,329],$V54=[1,981],$V64=[1,982],$V74=[1,988],$V84=[1,997],$V94=[1,998],$Va4=[1,1000],$Vb4=[1,1001],$Vc4=[1,1010],$Vd4=[2,6,7,114,115,116,152,170,230,239,254,261,317,322,323,325,326,328,329],$Ve4=[13,30,112];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"InitResults":3,"Sql":4,"SqlStatements":5,";":6,"EOF":7,"SqlStatement":8,"DataDefinition":9,"DataManipulation":10,"QuerySpecification_Complete":11,"QuerySpecification_Cursored":12,"REGULAR_IDENTIFIER":13,"PARTIAL_CURSOR":14,"AnyCursor":15,"CreateStatement":16,"DescribeStatement":17,"DropStatement":18,"ShowStatement":19,"UseStatement":20,"LoadStatement":21,"UpdateStatement":22,"AggregateOrAnalytic":23,"<impala>AGGREGATE":24,"<impala>ANALYTIC":25,"AnyCreate":26,"CREATE":27,"<hive>CREATE":28,"<impala>CREATE":29,"CURSOR":30,"AnyDot":31,".":32,"<impala>.":33,"<hive>.":34,"AnyFromOrIn":35,"FROM":36,"<hive>IN":37,"AnyTable":38,"TABLE":39,"<hive>TABLE":40,"<impala>TABLE":41,"ComparisonOperators":42,"=":43,"<>":44,"<=":45,">=":46,"<":47,">":48,"DatabaseOrSchema":49,"DATABASE":50,"SCHEMA":51,"FromOrIn":52,"HiveIndexOrIndexes":53,"<hive>INDEX":54,"<hive>INDEXES":55,"HiveOrImpalaComment":56,"<hive>COMMENT":57,"<impala>COMMENT":58,"HiveOrImpalaCreate":59,"HiveOrImpalaCurrent":60,"<hive>CURRENT":61,"<impala>CURRENT":62,"HiveOrImpalaData":63,"<hive>DATA":64,"<impala>DATA":65,"HiveOrImpalaDatabasesOrSchemas":66,"<hive>DATABASES":67,"<hive>SCHEMAS":68,"<impala>DATABASES":69,"<impala>SCHEMAS":70,"HiveOrImpalaExternal":71,"<hive>EXTERNAL":72,"<impala>EXTERNAL":73,"HiveOrImpalaLoad":74,"<hive>LOAD":75,"<impala>LOAD":76,"HiveOrImpalaIn":77,"<impala>IN":78,"HiveOrImpalaInpath":79,"<hive>INPATH":80,"<impala>INPATH":81,"HiveOrImpalaLeftSquareBracket":82,"<hive>[":83,"<impala>[":84,"HiveOrImpalaLocation":85,"<hive>LOCATION":86,"<impala>LOCATION":87,"HiveOrImpalaRightSquareBracket":88,"<hive>]":89,"<impala>]":90,"HiveOrImpalaRole":91,"<hive>ROLE":92,"<impala>ROLE":93,"HiveOrImpalaRoles":94,"<hive>ROLES":95,"<impala>ROLES":96,"HiveOrImpalaTables":97,"<hive>TABLES":98,"<impala>TABLES":99,"HiveRoleOrUser":100,"<hive>USER":101,"SignedInteger_Complete":102,"UNSIGNED_INTEGER":103,"-":104,"SingleQuotedValue_Complete":105,"SINGLE_QUOTE":106,"VALUE":107,"DoubleQuotedValue_Complete":108,"DOUBLE_QUOTE":109,"AnyAs":110,"AS":111,"<hive>AS":112,"AnyGroup":113,"GROUP":114,"<hive>GROUP":115,"<impala>GROUP":116,"OptionalAggregateOrAnalytic":117,"OptionalExtended":118,"<hive>EXTENDED":119,"OptionalExtendedOrFormatted":120,"<hive>FORMATTED":121,"OptionalFormatted":122,"<impala>FORMATTED":123,"OptionallyFormattedIndex_Complete":124,"OptionallyFormattedIndex_Cursored":125,"OptionalFromDatabase_Complete":126,"DatabaseIdentifier_Complete":127,"OptionalFromDatabase_Cursored":128,"DatabaseIdentifier_Cursored":129,"OptionalHiveCascadeOrRestrict_Complete":130,"<hive>CASCADE":131,"<hive>RESTRICT":132,"OptionalIfExists_Complete":133,"IF":134,"EXISTS":135,"OptionalIfExists_Cursored":136,"OptionalIfNotExists_Complete":137,"NOT":138,"OptionalIfNotExists_Cursored":139,"OptionalInDatabase":140,"ConfigurationName":141,"PartialBacktickedOrCursor":142,"PartialBacktickedIdentifier":143,"PartialBacktickedOrPartialCursor":144,"BACKTICK":145,"PARTIAL_VALUE":146,"SchemaQualifiedTableIdentifier_Complete":147,"RegularOrBacktickedIdentifier":148,"SchemaQualifiedTableIdentifier_Cursored":149,"PartitionSpecList":150,"PartitionSpec":151,",":152,"CleanRegularOrBackTickedSchemaQualifiedName":153,"RegularOrBackTickedSchemaQualifiedName":154,"LocalOrSchemaQualifiedName":155,"DerivedColumnChain_Complete":156,"ColumnIdentifier_Complete":157,"DerivedColumnChain_Cursored":158,"OptionalMapOrArrayKey_Complete":159,"ColumnIdentifier_Cursored":160,"TableDefinition":161,"DatabaseDefinition":162,"Comment":163,"HivePropertyAssignmentList":164,"HivePropertyAssignment":165,"HiveDbProperties":166,"<hive>WITH":167,"DBPROPERTIES":168,"(":169,")":170,"DatabaseDefinitionOptionals":171,"OptionalComment":172,"OptionalHdfsLocation":173,"OptionalHiveDbProperties":174,"HdfsLocation":175,"TableScope":176,"TableElementList":177,"TableElements":178,"TableElement":179,"ColumnDefinition":180,"PrimitiveType":181,"ColumnDefinitionError":182,"TINYINT":183,"SMALLINT":184,"INT":185,"BIGINT":186,"BOOLEAN":187,"FLOAT":188,"DOUBLE":189,"STRING":190,"DECIMAL":191,"CHAR":192,"VARCHAR":193,"TIMESTAMP":194,"<hive>BINARY":195,"<hive>DATE":196,"HdfsPath":197,"HDFS_START_QUOTE":198,"HDFS_PATH":199,"HDFS_END_QUOTE":200,"HiveDescribeStatement":201,"ImpalaDescribeStatement":202,"<hive>DESCRIBE":203,"<impala>DESCRIBE":204,"DROP":205,"DropDatabaseStatement":206,"DropTableStatement":207,"TablePrimary_Complete":208,"TablePrimary_Cursored":209,"INTO":210,"SELECT":211,"SelectList_Complete":212,"TableExpression_Complete":213,"SelectList_Cursored":214,"TableExpression_Cursored":215,"FromClause_Complete":216,"SelectConditions_Complete":217,"SelectConditions_Cursored":218,"FromClause_Cursored":219,"TableReferenceList_Complete":220,"TableReferenceList_Cursored":221,"OptionalWhereClause_Complete":222,"OptionalGroupByClause_Complete":223,"OptionalOrderByClause_Complete":224,"OptionalLimitClause_Complete":225,"OptionalWhereClause_Cursored":226,"OptionalGroupByClause_Cursored":227,"OptionalOrderByClause_Cursored":228,"OptionalLimitClause_Cursored":229,"WHERE":230,"SearchCondition_Complete":231,"SearchCondition_Cursored":232,"BY":233,"GroupByColumnList_Complete":234,"GroupByColumnList_Cursored":235,"DerivedColumnOrUnsignedInteger_Complete":236,"DerivedColumnOrUnsignedInteger_Cursored":237,"GroupByColumnListPartTwo_Cursored":238,"ORDER":239,"OrderByColumnList_Complete":240,"OrderByColumnList_Cursored":241,"OrderByIdentifier_Complete":242,"OrderByIdentifier_Cursored":243,"OptionalAscOrDesc_Complete":244,"OptionalImpalaNullsFirstOrLast_Complete":245,"OptionalImpalaNullsFirstOrLast_Cursored":246,"DerivedColumn_Complete":247,"DerivedColumn_Cursored":248,"ASC":249,"DESC":250,"<impala>NULLS":251,"<impala>FIRST":252,"<impala>LAST":253,"LIMIT":254,"BooleanValueExpression_Complete":255,"BooleanValueExpression_Cursored":256,"BooleanTerm_Complete":257,"OR":258,"BooleanTerm_Cursored":259,"BooleanFactor_Complete":260,"AND":261,"BooleanFactor_Cursored":262,"BooleanTest_Complete":263,"BooleanTest_Cursored":264,"BooleanPrimary_Complete":265,"OptionalIsNotTruthValue_Complete":266,"BooleanPrimary_Cursored":267,"IS":268,"OptionalNot_Complete":269,"TruthValue_Complete":270,"TRUE":271,"FALSE":272,"Predicate_Complete":273,"BooleanPredicand_Complete":274,"Predicate_Cursored":275,"BooleanPredicand_Cursored":276,"ComparisonPredicate_Complete":277,"InPredicate_Complete":278,"ComparisonPredicate_Cursored":279,"InPredicate_Cursored":280,"AnyIn":281,"IN":282,"ParenthesizedBooleanValueExpression_Complete":283,"NonParenthesizedValueExpressionPrimary_Complete":284,"CommonValueExpression_Complete":285,"ParenthesizedBooleanValueExpression_Cursored":286,"NonParenthesizedValueExpressionPrimary_Cursored":287,"InPredicatePartTwo_Complete":288,"InPredicatePartTwo_Cursored":289,"InPredicateValue_Complete":290,"InPredicateValue_Cursored":291,"TableSubquery_Complete":292,"TableSubquery_Cursored":293,"ColumnReference_Complete":294,"ColumnReference_Cursored":295,"BasicIdentifierChain_Complete":296,"BasicIdentifierChain_Cursored":297,"Identifier_Complete":298,"Identifier_Cursored":299,"SelectSubList_Complete":300,"*":301,"SelectSubList_Cursored":302,"ColumnList_Complete":303,"ColumnList_Cursored":304,"OptionalCorrelationName_Complete":305,"OptionalCorrelationName_Cursored":306,"ColumnListPartTwo_Cursored":307,"TableReference_Complete":308,"TableReference_Cursored":309,"TablePrimaryOrJoinedTable_Complete":310,"TablePrimaryOrJoinedTable_Cursored":311,"JoinedTable_Complete":312,"JoinedTable_Cursored":313,"Joins_Complete":314,"Joins_Cursored":315,"JoinTypes_Complete":316,"JOIN":317,"JoinCondition_Complete":318,"JoinTypes_Cursored":319,"JoinCondition_Cursored":320,"JoinsTableSuggestions_Cursored":321,"<hive>CROSS":322,"FULL":323,"OptionalOuter":324,"<impala>INNER":325,"LEFT":326,"SEMI":327,"RIGHT":328,"<impala>RIGHT":329,"OUTER":330,"ON":331,"JoinEqualityExpression_Cursored":332,"ParenthesizedJoinEqualityExpression_Cursored":333,"JoinEqualityExpression_Complete":334,"ParenthesizedJoinEqualityExpression_Complete":335,"EqualityExpression_Complete":336,"EqualityExpression_Cursored":337,"TableOrQueryName_Complete":338,"OptionalLateralViews_Complete":339,"DerivedTable_Complete":340,"TableOrQueryName_Cursored":341,"OptionalLateralViews_Cursored":342,"DerivedTable_Cursored":343,"PushQueryState":344,"PopQueryState":345,"Subquery_Complete":346,"Subquery_Cursored":347,"QueryExpression_Complete":348,"QueryExpression_Cursored":349,"QueryExpressionBody_Complete":350,"QueryExpressionBody_Cursored":351,"NonJoinQueryExpression_Complete":352,"NonJoinQueryExpression_Cursored":353,"NonJoinQueryTerm_Complete":354,"NonJoinQueryTerm_Cursored":355,"NonJoinQueryPrimary_Complete":356,"NonJoinQueryPrimary_Cursored":357,"SimpleTable_Complete":358,"SimpleTable_Cursored":359,"LateralView_Complete":360,"LateralView_Cursored":361,"UserDefinedTableGeneratingFunction_Complete":362,"<hive>explode":363,"<hive>posexplode":364,"UserDefinedTableGeneratingFunction_Cursored":365,"<hive>LATERAL":366,"VIEW":367,"LateralViewColumnAliases_Complete":368,"SHOW":369,"LIKE":370,"ShowColumnStatement":371,"ShowColumnsStatement":372,"ShowCompactionsStatement":373,"ShowConfStatement":374,"ShowCreateTableStatement":375,"ShowCurrentStatement":376,"ShowDatabasesStatement":377,"ShowFunctionsStatement":378,"ShowGrantStatement_Complete":379,"ShowGrantStatement_Cursored":380,"ShowIndexStatement":381,"ShowLocksStatement":382,"ShowPartitionsStatement":383,"ShowRoleStatement":384,"ShowRolesStatement":385,"ShowTableStatement":386,"ShowTablesStatement":387,"ShowTblPropertiesStatement":388,"ShowTransactionsStatement":389,"<impala>COLUMN":390,"<impala>STATS":391,"if":392,"partial":393,"identifierChain":394,"length":395,"<hive>COLUMNS":396,"<hive>COMPACTIONS":397,"<hive>CONF":398,"<hive>FUNCTIONS":399,"<impala>FUNCTIONS":400,"SingleQuoteValue":401,"<hive>GRANT":402,"OptionalPrincipalName_Complete":403,"<hive>ALL":404,"OptionalPrincipalName_Cursored":405,"<impala>GRANT":406,"<hive>LOCKS":407,"<hive>PARTITION":408,"<hive>PARTITIONS":409,"<impala>PARTITIONS":410,"<hive>TBLPROPERTIES":411,"<hive>TRANSACTIONS":412,"UPDATE":413,"TargetTable":414,"SET":415,"SetClauseList":416,"TableName":417,"SetClause":418,"SetTarget":419,"UpdateSource":420,"ValueExpression":421,"USE":422,"$accept":0,"$end":1},
terminals_: {2:"error",6:";",7:"EOF",13:"REGULAR_IDENTIFIER",14:"PARTIAL_CURSOR",24:"<impala>AGGREGATE",25:"<impala>ANALYTIC",27:"CREATE",28:"<hive>CREATE",29:"<impala>CREATE",30:"CURSOR",32:".",33:"<impala>.",34:"<hive>.",36:"FROM",37:"<hive>IN",39:"TABLE",40:"<hive>TABLE",41:"<impala>TABLE",43:"=",44:"<>",45:"<=",46:">=",47:"<",48:">",50:"DATABASE",51:"SCHEMA",54:"<hive>INDEX",55:"<hive>INDEXES",57:"<hive>COMMENT",58:"<impala>COMMENT",61:"<hive>CURRENT",62:"<impala>CURRENT",64:"<hive>DATA",65:"<impala>DATA",67:"<hive>DATABASES",68:"<hive>SCHEMAS",69:"<impala>DATABASES",70:"<impala>SCHEMAS",72:"<hive>EXTERNAL",73:"<impala>EXTERNAL",75:"<hive>LOAD",76:"<impala>LOAD",78:"<impala>IN",80:"<hive>INPATH",81:"<impala>INPATH",83:"<hive>[",84:"<impala>[",86:"<hive>LOCATION",87:"<impala>LOCATION",89:"<hive>]",90:"<impala>]",92:"<hive>ROLE",93:"<impala>ROLE",95:"<hive>ROLES",96:"<impala>ROLES",98:"<hive>TABLES",99:"<impala>TABLES",101:"<hive>USER",103:"UNSIGNED_INTEGER",104:"-",106:"SINGLE_QUOTE",107:"VALUE",109:"DOUBLE_QUOTE",111:"AS",112:"<hive>AS",114:"GROUP",115:"<hive>GROUP",116:"<impala>GROUP",119:"<hive>EXTENDED",121:"<hive>FORMATTED",123:"<impala>FORMATTED",131:"<hive>CASCADE",132:"<hive>RESTRICT",134:"IF",135:"EXISTS",138:"NOT",145:"BACKTICK",146:"PARTIAL_VALUE",152:",",167:"<hive>WITH",168:"DBPROPERTIES",169:"(",170:")",183:"TINYINT",184:"SMALLINT",185:"INT",186:"BIGINT",187:"BOOLEAN",188:"FLOAT",189:"DOUBLE",190:"STRING",191:"DECIMAL",192:"CHAR",193:"VARCHAR",194:"TIMESTAMP",195:"<hive>BINARY",196:"<hive>DATE",198:"HDFS_START_QUOTE",199:"HDFS_PATH",200:"HDFS_END_QUOTE",203:"<hive>DESCRIBE",204:"<impala>DESCRIBE",205:"DROP",210:"INTO",211:"SELECT",230:"WHERE",233:"BY",239:"ORDER",249:"ASC",250:"DESC",251:"<impala>NULLS",252:"<impala>FIRST",253:"<impala>LAST",254:"LIMIT",258:"OR",261:"AND",268:"IS",271:"TRUE",272:"FALSE",282:"IN",301:"*",317:"JOIN",322:"<hive>CROSS",323:"FULL",325:"<impala>INNER",326:"LEFT",327:"SEMI",328:"RIGHT",329:"<impala>RIGHT",330:"OUTER",331:"ON",363:"<hive>explode",364:"<hive>posexplode",366:"<hive>LATERAL",367:"VIEW",369:"SHOW",370:"LIKE",390:"<impala>COLUMN",391:"<impala>STATS",392:"if",393:"partial",394:"identifierChain",395:"length",396:"<hive>COLUMNS",397:"<hive>COMPACTIONS",398:"<hive>CONF",399:"<hive>FUNCTIONS",400:"<impala>FUNCTIONS",401:"SingleQuoteValue",402:"<hive>GRANT",404:"<hive>ALL",406:"<impala>GRANT",407:"<hive>LOCKS",408:"<hive>PARTITION",409:"<hive>PARTITIONS",410:"<impala>PARTITIONS",411:"<hive>TBLPROPERTIES",412:"<hive>TRANSACTIONS",413:"UPDATE",415:"SET",422:"USE"},
productions_: [0,[3,0],[4,4],[4,3],[5,1],[5,3],[8,1],[8,1],[8,1],[8,1],[8,3],[8,2],[8,1],[9,1],[9,1],[9,1],[9,1],[9,1],[10,1],[10,1],[23,1],[23,1],[26,1],[26,1],[26,1],[15,1],[15,1],[31,1],[31,1],[31,1],[35,1],[35,1],[38,1],[38,1],[38,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[49,1],[49,1],[52,1],[52,1],[53,1],[53,1],[56,1],[56,1],[59,1],[59,1],[60,1],[60,1],[63,1],[63,1],[66,1],[66,1],[66,1],[66,1],[71,1],[71,1],[74,1],[74,1],[77,1],[77,1],[79,1],[79,1],[82,1],[82,1],[85,1],[85,1],[88,1],[88,1],[91,1],[91,1],[94,1],[94,1],[97,1],[97,1],[100,1],[100,1],[102,1],[102,2],[105,3],[108,3],[110,1],[110,1],[113,1],[113,1],[113,1],[117,0],[117,1],[118,0],[118,1],[120,0],[120,1],[120,1],[122,0],[122,1],[124,2],[124,1],[125,2],[125,2],[126,0],[126,2],[128,2],[130,0],[130,1],[130,1],[133,0],[133,2],[136,2],[137,0],[137,3],[139,1],[139,2],[139,3],[140,0],[140,2],[140,2],[141,1],[141,1],[141,3],[141,3],[142,1],[142,1],[144,1],[144,1],[143,2],[147,1],[147,3],[149,1],[149,3],[149,3],[127,1],[129,1],[150,1],[150,3],[151,3],[153,1],[153,1],[148,1],[148,3],[154,3],[154,5],[154,5],[154,7],[154,5],[154,3],[154,1],[154,3],[155,1],[155,2],[155,1],[155,2],[156,1],[156,3],[158,3],[158,3],[157,2],[160,2],[159,0],[159,3],[159,3],[159,2],[16,1],[16,1],[16,2],[163,2],[163,3],[163,4],[164,1],[164,3],[165,3],[165,7],[166,5],[166,2],[166,2],[171,3],[172,0],[172,1],[173,0],[173,1],[174,0],[174,1],[162,3],[162,3],[162,4],[162,4],[162,6],[162,6],[161,6],[161,5],[161,4],[161,3],[161,6],[161,4],[176,1],[177,3],[178,1],[178,3],[179,1],[180,2],[180,2],[180,4],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[181,1],[182,0],[175,2],[197,3],[197,5],[197,4],[197,3],[197,3],[197,2],[17,1],[17,1],[201,3],[201,3],[201,3],[201,4],[201,4],[202,3],[202,3],[202,4],[202,3],[18,2],[18,1],[18,1],[206,3],[206,3],[206,4],[206,5],[206,5],[206,5],[207,3],[207,3],[207,4],[207,4],[207,4],[207,4],[207,5],[21,7],[21,6],[21,5],[21,4],[21,3],[21,2],[11,2],[11,3],[12,2],[12,2],[12,3],[12,3],[12,3],[12,3],[12,3],[12,4],[12,5],[12,6],[12,3],[213,2],[215,2],[215,2],[215,3],[216,2],[219,2],[219,2],[217,4],[218,4],[218,4],[218,4],[218,4],[222,0],[222,2],[226,2],[226,2],[223,0],[223,3],[227,3],[227,3],[227,2],[234,1],[234,2],[235,1],[235,2],[235,3],[235,4],[235,5],[238,1],[238,1],[224,0],[224,3],[228,3],[228,2],[240,1],[240,3],[241,1],[241,2],[241,3],[241,4],[241,5],[242,3],[243,3],[243,3],[243,3],[236,1],[236,1],[237,1],[244,0],[244,1],[244,1],[245,0],[245,2],[245,2],[246,2],[225,0],[225,2],[229,2],[231,1],[232,1],[255,1],[255,3],[256,1],[256,3],[256,3],[257,1],[257,3],[259,1],[259,3],[259,3],[259,3],[260,2],[260,1],[262,2],[262,1],[263,2],[264,2],[266,0],[266,3],[270,1],[270,1],[269,0],[269,1],[265,1],[265,1],[267,1],[267,1],[273,1],[273,1],[275,1],[275,1],[281,1],[281,1],[281,1],[277,3],[279,3],[279,3],[279,3],[274,1],[274,1],[274,1],[276,1],[276,1],[285,1],[285,1],[278,2],[280,2],[280,2],[288,2],[288,3],[289,2],[289,2],[289,3],[289,2],[290,1],[291,1],[283,3],[286,3],[286,2],[284,1],[287,1],[294,1],[295,1],[296,1],[296,3],[297,1],[297,3],[297,3],[298,1],[298,1],[299,2],[212,1],[212,1],[214,1],[300,1],[302,1],[303,2],[303,4],[304,2],[304,2],[304,2],[304,4],[304,3],[304,4],[304,5],[307,1],[307,1],[247,1],[247,3],[247,3],[248,3],[248,5],[248,5],[220,1],[220,3],[221,1],[221,3],[221,3],[221,3],[308,1],[309,1],[310,1],[310,1],[311,1],[311,1],[312,2],[313,2],[313,2],[314,3],[314,4],[314,4],[314,5],[315,3],[315,3],[315,4],[315,4],[315,4],[315,4],[315,4],[315,4],[315,5],[315,5],[315,5],[315,5],[315,1],[321,3],[321,4],[321,4],[321,5],[316,0],[316,1],[316,2],[316,1],[316,2],[316,2],[316,2],[316,2],[316,2],[319,3],[319,3],[319,3],[319,3],[324,0],[324,1],[320,2],[320,2],[320,2],[318,2],[318,2],[335,3],[333,3],[333,2],[333,4],[334,1],[334,3],[332,1],[332,3],[332,3],[332,3],[332,3],[332,5],[332,5],[336,3],[337,3],[337,3],[337,3],[337,3],[337,3],[337,3],[208,3],[208,2],[209,3],[209,3],[209,2],[209,2],[338,1],[341,1],[340,1],[343,1],[344,0],[345,0],[292,5],[293,5],[293,5],[293,4],[293,4],[346,1],[347,1],[348,1],[349,1],[350,1],[351,1],[352,1],[353,1],[354,1],[355,1],[356,1],[357,1],[358,1],[359,1],[305,0],[305,1],[305,2],[306,1],[306,2],[306,2],[339,0],[339,2],[342,3],[362,4],[362,4],[365,3],[365,3],[360,5],[360,4],[361,4],[361,5],[361,4],[361,3],[361,2],[368,2],[368,6],[19,2],[19,3],[19,4],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[19,1],[371,3],[371,4],[371,8],[372,3],[372,4],[372,4],[372,5],[372,6],[372,4],[372,5],[372,6],[372,6],[372,6],[373,2],[374,3],[375,3],[375,4],[375,4],[375,4],[376,3],[376,3],[376,3],[377,3],[377,4],[377,3],[378,2],[378,3],[378,3],[378,4],[378,4],[378,5],[378,6],[378,6],[378,6],[378,6],[379,3],[379,5],[379,5],[379,6],[380,3],[380,5],[380,5],[380,6],[380,6],[380,3],[403,0],[403,1],[405,1],[405,2],[381,2],[381,4],[381,6],[381,2],[381,4],[381,6],[381,3],[381,4],[381,4],[381,5],[381,6],[381,6],[381,6],[382,3],[382,3],[382,4],[382,4],[382,7],[382,8],[382,8],[382,4],[382,4],[383,3],[383,7],[383,4],[383,5],[383,3],[383,7],[384,3],[384,5],[384,4],[384,5],[384,5],[384,4],[384,5],[384,5],[385,2],[386,3],[386,4],[386,4],[386,5],[386,6],[386,6],[386,6],[386,6],[386,7],[386,8],[386,8],[386,8],[386,8],[386,8],[386,3],[386,4],[386,4],[387,3],[387,4],[387,4],[387,5],[388,3],[389,2],[22,5],[22,5],[22,6],[22,3],[22,2],[22,2],[414,1],[417,1],[416,1],[416,3],[418,3],[418,2],[418,1],[419,1],[420,1],[421,1],[421,1],[20,2],[20,2]],
performAction: function anonymous(yytext, yyleng, yylineno, yy, yystate /* action[1] */, $$ /* vstack */, _$ /* lstack */) {
/* this == yyval */

var $0 = $$.length - 1;
switch (yystate) {
case 1:

     parser.yy.result = {};
     parser.yy.cursorFound = false;

     // TODO: Move these below before token or use this.$ instead
     delete parser.yy.latestTablePrimaries;
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
case 11: case 12:

     suggestDdlAndDmlKeywords();
   
break;
case 83: case 84: case 142:

     this.$ = $$[$0-1];
   
break;
case 101:

     suggestKeywords(['INDEX', 'INDEXES']);
   
break;
case 102:

     suggestKeywords(['FORMATTED']);
   
break;
case 111: case 116:

     suggestKeywords(['EXISTS']);
   
break;
case 114:

     suggestKeywords(['IF NOT EXISTS']);
   
break;
case 115:

     suggestKeywords(['NOT EXISTS']);
   
break;
case 129:

     this.$ = { identifierChain: [{ name: $$[$0] }] }
   
break;
case 130:

     this.$ = { identifierChain: [{ name: $$[$0-2] }, { name: $$[$0] }] }
   
break;
case 131: case 691:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 132:

     suggestDatabases();
     this.$ = { identifierChain: [{ name: $$[$0-2] }] }
   
break;
case 133:

     // In Impala you can have statements like 'SELECT ... FROM testTable t, t.|'
     suggestTablesOrColumns($$[$0-2]);
   
break;
case 135:

     this.$ = { cursorOrPartialIdentifier: true }
     suggestDatabases();
   
break;
case 139: case 151:

     this.$ = { identifierChain: [ { name: $$[$0] } ] }
   
break;
case 140: case 277: case 286: case 304: case 308: case 392: case 409: case 410: case 427: case 438:

     this.$ = $$[$0];
   
break;
case 143:

     this.$ = { identifierChain: [ { name: $$[$0-2] }, { name: $$[$0] } ] }
   
break;
case 144:

     this.$ = { identifierChain: [ { name: $$[$0-3] }, { name: $$[$0] } ] }
   
break;
case 145:

     this.$ = { identifierChain: [ { name: $$[$0-4] }, { name: $$[$0-1] } ] }
   
break;
case 146:

     this.$ = { identifierChain: [ { name: $$[$0-5] }, { name: $$[$0-1] } ] }
   
break;
case 147:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-3] } ] };
   
break;
case 148:

     this.$ = { partial: true, identifierChain: [ { name: $$[$0-2] } ] };
   
break;
case 149:

     this.$ = { partial: true, identifierChain: [ ] };
   
break;
case 150:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ] }
   
break;
case 152:

     this.$ = { identifierChain: [ { name: $$[$0-1] } ], alias: $$[$0] };
   
break;
case 154:

     this.$ = { identifierChain: $$[$0-1].identifierChain, alias: $$[$0] }
   
break;
case 155: case 553:

     this.$ = [ $$[$0] ]
   
break;
case 156:

     this.$ = $$[$0-2].concat($$[$0])
   
break;
case 157: case 158:

     this.$ = $$[$0-2];
   
break;
case 159:

     if (typeof $$[$0].key !== 'undefined') {
       this.$ = { name: $$[$0-1], key: $$[$0].key }
     } else {
       this.$ = { name: $$[$0-1] }
     }
   
break;
case 161:
 this.$ = {} 
break;
case 162:

     this.$ = { key: '"' + $$[$0-1] + '"' }
   
break;
case 163:

     this.$ = { key: parseInt($$[$0-1]) }
   
break;
case 164:

     this.$ = { key: null }
   
break;
case 167:

     if (isHive() || isImpala()) {
       suggestKeywords(['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
   
break;
case 177:

     suggestKeywords(['DBPROPERTIES']);
   
break;
case 178:

     this.$ = mergeSuggestKeywords($$[$0-2], $$[$0-1], $$[$0]);
   
break;
case 179:

     this.$ = { suggestKeywords: ['COMMENT'] }
   
break;
case 181:

     this.$ = { suggestKeywords: ['LOCATION'] }
   
break;
case 183:

     this.$ = { suggestKeywords: isHive() ? ['WITH DBPROPERTIES'] : [] }
   
break;
case 190:

     if ($$[$0-1] && $$[$0-1].suggestKeywords.length > 0) {
       suggestKeywords($$[$0-1].suggestKeywords);
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
case 230:

      if ($$[$0].length > 0) {
        var table =  $$[$0].shift().name;
        suggestColumns({
          table: table,
          identifierChain: $$[$0]
        });
      } else {
        if (!$$[$0-1]) {
          suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'SCHEMA']);
        }
        suggestTables();
      }
    
break;
case 231:

     if (!$$[$0-1]) {
       suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'SCHEMA']);
     }
     suggestTables();
    
break;
case 233:

     if (!$$[$0-1]) {
       suggestKeywords(['EXTENDED']);
     }
   
break;
case 236:

      if (!$$[$0-2]) {
        suggestKeywords(['FORMATTED']);
      }
    
break;
case 237:

      if (!$$[$0-1]) {
        suggestKeywords(['FORMATTED']);
      }
      suggestTables();
      suggestDatabases({ appendDot: true });
      this.$ = { cursorOrPartialIdentifier: true }
    
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
case 243:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   
break;
case 244:

     if (isHive()) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   
break;
case 249:

     if (!$$[$0-1]) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 251:

     if ($$[$0].identifierChain && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name);
     } else if ($$[$0].identifierChain && $$[$0].identifierChain.length === 0) {
       suggestTables();
       suggestDatabases({ appendDot: true });
     }
   
break;
case 253:

     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   
break;
case 255:

     suggestKeywords([ 'TABLE' ]);
   
break;
case 256:

     suggestKeywords([ 'INTO' ]);
   
break;
case 258:

     suggestKeywords([ 'INPATH' ]);
   
break;
case 259:

     suggestKeywords([ 'DATA' ]);
   
break;
case 261: case 264: case 265: case 267: case 268: case 686:

     linkTablePrimaries();
   
break;
case 263: case 419:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 266:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     linkTablePrimaries();
   
break;
case 269:

     if ($$[$0-2].suggestKeywords) {
       suggestKeywords($$[$0-2].suggestKeywords);
     }
   
break;
case 271:

      if ($$[$0-4].suggestKeywords) {
        suggestKeywords($$[$0-4].suggestKeywords);
      }
    
break;
case 272:

     if ($$[$0-1].suggestKeywords) {
       suggestKeywords($$[$0-1].suggestKeywords);
     }
     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 276:

     if ($$[$0-1].suggestKeywords.length == 0) {
       var keywords = [];
       if (typeof $$[$0-2].hasJoinCondition !== 'undefined' && ! $$[$0-2].hasJoinCondition) {
         keywords.push('ON');
       }
       if (isHive()) {
         keywords = keywords.concat(['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']);
       } else if (isImpala()) {
         keywords = keywords.concat(['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT ANTI JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT ANTI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'RIGHT SEMI JOIN', 'WHERE']);
       } else {
         keywords = keywords.concat(['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']);
       }
       suggestKeywords(keywords);
     } else if ($$[$0-1].suggestKeywords) {
       suggestKeywords($$[$0-1].suggestKeywords);
     }
   
break;
case 279: case 431:

       suggestTables();
       suggestDatabases({ appendDot: true });
   
break;
case 280:

     if (!$$[$0-3] && !$$[$0-2] && !$$[$0-1] && !$$[$0]) {
       this.$ = { suggestKeywords: [] }
     } else if ($$[$0-3] && !$$[$0-2] && !$$[$0-1] && !$$[$0]) {
       this.$ = mergeSuggestKeywords($$[$0-3], { suggestKeywords: ['GROUP BY', 'LIMIT', 'ORDER BY'] });
     } else if ($$[$0-2] && !$$[$0-1] && !$$[$0]) {
       this.$ = { suggestKeywords: ['ORDER BY', 'LIMIT'] }
     } else if ($$[$0-1] && !$$[$0]) {
       if ($$[$0-1].suggestKeywords) {
         this.$ = { suggestKeywords: $$[$0-1].suggestKeywords.concat(['LIMIT']) }
       } else {
         this.$ = { suggestKeywords: ['LIMIT'] }
       }
     }
   
break;
case 288: case 297: case 302: case 310: case 317: case 403: case 479: case 484: case 490: case 492: case 494: case 498: case 499: case 500: case 501: case 698:

     suggestColumns();
   
break;
case 291: case 305:

     delete parser.yy.result.suggestStar;
   
break;
case 292:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 293: case 306:

     suggestKeywords(['BY']);
   
break;
case 314:

     this.$ = mergeSuggestKeywords($$[$0-1], $$[$0]);
   
break;
case 321:

    this.$ = { suggestKeywords: ['ASC', 'DESC'] }
  
break;
case 324:

    if (isImpala()) {
      this.$ = { suggestKeywords: ['NULLS FIRST', 'NULLS LAST'] }
    } else {
      this.$ = {}
    }
  
break;
case 327:

     suggestKeywords(['FIRST', 'LAST']);
   
break;
case 330:

     suggestNumbers([1, 5, 10]);
   
break;
case 341:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 357:

     this.$ = { suggestKeywords: ['<', '<=', '<>', '=', '=>', '>', 'IN', 'NOT IN'] }
   
break;
case 360:

     this.$ = { suggestKeywords: ['AND'] }
   
break;
case 370:

     if (typeof $$[$0-2] !== 'undefined') {
       suggestValues({ identifierChain: $$[$0-2]});
     }
   
break;
case 386:

     suggestKeywords(['IN']);
   
break;
case 391:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 396:

     this.$ = [ $$[$0] ];
   
break;
case 397:

     this.$ = $$[$0-2].concat($$[$0]);
   
break;
case 400:

     suggestColumns({
       identifierChain: $$[$0-2]
     });
   
break;
case 402:

     this.$ = { name: $$[$0] }
   
break;
case 413:

     parser.yy.result.suggestStar = true;
     suggestColumns();
   
break;
case 423:

     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $$[$0-2].key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 424: case 425:

      $$[$0-2].unshift($$[$0-4]);
      suggestColumns({
        identifierChain: $$[$0-2]
      });
    
break;
case 441: case 443:

     this.$ = { hasJoinCondition: false }
   
break;
case 442: case 444:

     this.$ = { hasJoinCondition: true }
   
break;
case 457: case 578: case 593: case 648: case 652: case 678:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   
break;
case 471: case 473:

     if (!$$[$0-1]) {
       suggestKeywords(['OUTER']);
     }
   
break;
case 472:

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
case 474:

     if (!$$[$0-1]) {
       suggestKeywords(['ANTI', 'SEMI', 'OUTER']);
     } else {
       suggestKeywords(['ANTI', 'SEMI']);
     }
   
break;
case 485:

      suggestColumns();
    
break;
case 502:

     if ($$[$0-2].identifierChain) {
       if ($$[$0-1] && !$$[$0-1].suggestKeywords) {
         $$[$0-2].alias = $$[$0-1]
       }
       if ($$[$0] && $$[$0].length > 0) {
         $$[$0-2].lateralViews = $$[$0];
       }
       addTablePrimary($$[$0-2]);
     }
   
break;
case 503: case 506:

     if ($$[$0] && !$$[$0].suggestKeywords) {
       // TODO: Potentially add columns for SELECT bla.| FROM (SELECT * FROM foo) AS bla;
       addTablePrimary({ subqueryAlias: $$[$0] });
     }
   
break;
case 512:

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
case 513:

     if (Object.keys(parser.yy.result).length === 0) {
       parser.yy.result = parser.yy.resultStack.pop();
       parser.yy.latestTablePrimaries = parser.yy.primariesStack.pop();
     }
   
break;
case 516: case 518:

     suggestKeywords(['SELECT']);
   
break;
case 533:

     this.$ = { suggestKeywords: ['AS'] }
   
break;
case 534: case 535:

     this.$ = $$[$0]
   
break;
case 540:

     if ($$[$0-1]) {
       this.$ = $$[$0-1].concat($$[$0]);
     } else {
       this.$ = $$[$0];
     }
   
break;
case 542: case 543:

     this.$ = { function: $$[$0-3], expression: $$[$0-1] }
   
break;
case 546:

     this.$ = [{ udtf: $$[$0-2], tableAlias: $$[$0-1], columnAliases: $$[$0] }]
   
break;
case 547:

      this.$ = [{ udtf: $$[$0-1], columnAliases: $$[$0] }]
    
break;
case 549: case 550:

     this.$ = [];
     suggestKeywords(['AS']);
   
break;
case 551:

     this.$ = [];
     suggestKeywords(['explode', 'posexplode']);
   
break;
case 552:

     this.$ = [];
     suggestKeywords(['VIEW']);
   
break;
case 554:

     this.$ = [ $$[$0-3], $$[$0-1] ]
   
break;
case 555:

     if (isHive()) {
       suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
     } else {
       suggestKeywords(['COLUMNS', 'DATABASES', 'TABLES']);
     }
   
break;
case 556:

     if (isImpala()) {
       suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'PARTITIONS', 'TABLE STATS']);
     }
   
break;
case 557:

     if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'DATABASES', 'FUNCTIONS', 'SCHEMAS', 'TABLES']);
     } else if (isHive()) {
       suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
     }
   
break;
case 577: case 677:

     suggestKeywords(['STATS']);
   
break;
case 579:

     suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
   
break;
case 580: case 581: case 586: case 587: case 635: case 636:

     suggestKeywords(['FROM', 'IN']);
   
break;
case 582: case 583: case 584: case 619: case 633: case 684:

     suggestTables();
   
break;
case 588: case 637: case 646: case 704:

     suggestDatabases();
   
break;
case 592: case 595: case 620:

     suggestKeywords(['TABLE']);
   
break;
case 594:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name);
     }
   
break;
case 596:

     suggestKeywords([ 'ROLES' ]);
   
break;
case 597:

     suggestKeywords([ 'CURRENT' ]);
   
break;
case 599: case 675:

     suggestKeywords(['LIKE']);
   
break;
case 604: case 609:

     suggestKeywords(['FUNCTIONS']);
   
break;
case 606: case 610:

     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   
break;
case 607: case 681:

     if (!$$[$0-1]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 611:

     if (!$$[$0-2]) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   
break;
case 616: case 632: case 634:

     suggestKeywords(['ON']);
   
break;
case 618:

     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   
break;
case 621:

     suggestKeywords(['ROLE']);
   
break;
case 638:

     suggestTablesOrColumns($$[$0]);
   
break;
case 639:

     suggestTables();
     suggestDatabases({
       appendDot: true
     });
     suggestKeywords(['DATABASE', 'SCHEMA']);
   
break;
case 640:

     if ($$[$0].partial && $$[$0].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0].identifierChain[0].name)
     }
   
break;
case 641:

      suggestKeywords(['EXTENDED', 'PARTITION']);
    
break;
case 642: case 679:

     if ($$[$0-1].partial && $$[$0-1].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-1].identifierChain[0].name)
     }
   
break;
case 643:

     if ($$[$0-4].partial && $$[$0-4].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
     }
   
break;
case 644: case 663: case 674:

     suggestKeywords(['EXTENDED']);
   
break;
case 645:

     // TODO: Move into CleanRegularOrBackTickedSchemaQualifiedName
     if ($$[$0-5].partial && $$[$0-5].identifierChain.length === 1) {
       suggestTablesOrColumns($$[$0-5].identifierChain[0].name)
     }
   
break;
case 649: case 653:

     suggestTablesOrColumns($$[$0-4].identifierChain[0].name)
   
break;
case 650: case 676:

     suggestKeywords(['PARTITION']);
   
break;
case 654: case 655:

     suggestKeywords(['GRANT']);
   
break;
case 656: case 657:

     suggestKeywords(['ROLE', 'USER']);
   
break;
case 659: case 660:

     suggestKeywords(['GROUP']);
   
break;
case 666:

      if ($$[$0-1]) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    
break;
case 669:

      if (isHive())
        suggestKeywords(['EXTENDED']);
      
break;
case 670:

      suggestKeywords(['LIKE']);
    
break;
case 671:

      suggestKeywords(['PARTITION']);
    
break;
case 687:

      linkTablePrimaries();
    
break;
case 688:

     if (!$$[$0-1]) {
       suggestKeywords([ 'WHERE' ]);
     }
   
break;
case 689:

     suggestKeywords([ 'SET' ]);
   
break;
case 693:

     // TODO: Replace with TablePrimary?
     if ($$[$0].partial) {
       if ($$[$0].identifierChain.length === 1) {
         suggestTablesOrColumns($$[$0].identifierChain[0].name);
       }
     } else if (typeof $$[$0].identifierChain !== 'undefined') {
       addTablePrimary($$[$0]);
     }
   
break;
case 697:

     suggestKeywords([ '=' ]);
   
break;
case 703:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
}
},
table: [o([13,14,27,28,29,30,75,76,203,204,205,211,369,413,422],[2,1],{4:1,3:2}),{1:[3]},{5:3,8:4,9:5,10:6,11:7,12:8,13:$V0,14:$V1,15:10,16:11,17:12,18:13,19:14,20:15,21:16,22:17,26:23,27:$V2,28:$V3,29:$V4,30:$V5,74:50,75:$V6,76:$V7,161:21,162:22,201:24,202:25,203:$V8,204:$V9,205:$Va,206:27,207:28,211:$Vb,369:$Vc,371:30,372:31,373:32,374:33,375:34,376:35,377:36,378:37,379:38,380:39,381:40,382:41,383:42,384:43,385:44,386:45,387:46,388:47,389:48,413:$Vd,422:$Ve},{6:[1,59],7:[1,60]},o($Vf,[2,4]),o($Vf,[2,6]),o($Vf,[2,7]),o($Vf,[2,8]),o($Vf,[2,9]),{14:[1,61]},o($Vf,[2,12]),o($Vf,[2,13]),o($Vf,[2,14]),o($Vf,[2,15]),o($Vf,[2,16]),o($Vf,[2,17]),o($Vf,[2,18]),o($Vf,[2,19]),{2:[1,65],13:$Vg,30:[1,64],145:$Vh,148:74,157:73,212:62,214:63,247:71,248:72,300:66,301:$Vi,302:68,303:69,304:70},o($Vj,$Vk),o($Vj,[2,26]),o($Vf,[2,165]),o($Vf,[2,166]),{30:[1,77],38:79,39:$Vl,40:$Vm,41:$Vn,49:80,50:$Vo,51:$Vp,71:81,72:[1,87],73:[1,88],176:78},o($Vf,[2,227]),o($Vf,[2,228]),{30:[1,89],38:91,39:$Vl,40:$Vm,41:$Vn,49:90,50:$Vo,51:$Vp},o($Vf,[2,239]),o($Vf,[2,240]),{23:102,24:[1,125],25:[1,126],28:[1,118],29:[1,119],30:[1,92],40:[1,113],41:[1,114],53:128,54:$Vq,55:$Vr,59:97,60:98,61:[1,120],62:[1,121],66:99,67:[1,122],68:[1,123],69:[1,100],70:[1,124],91:111,92:[1,129],93:[1,130],96:[1,112],97:115,98:[1,131],99:[1,132],117:103,121:[1,127],124:106,125:107,390:[1,93],396:[1,94],397:[1,95],398:[1,96],399:[1,101],400:[2,90],402:[1,104],406:[1,105],407:[1,108],409:[1,109],410:[1,110],411:[1,116],412:[1,117]},o($Vf,[2,558]),o($Vf,[2,559]),o($Vf,[2,560]),o($Vf,[2,561]),o($Vf,[2,562]),o($Vf,[2,563]),o($Vf,[2,564]),o($Vf,[2,565]),o($Vf,[2,566]),o($Vf,[2,567]),o($Vf,[2,568]),o($Vf,[2,569]),o($Vf,[2,570]),o($Vf,[2,571]),o($Vf,[2,572]),o($Vf,[2,573]),o($Vf,[2,574]),o($Vf,[2,575]),o($Vf,[2,576]),{13:[1,135],30:[1,136]},{30:[1,138],63:137,64:[1,139],65:[1,140]},{13:[1,145],30:[1,142],143:148,145:$Vs,154:146,155:144,414:141,417:143},o($Vt,[2,22]),o($Vt,[2,23]),o($Vt,[2,24]),o($Vu,[2,94],{120:149,49:150,50:$Vo,51:$Vp,119:[1,151],121:[1,152]}),o($Vu,[2,97],{122:153,123:[1,154]}),o($Vv,[2,61]),o($Vv,[2,62]),{7:[1,155],8:156,9:5,10:6,11:7,12:8,13:$V0,14:$V1,15:10,16:11,17:12,18:13,19:14,20:15,21:16,22:17,26:23,27:$V2,28:$V3,29:$V4,30:$V5,74:50,75:$V6,76:$V7,161:21,162:22,201:24,202:25,203:$V8,204:$V9,205:$Va,206:27,207:28,211:$Vb,369:$Vc,371:30,372:31,373:32,374:33,375:34,376:35,377:36,378:37,379:38,380:39,381:40,382:41,383:42,384:43,385:44,386:45,387:46,388:47,389:48,413:$Vd,422:$Ve},{1:[2,3]},o($Vf,[2,11],{13:[1,157]}),o($Vw,$Vx,{213:158,215:159,216:161,219:162,30:[1,160],36:$Vy}),o($Vz,[2,262],{213:164,216:165,36:$VA}),o($Vz,[2,263],{148:74,216:165,213:167,303:168,247:169,157:170,13:$Vg,36:$VA,145:$Vh}),{36:$Vy,213:171,215:172,216:161,219:162},o($VB,[2,404]),o($VB,[2,405]),o($VC,[2,406]),o($VB,$VD,{152:[1,173]}),o($VC,[2,408]),o($VE,$VF,{305:174,306:175,148:176,110:177,143:178,13:$Vg,111:$VG,112:$VH,145:$VI}),o($VC,$VF,{148:176,305:182,110:183,13:$Vg,111:$VG,112:$VH,145:$Vh}),o($VJ,$VK,{31:184,32:$VL,33:$VM,34:$VN}),o($VO,[2,161],{159:188,82:189,83:[1,190],84:[1,191]}),o($VP,[2,141]),{107:$VQ},o($Vf,[2,167],{38:193,39:$Vl,40:$Vm,41:$Vn}),{38:194,39:$Vl,40:$Vm,41:$Vn},{13:[1,195]},o($VR,[2,112],{137:196,139:197,30:[1,199],134:[1,198]}),o($VS,[2,197]),o($VT,[2,32]),o($VT,[2,33]),o($VT,[2,34]),o($VU,[2,41]),o($VU,[2,42]),o($VS,[2,59]),o($VS,[2,60]),o($Vf,[2,238]),o($VV,$VW,{133:200,136:201,134:$VX}),o($VY,$VW,{133:203,136:204,134:$VX}),o($Vf,[2,555],{143:148,153:205,94:207,53:209,154:211,13:$VZ,54:$Vq,55:$Vr,95:$V_,96:$V$,145:$Vs,370:[1,206],400:[1,208]}),{30:[1,214],391:[1,215]},{30:[1,216],35:217,36:$V01,37:$V11},o($Vf,[2,590]),{13:[1,221],30:[1,222],141:220},{30:[1,223],38:224,39:$Vl,40:$Vm,41:$Vn},{30:[1,225],94:226,95:$V_,96:$V$},{30:[1,227],370:[1,228]},o($V21,[2,57],{105:229,106:$V31}),o($Vf,[2,602],{108:231,109:$V41}),{30:[1,233],400:[2,91]},{400:[1,234]},o($V51,[2,622],{403:235,405:236,13:[1,237],30:[1,238]}),{30:[1,239]},o($Vf,[2,626],{30:[1,241],331:[1,240]}),o($Vf,[2,629],{331:[1,242]}),{13:$VZ,30:[1,243],49:245,50:$Vo,51:$Vp,143:148,145:$Vs,153:244,154:211},{13:$VZ,30:[1,246],143:148,145:$Vs,153:247,154:211},{13:$VZ,30:[1,248],143:148,145:$Vs,153:249,154:211},{30:[1,250],402:[1,251],406:[1,252]},o($Vf,[2,662]),{30:[1,253],119:[1,254]},{30:[1,255],391:[1,256]},o($V61,$V71,{140:257,77:258,37:$V81,78:$V91}),{30:[1,261]},o($Vf,[2,685]),o($Va1,[2,49]),o($Va1,[2,50]),o($Vb1,[2,51]),o($Vb1,[2,52]),o($V21,[2,55]),o($V21,[2,56]),o($V21,[2,58]),o($Vc1,[2,20]),o($Vc1,[2,21]),{30:[1,263],53:262,54:$Vq,55:$Vr},o($Vd1,[2,100]),o($Ve1,[2,73]),o($Ve1,[2,74]),o($Vf1,[2,77]),o($Vf1,[2,78]),o($Vd1,[2,45]),o($Vd1,[2,46]),o($Vf,[2,703]),o($Vf,[2,704]),{30:[1,265],79:264,80:[1,266],81:[1,267]},o($Vf,[2,259]),o($Vg1,[2,53]),o($Vg1,[2,54]),o($Vf,[2,690],{30:[1,269],415:[1,268]}),o($Vf,[2,691]),o($Vh1,[2,692]),o($Vh1,[2,693]),o($Vh1,[2,151],{31:271,13:[1,270],32:$VL,33:$VM,34:$VN}),o($Vh1,[2,153],{13:[1,272]}),{107:[1,273],146:$Vi1},o($Vj1,[2,149]),{13:$Vg,30:[1,277],145:$Vh,148:74,156:275,157:278,158:276},o($Vu,[2,92],{118:279,119:[1,280]}),o($Vu,[2,95]),o($Vu,[2,96]),{13:$Vg,30:[1,283],143:285,145:$VI,147:281,148:284,149:282},o($Vu,[2,98]),{1:[2,2]},o($Vf,[2,5]),o($Vf,[2,10]),o($Vw,[2,261]),o($Vz,[2,264]),o($Vz,[2,272],{216:165,213:286,36:$VA,152:[1,287]}),o($Vk1,$Vl1,{217:288,218:289,222:290,226:291,230:$Vm1}),o($Vn1,$Vl1,{217:293,222:294,230:$Vo1}),{13:$Vg,30:[1,298],143:285,145:$VI,147:311,148:284,149:313,169:$Vp1,208:303,209:305,220:296,221:297,292:312,293:314,308:299,309:300,310:301,311:302,312:304,313:306,338:307,340:308,341:309,343:310},o($Vz,[2,265]),o($Vn1,$Vl1,{222:294,217:316,230:$Vo1}),{13:$Vg,145:$Vh,147:311,148:321,169:$Vq1,208:318,220:317,292:312,308:299,310:301,312:304,338:319,340:320},o($Vz,[2,266]),o($VC,[2,413],{152:$Vr1}),o($Vs1,$VF,{305:174,148:176,110:183,13:$Vg,111:$VG,112:$VH,145:$Vh}),o($VJ,$VK,{31:324,32:$VL,33:$VM,34:$VN}),o($Vz,[2,267]),o($Vz,[2,268]),{13:$Vg,14:$V1,15:328,30:$V5,145:$Vh,148:74,157:73,247:325,248:327,307:326},o($Vt1,[2,409]),o($VC,[2,412]),o($Vu1,[2,534]),{13:$Vg,30:[1,331],143:330,145:$VI,148:329},o($Vv1,[2,536]),{107:$VQ,146:$Vi1},o($Vu,[2,85]),o($Vu,[2,86]),o($VC,[2,411]),{13:$Vg,145:$Vh,148:329},{13:$Vg,14:$Vw1,143:336,144:334,145:$VI,148:74,156:333,157:278,301:$Vx1},o($Vy1,[2,27]),o($Vy1,$Vz1),o($Vy1,$VA1),o($VO,[2,159]),{88:339,89:$VB1,90:$VC1,103:[1,338],108:337,109:$V41},o($VD1,[2,67]),o($VD1,[2,68]),{145:[1,342]},o($Vf,[2,194],{13:[1,343]}),{13:[1,344]},{169:$VE1,177:345},o($Vf,[2,185],{13:[1,347]}),o($Vf,[2,186],{13:[1,348]}),{30:[1,350],138:[1,349]},o($VR,[2,114]),o($Vf,[2,241],{148:352,13:$Vg,30:[1,351],145:$Vh}),o($Vf,[2,242],{148:353,13:$Vg,145:$Vh}),{30:[1,355],135:[1,354]},o($Vf,[2,247],{148:284,143:285,338:307,340:308,341:309,343:310,147:311,292:312,149:313,293:314,208:357,209:358,13:$Vg,30:[1,356],145:$VI,169:$Vp1}),o($Vf,[2,248],{147:311,292:312,338:319,340:320,148:321,208:359,13:$Vg,145:$Vh,169:$Vq1}),o($Vf,[2,556]),{105:360,106:$V31},o($Vf,[2,597]),o($VF1,$V71,{77:258,140:361,37:$V81,78:$V91}),o($V51,[2,102]),o($VG1,[2,139],{31:271,32:$VL,33:$VM,34:$VN}),o($VG1,[2,140]),o($Vf,[2,75]),o($Vf,[2,76]),o($Vf,[2,577]),{13:$VZ,30:[1,362],143:148,145:$Vs,153:363,154:211},o($Vf,[2,580],{148:364,13:$Vg,145:$Vh}),{13:$Vg,30:[1,365],145:$Vh,148:366},o($VV,$VH1),o($VV,[2,31]),o($Vf,[2,591],{34:[1,367]}),o($VI1,[2,120]),o($VI1,[2,121]),o($Vf,[2,592],{143:148,154:211,153:368,13:$VZ,145:$Vs}),{13:$VZ,30:[1,369],143:148,145:$Vs,153:370,154:211},o($Vf,[2,596]),o($Vf,[2,598]),o($Vf,[2,599]),{105:371,106:$V31},o($Vf,[2,601]),{107:[1,372]},o($Vf,[2,603]),{107:[1,373]},o($Vf,[2,604],{77:258,140:374,37:$V81,78:$V91,370:$V71}),o($VJ1,$V71,{77:258,140:375,37:$V81,78:$V91}),o($Vf,[2,612],{331:[1,376]}),o($Vf,[2,616],{331:[1,377]}),o($V51,[2,623],{30:[1,378]}),o($V51,[2,624]),o($Vf,[2,621]),{13:$Vg,30:[1,380],145:$Vh,148:379},o($Vf,[2,632],{148:381,13:$Vg,145:$Vh}),{13:$Vg,145:$Vh,148:382},o($Vf,[2,639]),o($Vf,[2,640],{30:[1,383],119:[1,384],408:[1,385]}),{13:$Vg,30:[1,386],145:$Vh,148:387},o($Vf,[2,648]),{30:[1,389],392:[1,388],408:[1,390]},o($Vf,[2,652]),{392:[1,391]},o($Vf,[2,654],{100:392,92:$VK1,101:$VL1}),{30:[1,395],92:$VK1,100:396,101:$VL1},{30:[1,397],116:[1,398]},o($Vf,[2,663],{126:399,52:400,36:$VM1,37:$VN1,370:$VO1}),o($VJ1,$VO1,{126:403,128:404,52:405,36:$VM1,37:$VN1}),o($Vf,[2,677]),{13:$VZ,30:[1,406],143:148,145:$Vs,153:407,154:211},o($Vf,[2,680],{105:409,30:[1,408],106:$V31,370:[1,410]}),{13:$Vg,30:$VP1,127:411,129:412,142:414,143:416,145:$VI,148:413},o($Vu,[2,63]),o($Vu,[2,64]),o($Vf,[2,684]),o($Vd1,[2,99]),o($V51,[2,101]),{197:417,198:$VQ1},o($Vf,[2,258]),{198:[2,65]},{198:[2,66]},{13:$VR1,30:$VS1,416:419,418:420,419:421},o($Vf,[2,689]),o($Vh1,[2,152]),{13:[1,424],14:$Vw1,143:336,144:426,145:[1,425]},o($Vh1,[2,154]),{145:[1,427]},o([2,6,7,13,30,32,33,34,36,106,111,112,114,115,116,119,145,152,170,230,239,249,250,251,254,317,322,323,325,326,328,329,331,366,370,392,408,415],[2,128]),o($Vf,[2,229],{31:428,32:$VL,33:$VM,34:$VN}),o($Vf,[2,230]),o($Vf,[2,231]),o($VT1,[2,155]),{13:$Vg,30:$VP1,127:429,129:430,142:414,143:416,145:$VI,148:413},o($Vu,[2,93]),o($Vf,[2,234]),o($Vf,[2,235]),o($Vf,[2,237],{148:321,147:431,13:$Vg,145:$Vh}),o($VU1,$VV1,{31:432,32:$VL,33:$VM,34:$VN}),o($VW1,[2,131],{31:433,32:$VL,33:$VM,34:$VN}),o($Vz,[2,269]),{2:[1,435],36:$VA,213:434,216:165},o($Vz,$VX1,{30:[1,436]}),o($Vz,[2,274]),o($VY1,$VZ1,{223:437,227:438,113:439,114:$V_1,115:$V$1,116:$V02}),o($V12,$VZ1,{223:443,113:444,114:$V_1,115:$V$1,116:$V02}),{13:$Vg,30:[1,447],102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V42,145:$Vh,148:74,157:483,169:$V52,231:445,232:446,255:448,256:449,257:450,259:451,260:452,262:453,263:455,264:456,265:457,267:458,273:459,274:460,275:461,276:462,277:463,278:464,279:468,280:469,283:465,284:466,285:467,286:470,287:471,294:473,295:476,296:477,297:480,298:481,299:482},o($Vz,[2,275]),o($V12,$VZ1,{113:444,223:485,114:$V_1,115:$V$1,116:$V02}),{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V62,145:$Vh,148:74,157:492,169:$V72,231:445,255:486,257:450,260:487,263:455,265:457,273:459,274:489,277:463,278:464,283:465,284:466,285:467,294:473,296:491,298:481},o([2,6,7,30,114,115,116,170,230,239,254],$V82,{152:[1,493]}),o($V92,[2,278],{152:[1,494]}),o($V92,[2,279]),o($Va2,[2,426]),o($Vb2,[2,428]),o($Va2,[2,432]),o($Vb2,[2,433]),o($Va2,$Vc2,{314:495,315:496,316:497,319:498,321:499,317:$Vd2,322:$Ve2,323:$Vf2,325:$Vg2,326:$Vh2,328:$Vi2,329:$Vj2}),o($Va2,[2,435]),o($Vb2,[2,436],{314:506,316:507,317:$Vd2,322:$Ve2,323:$Vk2,325:$Vg2,326:$Vl2,328:$Vm2,329:$Vn2}),o($Vb2,[2,437]),o($Vo2,$VF,{148:176,110:183,305:512,13:$Vg,111:$VG,112:$VH,145:$Vh}),o($Vp2,$VF,{148:176,110:177,143:178,305:513,306:514,13:$Vg,111:$VG,112:$VH,145:$VI}),o($Vq2,$VF,{148:176,110:183,305:515,13:$Vg,111:$VG,112:$VH,145:$Vh}),o($Vr2,$VF,{148:176,110:183,305:516,13:$Vg,111:$VG,112:$VH,145:$Vh}),o($VU1,[2,508]),o([2,6,7,13,30,111,112,114,115,116,145,152,170,230,239,254,317,322,323,325,326,328,329,331],[2,510]),o($VW1,[2,509]),o([2,6,7,13,111,112,114,115,116,145,152,170,230,239,254,317,322,323,325,326,328,329,331],[2,511]),o([14,30,211],$Vs2,{344:517}),o($Vz,$VX1),o($V92,$V82,{152:[1,518]}),o($Vb2,$Vc2,{316:507,314:519,317:$Vd2,322:$Ve2,323:$Vk2,325:$Vg2,326:$Vl2,328:$Vm2,329:$Vn2}),o($Vq2,$VF,{148:176,110:183,305:520,13:$Vg,111:$VG,112:$VH,145:$Vh}),o($Vr2,$VF,{148:176,110:183,305:513,13:$Vg,111:$VG,112:$VH,145:$Vh}),o($VW1,$VV1,{31:521,32:$VL,33:$VM,34:$VN}),{211:$Vs2,344:522},{13:$Vg,145:$Vh,148:74,157:170,247:523},{13:$Vg,145:$Vh,148:74,156:524,157:278,301:$Vx1},o($VE,$VF,{148:176,110:177,143:178,305:525,306:526,13:$Vg,111:$VG,112:$VH,145:$VI}),o($VC,[2,415],{152:[1,527]}),o($Vs1,[2,418]),o($Vs1,[2,419]),o($Vu1,[2,535]),o($Vv1,[2,537]),o($Vv1,[2,538]),o($VJ,[2,421]),o($VJ,$Vt2,{31:530,32:$VL,33:$Vu2,34:$Vv2}),o($Vw2,[2,423]),o($Vx2,[2,126]),o($Vx2,[2,127]),{88:531,89:$VB1,90:$VC1},{88:532,89:$VB1,90:$VC1},o($VO,[2,164]),o($VO,[2,71]),o($VO,[2,72]),o($VP,[2,142]),o($Vf,[2,193],{177:533,169:$VE1}),{169:$VE1,177:534},o($Vf,[2,196]),{13:$Vy2,178:535,179:536,180:537},o($Vz2,[2,179],{171:539,172:540,163:541,56:542,6:$VA2,7:$VA2,57:[1,543],58:[1,544]}),o($Vf,[2,188]),{30:[1,546],135:[1,545]},o($VR,[2,115]),o($Vf,[2,243]),o($Vf,$VB2,{130:548,30:[1,547],131:$VC2,132:$VD2}),o($Vf,$VB2,{130:551,131:$VC2,132:$VD2}),o($VY,[2,110]),o([6,7,13,145,169],[2,111]),o($Vf,[2,249]),o($Vf,[2,250],{30:[1,552]}),o($Vf,[2,251]),o($Vf,[2,252]),o($Vf,[2,557]),o($Vf,[2,606],{370:[1,553]}),o($Vf,[2,578]),{392:[1,554]},o($Vf,[2,581]),o($Vf,[2,582],{35:555,36:$V01,37:$V11}),o($Vf,[2,585],{35:557,30:[1,556],36:$V01,37:$V11}),{13:[1,558],14:[1,559]},o($Vf,[2,595]),o($Vf,[2,593]),o($Vf,[2,594]),o($Vf,[2,600]),{106:[1,560]},{109:[1,561]},{370:[1,562]},o($Vf,[2,605],{30:[1,563],370:[1,564]}),{13:$Vg,30:[1,568],38:567,39:$Vl,40:$Vm,41:$Vn,145:$Vh,148:566,404:[1,565]},{404:[1,569]},o($V51,[2,625]),o($Vf,[2,627],{35:570,30:[1,571],36:$V01,37:$V11}),o($Vf,[2,633],{35:572,36:$V01,37:$V11}),o($Vf,[2,634]),o($Vf,[2,630],{35:573,36:$V01,37:$V11}),o($Vf,[2,641]),o($Vf,[2,642]),{169:[1,574]},o($Vf,[2,646]),o($Vf,[2,647]),{393:[1,575]},o($Vf,[2,650]),{13:$VE2,150:576,151:577},{393:[1,579]},{13:[1,580]},{13:[2,79]},{13:[2,80]},o($Vf,[2,656],{13:[1,581]}),{13:[1,582]},o($Vf,[2,659],{13:[1,583]}),{13:[1,584]},{370:[1,585]},{13:$Vg,127:586,145:$Vh,148:413},o($Vu,[2,43]),o($Vu,[2,44]),o($Vf,[2,664],{30:[1,587],370:[1,588]}),o($Vf,[2,665],{370:[1,589]}),{13:$Vg,30:$VP1,127:586,129:590,142:414,143:416,145:$VI,148:413},o($Vf,[2,678]),o($Vf,[2,679]),o($Vf,[2,681]),o($Vf,[2,682]),{105:591,106:$V31},o($V61,[2,118]),o($V61,[2,119]),o($V61,[2,134]),o($V61,[2,135]),o($V61,[2,124]),o($V61,[2,125]),o($Vf,[2,257],{30:[1,593],210:[1,592]}),{14:[1,595],199:[1,594]},o([6,7,30],$Vl1,{222:596,226:597,152:[1,598],230:$Vm1}),o($VF2,[2,694]),{30:[1,600],43:[1,599]},o($VF2,[2,698]),o([30,43],[2,699]),o($Vj1,[2,143]),{107:[1,601],146:$Vi1},o($Vj1,[2,148]),o($Vj1,[2,150],{31:602,32:$VL,33:$VM,34:$VN}),{13:$Vg,14:[1,605],143:604,145:$VI,148:74,157:603},o($Vf,[2,232]),o($Vf,[2,233]),o($Vf,[2,236]),{13:$Vg,14:$Vw1,143:336,144:607,145:$VI,148:606},{13:$Vg,145:$Vh,148:608},o($Vz,[2,270]),{36:$VA,213:609,216:165},o($Vz,[2,276]),o($VG2,$VH2,{224:610,228:611,239:[1,612]}),o($VI2,$VH2,{224:613,239:$VJ2}),{30:[1,616],233:[1,615]},o($VK2,[2,87]),o($VK2,[2,88]),o($VK2,[2,89]),o($VI2,$VH2,{224:617,239:$VJ2}),{233:[1,618]},o($Vk1,[2,286]),o($Vn1,[2,287]),o($Vn1,[2,288]),o($Vk1,$VL2,{258:$VM2}),o($Vn1,[2,332],{258:$VN2}),o($VO2,[2,333]),o($VO2,[2,335]),o($VO2,$VP2,{261:[1,621]}),o($VO2,[2,340],{261:[1,622]}),{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,145:$Vh,148:74,157:483,169:$V52,263:623,264:624,265:457,267:458,273:459,274:460,275:461,276:462,277:463,278:464,279:468,280:469,283:465,284:466,285:467,286:470,287:471,294:473,295:476,296:477,297:480,298:481,299:482},o($VQ2,[2,345]),o($VQ2,[2,347]),o($VQ2,$VR2,{266:625,268:$VS2}),o($VQ2,$VR2,{266:627,268:$VS2}),o($VT2,[2,356]),o($VT2,$VU2,{42:628,288:629,289:630,281:637,37:$VV2,43:$VW2,44:$VX2,45:$VY2,46:$VZ2,47:$V_2,48:$V$2,78:$V03,138:[1,638],282:$V13}),o($VT2,[2,358]),o($VT2,[2,359],{42:642,288:643,281:644,37:$VV2,43:$VW2,44:$VX2,45:$VY2,46:$VZ2,47:$V_2,48:$V$2,78:$V03,138:$V23,282:$V13}),o($VT2,[2,360]),o($VT2,[2,361]),o($V33,[2,371]),o($V33,[2,372]),o($V33,[2,373]),o($VT2,[2,362]),o($VT2,[2,363]),o($V33,[2,374]),o($V33,[2,375]),{13:$Vg,14:$V1,15:648,30:$V5,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V42,145:$Vh,148:74,157:483,169:$V52,255:646,256:647,257:450,259:451,260:452,262:453,263:455,264:456,265:457,267:458,273:459,274:460,275:461,276:462,277:463,278:464,279:468,280:469,283:465,284:466,285:467,286:470,287:471,294:473,295:476,296:477,297:480,298:481,299:482},o($V33,[2,392]),o($V33,[2,376]),o($V33,[2,377]),o($V33,[2,393]),o($V43,$V53,{31:649,32:$VL,33:$VM,34:$VN}),o($V33,[2,81]),{103:[1,650]},o($V43,[2,395]),o($V63,[2,396]),o($V43,[2,398]),o($V63,$V73,{14:[1,651]}),o($V63,[2,402]),o($VI2,$VH2,{224:652,239:$VJ2}),o($Vn1,$VL2,{258:$V83}),o($VO2,$VP2,{261:[1,654]}),{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,145:$Vh,148:74,157:492,169:$V72,263:623,265:457,273:459,274:489,277:463,278:464,283:465,284:466,285:467,294:473,296:491,298:481},o($VT2,$VU2,{288:629,281:644,42:655,37:$VV2,43:$VW2,44:$VX2,45:$VY2,46:$VZ2,47:$V_2,48:$V$2,78:$V03,138:$V23,282:$V13}),{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V62,145:$Vh,148:74,157:492,169:$V72,255:656,257:450,260:487,263:455,265:457,273:459,274:489,277:463,278:464,283:465,284:466,285:467,294:473,296:491,298:481},o($V43,$V53,{31:657,32:$VL,33:$VM,34:$VN}),o($V63,$V73),{13:$Vg,30:[1,660],143:285,145:$VI,147:311,148:284,149:313,169:$Vp1,208:303,209:305,292:312,293:314,308:658,309:659,310:301,311:302,312:304,313:306,338:307,340:308,341:309,343:310},{13:$Vg,145:$Vh,147:311,148:321,169:$Vq1,208:318,292:312,308:661,310:301,312:304,338:319,340:320},o($Va2,$V93,{316:662,319:663,317:$Vd2,322:$Ve2,323:$Vf2,325:$Vg2,326:$Vh2,328:$Vi2,329:$Vj2}),o($Vb2,[2,439],{316:664,317:$Vd2,322:$Ve2,323:$Vk2,325:$Vg2,326:$Vl2,328:$Vm2,329:$Vn2}),{317:[1,665]},{317:[1,666]},o($Va3,[2,457]),{317:[2,463]},o($Vb3,$Vc3,{324:667,330:$Vd3}),{317:[2,465]},o($Vb3,$Vc3,{324:670,327:$Ve3,330:$Vd3}),o($Vb3,$Vc3,{324:671,330:$Vd3}),o($Vb3,$Vc3,{324:673,327:$Vf3,330:$Vd3}),o($Vb2,[2,440],{316:674,317:$Vd2,322:$Ve2,323:$Vk2,325:$Vg2,326:$Vl2,328:$Vm2,329:$Vn2}),{317:[1,675]},{317:$Vc3,324:676,330:$Vd3},{317:$Vc3,324:677,327:$Ve3,330:$Vd3},{317:$Vc3,324:678,330:$Vd3},{317:$Vc3,324:679,327:$Vf3,330:$Vd3},o($Vo2,$Vg3,{339:680,342:681}),o($Vp2,[2,503]),o($Vr2,[2,507]),o($Vq2,$Vg3,{339:682}),o($Vr2,[2,506]),{11:698,12:699,14:$V1,15:685,30:$V5,211:$Vb,346:683,347:684,348:686,349:687,350:688,351:689,352:690,353:691,354:692,355:693,356:694,357:695,358:696,359:697},{13:$Vg,145:$Vh,147:311,148:321,169:$Vq1,208:318,292:312,308:658,310:301,312:304,338:319,340:320},o($Vb2,$V93,{316:674,317:$Vd2,322:$Ve2,323:$Vk2,325:$Vg2,326:$Vl2,328:$Vm2,329:$Vn2}),o($Vq2,$Vg3,{339:700}),{13:$Vg,145:$Vh,148:606},{11:698,211:[1,701],346:683,348:686,350:688,352:690,354:692,356:694,358:696},o($Vs1,$VF,{148:176,110:183,305:525,13:$Vg,111:$VG,112:$VH,145:$Vh}),o($VJ,$Vt2,{31:530,32:$VL,33:$VM,34:$VN}),o($Vt1,[2,410]),o($VC,[2,414]),o($VC,[2,416],{148:74,247:169,157:170,303:702,13:$Vg,145:$Vh}),o($Vh3,$Vz1,{14:[1,703]}),o($Vh3,$VA1,{14:[1,704]}),{13:$Vg,145:$Vh,148:74,157:603},o($VO,[2,162]),o($VO,[2,163]),o($Vf,[2,192]),{30:[1,706],85:707,86:$Vi3,87:$Vj3,175:705},{152:[1,711],170:[1,710]},o($Vk3,[2,199]),o($Vk3,[2,201]),{30:[1,713],181:712,183:[1,714],184:[1,715],185:[1,716],186:[1,717],187:[1,718],188:[1,719],189:[1,720],190:[1,721],191:[1,722],192:[1,723],193:[1,724],194:[1,725],195:[1,726],196:[1,727]},{2:[1,728],30:[1,729]},o($Vl3,[2,181],{85:707,173:730,175:731,86:$Vi3,87:$Vj3}),o($Vz2,[2,180]),{106:[1,732]},{106:[2,47]},{106:[2,48]},o($VR,[2,113]),o($VR,[2,116]),o($Vf,[2,244]),o($Vf,[2,245]),o($Vf,[2,107]),o($Vf,[2,108]),o($Vf,[2,246]),o($Vf,[2,253]),{401:[1,733]},{393:[1,734]},o($Vf,[2,583],{148:735,13:$Vg,145:$Vh}),o($Vf,[2,586],{148:736,13:$Vg,145:$Vh}),{13:$Vg,30:[1,737],145:$Vh,148:738},o($VI1,[2,122]),o($VI1,[2,123]),o([2,6,7,30,37,43,44,45,46,47,48,78,114,115,116,138,152,170,230,239,254,258,261,268,282,408],[2,83]),o([2,6,7,30,32,33,34,37,43,44,45,46,47,48,78,89,90,114,115,116,138,152,170,230,239,254,258,261,268,282,317,322,323,325,326,328,329],[2,84]),{401:[1,739]},o($Vf,[2,607],{401:[1,740]}),{401:[1,741]},o($Vf,[2,613]),o($Vf,[2,614]),{13:$Vg,30:[1,743],145:$Vh,148:742},o($Vf,[2,618],{148:744,13:$Vg,145:$Vh}),o($Vf,[2,617]),{13:$Vg,30:[1,746],145:$Vh,148:745},o($Vf,[2,635],{148:747,13:$Vg,145:$Vh}),{13:$Vg,145:$Vh,148:748},{13:$Vg,145:$Vh,148:749},{13:$VE2,150:750,151:577},{394:[1,751]},o($Vf,[2,651],{152:$Vm3}),o($Vn3,[2,136]),{43:[1,753]},{394:[1,754]},o($Vf,[2,655]),o($Vf,[2,657]),o($Vf,[2,658]),o($Vf,[2,660]),o($Vf,[2,661]),{105:755,106:$V31},o($VJ1,[2,104]),o($Vf,[2,666],{105:756,106:$V31}),{105:757,106:$V31},{105:758,106:$V31},o($VF1,[2,105]),o($Vf,[2,683]),{30:[1,760],38:759,39:$Vl,40:$Vm,41:$Vn},o($Vf,[2,256]),{14:[1,762],200:[1,761]},o($Vo3,[2,226],{200:[1,763]}),o($Vf,[2,686],{30:[1,764]}),o($Vf,[2,687]),{13:$VR1,30:$VS1,418:765,419:421},{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V42,145:$Vh,148:74,157:483,169:$V52,255:768,256:769,257:450,259:451,260:452,262:453,263:455,264:456,265:457,267:458,273:459,274:460,275:461,276:462,277:463,278:464,279:468,280:469,283:465,284:466,285:467,286:470,287:471,294:473,295:476,296:477,297:480,298:481,299:482,420:766,421:767},o($VF2,[2,697]),{145:[1,770]},{13:[1,771],14:$Vw1,143:336,144:773,145:[1,772]},o($VT1,[2,156]),o($Vf,[2,157]),o($Vf,[2,158]),o($VU1,[2,130]),o($VW1,[2,133]),o($VW1,[2,132]),o($Vz,[2,271]),o($Vp3,$Vq3,{225:774,229:775,254:[1,776]}),o($Vz,$Vq3,{225:777,254:$Vr3}),{30:[1,780],233:[1,779]},o($Vz,$Vq3,{225:781,254:$Vr3}),{233:[1,782]},{13:$Vg,30:[1,785],103:$Vs3,145:$Vh,148:74,157:73,234:783,235:784,236:786,237:787,247:788,248:790},o($V12,[2,293]),o($Vz,$Vq3,{225:791,254:$Vr3}),{13:$Vg,103:$Vs3,145:$Vh,148:74,157:170,234:792,236:786,247:788},{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V42,145:$Vh,148:74,157:483,169:$V52,257:793,259:794,260:452,262:453,263:455,264:456,265:457,267:458,273:459,274:460,275:461,276:462,277:463,278:464,279:468,280:469,283:465,284:466,285:467,286:470,287:471,294:473,295:476,296:477,297:480,298:481,299:482},{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V62,145:$Vh,148:74,157:492,169:$V72,257:795,260:487,263:455,265:457,273:459,274:489,277:463,278:464,283:465,284:466,285:467,294:473,296:491,298:481},{13:$Vg,30:[1,797],102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V42,145:$Vh,148:74,157:483,169:$V52,257:796,259:798,260:452,262:453,263:455,264:456,265:457,267:458,273:459,274:460,275:461,276:462,277:463,278:464,279:468,280:469,283:465,284:466,285:467,286:470,287:471,294:473,295:476,296:477,297:480,298:481,299:482},{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V62,145:$Vh,148:74,157:492,169:$V72,257:799,260:487,263:455,265:457,273:459,274:489,277:463,278:464,283:465,284:466,285:467,294:473,296:491,298:481},o($VQ2,[2,344]),o($VQ2,[2,346]),o($VQ2,[2,348]),o($Vt3,[2,354],{269:800,138:[1,801]}),o($VQ2,[2,349]),{13:$Vg,14:$V1,15:804,30:$V5,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,145:$Vh,148:74,157:483,169:$V52,274:802,276:803,283:465,284:466,285:467,286:470,287:471,294:473,295:476,296:477,297:480,298:481,299:482},o($VT2,[2,378]),o($VT2,[2,380]),o($Vu3,[2,35]),o($Vu3,[2,36]),o($Vu3,[2,37]),o($Vu3,[2,38]),o($Vu3,[2,39]),o($Vu3,[2,40]),{30:[1,807],169:$Vp1,290:805,291:806,292:808,293:809},{30:[1,811],37:$VV2,78:$V03,281:810,282:$V13},o($Vv3,[2,364]),o($Vv3,[2,365]),o($Vv3,[2,366]),{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,145:$Vh,148:74,157:492,169:$V72,274:812,283:465,284:466,285:467,294:473,296:491,298:481},o($VT2,[2,379]),{169:$Vq1,290:805,292:808},{37:$VV2,78:$V03,281:813,282:$V13},{170:$Vw3,258:$VM2},{170:[1,815],258:$VN2},o($V33,[2,391]),{13:$Vg,14:[1,818],108:484,109:$V41,145:$Vh,148:74,157:483,298:816,299:817},o($V33,[2,82]),o($V43,[2,403]),o($Vz,$Vq3,{225:774,254:$Vr3}),{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V62,145:$Vh,148:74,157:492,169:$V72,257:793,260:487,263:455,265:457,273:459,274:489,277:463,278:464,283:465,284:466,285:467,294:473,296:491,298:481},{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,138:$V62,145:$Vh,148:74,157:492,169:$V72,257:796,260:487,263:455,265:457,273:459,274:489,277:463,278:464,283:465,284:466,285:467,294:473,296:491,298:481},{13:$Vg,102:474,103:$V22,104:$V32,105:475,106:$V31,108:484,109:$V41,145:$Vh,148:74,157:492,169:$V72,274:802,283:465,284:466,285:467,294:473,296:491,298:481},{170:$Vw3,258:$V83},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,298:816},o($Va2,[2,427]),o($Vb2,[2,430]),o($Vb2,[2,431]),o($Vb2,[2,429]),{317:[1,819]},{317:[1,820]},{317:[1,821]},{13:$Vg,30:[1,824],143:285,145:$VI,147:311,148:284,149:313,169:$Vp1,208:822,209:823,292:312,293:314,338:307,340:308,341:309,343:310},{13:$Vg,145:$Vh,147:311,148:321,169:$Vq1,208:825,292:312,338:319,340:320},{30:[1,826],317:$Vx3},o($Vb3,[2,476]),{317:[2,466]},{30:[1,827],317:$Vy3},{30:[1,828],317:$Vz3},{317:[2,469]},{30:[1,829],317:$VA3},{317:[1,830]},{13:$Vg,145:$Vh,147:311,148:321,169:$Vq1,208:831,292:312,338:319,340:320},{317:$Vx3},{317:$Vy3},{317:$Vz3},{317:$VA3},o($Vp2,$VB3,{360:832,361:833,366:[1,834]}),o($Vr2,[2,505]),o($Vr2,[2,504],{360:832,366:$VC3}),{170:$VD3,345:836},{2:[1,838],170:$VD3,345:837},{2:[1,840],170:$VD3,345:839},{170:[2,519]},o($VE3,[2,520]),{170:[2,521]},o($VE3,[2,522]),{170:[2,523]},o($VE3,[2,524]),{170:[2,525]},o($VE3,[2,526]),{170:[2,527]},o($VE3,[2,528]),{170:[2,529]},o($VE3,[2,530]),{170:[2,531]},o($VE3,[2,532]),o($Vr2,$VB3,{360:832,366:$VC3}),{13:$Vg,145:$Vh,148:74,157:170,212:841,247:169,300:66,301:$Vi,303:842},o($VC,[2,417],{152:$Vr1}),o($Vw2,[2,424]),o($Vw2,[2,425]),o($Vf,[2,191]),o($Vf,[2,195]),{197:843,198:$VQ1},{198:[2,69]},{198:[2,70]},o([6,7,30,86,87],[2,198]),{13:$Vy2,179:844,180:537},o($Vk3,[2,202]),o($Vk3,[2,203],{182:845,2:[2,219]}),o($Vk3,[2,205]),o($Vk3,[2,206]),o($Vk3,[2,207]),o($Vk3,[2,208]),o($Vk3,[2,209]),o($Vk3,[2,210]),o($Vk3,[2,211]),o($Vk3,[2,212]),o($Vk3,[2,213]),o($Vk3,[2,214]),o($Vk3,[2,215]),o($Vk3,[2,216]),o($Vk3,[2,217]),o($Vk3,[2,218]),o($Vf,[2,189]),o($Vf,[2,190]),o($VH1,[2,183],{174:846,166:847,167:[1,848]}),o($Vl3,[2,182]),o($Vz2,[2,168],{107:[1,849]}),o($Vf,[2,610]),{394:[1,850]},o($Vf,[2,584]),o($Vf,[2,587]),o($Vf,[2,588]),o($Vf,[2,589]),o($Vf,[2,609]),o($Vf,[2,611]),o($Vf,[2,608]),o($Vf,[2,615]),o($Vf,[2,619]),o($Vf,[2,620]),o($Vf,[2,628]),o($Vf,[2,637]),o($Vf,[2,636]),o($Vf,[2,638]),o($Vf,[2,631]),{152:$Vm3,170:[1,851]},{395:[1,852]},{13:$VE2,151:853},{105:854,106:$V31},{395:[1,855]},o($Vf,[2,669],{408:[1,856]}),o($Vf,[2,670],{408:[1,857]}),o($Vf,[2,667],{30:[1,858],408:[1,859]}),o($Vf,[2,668],{408:[1,860]}),{13:[1,861]},o($Vf,[2,255]),o($Vo3,[2,221]),o($Vo3,[2,224],{199:[1,862],200:[1,863]}),o($Vo3,[2,225]),o($Vf,[2,688]),o($VF2,[2,695]),o($VF2,[2,696]),o($VF2,[2,700]),o($VF2,[2,701],{258:$VM2}),o($VF2,[2,702],{258:$VN2}),o($Vj1,[2,145]),o($Vj1,[2,144]),{107:[1,864],146:$Vi1},o($Vj1,[2,147]),o($Vp3,[2,280]),o($Vz,[2,284]),{30:[1,866],103:$VF3},o($Vz,[2,283]),{103:$VF3},{13:$Vg,14:$V1,15:874,30:[1,871],103:$Vs3,145:$Vh,148:74,157:73,236:872,237:873,240:867,241:868,242:869,243:870,247:788,248:790},o($VI2,[2,306]),o($Vz,[2,282]),{13:$Vg,103:$Vs3,145:$Vh,148:74,157:170,236:876,240:875,242:869,247:788},o($VY1,$VG3,{148:74,157:170,247:788,236:877,13:$Vg,103:$Vs3,145:$Vh,152:[1,878]}),o($V12,[2,291]),o($V12,[2,292],{148:74,157:170,247:788,236:879,13:$Vg,103:$Vs3,145:$Vh}),o($VH3,[2,294]),o($V12,[2,296]),o($VI3,[2,318]),o($VI3,[2,319]),o([2,6,7,152,170,239,249,250,251,254],[2,320]),o($Vz,[2,281]),o($V12,$VG3,{148:74,157:170,247:788,236:877,13:$Vg,103:$Vs3,145:$Vh}),o($VO2,[2,334]),o($VO2,[2,336]),o($VO2,[2,337]),o($VO2,[2,339]),o($VO2,[2,341]),o($VO2,[2,342]),o($VO2,[2,343]),{270:880,271:[1,881],272:[1,882]},o($Vt3,[2,355]),o($VT2,[2,367]),o($VT2,[2,369]),o($VT2,[2,370]),o($VT2,[2,381]),o($VT2,[2,383]),o($VT2,[2,384]),o($VT2,[2,387]),o($VT2,[2,388]),{169:$Vp1,290:883,291:884,292:808,293:809},o($VT2,[2,386]),o($VT2,[2,368]),{169:$Vq1,290:883,292:808},o($V33,[2,389]),o($V33,[2,390]),o($V63,[2,397]),o($V43,[2,399]),o($V43,[2,400]),{13:$Vg,30:[1,887],143:285,145:$VI,147:311,148:284,149:313,169:$Vp1,208:885,209:886,292:312,293:314,338:307,340:308,341:309,343:310},{13:$Vg,145:$Vh,147:311,148:321,169:$Vq1,208:888,292:312,338:319,340:320},{13:$Vg,145:$Vh,147:311,148:321,169:$Vq1,208:889,292:312,338:319,340:320},o($VJ3,$VK3,{318:890,320:891,331:$VL3}),o($Va3,[2,446],{318:893,331:$VM3}),o($Va3,[2,458],{318:895,331:$VM3}),o($Va3,[2,445],{318:896,331:$VM3}),{317:[2,471]},{317:[2,472]},{317:[2,473]},{317:[2,474]},{13:$Vg,145:$Vh,147:311,148:321,169:$Vq1,208:897,292:312,338:319,340:320},o($Va3,$VK3,{318:890,331:$VM3}),o($Vo2,[2,540]),o($Vq2,$Vg3,{339:898}),{30:[1,900],367:[1,899]},{367:[1,901]},{170:[1,902]},{170:[1,903]},o($VN3,[2,517]),{170:[1,904]},o($VN3,[2,518]),{36:$VA,170:$Vx,213:158,216:165},o([36,170],$VD,{152:$Vr1}),o([2,6,7,30,167],[2,220]),o($Vk3,[2,200]),{2:[1,905]},o($VH1,[2,178]),o($VH1,[2,184]),{30:[1,907],168:[1,906]},o($Vz2,[2,169],{106:[1,908]}),{395:[1,909]},o($Vf,[2,643],{30:[1,910],119:[1,911]}),o($Vf,[2,649]),o($Vn3,[2,137]),o($Vn3,[2,138]),o($Vf,[2,653]),{13:$VE2,150:912,151:577},{13:$VE2,150:913,151:577},o($Vf,[2,671],{151:577,150:914,13:$VE2}),{13:$VE2,150:915,151:577},{13:$VE2,150:916,151:577},o($Vf,[2,254]),{200:[1,917]},o($Vo3,[2,223]),{145:[1,918]},o($Vp3,[2,329]),o($Vz,[2,330]),o($VG2,$VO3,{152:[1,919]}),o($VI2,[2,305]),o($VP3,[2,307]),o($VI2,[2,309]),o([2,6,7,170,249,250,251,254],$Vk,{148:74,157:170,247:788,236:876,242:920,13:$Vg,103:$Vs3,145:$Vh}),o($VQ3,$VR3,{244:921,249:$VS3,250:$VT3}),o($VU3,$VR3,{244:924,249:$VS3,250:$VT3}),o($VU3,$VR3,{244:925,249:$VS3,250:$VT3}),o($VI2,$VO3,{152:$VV3}),o($VU3,$VR3,{244:927,249:$VS3,250:$VT3}),o($VH3,[2,295]),{13:$Vg,14:$V1,15:930,30:$V5,145:$Vh,148:74,157:931,237:929,238:928,248:790},o($V12,[2,297]),o($VQ2,[2,351]),o($VQ2,[2,352]),o($VQ2,[2,353]),o($VT2,[2,382]),o($VT2,[2,385]),o($VJ3,$VW3,{318:932,320:933,331:$VL3}),o($Va3,[2,452],{318:934,331:$VM3}),o($Va3,[2,460],{318:935,331:$VM3}),o($Va3,[2,451],{318:936,331:$VM3}),o($Va3,[2,450],{318:937,331:$VM3}),o($VJ3,[2,442]),o($Va3,[2,449]),{13:$Vg,14:$VX3,30:[1,942],108:484,109:$V41,145:$Vh,148:74,157:483,169:[1,944],294:946,295:947,296:477,297:480,298:481,299:482,332:940,333:941,334:938,335:939,336:943,337:945},o($Va3,[2,448]),{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,169:[1,950],294:951,296:491,298:481,334:949,335:939,336:943},o($Va3,[2,459]),o($Va3,[2,447]),o($Va3,$VW3,{318:932,331:$VM3}),o($Vr2,[2,541],{360:832,366:$VC3}),{30:[1,954],362:952,363:[1,955],364:[1,956],365:953},o($Vq2,[2,552]),{362:957,363:[1,958],364:[1,959]},o($VN3,[2,514]),o($VN3,[2,515]),o($VN3,[2,516]),o($Vk3,[2,204]),o($VH1,[2,176],{169:[1,960]}),o($VH1,[2,177]),o($Vz2,$VE3),o($Vf,[2,579]),o($Vf,[2,644]),o($Vf,[2,645]),o($Vf,[2,674],{152:$Vm3}),o($Vf,[2,675],{152:$Vm3}),o($Vf,[2,676],{152:$Vm3}),o($Vf,[2,672],{152:$Vm3}),o($Vf,[2,673],{152:$Vm3}),o($Vo3,[2,222]),o($Vj1,[2,146]),{13:$Vg,14:$V1,15:874,30:$V5,103:$Vs3,145:$Vh,148:74,157:73,236:872,237:873,242:961,243:962,247:788,248:790},o($VI2,[2,310]),o($VP3,$VY3,{245:963,246:964,251:[1,965]}),o($VQ3,[2,322]),o($VQ3,[2,323]),o($VZ3,$VY3,{245:966,251:$V_3}),o($VZ3,$VY3,{245:968,251:$V_3}),{13:$Vg,103:$Vs3,145:$Vh,148:74,157:170,236:876,242:961,247:788},o($VZ3,$VY3,{245:963,251:$V_3}),o($V12,[2,298],{152:[1,969]}),o($V$3,[2,301]),o($V$3,[2,302]),{31:970,32:$VL,33:$VM,34:$VN},o($VJ3,[2,444]),o($Va3,[2,456]),o($Va3,[2,455]),o($Va3,[2,461]),o($Va3,[2,454]),o($Va3,[2,453]),o($VJ3,$V04,{261:$V14}),o($VJ3,[2,481]),o($Va3,[2,477]),o($Va3,[2,478]),o($Va3,[2,479],{43:$V24,261:$V34}),o($V44,[2,486]),{13:$Vg,14:[1,976],30:[1,977],108:484,109:$V41,145:$Vh,148:74,157:483,294:946,295:947,296:477,297:480,298:481,299:482,332:975,334:974,336:943,337:945},o($Va3,[2,488],{261:[1,978]}),{43:[1,979]},{43:[1,980]},{43:$V54},o($Va3,$V04,{261:$V64}),{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:951,296:491,298:481,334:983,336:943},{43:[1,984]},{13:[1,985],30:[1,987],112:$V74,368:986},{112:$V74,368:989},o($Vq2,[2,551]),{169:[1,990]},{169:[1,991]},{13:[1,992],112:$V74,368:986},{169:[1,993]},{169:[1,994]},{13:$V84,106:$V94,164:995,165:996},o($VP3,[2,308]),o($VI2,[2,311],{152:[1,999]}),o($VP3,[2,314]),o($VZ3,[2,316]),{30:[1,1002],252:$Va4,253:$Vb4},o($VZ3,[2,315]),{252:$Va4,253:$Vb4},o($VZ3,[2,317]),o($V12,[2,299],{148:74,157:170,236:786,247:788,234:1003,13:$Vg,103:$Vs3,145:$Vh}),{13:$Vg,14:$Vw1,143:336,144:334,145:$VI,148:74,156:1004,157:278},{13:$Vg,14:$VX3,30:[1,1007],108:484,109:$V41,145:$Vh,148:74,157:483,294:946,295:947,296:477,297:480,298:481,299:482,336:1005,337:1006},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:951,296:491,298:481,334:1008,336:943},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:1009,296:491,298:481},{170:$Vc4,261:$V14},{170:[1,1011]},o($Va3,[2,484],{43:$V54,261:[1,1012]}),{43:$V24,261:$V34},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:951,296:491,298:481,334:1013,336:943},{13:$Vg,14:[1,1017],30:[1,1016],108:484,109:$V41,145:$Vh,148:74,157:483,294:1014,295:1015,296:477,297:480,298:481,299:482},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:1018,296:491,298:481},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:1019,296:491,298:481},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:951,296:491,298:481,336:1005},{170:$Vc4,261:$V64},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:1014,296:491,298:481},{30:[1,1021],112:$V74,368:1020},o($Vo2,[2,547]),o($Vq2,[2,550]),{13:[1,1022],169:[1,1023]},o($Vq2,[2,548]),{13:$Vg,14:$Vw1,143:336,144:1025,145:$VI,148:74,156:1024,157:278},{13:$Vg,14:$Vw1,143:336,144:1027,145:$VI,148:74,156:1026,157:278},{112:$V74,368:1020},{13:$Vg,145:$Vh,148:74,156:1024,157:278},{13:$Vg,145:$Vh,148:74,156:1026,157:278},{152:[1,1029],170:[1,1028]},o($Vk3,[2,171]),{43:[1,1030]},{107:[1,1031]},o($VI2,[2,312],{148:74,157:170,247:788,242:869,236:876,240:1032,13:$Vg,103:$Vs3,145:$Vh}),o($VP3,[2,325]),o($VP3,[2,326]),o($VZ3,[2,327]),o($V12,[2,300],{148:74,157:170,247:788,236:877,13:$Vg,103:$Vs3,145:$Vh}),{31:530,32:$VL,33:$Vu2,34:$Vv2},o($V44,[2,487]),o($Va3,[2,491],{261:[1,1033]}),o($Va3,[2,492],{43:$V24,261:[1,1034]}),o($Va3,[2,490],{261:$V64}),o($Vd4,[2,499]),o($VJ3,[2,482]),o($Va3,[2,483]),{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:951,296:491,298:481,334:1035,336:943},o($Va3,[2,489],{261:$V64}),o($V44,[2,495]),o($Vd4,[2,496]),o($Vd4,[2,498]),o($Vd4,[2,501]),o($Vd4,[2,497]),o($Vd4,[2,500]),o($Vo2,[2,546]),o($Vq2,[2,549]),o($Vo2,[2,553]),{13:[1,1036]},{31:530,32:$VL,33:$VM,34:$VN,170:[1,1037]},{112:[2,544]},{31:530,32:$VL,33:$VM,34:$VN,170:[1,1038]},{112:[2,545]},o($VH1,[2,175]),{13:$V84,106:$V94,165:1039},{13:[1,1040]},{106:[1,1041]},o($VI2,[2,313],{152:$VV3}),{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:951,296:491,298:481,334:1042,336:943},{13:$Vg,108:484,109:$V41,145:$Vh,148:74,157:492,294:951,296:491,298:481,334:1043,336:943},o($Va3,[2,485],{261:$V64}),{152:[1,1044]},o($Ve4,[2,542]),o($Ve4,[2,543]),o($Vk3,[2,172]),o($Vk3,[2,173]),{43:[1,1045]},o($Va3,[2,493],{261:$V64}),o($Va3,[2,494],{261:$V64}),{13:[1,1046]},{106:[1,1047]},{170:[1,1048]},{107:[1,1049]},o($Vo2,[2,554]),{106:[1,1050]},o($Vk3,[2,174])],
defaultActions: {60:[2,3],155:[2,2],266:[2,65],267:[2,66],393:[2,79],394:[2,80],500:[2,463],502:[2,465],543:[2,47],544:[2,48],669:[2,466],672:[2,469],676:[2,464],677:[2,467],678:[2,468],679:[2,470],686:[2,519],688:[2,521],690:[2,523],692:[2,525],694:[2,527],696:[2,529],698:[2,531],708:[2,69],709:[2,70],826:[2,471],827:[2,472],828:[2,473],829:[2,474],1025:[2,544],1027:[2,545]},
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

var mergeSuggestKeywords = function() {
  var result = [];
  Array.prototype.slice.call(arguments).forEach(function (suggestion) {
    if (typeof suggestion !== 'undefined' && typeof suggestion.suggestKeywords !== 'undefined') {
      result = result.concat(suggestion.suggestKeywords);
    }
  });
  if (result.length > 0) {
    return { suggestKeywords: result }
  }
  return {}
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

  if (typeof identifierChain === 'undefined' || typeof tablePrimaries === 'undefined') {
    return;
  }

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

  suggestKeywords(keywords);
}

var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords.sort();
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
    if (parser.yy.result.error) {
      console.log(parser.yy.result.error);
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
case 3: parser.yy.cursorFound = true; return 30; 
break;
case 4: parser.yy.cursorFound = true; return 14; 
break;
case 5: return 112; 
break;
case 6: return 404; 
break;
case 7: return 195; 
break;
case 8: return 396; 
break;
case 9: return 57; 
break;
case 10: return 397; 
break;
case 11: return 398; 
break;
case 12: determineCase(yy_.yytext); return 28; 
break;
case 13: return 322; 
break;
case 14: return 61; 
break;
case 15: return 64; 
break;
case 16: return 67; 
break;
case 17: return 196; 
break;
case 18: determineCase(yy_.yytext); return 203; 
break;
case 19: return 119; 
break;
case 20: return 72; 
break;
case 21: return 121; 
break;
case 22: return '<hive>FUNCTION'; 
break;
case 23: return 399; 
break;
case 24: return 402; 
break;
case 25: return 37; 
break;
case 26: return 54; 
break;
case 27: return 55; 
break;
case 28: this.begin('hdfs'); return 80; 
break;
case 29: return 366; 
break;
case 30: return 75; 
break;
case 31: this.begin('hdfs'); return 86; 
break;
case 32: return 407; 
break;
case 33: return '<hive>MACRO'; 
break;
case 34: return 408; 
break;
case 35: return 409; 
break;
case 36: return 92; 
break;
case 37: return 95; 
break;
case 38: return 68; 
break;
case 39: return 40; 
break;
case 40: return 98; 
break;
case 41: return 411; 
break;
case 42: return '<hive>TEMPORARY'; 
break;
case 43: return 412; 
break;
case 44: return 101; 
break;
case 45: return 363; 
break;
case 46: return 364; 
break;
case 47: return 34; 
break;
case 48: return 83; 
break;
case 49: return 89; 
break;
case 50: return 24; 
break;
case 51: return 25; 
break;
case 52: return '<impala>ANTI'; 
break;
case 53: return 390; 
break;
case 54: return 58; 
break;
case 55: determineCase(yy_.yytext); return 29; 
break;
case 56: return 62; 
break;
case 57: return 65; 
break;
case 58: return 69; 
break;
case 59: determineCase(yy_.yytext); return 204; 
break;
case 60: return 73; 
break;
case 61: return 252; 
break;
case 62: return 123; 
break;
case 63: return '<impala>FUNCTION'; 
break;
case 64: return 400; 
break;
case 65: return 406; 
break;
case 66: return 116; 
break;
case 67: return '<impala>INCREMENTAL'; 
break;
case 68: this.begin('hdfs'); return 81; 
break;
case 69: return 78; 
break;
case 70: return 325; 
break;
case 71: return 253; 
break;
case 72: return 76; 
break;
case 73: this.begin('hdfs'); return 87; 
break;
case 74: return 251; 
break;
case 75: return 410; 
break;
case 76: return 329; 
break;
case 77: return 93; 
break;
case 78: return 96; 
break;
case 79: return 70; 
break;
case 80: return 391; 
break;
case 81: return 41; 
break;
case 82: return 99; 
break;
case 83: return 33; 
break;
case 84: return 84; 
break;
case 85: return 90; 
break;
case 86: return 261; 
break;
case 87: return 111; 
break;
case 88: return 249; 
break;
case 89: return 186; 
break;
case 90: return 187; 
break;
case 91: return 233; 
break;
case 92: return 192; 
break;
case 93: determineCase(yy_.yytext); return 27; 
break;
case 94: return 50; 
break;
case 95: return 191; 
break;
case 96: return 250; 
break;
case 97: return 189; 
break;
case 98: determineCase(yy_.yytext); return 205; 
break;
case 99: return 135; 
break;
case 100: return 272; 
break;
case 101: return 188; 
break;
case 102: return 36; 
break;
case 103: return 330; 
break;
case 104: return 'INNER'; 
break;
case 105: return 328; 
break;
case 106: return 323; 
break;
case 107: return 114; 
break;
case 108: return 134; 
break;
case 109: return 185; 
break;
case 110: return 210; 
break;
case 111: return 268; 
break;
case 112: return 282; 
break;
case 113: return 317; 
break;
case 114: return 326; 
break;
case 115: return 370; 
break;
case 116: return 138; 
break;
case 117: return 'NOT_IN'; 
break;
case 118: return 331; 
break;
case 119: return 258; 
break;
case 120: return 239; 
break;
case 121: return 'ROLE'; 
break;
case 122: return 51; 
break;
case 123: determineCase(yy_.yytext); return 211; 
break;
case 124: return 327; 
break;
case 125: return 415; 
break;
case 126: determineCase(yy_.yytext); return 369; 
break;
case 127: return 184; 
break;
case 128: return 190; 
break;
case 129: return 39; 
break;
case 130: return 194; 
break;
case 131: return 183; 
break;
case 132: return 271; 
break;
case 133: determineCase(yy_.yytext); return 413; 
break;
case 134: determineCase(yy_.yytext); return 422; 
break;
case 135: return 193; 
break;
case 136: return 367; 
break;
case 137: return 230; 
break;
case 138: return 103; 
break;
case 139: return 13; 
break;
case 140: parser.yy.cursorFound = true; return 30; 
break;
case 141: parser.yy.cursorFound = true; return 14; 
break;
case 142: return 198; 
break;
case 143: return 199; 
break;
case 144: this.popState(); return 200; 
break;
case 145: return 7; 
break;
case 146: return yy_.yytext; 
break;
case 147: return yy_.yytext; 
break;
case 148: return '['; 
break;
case 149: return ']'; 
break;
case 150: this.begin('backtickedValue'); return 145; 
break;
case 151: if (yy_.yytext.indexOf('\u2020') !== -1 || yy_.yytext.indexOf('\u2021') !== -1) {
                                        this.popState();
                                        return 146;
                                      }
                                      return 107;
                                    
break;
case 152: this.popState(); return 145; 
break;
case 153: this.begin('SingleQuotedValue_Complete'); return 106; 
break;
case 154: return 107; 
break;
case 155: this.popState(); return 106; 
break;
case 156: this.begin('DoubleQuotedValue_Complete'); return 109; 
break;
case 157: return 107; 
break;
case 158: this.popState(); return 109; 
break;
case 159: return 7; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:AS\b)/i,/^(?:ALL\b)/i,/^(?:BINARY\b)/i,/^(?:COLUMNS\b)/i,/^(?:COMMENT\b)/i,/^(?:COMPACTIONS\b)/i,/^(?:CONF\b)/i,/^(?:CREATE\b)/i,/^(?:CROSS\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DATE\b)/i,/^(?:DESCRIBE\b)/i,/^(?:EXTENDED\b)/i,/^(?:EXTERNAL\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:IN\b)/i,/^(?:INDEX\b)/i,/^(?:INDEXES\b)/i,/^(?:INPATH\b)/i,/^(?:LATERAL\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:LOCKS\b)/i,/^(?:MACRO\b)/i,/^(?:PARTITION\b)/i,/^(?:PARTITIONS\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:TBLPROPERTIES\b)/i,/^(?:TEMPORARY\b)/i,/^(?:TRANSACTIONS\b)/i,/^(?:USER\b)/i,/^(?:explode\b)/i,/^(?:posexplode\b)/i,/^(?:[.])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:AGGREGATE\b)/i,/^(?:ANALYTIC\b)/i,/^(?:ANTI\b)/i,/^(?:COLUMN\b)/i,/^(?:COMMENT\b)/i,/^(?:CREATE\b)/i,/^(?:CURRENT\b)/i,/^(?:DATA\b)/i,/^(?:DATABASES\b)/i,/^(?:DESCRIBE\b)/i,/^(?:EXTERNAL\b)/i,/^(?:FIRST\b)/i,/^(?:FORMATTED\b)/i,/^(?:FUNCTION\b)/i,/^(?:FUNCTIONS\b)/i,/^(?:GRANT\b)/i,/^(?:GROUP\b)/i,/^(?:INCREMENTAL\b)/i,/^(?:INPATH\b)/i,/^(?:IN\b)/i,/^(?:INNER\b)/i,/^(?:LAST\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:NULLS\b)/i,/^(?:PARTITIONS\b)/i,/^(?:RIGHT\b)/i,/^(?:ROLE\b)/i,/^(?:ROLES\b)/i,/^(?:SCHEMAS\b)/i,/^(?:STATS\b)/i,/^(?:TABLE\b)/i,/^(?:TABLES\b)/i,/^(?:[.])/i,/^(?:\[)/i,/^(?:\])/i,/^(?:AND\b)/i,/^(?:AS\b)/i,/^(?:ASC\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DATABASE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DESC\b)/i,/^(?:DOUBLE\b)/i,/^(?:DROP\b)/i,/^(?:EXISTS\b)/i,/^(?:FALSE\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:OUTER\b)/i,/^(?:INNER\b)/i,/^(?:RIGHT\b)/i,/^(?:FULL\b)/i,/^(?:GROUP\b)/i,/^(?:IF\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:IN\b)/i,/^(?:JOIN\b)/i,/^(?:LEFT\b)/i,/^(?:LIKE\b)/i,/^(?:NOT\b)/i,/^(?:NOT IN\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:ROLE\b)/i,/^(?:SCHEMA\b)/i,/^(?:SELECT\b)/i,/^(?:SEMI\b)/i,/^(?:SET\b)/i,/^(?:SHOW\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:TRUE\b)/i,/^(?:UPDATE\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:VIEW\b)/i,/^(?:WHERE\b)/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\u2020)/i,/^(?:\u2021)/i,/^(?:\s+['])/i,/^(?:[^'\u2020\u2021]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>]+)/i,/^(?:\[)/i,/^(?:\])/i,/^(?:`)/i,/^(?:[^`]+)/i,/^(?:`)/i,/^(?:')/i,/^(?:[^']+)/i,/^(?:')/i,/^(?:")/i,/^(?:[^"]+)/i,/^(?:")/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[140,141,142,143,144,145],"inclusive":false},"DoubleQuotedValue_Complete":{"rules":[157,158],"inclusive":false},"SingleQuotedValue_Complete":{"rules":[154,155],"inclusive":false},"backtickedValue":{"rules":[151,152],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,146,147,148,149,150,153,156,159],"inclusive":true},"impala":{"rules":[0,1,2,3,4,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,146,147,148,149,150,153,156,159],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,146,147,148,149,150,153,156,159],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});