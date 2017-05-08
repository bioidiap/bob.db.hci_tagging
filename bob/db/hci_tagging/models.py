#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
import pkg_resources

import bob.db.base
import bob.io.base
import bob.ip.facedetect

from . import utils


class File(bob.db.base.File):
  """ Generic file container for HCI-Tagging files


  Parameters:

    basedir (str): The base directory for the data

    bdf (str): The name of the BDF file that accompanies the video file,
      containing the physiological signals.

    video (str): The name of the video file to be used

    duration (int): The time in seconds that corresponds to the estimated
      duration of the data (video and physiological signals).

  """

  def __init__(self, basedir, bdf, video, duration):

    self.basedir = basedir
    self.stem = bdf
    self.path = os.path.join(self.basedir, self.stem)
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


  def load(self, directory=None, extension='.avi'):
    """Loads the video for this file entry


    Parameters:

      directory (str): The path to the root of the database installation.  This
        is the path leading to the directory ``Sessions`` of the database.


    Returns:

      numpy.ndarray: A 4D array of 8-bit unsigned integers corresponding to the
      input video for this file in (frame,channel,y,x) notation (Bob-style).

    """

    path = os.path.join(directory, self.basedir, self.video_stem + '.avi')

    if not os.path.exists(path):
      raise IOError("Video file `%s' is not available - have you downloaded the database raw files from the original site?" % (path,))

    return bob.io.base.load(path)


  def load_video(self, directory):
    """Loads the colored video file associated to this object

    Parameters:

      directory (str): A directory name that will be prefixed to the returned
        result.


    Returns

      bob.io.video.reader: Preloaded and ready to be iterated by your code.

    """

    path = os.path.join(directory, self.basedir, self.video_stem + '.avi')

    if not os.path.exists(path):
      raise IOError("Video file `%s' is not available - have you downloaded the database raw files from the original site?" % (path,))

    return bob.io.video.reader(path)


  def run_face_detector(self, directory, max_frames=0):
    """Runs bob.ip.facedetect stock detector on the selected frames.

    .. warning::

       This method is deprecated and serves only as a development basis to
       clean-up the :py:meth:`load_face_detection`, which for now relies on
       ``.face`` files shipped with this package. Technically, the output of
       this method and the detected faces shipped should be the same as of
       today, 13 december 2016.


    Parameters:

      directory (str): A directory name that leads to the location the database
        is installed on the local disk

      max_frames (int): If set, delimits the maximum number of frames to treat
        from the associated video file. A value of zero (default), makes the
        detector run for all frames.


    Returns:

      dict: A dictionary where the key is the frame number and the values are
      instances of :py:class:`bob.ip.facedetect.BoundingBox`.

    """

    detections = {}
    data = self.load_video(directory)
    if max_frames: data = data[:max_frames]
    for k, frame in enumerate(data):
      bb, quality = bob.ip.facedetect.detect_single_face(frame)
      detections[k] = bb
    return detections


  def load_face_detection(self):
    """Load bounding boxes for this file

    This function loads bounding boxes for each frame of a video sequence.
    Bounding boxes are loaded from the package directory and are the ones
    provided with it. Bounding boxes generated from
    :py:meth:`run_face_detector` (which should be exactly the same) are not
    used by this method.


    Returns:

      dict: A dictionary where the key is the frame number and the values are
      instances of :py:class:`bob.ip.facedetect.BoundingBox`.

    """

    basedir = os.path.join('data', 'bbox')
    data_dir = pkg_resources.resource_filename(__name__, basedir)
    path = self.make_path(data_dir, '.face')

    if not os.path.exists(path):
      raise IOError("Face bounding-box file `%s' is not available - have you run the metadata generation step or `bob_dbmanage.py hci_tagging download'?" % (path,))

    retval = {}
    with open(path, 'rt') as f:
      for row in f:
        if not row.strip(): continue
        p = row.split()
        # .face file: <frame> <x> <y> <width> <height>
        # BoundingBox ctor: top left (y, x), size (height, width)
        retval[int(p[0])] = bob.ip.facedetect.BoundingBox((float(p[2]), float(p[1])), (float(p[4]), float(p[3])))
    return retval


  def estimate_heartrate_in_bpm(self, directory):
    """Estimates the person's heart rate using the ECG sensor data

    Parameters:

      directory (str): A directory name that leads to the location the database
        is installed on the local disk

    """

    from .utils import estimate_average_heartrate, chooser


    estimates = []
    for channel in ('EXG1', 'EXG2', 'EXG3'):
      signal, freq = utils.bdf_load_signal(self.make_path(directory), channel)
      avg_hr, peaks = estimate_average_heartrate(signal, freq)
      estimates.append(avg_hr)
    return chooser(estimates)


  def load_heart_rate_in_bpm(self):
    """Loads heart-rate from locally stored files, raises if it isn't there"""

    data_dir = pkg_resources.resource_filename(__name__, 'data')
    path = self.make_path(data_dir, '.hdf5')

    if not os.path.exists(path):
      raise IOError("Metadata file `%s' is not available - have you run the metadata generation step or `bob_dbmanage.py hci_tagging download'?" % (path,))

    f = bob.io.base.HDF5File(path)
    return f.get('heartrate')


  def load_drmf_keypoints(self):
    """Loads the 66-keypoints coming from the Discriminative Response Map
    Fitting (DRMF) landmark detector. Raises if metadata file isn't there.

    Reference: http://ibug.doc.ic.ac.uk/resources/drmf-matlab-code-cvpr-2013/.

    The code was written for Matlab. Data for the first frame of the colour
    video of this object was loaded on a compatible Matlab framework and the
    keypoints extracted taking as basis the currently available face bounding
    box, enlarged by 7% (so the key-point detector performs reasonably well).
    The extracted keypoints were then merged into this database access package
    so they are easy to load from python.

    The points are in the form (y, x), as it is standard on Bob-based packages.
    """

    data_dir = pkg_resources.resource_filename(__name__, 'data')
    path = self.make_path(data_dir, '.hdf5')

    if not os.path.exists(path):
      raise IOError("Metadata file `%s' is not available - have you run the metadata generation step or `bob_dbmanage.py hci_tagging download'?" % (path,))

    f = bob.io.base.HDF5File(path)
    return f.get('drmf_landmarks66')


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
