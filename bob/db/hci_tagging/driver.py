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

from . import utils

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

  if not args.force:
    raise RuntimeError("This method will re-write the internal HDF5 files, " \
        "which contain vital metadata used for generating results." \
        " Make sure this is what you want to do reading the API for this " \
        "package first (special attention to the method " \
        ":py:meth:`File.run_face_detector`).")

  from . import Database
  db = Database()

  objects = db.objects()
  if args.selftest:
    objects = objects[:5]
  if args.limit:
    objects = objects[:args.limit]

  if args.grid_count:
    print(len(objects))
    sys.exit(0)

  # if we are on a grid environment, just find what I have to process.
  if os.environ.has_key('SGE_TASK_ID'):
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(objects):
      raise RuntimeError("Grid request for job %d on a setup with %d jobs" % \
          (pos, len(objects)))
    objects = [objects[pos]]

  if args.selftest:
    basedir = pkg_resources.resource_filename(__name__, 'test-data')
  else:
    basedir = pkg_resources.resource_filename(__name__, 'data')

  for obj in objects:
    output = obj.make_path(basedir, '.hdf5')
    if os.path.exists(output) and not args.force:
      print("Skipping `%s' (meta file exists)" % obj.make_path())
      continue
    try:
      print("Creating meta data for `%s'..." % obj.make_path())
      bb = obj.run_face_detector(args.directory, max_frames=1)[0]
      hr = obj.estimate_heartrate_in_bpm(args.directory)
      if bb and hr:
        outdir = os.path.dirname(output)
        if not os.path.exists(outdir): os.makedirs(outdir)
        h5 = bob.io.base.HDF5File(output, 'a')
        h5.create_group('face_detector')
        h5.cd('face_detector')
        h5.set('topleft_x', bb.topleft[1])
        h5.set('topleft_y', bb.topleft[0])
        h5.set('width', bb.size[1])
        h5.set('height', bb.size[0])
        h5.cd('..')
        h5.set('heartrate', hr)
        h5.set_attribute('units', 'beats-per-minute', 'heartrate')
        h5.close()
      else:
        print("Skipping `%s': Missing Bounding box and/or Heart-rate" % (obj.stem,))
        print(" -> Bounding box: %s" % bb)
        print(" -> Heart-rate  : %s" % hr)

    except IOError as e:
      print("Skipping `%s': %s" % (obj.stem, str(e)))
      continue

    finally:
      if args.selftest:
        if os.path.exists(basedir):
          import shutil
          shutil.rmtree(basedir)

  return 0


def debug(args):
  """Debugs the face detection and heart-rate estimation"""


  from . import Database
  db = Database()

  objects = db.objects()
  if args.selftest:
    objects = objects[:5]
  if args.limit:
    objects = objects[:args.limit]

  if args.grid_count:
    print(len(objects))
    sys.exit(0)

  # if we are on a grid environment, just find what I have to process.
  if os.environ.has_key('SGE_TASK_ID'):
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(objects):
      raise RuntimeError("Grid request for job %d on a setup with %d jobs" % \
          (pos, len(objects)))
    objects = [objects[pos]]

  basedir = 'debug'

  for obj in objects:
    print("Creating debug data for `%s'..." % obj.make_path())
    try:

      detections = obj.run_face_detector(args.directory)
      # save annotated video file
      output = obj.make_path(args.output_directory, '.avi')
      print("Annotating video `%s'" % output)
      utils.annotate_video(obj.load_video(args.directory), detections, output)

      print("Annotating heart-rate `%s'" % output)
      output = obj.make_path(args.output_directory, '.pdf')
      utils.explain_heartrate(obj, args.directory, output)

    except IOError as e:
      print("Skipping `%s': %s" % (obj.stem, str(e)))
      continue

    finally:
      if args.selftest:
        if os.path.exists(args.output_directory):
          import shutil
          shutil.rmtree(args.output_directory)

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


def _files():
  filelist = pkg_resources.resource_filename(__name__, 'files.txt')
  return [k.strip() for k in open(filelist, 'rt').readlines() if k.strip()]


