#._cv_part genguppydoc.py

import guppy,os
from os.path import join

class GenGuppyDoc:
    extemplate = """\
.document: gslexample
..output: html
..h1: GSL Document and Test Example
..ul
...li
....a: Source Code
.....href= #source
...li
....a: Generated Test Class
.....href= #test
...li
....a: Generated Document
.....href= docexample.html
..a
...name=source
...h2: Source Code
..pre
%s
..c: end pre
..a
...name=test
...h2: Generated Test Class
..pre
%s
..c: end pre
    """


    def __init__(self, input_dir=None, output_dir=None):
        if input_dir is None:
            # Default to current directory
            input_dir = os.getcwd()
        if output_dir is None:
            output_dir = join(input_dir, '..','guppy','doc')
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.gsl = guppy.Root().guppy.gsl

    def gen(self, gslfile, **kwds):
        self.gsl.Main.main(gslfile, input_dir=self.input_dir,
                           output_dir=self.output_dir, **kwds)

    def genext(self):
        self.gen('genext.gsl')

    def genguppy(self):
        self.gen('genguppy.gsl')

    def gengsl(self):
	self.gen('index.gsl')
	self.gen('heapy_tutorial.gsl')

	self.gen('gsl.gsl')
	self.gen('docexample.gsl')
	gslexample = self.extemplate % (
	    ('\n'+open(join(self.input_dir, 'docexample.gsl')).read()).replace('\n.','\n\\.'),
	    open(join(self.output_dir, 'docexample.py')).read())
		    
	self.gen('gslexample.gsl',input_string=gslexample)


		 
def main():
    g=GenGuppyDoc()
    g.genext()
    g.genguppy()
    g.gengsl()

if __name__=='__main__':
    main()
