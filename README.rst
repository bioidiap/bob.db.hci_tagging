.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Wed 30 Sep 2015 11:03:49 CEST

===============================================
 Mahnob HCI-Tagging Database Interface for Bob
===============================================

This package contains an interface for the `Mahnob HCI-Tagging dataset`_
interface. It is presently used to benchmark and test Remote
Photo-Plethysmography algorithms. This package only uses the colored videos
(from Camera 1, in AVI format) and the biological signals saved in BDF_ format.

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


.. Your references go here

.. _bob: https://www.idiap.ch/software/bob
.. _mahnob hci-tagging dataset: http://mahnob-db.eu/hci-tagging/
.. _bdf: http://www.biosemi.com/faq/file_format.htm
