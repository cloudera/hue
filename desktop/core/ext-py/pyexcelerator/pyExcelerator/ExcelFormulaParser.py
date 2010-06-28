### $ANTLR 2.7.5 (20050128): "excel-formula.g" -> "ExcelFormulaParser.py"$
### import antlr and other modules ..
import sys
import antlr

version = sys.version.split()[0]
if version < '2.2.1':
    False = 0
if version < '2.3':
    True = not False
### header action >>> 
__rev_id__ = """$Id: ExcelFormulaParser.py,v 1.4 2005/08/14 06:40:23 rvk Exp $"""

import struct
import Utils
from UnicodeUtils import upack1
from ExcelMagic import *
### header action <<< 
### preamble action>>>

### preamble action <<<

### import antlr.Token 
from antlr import Token
### >>>The Known Token Types <<<
SKIP                = antlr.SKIP
INVALID_TYPE        = antlr.INVALID_TYPE
EOF_TYPE            = antlr.EOF_TYPE
EOF                 = antlr.EOF
NULL_TREE_LOOKAHEAD = antlr.NULL_TREE_LOOKAHEAD
MIN_USER_TYPE       = antlr.MIN_USER_TYPE
TRUE_CONST = 4
FALSE_CONST = 5
STR_CONST = 6
NUM_CONST = 7
INT_CONST = 8
NAME = 9
EQ = 10
NE = 11
GT = 12
LT = 13
GE = 14
LE = 15
ADD = 16
SUB = 17
MUL = 18
DIV = 19
POWER = 20
PERCENT = 21
LP = 22
RP = 23
LB = 24
RB = 25
COLON = 26
COMMA = 27
SEMICOLON = 28
CONCAT = 29
REF2D = 30

