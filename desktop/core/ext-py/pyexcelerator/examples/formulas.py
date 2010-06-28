#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman
__rev_id__ = """$Id: formulas.py,v 1.4 2005/10/26 07:44:24 rvk Exp $"""


from pyExcelerator import *
from pyExcelerator.Worksheet import *

w = Workbook()
ws = w.add_sheet('F')
ws.frmla_opts=NoCalcs

ws.write(0, 0, Formula("-(1+1)", None))
ws.write(1, 0, Formula("-(1+1)/(-2-2)", 3.14))
ws.write(2, 0, Formula("-(134.8780789+1)", ErrorCode("#NULL!"), CalcOnOpen))
ws.write(3, 0, Formula("-(134.8780789e-10+1)", ErrorCode("#NAME?")))
ws.write(4, 0, Formula("-1/(1+1)+9344", 12345))

ws.write(0, 1, Formula("-(1+1)", "this is 2", CalcOnOpen))
ws.write(1, 1, Formula("-(1+1)/(-2-2)", u"this is 0.5"))
ws.write(2, 1, Formula("-(134.8780789+1)", ""))
ws.write(3, 1, Formula("-(134.8780789e-10+1)"))
ws.write(4, 1, Formula("-1/(1+1)+9344"))

ws.write(0, 2, Formula("A1*B1"))
ws.write(1, 2, Formula("A2*B2"))
ws.write(2, 2, Formula("A3*B3"))
ws.write(3, 2, Formula("A4*B4*sin(pi()/4)"))
ws.write(4, 2, Formula("A5%*B5*pi()/1000"))

##############
## NOTE: parameters are separated by semicolon!!!
##############


ws.write(5, 2, Formula("C1+C2+C3+C4+C5/(C1+C2+C3+C4/(C1+C2+C3+C4/(C1+C2+C3+C4)+C5)+C5)-20.3e-2"))
ws.write(5, 3, Formula("C1^2"))
ws.write(6, 2, Formula("SUM(C1;C2;;;;;C3;;;C4)"))
ws.write(6, 3, Formula("SUM($A$1:$C$5)"))

ws.write(7, 0, Formula('"lkjljllkllkl"'))
ws.write(7, 1, Formula('"yuyiyiyiyi"'))
ws.write(7, 2, Formula('A8 & B8 & A8'))
ws.write(8, 2, Formula('now()'))

ws.write(10, 2, Formula('TRUE'))
ws.write(11, 2, Formula('FALSE'))
ws.write(12, 3, Formula('IF(A1>A2;3;"hkjhjkhk")'))

w.save('formulas.xls')
