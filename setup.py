#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='aura-flightdata',
      version='1.0',
      description='Flight data management libs',
      author='Curtis L. Olson',
      author_email='curtolson@flightgear.org',
      url='https://github.com/AuraUAS',
      package_dir = {'': 'src'},
      packages = find_packages('src'),
     )
