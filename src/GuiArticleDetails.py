import gtk

class GuiArticleDetails:
	def __init__(self):
		self.nodeinformationwindow = gtk.Window()
		self.nodeinformationwindow.set_size_request(200, 200)
		self.text = gtk.TextView()
		self.nodeinformationwindow.add(self.text)
		self.text.show()
		self.nodeinformationwindow.show()
	
	def updateArticleInformation(self, url, article = None, graph = None):
		try:
			author = article["AU"]
			year = article["PY"]
			title = article["TI"]
			nreferences = article["NR"]
			nreferencesInGraph = graph.in_degree(url)
			ncitations = article["TC"]
			ncitationsInGraph = graph.out_degree(url)
			self.text.get_buffer().insert_at_cursor('%s\n' % url)
			self.text.get_buffer().insert_at_cursor('%s\n' % author)
			self.text.get_buffer().insert_at_cursor('%s\n' % year)
			self.text.get_buffer().insert_at_cursor('%s\n' % title)
			self.text.get_buffer().insert_at_cursor('Number of references: %s (%s)\n' % (nreferences, nreferencesInGraph))
			self.text.get_buffer().insert_at_cursor('Times cited: %s (%s)\n' % (ncitations, ncitationsInGraph))
		except:
			self.text.get_buffer().insert_at_cursor('%s\n' % url)
			
		try:
			self.text.get_buffer().insert_at_cursor('%s\n' % article["Journal"])
		except:
			pass



def main():
	gad = GuiArticleDetails()
	gtk.main()

if __name__ == "__main__":
	main()
