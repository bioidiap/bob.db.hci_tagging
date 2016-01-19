#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Sep 2015 12:14:50 CEST

import os
from .models import *

from pkg_resources import resource_filename
LOCATION = resource_filename(__name__, 'metadata.csv')

class Database(object):

  def __init__(self):
    from .driver import Interface
    self.info = Interface()

    # Loads metadata
    import csv
    with open(LOCATION) as f:
      reader = csv.DictReader(f)
      self.metadata = [row for row in reader]


  def objects(self, protocol=None):
    """Returns a list of unique :py:class:`.File` objects for the specific
    query by the user.


    Parameters:

      protocol (str, optional): If set, can take the value of 'cvpr14',
        which subselects samples used by Li et al. on their CVPR'14 paper for
        heart-rate estimation.


    Returns: A list of :py:class:`File` objects.
    """

    if protocol in ('cvpr14',):
      d = resource_filename(__name__, os.path.join('data', 'li_samples_cvpr14.txt'))
      with open(d, 'rt') as f: sessions = f.read().split()
      return [File(**k) for k in self.metadata if k['basedir'] in sessions]
    
    elif protocol in ('train',):
      d = resource_filename(__name__, os.path.join('data', 'train.txt'))
      with open(d, 'rt') as f: sessions = f.read().split()
      return [File(**k) for k in self.metadata if k['basedir'] in sessions]
    
    elif protocol in ('dev',):
      d = resource_filename(__name__, os.path.join('data', 'dev.txt'))
      with open(d, 'rt') as f: sessions = f.read().split()
      return [File(**k) for k in self.metadata if k['basedir'] in sessions]
    
    elif protocol in ('test',):
      d = resource_filename(__name__, os.path.join('data', 'test.txt'))
      with open(d, 'rt') as f: sessions = f.read().split()
      return [File(**k) for k in self.metadata if k['basedir'] in sessions]
    
    elif protocol in ('traindev',):
      d = resource_filename(__name__, os.path.join('data', 'traindev.txt'))
      with open(d, 'rt') as f: sessions = f.read().split()
      return [File(**k) for k in self.metadata if k['basedir'] in sessions]

    elif protocol is not None:
      raise RuntimeError('Protocol should be either "train", "dev", "traindev", "test", "cvpr14" or not set. The value %s is not valid' % protocol)

    return [File(**k) for k in self.metadata]
