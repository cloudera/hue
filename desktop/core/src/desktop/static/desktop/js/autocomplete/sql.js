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
var o=function(k,v,o,l){for(o=o||{},l=k.length;l--;o[k[l]]=v);return o},$V0=[1,11],$V1=[1,12],$V2=[1,7],$V3=[1,9],$V4=[1,10],$V5=[9,10],$V6=[1,23],$V7=[1,22],$V8=[4,5,9,10,14,21,28,32,34,39,43,44,45,46,47,48,50,58,61,62,66,71,74],$V9=[9,10,21],$Va=[1,31],$Vb=[4,9,10,21,28,58,61,62,66],$Vc=[1,43],$Vd=[1,44],$Ve=[1,45],$Vf=[1,46],$Vg=[1,47],$Vh=[1,54],$Vi=[4,9,10,28,58,61,62],$Vj=[14,57],$Vk=[2,57],$Vl=[1,66],$Vm=[1,71],$Vn=[4,5,9,10,28,58,61,62],$Vo=[4,5,9,10,28,58,61,62,66],$Vp=[1,82],$Vq=[4,5,9,10,28,58,61,62,66,71,74],$Vr=[1,85],$Vs=[4,5,9,10,28,32,50,58,61,62,66,71,74],$Vt=[4,5,9,10,28,32,34,50,58,61,62,66,71,74],$Vu=[4,5,9,10,28,32,34,39,43,44,45,46,47,48,50,58,61,62,66,71,74],$Vv=[1,100],$Vw=[1,101],$Vx=[14,49,57],$Vy=[4,5,9,10,28,32,34,39,43,44,45,46,47,48,50,56,58,61,62,66,71,74];
var parser = {trace: function trace() { },
yy: {},
symbols_: {"error":2,"AnyCursor":3,"CURSOR":4,"PARTIAL_CURSOR":5,"InitResults":6,"Sql":7,"SqlStatements":8,";":9,"EOF":10,"SqlStatement":11,"UseStatement":12,"QueryExpression":13,"REGULAR_IDENTIFIER":14,"USE":15,"SELECT":16,"SelectList":17,"TableExpression":18,"FromClause":19,"SelectConditionList":20,"FROM":21,"TableReferenceList":22,"SelectCondition":23,"WhereClause":24,"GroupByClause":25,"OrderByClause":26,"LimitClause":27,"WHERE":28,"SearchCondition":29,"BooleanValueExpression":30,"BooleanTerm":31,"OR":32,"BooleanFactor":33,"AND":34,"NOT":35,"BooleanTest":36,"Predicate":37,"CompOp":38,"IS":39,"TruthValue":40,"ParenthesizedBooleanValueExpression":41,"NonParenthesizedValueExpressionPrimary":42,"=":43,"<>":44,"<":45,">":46,"<=":47,">=":48,"(":49,")":50,"ColumnReference":51,"BasicIdentifierChain":52,"InitIdentifierChain":53,"IdentifierChain":54,"Identifier":55,".":56,"\"":57,"GROUP":58,"BY":59,"ColumnList":60,"ORDER":61,"LIMIT":62,"UNSIGNED_INTEGER":63,"*":64,"DerivedColumn":65,",":66,"TableReference":67,"TablePrimaryOrJoinedTable":68,"TablePrimary":69,"JoinedTable":70,"JOIN":71,"JoinSpecification":72,"JoinCondition":73,"ON":74,"$accept":0,"$end":1},
terminals_: {2:"error",4:"CURSOR",5:"PARTIAL_CURSOR",9:";",10:"EOF",14:"REGULAR_IDENTIFIER",15:"USE",16:"SELECT",21:"FROM",28:"WHERE",32:"OR",34:"AND",35:"NOT",39:"IS",40:"TruthValue",43:"=",44:"<>",45:"<",46:">",47:"<=",48:">=",49:"(",50:")",56:".",57:"\"",58:"GROUP",59:"BY",61:"ORDER",62:"LIMIT",63:"UNSIGNED_INTEGER",64:"*",66:",",71:"JOIN",74:"ON"},
productions_: [0,[3,1],[3,1],[6,0],[7,4],[7,3],[8,1],[8,3],[11,1],[11,1],[11,3],[11,2],[11,1],[12,3],[12,2],[12,2],[13,3],[13,2],[18,1],[18,2],[18,2],[19,2],[19,2],[20,1],[20,2],[23,1],[23,1],[23,1],[23,1],[23,1],[24,2],[24,2],[29,1],[30,1],[30,3],[31,1],[31,3],[31,3],[33,2],[33,1],[36,1],[36,3],[36,3],[36,4],[37,1],[37,1],[38,1],[38,1],[38,1],[38,1],[38,1],[38,1],[41,3],[41,2],[42,1],[51,1],[52,2],[53,0],[54,1],[54,3],[54,3],[55,1],[55,3],[25,3],[25,2],[26,3],[26,2],[27,2],[27,2],[17,1],[17,3],[17,2],[17,1],[60,1],[60,3],[65,3],[65,3],[65,3],[65,2],[65,1],[65,1],[22,1],[22,3],[67,1],[68,1],[68,1],[69,1],[69,2],[69,3],[69,4],[69,3],[70,4],[70,3],[72,1],[73,2]],
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
case 11: case 12:

     suggestKeywords(['SELECT', 'USE']);
   
break;
case 13: case 15:

     suggestDatabases();
   
break;
case 14:

     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $$[$0];
     }
   
