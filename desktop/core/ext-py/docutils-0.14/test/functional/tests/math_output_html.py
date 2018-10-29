# Source and destination file names.
test_source = "data/math.txt"
test_destination = "math_output_html.html"

# Keyword parameters passed to publish_file.
reader_name = "standalone"
parser_name = "rst"
writer_name = "html"

# Extra settings
settings_overrides['math_output'] = 'HTML'
# stylesheets: 
settings_overrides['stylesheet_path'] = ( 
    'functional/input/data/html4css1.css,'
    'functional/input/data/math.css')

    
