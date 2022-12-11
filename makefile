GIT_PORCELAIN_STATUS=$(shell git status --porcelain)

.PHONY: mypy-and-tests
mypy-and-tests: mypy run-gpxinfo test
	echo "Done"


.PHONY: run-gpxinfo
run-gpxinfo:
	./gpxinfo test_files/*gpx

.PHONY: test
test:
	python3 -m unittest test

.PHONY: check-all-committed
check-all-committed:
	if [ -n "$(GIT_PORCELAIN_STATUS)" ]; \
	then \
	    echo 'YOU HAVE UNCOMMITTED CHANGES'; \
	    git status; \
	    exit 1; \
	fi

.PHONY: pypi-upload
pypi-upload: check-all-committed test
	rm -Rf dist/*
	python3 -m build --help > /dev/null 2>&1 || python3 -m pip install build
	python3 -m build
	twine check dist/*
	twine upload dist/*

.PHONY: ctags
ctags:
	ctags -R .

.PHONY: clean
clean:
	-rm -R build
	-rm -v -- $(shell find . -name "*.pyc")
	-rm -R xsd

.PHONY: analyze-xsd
analyze-xsd:
	mkdir -p xsd
	test -f xsd/gpx1.1.xsd || wget -c http://www.topografix.com/gpx/1/1/gpx.xsd -O xsd/gpx1.1.xsd
	test -f xsd/gpx1.0.xsd || wget -c http://www.topografix.com/gpx/1/0/gpx.xsd -O xsd/gpx1.0.xsd
	cd xsd && python pretty_print_schemas.py

.PHONY: mypy
mypy:
	mypy --strict . gpxinfo