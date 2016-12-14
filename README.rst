.. vim: set fileencoding=utf-8 :
.. Tue 13 Dec 18:31:43 CET 2016

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.db.hci_tagging/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bob/bob.db.hci_tagging/master/index.html
.. image:: https://gitlab.idiap.ch/bob/bob.db.hci_tagging/badges/v1.0.1/build.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.hci_tagging/commits/v1.0.1
.. image:: https://img.shields.io/badge/gitlab-project-0000c0.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.hci_tagging
.. image:: http://img.shields.io/pypi/v/bob.db.hci_tagging.png
   :target: https://pypi.python.org/pypi/bob.db.hci_tagging
.. image:: http://img.shields.io/pypi/dm/bob.db.hci_tagging.png
   :target: https://pypi.python.org/pypi/bob.db.hci_tagging


================================================
 Mahnob HCI-Tagging Database Access API for Bob
================================================

This package is part of the signal-processing and machine learning toolbox
Bob_. It contains an interface for the evaluation protocols of the `Mahnob
HCI-Tagging Dataset`_. Notice this package does not contain the raw data files
from this dataset, which need to be obtained through the link above.


Installation
------------

Follow our `installation`_ instructions. Then, using the Python interpreter
provided by the distribution, bootstrap and buildout this package::

  $ python bootstrap-buildout.py
  $ ./bin/buildout


Contact
-------

For questions or reporting issues to this software package, contact our
development `mailing list`_.


.. Place your references here:
.. _bob: https://www.idiap.ch/software/bob
.. _installation: https://www.idiap.ch/software/bob/install
.. _mailing list: https://www.idiap.ch/software/bob/discuss
.. _mahnob hci-tagging dataset: http://mahnob-db.eu/hci-tagging/
