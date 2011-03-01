import gtk

class GuiArticleContextMenu:
	def __init__(self):
		pass

	def hello(self, widget, data=None):
		print "hello"
		print data
		return False

	def showContextMenu(self, widget, data, event):
		menu = gtk.Menu()
		one = gtk.MenuItem("One")
		menu.append(one)
		submenu = gtk.Menu()
		two = gtk.MenuItem("Two")
		two.connect("activate", self.hello)
		submenu.append(two)
		one.set_submenu(submenu)
		three = gtk.MenuItem("Three")
		three.connect("activate", self.hello)
		menu.append(three)
		menu.show_all()
		menu.popup(None, None, None, event.button, event.get_time())
		return True