break;
case 16:

     completeSuggestColumns();
   
break;
case 19: case 22:

     suggestTables();
     suggestDatabases({ appendDot: true });
   
break;
case 26: case 27: case 28:

     delete parser.yy.result.suggestStar;
   
break;
case 29:

     suggestKeywords(['WHERE', 'GROUP BY', 'LIMIT']);
   
break;
case 31:

     suggestColumns();
   
break;
case 36:

     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   
break;
case 53:

     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   
break;
case 56:

     delete parser.yy.identifierChain;
   
break;
case 57:

     parser.yy.identifierChain = [];
   
break;
case 59:

     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   
break;
case 61:

     parser.yy.identifierChain.push($$[$0]);
   
break;
case 62:

     parser.yy.identifierChain.push($$[$0-1]);
   
break;
case 64: case 66:

     suggestKeywords(['BY']);
   
break;
case 68:

     suggestNumbers([5, 10, 15]);
   
break;
case 70: case 71:

     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   
break;
case 77:

     parser.yy.result.suggestStar = true;
     suggestColumns({
       identifierChain: [ $$[$0-2] ]
     });
   
break;
case 78:

     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 80:

     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   
break;
case 86:

     addTableReference({ table: $$[$0] });
   
break;
case 87:

     addTableReference({ table: $$[$0-1], alias: $$[$0] });
   
break;
case 88:

     addTableReference({ database: $$[$0-2], table: $$[$0] });
   
break;
case 89:

     addTableReference({ database: $$[$0-3], table: $$[$0-1], alias: $$[$0] });
   
break;
case 90:

     suggestTables({ database: $$[$0-2] });
   
break;
case 92:

     suggestTables({});
     suggestDatabases({ appendDot: true });
   
