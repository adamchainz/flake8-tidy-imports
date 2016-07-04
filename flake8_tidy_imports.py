# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ast

__author__ = 'Adam Johnson'
__email__ = 'me@adamj.eu'
__version__ = '1.0.2'


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
        parser.add_option(
            '--banned-modules', default='', action='store',
            help="A map of modules to ban to the error messages to display "
                 "in the error."
        )

        if hasattr(parser, 'config_options'):  # for flake8 < 3.0
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
    message_I201 = "I201 Banned module '{name}' imported - {msg}."

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
            module_names = [node.module]
            for alias in node.names:
                module_names.append('{}.{}'.format(node.module, alias.name))
        else:
            return

        for module_name in module_names:

            if module_name in self.banned_modules:
                message = self.message_I201.format(
                    name=module_name,
                    msg=self.banned_modules[module_name]
                )
                yield (
                    node.lineno,
                    node.col_offset,
                    message,
                    type(self)
                )
