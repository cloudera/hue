import parquet
import sys
parquet.dump_metadata(sys.argv[1])
parquet.dump(sys.argv[1])