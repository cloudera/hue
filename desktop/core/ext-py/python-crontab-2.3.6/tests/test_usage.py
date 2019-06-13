#!/usr/bin/env python
#
# Copyright (C) 2012 Jay Sigbrandt <jsigbrandt@slb.com>
#                    Martin Owens <doctormo@gmail.com>
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
Test crontab usage.
"""

import os
import sys

import unittest
import crontab

from datetime import date, time, datetime, timedelta

try:
    from test import test_support
except ImportError:
    from test import support as test_support

crontab.LOG.setLevel(crontab.logging.ERROR)
TEST_DIR = os.path.dirname(__file__)

class DummyStdout(object):
    def write(self, text):
        pass

BASIC = '@hourly firstcommand\n\n'
USER = '\n*/4 * * * * user_command # user_comment\n\n\n'
crontab.CRONCMD = "%s %s" % (sys.executable, os.path.join(TEST_DIR, 'data', 'crontest'))

def flush():
    pass

class Attribute(object):
    def __init__(self, obj, attr, value):
        self.obj = obj
        self.attr = attr
        self.value = value

    def __enter__(self, *args, **kw):
        if hasattr(self.obj, self.attr):
            self.previous = getattr(self.obj, self.attr)
        setattr(self.obj, self.attr, self.value)

    def __exit__(self, *args, **kw):
        if hasattr(self, 'previous'):
            setattr(self.obj, self.attr, self.previous)
        else:
            delattr(self.obj, self.attr)


class UseTestCase(unittest.TestCase):
    """Test use documentation in crontab."""
    def setUp(self):
        self.filenames = []

    def test_01_empty(self):
        """Open system crontab"""
        cron = crontab.CronTab()
        self.assertEqual(cron.render(), "")
        self.assertEqual(cron.__unicode__(), "")
        self.assertEqual(repr(cron), "<Unattached CronTab>")

    def test_02_user(self):
        """Open a user's crontab"""
        cron = crontab.CronTab(user='basic')
        self.assertEqual(cron.render(), BASIC)
        self.assertEqual(repr(cron), "<User CronTab 'basic'>")

    def test_03_usage(self):
        """Dont modify crontab"""
        cron = crontab.CronTab(tab='')
        sys.stdout = DummyStdout()
        sys.stdout.flush = flush
        try:
            exec(crontab.__doc__)
        except ImportError:
            pass
        sys.stdout = sys.__stdout__
        self.assertEqual(cron.render(), '')

    def test_04_username(self):
        """Username is True"""
        cron = crontab.CronTab(user=True)
        self.assertNotEqual(cron.user, True)
        self.assertEqual(cron.render(), USER)
        self.assertEqual(repr(cron), "<My CronTab>")

    def test_05_nouser(self):
        """Username doesn't exist"""
        cron = crontab.CronTab(user='nouser')
        self.assertEqual(cron.render(), '')

    def test_06_touser(self):
        """Write to use API"""
        cron = crontab.CronTab(tab=USER)
        self.assertEqual(repr(cron), "<Unattached CronTab>")
        cron.write_to_user('bob')
        filename = os.path.join(TEST_DIR, 'data', 'spool', 'bob')
        self.filenames.append(filename)
        self.assertTrue(os.path.exists(filename))
        self.assertEqual(repr(cron), "<User CronTab 'bob'>")

    def test_07_ioerror_read(self):
        """No filename ioerror"""
        with self.assertRaises(IOError):
            cron = crontab.CronTab(user='error')
            cron.read()

    def test_07_ioerror_write(self):
        """User not specified, nowhere to write to"""
        cron = crontab.CronTab()
        with self.assertRaises(IOError):
            cron.write()

    def test_08_cronitem(self):
        """CronItem Standalone"""
        item = crontab.CronItem.from_line('noline')
        self.assertTrue(item.is_enabled())
        with self.assertRaises(UnboundLocalError):
            item.delete()
        item.command = str('nothing')
        self.assertEqual(item.render(), '* * * * * nothing')

    def test_10_time_object(self):
        """Set slices using time object"""
        item = crontab.CronItem(command='cmd')
        self.assertEqual(str(item.slices), '* * * * *')
        item.setall(time(1, 2))
        self.assertEqual(str(item.slices), '2 1 * * *')
        self.assertTrue(item.is_valid())
        item.setall(time(0, 30, 0, 0))
        self.assertEqual(str(item.slices), '30 0 * * *')
        self.assertTrue(item.is_valid())
        self.assertEqual(str(item), '30 0 * * * cmd')

    def test_11_date_object(self):
        """Set slices using date object"""
        item = crontab.CronItem(command='cmd')
        self.assertEqual(str(item.slices), '* * * * *')
        item.setall(date(2010, 6, 7))
        self.assertEqual(str(item.slices), '0 0 7 6 *')
        self.assertTrue(item.is_valid())

    def test_12_datetime_object(self):
        """Set slices using datetime object"""
        item = crontab.CronItem(command='cmd')
        self.assertEqual(str(item.slices), '* * * * *')
        item.setall(datetime(2009, 8, 9, 3, 4))
        self.assertTrue(item.is_valid())
        self.assertEqual(str(item.slices), '4 3 9 8 *')

    def test_20_slice_validation(self):
        """CronSlices class and objects can validate"""
        CronSlices = crontab.CronSlices
        self.assertTrue(CronSlices('* * * * *').is_valid())
        self.assertTrue(CronSlices.is_valid('* * * * *'))
        self.assertTrue(CronSlices.is_valid('*/2 * * * *'))
        self.assertTrue(CronSlices.is_valid('* 1,2 * * *'))
        self.assertTrue(CronSlices.is_valid('* * 1-5 * *'))
        self.assertTrue(CronSlices.is_valid('* * * * MON-WED'))
        self.assertTrue(CronSlices.is_valid('@reboot'))

        sliced = CronSlices('* * * * *')
        sliced[0].parts = [300]
        self.assertEqual(str(sliced), '300 * * * *')
        self.assertFalse(sliced.is_valid())
        self.assertFalse(CronSlices.is_valid('P'))
        self.assertFalse(CronSlices.is_valid('*/61 * * * *'))
        self.assertFalse(CronSlices.is_valid('* 1,300 * * *'))
        self.assertFalse(CronSlices.is_valid('* * 50-1 * *'))
        self.assertFalse(CronSlices.is_valid('* * * * FRO-TOO'))
        self.assertFalse(CronSlices.is_valid('@retool'))

    def test_25_open_pipe(self):
        """Test opening pipes"""
        from crontab import open_pipe, CRONCMD
        pipe = open_pipe(CRONCMD, h=None, a='one', abc='two')
        (out, err) = pipe.communicate()
        self.assertEqual(err, b'')
        self.assertEqual(out, b'--abc=two|-a|-h|one\n')

    def test_07_zero_padding(self):
        """Can we get zero padded output"""
        cron = crontab.CronTab(tab="02 3-5 2,4 */2 01 cmd")
        self.assertEqual(str(cron), '2 3-5 2,4 */2 1 cmd\n')
        with Attribute(crontab, 'ZERO_PAD', True):
            self.assertEqual(str(cron), '02 03-05 02,04 */2 01 cmd\n')

    def tearDown(self):
        for filename in self.filenames:
            if os.path.exists(filename):
                os.unlink(filename)


if __name__ == '__main__':
    test_support.run_unittest(
       UseTestCase,
    )
