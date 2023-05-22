#!/usr/bin/env python

from setuptools import setup

setup(name='ftw',
      version='1.2.1',
      description='Framework for Testing WAFs',
      author='Chaim Sanders, Zack Allen',
      author_email='zma4580@gmail.com, chaim.sanders@gmail.com',
      url='https://www.github.com/fastly/ftw',
      download_url='https://github.com/fastly/ftw/tarball/1.2.0',
      entry_points = {
        'pytest11': [
            'ftw = ftw.pytest_plugin'
        ]
      },
      packages=['ftw'],
      keywords=['waf'],
      install_requires=[
          'astroid==1.4.5',
          'colorama==0.3.7',
          'IPy==0.83',
          'lazy-object-proxy==1.2.2',
          'py==1.4.31',
          'pylint==1.5.5',
          'pytest==2.9.1',
          'PyYAML==4.2b1',
          'requests==2.31.0',
          'six==1.10.0',
          'wrapt==1.10.8',
          'python-dateutil==2.6.0'
      ],
     )
