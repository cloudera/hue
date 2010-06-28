#!/usr/bin/env python
# tries stress SST, SAT and MSAT
__rev_id__ = """$Id: big-16Mb.py,v 1.3 2005/03/27 12:47:06 rvk Exp $"""


from time import *
from pyExcelerator.Workbook import *
from pyExcelerator.Style import *

style = XFStyle()

wb = Workbook()
ws0 = wb.add_sheet('0')

colcount = 200 + 1
rowcount = 6000 + 1

t0 = time()
print "\nstart: %s" % ctime(t0)

print "Filling..."
for col in xrange(colcount):
    print "[%d]" % col, 
    for row in xrange(rowcount):
        #ws0.write(row, col, "BIG(%d, %d)" % (row, col))
        ws0.write(row, col, "BIG")

t1 = time() - t0
print "\nsince starting elapsed %.2f s" % (t1)

print "Storing..."
wb.save('big-16Mb.xls')

t2 = time() - t0
print "since starting elapsed %.2f s" % (t2)


