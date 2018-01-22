import os
from datetime import date

import sphinx_py3doc_enhanced_theme
from pkg_resources import get_distribution

release = get_distribution('tox3').version

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.extlinks',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode',
              'sphinxarg.ext',
              'sphinx_autodoc_typehints']

project = u'tox3'
version = release

author = 'Bernat Gabor'
year = date.today().year
copyright = u'2017-{}, {}'.format(year, author)

master_doc = 'index'
source_suffix = '.rst'

pygments_style = 'sphinx'

html_theme = "theme"
html_theme_path = [sphinx_py3doc_enhanced_theme.get_html_theme_path(), "."]
html_theme_options = {
    'githuburl': 'https://github.com/gaborbernat/tox3',
    'appendcss': '',
}

html_logo = 'theme/static/tox.png'
html_favicon = 'theme/static/toxfavi.ico'

tls_cacerts = os.getenv('SSL_CERT_FILE')  # we don't care here about the validity of certificates
linkcheck_timeout = 30

intersphinx_mapping = {'https://docs.python.org/3': None}
autoclass_content = 'class'
autodoc_default_flags = ["members", "undoc-members", "inherited-members"]


def process_sig(app, what, name, obj, options, signature, return_annotation):
    return '', return_annotation


def setup(app):
    app.connect("autodoc-process-signature", process_sig)
