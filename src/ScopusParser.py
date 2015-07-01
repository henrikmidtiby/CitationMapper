#-------------------------------------------------------------------------------
# Name:        ScopyParser
# Purpose:     
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
import sys
import string
import ArticleWithReferences
import bibtexparser

class ScopusParser:
    def __init__(self):
        self.articles = {}

    def parsefile(self, filename):
        print("parsefile filename = %s",  filename)
        bibtex_file = open(filename)
        bibtex_str = bibtex_file.read()
        bib_database = bibtexparser.loads(bibtex_str)

        for bibtexArticle in bib_database.entries:
            #print(bibtexArticle['year'], bibtexArticle['author'])
            #print(bibtexArticle['title'])
            
            article = ArticleWithReferences.ArticleWithReferences()
            article.id = self.generateArticleID(bibtexArticle)
            try:
                article.title = bibtexArticle['title']
            except:
                print("No title information")
                article.title = "None given"
            article.year = int(bibtexArticle['year'])
            article.ncites = 0    # TODO
            try:
                article.abstract = bibtexArticle["abstract"]
            except(KeyError):
                article.abstract = None
            try:
                article.doi = bibtexArticle["doi"]
            except(KeyError):
                article.doi = None
            try:
                article.authors = [bibtexArticle["author"]]
            except(KeyError):
                article.authors = None
                
            try:
                references = bibtexArticle['references'].split('; ')
                for reference in references:
                    referenceArticle = self.generateReference(reference)
                    if(not referenceArticle.id in self.articles):
                        self.articles[referenceArticle.id] = referenceArticle
                    article.references.append(referenceArticle.id)

            except(KeyError):
                pass

            self.articles[article.id] = article
        
        print("Found %d articles." % len(self.articles))
        
    def generateArticleID(self, article):
        try:
            #authors = article['author'].replace(' and ',  ', ')
            #id = article['year'] + " " + authors + article['title']
            #id = article['year'] + " " + article['title']
            year = int(article['year'])
            firstAuthor = article['author'].split(',',  1)[0]
            pages = article['pages']
            #print("Year: %s" % year)
            #print("Firstauthor: %s" % firstAuthor)
            #print("Pages: '%s'" % pages)
            
            id = "%d %s %s" % (year, firstAuthor,  pages)
            #print("id: '%s'" % id)
        except KeyError as KE:
            print("<generateArticleID>")
            print sys.exc_info()[0]
            print("Could not find %s" % KE)
            #print article
            for key in article.keys():
                print key, 
            print
            id = "test"
            print("</generateArticleID>")
        return id
        
    def generateReference(self, reference):
           
        # Zwiggelaar, R., A review of spectral properties of plants and their potential use for crop/weed discrimination in row-crops (1998) Crop Prot., 17 (3), pp. 189-206
        pattern = re.compile("(.*) \((\d\d\d\d)\) (.*), (.*), pp. (.*)")
        res = pattern.match(reference)

        if(res):
            authorandtitle = res.group(1)
            values = authorandtitle.rsplit(', ',  1)
            if(len(values) == 2):
                authors = values[0]
                title = values[1]
            else:
                authors = ""
                title = "authorandtitle"
            firstAuthor = authorandtitle.split(',', 1)[0]
            year = int(res.group(2))
            journal = res.group(3)
            volumeandnumber = res.group(4)
            pages = res.group(5)
            #print(authorandtitle)
            #print(year)
            #print(remaining)
            try:
#                print("Authors: '%s'" % authors)
#                print("Firstauthor: '%s'" % firstAuthor)
#                print("Title: '%s'" % title)
#                print("Year: '%d'" % year)
#                print("Journal: '%s'" % journal)
#                print("Volume: '%s'" % volumeandnumber)
#                print("Pages: '%s'" % pages)
                id = "%d %s %s" % (year, firstAuthor,  pages)
            except:
                print("<generateReference>")
                print sys.exc_info()[0]
                id = "test"
                print("ID = %s", id)
                print("</generateReference>")                
        else:
            id = "test"
            year = 0

        referenceArticle = ArticleWithReferences.ArticleWithReferences()
        referenceArticle.id = id
        referenceArticle.year = year
        return referenceArticle


def main():
    cmb = ScopusParser()

    if(len(sys.argv) > 1):
        for arg in sys.argv:
            cmb.parsefile(str(arg))
            
    for articleKey in cmb.articles.keys():
        article = cmb.articles[articleKey]
        article.printInformation()
        break

if __name__ == '__main__':
    main()







