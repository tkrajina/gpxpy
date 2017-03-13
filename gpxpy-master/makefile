GIT_PORCELAIN_STATUS=$(shell git status --porcelain)

test: test-py2 test-py3 
	echo 'OK'
test-py3:
	python3 -m unittest test
	SAXCount -v=always -n -s -f validation_gpx10.gpx
	SAXCount -v=always -n -s -f validation_gpx11.gpx
	rm validation_gpx*gpx
test-py2:
	python -m unittest test
	SAXCount -v=always -n -s -f validation_gpx10.gpx
	SAXCount -v=always -n -s -f validation_gpx11.gpx
	rm validation_gpx*gpx
check-all-commited:
	if [ -n "$(GIT_PORCELAIN_STATUS)" ]; \
	then \
	    echo 'YOU HAVE UNCOMMITED CHANGES'; \
	    git status; \
	    exit 1; \
	fi
pypi-upload: test check-all-commited
	python setup.py register
	python setup.py sdist upload
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
