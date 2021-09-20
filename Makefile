run:
	pipenv run python src/CitationMapper.py inputfiles/case1/

test:
	cd src && python -m unittest discover -v -p "*Test.py"

exe: 
	cd src && /cygdrive/c/Python27/python.exe py2exescript.py py2exe

dist:
	rm -rf citationmapper
	mkdir citationmapper
	cp src/*.py citationmapper
	zip citationmapper.zip citationmapper/*
