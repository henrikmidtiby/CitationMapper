#-------------------------------------------------------------------------------
# Name:        citationmapbuilder
# Purpose:     Library that builds citation networks based on files from
#              isiknowledge.
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
import pprint
import re
import sys
import string
import io

import ArticleWithReferences


class WebOfKnowledgeParser:
    def __init__(self):
        self.articles = {}

    def parsefile(self, filename):
        print("<parsing alt=%s>" % filename)
        filehandle = open(filename)
        pattern = re.compile("^([A-Z][A-Z0-9]) (.*)")
        repeatedPattern = re.compile("^   (.*)")
        crPattern = re.compile("^.. (.*?, \d{4}, .*?, V\d+, P\d+)")
        erPattern = re.compile("^ER")
        state = 0  # Are we currently looking for cross references?
        crlines = []
        lastSeenCode = "XX"
        values = {}
        erCounter = 0
        # Parse file line by line
        for line in filehandle:
            res = pattern.match(line)
            if (res):
                lastSeenCode = res.group(1)
                values[res.group(1)] = [res.group(2)]
                if (res.group(1) == "CR"):
                    state = 1
                else:
                    state = 0

            res = repeatedPattern.match(line)
            if (res):
                if (state == 1):
                    newres = crPattern.match(line)
                    if (newres):
                        crlines.append(res.group(1))

                tempkey = lastSeenCode
                if (not tempkey in values):
                    values[tempkey] = []
                values[tempkey].append(res.group(1))

            res = erPattern.match(line)
            if (res):
                erCounter += 1
                rawIdentifier = self.formatIdentifier(values)
                identifier = self.newIdentifierInspiredByWos2Pajek(rawIdentifier)

                try:
                    article = ArticleWithReferences.ArticleWithReferences()
                    article.id = identifier
                    article.title = " ".join(values["TI"])
                    article.year = int(values["PY"][0])
                    article.ncites = int(values["TC"][0])
                    article.origin = "PrimaryRecord"
                    try:
                        article.abstract = " ".join(values["AB"])
                    except (KeyError):
                        article.abstract = None
                    try:
                        article.doi = values["DI"][0]
                    except (KeyError):
                        article.doi = None
                    try:
                        article.authors = values["AU"]
                        article.firstAuthor = values["AU"][0]
                    except (KeyError):
                        article.authors = None
                        article.firstAuthor = None

                    for cr_line in crlines:


                        referenceArticle = self.get_reference_article_from_cr_line(cr_line)
                        article.references.append(referenceArticle.id)
                        self.articles[referenceArticle.id] = referenceArticle

                    self.articles[identifier] = article

                except (KeyError):
                    print(values)

                crlines = []
                values = {}
        print("Analyzed %d entries." % erCounter)
        print("Found %d articles." % len(self.articles))
        #print("</parsing>")

    def get_reference_article_from_cr_line(self, cr_line):
        year = self.getYearFromIdentity(cr_line)
        crIdentifier = self.newIdentifierInspiredByWos2Pajek(cr_line)
        referenceArticle = ArticleWithReferences.ArticleWithReferences()
        referenceArticle.id = crIdentifier
        referenceArticle.year = year
        referenceArticle.firstAuthor = self.getAuthorFromIdentity(cr_line)
        referenceArticle.doi = self.get_doi_from_cr_line(cr_line)

        referenceArticle.origin = "ListedInCitations"
        return referenceArticle

    def get_doi_from_cr_line(self, cr_line):
        doi = None
        doiPattern = re.compile("^DOI (.*)")
        doiRes = doiPattern.match(cr_line)
        if(doiRes):
            doi = doiRes.group(1)
        return doi    

    def newIdentifierInspiredByWos2Pajek(self, ident):
        # Basically ignore the abbreviated journal name
        self.getYearFromIdentity(ident)

        pattern = re.compile(".*DOI (.*)")
        res = pattern.match(ident)
        if (res):
            return "DOI %s" % res.group(1)

        # Match journal entries (Volume and page present)
        # VIENOT TC, 2007, LIB Q, V77, P157
        crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+), (P\d+)")
        res = crPattern.match(ident)
        if (res):
            # VIENOT TC,2007,V77,P157
            return ("%s,%s,%s,%s" % (res.group(1), res.group(2), res.group(4),
                                     res.group(5))).upper()

        # Match book entries
        crPattern2 = re.compile("(.*?), (\d{4}), (.*?), (P\d+)")
        res = crPattern2.match(ident)
        if (res):
            return ("%s,%s,%s" %
                    (res.group(1), res.group(2), res.group(4))).upper()

        # Match cases with only volume and not page numbers
        # OLANDER B, 2007, INFORM RES, V12
        crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+)")
        res = crPattern.match(ident)
        if (res):
            # OLANDER B,2007,V12
            return ("%s,%s,%s" %
                    (res.group(1), res.group(2), res.group(4))).upper()

        # Match book entries
        # FRION P, 2009, P68
        crPattern2 = re.compile("(.*?), (\d{4}), (P\d+)")
        res = crPattern2.match(ident)
        if (res):
            # FRION P,2009,P68
            return ("%s,%s,%s" %
                    (res.group(1), res.group(2), res.group(3))).upper()

        # Match entries like
        # JACKSON MA, 2010, PROC FRONT EDUC CONF
        crPattern2 = re.compile("(.*?), (\d{4}), (.*)")
        res = crPattern2.match(ident)
        if (res):
            # JACKSON MA,2010,PROC FRONT EDUC CONF
            return ("%s,%s,%s" %
                    (res.group(1), res.group(2), res.group(3))).upper()

        # Match entries like
        # ANTON G, 2010
        crPattern2 = re.compile("(.*?), (\d{4})")
        res = crPattern2.match(ident)
        if (res):
            # ANTON G,2010
            return ("%s,%s" % (res.group(1), res.group(2))).upper()

        print("ErrorInMatching %s" % ident)
        return ident

    def getYearFromIdentity(self, ident):
        # type: (str) -> int
        # Match journal entries (Volume and page present)
        # VIENOT TC, 2007, LIB Q, V77, P157
        crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+), (P\d+)")
        res = crPattern.match(ident)
        if (res):
            # VIENOT TC,2007,V77,P157
            return int(res.group(2))

        # Match book entries
        crPattern2 = re.compile("(.*?), (\d{4}), (.*?), (P\d+)")
        res = crPattern2.match(ident)
        if (res):
            return int(res.group(2))

        # Match cases with only volume and not page numbers
        # OLANDER B, 2007, INFORM RES, V12
        crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+)")
        res = crPattern.match(ident)
        if (res):
            # OLANDER B,2007,V12
            return int(res.group(2))

        # Match book entries
        # FRION P, 2009, P68
        crPattern2 = re.compile("(.*?), (\d{4}), (P\d+)")
        res = crPattern2.match(ident)
        if (res):
            # FRION P,2009,P68
            return int(res.group(2))

        # Match entries like
        # JACKSON MA, 2010, PROC FRONT EDUC CONF
        crPattern2 = re.compile("(.*?), (\d{4}), (.*)")
        res = crPattern2.match(ident)
        if (res):
            # JACKSON MA,2010,PROC FRONT EDUC CONF
            return int(res.group(2))

        # Match entries like
        # ANTON G, 2010
        crPattern2 = re.compile("(.*?), (\d{4})")
        res = crPattern2.match(ident)
        if (res):
            # ANTON G,2010
            return int(res.group(2))

        try:
            return self.idsAndYears[ident]
        except KeyError:
            print("Could not determine year from %s" % ident)
            return -1
        except Exception as e:
            print("ident: ", ident)
            print(e)
            return -1

    def getAuthorFromIdentity(self, ident):
        # Match journal entries (Volume and page present)
        # VIENOT TC, 2007, LIB Q, V77, P157
        crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+), (P\d+)")
        res = crPattern.match(ident)
        if (res):
            # VIENOT TC,2007,V77,P157
            return res.group(1)

        # Match book entries
        crPattern2 = re.compile("(.*?), (\d{4}), (.*?), (P\d+)")
        res = crPattern2.match(ident)
        if (res):
            return res.group(1)

        # Match cases with only volume and not page numbers
        # OLANDER B, 2007, INFORM RES, V12
        crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+)")
        res = crPattern.match(ident)
        if (res):
            # OLANDER B,2007,V12
            return res.group(1)

        # Match book entries
        # FRION P, 2009, P68
        crPattern2 = re.compile("(.*?), (\d{4}), (P\d+)")
        res = crPattern2.match(ident)
        if (res):
            # FRION P,2009,P68
            return res.group(1)

        # Match entries like
        # JACKSON MA, 2010, PROC FRONT EDUC CONF
        crPattern2 = re.compile("(.*?), (\d{4}), (.*)")
        res = crPattern2.match(ident)
        if (res):
            # JACKSON MA,2010,PROC FRONT EDUC CONF
            return res.group(1)

        # Match entries like
        # ANTON G, 2010
        crPattern2 = re.compile("(.*?), (\d{4})")
        res = crPattern2.match(ident)
        if (res):
            # ANTON G,2010
            return res.group(1)

        print("Could not determine author from %s" % ident)
        return "No author found"

    def formatIdentifier(self, values):
        try:
            try:
                author = values["AU"][0].replace(",", "").upper()
                author = author.replace("'", "")
                identString = author
            except KeyError:
                identString = 'NoAuthorInformationWasPresent'
            try:
                identString = "%s, %s" % (identString, values["PY"][0])
            except KeyError:
                pass
            try:
                identString = "%s, %s" % (identString, values["J9"][0])
            except KeyError:
                pass
            try:
                identString = "%s, V%s" % (identString, values["VL"][0])
            except KeyError:
                pass
            try:
                identString = "%s, P%s" % (identString, values["BP"][0])
            except KeyError:
                pass
            try:
                identString = "%s, DOI %s" % (identString, values["DI"][0])
            except KeyError:
                pass
            return (identString)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            logfile = open('logfile.txt', 'a')
            allKnowledgeAboutArticle = io.StringIO()
            formattedValues = pprint.PrettyPrinter(
                stream=allKnowledgeAboutArticle)
            formattedValues.pprint(values)
            fullInfoAsText = allKnowledgeAboutArticle.getvalue()
            logfile.write(fullInfoAsText)
            return "Conversion error: %s %s %s" % (
                values["PT"][0], values["AU"][0], values["PY"][0])


def main():
    cmb = WebOfKnowledgeParser()

    if (len(sys.argv) > 1):
        for arg in sys.argv:
            cmb.parsefile(str(arg))

    for article in cmb.articles:
        article.print_information()
        break


if __name__ == '__main__':
    main()
