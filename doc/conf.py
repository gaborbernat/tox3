import inspect
import os
from datetime import date

import sphinx_py3doc_enhanced_theme
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList
from pkg_resources import get_distribution
from sphinx.util import nested_parse_with_titles
from sphinx.util.docstrings import prepare_docstring
from sphinx_autodoc_typehints import format_annotation

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


class TableAutoClassDoc(Directive):
    has_content = True
    required_arguments = 1

    def run(self):
        of_class = self.arguments[0].split('.')
        class_type = getattr(__import__('.'.join(of_class[:-1]), fromlist=[of_class[-1]]), of_class[-1])

        def predicate(a):
            return isinstance(a, property)

        class_members = inspect.getmembers(class_type, predicate=predicate)
        return_types = [inspect.signature(p.fget).return_annotation for _, p in class_members]
        docs = [inspect.getdoc(p) or '' for _, p in class_members]

        table = nodes.table()
        t_group = nodes.tgroup(cols=4)

        t_group += nodes.colspec(colwidth=1)
        t_group += nodes.colspec(colwidth=1)
        t_group += nodes.colspec(colwidth=1)
        t_group += nodes.colspec(colwidth=10)

        # header
        t_group += nodes.thead('', nodes.row('', *[nodes.entry('', nodes.line(text=c)) for c in
                                                   ["field", "type", "note", "description"]]))

        # rows
        t_body = nodes.tbody()
        for (name, _), return_type, doc in zip(class_members, return_types, docs):
            doc_l = doc.split('\n')
            location = next((i for i in doc_l if i.startswith(':note:')), '')[len(':note:'):]
            doc_stripped = '\n'.join(i for i in doc_l if not i.startswith(':note:'))

            doc_stripped_view = ViewList(prepare_docstring(doc_stripped))
            doc_stripped_node = nodes.container()
            nested_parse_with_titles(self.state, doc_stripped_view, doc_stripped_node)

            return_type_view = ViewList(prepare_docstring(format_annotation(return_type)))
            return_type_node = nodes.container()
            nested_parse_with_titles(self.state, return_type_view, return_type_node)

            name_node = nodes.reference('',
                                        nodes.Text(name, name),
                                        refid='{}.{}'.format(self.arguments[0], name))
            t_body += nodes.row(name,
                                nodes.entry('', nodes.literal(text=name)),
                                nodes.entry('', return_type_node),
                                nodes.entry('', nodes.literal(text=location)),
                                nodes.entry('', doc_stripped_node))

        t_group += t_body
        table += t_group

        section = nodes.section(ids=[self.arguments[0]])
        section += nodes.title(self.arguments[0], self.arguments[0])

        return [section, table]


def setup(app):
    app.add_directive('auto_doc_class_table', TableAutoClassDoc)
