#!/usr/bin/env python
# -*- coding: ascii -*-
# portions Copyright (C) 2005 Kiseliov Roman

import xlwt

w = xlwt.Workbook()
sheets = [w.add_sheet('sheet ' + str(sheetx+1)) for sheetx in range(7)]
ws1, ws2, ws3, ws4, ws5, ws6, ws7 = sheets
for sheet in sheets:
    for i in range(0x100):
        sheet.write(i // 0x10, i % 0x10, i)

H = 1
V = 2
HF = H + 2
VF = V + 2

ws1.panes_frozen = True
ws1.horz_split_pos = H
ws1.horz_split_first_visible = HF

ws2.panes_frozen = True
ws2.vert_split_pos = V
ws2.vert_split_first_visible = VF

ws3.panes_frozen = True
ws3.horz_split_pos = H
ws3.vert_split_pos = V
ws3.horz_split_first_visible = HF
ws3.vert_split_first_visible = VF

H = 10
V = 12
HF = H + 2
VF = V + 2

ws4.panes_frozen = False
ws4.horz_split_pos = H * 12.75 # rows
ws4.horz_split_first_visible = HF

ws5.panes_frozen = False
ws5.vert_split_pos = V * 8.43 # rows
ws5.vert_split_first_visible = VF

ws6.panes_frozen = False
ws6.horz_split_pos = H * 12.75 # rows
ws6.horz_split_first_visible = HF
ws6.vert_split_pos = V * 8.43 # cols
ws6.vert_split_first_visible = VF

ws7.split_position_units_are_twips = True
ws7.panes_frozen = False
ws7.horz_split_pos = H * 250 + 240 # twips
ws7.horz_split_first_visible = HF
ws7.vert_split_pos = V * 955 + 410 # twips
ws7.vert_split_first_visible = VF

w.save('panes2.xls')

