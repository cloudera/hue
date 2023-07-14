#!/bin/sh
curl -O -G http://md.swamid.se/md/swamid-2.0.xml
python3 mdexport.py -t local -o swamid2.md swamid-2.0.xml
