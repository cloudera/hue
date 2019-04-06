# This demonstrates the effect of changing the column width
# when inserting a picture/image.

import xlwt
w = xlwt.Workbook()
ws = w.add_sheet('Image')

ws.write(0, 2, "chg wid: none")
ws.insert_bitmap('python.bmp', 2, 2)

ws.write(0, 4, "chg wid: after")
ws.insert_bitmap('python.bmp', 2, 4)
ws.col(4).width = 20 * 256

ws.write(0, 6, "chg wid: before")
ws.col(6).width = 20 * 256
ws.insert_bitmap('python.bmp', 2, 6)

ws.write(0, 8, "chg wid: after")
ws.insert_bitmap('python.bmp', 2, 8)
ws.col(5).width = 8 * 256

ws.write(0, 10, "chg wid: before")
ws.col(10).width = 8 * 256
ws.insert_bitmap('python.bmp', 2, 10)

w.save('image_chg_col_wid.xls')
