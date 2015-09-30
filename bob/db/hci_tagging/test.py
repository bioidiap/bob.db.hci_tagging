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
