# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import ast

__author__ = 'Adam Johnson'
__email__ = 'me@adamj.eu'
__version__ = '1.0.0'


class ImportChecker(object):
    """
    Flake8 plugin to make your import statements tidier.
    """
    name = 'flake8-tidy-imports'
    version = __version__

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

    message_I200 = "I200 Unnecessary import alias - rewrite as '{}'."

    def run(self):
        for node in ast.walk(self.tree):
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
