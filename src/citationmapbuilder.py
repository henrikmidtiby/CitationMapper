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
import WebOfKnowledgeParser
import ScopusParser
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

    def parsefile(self, filename):
        parser = WebOfKnowledgeParser.WebOfKnowledgeParser()
        #parser = ScopusParser.ScopusParser()
        parser.parsefile(filename)
        
        for articleKey in parser.articles.keys():
            article = parser.articles[articleKey]
            if not type(article.year) is types.IntType:
                print("Year is not a number")
            self.articles[article.id] = article
            self.graph.add_node(article.id)
            self.idsAndYears[article.id] = int(article.year)
            print("nodeid %s out" % article.id)
            halt = 1 == 2
            for reference in article.references:
                self.graph.add_edge(reference, article.id)
                print("nodeid %s in" % reference)
                halt = 1 == 1
            if(halt):
                #return
                pass
                
        #for node in self.graph.nodes():
        #    print node

    def analyzeGraph(self):
        self.graphForAnalysis = self.graph.copy()
        # Extract node parameters
        self.outdegrees = self.graphForAnalysis.out_degree()
        self.indegrees = self.graphForAnalysis.in_degree()

    def cleanUpGraph(self, minNumberOfReferences = 1, minNumberOfCitations = 3):
        # Only keep articles that cite others (ie we have full information about them)
        for key in self.outdegrees:
            if self.outdegrees[key] < minNumberOfCitations:
                self.graphForAnalysis.remove_node(key)

        # Only keep articles that are cited by others
        for key in self.indegrees:
            if self.graphForAnalysis.has_node(key) and self.indegrees[key] < minNumberOfReferences:
                self.graphForAnalysis.remove_node(key)

    def getYearsAndArticles(self):
        
        years = {}
        for elem in self.graphForAnalysis.nodes():
            try:
                curYear = self.idsAndYears[elem]
                if not curYear in years.keys():
                    years[curYear] = []
                years[curYear].append(elem)
            except KeyError:
                print "getYearsAndArticles - KeyError - \'%s\''" % elem
                
        print years
        return years

    def outputGraph(self, stream, direction = "TD"):
        self.outputPreamble(stream, direction)
        self.outputYearNodesAndMarkObjectsWithTheSameRank(stream)
        self.outputNodeInformation(stream)
        self.outputEdges(stream)
        self.outputPostamble(stream)

    def outputYearNodesAndMarkObjectsWithTheSameRank(self, stream):
        years = self.getYearsAndArticles()
        yeartags = years.keys()
        yeartags.sort()
        for year in yeartags:
            stream.write('y%s [fontsize="10", height="0.1668", label="%s", margin="0", rank="%s", shape="plaintext", width="0.398147893333333"]\n' % (year, year, year))
        for index in range(len(yeartags) - 1):
            stream.write("y%s -> y%s [arrowhead=\"normal\", arrowtail=\"none\", color=\"white\", style=\"invis\"];\n" % (yeartags[index], yeartags[index + 1]))

        for year in yeartags:
            yearElements = ""
            for element in years[year]:
                yearElements = "%s \"%s\"" % (yearElements, element)
            stream.write("{rank=same; y%s %s}\n" % (year, yearElements))

    def outputNodeInformation(self, stream):
        for key in self.graphForAnalysis.nodes():
            color = "#0000ff"
            firstauthor = key
            try:
                ncites = self.articles[key].ncites
                ncitesingraph = self.graph.out_degree(key)
                if 0.95 * ncites < ncitesingraph:
                    color = "#00ff00"
                else:
                    color = "#ff0000"
            except(KeyError):
                print("outputNodeInformation: KeyError: %s" % key)
                pass

            nodesize = math.sqrt((self.outdegrees[key] + 1) / 75.)
            fontsize = math.sqrt(self.outdegrees[key] + 1)*2
            stream.write('"%s" [URL="%s", height="%f", label="%s", fontsize="%f", style=filled, color="%s"]\n' % (key, key, nodesize, firstauthor, fontsize, color))

    def createLabelFromCRLine(self, crline):
        authorYearPattern = re.compile("^(.*?,\s?\d{4})")
        res = authorYearPattern.match(crline)
        if(res):
            #print(res.group(1))
            return res.group(1)
        print crline
        return crline

    def outputEdges(self, stream):
        for edge in self.graphForAnalysis.edges():
            stream.write("\"%s\" -> \"%s\"\n" % edge)

    def outputPreamble(self, stream, direction = "TD"):
        stream.write("digraph citations {\n")
        stream.write("graph [rankdir=%s];\n" % direction)
        stream.write("ranksep=0.2;\n")
        stream.write("nodesep=0.1;\n")
        stream.write('size="11.0729166666667,5.26041666666667";\n')
        stream.write("ratio=\"fill\"\n")
        stream.write("node [fixedsize=\"true\", fontsize=\"9\", shape=\"circle\"];\n")
        stream.write('edge [arrowhead="none", arrowsize="0.6", arrowtail="normal"];\n')

    def outputPostamble(self, stream):
        stream.write("}")

    def removeNamedNodes(self, excludedNodeNames):
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

    if(len(sys.argv) > 1):
        for arg in sys.argv:
            cmb.parsefile(str(arg))
        cmb.analyzeGraph()
        cmb.cleanUpGraph()
        cmb.outputGraph(output)

        temp = output.getvalue()

        print(temp)

if __name__ == '__main__':
    main()



