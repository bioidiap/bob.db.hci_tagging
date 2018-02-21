.. vim: set fileencoding=utf-8 :

.. _bob.db.hci_tagging:
=============================
 Manhob HCI-Tagging Database
=============================

This package contains an interface for the `Mahnob HCI-Tagging dataset`_
interface. It is presently used to benchmark and test Remote
Photo-Plethysmography algorithms at Idiap. This package only uses the colored
videos (from Camera 1, in AVI format) and the biological signals saved in BDF_
format.

If you decide to use this package, please consider citing `Bob`_, as a software
development environment and the authors of the dataset:

.. code-block:: tex

  @article{soleymani-2012,
    author={Soleymani, M. and Lichtenauer, J. and Pun, T. and Pantic, M.},
    journal={Affective Computing, IEEE Transactions on},
    title={A Multimodal Database for Affect Recognition and Implicit Tagging},
    year={2012},
    volume={3},
    number={1},
    pages={42-55},
    doi={10.1109/T-AFFC.2011.25},
    month=Jan,
    }


Dependencies
============

This package makes use of the following important external dependencies (aside
from Bob_):

  * mne_: For estimating the heart-rate in beats-per-minute using the
    Pam-Tompkins algorithm
  * Python-EDF_ tools: to read physiological sensor information out of BDF
    files


Development
===========

This package can, optionally, *automatically* annotate the following key
aspects of the Mahnob HCI-Tagging dataset:

  * Average heart-rate in beats-per-minute (BPM), using the Pam-Tompkins
    algorithm as implemented by `mne`_.
  * Face bounding boxes, as detected by the default detector on
    `bob.ip.facedetect`_.

.. warning::

   Note this procedure is **outdated** by current metadata which is already
   shipped with this package. Only use it in case you know what you're doing
   and/or want to modify/re-evaluate this package's metadata.

   For it to work properly, you'll need to modify the method
   :py:meth:`bob.db.hci_tagging.File.load_face_detection` to take it into
   account. As of today, it is set to load face detections from the HDF5 files
   distributed with this package.


The annotation procedure can be launched with the following command::

  $ bob_dbmanage.py hci_tagging mkmeta


Each video, which is composed of a significant number of frames (hundreds),
takes about 5 minutes to get completely processed. If are at Idiap, you can
launch the job on the SGE queue using the following command-line::

  $ jman sub -q q1d --io-big -t 3490 `which bob_dbmanage.py` hci_tagging mkmeta



API
===


.. automodule:: bob.db.hci_tagging


.. Your references go here

.. _bob: https://www.idiap.ch/software/bob
.. _mahnob hci-tagging dataset: http://mahnob-db.eu/hci-tagging/
.. _bdf: http://www.biosemi.com/faq/file_format.htm
.. _bob.ip.facedetect: https://pypi.python.org/pypi/bob.ip.facedetect
.. _mne: https://pypi.python.org/pypi/mne
.. _python-edf: https://bitbucket.org/cleemesser/python-edf/
