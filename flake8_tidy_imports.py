# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ast

import flake8

__author__ = 'Adam Johnson'
__email__ = 'me@adamj.eu'
__version__ = '1.0.6'


class ImportChecker(object):
    """
    Flake8 plugin to make your import statements tidier.
    """
    name = 'flake8-tidy-imports'
    version = __version__

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

    @classmethod
    def add_options(cls, parser):
        kwargs = {
            'action': 'store',
            'default': '',
            'help': "A map of modules to ban to the error messages to "
                    "display in the error.",
        }
        if flake8.__version__.startswith('3.'):
            kwargs['parse_from_config'] = True

        parser.add_option('--banned-modules', **kwargs)

        if flake8.__version__.startswith('2.'):
            parser.config_options.append('banned-modules')

    @classmethod
    def parse_options(cls, options):
        lines = [line.strip() for line in options.banned_modules.split('\n')
                 if line.strip()]
        cls.banned_modules = {}
        for line in lines:
            if '=' not in line:
                raise ValueError("'=' not found")
            module, message = line.split('=', 1)
            module = module.strip()
            message = message.strip()
            cls.banned_modules[module] = message

    message_I200 = "I200 Unnecessary import alias - rewrite as '{}'."
    message_I201 = "I201 Banned import '{name}' used - {msg}."

    def run(self):
        for node in ast.walk(self.tree):

            for rule in ('I200', 'I201'):
                for err in getattr(self, 'rule_{}'.format(rule))(node):
                    yield err

    def rule_I200(self, node):
        if isinstance(node, ast.Import):
            for alias in node.names:

                if '.' not in alias.name:
                    from_name = None
                    imported_name = alias.name
                else:
                    from_name, imported_name = alias.name.rsplit('.', 1)

                if imported_name == alias.asname:

                    if from_name:
                        rewritten = 'from {} import {}'.format(
                            from_name, imported_name
                        )
                    else:
                        rewritten = 'import {}'.format(imported_name)

                    yield (
                        node.lineno,
                        node.col_offset,
                        self.message_I200.format(rewritten),
                        type(self)
                    )
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == alias.asname:

                    rewritten = 'from {} import {}'.format(node.module, alias.name)

                    yield (
                        node.lineno,
                        node.col_offset,
                        self.message_I200.format(rewritten),
                        type(self)
                    )

    def rule_I201(self, node):
        if isinstance(node, ast.Import):
            module_names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            node_module = node.module or ''
            module_names = [node_module]
            for alias in node.names:
                module_names.append('{}.{}'.format(node_module, alias.name))
        else:
            return

        # Sort from most to least specific paths.
        module_names.sort(key=len, reverse=True)

        warned = set()

        for module_name in module_names:

            if module_name in self.banned_modules:
                message = self.message_I201.format(
                    name=module_name,
                    msg=self.banned_modules[module_name]
                )
                if any(mod.startswith(module_name) for mod in warned):
                    # Do not show an error for this line if we already showed
                    # a more specific error.
                    continue
                else:
                    warned.add(module_name)
                yield (
                    node.lineno,
                    node.col_offset,
                    message,
                    type(self)
                )
