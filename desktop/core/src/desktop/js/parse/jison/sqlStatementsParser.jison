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

%lex
%options flex
%x multiLineComment inLineComment singleQuote doubleQuote backTick
%%

'/*'                                                                  { this.begin("multiLineComment"); return 'PART_OF_STATEMENT'; }
<multiLineComment>[^*]+                                               { return 'PART_OF_STATEMENT'; }
<multiLineComment>[*][^/]                                             { return 'PART_OF_STATEMENT'; }
<multiLineComment><<EOF>>                                             { this.popState(); return 'PART_OF_STATEMENT'; }
<multiLineComment>'*/'                                                { this.popState(); return 'PART_OF_STATEMENT'; }

'--'                                                                  { this.begin("inLineComment"); return 'PART_OF_STATEMENT'; }
<inLineComment>[^\n]+                                                 { return 'PART_OF_STATEMENT'; }
<inLineComment><<EOF>>                                                { this.popState(); return 'EOF'; }
<inLineComment>[\n]                                                   { this.popState(); return 'PART_OF_STATEMENT'; }

'"'                                                                   { this.begin("doubleQuote"); return 'PART_OF_STATEMENT'; }
<doubleQuote>(?:\\["]|[^"])+                                          { return 'PART_OF_STATEMENT'; }
<doubleQuote><<EOF>>                                                  { this.popState(); return 'EOF'; }
<doubleQuote>'"'                                                      { this.popState(); return 'PART_OF_STATEMENT'; }

'\''                                                                  { this.begin("singleQuote"); return 'PART_OF_STATEMENT'; }
<singleQuote>(?:\\[']|[^'])+                                          { return 'PART_OF_STATEMENT'; }
<singleQuote><<EOF>>                                                  { this.popState(); return 'EOF'; }
<singleQuote>'\''                                                     { this.popState(); return 'PART_OF_STATEMENT'; }

'`'                                                                   { this.begin("backTick"); return 'PART_OF_STATEMENT'; }
<backTick>[^`]+                                                       {
                                                                        if (parser.yy.usePreceding) {
                                                                          parser.yy.useDatabase = yytext;
                                                                          parser.yy.usePreceding = false;
                                                                        }
                                                                        return 'PART_OF_STATEMENT';
                                                                      }
<backTick><<EOF>>                                                     { this.popState(); return 'EOF'; }
<backTick>'`'                                                         { this.popState(); return 'PART_OF_STATEMENT'; }

[^"\/;'`-]+                                                           {
                                                                        if (!parser.yy.firstToken) {
                                                                          var firstWordMatch = yytext.match(/[a-zA-Z_]+/);
                                                                          if (firstWordMatch) {
                                                                            parser.yy.firstToken = firstWordMatch[0];
                                                                          }
                                                                          var useDatabaseMatch = yytext.match(/USE\s+(\S+)/i);
                                                                          if (useDatabaseMatch) {
                                                                            parser.yy.useDatabase = useDatabaseMatch[1];
                                                                          } else {
                                                                            // For backticked
                                                                            parser.yy.usePreceding = /USE/i.test(yytext);
                                                                          }
                                                                        } else if (parser.yy.usePreceding) {
                                                                          parser.yy.useDatabase = yytext;
                                                                          parser.yy.usePreceding = false;
                                                                        }
                                                                        return 'PART_OF_STATEMENT';
                                                                      }
[-][^;-]?                                                             { return 'PART_OF_STATEMENT'; }
[/][^;*]?                                                             { return 'PART_OF_STATEMENT'; }

';'                                                                   { return ';'; }

<<EOF>>                                                               { return 'EOF'; }

.                                                                     { /* To prevent console logging of unknown chars */ }
/lex

%start SqlStatementsParser

%%

SqlStatementsParser
 : Statements 'EOF'
   {
     parser.removeTrailingWhiteSpace($1);
     return $1;
   }
 | OneOrMoreSeparators Statements 'EOF'
   {
     parser.handleLeadingStatements($1, $2);
     parser.removeTrailingWhiteSpace($2);
     return $2;
   }
 | OneOrMoreSeparators Statements OneOrMoreSeparators 'EOF'
   {
     parser.handleLeadingStatements($1, $2);
     parser.handleTrailingStatements($2, $3);
     parser.removeTrailingWhiteSpace($2);
     return $2;
   }
 | Statements OneOrMoreSeparators 'EOF'
   {
     parser.handleTrailingStatements($1, $2);
     parser.removeTrailingWhiteSpace($1);
     return $1;
   }
 | OneOrMoreSeparators 'EOF'
   {
     var result = [];
     parser.handleLeadingStatements($1, result);
     return result;
   }
 | 'EOF'
   {
     var result = [];
     parser.addEntry(result, 'statement', $1, @1);
     return result;
   }
 ;

Statements
 : StatementParts
   {
     $$ = [];
     parser.addEntry($$, 'statement', $1, @1);
   }
 | Statements OneOrMoreSeparators StatementParts
   {
     parser.handleTrailingStatements($1, $2);
     parser.addEntry($1, 'statement', $3, @3);
   }
 ;

StatementParts
 : 'PART_OF_STATEMENT'
 | StatementParts 'PART_OF_STATEMENT'                              -> $1 + $2;
 ;

OneOrMoreSeparators
 : ';'                                                             -> [@1]
 | OneOrMoreSeparators ';'
   {
     $1.push(@2);
   }
 ;

%%

parser.addEntry = function (statements, type, statement, location) {
  if (parser.yy.firstToken) {
    if (parser.yy.useDatabase) {
      statements.push({ type: type, statement: statement, location: location, firstToken: parser.yy.firstToken, database: parser.yy.useDatabase });
      delete parser.yy.useDatabase;
    } else {
      statements.push({ type: type, statement: statement, location: location, firstToken: parser.yy.firstToken });
    }
    delete parser.yy.firstToken;
  } else {
    statements.push({ type: type, statement: statement, location: location });
  }
}

parser.handleLeadingStatements = function (emptyStatements, result) {
  for (var i = emptyStatements.length - 1; i >= 0; i--) {
    result.unshift({ type: 'statement', statement: ';', location: emptyStatements[i] });
  }
}

parser.handleTrailingStatements = function (result, emptyStatements) {
  var lastStatement = result[result.length - 1];
  lastStatement.statement += ';'
  lastStatement.location = {
    first_line: lastStatement.location.first_line,
    first_column: lastStatement.location.first_column,
    last_line: emptyStatements[0].last_line,
    last_column: emptyStatements[0].last_column
  }
  if (emptyStatements.length > 1) {
    for (var i = 1; i < emptyStatements.length; i++) {
      result.push({ type: 'statement', statement: ';', location: emptyStatements[i] });
    }
  }
}

parser.removeTrailingWhiteSpace = function (result) {
  if (result.length > 1) {
      var lastStatement = result[result.length - 1];
      if (/^\s+$/.test(lastStatement.statement)) {
        result.pop()
      }
  }
}
