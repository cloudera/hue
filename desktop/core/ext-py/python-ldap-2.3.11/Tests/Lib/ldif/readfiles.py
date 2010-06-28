import sys,ldif

sum_records = 0

for pname in sys.argv[1:]:

#  ldif_parser = ldif.LDIFCopy(open(pname,'rb'),sys.stdout)
  ldif_parser = ldif.LDIFRecordList(open(pname,'rb'))
#  ldif_parser = ldif.LDIFParser(open(pname,'rb'))
  ldif_parser.parse()
  sys.stderr.write('%d records read from %s.\n' % (
    ldif_parser.records_read,pname)
  )
  sum_records = sum_records+ldif_parser.records_read

import pprint
pprint.pprint(ldif_parser.all_records)

assert len(ldif_parser.all_records)==sum_records,"Counted records differs from length of all parsed records."

sys.stderr.write('Total: %d records parsed.\n' % (sum_records))
