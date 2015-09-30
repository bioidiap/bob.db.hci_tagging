#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri Mar 14 14:44:31 CET 2014

"""A few checks at the Mahnob HCI-Tagging dataset
"""

import os, sys
import unittest
from . import Database

DATABASE_LOCATION = '/idiap/resource/database/HCI_Tagging'

def db_available(test):
  """Decorator for detecting if we're running the test at Idiap"""
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):

    if os.path.exists(DATABASE_LOCATION):
      return test(*args, **kwargs)
    else:
      raise SkipTest("Raw database files are not available")

  return wrapper


class HCITaggingTest(unittest.TestCase):
  """Performs various tests on the HCI-Tagging database."""

  def setUp(self):
    self.db = Database()


  def test01_objects(self):
    self.assertEqual(len(self.db.objects()), 3490)


  @db_available
  def test02_can_read_bdf(self):

    from .models import bdf_load_signal

    for obj in self.db.objects():

      path = obj.make_path(DATABASE_LOCATION, '.bdf')
      self.assertTrue(os.path.exists(path))

      signal, freq = bdf_load_signal(path)

      time = len(signal)/freq

      # correlation between video data and physiological signal
      if abs(time-obj.duration) > 2:
        print('Physiological signal (%d seconds) is very different in size from estimated video duration (%d seconds) on sample `%s/%s\'' % (time, obj.duration, obj.basedir, obj.stem))


class CmdLineTest(unittest.TestCase):
  """Makes sure our command-line is working properly."""

  def test01_manage_dumplist(self):

    from bob.db.base.script.dbmanage import main

    args = [
            'hci_tagging',
            'dumplist',
            '--self-test',
            ]

    self.assertEqual(main(args), 0)


  @db_available
  def test02_manage_checkfiles(self):

    from bob.db.base.script.dbmanage import main

    args = [
            'hci_tagging',
            'checkfiles',
            '--self-test',
            '--directory=%s' % DATABASE_LOCATION,
            ]

    self.assertEqual(main(args), 0)
