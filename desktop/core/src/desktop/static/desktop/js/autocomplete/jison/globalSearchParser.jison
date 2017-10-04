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
%x singleQuote doubleQuote
%%

\s                                              { /* skip whitespace */ }

'\u2020'                                        { parser.yy.cursorFound = yylloc; return 'CURSOR'; }

[a-zA-Z]+[:]                                    { return 'FACET' }

\'                                              { this.begin('singleQuote'); return 'QUOTE'; }

<singleQuote>(?:\\[']|[^'])+                    {
                                                  if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '\'')) {
                                                    return 'PARTIAL_VALUE';
                                                  }
                                                  return 'VALUE';
                                                }

<singleQuote>\'                                 { this.popState(); return 'QUOTE'; }

\"                                              { this.begin('doubleQuote'); return 'QUOTE'; }

<doubleQuote>(?:\\["]|[^"])+                    {
                                                  if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '"')) {
                                                    return 'PARTIAL_VALUE';
                                                  }
                                                  return 'VALUE';
                                                }

<doubleQuote>\"                                 { this.popState(); return 'QUOTE'; }

[^"'\s\u2020]+                                  { return 'TEXT'; }

<<EOF>>                                         { return 'EOF'; }

/lex

%start GlobalSearchAutocomplete

%%

GlobalSearchAutocomplete
 : SearchParts 'EOF'
   {
     return $1;
   }
 | SearchParts_EDIT 'EOF'
   {
     if (!$1.facets) {
       $1.facets = {};
     }
     if (!$1.text) {
       $1.text = [];
     }
     return $1;
   }
 | 'EOF'
   {
     return { facets: {}, text: [] };
   }
 ;

SearchParts
 : SearchPart
   {
     $$ = {
       facets: $1.facets ? $1.facets : {},
       text: $1.text ? $1.text : []
     };
   }
 | SearchParts SearchPart
   {
     $$ = {
       facets: $1.facets ? $1.facets : {},
       text: $1.text ? $1.text : []
     };
     if ($2.facets) {
       parser.mergeFacets($$.facets, $2.facets);
     }
     if ($2.text && $2.text.length) {
       $$.text = $$.text.concat($2.text);
     }
   }
 ;

SearchParts_EDIT
 : SearchPart_EDIT
 | SearchParts SearchPart_EDIT
   {
     $$ = $2;
     $$.facets = $1.facets;
     $$.text = $1.text;
   }
 | SearchPart_EDIT SearchParts
   {
     $$ = $1;
     $$.facets = $2.facets;
     $$.text = $2.text;
   }
 | SearchParts SearchPart_EDIT SearchParts
   {
     $$ = $2;
     $$.facets = $1.facets;
     $$.text = $1.text;
     parser.mergeFacets($$.facets, $3.facets);
     $$.text = $$.text.concat($3.text);
   }
 ;

SearchPart
 : Facet
 | FreeText  --> { text: [ $1 ] }
 ;

SearchPart_EDIT
 : Facet_EDIT
 | FreeText_EDIT
 ;

Facet
 : 'FACET' FreeText
   {
     var facet = {};
     facet[$1.substring(0, $1.length - 1)] = [ $2 ];
     $$ = { facets: facet };
   }
 ;

Facet_EDIT
 : 'FACET' 'CURSOR'     --> { suggestFacetValues: $1.substring(0, $1.length - 1) }
 ;

FreeText
 : 'TEXT'
 | QuotedValue
 ;

FreeText_EDIT
 : 'CURSOR'             --> { suggestFacets: true, suggestResults: true }
 | QuotedValue_EDIT
 ;

QuotedValue
 : 'QUOTE' 'VALUE' 'QUOTE'  --> $2
 | 'QUOTE' 'QUOTE'          --> ''
 ;

QuotedValue_EDIT
 : 'QUOTE' 'PARTIAL_VALUE'  --> $2
 ;

%%

SqlParseSupport.initGlobalSearchParser(parser);