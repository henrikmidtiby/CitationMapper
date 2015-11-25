#-------------------------------------------------------------------------------
# Name:        citationmapbuilder
# Purpose:     Library that builds citation networks based on files from
#              isiknowledge.
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
import sys
import networkx
import math
import StringIO
import pprint
import ArticleWithReferences
import WebOfKnowledgeParser
#import ScopusParser
import types


class citationmapbuilder:
    def __init__(self):
        self.graph = networkx.DiGraph()
        self.graphForAnalysis = self.graph.copy()
        self.articles = {}
        self.outdegrees = None
        self.indegrees = None
        self.idsAndYears = {}
        self.idsAndCRLines = {}

    def parse_file(self, filename):
        parser = WebOfKnowledgeParser.WebOfKnowledgeParser()
        # parser = ScopusParser.ScopusParser()
        parser.parsefile(filename)

        for articleKey in parser.articles.keys():
            article = parser.articles[articleKey]
            self.add_article_to_graph(article)

    def add_article_to_graph(self, article):
        """

        Args:
            article (ArticleWithReferences.ArticleWithReferences):
        """
        if not type(article.year) is types.IntType:
            print("Year is not a number")

        # not in the database already.
        if (article.origin == "PrimaryRecord"):
            self.articles[article.id] = article
        elif (not self.articles.has_key(article.id)):
            self.articles[article.id] = article
        self.articles[article.id] = article
        self.graph.add_node(article.id)
        self.idsAndYears[article.id] = int(article.year)
        halt = 1 == 2
        for reference in article.references:
            self.graph.add_edge(reference, article.id)
            halt = 1 == 1
        if (halt):
            # return
            pass

            # for node in self.graph.nodes():
            #    print node

    def analyze_graph(self):
        self.graphForAnalysis = self.graph.copy()
        # Extract node parameters
        self.outdegrees = self.graphForAnalysis.out_degree()
        self.indegrees = self.graphForAnalysis.in_degree()

    def clean_up_graph(self, minNumberOfReferences=1, minNumberOfCitations=3):
        # Only keep articles that cite others (ie we have full information about them)
        for key in self.outdegrees:
            if self.outdegrees[key] < minNumberOfCitations:
                self.graphForAnalysis.remove_node(key)

        # Only keep articles that are cited by others
        for key in self.indegrees:
            if self.graphForAnalysis.has_node(
                    key) and self.indegrees[key] < minNumberOfReferences:
                self.graphForAnalysis.remove_node(key)

    def get_years_and_articles(self):
        years = {}
        for elem in self.graphForAnalysis.nodes():
            try:
                curYear = self.idsAndYears[elem]
                if not curYear in years.keys():
                    years[curYear] = []
                years[curYear].append(elem)
            except KeyError:
                print "get_years_and_articles - KeyError - \'%s\''" % elem

        print years
        return years

    def output_graph(self, stream, direction="TD"):
        self.output_preamble(stream, direction)
        self.output_year_nodes_and_mark_objects_with_the_same_rank(stream)
        self.output_node_information(stream)
        self.output_edges(stream)
        self.output_postamble(stream)

    def output_year_nodes_and_mark_objects_with_the_same_rank(self, stream):
        years = self.get_years_and_articles()
        yeartags = years.keys()
        yeartags.sort()
        for year in yeartags:
            stream.write(
                'y%s [fontsize="10", height="0.1668", label="%s", margin="0", rank="%s", shape="plaintext", width="0.398147893333333"]\n'
                % (year, year, year))
        for index in range(len(yeartags) - 1):
            stream.write(
                "y%s -> y%s [arrowhead=\"normal\", arrowtail=\"none\", color=\"white\", style=\"invis\"];\n"
                % (yeartags[index], yeartags[index + 1]))

        for year in yeartags:
            yearElements = ""
            for element in years[year]:
                yearElements = "%s \"%s\"" % (yearElements, element)
            stream.write("{rank=same; y%s %s}\n" % (year, yearElements))

    def output_node_information(self, stream):
        for key in self.graphForAnalysis.nodes():
            color = "#0000ff"
            labelOnGraph = key
            try:
                ncites = self.articles[key].ncites
                ncitesingraph = self.graph.out_degree(key)
                labelOnGraph = self.articles[key].firstAuthor
                if 0.95 * ncites < ncitesingraph:
                    color = "#00ff00"
                else:
                    color = "#ff0000"
            except (KeyError):
                print("output_node_information: KeyError: %s" % key)
                pass

            nodesize = math.sqrt((self.outdegrees[key] + 1) / 75.)
            fontsize = math.sqrt(self.outdegrees[key] + 1) * 2
            stream.write(
                '"%s" [URL="%s", height="%f", label="%s", fontsize="%f", style=filled, color="%s"]\n'
                % (key, key, nodesize, labelOnGraph, fontsize, color))

    def create_label_from_cr_line(self, crline):
        authorYearPattern = re.compile("^(.*?,\s?\d{4})")
        res = authorYearPattern.match(crline)
        if (res):
            return res.group(1)
        print crline
        return crline

    def output_edges(self, stream):
        for edge in self.graphForAnalysis.edges():
            stream.write("\"%s\" -> \"%s\"\n" % edge)

    def output_preamble(self, stream, direction="TD"):
        stream.write("digraph citations {\n")
        stream.write("graph [rankdir=%s];\n" % direction)
        stream.write("ranksep=0.2;\n")
        stream.write("nodesep=0.1;\n")
        stream.write('size="11.0729166666667,5.26041666666667";\n')
        stream.write("ratio=\"fill\"\n")
        stream.write(
            "node [fixedsize=\"true\", fontsize=\"9\", shape=\"circle\"];\n")
        stream.write(
            'edge [arrowhead="none", arrowsize="0.6", arrowtail="normal"];\n')

    def output_postamble(self, stream):
        stream.write("}")

    def remove_named_nodes(self, excludedNodeNames):
        print("len(excludedNodeNames) = %d" % len(excludedNodeNames))
        for key in excludedNodeNames:
            try:
                self.graphForAnalysis.remove_node(key)
            except networkx.NetworkXError as KE:
                #print("NetworkXError: %s" % KE)
                pass
        print("left nodes: %d" % len(self.graphForAnalysis.nodes()))


def main():
    output = StringIO.StringIO()
    cmb = citationmapbuilder()

    if len(sys.argv) > 1:
        for arg in sys.argv:
            cmb.parse_file(str(arg))
        cmb.analyze_graph()
        cmb.clean_up_graph()
        cmb.output_graph(output)

        temp = output.getvalue()

        print(temp)


if __name__ == '__main__':
    main()
