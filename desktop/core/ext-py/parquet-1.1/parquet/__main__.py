"""parquet - tool for inspecting parquet files."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import argparse
import logging
import sys


def setup_logging(options=None):
    """Configure logging based on options."""
    level = logging.DEBUG if options is not None and options.debug \
        else logging.WARNING
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter('%(name)s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('parquet').setLevel(level)
    logging.getLogger('parquet').addHandler(console)


def main(argv=None):
    """Run parquet utility application."""
    argv = argv or sys.argv[1:]

    parser = argparse.ArgumentParser('parquet',
                                     description='Read parquet files')
    parser.add_argument('--metadata', action='store_true',
                        help='show metadata on file')
    parser.add_argument('--row-group-metadata', action='store_true',
                        help="show per row group metadata")
    parser.add_argument('--no-data', action='store_true',
                        help="don't dump any data from the file")
    parser.add_argument('--limit', action='store', type=int, default=-1,
                        help='max records to output')
    parser.add_argument('--col', action='append', type=str,
                        help='only include this column (can be '
                             'specified multiple times)')
    parser.add_argument('--no-headers', action='store_true',
                        help='skip headers in output (only applies if '
                             'format=csv)')
    parser.add_argument('--format', action='store', type=str, default='csv',
                        help='format for the output data. can be csv or json.')
    parser.add_argument('--debug', action='store_true',
                        help='log debug info to stderr')
    parser.add_argument('file',
                        help='path to the file to parse')

    args = parser.parse_args(argv)

    setup_logging(args)

    import parquet

    if args.metadata:
        parquet.dump_metadata(args.file, args.row_group_metadata)
    if not args.no_data:
        parquet.dump(args.file, args)

if __name__ == '__main__':
    main()
