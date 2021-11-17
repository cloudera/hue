from xlwt import Workbook
from xlwt.BIFFRecords import PanesRecord
w = Workbook()

# do each of the 4 scenarios with each of the 4 possible
# active pane settings

for px,py in (
    (0,0),   # no split
    (0,10),  # horizontal split
    (10,0),  # vertical split
    (10,10), # both split
    ):
    
    for active in range(4):

        # 0 - logical bottom-right pane
        # 1 - logical top-right pane
        # 2 - logical bottom-left pane
        # 3 - logical top-left pane

        # only set valid values:
        if active not in PanesRecord.valid_active_pane.get(
            (int(px > 0),int(py > 0))
            ):
            continue

        sheet = w.add_sheet('px-%i py-%i active-%i' %(
                px,py,active
                ))

        for rx in range(20):
            for cx in range(20):
                sheet.write(rx,cx,'R%iC%i'%(rx,cx))

        sheet.panes_frozen = False
        sheet.vert_split_pos = px * 8.43
        sheet.horz_split_pos = py * 12.75
        sheet.active_pane = active

w.save('panes3.xls')

