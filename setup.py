"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['zipperscript.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True, 'excludes': ['']}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    version="4.0.4"
)
