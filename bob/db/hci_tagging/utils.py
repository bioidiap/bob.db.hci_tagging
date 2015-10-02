#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Thu  1 Oct 11:00:44 CEST 2015

'''Utilities for Remote Photo-Plethysmography Benchmarking'''

import numpy
import bob.ip.facedetect
import antispoofing.utils.faceloc
from mne.preprocessing.ecg import qrs_detector


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


def plot_signal(s, sampling_frequency):
  '''Estimates the heart rate taking as base the input signal and its sampling
  frequency, plots QRS peaks discovered on the base signal.

  This method will use the Pam-Tompkins detector available the MNE package to
  clean-up and estimate the heart-beat frequency based on the ECG sensor
  information provided.

  Returns:

    float: The estimated average heart-rate in beats-per-minute

  '''

  avg, peaks = estimate_average_heartrate(s, sampling_frequency)

  import matplotlib.pyplot as plt

  fig, ax = plt.subplots(1)
  fig.set_size_inches(18, 6, forward=True)

  ax.plot(numpy.arange(0, len(s)/sampling_frequency, 1/sampling_frequency),
          s, label='Raw signal');
  xmin, xmax, ymin, ymax = plt.axis()
  ax.vlines(peaks / sampling_frequency, ymin, ymax, colors='r', label='P-T QRS detector')
  plt.xlim(0, len(s)/sampling_frequency)
  plt.ylabel('uV')
  plt.xlabel('time (s)')
  plt.title('Average heart-rate = %d bpm' % avg)
  ax.grid(True)
  ax.legend(loc='best', fancybox=True, framealpha=0.5)
  plt.show()

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


def detect_faces_on_video(data):
  """Detect faces on a video sequence using bob.ip.facedetect"""

  detections = {}
  for k, frame in enumerate(data):
    bb, quality = bob.ip.facedetect.detect_single_face(frame)
    if quality > 20:
      detections[k] = antispoofing.utils.faceloc.BoundingBox(bb.topleft[1], bb.topleft[0], bb.size[1], bb.size[0])
  return detections
