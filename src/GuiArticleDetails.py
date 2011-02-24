import gtk

class GuiArticleDetails:
	def __init__(self):
		self.nodeinformationwindow = gtk.Window()
		self.nodeinformationwindow.set_title("Article details")
		self.nodeinformationwindow.set_size_request(500, 200)
		self.text = gtk.TextView()
		self.generateNodeScrolledWindow()
		self.nodescrolledwindow.show_all()
		self.nodeinformationwindow.add(self.nodescrolledwindow)
		self.nodeinformationwindow.show()

	def generateNodeScrolledWindow(self):
		self.nodescrolledwindow = gtk.ScrolledWindow()
		self.nodescrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.nodescrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.nodescrolledwindow.add(self.text)
	
	def updateArticleInformation(self, url, article = None, graph = None):

		try:
			author = self.getListOfAuthors(article["AU"])
			year = article["PY"]
			title = article["TI"]
			page = article["BP"]
			journal = article["SO"]
			nreferences = article["NR"]
			nreferencesInGraph = graph.in_degree(url)
			ncitations = article["TC"]
			ncitationsInGraph = graph.out_degree(url)
			self.text.get_buffer().insert_at_cursor('%s\n' % url)
			self.text.get_buffer().insert_at_cursor('%s\n' % author)
			self.text.get_buffer().insert_at_cursor('%s\n' % year)
			self.text.get_buffer().insert_at_cursor('%s\n' % journal)
			self.text.get_buffer().insert_at_cursor('%s\n' % page)
			self.text.get_buffer().insert_at_cursor('%s\n' % title)
			self.text.get_buffer().insert_at_cursor('Number of references: %s (%s)\n' % (nreferences, nreferencesInGraph))
			self.text.get_buffer().insert_at_cursor('Times cited: %s (%s)\n' % (ncitations, ncitationsInGraph))
		except:
			self.text.get_buffer().insert_at_cursor('%s\n' % url)
			
		try:
			self.text.get_buffer().insert_at_cursor('%s\n' % article["Journal"])
		except:
			pass
	def getListOfAuthors(self, authors):
		if(len(authors) == 1):
			return authors[0]
		else:
			outstring = authors[0]
			for author in authors[1:]:
				outstring = outstring + " and " + author
			return outstring



def main():
	gad = GuiArticleDetails()
	gtk.main()

if __name__ == "__main__":
	main()
