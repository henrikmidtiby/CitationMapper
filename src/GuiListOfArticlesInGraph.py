import gtk
import networkx

class GuiListOfArticlesInGraph:
	def __init__(self):
		self.nodewindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.nodewindow.set_title("List of nodes")
		self.nodewindow.set_size_request(200, 200)
		self.generateNodesTreeStore()
		self.generateNodesTreeView()
		self.generateNodeScrolledWindow()
		vbox = gtk.VBox(False, 0)
		self.nodewindow.add(vbox)
		exportlistofnodesbutton = gtk.Button("Export list of nodes")
		exportlistofnodesbutton.connect("clicked", self.exportListOfNodes, None)
		exportlistofnodesbutton.show()
		vbox.pack_start(self.nodescrolledwindow, True, True, 0)
		vbox.pack_start(exportlistofnodesbutton, False, False, 0)
		self.nodescrolledwindow.show_all()
		self.nodewindow.show_all()

	def generateNodesTreeStore(self):
		# create a TreeStore with one string column to use as the model
		self.nodesTreestore = gtk.TreeStore(str, int, int, int)

		self.nodesTreestore.append(None, ["jeh", 1, 2, 3])
		self.nodesTreestore.append(None, ["ahej", 4, 22, 113])
		self.nodesTreestore.append(None, ["uha", 12, 12, 43])
		self.nodesTreestore.append(None, ["jgh", 11, 12, 3])
		self.nodesTreestore.append(None, ["hsej", 4, 122, 13])
		self.nodesTreestore.append(None, ["wha", 2, 12, 433])
		self.nodesTreestore.append(None, ["jeh", 1, 2, 3])
		self.nodesTreestore.append(None, ["ahej", 4, 22, 113])
		self.nodesTreestore.append(None, ["uha", 12, 12, 43])
		self.nodesTreestore.append(None, ["jgh", 11, 12, 3])
		self.nodesTreestore.append(None, ["hsej", 4, 122, 13])
		self.nodesTreestore.append(None, ["wha", 2, 12, 433])

	def generateNodesTreeView(self):
		tmsort = gtk.TreeModelSort(self.nodesTreestore) # produce a sortable treemodel
		self.nodesTreeview = gtk.TreeView(tmsort)
		self.nodesTreeview.connect("row-activated", self.row_clicked)

		column_names = ['ID', 'Year', 'Citations', 'References']

		self.tvcolumn = [None] * len(column_names)
		for n in range(0, len(column_names)):
			cell = gtk.CellRendererText()
			self.tvcolumn[n] = gtk.TreeViewColumn(column_names[n])
			self.tvcolumn[n].pack_start(cell, True)
			self.tvcolumn[n].add_attribute(cell, 'text', n)
			self.tvcolumn[n].set_sort_column_id(n)
			if n == 1:
				cell.set_property('xalign', 1.0)
			self.nodesTreeview.append_column(self.tvcolumn[n])

	def generateNodeScrolledWindow(self):
		self.nodescrolledwindow = gtk.ScrolledWindow()
		self.nodescrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.nodescrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.nodescrolledwindow.add(self.nodesTreeview)

	def row_clicked(self, widget, row, col):
		model = widget.get_model()
		text = "%s %d %d %d" % (model[row][0], model[row][1], model[row][2], model[row][3])
		print(text)

	def exportListOfNodes(self, temp = None, temp2 = None):
		pass

def main():
	loaig = GuiListOfArticlesInGraph()
	loaig.nodewindow.connect('destroy', gtk.main_quit)
	gtk.main()

if __name__ == '__main__':
	main()
