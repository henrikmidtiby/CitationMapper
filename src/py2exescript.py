#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      hemi
#
# Created:     25-02-2011
# Copyright:   (c) hemi 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from distutils.core import setup
import py2exe

setup(
    name = 'CitationMapper',
    description = 'Citation mapper based on information from ISI knowledge.',
    version = '0.2',

    windows = [
                  {
                      'script': 'GuiMainWindow.py',
                  }
              ],

    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo, pango, pangocairo, atk, gtk, gobject, gio',

                  }
              },
	excludes = ["Tkconstants","Tkinter","tcl"],

    data_files=[
                   '../notes.txt'
               ]
)

