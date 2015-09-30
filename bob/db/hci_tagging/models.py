#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Sep 2015 12:13:47 CEST

import os
import bob

class File(object):
  """ Generic file container for HCI-Tagging files


  Parameters:

    basedir (path): The base directory for the data
    bdf (str): The name of the BDF file that accompanies the video file,
      containing the physiological signals.
    video (str): The name of the video file to be used
    duration (int): The time in seconds that corresponds to the estimated
      duration of the data (video and physiological signals).

  """

  def __init__(self, basedir, bdf, video, duration):

    self.basedir = basedir
    self.stem = bdf
    self.video_stem = video
    self.duration = duration


  def __repr__(self):
    return "File('%s')" % self.stem


  def default_extension(self):
      return '.bdf'


  def make_path(self, directory=None, extension=None):
    """Wraps this files' filename so that a complete path is formed

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.png`` or
      ``.bmp``. If not specified the default extension for the original file in
      the database will be used

    Returns a string containing the newly generated file path.
    """

    return os.path.join(
            directory or '',
            self.basedir,
            self.stem + (extension or self.default_extension()),
            )


  def save(self, data, directory=None, extension='.hdf5'):
    """Saves the input data at the specified location and using the given
    extension.

    Keyword parameters:

    data
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory
      If not empty or None, this directory is prefixed to the final file
      destination

    extension
      The extension of the filename - this will control the type of output and
      the codec for saving the input blob.
    """

    path = self.make_path(directory, extension)
    bob.db.utils.makedirs_safe(os.path.dirname(path))
    bob.io.save(data, path)
