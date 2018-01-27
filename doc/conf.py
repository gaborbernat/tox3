import inspect
import os
from datetime import date
from itertools import chain

import sphinx_py3doc_enhanced_theme
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import unchanged
from docutils.statemachine import ViewList
from pkg_resources import get_distribution
from sphinx.util import nested_parse_with_titles
from sphinx.util.docstrings import prepare_docstring
from sphinx_autodoc_typehints import format_annotation
from sphinxarg.parser import parse_parser

release = get_distribution('toxn').version

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.extlinks',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode',
              'sphinxarg.ext',
              'sphinx_autodoc_typehints']

project = u'toxn'
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
    'githuburl': 'https://github.com/gaborbernat/toxn',
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
    required_arguments = 2

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

        t_body = nodes.tbody()
        for (name, _), return_type, doc in zip(class_members, return_types, docs):
            doc_l = doc.split('\n')
            location = next((i for i in doc_l if i.startswith(':note:')), '')[len(':note:'):]
            doc_stripped = '\n'.join(i for i in doc_l if not i.startswith(':note:'))

            doc_stripped_node = self.render_content(doc_stripped)
            return_type_node = self.render_content(format_annotation(return_type))

            ref_key = '{}.{}'.format(self.arguments[1], name)
            name_node = nodes.reference('', name, refid=ref_key)
            ref = nodes.paragraph('', '', name_node)

            t_body += nodes.row(name,
                                nodes.entry('', ref),
                                nodes.entry('', return_type_node),
                                nodes.entry('', nodes.literal(text=location)),
                                nodes.entry('', doc_stripped_node),
                                ids=[ref_key])

        t_group += t_body
        table += t_group

        return [table]

    def render_content(self, doc_stripped):
        doc_stripped_view = ViewList(prepare_docstring(doc_stripped))
        doc_stripped_node = nodes.container()
        nested_parse_with_titles(self.state, doc_stripped_view, doc_stripped_node)
        return doc_stripped_node


class Cli(Directive):
    has_content = True
    option_spec = dict(module=unchanged, func=unchanged,
                       prog=unchanged,
                       noepilog=unchanged, nodescription=unchanged, )

    def run(self):
        module_name, attr_name, prog = self.options['module'], self.options['func'], self.options['prog']
        parser = getattr(__import__(module_name, fromlist=[attr_name]), attr_name)()
        result = parse_parser(parser)

        table = nodes.table()
        t_group = nodes.tgroup(cols=4)

        t_group += nodes.colspec(colwidth=1.5)
        t_group += nodes.colspec(colwidth=1.5)
        t_group += nodes.colspec(colwidth=8)

        # header
        t_group += nodes.thead('', nodes.row('', *[nodes.entry('', nodes.line(text=c)) for c in
                                                   ["name", "default", "help"]]))

        # rows
        t_body = nodes.tbody()
        for option in chain.from_iterable(g['options'] for g in result['action_groups']):
            names, default, help_text, choice = option['name'], option['default'], option['help'], option.get('choices')

            refs, name_nodes = [], []
            ref = nodes.paragraph('', '')
            first = True
            for name in names:
                if not first:
                    ref.append(nodes.Text(', '))
                else:
                    first = False
                ref_key = '{} {}'.format(prog, name)
                ref_node = nodes.reference('', '', refid=ref_key)
                ref_node += nodes.literal(text=name)
                ref += ref_node
                refs.append(ref_key)

            help_body = nodes.paragraph('', '', nodes.Text(help_text))
            if choice is not None:
                help_body += nodes.Text('; one of: ')
                help_body += nodes.literal(text=', '.join(choice))

            if default is None:
                default_body = nodes.paragraph('', text='')
            else:
                if default and default[0] == '"' and default[-1] == '"':
                    default = default[1:-1]
                default_body = nodes.literal(text=default)

            t_body += nodes.row('',
                                nodes.entry('', ref),
                                nodes.entry('', default_body),
                                nodes.entry('', help_body),
                                ids=refs)

        t_group += t_body
        table += t_group

        return [nodes.literal_block(text=result['usage']),
                table]


def literal_data(rawtext, app, type, slug, options):
    """Create a link to a BitBucket resource."""
    of_class = type.split('.')
    data = getattr(__import__('.'.join(of_class[:-1]), fromlist=[of_class[-1]]), of_class[-1])
    return [nodes.literal('', text=','.join(data))], []


def setup(app):
    app.add_directive('auto_doc_class_table', TableAutoClassDoc)
    app.add_directive('table_cli', Cli)
    app.add_role('literal_data', literal_data)
