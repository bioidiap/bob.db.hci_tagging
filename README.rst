.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Wed 30 Sep 2015 11:03:49 CEST

===============================================
 Mahnob HCI-Tagging Database Interface for Bob
===============================================

This package contains an interface for the `Mahnob HCI-Tagging dataset`_
interface. It is presently used to benchmark and test Remote
Photo-Plethysmography algorithms at Idiap. This package only uses the colored
videos (from Camera 1, in AVI format) and the biological signals saved in BDF_
format.

If you decide to use this package, please consider citing `Bob`_, as a software
development environment and the authors of the dataset::

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


Installation
------------

To install this package -- alone or together with other `Packages of Bob
<https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation
Instructions <https://github.com/idiap/bob/wiki/Installation>`_.  For Bob_ to
be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies
<https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.


Dependencies
============

This package makes use of the following important external dependencies:

  * bob.ip.facedetect_: For automatically detecting faces using a boosted
    classifier based on LBPs
  * mne_: For estimating the heart-rate in beats-per-minute using the
    Pam-Tompkins algorithm
  * Python-EDF_ tools: to read physiological sensor information out of BDF
    files


Usage
-----

You can read videos and sensor information out of the database using the
provided API.


Annotations
===========

This package can, optionally, *automatically* annotate the following key
aspects of the Mahnob HCI-Tagging dataset:

  * Average heart-rate in beats-per-minute (BPM), using the Pam-Tompkins
    algorithm as implemented by `mne`_.
  * Face bounding boxes, as detected by the default detector on
    `bob.ip.facedetect`_.


The annotation procedure can be launched with the following command::

  $ ./bin/bob_dbmanage.py hci_tagging mkmeta


Each video, which is composed of a significant number of frames (hundreds),
takes about 5 minutes to get completely processed. If are at Idiap, you can
launch the job on the SGE queue using the following command-line::

  $ ./bin/jman sub -q q1d --io-big -t 3490 `pwd`/bin/bob_dbmanage.py hci_tagging mkmeta


.. Your references go here

.. _bob: https://www.idiap.ch/software/bob
.. _mahnob hci-tagging dataset: http://mahnob-db.eu/hci-tagging/
.. _bdf: http://www.biosemi.com/faq/file_format.htm
.. _bob.ip.facedetect: https://pypi.python.org/pypi/bob.ip.facedetect
.. _mne: https://pypi.python.org/pypi/mne
.. _python-edf: https://bitbucket.org/cleemesser/python-edf/
