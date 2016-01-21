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


  def objects(self, protocol='all', subset=None):
    """Returns a list of unique :py:class:`.File` objects for the specific
    query by the user.


    Parameters:

      protocol (str, optional): If set, can take the value of either 'cvpr14' or 'all'.
        'cvpr14' subselects samples used by Li et al. on their CVPR'14 paper for
        heart-rate estimation. If 'all' is set, the complete database is selected.

      subset (str, optional): If set, it could be either 'train', 'dev' or 'test'
        or a combination of them (i.e. a list). If not set (default), 
        the files from all these sets are retrieved for the 'all' protocol.
        Note that for 'cvpr14' protocol, this has no effect, since no training,
        development and test set have been defined in this case.



    Returns: A list of :py:class:`File` objects.
    """
    if protocol in ('cvpr14',):
      d = resource_filename(__name__, os.path.join('protocols/cvpr14', 'li_samples_cvpr14.txt'))
      with open(d, 'rt') as f: sessions = f.read().split()
      return [File(**k) for k in self.metadata if k['basedir'] in sessions]
    
    if protocol in ('all'):

      if 'None' in subset:
        return [File(**k) for k in self.metadata]
      else:
        files = []
        if 'train' in subset:
          d = resource_filename(__name__, os.path.join('protocols/all', 'train.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(**k) for k in self.metadata if k['basedir'] in sessions]
        if 'dev' in subset:
          d = resource_filename(__name__, os.path.join('protocols/all', 'dev.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(**k) for k in self.metadata if k['basedir'] in sessions]
        if 'test' in subset:
          d = resource_filename(__name__, os.path.join('protocols/all', 'test.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(**k) for k in self.metadata if k['basedir'] in sessions]
      
        return files
