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
import DoiLookup
import ArticleWithReferences


def open_url(widget, url):
    webbrowser.open(url)


# noinspection PyAttributeOutsideInit
class GuiArticleDetails:
    def __init__(self):
        self.doi = None
        self.nodescrolledwindow = None
        self.nodeinformationwindow = gtk.Window()
        self.nodeinformationwindow.set_title("Article details")
        self.nodeinformationwindow.set_size_request(500, 300)
        self.vbox = gtk.VBox(False, 0)
        self.add_link_button()
        self.add_text_area()
        self.generate_node_scrolled_window()
        self.nodescrolledwindow.show_all()
        self.add_request_doi_information_button()
        self.vbox.pack_start(self.nodescrolledwindow, True, True, 0)
        self.nodeinformationwindow.add(self.vbox)
        self.nodeinformationwindow.show_all()
        gtk.link_button_set_uri_hook(open_url)

    def add_link_button(self):
        self.link_label = gtk.LinkButton("http://www.sdu.dk",
                                         label="Locate article on Web of Science")
        self.vbox.pack_start(self.link_label, False, False, 0)

    def add_text_area(self):
        self.text = gtk.TextView()
        self.text.set_wrap_mode(gtk.WRAP_WORD)

    def add_request_doi_information_button(self):
        self.requestDOIInformation = gtk.Button(
            "Fetch more information based on DOI")
        self.requestDOIInformation.show()
        self.vbox.pack_start(self.requestDOIInformation, False, False, 5)
        self.requestDOIInformation.connect(
            "clicked", self.request_doi_information_callback, None)

    def request_doi_information_callback(self, p1, p2):
        text = DoiLookup.get_doi_information(self.doi)
        end_iterator = self.text.get_buffer().get_end_iter()
        self.text.get_buffer().insert(end_iterator, '\nDOI Information: \n')

        for k, v in text.items():
            end_iterator = self.text.get_buffer().get_end_iter()
            self.text.get_buffer().insert(end_iterator, "%-*s: %s\n" % (15, k, v))

        self.requestDOIInformation.hide()

    def generate_node_scrolled_window(self):
        self.nodescrolledwindow = gtk.ScrolledWindow()
        self.nodescrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.nodescrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.nodescrolledwindow.add(self.text)

    def update_article_information(self, url,
                                   citationmapbuild=None,
                                   article=None):
        print("update_article_information url = '%s'" % url)
        try:
            article = citationmapbuild.articles[url]
        except:
            print("Lookup failed")

        self.update_buttons(url)

        if isinstance(article, ArticleWithReferences.ArticleWithReferences):
            article = self.use_doi_information(article)
            self.text.get_buffer().insert_at_cursor('%s\n' % url)
            article.print_information()
            self.doi = article.doi
            self.text.get_buffer().insert_at_cursor('%d %s\n' % (int(article.year),  string.join(article.authors,  " and ")))
            if article.doi:
                self.text.get_buffer().insert_at_cursor('%s\n' % article.doi)
            self.text.get_buffer().insert_at_cursor('%s\n\n' % article.title)
            self.text.get_buffer().insert_at_cursor('%s\n\n' % article.origin)
            self.text.get_buffer().insert_at_cursor('%s\n\n' % article.abstract)
            self.text.get_buffer().insert_at_cursor('ncites: %d\n' % article.ncites)
            self.text.get_buffer().insert_at_cursor('%s\n' % article.references)

            self.insert_graph_information(article, citationmapbuild.graph)

            self.list_citation_of_current_article(url, citationmapbuild.graph)
            self.list_references_of_current_article(url, citationmapbuild.graph)

            full_info_as_text = self.get_all_information_as_text(article)
            self.text.get_buffer().insert_at_cursor(
                '\nAll available information:\n%s' % full_info_as_text)
            return
        else:
            print("Not an article")

    def use_doi_information(self, article):
        try:
            doi_information = DoiLookup.get_doi_information(article.doi)
            article.title = doi_information['title']
            article.journal = doi_information['container-title']
        except:
            pass
        return article

    def get_all_information_as_text(self, article):
        allKnowledgeAboutArticle = StringIO.StringIO()
        pp = pprint.PrettyPrinter(stream=allKnowledgeAboutArticle)
        pp.pprint(article)
        fullInfoAsText = allKnowledgeAboutArticle.getvalue()
        return fullInfoAsText

    def update_buttons(self, url):
        pattern = re.compile(".*DOI (.*)")
        res = pattern.match(url)
        if (res):
            print(res.group(1))
            self.update_doi_information(res.group(1))
        else:
            self.link_label.set_uri("http://google.com/#q=%s" % url)
            self.link_label.set_label("Google this article")
            self.requestDOIInformation.hide()
            print("Not found")

    def insert_graph_information(self, article, graph):
        nreferencesInGraph = graph.in_degree(article.id)
        ncitationsInGraph = graph.out_degree(article.id)
        self.text.get_buffer().insert_at_cursor(
            'Number of references in graph: %s\n' % nreferencesInGraph)
        self.text.get_buffer().insert_at_cursor(
            'Number of citations in graph: %s\n' % ncitationsInGraph)

    def list_citation_of_current_article(self, url, graph):
        listOfEdges = graph.out_edges(url)
        self.text.get_buffer().insert_at_cursor("\nCited by\n")
        for edge in listOfEdges:
            self.text.get_buffer().insert_at_cursor(" * %s\n" % edge[1])

    def list_references_of_current_article(self, url, graph):
        listOfEdges = graph.in_edges(url)
        self.text.get_buffer().insert_at_cursor("\nReferences\n")
        for edge in listOfEdges:
            self.text.get_buffer().insert_at_cursor(" * %s\n" % edge[0])

    def update_doi_information(self, doi):
        print("Updating doi information: %s" % doi)
        self.link_label.set_uri("http://dx.doi.org/%s" % doi)
        self.link_label.set_label("Open full text")
        self.doi = doi


def main():
    GuiArticleDetails()
    gtk.main()


if __name__ == "__main__":
    main()
