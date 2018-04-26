#! /usr/bin/env python

# $Id: test_dependencies.py 8059 2017-04-19 16:47:35Z milde $
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Test module for the --record-dependencies option.
"""

import os.path
import unittest
import sys
import DocutilsTestSupport              # must be imported before docutils
import docutils.core
import docutils.utils
import docutils.io
from docutils.parsers.rst.directives.images import PIL

# docutils.utils.DependencyList records POSIX paths,
# i.e. "/" as a path separator even on Windows (not os.path.join).
paths = {'include': u'data/include.txt',  # included rst file
         'raw':     u'data/raw.txt',      # included raw "HTML file"
         'scaled-image': u'../docs/user/rst/images/biohazard.png',
         'figure-image': u'../docs/user/rst/images/title.png',
         'stylesheet':   u'data/stylesheet.txt',
        }


class RecordDependenciesTests(unittest.TestCase):

    def get_record(self, **settings):
        recordfile = 'record.txt'
        recorder = docutils.utils.DependencyList(recordfile)
        # (Re) create the record file by running a conversion:
        settings.setdefault('source_path',
                            os.path.join('data', 'dependencies.txt'))
        settings.setdefault('settings_overrides', {})
        settings['settings_overrides'].update(_disable_config=True,
                                              record_dependencies=recorder)
        docutils.core.publish_file(destination=DocutilsTestSupport.DevNull(),
                                   **settings)
        recorder.close()
        # Read the record file:
        record = docutils.io.FileInput(source_path=recordfile,
                                       encoding='utf8')
        return record.read().splitlines()

    def test_dependencies(self):
        # Note: currently, raw input files are read (and hence recorded) while
        # parsing even if not used in the chosen output format.
        # This should change (see parsers/rst/directives/misc.py).
        keys = ['include', 'raw']
        if PIL:
            keys += ['figure-image']
        expected = [paths[key] for key in keys]
        record = self.get_record(writer_name='xml')
        # the order of the files is arbitrary
        record.sort()
        expected.sort()
        self.assertEqual(record, expected)

    def test_dependencies_html(self):
        keys = ['include', 'raw']
        if PIL:
            keys += ['figure-image', 'scaled-image']
        expected = [paths[key] for key in keys]
        # stylesheets are tested separately in test_stylesheet_dependencies():
        so = {'stylesheet_path': None, 'stylesheet': None}
        record = self.get_record(writer_name='html', settings_overrides=so)
        # the order of the files is arbitrary
        record.sort()
        expected.sort()
        self.assertEqual(record, expected)

    def test_dependencies_latex(self):
        # since 0.9, the latex writer records only really accessed files, too.
        # Note: currently, raw input files are read (and hence recorded) while
        # parsing even if not used in the chosen output format.
        # This should change (see parsers/rst/directives/misc.py).
        keys = ['include', 'raw']
        if PIL:
            keys += ['figure-image']
        expected = [paths[key] for key in keys]
        record = self.get_record(writer_name='latex')
        # the order of the files is arbitrary
        record.sort()
        expected.sort()
        self.assertEqual(record, expected)

    def test_csv_dependencies(self):
        try:
            import csv
            csvsource = os.path.join('data', 'csv_dep.txt')
            self.assertEqual(self.get_record(source_path=csvsource),
                             ['data/csv_data.txt'])
        except ImportError:
            pass

    def test_stylesheet_dependencies(self):
        stylesheet = paths['stylesheet']
        so = {'stylesheet_path': paths['stylesheet'],
              'stylesheet': None}

        so['embed_stylesheet'] = False
        record = self.get_record(writer_name='html', settings_overrides=so)
        self.assertTrue(stylesheet not in record,
                     '%r should not be in %r' % (stylesheet, record))
        record = self.get_record(writer_name='latex', settings_overrides=so)
        self.assertTrue(stylesheet not in record,
                     '%r should not be in %r' % (stylesheet, record))

        so['embed_stylesheet'] = True
        record = self.get_record(writer_name='html', settings_overrides=so)
        self.assertTrue(stylesheet in record,
                     '%r should be in %r' % (stylesheet, record))
        record = self.get_record(writer_name='latex', settings_overrides=so)
        self.assertTrue(stylesheet in record,
                     '%r should be in %r' % (stylesheet, record))


if __name__ == '__main__':
    unittest.main()
