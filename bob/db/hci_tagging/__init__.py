#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

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

      protocol (:py:class:`str`, optional): If set, can take the value of
        either ``cvpr14`` or ``all``. ``cvpr14`` subselects samples used by Li
        et al. on their CVPR``14 paper for heart-rate estimation. If ``all`` is
        set, the complete database is selected.

      subset (:py:class:`str`, optional): If set, it could be either ``train``,
        ``dev`` or ``test`` or a combination of them (i.e. a list). If not set
        (default), the files from all these sets are retrieved for the ``all``
        protocol. Note that for the ``cvpr14`` protocol, this has no effect,
        since no training, development and test set have been defined in this
        case.


    Returns:

      list: A list of :py:class:`File` objects.

    """

    proto_basedir = os.path.join('data', 'protocols')

    if protocol in ('cvpr14',):
      d = resource_filename(__name__, os.path.join(proto_basedir, 'cvpr14', 'li_samples_cvpr14.txt'))
      with open(d, 'rt') as f: sessions = f.read().split()
      return [File(**k) for k in self.metadata if k['basedir'] in sessions]

    if protocol in ('all'):

      if not subset:
        return [File(**k) for k in self.metadata]
      else:
        files = []
        if 'train' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'all', 'train.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(**k) for k in self.metadata if k['basedir'] in sessions]
        if 'dev' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'all', 'dev.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(**k) for k in self.metadata if k['basedir'] in sessions]
        if 'test' in subset:
          d = resource_filename(__name__, os.path.join(proto_basedir, 'all', 'test.txt'))
          with open(d, 'rt') as f: sessions = f.read().split()
          files += [File(**k) for k in self.metadata if k['basedir'] in sessions]

        return files


# gets sphinx autodoc done right - don't remove it
def __appropriate__(*args):
  """Says object was actually declared here, an not on the import module.

  Parameters:

    *args: An iterable of objects to modify

  Resolves `Sphinx referencing issues
  <https://github.com/sphinx-doc/sphinx/issues/3048>`
  """

  for obj in args: obj.__module__ = __name__

__appropriate__(
    File,
    )

__all__ = [_ for _ in dir() if not _.startswith('_')]
