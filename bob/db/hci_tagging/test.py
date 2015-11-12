#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri Mar 14 14:44:31 CET 2014

"""A few checks at the Mahnob HCI-Tagging dataset
"""

import os, sys
import unittest
import nose.tools
import pkg_resources

from . import Database
from .driver import DATABASE_LOCATION


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


def meta_available(test):
  """Decorator for detecting if we're running the test on an annotated db"""
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):

    if os.path.exists(pkg_resources.resource_filename(__name__, 'data')):
      return test(*args, **kwargs)
    else:
      raise SkipTest("Annotation files are not available")

  return wrapper


class HCITaggingTest(unittest.TestCase):
  """Performs various tests on the HCI-Tagging database."""

  def setUp(self):
    self.db = Database()


  def test01_objects(self):
    self.assertEqual(len(self.db.objects()), 3490)


  def test01b_objects_cvpr14(self):
    self.assertEqual(len(self.db.objects('cvpr14')), 527)


  @db_available
  def test02_can_read_bdf(self):

    from .utils import bdf_load_signal

    for obj in self.db.objects()[:3]:

      path = obj.make_path(DATABASE_LOCATION, '.bdf')
      self.assertTrue(os.path.exists(path))

      signal, freq = bdf_load_signal(path)

      assert signal.size
      assert freq

      '''
      time = len(signal)/freq

      # correlation between video data and physiological signal
      if abs(time-obj.duration) > 2:
        print('Physiological signal (%d seconds) is very different in size from estimated video duration (%d seconds) on sample `%s/%s\'' % (time, obj.duration, obj.basedir, obj.stem))
      '''


  @db_available
  def test03_can_read_camera1_video(self):

    for obj in self.db.objects()[:5]:

      video = obj.load_video(DATABASE_LOCATION)
      assert video.number_of_frames


  @meta_available
  def test04_can_read_meta(self):

    for obj in self.db.objects()[:3]:

      detection = obj.load_face_detection()
      assert detection

      hr = obj.load_heart_rate_in_bpm()
      assert hr


  @nose.tools.nottest
  @db_available
  def test05_can_write_meta(self):

    import matplotlib.pyplot as plt
    from .utils import bdf_load_signal, plot_signal

    for obj in self.db.objects()[:1]:
      #if obj.stem.find('Part_1_') < 0: continue

      estimates = []
      for i, channel in enumerate(('EXG1', 'EXG2', 'EXG3')):
        plt.subplot(3, 1, i+1)
        signal_file = obj.make_path(DATABASE_LOCATION)
        signal, freq = bdf_load_signal(signal_file, channel)
        avg_hr, peaks = plot_signal(signal, freq, channel)
        estimates.append(avg_hr)

      plt.tight_layout()
      plt.show()


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


  @db_available
  def notest03_can_create_meta(self):

    from bob.db.base.script.dbmanage import main

    args = [
            'hci_tagging',
            'mkmeta',
            '--self-test',
            '--directory=%s' % DATABASE_LOCATION,
            ]

    self.assertEqual(main(args), 0)
