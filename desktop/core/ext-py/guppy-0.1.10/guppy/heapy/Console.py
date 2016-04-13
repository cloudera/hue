#._cv_part guppy.heapy.Console

import code 

class Console(code.InteractiveConsole):
    EOF_key_sequence = '-'
    def __init__(self, stdin, stdout, locals=None, filename="<console>"):
	self.stdin = stdin
	self.stdout = stdout
	code.InteractiveConsole.__init__(self, locals, filename)

    def raw_input(self, prompt=""):
        """Write a prompt and read a line.

        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.

        """
	self.write(prompt)
	line = self.stdin.readline()
        if not line:
            raise EOFError
        line=line.rstrip()
	if line == self.EOF_key_sequence:
	    raise EOFError
	else:
	    return line


    def write(self, data):
	self.stdout.write(data)


