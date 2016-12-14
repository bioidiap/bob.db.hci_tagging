#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements, find_packages
install_requires = load_requirements()

setup(

    name='bob.db.hci_tagging',
    version=open("version.txt").read().rstrip(),
    description='Mahnob HCI-Tagging Database Access API for Bob',
    keywords=['bob', 'database', 'manhob', 'hci-tagging'],
    url='https://gitlab.idiap.ch/bob/bob.db.cohface',
    license='BSD',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,

    entry_points = {
        'bob.db': [
            'hci_tagging = bob.db.hci_tagging.driver:Interface',
            ],
      },

    classifiers=[
      'Framework :: Bob',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],

    )
