import re
import sys
import networkx
import math
import StringIO
import pprint


class citationmapbuilder:
	def __init__(self):
		self.graph = networkx.DiGraph()
		self.graphForAnalysis = self.graph.copy()
		self.articles = {}

	def parsefile(self, filename):
		#print("<parsing alt=%s>" % filename)
		fh = open(filename)
		pattern = re.compile("^([A-Z][A-Z0-9]) (.*)")
		repeatedPattern = re.compile("^   (.*)")
		crPattern = re.compile("^.. (.*?, \d{4}, .*?, V\d+, P\d+)")
		erPattern = re.compile("^ER")
		state = 0	# Are we currently looking for cross references?
		crlines = []
		lastSeenCode = "XX"
		values = {}
		# Parse file line by line
		for line in fh:
			res = pattern.match(line)
			if(res):
				lastSeenCode = res.group(1)
				values[res.group(1)] = [res.group(2)]
				if(res.group(1) == "CR"):
					state = 1
				else:
					state = 0

			res = repeatedPattern.match(line)
			if(res):
				if(state == 1):
					newres = crPattern.match(line)
					if(newres):
						crlines.append(res.group(1))

				tempkey = lastSeenCode
				if(not tempkey in values):
					values[tempkey] = []
				values[tempkey].append(res.group(1))

			res = erPattern.match(line)
			if(res):
				#print("<nodes count=%d>" % len(self.graph.nodes()))
				rawIdentifier = self.formatIdentifier(values)
				identifier = self.newIdentifierInspiredByWos2Pajek(rawIdentifier)
				for line in crlines:
					crIdentifier = self.newIdentifierInspiredByWos2Pajek(line)
					self.graph.add_edge(crIdentifier, identifier)
					try:
						self.articles[crIdentifier]["Journal"] = line
					except KeyError:
						tempvalue = {}
						tempvalue["Journal"] = line
						self.articles[crIdentifier] = tempvalue

				self.articles[identifier] = values
				crlines = []
				values = {}
		#print("</parsing>")


	def newIdentifierInspiredByWos2Pajek(self, ident):
		# Basically ignore the abbreviated journal name

		# Match journal entries (Volume and page present)
		# VIENOT TC, 2007, LIB Q, V77, P157
		crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+), (P\d+)")
		res = crPattern.match(ident)
		if(res):
			# VIENOT TC,2007,V77,P157
			return "%s,%s,%s,%s" % (res.group(1), res.group(2), res.group(4), res.group(5))

		# Match book entries
		crPattern2 = re.compile("(.*?), (\d{4}), (.*?), (P\d+)")
		res = crPattern2.match(ident)
		if(res):
			return "%s,%s,%s" % (res.group(1), res.group(2), res.group(4))

		# Match cases with only volume and not page numbers
		# OLANDER B, 2007, INFORM RES, V12
		crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+)")
		res = crPattern.match(ident)
		if(res):
			# OLANDER B,2007,V12
			return "%s,%s,%s" % (res.group(1), res.group(2), res.group(4))

		# Match book entries
		# FRION P, 2009, P68
		crPattern2 = re.compile("(.*?), (\d{4}), (P\d+)")
		res = crPattern2.match(ident)
		if(res):
			# FRION P,2009,P68
			return "%s,%s,%s" % (res.group(1), res.group(2), res.group(3))
		return "ErrorInMatching %s" % ident


	def formatIdentifier(self, values):
		try:
			author = values["AU"][0].replace(",", "").upper()
			identString = author
			try:
				identString = "%s, %s" % (identString, values["PY"][0])
			except:
				pass
			try:
				identString = "%s, %s" % (identString, values["J9"][0])
			except:
				pass
			try:
				identString = "%s, V%s" % (identString, values["VL"][0])
			except:
				pass
			try:
				identString = "%s, P%s" % (identString, values["BP"][0])
			except:
				pass
			return(identString)
		except:
			logfile = open('logfile.txt', 'a')
			allKnowledgeAboutArticle = StringIO.StringIO()
			pp = pprint.PrettyPrinter(stream = allKnowledgeAboutArticle)
			pp.pprint(values)
			fullInfoAsText = allKnowledgeAboutArticle.getvalue()
			logfile.write(fullInfoAsText)
			return "Conversion error: %s %s %s" % (values["PT"][0], values["AU"][0], values["PY"][0])

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
		citationPattern = re.compile("^(.*?),(\d{4}),(V\d+),(P\d+)")
		for elem in self.graphForAnalysis.nodes():
			res = citationPattern.match(elem)
			if(res):
				curYear = res.group(2)
				if not curYear in years.keys():
					years[curYear] = []
				years[curYear].append(elem)
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
				ncites = int(self.articles[key]["TC"][0])
				ncitesingraph = self.graph.out_degree(key)
				if 0.95 * ncites < ncitesingraph:
					color = "#00ff00"
				else:
					color = "#ff0000"
				firstauthor = self.articles[key]["AU"][0]
			except:
				pass
			nodesize = math.sqrt((self.outdegrees[key] + 1) / 75.)
			fontsize = math.sqrt(self.outdegrees[key] + 1)*2
			stream.write('"%s" [URL="%s", height="%f", label="%s", fontsize="%f", style=filled, color="%s"]\n' % (key, key, nodesize, firstauthor, fontsize, color))

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



if __name__ == '__main__':

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




