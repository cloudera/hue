#!/usr/bin/env python
# -*- coding: windows-1251 -*-
# Copyright (C) 2005 Kiseliov Roman

__rev_id__ = """$Id: xls2csv-gerry.py,v 1.1 2005/10/26 07:44:24 rvk Exp $"""

###--xls2csv.py
###--modified by gerry 10/5/2005
###--with args, processes just those files
###--with no args, processes all csvs in the current directory
###--args may include or exclude the .xls suffix
###--no files are written for empty sheets

from    pyExcelerator import *
import  re
import  os
import  sys

def process(fname):
    
    if fname[-4:] != ".xls": 
        fname = fname + ".xls"    
   
    print "processing", fname
    
    for sheet_name, values in parse_xls(fname, 'cp1251'): # parse_xls(arg) -- default encoding
        print "     starting", sheet_name,
        
        keys = values.keys()
        
        rows    = []
        cols    = []
        for key in keys:
            row, col = key
            if not col in cols: cols.append(col)
            if not row in rows: rows.append(row)
        
        try:    n_rows = max(rows)
        except:
            print "which is null." 
            continue
        n_cols = max(cols)
        print "which has", n_rows+1, "rows, and", n_cols+1, "columns."
        
        ofile = open(fname + "." + sheet_name + ".csv",     "w")
        
        for row in range(n_rows+1):
            line = ""
            for col in range(n_cols+1):
                try:    cell = str(values[(row, col)])
                except: cell = ""
                if commas.search(cell) != None: cell = '"' + cell + '"'
                line = line + cell + ","
            print >> ofile, line[:-1]
            
        ofile.close()
        
    print '----------------'

commas = re.compile(",")

try:    args = sys.argv[1:]
except: args = []

if len(args) < 1:
    fnames = os.listdir(".")
    fnames.sort()
    for fname in fnames:
        parts = fname.split(".")
        if parts[-1] != "xls": continue
        process(fname) 
    sys.exit()
else:
    for arg in args:
        process(arg)

    
    
    