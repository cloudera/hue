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

\s+                                             { return 'WS' }

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
 : OptionalWhitespace SearchParts OptionalWhitespace 'EOF'
   {
     return $2;
   }
 | OptionalWhitespace SearchParts_EDIT 'EOF'
   {
     if (!$2.facets) {
       $2.facets = {};
     }
     if (!$2.text) {
       $2.text = [];
     }
     return $2;
   }
 | OptionalWhitespace 'EOF'
   {
     return { facets: {}, text: [] };
   }
 ;

SearchParts
 : SearchPart
 | SearchParts WS SearchPart
   {
     parser.mergeFacets($1, $3);
     parser.mergeText($1, $3);
   }
 ;

SearchParts_EDIT
 : SearchPart_EDIT
 | SearchParts WS SearchPart_EDIT
   {
     parser.mergeFacets($1, $3);
     parser.mergeText($1, $3);
     $$ = $3;
     $$.text = $1.text;
     $$.facets = $1.facets;
   }
 | SearchPart_EDIT WS SearchParts
   {
     $$ = $1;
     parser.mergeFacets($$, $3);
     parser.mergeText($$, $3);
   }
 | SearchParts WS SearchPart_EDIT WS SearchParts
   {
     parser.mergeFacets($1, $3);
     parser.mergeFacets($1, $5);
     parser.mergeText($1, $3);
     parser.mergeText($1, $5);
     $$ = $3;
     $$.text = $1.text;
     $$.facets = $1.facets;
   }
 ;

SearchPart
 : Facet     --> { text: [], facets: $1.facets }
 | FreeText  --> { text: [$1], facets: {} }
 ;

SearchPart_EDIT
 : Facet_EDIT
 | FreeText_EDIT
 ;

Facet
 : 'FACET' OptionalWhitespace FreeText
   {
     var facet = {};
     var facetName = $1.substring(0, $1.length - 1).toLowerCase();
     facet[facetName] = {};
     facet[facetName][$3.toLowerCase()] = true;
     $$ = { facets: facet };
   }
 ;

Facet_EDIT
 : 'FACET' OptionalWhitespace 'CURSOR'           --> { suggestFacetValues: $1.substring(0, $1.length - 1).toLowerCase() }
 | 'FACET' OptionalWhitespace FreeText 'CURSOR'
   {
     var facet = {};
     var facetName = $1.substring(0, $1.length - 1).toLowerCase();
     facet[facetName] = {};
     facet[facetName][$3.toLowerCase()] = true;
     $$ = { suggestFacetValues: facetName, facets: facet }
   }
 ;

FreeText
 : 'TEXT'
 | QuotedValue
 ;

FreeText_EDIT
 : 'CURSOR'                --> { suggestFacets: true, suggestResults: true }
 | 'CURSOR' 'TEXT'         --> { suggestFacets: true, suggestResults: true, text: [$2] }
 | 'TEXT' 'CURSOR' 'TEXT'  --> { suggestFacets: true, suggestResults: true, text: [$1+$3] }
 | 'TEXT' 'CURSOR'         --> { suggestFacets: true, suggestResults: true, text: [$1] }
 | QuotedValue_EDIT
 ;

QuotedValue
 : 'QUOTE' 'VALUE' 'QUOTE'  --> $2
 | 'QUOTE' 'QUOTE'          --> ''
 ;

QuotedValue_EDIT
 : 'QUOTE' 'PARTIAL_VALUE'  --> $2
 ;

OptionalWhitespace
 :
 | WS
 ;

%%

SqlParseSupport.initGlobalSearchParser(parser);