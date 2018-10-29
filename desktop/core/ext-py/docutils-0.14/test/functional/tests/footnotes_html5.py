exec(open('functional/tests/_standalone_rst_defaults.py').read())

# Source and destination file names.
test_source = "footnotes.txt"
test_destination = "footnotes_html5.html"

# Keyword parameters passed to publish_file.
writer_name = "html5"

# Settings:
settings_overrides['footnote_references']='superscript'
# local copy of stylesheets:
# (Test runs in ``docutils/test/``, we need relative path from there.)
settings_overrides['stylesheet_dirs'] = ('.', 'functional/input/data')
