#!/usr/bin/env python

"""Script that makes determining PATTERN for a new [2to3] fix much easier.

Figuring out exactly what PATTERN I want for a given fixer class is
getting tedious. This script will step through each possible subtree
for a given string, allowing you to select which one you want. It will
then try to figure out an appropriate pattern to match that tree. This
pattern will require some editing (it will be overly restrictive) but
should provide a solid base to work with and handle the tricky parts.

Usage:

    python find_pattern.py "g.throw(E, V, T)"

This will step through each subtree in the parse. To reject a
candidate subtree, hit enter; to accept a candidate, hit "y" and
enter. The pattern will be spit out to stdout.

For example, the above will yield a succession of possible snippets,
skipping all leaf-only trees. I accept

'g.throw(E, V, T)'

This causes find_pattern to spit out

power< 'g' trailer< '.' 'throw' >
           trailer< '(' arglist< 'E' ',' 'V' ',' 'T' > ')' > >


Some minor tweaks later, I'm left with

power< any trailer< '.' 'throw' >
       trailer< '(' args=arglist< exc=any ',' val=any [',' tb=any] > ')' > >

which is exactly what I was after.

Larger snippets can be placed in a file (as opposed to a command-line
arg) and processed with the -f option.
"""

__author__ = "Collin Winter <collinw@gmail.com>"

# Python imports
import optparse
import sys
from StringIO import StringIO

# Local imports
from lib2to3 import pytree
from lib2to3.pgen2 import driver
from lib2to3.pygram import python_symbols, python_grammar

driver = driver.Driver(python_grammar, convert=pytree.convert)

def main(args):
    parser = optparse.OptionParser(usage="find_pattern.py [options] [string]")
    parser.add_option("-f", "--file", action="store",
                      help="Read a code snippet from the specified file")

    # Parse command line arguments
    options, args = parser.parse_args(args)
    if options.file:
        tree = driver.parse_file(options.file)
    elif len(args) > 1:
        tree = driver.parse_stream(StringIO(args[1] + "\n"))
    else:
        print >>sys.stderr, "You must specify an input file or an input string"
        return 1

    examine_tree(tree)
    return 0

def examine_tree(tree):
    for node in tree.post_order():
        if isinstance(node, pytree.Leaf):
            continue
        print repr(str(node))
        verdict = raw_input()
        if verdict.strip():
            print find_pattern(node)
            return

def find_pattern(node):
    if isinstance(node, pytree.Leaf):
        return repr(node.value)

    return find_symbol(node.type) + \
           "< " + " ".join(find_pattern(n) for n in node.children) + " >"

def find_symbol(sym):
    for n, v in python_symbols.__dict__.items():
        if v == sym:
            return n

if __name__ == "__main__":
    sys.exit(main(sys.argv))
