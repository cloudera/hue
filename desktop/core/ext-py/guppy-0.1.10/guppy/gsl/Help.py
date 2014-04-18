#._cv_part guppy.gsl.Help

class _GLUECLAMP_:
    _imports_ = (
	'_root:os',
	'_root.guppy:specs',
	'_root:webbrowser',
	)
    
    default_doc_file = 'guppy.html'

    def _get_doc_dir(self):
	os = self.os
	return os.path.join(os.path.abspath(self.os.path.dirname(self.specs.__file__)),
			    'generated')

    def doc(self, subject=None, *args, **kwds):
	"""\
	This doesnt work well or at all
	There are painful were where-to-find the files issues
	for the distributed and installed package.
	for I couldn't have the data among the modules themselves.

    Get documentation about a subject or generally about the Guppy system.
    It will show the documentation in the system web browser.
    If the subject argument is an object that the documentation system
    recognizes, it will bring up the documentation for that kind of object.
    Otherwise it will bring up a general documentation page.
    """

	self.doc_default()

    def doc_default(self):
	self.open_local_filename(self.default_doc_file)

    def open_local_filename(self, filename):
	self.webbrowser.open(self.os.path.join(self.doc_dir, filename))
