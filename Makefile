run:
	python src/GuiMainWindow.py data/

exe: 
	cd src && /cygdrive/c/Python27/python.exe py2exescript.py py2exe

dist:
	rm -rf citationmapper
	mkdir citationmapper
	cp src/*.py citationmapper
	zip citationmapper.zip citationmapper/*
