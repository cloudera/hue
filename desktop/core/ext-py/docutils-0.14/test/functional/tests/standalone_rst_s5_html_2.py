# initialize with the settings & definitions from test 1:
exec(open('functional/tests/standalone_rst_s5_html_1.py').read())

# overrides specific to this test:
test_destination = 'standalone_rst_s5_html_2.html'
del settings_overrides['theme']         # use the default
settings_overrides['current_slide'] = 1
