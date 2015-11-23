#-------------------------------------------------------------------------------
# Name:        ArticleWithReferences
# Purpose:     Data structure for representing articles.
#
# Author:      Henrik Skov Midtiby
#
# Created:     2015-06-30
# Copyright:   (c) Henrik Skov Midtiby 2015
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
#
# Copyright 2015 Henrik Skov Midtiby
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


class ArticleWithReferences:
    def __init__(self):
        self.id = None
        self.title = None
        self.year = 0
        self.firstAuthor = None
        self.authors = []
        self.doi = None
        self.references = []
        self.abstract = None
        self.ncites = 0
        self.origin = None

    def printInformation(self):
        print("Article")
        print("id: %s" % self.id)
        print("doi: %s" % self.doi)
        print("Title: %s" % self.title)
        print("Year: %s" % self.year)
        print("First author: %s" % self.firstAuthor)
        print("Origin: %s" % self.origin)
        #print("Abstract: %s" % self.abstract)
        #print("References:")
        #for reference in self.references:
        #    print("  %s" % reference)
        print("\n")
