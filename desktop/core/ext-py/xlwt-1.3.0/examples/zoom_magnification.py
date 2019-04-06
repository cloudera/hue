import xlwt
book = xlwt.Workbook()
for magn in (0, 60, 100, 75, 150):
    for preview in (False, True):
        sheet = book.add_sheet('magn%d%s' % (magn, "np"[preview]))
        if preview:
            sheet.preview_magn = magn
        else:
            sheet.normal_magn = magn
        sheet.page_preview = preview
        for rowx in range(100):
            sheet.write(rowx, 0, "Some text")
book.save("zoom_magnification.xls")