break;
}
},
table: [o([4,5,14,15,16],[2,3],{7:1,6:2}),{1:[3]},{3:8,4:$V0,5:$V1,8:3,11:4,12:5,13:6,14:$V2,15:$V3,16:$V4},{9:[1,13],10:[1,14]},o($V5,[2,6]),o($V5,[2,8]),o($V5,[2,9]),{3:15,4:$V0,5:$V1},o($V5,[2,12]),{3:17,4:$V0,5:$V1,14:[1,16]},{4:$V6,14:$V7,17:18,60:19,64:[1,20],65:21},o($V8,[2,1]),o($V8,[2,2]),{3:8,4:$V0,5:$V1,10:[1,24],11:25,12:5,13:6,14:$V2,15:$V3,16:$V4},{1:[2,5]},o($V5,[2,11],{14:[1,26]}),o($V5,[2,14],{3:27,4:$V0,5:$V1}),o($V5,[2,15]),o($V5,[2,17],{18:28,19:29,21:[1,30]}),o($V9,[2,69],{66:$Va}),o($V9,[2,72],{4:[1,33],14:[1,32]}),o($Vb,[2,73]),o($Vb,[2,79],{5:[1,35],56:[1,34]}),o($Vb,[2,80]),{1:[2,4]},o($V5,[2,7]),o($V5,[2,10]),o($V5,[2,13]),o($V5,[2,16]),o($V5,[2,18],{20:37,23:38,24:39,25:40,26:41,27:42,4:$Vc,5:[1,36],28:$Vd,58:$Ve,61:$Vf,62:$Vg}),{3:49,4:$V0,5:$V1,14:$Vh,22:48,67:50,68:51,69:52,70:53},{4:$V6,14:$V7,65:55},{5:[1,56]},o($V9,[2,71]),{3:59,4:$V0,5:$V1,14:[1,57],64:[1,58]},o($Vb,[2,78]),o($V5,[2,19]),o($V5,[2,20],{24:39,25:40,26:41,27:42,23:60,4:$Vc,28:$Vd,58:$Ve,61:$Vf,62:$Vg}),o($Vi,[2,23]),o($Vi,[2,25]),o($Vi,[2,26]),o($Vi,[2,27]),o($Vi,[2,28]),o($Vi,[2,29]),o($Vj,$Vk,{29:61,30:63,31:64,33:65,36:67,37:68,41:69,42:70,51:72,52:73,53:74,4:[1,62],35:$Vl,49:$Vm}),{4:[1,76],59:[1,75]},{4:[1,78],59:[1,77]},{4:[1,80],63:[1,79]},o($Vn,[2,21],{66:[1,81]}),o($Vn,[2,22]),o($Vo,[2,81],{71:$Vp}),o($Vq,[2,83]),o($Vq,[2,84]),o($Vq,[2,85]),o($Vq,[2,86],{14:[1,83],56:[1,84]}),o($Vb,[2,74]),o($V9,[2,70]),o($Vb,[2,75]),o($Vb,[2,76]),o($Vb,[2,77]),o($Vi,[2,24]),o($Vi,[2,30]),o($Vi,[2,31]),o($Vq,[2,32],{32:$Vr}),o($Vs,[2,33]),o($Vs,[2,35],{34:[1,86]}),o($Vj,$Vk,{37:68,41:69,42:70,51:72,52:73,53:74,36:87,49:$Vm}),o($Vt,[2,39]),o($Vt,[2,40],{38:88,39:[1,89],43:[1,90],44:[1,91],45:[1,92],46:[1,93],47:[1,94],48:[1,95]}),o($Vu,[2,44]),o($Vu,[2,45]),o($Vj,$Vk,{31:64,33:65,36:67,37:68,41:69,42:70,51:72,52:73,53:74,30:96,3:97,4:$V0,5:$V1,35:$Vl,49:$Vm}),o($Vu,[2,54]),o($Vu,[2,55]),{14:$Vv,54:98,55:99,57:$Vw},{4:$V6,14:$V7,60:102,65:21},o($Vi,[2,64]),{4:$V6,14:$V7,60:103,65:21},o($Vi,[2,66]),o($Vi,[2,67]),o($Vi,[2,68]),{14:$Vh,67:104,68:51,69:52,70:53},{3:106,4:$V0,5:$V1,14:$Vh,67:105,68:51,69:52,70:53},o($Vq,[2,87]),{3:108,4:$V0,5:$V1,14:[1,107]},o($Vj,$Vk,{33:65,36:67,37:68,41:69,42:70,51:72,52:73,53:74,31:109,35:$Vl,49:$Vm}),o($Vj,$Vk,{33:65,36:67,37:68,41:69,42:70,51:72,52:73,53:74,31:111,4:[1,110],35:$Vl,49:$Vm}),o($Vt,[2,38]),o($Vj,$Vk,{41:69,42:70,51:72,52:73,53:74,37:112,49:$Vm}),{35:[1,114],40:[1,113]},o($Vx,[2,46]),o($Vx,[2,47]),o($Vx,[2,48]),o($Vx,[2,49]),o($Vx,[2,50]),o($Vx,[2,51]),{32:$Vr,50:[1,115]},o($Vu,[2,53]),o($Vu,[2,56],{56:[1,116]}),o($Vy,[2,58]),o($Vy,[2,61]),{14:[1,117]},o($Vi,[2,63],{66:$Va}),o($Vi,[2,65],{66:$Va}),o($Vo,[2,82],{71:$Vp}),{71:$Vp,72:118,73:119,74:[1,120]},o($Vq,[2,92]),o($Vq,[2,88],{14:[1,121]}),o($Vq,[2,90]),o($Vs,[2,34]),o($Vs,[2,36]),o($Vs,[2,37]),o($Vt,[2,41]),o($Vt,[2,42]),{40:[1,122]},o($Vu,[2,52]),{5:[1,123],14:$Vv,55:124,57:$Vw},{57:[1,125]},o($Vq,[2,91]),o($Vq,[2,93]),o($Vj,$Vk,{30:63,31:64,33:65,36:67,37:68,41:69,42:70,51:72,52:73,53:74,29:126,35:$Vl,49:$Vm}),o($Vq,[2,89]),o($Vt,[2,43]),o($Vy,[2,59]),o($Vy,[2,60]),o($Vy,[2,62]),o($Vq,[2,94])],
defaultActions: {14:[2,5],24:[2,4]},
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

