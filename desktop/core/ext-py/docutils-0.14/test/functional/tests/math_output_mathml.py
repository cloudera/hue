# Source and destination file names.
test_source = "data/math.txt"
test_destination = "math_output_mathml.xhtml"

# Keyword parameters passed to publish_file.
reader_name = "standalone"
parser_name = "rst"
writer_name = "html5"

# Settings
settings_overrides['math_output'] = 'MathML'
# local copy of default stylesheet:
# (test runs in ``docutils/test/``, we need relative path from there.)
settings_overrides['stylesheet_dirs'] = ('.','functional/input/data')
