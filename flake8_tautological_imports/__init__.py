# -*- coding: utf-8 -*-
import ast

__author__ = 'Adam Johnson'
__email__ = 'me@adamj.eu'
__version__ = '1.0.0'


class ImportChecker(object):
    """
    Flake8 plugin to check import statements
    """
    name = 'flake8_tautological_imports'
    version = __version__

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

    def run(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                names = node.names[0]
                final_name = names.name.rsplit('.')[-1]
                asname = names.asname

                if final_name == asname:
                    yield (
                        node.lineno,
                        node.col_offset,
                        "Baaaaa",
                        type(self)
                    )
