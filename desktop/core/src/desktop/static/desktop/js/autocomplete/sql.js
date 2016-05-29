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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,15],$V1=[1,16],$V2=[1,9],$V3=[1,11],$V4=[1,17],$V5=[1,18],$V6=[1,13],$V7=[1,14],$V8=[9,10],$V9=[1,36],$Va=[1,35],$Vb=[4,5,9,10,16,38,40,68,75,79,81,86,90,91,92,93,94,95,103,106,107,115,118],$Vc=[26,27],$Vd=[28,29],$Ve=[9,10,68],$Vf=[1,48],$Vg=[4,9,10,40,68,75,103,106,107],$Vh=[1,54],$Vi=[1,63],$Vj=[1,64],$Vk=[1,65],$Vl=[1,66],$Vm=[1,67],$Vn=[1,74],$Vo=[4,9,10,75,103,106,107],$Vp=[16,102],$Vq=[2,99],$Vr=[1,96],$Vs=[1,91],$Vt=[4,5,9,10,75,103,106,107],$Vu=[4,5,9,10,40,75,103,106,107],$Vv=[1,107],$Vw=[4,5,9,10,40,75,103,106,107,115,118],$Vx=[9,10,22],$Vy=[1,121],$Vz=[1,122],$VA=[4,5,9,10,38,40,75,79,103,106,107,115,118],$VB=[4,5,9,10,38,40,75,79,81,103,106,107,115,118],$VC=[4,5,9,10,38,40,75,79,81,86,90,91,92,93,94,95,103,106,107,115,118],$VD=[1,137],$VE=[1,138],$VF=[38,40],$VG=[16,36,102],$VH=[4,5,9,10,38,40,75,79,81,86,90,91,92,93,94,95,101,103,106,107,115,118];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"InitResults":6,"Sql":7,"SqlStatements":8,";":9,"EOF":10,"SqlStatement":11,"UseStatement":12,"DataManipulation":13,"TableDefinition":14,"QueryExpression":15,"REGULAR_IDENTIFIER":16,"USE":17,"HiveOrImpalaLoad":18,"HiveOrImpalaData":19,"HiveOrImpalaInpath":20,"HdfsPath":21,"INTO":22,"TABLE":23,"<hive>LOAD":24,"<impala>LOAD":25,"<hive>DATA":26,"<impala>DATA":27,"<hive>INPATH":28,"<impala>INPATH":29,"CREATE":30,"TableScope":31,"TableElementList":32,"TableLocation":33,"<hive>EXTERNAL":34,"<impala>EXTERNAL":35,"(":36,"TableElements":37,")":38,"TableElement":39,",":40,"ColumnDefinition":41,"PrimitiveType":42,"HiveOrImpalaLocation":43,"<hive>LOCATION":44,"<impala>LOCATION":45,"HDFS_START_QUOTE":46,"HDFS_PATH":47,"HDFS_END_QUOTE":48,"TINYINT":49,"SMALLINT":50,"INT":51,"BIGINT":52,"BOOLEAN":53,"FLOAT":54,"DOUBLE":55,"STRING":56,"DECIMAL":57,"CHAR":58,"VARCHAR":59,"TIMESTAMP":60,"<hive>BINARY":61,"<hive>DATE":62,"SELECT":63,"SelectList":64,"TableExpression":65,"FromClause":66,"SelectConditionList":67,"FROM":68,"TableReferenceList":69,"SelectCondition":70,"WhereClause":71,"GroupByClause":72,"OrderByClause":73,"LimitClause":74,"WHERE":75,"SearchCondition":76,"BooleanValueExpression":77,"BooleanTerm":78,"OR":79,"BooleanFactor":80,"AND":81,"NOT":82,"BooleanTest":83,"Predicate":84,"CompOp":85,"IS":86,"TruthValue":87,"ParenthesizedBooleanValueExpression":88,"NonParenthesizedValueExpressionPrimary":89,"=":90,"<>":91,"<":92,">":93,"<=":94,">=":95,"ColumnReference":96,"BasicIdentifierChain":97,"InitIdentifierChain":98,"IdentifierChain":99,"Identifier":100,".":101,"\"":102,"GROUP":103,"BY":104,"ColumnList":105,"ORDER":106,"LIMIT":107,"UNSIGNED_INTEGER":108,"*":109,"DerivedColumn":110,"TableReference":111,"TablePrimaryOrJoinedTable":112,"TablePrimary":113,"JoinedTable":114,"JOIN":115,"JoinSpecification":116,"JoinCondition":117,"ON":118,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",9:";",10:"EOF",16:"REGULAR_IDENTIFIER",17:"USE",22:"INTO",23:"TABLE",24:"<hive>LOAD",25:"<impala>LOAD",26:"<hive>DATA",27:"<impala>DATA",28:"<hive>INPATH",29:"<impala>INPATH",30:"CREATE",34:"<hive>EXTERNAL",35:"<impala>EXTERNAL",36:"(",38:")",40:",",44:"<hive>LOCATION",45:"<impala>LOCATION",46:"HDFS_START_QUOTE",47:"HDFS_PATH",48:"HDFS_END_QUOTE",49:"TINYINT",50:"SMALLINT",51:"INT",52:"BIGINT",53:"BOOLEAN",54:"FLOAT",55:"DOUBLE",56:"STRING",57:"DECIMAL",58:"CHAR",59:"VARCHAR",60:"TIMESTAMP",61:"<hive>BINARY",62:"<hive>DATE",63:"SELECT",68:"FROM",75:"WHERE",79:"OR",81:"AND",82:"NOT",86:"IS",87:"TruthValue",90:"=",91:"<>",92:"<",93:">",94:"<=",95:">=",101:".",102:"\"",103:"GROUP",104:"BY",106:"ORDER",107:"LIMIT",108:"UNSIGNED_INTEGER",109:"*",115:"JOIN",118:"ON"},
productions_: [0,[3,1],[3,1],[6,0],[7,4],[7,3],[8,1],[8,3],[11,1],[11,1],[11,1],[11,1],[11,3],[11,2],[11,1],[12,3],[12,2],[12,2],[13,7],[13,4],[18,1],[18,1],[19,1],[19,1],[20,1],[20,1],[14,6],[14,2],[31,1],[31,1],[32,3],[37,1],[37,3],[39,1],[41,2],[33,2],[43,1],[43,1],[21,3],[21,5],[21,4],[21,3],[21,3],[21,2],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[42,1],[15,3],[15,2],[65,1],[65,2],[65,2],[66,2],[66,2],[67,1],[67,2],[70,1],[70,1],[70,1],[70,1],[70,1],[71,2],[71,2],[76,1],[77,1],[77,3],[78,1],[78,3],[78,3],[80,2],[80,1],[83,1],[83,3],[83,3],[83,4],[84,1],[84,1],[85,1],[85,1],[85,1],[85,1],[85,1],[85,1],[88,3],[88,2],[89,1],[96,1],[97,2],[98,0],[99,1],[99,3],[99,3],[100,1],[100,3],[72,3],[72,2],[73,3],[73,2],[74,2],[74,2],[64,1],[64,3],[64,2],[64,1],[105,1],[105,3],[110,3],[110,3],[110,3],[110,2],[110,1],[110,1],[69,1],[69,3],[111,1],[112,1],[112,1],[113,1],[113,2],[113,3],[113,4],[113,3],[114,4],[114,3],[116,1],[117,2]],
performAction: function anonymous(yytext, yyleng, yylineno, yy, yystate /* action[1] */, $$ /* vstack */, _$ /* lstack */) {
/* this == yyval */

var $0 = $$.length - 1;
switch (yystate) {
case 3:

     parser.yy.result = {};
     parser.yy.cursorFound = false;
     delete parser.yy.latestTableReferences;
     parser.parseError = function (message, error) {
       if (typeof parser.yy.result.suggestColumns !== 'undefined') {
         completeSuggestColumns();
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
case 58:

     completeSuggestColumns();
   
break;
case 61: case 64:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 68: case 69: case 70:

     delete parser.yy.result.suggestStar;
   
break;
case 71:

     suggestKeywords(['WHERE', 'GROUP BY', 'LIMIT']);
   
break;
case 73:

     suggestColumns();
   
break;
case 78:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 95:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 98:

     delete parser.yy.identifierChain;
   
break;
case 99:

     parser.yy.identifierChain = [];
   
break;
case 101:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 103:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 104:

     parser.yy.identifierChain.push($$[$0-1]);
   
break;
case 106: case 108:

     suggestKeywords(['BY']);
   
break;
case 110:

     suggestNumbers([5, 10, 15]);
   
break;
case 112: case 113:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 119:

     parser.yy.result.suggestStar = true;
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 120:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 122:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 128:

     addTableReference({ table: $$[$0] });
   
break;
case 129:

     addTableReference({ table: $$[$0-1], alias: $$[$0] });
   
break;
case 130:

     addTableReference({ database: $$[$0-2], table: $$[$0] });
   
break;
case 131:

     addTableReference({ database: $$[$0-3], table: $$[$0-1], alias: $$[$0] });
   
break;
case 132:

     suggestTables({ database: $$[$0-2] });
   
break;
case 134:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,16,17,24,25,30,63],[2,3],{7:1,6:2}),{1:[3]},{3:10,4:$V0,5:$V1,8:3,11:4,12:5,13:6,14:7,15:8,16:$V2,17:$V3,18:12,24:$V4,25:$V5,30:$V6,63:$V7},{9:[1,19],10:[1,20]},o($V8,[2,6]),o($V8,[2,8]),o($V8,[2,9]),o($V8,[2,10]),o($V8,[2,11]),{3:21,4:$V0,5:$V1},o($V8,[2,14]),{3:23,4:$V0,5:$V1,16:[1,22]},{19:24,26:[1,25],27:[1,26]},{23:[1,28],31:27,34:[1,29],35:[1,30]},{4:$V9,16:$Va,64:31,105:32,109:[1,33],110:34},o($Vb,[2,1]),o($Vb,[2,2]),o($Vc,[2,20]),o($Vc,[2,21]),{3:10,4:$V0,5:$V1,10:[1,37],11:38,12:5,13:6,14:7,15:8,16:$V2,17:$V3,18:12,24:$V4,25:$V5,30:$V6,63:$V7},{1:[2,5]},o($V8,[2,13],{16:[1,39]}),o($V8,[2,16],{3:40,4:$V0,5:$V1}),o($V8,[2,17]),{20:41,28:[1,42],29:[1,43]},o($Vd,[2,22]),o($Vd,[2,23]),{23:[1,44]},o($V8,[2,27]),{23:[2,28]},{23:[2,29]},o($V8,[2,59],{65:45,66:46,68:[1,47]}),o($Ve,[2,111],{40:$Vf}),o($Ve,[2,114],{4:[1,50],16:[1,49]}),o($Vg,[2,115]),o($Vg,[2,121],{5:[1,52],101:[1,51]}),o($Vg,[2,122]),{1:[2,4]},o($V8,[2,7]),o($V8,[2,12]),o($V8,[2,15]),{21:53,46:$Vh},{46:[2,24]},{46:[2,25]},{16:[1,55]},o($V8,[2,58]),o($V8,[2,60],{67:57,70:58,71:59,72:60,73:61,74:62,4:$Vi,5:[1,56],75:$Vj,103:$Vk,106:$Vl,107:$Vm}),{3:69,4:$V0,5:$V1,16:$Vn,69:68,111:70,112:71,113:72,114:73},{4:$V9,16:$Va,110:75},{5:[1,76]},o($Ve,[2,113]),{3:79,4:$V0,5:$V1,16:[1,77],109:[1,78]},o($Vg,[2,120]),o($V8,[2,19],{22:[1,80]}),{5:[1,82],47:[1,81]},{32:83,36:[1,84]},o($V8,[2,61]),o($V8,[2,62],{71:59,72:60,73:61,74:62,70:85,4:$Vi,75:$Vj,103:$Vk,106:$Vl,107:$Vm}),o($Vo,[2,65]),o($Vo,[2,67]),o($Vo,[2,68]),o($Vo,[2,69]),o($Vo,[2,70]),o($Vo,[2,71]),o($Vp,$Vq,{76:86,77:88,78:89,80:90,83:92,84:93,88:94,89:95,96:97,97:98,98:99,4:[1,87],36:$Vr,82:$Vs}),{4:[1,101],104:[1,100]},{4:[1,103],104:[1,102]},{4:[1,105],108:[1,104]},o($Vt,[2,63],{40:[1,106]}),o($Vt,[2,64]),o($Vu,[2,123],{115:$Vv}),o($Vw,[2,125]),o($Vw,[2,126]),o($Vw,[2,127]),o($Vw,[2,128],{16:[1,108],101:[1,109]}),o($Vg,[2,116]),o($Ve,[2,112]),o($Vg,[2,117]),o($Vg,[2,118]),o($Vg,[2,119]),{23:[1,110]},{5:[1,112],48:[1,111]},o($Vx,[2,43],{48:[1,113]}),{33:114,43:115,44:[1,116],45:[1,117]},{16:$Vy,37:118,39:119,41:120},o($Vo,[2,66]),o($Vo,[2,72]),o($Vo,[2,73]),o($Vw,[2,74],{79:$Vz}),o($VA,[2,75]),o($VA,[2,77],{81:[1,123]}),o($Vp,$Vq,{84:93,88:94,89:95,96:97,97:98,98:99,83:124,36:$Vr}),o($VB,[2,81]),o($VB,[2,82],{85:125,86:[1,126],90:[1,127],91:[1,128],92:[1,129],93:[1,130],94:[1,131],95:[1,132]}),o($VC,[2,86]),o($VC,[2,87]),o($Vp,$Vq,{78:89,80:90,83:92,84:93,88:94,89:95,96:97,97:98,98:99,77:133,3:134,4:$V0,5:$V1,36:$Vr,82:$Vs}),o($VC,[2,96]),o($VC,[2,97]),{16:$VD,99:135,100:136,102:$VE},{4:$V9,16:$Va,105:139,110:34},o($Vo,[2,106]),{4:$V9,16:$Va,105:140,110:34},o($Vo,[2,108]),o($Vo,[2,109]),o($Vo,[2,110]),{16:$Vn,111:141,112:71,113:72,114:73},{3:143,4:$V0,5:$V1,16:$Vn,111:142,112:71,113:72,114:73},o($Vw,[2,129]),{3:145,4:$V0,5:$V1,16:[1,144]},{16:[1,146]},o($Vx,[2,38]),o($Vx,[2,41],{47:[1,147],48:[1,148]}),o($Vx,[2,42]),o($V8,[2,26]),{21:149,46:$Vh},{46:[2,36]},{46:[2,37]},{38:[1,150],40:[1,151]},o($VF,[2,31]),o($VF,[2,33]),{42:152,49:[1,153],50:[1,154],51:[1,155],52:[1,156],53:[1,157],54:[1,158],55:[1,159],56:[1,160],57:[1,161],58:[1,162],59:[1,163],60:[1,164],61:[1,165],62:[1,166]},o($Vp,$Vq,{80:90,83:92,84:93,88:94,89:95,96:97,97:98,98:99,78:167,36:$Vr,82:$Vs}),o($Vp,$Vq,{80:90,83:92,84:93,88:94,89:95,96:97,97:98,98:99,78:169,4:[1,168],36:$Vr,82:$Vs}),o($VB,[2,80]),o($Vp,$Vq,{88:94,89:95,96:97,97:98,98:99,84:170,36:$Vr}),{82:[1,172],87:[1,171]},o($VG,[2,88]),o($VG,[2,89]),o($VG,[2,90]),o($VG,[2,91]),o($VG,[2,92]),o($VG,[2,93]),{38:[1,173],79:$Vz},o($VC,[2,95]),o($VC,[2,98],{101:[1,174]}),o($VH,[2,100]),o($VH,[2,103]),{16:[1,175]},o($Vo,[2,105],{40:$Vf}),o($Vo,[2,107],{40:$Vf}),o($Vu,[2,124],{115:$Vv}),{115:$Vv,116:176,117:177,118:[1,178]},o($Vw,[2,134]),o($Vw,[2,130],{16:[1,179]}),o($Vw,[2,132]),o($V8,[2,18]),{48:[1,180]},o($Vx,[2,40]),o($V8,[2,35]),o([44,45],[2,30]),{16:$Vy,39:181,41:120},o($VF,[2,34]),o($VF,[2,44]),o($VF,[2,45]),o($VF,[2,46]),o($VF,[2,47]),o($VF,[2,48]),o($VF,[2,49]),o($VF,[2,50]),o($VF,[2,51]),o($VF,[2,52]),o($VF,[2,53]),o($VF,[2,54]),o($VF,[2,55]),o($VF,[2,56]),o($VF,[2,57]),o($VA,[2,76]),o($VA,[2,78]),o($VA,[2,79]),o($VB,[2,83]),o($VB,[2,84]),{87:[1,182]},o($VC,[2,94]),{5:[1,183],16:$VD,100:184,102:$VE},{102:[1,185]},o($Vw,[2,133]),o($Vw,[2,135]),o($Vp,$Vq,{77:88,78:89,80:90,83:92,84:93,88:94,89:95,96:97,97:98,98:99,76:186,36:$Vr,82:$Vs}),o($Vw,[2,131]),o($Vx,[2,39]),o($VF,[2,32]),o($VB,[2,85]),o($VH,[2,101]),o($VH,[2,102]),o($VH,[2,104]),o($Vw,[2,136])],
defaultActions: {20:[2,5],29:[2,28],30:[2,29],37:[2,4],42:[2,24],43:[2,25],116:[2,36],117:[2,37]},
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
     delete parser.yy.result.suggestColumns;
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

var completeSuggestColumns = function () {
   if (parser.yy.cursorFound &&
       typeof parser.yy.result.suggestColumns !== 'undefined') {
     var identifierChain = parser.yy.result.suggestColumns.identifierChain;
     delete parser.yy.result.suggestColumns.identifierChain;
     var tableReferences = parser.yy.latestTableReferences;

     // IdentifierChain contains a possibly started identifier or empty, example: a.b.c = ['a', 'b', 'c']
     if (identifierChain.length > 0) {
       var foundTable = tableReferences.filter(function (tableRef) {
         return identifierChain[0] === tableRef.alias || identifierChain[0] === tableRef.table;
       })
       if (foundTable.length === 1) {
         tableReferences = foundTable;
       }
     }

     if (tableReferences.length === 1) {
       parser.yy.result.suggestColumns.table = tableReferences[0].table;
       if (typeof tableReferences[0].database !== 'undefined') {
         parser.yy.result.suggestColumns.database = tableReferences[0].database;
       }
     } else if (tableReferences.length > 1) {
       // Table identifier is required for column completion
       delete parser.yy.result.suggestColumns;
       parser.yy.result.suggestIdentifiers = [];
       tableReferences.forEach(function (tableRef) {
         parser.yy.result.suggestIdentifiers.push((tableRef.alias || tableRef.table) + '.');
       });
     }
   }
}

var addTableReference = function (ref) {
  if (typeof parser.yy.latestTableReferences === 'undefined') {
    parser.yy.latestTableReferences = [];
  }
  parser.yy.latestTableReferences.push(ref);
}

var suggestNumbers = function (numbers) {
  parser.yy.result.suggestNumbers = numbers;
}

var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords;
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

var determineCase = function (text) {
  parser.yy.lowerCase = text.toLowerCase() === text;
};

var lexerModified = false;

/**
 * Main parser function
 */
parser.parseSql = function(beforeCursor, afterCursor, dialect) {

  // Hack to set the inital state of the lexer without first having to hit a token
  // has to be done as the first token found can be dependant on dialect
  if (!lexerModified && typeof dialect !== 'undefined') {
    var originalSetInput = parser.lexer.setInput;
    parser.lexer.setInput = function (input) {
      var lexer = originalSetInput.bind(parser.lexer)(input);
      lexer.begin(dialect)
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
case 5: return 81; 
break;
case 6: return 52; 
break;
case 7: return 53; 
break;
case 8: return 104; 
break;
case 9: return 58; 
break;
case 10: return 30; 
break;
case 11: return 57; 
break;
case 12: return 55; 
break;
case 13: return 54; 
break;
case 14: return 68; 
break;
case 15: return 103; 
break;
case 16: return 51; 
break;
case 17: return 22; 
break;
case 18: return 86; 
break;
case 19: return 115; 
break;
case 20: return 82; 
break;
case 21: return 118; 
break;
case 22: return 79; 
break;
case 23: return 106; 
break;
case 24: determineCase(yy_.yytext); return 63; 
break;
case 25: return 50; 
break;
case 26: return 56; 
break;
case 27: return 23; 
break;
case 28: return 60; 
break;
case 29: return 49; 
break;
case 30: determineCase(yy_.yytext); return 17; 
break;
case 31: return 59; 
break;
case 32: return 75; 
break;
case 33: return 61; 
break;
case 34: return 26; 
break;
case 35: return 62; 
break;
case 36: return 34; 
break;
case 37: this.begin('hdfs'); return 28; 
break;
case 38: return 24; 
break;
case 39: this.begin('hdfs'); return 44; 
break;
case 40: return 27; 
break;
case 41: return 35; 
break;
case 42: this.begin('hdfs'); return 29; 
break;
case 43: return 25; 
break;
case 44: this.begin('hdfs'); return 45; 
break;
case 45: return 108; 
break;
case 46: return 16; 
break;
case 47: parser.yy.cursorFound = true; return 4; 
break;
case 48: parser.yy.cursorFound = true; return 5; 
break;
case 49: return 46; 
break;
case 50: return 47; 
break;
case 51: this.popState(); return 48; 
break;
case 52: return 10; 
break;
case 53: return yy_.yytext; 
break;
case 54: return yy_.yytext; 
break;
case 55: return 10; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:AND\b)/i,/^(?:BIGINT\b)/i,/^(?:BOOLEAN\b)/i,/^(?:BY\b)/i,/^(?:CHAR\b)/i,/^(?:CREATE\b)/i,/^(?:DECIMAL\b)/i,/^(?:DOUBLE\b)/i,/^(?:FLOAT\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:INT\b)/i,/^(?:INTO\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:SELECT\b)/i,/^(?:SMALLINT\b)/i,/^(?:STRING\b)/i,/^(?:TABLE\b)/i,/^(?:TIMESTAMP\b)/i,/^(?:TINYINT\b)/i,/^(?:USE\b)/i,/^(?:VARCHAR\b)/i,/^(?:WHERE\b)/i,/^(?:BINARY\b)/i,/^(?:DATA\b)/i,/^(?:DATE\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:DATA\b)/i,/^(?:EXTERNAL\b)/i,/^(?:INPATH\b)/i,/^(?:LOAD\b)/i,/^(?:LOCATION\b)/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:\s+['])/i,/^(?:[^'|]+)/i,/^(?:['])/i,/^(?:$)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>])/i,/^(?:$)/i],
conditions: {"hdfs":{"rules":[47,48,49,50,51,52],"inclusive":false},"hive":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,45,46,53,54,55],"inclusive":true},"impala":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,40,41,42,43,44,45,46,53,54,55],"inclusive":true},"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,45,46,53,54,55],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});