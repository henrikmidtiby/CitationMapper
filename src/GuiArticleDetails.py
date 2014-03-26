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

def open_url(widget, url):
    webbrowser.open(url)

class GuiArticleDetails:
    def __init__(self):
        self.doi = None
        self.nodescrolledwindow = None
        self.nodeinformationwindow = gtk.Window()
        self.nodeinformationwindow.set_title("Article details")
        self.nodeinformationwindow.set_size_request(500, 200)
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

    def addRequestDOIInformationButton(self):
        self.requestDOIInformation = gtk.Button("Look up DOI")
        self.requestDOIInformation.show()
        self.vbox.pack_start(self.requestDOIInformation, False, False, 5)
        self.requestDOIInformation.connect("clicked", self.requestDOIInformationCallback, None)

    def requestDOIInformationCallback(self, p1, p2):
        text = DoiLookup.DoiLookup.getDOIInformation(self.doi)
        self.text.get_buffer().insert_at_cursor('\nDOI Information: \n')

        for k,v in text.items():
            self.text.get_buffer().insert_at_cursor('%s:\t%s\n' % (k, v))

    def generateNodeScrolledWindow(self):
        self.nodescrolledwindow = gtk.ScrolledWindow()
        self.nodescrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.nodescrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.nodescrolledwindow.add(self.text)

    def updateArticleInformation(self, url, article = None, graph = None):
        allKnowledgeAboutArticle = StringIO.StringIO()
        pp = pprint.PrettyPrinter(stream = allKnowledgeAboutArticle)
        pp.pprint(article)
        fullInfoAsText = allKnowledgeAboutArticle.getvalue()

        try:
            author = string.join(article["AU"], ' and ')
            title = string.join(article["TI"], " ")
            journal = article["SO"][0]
            nreferences = article["NR"][0]
            nreferencesInGraph = graph.in_degree(url)
            ncitations = article["TC"][0]
            ncitationsInGraph = graph.out_degree(url)
            self.text.get_buffer().insert_at_cursor('%s\n' % url)
            self.text.get_buffer().insert_at_cursor('\n')
            self.text.get_buffer().insert_at_cursor('%s\n' % title)
            self.text.get_buffer().insert_at_cursor('%s\n' % author)
            self.text.get_buffer().insert_at_cursor('%s\n' % journal)
            self.text.get_buffer().insert_at_cursor('\n')
            self.text.get_buffer().insert_at_cursor('Number of references: %s (%s)\n' % (nreferences, nreferencesInGraph))
            self.text.get_buffer().insert_at_cursor('Times cited: %s (%s)\n' % (ncitations, ncitationsInGraph))
            self.text.get_buffer().insert_at_cursor('\n')

            baseurl = "http://gateway.isiknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcApp=SFX&SrcAuth=SFX&DestApp=WOS&DestLinkType=GeneralSearchSummary"
            titlematch = "&title=%s" % title.replace(" ", "+")
            yearmatch = "&Period=Year+Selection&years=1985+1986+1987"
            searchurl = baseurl +  titlematch
            self.linklabel.set_uri(searchurl)

        except(KeyError):
            try:
                # BLUM H, 1978, PATTERN RECOGN, V10, P167, DOI 10.1016/0031-3203(78)90025-0
                pattern = re.compile(".*DOI (.*)")
                res = pattern.match(article["Journal"])
                if(res):
                    print(res.group(1))
                    self.linklabel.set_uri("http://dx.doi.org/%s" % res.group(1))
                    self.linklabel.set_label("Locate by DOI")
                    self.doi = res.group(1)
                else:
                    print("Not found")

                self.text.get_buffer().insert_at_cursor('%s\n' % article["Journal"])
                nreferencesInGraph = graph.in_degree(url)
                ncitationsInGraph = graph.out_degree(url)
                self.text.get_buffer().insert_at_cursor('Number of references in graph: %s\n' % nreferencesInGraph)
                self.text.get_buffer().insert_at_cursor('Number of citations in graph: %s\n' % ncitationsInGraph)

            except:
                print "Unexpected error:", sys.exc_info()[0]

        self.text.get_buffer().insert_at_cursor('\nAll available information:\n%s' % fullInfoAsText)

def main():
    GuiArticleDetails()
    gtk.main()

if __name__ == "__main__":
    main()