class Parser(antlr.LLkParser):
    ### user action >>>
    ### user action <<<
    
    def __init__(self, *args, **kwargs):
        antlr.LLkParser.__init__(self, *args, **kwargs)
        self.tokenNames = _tokenNames
        ### __init__ header action >>> 
        self.rpn = ""
        ### __init__ header action <<< 
        
    def formula(self):    
        
        pass
        self.expr("V")
    
    def expr(self,
        arg_type
    ):    
        
        pass
        self.prec0_expr(arg_type)
        while True:
            if ((self.LA(1) >= EQ and self.LA(1) <= LE)):
                pass
                la1 = self.LA(1)
                if False:
                    pass
                elif la1 and la1 in [EQ]:
                    pass
                    self.match(EQ)
                    op = struct.pack('B', ptgEQ)
                elif la1 and la1 in [NE]:
                    pass
                    self.match(NE)
                    op = struct.pack('B', ptgNE)
                elif la1 and la1 in [GT]:
                    pass
                    self.match(GT)
                    op = struct.pack('B', ptgGT)
                elif la1 and la1 in [LT]:
                    pass
                    self.match(LT)
                    op = struct.pack('B', ptgLT)
                elif la1 and la1 in [GE]:
                    pass
                    self.match(GE)
                    op = struct.pack('B', ptgGE)
                elif la1 and la1 in [LE]:
                    pass
                    self.match(LE)
                    op = struct.pack('B', ptgLE)
                else:
                        raise antlr.NoViableAltException(self.LT(1), self.getFilename())
                    
                self.prec0_expr(arg_type)
                self.rpn += op
            else:
                break
            
    
    def prec0_expr(self,
        arg_type
    ):    
        
        pass
        self.prec1_expr(arg_type)
        while True:
            if (self.LA(1)==CONCAT):
                pass
                pass
                self.match(CONCAT)
                op = struct.pack('B', ptgConcat)
                self.prec1_expr(arg_type)
                self.rpn += op
            else:
                break
            
    
    def prec1_expr(self,
        arg_type
    ):    
        
        pass
        self.prec2_expr(arg_type)
        while True:
            if (self.LA(1)==ADD or self.LA(1)==SUB):
                pass
                la1 = self.LA(1)
                if False:
                    pass
                elif la1 and la1 in [ADD]:
                    pass
                    self.match(ADD)
                    op = struct.pack('B', ptgAdd)
                elif la1 and la1 in [SUB]:
                    pass
                    self.match(SUB)
                    op = struct.pack('B', ptgSub)
                else:
                        raise antlr.NoViableAltException(self.LT(1), self.getFilename())
                    
                self.prec2_expr(arg_type)
                self.rpn += op
            else:
                break
            
    
    def prec2_expr(self,
        arg_type
    ):    
        
        pass
        self.prec3_expr(arg_type)
        while True:
            if (self.LA(1)==MUL or self.LA(1)==DIV):
                pass
                la1 = self.LA(1)
                if False:
                    pass
                elif la1 and la1 in [MUL]:
                    pass
                    self.match(MUL)
                    op = struct.pack('B', ptgMul)
                elif la1 and la1 in [DIV]:
                    pass
                    self.match(DIV)
                    op = struct.pack('B', ptgDiv)
                else:
                        raise antlr.NoViableAltException(self.LT(1), self.getFilename())
                    
                self.prec3_expr(arg_type)
                self.rpn += op
            else:
                break
            
    
    def prec3_expr(self,
        arg_type
    ):    
        
        pass
        self.prec4_expr(arg_type)
        while True:
            if (self.LA(1)==POWER):
                pass
                pass
                self.match(POWER)
                op = struct.pack('B', ptgPower)
                self.prec4_expr(arg_type)
                self.rpn += op
            else:
                break
            
    
    def prec4_expr(self,
        arg_type
    ):    
        
        pass
        self.prec5_expr(arg_type)
        la1 = self.LA(1)
        if False:
            pass
        elif la1 and la1 in [PERCENT]:
            pass
            self.match(PERCENT)
            self.rpn += struct.pack('B', ptgPercent)
        elif la1 and la1 in [EOF,EQ,NE,GT,LT,GE,LE,ADD,SUB,MUL,DIV,POWER,RP,SEMICOLON,CONCAT]:
            pass
        else:
                raise antlr.NoViableAltException(self.LT(1), self.getFilename())
            
    
    def prec5_expr(self,
        arg_type
    ):    
        
        la1 = self.LA(1)
        if False:
            pass
        elif la1 and la1 in [TRUE_CONST,FALSE_CONST,STR_CONST,NUM_CONST,INT_CONST,NAME,LP,REF2D]:
            pass
            self.primary(arg_type)
        elif la1 and la1 in [SUB]:
            pass
            self.match(SUB)
            self.primary(arg_type)
            self.rpn += struct.pack('B', ptgUminus)
        else:
                raise antlr.NoViableAltException(self.LT(1), self.getFilename())
            
    
    def primary(self,
        arg_type
    ):    
        
        str_tok = None
        int_tok = None
        num_tok = None
        ref2d_tok = None
        ref2d1_tok = None
        ref2d2_tok = None
        name_tok = None
        func_tok = None
        la1 = self.LA(1)
        if False:
            pass
        elif la1 and la1 in [TRUE_CONST]:
            pass
            self.match(TRUE_CONST)
            self.rpn += struct.pack("2B", ptgBool, 1)
        elif la1 and la1 in [FALSE_CONST]:
            pass
            self.match(FALSE_CONST)
            self.rpn += struct.pack("2B", ptgBool, 0)
        elif la1 and la1 in [STR_CONST]:
            pass
            str_tok = self.LT(1)
            self.match(STR_CONST)
            self.rpn += struct.pack("B", ptgStr) + upack1(str_tok.text[1:-1])
        elif la1 and la1 in [INT_CONST]:
            pass
            int_tok = self.LT(1)
            self.match(INT_CONST)
            self.rpn += struct.pack("<BH", ptgInt, int(int_tok.text))
        elif la1 and la1 in [NUM_CONST]:
            pass
            num_tok = self.LT(1)
            self.match(NUM_CONST)
            self.rpn += struct.pack("<Bd", ptgNum, float(num_tok.text))
        elif la1 and la1 in [LP]:
            pass
            self.match(LP)
            self.expr(arg_type)
            self.match(RP)
            self.rpn += struct.pack("B", ptgParen)
        else:
            if (self.LA(1)==REF2D) and (_tokenSet_0.member(self.LA(2))):
                pass
                ref2d_tok = self.LT(1)
                self.match(REF2D)
                r, c = Utils.cell_to_packed_rowcol(ref2d_tok.text)
                if arg_type == "R":
                   self.rpn += struct.pack("<B2H", ptgRefR, r, c)
                else:
                   self.rpn += struct.pack("<B2H", ptgRefV, r, c)
            elif (self.LA(1)==REF2D) and (self.LA(2)==COLON):
                pass
                ref2d1_tok = self.LT(1)
                self.match(REF2D)
                self.match(COLON)
                ref2d2_tok = self.LT(1)
                self.match(REF2D)
                r1, c1 = Utils.cell_to_packed_rowcol(ref2d1_tok.text)
                r2, c2 = Utils.cell_to_packed_rowcol(ref2d2_tok.text)
                if arg_type == "R":
                   self.rpn += struct.pack("<B4H", ptgAreaR, r1, r2, c1, c2)
                else:
                   self.rpn += struct.pack("<B4H", ptgAreaV, r1, r2, c1, c2)
            elif (self.LA(1)==NAME) and (_tokenSet_0.member(self.LA(2))):
                pass
                name_tok = self.LT(1)
                self.match(NAME)
                self.rpn += ""
            elif (self.LA(1)==NAME) and (self.LA(2)==LP):
                pass
                func_tok = self.LT(1)
                self.match(NAME)
                if func_tok.text.upper() in std_func_by_name:
                   (opcode,
                   min_argc,
                   max_argc,
                   func_type,
                   arg_type_list,
                   volatile_func) = std_func_by_name[func_tok.text.upper()]
                else:
                   raise Exception, "unknown function: %s" % func_tok.text
                self.match(LP)
                arg_count=self.expr_list(arg_type_list, min_argc, max_argc)
                self.match(RP)
                if arg_count > max_argc or arg_count < min_argc:
                   raise Exception, "%d parameters for function: %s" % (arg_count, func_tok.text)
                if min_argc == max_argc:
                   if func_type == "V":
                       func_ptg = ptgFuncV
                   elif func_type == "R":
                       func_ptg = ptgFuncR
                   elif func_type == "A":
                       func_ptg = ptgFuncA
                   else:
                       raise Exception, "wrong function type"
                   self.rpn += struct.pack("<BH", func_ptg, opcode)
                else:
                   if func_type == "V":
                       func_ptg = ptgFuncVarV
                   elif func_type == "R":
                       func_ptg = ptgFuncVarR
                   elif func_type == "A":
                       func_ptg = ptgFuncVarA
                   else:
                       raise Exception, "wrong function type"
                   self.rpn += struct.pack("<2BH", func_ptg, arg_count, opcode)
            else:
                raise antlr.NoViableAltException(self.LT(1), self.getFilename())
            
    
    def expr_list(self,
        arg_type_list, min_argc, max_argc
    ):    
        arg_cnt = None
        
        arg_cnt = 0
        arg_type_list = arg_type_list.split()
        arg_type = arg_type_list[arg_cnt]
        la1 = self.LA(1)
        if False:
            pass
        elif la1 and la1 in [TRUE_CONST,FALSE_CONST,STR_CONST,NUM_CONST,INT_CONST,NAME,SUB,LP,REF2D]:
            pass
            self.expr(arg_type)
            arg_cnt += 1
            while True:
                if (self.LA(1)==SEMICOLON):
                    pass
                    if arg_cnt < len(arg_type_list):
                       arg_type = arg_type_list[arg_cnt]
                    else:
                       arg_type = arg_type_list[-1]
                    if arg_type == "...":
                       arg_type = arg_type_list[-2]
                    self.match(SEMICOLON)
                    la1 = self.LA(1)
                    if False:
                        pass
                    elif la1 and la1 in [TRUE_CONST,FALSE_CONST,STR_CONST,NUM_CONST,INT_CONST,NAME,SUB,LP,REF2D]:
                        pass
                        self.expr(arg_type)
                    elif la1 and la1 in [RP,SEMICOLON]:
                        pass
                        self.rpn += struct.pack("B", ptgMissArg)
                    else:
                            raise antlr.NoViableAltException(self.LT(1), self.getFilename())
                        
                    arg_cnt += 1
                else:
                    break
                
        elif la1 and la1 in [RP]:
            pass
        else:
                raise antlr.NoViableAltException(self.LT(1), self.getFilename())
            
        return arg_cnt
    

_tokenNames = [
    "<0>", 
    "EOF", 
    "<2>", 
    "NULL_TREE_LOOKAHEAD", 
    "TRUE_CONST", 
    "FALSE_CONST", 
    "STR_CONST", 
    "NUM_CONST", 
    "INT_CONST", 
    "NAME", 
    "EQ", 
    "NE", 
    "GT", 
    "LT", 
    "GE", 
    "LE", 
    "ADD", 
    "SUB", 
    "MUL", 
    "DIV", 
    "POWER", 
    "PERCENT", 
    "LP", 
    "RP", 
    "LB", 
    "RB", 
    "COLON", 
    "COMMA", 
    "SEMICOLON", 
    "CONCAT", 
    "REF2D"
]
    

### generate bit set
def mk_tokenSet_0(): 
    ### var1
    data = [ 817888258L, 0L]
    return data
_tokenSet_0 = antlr.BitSet(mk_tokenSet_0())
    
