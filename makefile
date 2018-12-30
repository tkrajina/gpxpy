GIT_PORCELAIN_STATUS=$(shell git status --porcelain)

test: test-py2 test-py3 
	echo 'OK'
test-py3:
	python3 -m unittest test
test-py2:
	python -m unittest test
check-all-committed:
	if [ -n "$(GIT_PORCELAIN_STATUS)" ]; \
	then \
	    echo 'YOU HAVE UNCOMMITTED CHANGES'; \
	    git status; \
	    exit 1; \
	fi
pypi-upload: check-all-committed test
	rm -Rf dist/*
	python setup.py sdist
	twine upload dist/*
ctags:
	ctags -R .
clean:
	rm -Rf build
	rm -v -- $(shell find . -name "*.pyc")
	rm -Rf xsd
analyze-xsd:
	mkdir -p xsd
	test -f xsd/gpx1.1.xsd || wget http://www.topografix.com/gpx/1/1/gpx.xsd -O xsd/gpx1.1.xsd
	test -f xsd/gpx1.0.xsd || wget http://www.topografix.com/gpx/1/0/gpx.xsd -O xsd/gpx1.0.xsd
	cd xsd && python pretty_print_schemas.py
