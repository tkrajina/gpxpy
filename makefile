GIT_PORCELAIN_STATUS=$(shell git status --porcelain)

test: test-py2 test-py3 
	echo 'OK'
test-py3:
	python3 -m unittest test
test-py2:
	python -m unittest test
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
