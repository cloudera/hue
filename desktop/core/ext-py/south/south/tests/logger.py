import os
import unittest
import tempfile

from django.conf import settings
from django.db import connection, models

from south.db import db
from south.logger import close_logger

class TestLogger(unittest.TestCase):

    """
    Tests if the logging is working reasonably. Some tests ignored if you don't
    have write permission to the disk.
    """
    
    def setUp(self):
        db.debug = False
        self.test_path = tempfile.mkstemp(suffix=".south.log")[1]
    
    def test_db_execute_logging_nofile(self):
        "Does logging degrade nicely if SOUTH_DEBUG_ON not set?"
        settings.SOUTH_LOGGING_ON = False     # this needs to be set to False
                                              # to avoid issues where other tests
                                              # set this to True. settings is shared
                                              # between these tests.
        db.create_table("test9", [('email_confirmed', models.BooleanField(default=False))])
        
    def test_db_execute_logging_validfile(self):
        "Does logging work when passing in a valid file?"
        settings.SOUTH_LOGGING_ON = True
        settings.SOUTH_LOGGING_FILE = self.test_path
        # Check to see if we can make the logfile
        try:
            open(self.test_path, "w")
        except IOError:
            # Permission was denied, ignore the test.
            return
        # Do an action which logs
        db.create_table("test10", [('email_confirmed', models.BooleanField(default=False))])
        # Close the logged file
        close_logger()
        try:
            os.remove(self.test_path)
        except:
            # It's a tempfile, it's not vital we remove it.
            pass

    def test_db_execute_logging_missingfilename(self):
        "Does logging raise an error if there is a missing filename?"
        settings.SOUTH_LOGGING_ON = True
        settings.SOUTH_LOGGING_FILE = None
        self.assertRaises(
            IOError,
            db.create_table,
            "test11",
            [('email_confirmed', models.BooleanField(default=False))],
        )
        
        