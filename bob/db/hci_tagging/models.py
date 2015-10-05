#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Sep 2015 12:13:47 CEST

import os
import pkg_resources

import bob.io.base
import bob.ip.facedetect

from . import utils


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
    self.duration = int(duration)


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

  def load_video(self, directory):
    """Loads the colored video file associated to this object

    Keyword parameters:

    directory
      A directory name that will be prefixed to the returned result.

    """

    path = os.path.join(directory, self.basedir, self.video_stem + '.avi')
    return bob.io.video.reader(path)


  def run_face_detector(self, directory, max_frames=0):
    """Runs bob.ip.facedetect stock detector on the whole video.

    Parameters:

      directory
        A directory name that leads to the location the database is installed
        on the local disk

      max_frames (int): If set, delimits the maximum number of frames to treat
        from the associated video file.

    Returns:

      dict: A dictionary containing the detected face bounding boxes and
        quality information.
    """

    detections = {}
    data = self.load_video(directory)
    if max_frames: data = data[:max_frames]
    for k, frame in enumerate(data):
      bb, quality = bob.ip.facedetect.detect_single_face(frame)
      detections[k] = {'boundingbox': bb, 'quality': quality}
    return detections


  def load_face_detections(self):
    """Loads face detections from locally stored files if they exist, fails
    gracefully otherwise, returning `None`"""

    data_dir = pkg_resources.resource_filename(__name__, 'data')
    path = self.make_path(data_dir, '.hdf5')

    if os.path.exists(path):
      f = bob.io.base.HDF5File(path)
      data = f.get('detections')
      return dict([(k[0], k[1:]) for k in f.get('detections')])

    return None


  def estimate_heartrate_in_bpm(self, directory):
    """Estimates the person's heart rate using the ECG sensor data

    Keyword parameters:

      directory
        A directory name that leads to the location the database is installed
        on the local disk

    """

    from .utils import estimate_average_heartrate, chooser


    estimates = []
    for channel in ('EXG1', 'EXG2', 'EXG3'):
      signal, freq = utils.bdf_load_signal(self.make_path(directory), channel)
      avg_hr, peaks = estimate_average_heartrate(signal, freq)
      estimates.append(avg_hr)
    return chooser(estimates)


  def load_heart_rate_in_bpm(self):
    """Loads the heart-rate from locally stored files if they exist, fails
    gracefully otherwise, returning `None`"""

    data_dir = pkg_resources.resource_filename(__name__, 'data')
    path = self.make_path(data_dir, '.hdf5')

    if os.path.exists(path):
      f = bob.io.base.HDF5File(path)
      return f.get_attribute('heartrate_bpm')

    return None


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
    if not os.path.exists(os.path.dirname(path)):
      os.makedirs(os.path.dirname(path))
    bob.io.base.save(data, path)
