#-------------------------------------------------------------------------------
# Name:        GuiArticleDetails
# Purpose:     Article details window for the citation mapper program
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-02-25
# Copyright:   (c) Henrik Skov Midtiby 2011
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
#
# Copyright 2011 Henrik Skov Midtiby
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
import gtk
import pprint
import StringIO
import string
import webbrowser
import sys
import DoiLookup
import ArticleWithReferences


def open_url(widget, url):
    webbrowser.open(url)


class GuiArticleDetails:
    def __init__(self):
        self.doi = None
        self.nodescrolledwindow = None
        self.nodeinformationwindow = gtk.Window()
        self.nodeinformationwindow.set_title("Article details")
        self.nodeinformationwindow.set_size_request(500, 300)
        self.vbox = gtk.VBox(False, 0)
        self.addLinkButton()
        self.addTextArea()
        self.generateNodeScrolledWindow()
        self.nodescrolledwindow.show_all()
        self.addRequestDOIInformationButton()
        self.vbox.pack_start(self.nodescrolledwindow, True, True, 0)
        self.nodeinformationwindow.add(self.vbox)
        self.nodeinformationwindow.show_all()
        gtk.link_button_set_uri_hook(open_url)

    def addLinkButton(self):
        self.linklabel = gtk.LinkButton("http://www.sdu.dk",
            label="Locate article on Web of Science")
        self.vbox.pack_start(self.linklabel, False, False, 0)

    def addTextArea(self):
        self.text = gtk.TextView()
        self.text.set_wrap_mode(gtk.WRAP_WORD)

    def addRequestDOIInformationButton(self):
        self.requestDOIInformation = gtk.Button(
            "Fetch more information based on DOI")
        self.requestDOIInformation.show()
        self.vbox.pack_start(self.requestDOIInformation, False, False, 5)
        self.requestDOIInformation.connect(
            "clicked", self.requestDOIInformationCallback, None)

    def requestDOIInformationCallback(self, p1, p2):
        text = DoiLookup.getDOIInformation(self.doi)
        endIter = self.text.get_buffer().get_end_iter()
        self.text.get_buffer().insert(endIter, '\nDOI Information: \n')

        for k, v in text.items():
            endIter = self.text.get_buffer().get_end_iter()
            self.text.get_buffer().insert(endIter, "%-*s: %s\n" % (15, k, v))

        self.requestDOIInformation.hide()

    def generateNodeScrolledWindow(self):
        self.nodescrolledwindow = gtk.ScrolledWindow()
        self.nodescrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.nodescrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.nodescrolledwindow.add(self.text)

    def updateArticleInformation(self, url,
                                 citationmapbuild=None,
                                 article=None):
        print("updateArticleInformation url = %s" % url)
        try:
            article = citationmapbuild.articles[url]
        except:
            print("Lookup failed")
        if (isinstance(article, ArticleWithReferences.ArticleWithReferences)):
            self.text.get_buffer().insert_at_cursor('%s\n' % url)
            article.printInformation()
            self.doi = article.doi
            self.text.get_buffer().insert_at_cursor('%d %s\n' % (int(article.year),  string.join(article.authors,  " and ")))
            if(article.doi):
                self.text.get_buffer().insert_at_cursor('%s\n' % article.doi)
            self.text.get_buffer().insert_at_cursor('%s\n\n' % article.title)
            self.text.get_buffer().insert_at_cursor('%s\n\n' % article.abstract)
            self.text.get_buffer().insert_at_cursor('ncites: %d\n' % article.ncites)
            self.text.get_buffer().insert_at_cursor('%s\n' % article.references)
            
            self.insertGraphInformation(article, citationmapbuild.graph)
            
            self.listCitationOfCurrentArticle(url,  citationmapbuild.graph)
            self.listReferencesOfCurrentArticle(url,  citationmapbuild.graph)

            return
        else:
            print("Not an article")

        fullInfoAsText = self.getAllInformationAsText(article)
        self.updateButtons(url)

        self.nodeinformationwindow.set_title("Article details - %s" % url)
        try:
            #self.insertDetailedArticleInformationIfAvailable(article, graph)
            pass
        except (KeyError):
            try:
                self.roughArticleInformation(article, graph)
            except:
                print "Unexpected error:", sys.exc_info()[0]
        except ():
            print "Other error", sys.exc_info()[0]

        self.text.get_buffer().insert_at_cursor(
            '\nAll available information:\n%s' % fullInfoAsText)
        self.listCitationOfCurrentArticle(url, graph)

    def getAllInformationAsText(self, article):
        allKnowledgeAboutArticle = StringIO.StringIO()
        pp = pprint.PrettyPrinter(stream=allKnowledgeAboutArticle)
        pp.pprint(article)
        fullInfoAsText = allKnowledgeAboutArticle.getvalue()
        return fullInfoAsText

    def updateButtons(self, url):
        pattern = re.compile(".*DOI (.*)")
        res = pattern.match(url)
        if (res):
            print(res.group(1))
            self.updateDOIInformation(res.group(1))
        else:
            self.linklabel.set_uri("http://google.com/#q=%s" % url)
            self.linklabel.set_label("Google this article")
            self.requestDOIInformation.hide()
            print("Not found")

    def insertDetailedArticleInformationIfAvailable(self, article, graph):
        nreferences = article["NR"][0]
        nreferencesInGraph = graph.in_degree(url)
        self.text.get_buffer().insert_at_cursor('\n')
        self.text.get_buffer().insert_at_cursor(
            'Number of references: %s (%s)\n' %
            (nreferences, nreferencesInGraph))

        ncitations = article["TC"][0]
        ncitationsInGraph = graph.out_degree(url)
        self.text.get_buffer().insert_at_cursor(
            'Times cited: %s (%s)\n' % (ncitations, ncitationsInGraph))
        self.text.get_buffer().insert_at_cursor('\n')

    def insertGraphInformation(self, article, graph):
        nreferencesInGraph = graph.in_degree(article.id)
        ncitationsInGraph = graph.out_degree(article.id)
        self.text.get_buffer().insert_at_cursor(
            'Number of references in graph: %s\n' % nreferencesInGraph)
        self.text.get_buffer().insert_at_cursor(
            'Number of citations in graph: %s\n' % ncitationsInGraph)

    def listCitationOfCurrentArticle(self, url, graph):
        listOfEdges = graph.out_edges(url)
        self.text.get_buffer().insert_at_cursor("\nCited by\n")
        for edge in listOfEdges:
            self.text.get_buffer().insert_at_cursor(" * %s\n" % edge[1])

    def listReferencesOfCurrentArticle(self, url, graph):
        listOfEdges = graph.in_edges(url)
        self.text.get_buffer().insert_at_cursor("\nReferences\n")
        for edge in listOfEdges:
            self.text.get_buffer().insert_at_cursor(" * %s\n" % edge[0])

    def updateDOIInformation(self, doi):
        print("Updating doi information: %s" % doi)
        self.linklabel.set_uri("http://dx.doi.org/%s" % doi)
        self.linklabel.set_label("Open full text")
        self.doi = doi


def main():
    GuiArticleDetails()
    gtk.main()


if __name__ == "__main__":
    main()
