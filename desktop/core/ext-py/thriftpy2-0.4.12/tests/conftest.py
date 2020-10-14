import sys

collect_ignore = ["setup.py"]
if sys.version_info < (3, 5):
    collect_ignore.append("test_aio.py")