def upload(arguments):
  """Uploads generated metadata to the Idiap build server"""

  target_file = os.path.join(arguments.destination,
      arguments.name + ".tar.bz2")

  # check all files exist
  names = _files()
  paths = [pkg_resources.resource_filename(__name__, f) for f in names]
  for n,p in zip(names, paths):
    if not os.path.exists(p):
      raise IOError("Metadata file `%s' (path: %s) is not available. Did you run `mkmeta' before attempting to upload?" % (n, p))

  # if you get here, all files are there, ready to package
  print("Compressing metadata files to `%s'" % (target_file,))

  # compress
  import tarfile
  f = tarfile.open(target_file, 'w:bz2')
  for k,(n,p) in enumerate(zip(names, paths)):
    print("+ [%d/%d] %s" % (k+1, len(names), n))
    f.add(p, n)
  f.close()

  # set permissions for sane Idiap storage
  import stat
  perms = stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IROTH
  os.chmod(target_file, perms)


def download(arguments):
  """Downloads and uncompresses meta data generated files from Idiap"""

  # check all files don't exist
  names = _files()
  paths = [pkg_resources.resource_filename(__name__, f) for f in names]
  for n,p in zip(names, paths):
    if os.path.exists(p):
      if arguments.force:
        os.unlink(p)
      else:
        raise IOError("Metadata file `%s' (path: %s) is already available. Please remove self-generated files before attempting download or --force" % (n, p))

  # if you get here, all files aren't there, unpack
  source_url = os.path.join(arguments.source, arguments.name + ".tar.bz2")

  # download file from Idiap server, unpack and remove it
  import sys, tempfile, tarfile
  if sys.version_info[0] <= 2:
    import urllib2 as urllib
  else:
    import urllib.request as urllib

  try:
    print ("Extracting url `%s' (this may be long)..." %(source_url,))
    u = urllib.urlopen(source_url)
    f = tempfile.NamedTemporaryFile(suffix = ".tar.bz2")
    open(f.name, 'wb').write(u.read())
    t = tarfile.open(fileobj=f, mode='r:bz2')
    t.extractall(pkg_resources.resource_filename(__name__, ''))
    t.close()
    f.close()
    return False

  except Exception as e:
    print ("Error while downloading: %s" % e)
    return True



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
    meta_parser.add_argument('--grid-count', dest="grid_count", default=False, action='store_true', help=SUPPRESS)
    meta_parser.add_argument('--force', dest="force", default=False, action='store_true', help='If set, will overwrite existing meta files if they exist. Otherwise, just run on unexisting data')
    meta_parser.add_argument('--limit', dest="limit", default=0, type=int, help="Limits the number of objects to treat (defaults to '%(default)')")
    meta_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    meta_parser.set_defaults(func=create_meta) #action

    # debug
    debug_message = debug.__doc__
    debug_parser = subparsers.add_parser('debug', help=debug.__doc__)
    debug_parser.add_argument('-d', '--directory', dest="directory", default=DATABASE_LOCATION, help="This path points to the location where the database raw files are installed (defaults to '%(default)s')")
    debug_parser.add_argument('-o', '--output-directory', dest="output_directory", default='debug', help="This path points to the location where the debugging results will be stored (defaults to '%(default)s')")
    debug_parser.add_argument('--grid-count', dest="grid_count", default=False, action='store_true', help=SUPPRESS)
    debug_parser.add_argument('--limit', dest="limit", default=0, type=int, help="Limits the number of objects to treat (defaults to '%(default)')")
    debug_parser.add_argument('--self-test', dest="selftest", default=False, action='store_true', help=SUPPRESS)
    debug_parser.set_defaults(func=debug) #action

    # add upload command
    upload_meta = upload.__doc__
    upload_parser = subparsers.add_parser('upload', help=upload.__doc__)
    upload_parser.add_argument("--destination",
        default="/idiap/group/torch5spro/databases/latest")
    upload_parser.set_defaults(func=upload)

    # add download command
    if 'DOCSERVER' in os.environ: USE_SERVER=os.environ['DOCSERVER']
    else: USE_SERVER='https://www.idiap.ch'
    download_meta = download.__doc__
    download_parser = subparsers.add_parser('download',
        help=download.__doc__)
    download_parser.add_argument("--source",
            default="%s/software/bob/databases/latest/" % USE_SERVER)
    download_parser.add_argument("--force", action='store_true',
        help = "Overwrite existing metadata files?")
    download_parser.set_defaults(func=download)
