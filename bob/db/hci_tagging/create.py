#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Sep 12:39:50 CEST 2015

"""A script to scan database directories and create a concise CSV descriptor"""

import os
import fnmatch
import bob.io.video


def estimate_duration(video):
  """Estimates the duration of a video clip using Bob"""

  v = bob.io.video.reader(video)
  return int(v.duration/float(10**6)) #returns in seconds


def scan(args):
  """Scans the given base directory for the database information to retrieve

  Yields:

    Dictionaries, each with the following fields:

      'basedir' (str): The base directory of the sample
      'bdf' (str): The stem of the BDF file from its base directory
      'video' (str): The stem of the video file from its base directory
      'duration' (int): The estimated duration of the video file in seconds

  """

  for dirpath, dirs, files in os.walk(args.basedir):
    bdf = fnmatch.filter(files, '*.bdf')
    video = fnmatch.filter(files, '*C1 trigger*.avi')

    if bdf and video: #interesting directory, yield a new dictionary
      if args.verbose:
        print("Adding BDF file `%s'..." % os.path.join(args.basedir, bdf[0]))

      yield {
              'basedir': os.path.relpath(dirpath, args.basedir),
              'bdf': os.path.splitext(bdf[0])[0],
              'video': os.path.splitext(video[0])[0],
              'duration': estimate_duration(os.path.join(dirpath, video[0])),
              }


def create(args):
  """Creates or re-creates this database"""

  from . import LOCATION

  if os.path.exists(LOCATION) and not args.recreate:
    print("CSV descriptor exists at `%s' and --recreate was not set" % LOCATION)
    return 1

  if os.path.exists(LOCATION): os.unlink(LOCATION)

  import csv
  with open(LOCATION, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, ('basedir','bdf','video','duration'),
            delimiter=',')
    writer.writeheader()
    counter = 0
    for row in scan(args):
      writer.writerow(row)
      counter += 1

    if args.verbose:
      print("Added %d items to metadata file `%s'" % (counter, LOCATION))

  return 0


def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', default=False,
      help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', default=0,
      help="Do operations in a verbose way")
  parser.add_argument('-D', '--basedir', action='store',
      default='/idiap/resource/database/HCI_Tagging',
      metavar='DIR',
      help="Change the relative path to the directory containing the root of the HCI-Tagging database (defaults to %(default)s)")

  parser.set_defaults(func=create) #action
