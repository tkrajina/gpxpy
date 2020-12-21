# Documentation build configuration file
import sys
from os.path import abspath, dirname, join

DOCS_DIR = abspath(dirname(__file__))
PROJECT_DIR = dirname(DOCS_DIR)
PACKAGE_DIR = join(PROJECT_DIR, 'gpxpy')

# Add project path so we can import our package
sys.path.insert(0, PROJECT_DIR)
import gpxpy

# General information about the project.
project = 'gpxpy'
copyright = '2020, Tomo Krajina'
needs_sphinx = '3.0'
master_doc = 'index'
source_suffix = ['.rst', '.md']
version = release = gpxpy.__version__
html_static_path = ['_static']
templates_path = ['_templates']

# Exclude the generated gpxpy.rst, which will just contain top-level __init__ info
exclude_patterns = ['_build', 'modules/gpxpy.rst']

# Sphinx extension modules
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.apidoc',
    'm2r2',
]

# Use sphinx-apidoc to auto-generate rst sources
# Configured here instead of instead of in Makefile so it will be used by ReadTheDocs
apidoc_module_dir = PACKAGE_DIR
apidoc_output_dir = 'modules'
apidoc_module_first = True
apidoc_separate_modules = True
apidoc_toc_file = False

# Move type hint info to function description instead of signature
autodoc_typehints = 'description'
set_type_checking_flag = True

# HTML theme settings
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
