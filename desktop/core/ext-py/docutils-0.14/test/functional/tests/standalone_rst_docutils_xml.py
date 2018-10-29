exec(open('functional/tests/_standalone_rst_defaults.py').read())

# Source and destination file names.
test_source = "standalone_rst_docutils_xml.txt"
test_destination = "standalone_rst_docutils_xml.xml"

# Keyword parameters passed to publish_file.
writer_name = "docutils_xml"

# Settings
# enable INFO-level system messages in this test:
settings_overrides['report_level'] = 1

# format output with indents and newlines
settings_overrides['indents'] = True