var determineCase = function (text) {
  parser.yy.lowerCase = text.toLowerCase() === text;
};

/**
 * Main parser function
 */
parser.parseSql = function(beforeCursor, afterCursor, dialect) {
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
case 5: return 34; 
break;
case 6: return 59; 
break;
case 7: return 21; 
break;
case 8: return 58; 
break;
case 9: return 39; 
break;
case 10: return 71; 
break;
case 11: return 35; 
break;
case 12: return 74; 
break;
case 13: return 32; 
break;
case 14: return 61; 
break;
case 15: determineCase(yy_.yytext); return 16; 
break;
case 16: determineCase(yy_.yytext); return 15; 
break;
case 17: return 28; 
break;
case 18: return 63; 
break;
case 19: return 14; 
break;
case 20: return yy_.yytext; 
break;
case 21: return yy_.yytext; 
break;
case 22: return 10; 
break;
}
},
rules: [/^(?:[ \t\n])/i,/^(?:--.*)/i,/^(?:[\/][*][^*]*[*]+([^\/*][^*]*[*]+)*[\/])/i,/^(?:\|CURSOR\|)/i,/^(?:\|PARTIAL_CURSOR\|)/i,/^(?:AND\b)/i,/^(?:BY\b)/i,/^(?:FROM\b)/i,/^(?:GROUP\b)/i,/^(?:IS\b)/i,/^(?:JOIN\b)/i,/^(?:NOT\b)/i,/^(?:ON\b)/i,/^(?:OR\b)/i,/^(?:ORDER\b)/i,/^(?:SELECT\b)/i,/^(?:USE\b)/i,/^(?:WHERE\b)/i,/^(?:[0-9]+)/i,/^(?:[A-Za-z][A-Za-z0-9_]*)/i,/^(?:[-+&~|^\/%*(),.;!])/i,/^(?:[=<>])/i,/^(?:$)/i],
conditions: {"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],"inclusive":true}}
});
return lexer;
})();
parser.lexer = lexer;
return parser;
});