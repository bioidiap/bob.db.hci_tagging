#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Sep 2015 12:08:31 CEST

"""Commands
"""

import os
import sys
import pkg_resources

import numpy

import bob.io.base
import bob.db.base
from bob.db.base.driver import Interface as BaseInterface

DATABASE_LOCATION = '/idiap/resource/database/HCI_Tagging'


# Driver API
# ==========

def dumplist(args):
  """Dumps lists of files on the database, inputs your arguments"""

  from . import Database
  db = Database()

  objects = db.objects()

  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  for obj in objects:
    output.write('%s\n' % (obj.make_path(directory=args.directory, extension=args.extension),))

  return 0


def create_meta(args):
  """Runs the face detection, heart-rate estimation, save outputs at package"""


  from . import Database
  db = Database()

  objects = db.objects()
  if args.selftest:
    objects = objects[:5]

  basedir = pkg_resources.resource_filename(__name__, 'data')

  for obj in objects:
    try:
      max_faces = 0
      if args.selftest: max_faces = 2
      detections = obj.run_face_detector(args.directory, max_faces)
      quality = []
      arr = []
      for k in sorted(detections.keys()):
        det = detections[k]
        quality.append(det['quality'])
        bb = det['boundingbox']
        arr.append([k, bb.topleft[1], bb.topleft[0], bb.size[1], bb.size[0]])
      output = obj.make_path(basedir, '.hdf5')
      outdir = os.path.dirname(output)
      if not os.path.exists(outdir): os.makedirs(outdir)
      h5 = bob.io.base.HDF5File(output, 'w')
      h5.set('detections', numpy.array(arr))
      h5.set_attribute('quality', numpy.array(quality))
      h5.set_attribute('heartrate_bpm',
              obj.estimate_heartrate_in_bpm(args.directory))
      h5.close()
    finally:
      if args.selftest:
        if os.path.exists(basedir):
          import shutil
          shutil.rmtree(basedir)

  return 0


def checkfiles(args):
  """Checks the existence of the files based on your criteria"""

  from . import Database
  db = Database()

  objects = db.objects()

  # go through all files, check if they are available on the filesystem
  good = []
  bad = []
  for obj in objects:
    if os.path.exists(obj.make_path(directory=args.directory, extension=args.extension)): good.append(obj)
    else: bad.append(obj)

  # report
  output = sys.stdout
  if args.selftest:
    from bob.db.base.utils import null
    output = null()

  if bad:
    for obj in bad:
      output.write('Cannot find file "%s"\n' % (obj.make_path(directory=args.directory, extension=args.extension),))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(objects), args.directory))

  return 0


class Interface(BaseInterface):

  def name(self):
    return 'hci_tagging'

  def files(self):
    from . import LOCATION
    return [LOCATION]

  def version(self):
    import pkg_resources
    return pkg_resources.require('bob.db.%s' % self.name())[0].version

  def type(self):
    return 'text'

  def add_commands(self, parser):
    """Add specific subcommands that the action "dumplist" can use"""

    from . import __doc__ as docs

    subparsers = self.setup_parser(parser, "Mahnob HCI-Tagging dataset", docs)

    # get the "create" action from a submodule
    from .create import add_command as create_command
    create_command(subparsers)

    from argparse import SUPPRESS

    # add the dumplist command
    dump_message = "Dumps list of files based on your criteria"
    dump_parser = subparsers.add_parser('dumplist', help=dump_message)
    dump_parser.add_argument('-d', '--directory', dest="directory", default=DATABASE_LOCATION, help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    dump_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
    dump_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    dump_parser.set_defaults(func=dumplist) #action

    # add the checkfiles command
    check_message = "Check if the files exist, based on your criteria"
    check_parser = subparsers.add_parser('checkfiles', help=check_message)
    check_parser.add_argument('-d', '--directory', dest="directory", default=DATABASE_LOCATION, help="if given, this path will be prepended to every entry returned (defaults to '%(default)s')")
    check_parser.add_argument('-e', '--extension', dest="extension", default='', help="if given, this extension will be appended to every entry returned (defaults to '%(default)s')")
    check_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    check_parser.set_defaults(func=checkfiles) #action

    # add the create_meta command
    meta_message = create_meta.__doc__
    meta_parser = subparsers.add_parser('mkmeta', help=create_meta.__doc__)
    meta_parser.add_argument('-d', '--directory', dest="directory", default=DATABASE_LOCATION, help="This path points to the location where the database raw files are installed (defaults to '%(default)s')")
    meta_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    meta_parser.set_defaults(func=create_meta) #action
