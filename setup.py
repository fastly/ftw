#!/usr/bin/env python

from setuptools import setup

setup(name='ftw',
      version='1.0.2',
      description='Framework for Testing WAFs',
      author='Chaim Sanders, Zack Allen',
      author_email='zallen@fastly.com, chaim.sanders@gmail.com',
      url='https://www.github.com/fastly/ftw',
      download_url='https://github.com/fastly/ftw/tarball/1.0.2',
      entry_points = {
        'pytest11': [
            'ftw = ftw.pytest_plugin'
        ]
      },
      packages=['ftw'],
      keywords=['waf'],
      install_requires=[
          'IPy',
          'pytest=2.9.1',
          'PyYAML'
      ],
     )
