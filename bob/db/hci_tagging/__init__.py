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


  def objects(self):
    """Returns a list of unique :py:class:`.File` objects for the specific
    query by the user.

    Returns: A list of :py:class:`.File` objects.
    """

    return [File(**k) for k in self.metadata]
