from __future__ import absolute_import

from django.db import models
from django.test import TestCase

from .models import Author, Book


class SignalsRegressTests(TestCase):
    """
    Testing signals before/after saving and deleting.
    """

    def get_signal_output(self, fn, *args, **kwargs):
        # Flush any existing signal output
        self.signal_output = []
        fn(*args, **kwargs)
        return self.signal_output

    def pre_save_test(self, signal, sender, instance, **kwargs):
        self.signal_output.append('pre_save signal, %s' % instance)
        if kwargs.get('raw'):
            self.signal_output.append('Is raw')

    def post_save_test(self, signal, sender, instance, **kwargs):
        self.signal_output.append('post_save signal, %s' % instance)
        if 'created' in kwargs:
            if kwargs['created']:
                self.signal_output.append('Is created')
            else:
                self.signal_output.append('Is updated')
        if kwargs.get('raw'):
            self.signal_output.append('Is raw')

    def pre_delete_test(self, signal, sender, instance, **kwargs):
        self.signal_output.append('pre_save signal, %s' % instance)
        self.signal_output.append('instance.id is not None: %s' % (instance.id != None))

    def post_delete_test(self, signal, sender, instance, **kwargs):
        self.signal_output.append('post_delete signal, %s' % instance)
        self.signal_output.append('instance.id is not None: %s' % (instance.id != None))

    def setUp(self):
        self.signal_output = []
        # Save up the number of connected signals so that we can check at the end
        # that all the signals we register get properly unregistered (#9989)
        self.pre_signals = (len(models.signals.pre_save.receivers),
                       len(models.signals.post_save.receivers),
                       len(models.signals.pre_delete.receivers),
                       len(models.signals.post_delete.receivers))

        models.signals.pre_save.connect(self.pre_save_test)
        models.signals.post_save.connect(self.post_save_test)
        models.signals.pre_delete.connect(self.pre_delete_test)
        models.signals.post_delete.connect(self.post_delete_test)

    def tearDown(self):
        models.signals.post_delete.disconnect(self.post_delete_test)
        models.signals.pre_delete.disconnect(self.pre_delete_test)
        models.signals.post_save.disconnect(self.post_save_test)
        models.signals.pre_save.disconnect(self.pre_save_test)

        # Check that all our signals got disconnected properly.
        post_signals = (len(models.signals.pre_save.receivers),
                        len(models.signals.post_save.receivers),
                        len(models.signals.pre_delete.receivers),
                        len(models.signals.post_delete.receivers))

        self.assertEqual(self.pre_signals, post_signals)

    def test_model_signals(self):
        """ Model saves should throw some signals. """
        a1 = Author(name='Neal Stephenson')
        self.assertEqual(self.get_signal_output(a1.save), [
            "pre_save signal, Neal Stephenson",
            "post_save signal, Neal Stephenson",
            "Is created"
        ])

        b1 = Book(name='Snow Crash')
        self.assertEqual(self.get_signal_output(b1.save), [
            "pre_save signal, Snow Crash",
            "post_save signal, Snow Crash",
            "Is created"
        ])

    def test_m2m_signals(self):
        """ Assigning and removing to/from m2m shouldn't generate an m2m signal """

        b1 = Book(name='Snow Crash')
        self.get_signal_output(b1.save)
        a1 = Author(name='Neal Stephenson')
        self.get_signal_output(a1.save)
        self.assertEqual(self.get_signal_output(setattr, b1, 'authors', [a1]), [])
        self.assertEqual(self.get_signal_output(setattr, b1, 'authors', []), [])
