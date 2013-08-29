import parquet
import sys
parquet.dump_metadata(sys.argv[1])
print("")
print("-"*80)
print("")
options = {}  # TODO(jcrobak)
parquet.dump(sys.argv[1], options)
