import os
import sys
from datetime import date
from pkg_resources import get_distribution

release = get_distribution('tox3').version

extensions = []

project = u'tox'
version = release

author = 'Bernat gABOR'
year = date.today().year
copyright = u'2017-{}, {}'.format(year, author)

master_doc = 'index'
source_suffix = '.rst'


pygments_style = 'sphinx'
html_theme = 'alabaster'
html_logo = 'img/tox.png'
html_favicon = 'img/toxfavi.ico'

tls_cacerts = os.getenv('SSL_CERT_FILE')  # we don't care here about the validity of certificates
linkcheck_timeout = 30