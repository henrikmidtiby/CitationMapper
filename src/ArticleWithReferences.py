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

import re
import DoiLookup

class ArticleWithReferences:
    def __init__(self):
        self.id = None
        self.title = None
        self.journal = None
        self.year = 0
        self.firstAuthor = None
        self.authors = []
        self.doi = None
        self.references = []
        self.abstract = None
        self.ncites = 0
        self.origin = None

    def print_information(self):
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

    def retrieve_information_based_on_doi(self):
        pattern = re.compile('DOI (.*)')
        res = pattern.match(self.id)
        if res:
            try:
                doi = res.group(1)
                res = DoiLookup.get_doi_information(doi)
                self.get_title_from_doi(res)
                self.get_publication_year_from_doi(res)
                self.get_journal_from_doi(res)
                self.get_author_information_from_doi(res)
            except Exception as e:
                print("retrieve_information_based_on_doi - error: %s" % e)
        else:
            print("Doi lookup failed: %s" % self.id)

    def get_author_information_from_doi(self, res):
        try:
            self.firstAuthor = res['author'][0]['family'] + ", " + res['author'][0]['given']
            self.authors = []
            for author in res['author']:
                self.authors.append(author['family'] + ", " + author['given'])
        except:
            print(res)
            print("No author information available")

    def get_journal_from_doi(self, res):
        try:
            self.journal = res['container-title']
        except:
            print(res)
            print("No journal information available")

    def get_publication_year_from_doi(self, res):
        try:
            self.year = res['issued']['date-parts'][0][0]
        except:
            print(res)
            print("No publication year available")

    def get_title_from_doi(self, res):
        try:
            self.title = res['title']
        except:
            print(res)
            print("No title available")
