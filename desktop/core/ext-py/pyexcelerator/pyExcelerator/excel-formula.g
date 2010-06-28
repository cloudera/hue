/*
 *  $Id: excel-formula.g,v 1.4 2005/08/14 06:40:23 rvk Exp $
 */

header {
    __rev_id__ = """$Id: excel-formula.g,v 1.4 2005/08/14 06:40:23 rvk Exp $"""

    import struct
    import Utils
    from UnicodeUtils import upack1
    from ExcelMagic import *
}

header "ExcelFormulaParser.__init__" {
    self.rpn = ""
}

options {
    language  = "Python";
}

class ExcelFormulaParser extends Parser;
options {
    k = 2;
    defaultErrorHandler = false;
    buildAST = false;
}


tokens {
    TRUE_CONST;
    FALSE_CONST;
    STR_CONST;
    NUM_CONST;
    INT_CONST;
    
    NAME;

    EQ;
    NE;
    GT;
    LT;
    GE;
    LE;

    ADD;
    SUB;
    MUL;
    DIV;

    POWER;
    PERCENT;

    LP;
    RP;

    LB;
    RB;

    COLON;
    COMMA;
    SEMICOLON;
}

formula
    : expr["V"]
    ;

expr[arg_type]
    : prec0_expr[arg_type]
        (
            (
                  EQ { op = struct.pack('B', ptgEQ) }
                | NE { op = struct.pack('B', ptgNE) }
                | GT { op = struct.pack('B', ptgGT) }
                | LT { op = struct.pack('B', ptgLT) }
                | GE { op = struct.pack('B', ptgGE) }
                | LE { op = struct.pack('B', ptgLE) }
            )
            prec0_expr[arg_type] { self.rpn += op }
        )*
    ;

prec0_expr[arg_type]
    : prec1_expr[arg_type]
        (
            (
                CONCAT { op = struct.pack('B', ptgConcat) }
            )
            prec1_expr[arg_type] { self.rpn += op }
        )*
    ;

prec1_expr[arg_type]
    : prec2_expr[arg_type]
        (
            (
                  ADD { op = struct.pack('B', ptgAdd) }
                | SUB { op = struct.pack('B', ptgSub) }
            )
            prec2_expr[arg_type] { self.rpn += op }
        )*
    ;


prec2_expr[arg_type]
    : prec3_expr[arg_type]
        (
            (
                  MUL { op = struct.pack('B', ptgMul) }
                | DIV { op = struct.pack('B', ptgDiv) }
            )
            prec3_expr[arg_type] { self.rpn += op }
        )*
    ;

prec3_expr[arg_type]
    : prec4_expr[arg_type]
        (
            (
                POWER { op = struct.pack('B', ptgPower) }
            )
            prec4_expr[arg_type] { self.rpn += op }
        )*
    ;

prec4_expr[arg_type]
    : prec5_expr[arg_type]
        (
            PERCENT { self.rpn += struct.pack('B', ptgPercent) }
        )?
    ;

prec5_expr[arg_type]
    : primary[arg_type]
    | SUB primary[arg_type] { self.rpn += struct.pack('B', ptgUminus) }
    ;

primary[arg_type]
    : TRUE_CONST
        {
            self.rpn += struct.pack("2B", ptgBool, 1)
        }
    | FALSE_CONST
        {
            self.rpn += struct.pack("2B", ptgBool, 0)
        }
    | str_tok:STR_CONST
        {
            self.rpn += struct.pack("B", ptgStr) + upack1(str_tok.text[1:-1])
        }
    | int_tok:INT_CONST
        {
            self.rpn += struct.pack("<BH", ptgInt, int(int_tok.text))
        }
    | num_tok:NUM_CONST
        {
            self.rpn += struct.pack("<Bd", ptgNum, float(num_tok.text))
        }
    | ref2d_tok:REF2D
        {
            r, c = Utils.cell_to_packed_rowcol(ref2d_tok.text)
            if arg_type == "R":
                self.rpn += struct.pack("<B2H", ptgRefR, r, c)
            else:
                self.rpn += struct.pack("<B2H", ptgRefV, r, c)
        }
    | ref2d1_tok:REF2D COLON ref2d2_tok:REF2D
        {
            r1, c1 = Utils.cell_to_packed_rowcol(ref2d1_tok.text)
            r2, c2 = Utils.cell_to_packed_rowcol(ref2d2_tok.text)
            if arg_type == "R":
                self.rpn += struct.pack("<B4H", ptgAreaR, r1, r2, c1, c2)
            else:
                self.rpn += struct.pack("<B4H", ptgAreaV, r1, r2, c1, c2)
        }
    | name_tok:NAME
        {
            self.rpn += ""
        }
    | func_tok:NAME
        {
            if func_tok.text.upper() in std_func_by_name:
                (opcode,
                min_argc,
                max_argc,
                func_type,
                arg_type_list,
                volatile_func) = std_func_by_name[func_tok.text.upper()]
            else:
                raise Exception, "unknown function: %s" % func_tok.text
        }
        LP arg_count = expr_list[arg_type_list, min_argc, max_argc] RP
        {
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
        }
    | LP expr[arg_type] RP
        {
            self.rpn += struct.pack("B", ptgParen)
        }
    ;

expr_list[arg_type_list, min_argc, max_argc] returns [arg_cnt]
{
    arg_cnt = 0
    arg_type_list = arg_type_list.split()
    arg_type = arg_type_list[arg_cnt]
}
    : expr[arg_type] { arg_cnt += 1 }
    (
        {
            if arg_cnt < len(arg_type_list):
                arg_type = arg_type_list[arg_cnt]
            else:
                arg_type = arg_type_list[-1]
            if arg_type == "...":
                arg_type = arg_type_list[-2]
        }
        SEMICOLON
            (
                  expr[arg_type]
                | { self.rpn += struct.pack("B", ptgMissArg) }
            )
            { arg_cnt += 1 }
    )*
    |
    ;

