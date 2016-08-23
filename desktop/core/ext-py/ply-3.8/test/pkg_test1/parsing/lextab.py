# lextab.py. This file automatically created by PLY (version 3.8). Don't edit!
_tabversion   = '3.8'
_lextokens    = set(['RPAREN', 'DIVIDE', 'NUMBER', 'TIMES', 'EQUALS', 'PLUS', 'LPAREN', 'MINUS', 'NAME'])
_lexreflags   = 0
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_NUMBER>\\d+)|(?P<t_newline>\\n+)|(?P<t_NAME>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<t_LPAREN>\\()|(?P<t_PLUS>\\+)|(?P<t_RPAREN>\\))|(?P<t_TIMES>\\*)|(?P<t_MINUS>-)|(?P<t_EQUALS>=)|(?P<t_DIVIDE>/)', [None, ('t_NUMBER', 'NUMBER'), ('t_newline', 'newline'), (None, 'NAME'), (None, 'LPAREN'), (None, 'PLUS'), (None, 'RPAREN'), (None, 'TIMES'), (None, 'MINUS'), (None, 'EQUALS'), (None, 'DIVIDE')])]}
_lexstateignore = {'INITIAL': ' \t'}
_lexstateerrorf = {'INITIAL': 't_error'}
_lexstateeoff = {}
