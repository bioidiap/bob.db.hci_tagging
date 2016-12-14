#!/usr/bin/env python
# encoding: utf-8

'''Utilities for Remote Photo-Plethysmography Benchmarking'''

import os
import numpy
import bob.io.video
import bob.ip.draw
import bob.ip.facedetect

from mne.preprocessing.ecg import qrs_detector


def bdf_load_signal(fn, name='EXG3', start=None, end=None):
  """Loads a signal named ``name`` from the BDF filenamed ``fn``


  Parameters:

    fn (path): The full path to the file to read
    name (str): The name of the channel to read.
    start (int, option): Start time in seconds
    end (int, optional): End time in seconds


  List of physiological channels used (there are more available, but contain no
  meaningful data) on the Mahnob HCI-Tagging database:

    These are the 32 electrodes from the EEG cap (measurements in uV; for full
    positioning details, see the full database description report, available on
    the database website):

      * AF3
      * AF4
      * C3
      * C4
      * CP1
      * CP2
      * CP5
      * CP6
      * Cz
      * F3
      * F4
      * F7
      * F8
      * FC1
      * FC2
      * FC5
      * FC6
      * Fp1
      * Fp2
      * Fz
      * O1
      * O2
      * Oz
      * P3
      * P4
      * P7
      * P8
      * PO3
      * PO4
      * Pz
      * T7
      * T8

    These are ECG sensors (measurements in uV):

    * EXG1: Upper right corner of chest, under clavicle bone
    * EXG2: Upper left corner of chest, under clavicle bone
    * EXG3: Left side of abdomen (very clean)

    Other sensors:

    * GSR1: Galvanic skin response (in Ohm)
    * Resp: Respiration belt (in uV)
    * Status: Status channel containing markers (Boolean)
    * Temp: Skin temperature on the left pinky (Celsius)

  """

  import pyedflib

  if not os.path.exists(fn): #or the EdfReader will crash the interpreter
    raise IOError("file `%s' does not exist" % fn)

  with pyedflib.EdfReader(fn) as e:

    # get the status information, so we how the video is synchronized
    status_index = e.getSignalLabels().index('Status')
    sample_frequency = e.samplefrequency(status_index)
    status_size = e.samples_in_file(status_index)
    status = numpy.zeros((status_size,), dtype='float64')
    e.readsignal(status_index, 0, status_size, status)
    status = status.round().astype('int')
    nz_status = status.nonzero()[0]

    # because we're interested in the video bits, make sure to get data
    # from that period only
    video_start = nz_status[0]
    video_end = nz_status[-1]

    # retrieve information from this rather chaotic API
    index = e.getSignalLabels().index(name)
    sample_frequency = e.samplefrequency(index)

    video_start_seconds = video_start/sample_frequency

    if start is not None:
      start += video_start_seconds
      start *= sample_frequency
      if start < video_start: start = video_start
      start = int(start)
    else:
      start = video_start

    if end is not None:
      end += video_start_seconds
      end *= sample_frequency
      if end > video_end: end = video_end
      end = int(end)
    else:
      end = video_end

    # now read the data into a numpy array (read everything)
    container = numpy.zeros((end-start,), dtype='float64')
    e.readsignal(index, start, end-start, container)

    return container, sample_frequency


def estimate_average_heartrate(s, sampling_frequency):
  '''Estimates the average heart rate taking as base the input signal and its
  sampling frequency.

  This method will use the Pam-Tompkins detector available the MNE package to
  clean-up and estimate the heart-beat frequency based on the ECG sensor
  information provided.

  Returns:

    float: The estimated average heart-rate in beats-per-minute

  '''

  peaks = qrs_detector(sampling_frequency, s)
  instantaneous_rates = (sampling_frequency * 60) / numpy.diff(peaks)

  # remove instantaneous rates which are lower than 30, higher than 240
  selector = (instantaneous_rates>30) & (instantaneous_rates<240)
  return float(numpy.nan_to_num(instantaneous_rates[selector].mean())), peaks


