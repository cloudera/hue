#!/usr/bin/env python
#
# Copyright (C) 2013 Martin Owens
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
"""
Test crontab interaction.
"""

import re
import os
import unittest

from crontab import CronTab, CronSlices, CronSlice, PY3
from .utils import LoggingMixin

try:
    from test import test_support
except ImportError:
    from test import support as test_support

TEST_DIR = os.path.dirname(__file__)

if PY3:
    unicode = str #pylint: disable=redefined-builtin

COMMANDS = [
    'firstcommand',
    'range',
    'byweek',
    'disabled',
    'spaced',
    'python /example_app/testing.py',
    'rebooted',
]

RESULT_TAB = """# First Comment
# Edit this line to test for mistaken checks

# m h dom mon dow user command

*/30 * * * * firstcommand
* 10-20/3 * * * range
# Middle Comment
* * * 10 * byweek # Comment One
# * * * * * disabled
0 5 * * * spaced # Comment  Two

*/59 * * * * python /example_app/testing.py # monitorCron

@reboot rebooted # re-id
# Last Comment @has this # extra
"""

class InteractionTestCase(LoggingMixin, unittest.TestCase):
    """Test basic functionality of crontab."""
    log_name = 'crontab'

    def setUp(self):
        super(InteractionTestCase, self).setUp()
        self.crontab = CronTab(tabfile=os.path.join(TEST_DIR, 'data', 'test.tab'))

    def test_01_presevation(self):
        """All Entries Re-Rendered Correctly"""
        results = RESULT_TAB.split('\n')
        for line_no, line in enumerate(self.crontab.lines):
            self.assertEqual(str(line), results[line_no])

    def test_02_access(self):
        """All Entries Are Accessable"""
        for line_no, job in enumerate(self.crontab):
            self.assertEqual(str(job.command), COMMANDS[line_no])
        else: # pylint: disable=useless-else-on-loop
            self.assertEqual(line_no + 1, 7)

    def test_03_blank(self):
        """Render Blank"""
        job = self.crontab.new(command='blank')
        self.assertEqual(repr(job), '<CronItem \'* * * * * blank\'>')
        self.assertEqual(job.render(), '* * * * * blank')

    def test_04_number(self):
        """Render Number"""
        job = self.crontab.new(command='number')
        job.minute.on(4)
        self.assertEqual(job.render(), '4 * * * * number')

    def test_05_fields(self):
        """Render Hours Days and Weeks"""
        job = self.crontab.new(command='fields')
        job.hour.on(4)
        self.assertEqual(job.render(), '* 4 * * * fields')
        job.dom.on(5)
        self.assertEqual(job.render(), '* 4 5 * * fields')
        job.month.on(6)
        self.assertEqual(job.render(), '* 4 5 6 * fields')
        job.dow.on(7)
        self.assertEqual(job.render(), '* 4 5 6 0 fields')

    def test_05_multiple_fields(self):
        """Test mutliple named fields"""
        job = self.crontab.new(command='fields')
        job.hour.on(4, 6, 7)
        self.assertEqual(job.render(), '* 4,6,7 * * * fields')
        job.dow.on('SUN', 'FRI')
        self.assertEqual(job.render(), '* 4,6,7 * * SUN,FRI fields')

    def test_06_clear(self):
        """Render Hours Days and Weeks"""
        job = self.crontab.new(command='clear')
        job.minute.on(3)
        job.hour.on(4)
        job.dom.on(5)
        job.month.on(6)
        job.dow.on(7)
        self.assertEqual(job.render(), '3 4 5 6 0 clear')
        job.clear()
        self.assertEqual(job.render(), '* * * * * clear')

    def test_07_range(self):
        """Render Time Ranges"""
        job = self.crontab.new(command='range')
        job.minute.during(4, 10)
        self.assertEqual(job.render(), '4-10 * * * * range')
        job.minute.during(15, 19)
        self.assertEqual(job.render(), '15-19 * * * * range')
        job.minute.clear()
        self.assertEqual(job.render(), '* * * * * range')
        job.minute.during(15, 19)
        self.assertEqual(job.render(), '15-19 * * * * range')
        job.minute.also.during(4, 10)
        self.assertEqual(job.render(), '4-10,15-19 * * * * range')

    def test_08_sequence(self):
        """Render Time Sequences"""
        job = self.crontab.new(command='seq')
        job.hour.every(4)
        self.assertEqual(job.render(), '* */4 * * * seq')
        job.hour.during(2, 10)
        self.assertEqual(job.render(), '* 2-10 * * * seq')
        job.hour.clear()
        self.assertEqual(job.render(), '* * * * * seq')
        job.hour.during(2, 10).every(4)
        self.assertEqual(job.render(), '* 2-10/4 * * * seq')
        job.hour.also.during(1, 4)
        self.assertEqual(job.render(), '* 1-4,2-10/4 * * * seq')
        job.hour.also.every(4)
        self.assertEqual(job.render(), '* */4,1-4,2-10/4 * * * seq')

    def test_10_comment(self):
        """Render cron Comments"""
        job = self.crontab.new(command='com', comment='I love this')
        self.assertEqual(unicode(job), '* * * * * com # I love this')

    def test_11_disabled(self):
        """Disabled Job"""
        jobs = list(self.crontab.find_command('firstcommand'))
        self.assertTrue(jobs[0].enabled)
        jobs = list(self.crontab.find_command('disabled'))
        self.assertFalse(jobs[0].enabled)

    def test_12_disable(self):
        """Disable and Enable Job"""
        job = self.crontab.new(command='dis')
        job.enable(False)
        self.assertEqual(unicode(job), '# * * * * * dis')
        job.enable()
        self.assertEqual(unicode(job), '* * * * * dis')

    def test_13_plural(self):
        """Plural API"""
        job = self.crontab.new(command='plural')
        job.minutes.every(4)
        job.hours.on(5, 6)
        job.day.on(4)
        job.months.on(2)
        self.assertEqual(unicode(job), '*/4 5,6 4 2 * plural')

    def test_14_valid(self):
        """Valid and Invalid"""
        job = self.crontab.new(command='valid')
        job.minute.every(2)
        job.valid = False
        with self.assertRaises(ValueError):
            unicode(job)
        # Disabled jobs still work
        job.enabled = False
        unicode(job)

        job.enabled = True
        with self.assertRaises(ValueError):
            self.crontab.render(errors=True)
        self.crontab.render(errors=False)
        self.assertFalse(job.enabled)

    def test_15_slices(self):
        """Invalid Slices"""
        mon = CronSlices('* * * * *')
        with self.assertRaises(ValueError):
            CronSlices('* * * */15 *')
        with self.assertRaises(AssertionError):
            mon.setall(mon)

    def test_16_slice(self):
        """Single Slice"""
        dow = CronSlice({'name': 'M', 'max': 7, 'min': 0, 'enum': ['a']}, '*/6')
        self.assertEqual(repr(dow), '<CronSlice \'*/6\'>')

        self.assertEqual(repr(dow.parse_value('a')), 'a')
        with self.assertRaises(ValueError):
            dow.parse_value('b')

        self.assertEqual(dow.get_range()[0].render(), '*')
        with self.assertRaises(ValueError):
            dow.get_range('%')

    def test_17_slice_id(self):
        """Single slice by Id"""
        self.assertEqual(CronSlice(1).max, 23)

    def test_18_range_cmp(self):
        """Compare ranges"""
        dow = CronSlice({'max': 5, 'min': 0})
        three = dow.get_range(2, 4)[0]
        self.assertGreater(three, 2)
        self.assertLess(three, 4)
        self.assertEqual(str(three), '2-4')

    def test_18_find(self):
        """Find a command and comments by name"""
        cmds = list(self.crontab.find_command('byweek'))
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].comment, 'Comment One')

        cmds = list(self.crontab.find_command(re.compile(r'stc\w')))
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].command, 'firstcommand')

        cmds = list(self.crontab.find_command('Comment One'))
        self.assertEqual(len(cmds), 0)

        cmds = list(self.crontab.find_comment('Comment One'))
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].command, 'byweek')

        cmds = list(self.crontab.find_comment(re.compile(r'om+en\w O')))
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].comment, 'Comment One')

        cmds = list(self.crontab.find_comment(re.compile(r'stc\w')))
        self.assertEqual(len(cmds), 0)

    def test_20_write(self):
        """Write CronTab to file"""
        self.crontab.write('output.tab')
        self.assertTrue(os.path.exists('output.tab'))
        os.unlink('output.tab')

    def test_21_multiuse(self):
        """Multiple Renderings"""
        cron = '# start of tab\n'
        for i in range(10):
            crontab = CronTab(tab=cron)
            p = list(crontab.new(command='multi%d' % i))
            cron = unicode(crontab)
            crontab = CronTab(tab=cron)
            list(crontab.find_command('multi%d' % i))[0].delete()
            cron = unicode(crontab)
        self.assertEqual(unicode(crontab), '# start of tab\n')

    def test_22_min(self):
        """Minimum Field Values"""
        job = self.crontab.new(command='min')
        job.minute.on('<')
        job.hour.on('<')
        job.dom.on('<')
        job.month.on('<')
        self.assertEqual(unicode(job), '@yearly min')

    def test_23_max(self):
        """Maximum Field Values"""
        job = self.crontab.new(command='max')
        job.minute.on('>')
        job.hour.on('>')
        job.dom.on('>')
        job.month.on('>')
        self.assertEqual(unicode(job), '59 23 31 12 * max')

    def test_24_special_r(self):
        """Special formats are read and written"""
        tab = CronTab(tabfile=os.path.join(TEST_DIR, 'data', 'specials_enc.tab'))
        self.assertEqual(tab.render(), """@hourly hourly\n@daily daily\n@midnight midnight\n@weekly weekly\n@reboot reboot\n""")
        self.assertEqual(len(list(tab)), 5)

    def test_24_special_d(self):
        """Removal All Specials"""
        tab = CronTab(tabfile=os.path.join(TEST_DIR, 'data', 'specials.tab'))
        tab.remove_all()
        self.assertEqual(len(list(tab)), 0)

    def test_24_special_w(self):
        """Write Specials"""
        tab = CronTab(tabfile=os.path.join(TEST_DIR, 'data', 'specials.tab'))
        self.assertEqual(tab.render(), """@hourly hourly\n@daily daily\n@weekly weekly\n""")
        self.assertEqual(len(list(tab)), 3)

    def test_25_setall(self):
        """Set all values at once"""
        job = self.crontab.new(command='all')
        job.setall(1, '*/2', '2-4', '>', 'SUN')
        self.assertEqual(unicode(job), '1 */2 2-4 12 SUN all')
        job.setall('*/2')
        self.assertEqual(unicode(job), '*/2 * * * * all')
        job.setall('1 */2 2-4 12 SUN')
        self.assertEqual(unicode(job), '1 */2 2-4 12 SUN all')
        job.setall(['*'])
        self.assertEqual(unicode(job), '* * * * * all')

    def test_26_setall_obj(self):
        """Copy all values"""
        job = self.crontab.new(command='all')
        job2 = self.crontab.new(command='ignore')
        job2.setall("1 */2 2-4 12 SUN")
        job.setall(job2)
        self.assertEqual(unicode(job), '1 */2 2-4 12 SUN all')
        job2.setall("2 */3 4-8 10 MON")
        job.setall(job2.slices)
        self.assertEqual(unicode(job), '2 */3 4-8 10 MON all')

    def test_27_commands(self):
        """Get all commands"""
        self.assertEqual(list(self.crontab.commands),
                         [u'firstcommand', u'range', u'byweek', u'disabled',
                          u'spaced', u'python /example_app/testing.py',
                          u'rebooted'])

    def test_28_comments(self):
        """Get all comments"""
        self.assertEqual(list(self.crontab.comments),
                         ['Comment One', 'Comment  Two', 'monitorCron', 're-id'])

    def test_29_set_lines(self):
        """Set crontab lines directly"""
        cron = CronTab(tab='')
        cron.lines = [
            str(self.crontab.lines[5]),
        ]
        self.assertEqual(str(cron), '\n*/30 * * * * firstcommand\n')

        with self.assertRaises(AttributeError):
            cron.crons = ['A']


if __name__ == '__main__':
    test_support.run_unittest(InteractionTestCase)
