# Minimal makefile for Sphinx documentation
# Put help first so that "make" without arguments is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help all clean-apidoc Makefile

all: clean clean-apidoc html

clean-apidoc:
	rm -rf "./modules"

# Catch-all target: route all unknown targets to Sphinx builder
%: Makefile
	sphinx-build -M $@ . _build $(O)