def plot_signal(s, sampling_frequency, channel_name):
  '''Estimates the heart rate taking as base the input signal and its sampling
  frequency, plots QRS peaks discovered on the base signal.

  This method will use the Pam-Tompkins detector available the MNE package to
  clean-up and estimate the heart-beat frequency based on the ECG sensor
  information provided.

  Returns:

    float: The estimated average heart-rate in beats-per-minute

  '''
  import matplotlib.pyplot as plt

  avg, peaks = estimate_average_heartrate(s, sampling_frequency)

  ax = plt.gca()
  ax.plot(numpy.arange(0, len(s)/sampling_frequency, 1/sampling_frequency),
          s, label='Raw signal');
  xmin, xmax, ymin, ymax = plt.axis()
  ax.vlines(peaks / sampling_frequency, ymin, ymax, colors='r', label='P-T QRS detector')
  plt.xlim(0, len(s)/sampling_frequency)
  plt.ylabel('uV')
  plt.xlabel('time (s)')
  plt.title('Channel %s - Average heart-rate = %d bpm' % (channel_name, avg))
  ax.grid(True)
  ax.legend(loc='best', fancybox=True, framealpha=0.5)

  return avg, peaks


def chooser(average_rates):
  '''Chooses the averate heart-rate from the estimates of 3 sensors. Avoid
  rates from sensors which are far way from the other ones.'''

  agreement = 3. #bpm

  non_zero = [k for k in average_rates if int(k)]

  if len(non_zero) == 0: return 0 #unknown!
  elif len(non_zero) == 1: return non_zero[0]
  elif len(non_zero) == 2:
    agree = abs(non_zero[0] - non_zero[1]) < agreement
    if agree: return numpy.mean(non_zero)
    else: #chooses the lowest
      return sorted(non_zero)[0]

  # else, there are 3 values and we must do a more complex heuristic

  r0_agrees_with_r1 = abs(average_rates[0] - average_rates[1]) < agreement
  r0_agrees_with_r2 = abs(average_rates[0] - average_rates[2]) < agreement
  r1_agrees_with_r2 = abs(average_rates[1] - average_rates[2]) < agreement

  if r0_agrees_with_r1:
    if r1_agrees_with_r2: #all 3 agree
      return numpy.mean(average_rates)
    else: #exclude r2
      return numpy.mean(average_rates[:2])
  else:
    if r1_agrees_with_r2: #exclude r0
      return numpy.mean(average_rates[1:])
    else: #no agreement at all pick mid-way
      return sorted(average_rates)[1]

  if r1_agrees_with_r2:
    if r0_agrees_with_r1: #all 3 agree
      return numpy.mean(average_rates)
    else: #exclude r0
      return numpy.mean(average_rates[1:])
  else:
    if r0_agrees_with_r1: #exclude r2
      return numpy.mean(average_rates[:2])
    else: #no agreement at all pick middle way
      return sorted(average_rates)[1]


def annotate_video(video, annotations, output, thickness=3,
        color=(255, 0, 0)):
  '''Annotates the input video with the detected bounding boxes'''

  directory = os.path.dirname(output)
  if not os.path.exists(directory): os.makedirs(directory)

  writer = bob.io.video.writer(output, height=video.height, width=video.width,
          framerate=video.frame_rate, codec=video.codec_name)
  for k, frame in enumerate(video):
    bb = annotations.get(k)
    if bb is not None:
      for t in range(thickness):
        bob.ip.draw.box(frame, bb.topleft, bb.size, color)
    writer.append(frame)
  del writer


def explain_heartrate(obj, dbdir, output):
  '''Explains why the currently chosen heart-rate is what it is'''

  import matplotlib
  matplotlib.use('agg')
  import matplotlib.pyplot as plt
  from matplotlib.backends.backend_pdf import PdfPages

  directory = os.path.dirname(output)
  if not os.path.exists(directory): os.makedirs(directory)

  # plots
  estimates = []
  pp = PdfPages(output)
  for k, channel in enumerate(('EXG1', 'EXG2', 'EXG3')):
    plt.figure(figsize=(12,4))
    signal, freq = bdf_load_signal(obj.make_path(dbdir), channel)
    avg_hr, peaks = plot_signal(signal, freq, channel)
    estimates.append(avg_hr)
    pp.savefig()
  estimated = chooser(estimates)
  pp.close()
