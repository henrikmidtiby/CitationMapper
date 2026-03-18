run:
	uv run python src/CitationMapper.py inputfiles/case1/

test:
	cd src && uv run python -m unittest discover -v -p "*Test.py"

