import re
import sys
import networkx
import math
import StringIO


class citationmapbuilder:
	def __init__(self):
		self.elements = []
		self.graph = networkx.DiGraph()
		self.graphForAnalysis = self.graph.copy()
		self.articles = {}

	def parsefile(self, filename):
		fh = open(filename)
		pattern = re.compile("^([A-Z][A-Z0-9]) (.*)")
		crPattern = re.compile("^.. (.*?, \d{4}, .*?, V\d+, P\d+)")
		erPattern = re.compile("^ER")
		state = 0	# Are we currently looking for cross references?
		crlines = []
		values = {}
		for line in fh:
			res = pattern.match(line)
			if(res):
				values[res.group(1)] = res.group(2)
				if(res.group(1) == "CR"):
					state = 1
				else:
					state = 0
			if(state == 1):
				res = crPattern.match(line)
				if(res):
					crlines.append(res.group(1))

			res = erPattern.match(line)
			if(res):
				identifier = self.newIdentifierInspiredByWos2Pajek(self.formatIdentifier(values))
				self.elements.append(identifier)
				for line in crlines:
					self.elements.append(line)
					self.graph.add_edge(self.newIdentifierInspiredByWos2Pajek(line), identifier)
				self.articles[identifier] = values
				crlines = []
				values = {}


	def newIdentifierInspiredByWos2Pajek(self, ident):
		crPattern = re.compile("(.*?), (\d{4}), (.*?), (V\d+), (P\d+)")
		res = crPattern.match(ident)
		if(res):
			return "%s,%s,%s,%s" % (res.group(1), res.group(2), res.group(4), res.group(5))
		crPattern2 = re.compile("(.*?), (\d{4}), (.*?), (P\d+)")
		res = crPattern2.match(ident)
		if(res):
			return "%s,%s,%s" % (res.group(1), res.group(2), res.group(4))
		return "ErrorInMatching %s" % ident

		
	def formatIdentifier(self, values):
		try:
			author = values["AU"].replace(",", "").upper()
			if(values["PT"] == "J"):
				return "%s, %s, %s, V%s, P%s" % (author, values["PY"], values["J9"], values["VL"], values["BP"])
			return "%s, %s, %s, P%s" % (author, values["PY"], values["J9"], values["BP"])
		except:
			return "Conversion error: %s %s %s" % (values["PT"], values["AU"], values["PY"])

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

	def outputGraph(self, stream):
		self.outputPreamble(stream)
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
			try:
				ncites = int(self.articles[key]["TC"])
				ncitesingraph = self.graph.out_degree(key)
				print(ncites)
				print(ncitesingraph)
				if ncites == ncitesingraph:
					color = "#00ff00"
				else:
					color = "#ff0000"
			except:
				pass
			stream.write('"%s" [URL="%s", height="%f", label="%s", fontsize="%f", style=filled, color="%s"]\n' % (key, key, math.sqrt(self.outdegrees[key] / 75.), key[0:11], math.sqrt(self.outdegrees[key])*2, color))

	def outputEdges(self, stream):
		for edge in self.graphForAnalysis.edges():
			stream.write("\"%s\" -> \"%s\"\n" % edge)

	def outputPreamble(self, stream):
		stream.write("digraph citations {\n")
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




