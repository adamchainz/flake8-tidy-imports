from __future__ import annotations

import ast
from collections.abc import Callable, Iterable
from typing import Literal

IsBanned = Callable[[str], tuple[bool, str]]


class _Scope:
    def __init__(
        self,
        parent: _Scope | None,
        kind: Literal["module", "function", "class"],
    ) -> None:
        self.parent = parent
        self.kind = kind
        self.imports: dict[str, str] = {}
        self.suppressed: dict[str, set[str]] = {}
        self.shadowed: set[str] = set()

    def resolve(self, name: str) -> tuple[str, set[str]] | None:
        scope: _Scope | None = self
        first = True
        while scope is not None:
            if scope.kind == "class" and not first:
                scope = scope.parent
                continue
            if name in scope.shadowed:
                return None
            module = scope.imports.get(name)
            if module is not None:
                return module, scope.suppressed.get(name, set())
            scope = scope.parent
            first = False
        return None


class _ScopeCollector(ast.NodeVisitor):
    _NESTED_SCOPES = (
        ast.Lambda,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
    )

    def __init__(self, scope: _Scope, is_banned: IsBanned) -> None:
        self.scope = scope
        self.is_banned = is_banned

    def collect(self, nodes: Iterable[ast.AST]) -> None:
        for node in nodes:
            self.visit(node)

    def visit(self, node: ast.AST) -> None:
        if isinstance(node, self._NESTED_SCOPES):
            return
        super().visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.asname is None:
                local = alias.name.split(".", 1)[0]
                module = local
            else:
                local = alias.asname
                module = alias.name
            self._add_import(local, module, alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level:
            for alias in node.names:
                if alias.name != "*":
                    self.scope.shadowed.add(alias.asname or alias.name)
            return
        if node.module is None:
            return
        for alias in node.names:
            if alias.name == "*":
                continue
            local = alias.asname or alias.name
            imported = f"{node.module}.{alias.name}"
            self._add_import(local, imported, imported, node.module)

    def _add_import(
        self,
        local: str,
        module: str,
        imported_name: str,
        parent: str | None = None,
    ) -> None:
        if self.is_banned(imported_name)[0]:
            self.scope.suppressed.setdefault(local, set()).add(imported_name)
        elif parent is not None and self.is_banned(parent)[0]:
            self.scope.suppressed.setdefault(local, set()).add(parent)
        self.scope.imports[local] = module

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scope.shadowed.add(node.name)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.scope.shadowed.add(node.name)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scope.shadowed.add(node.name)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.scope.shadowed.add(node.id)

    def visit_arg(self, node: ast.arg) -> None:
        self.scope.shadowed.add(node.arg)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            self.scope.shadowed.add(node.name)
        self.generic_visit(node)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name is not None:
            self.scope.shadowed.add(node.name)
        self.generic_visit(node)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name is not None:
            self.scope.shadowed.add(node.name)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest is not None:
            self.scope.shadowed.add(node.rest)
        self.generic_visit(node)


class _AttributeVisitor(ast.NodeVisitor):
    def __init__(self, is_banned: IsBanned) -> None:
        self.is_banned = is_banned
        self.found: dict[ast.Attribute, str] = {}
        self.scope: _Scope | None = None

    def visit_Module(self, node: ast.Module) -> None:
        scope = _Scope(None, "module")
        _ScopeCollector(scope, self.is_banned).collect(node.body)
        self._visit_scope(node.body, scope)

    def _visit_scope(self, body: Iterable[ast.AST], scope: _Scope) -> None:
        previous = self.scope
        self.scope = scope
        for node in body:
            self.visit(node)
        self.scope = previous

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._visit_function_signature(node)
        scope = _Scope(self.scope, "function")
        scope.shadowed.update(_argument_names(node.args))
        _ScopeCollector(scope, self.is_banned).collect(node.body)
        self._visit_scope(node.body, scope)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._visit_arguments(node.args)
        scope = _Scope(self.scope, "function")
        scope.shadowed.update(_argument_names(node.args))
        _ScopeCollector(scope, self.is_banned).collect([node.body])
        self._visit_scope([node.body], scope)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)
        scope = _Scope(self.scope, "class")
        _ScopeCollector(scope, self.is_banned).collect(node.body)
        self._visit_scope(node.body, scope)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._visit_comprehension(node.generators, [node.elt])

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._visit_comprehension(node.generators, [node.elt])

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._visit_comprehension(node.generators, [node.key, node.value])

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._visit_comprehension(node.generators, [node.elt])

    def _visit_comprehension(
        self,
        generators: list[ast.comprehension],
        results: list[ast.expr],
    ) -> None:
        first = generators[0]
        self.visit(first.iter)
        scope = _Scope(self.scope, "function")
        previous = self.scope
        self.scope = scope
        for index, generator in enumerate(generators):
            if index:
                self.visit(generator.iter)
            _add_target_names(generator.target, scope)
            for condition in generator.ifs:
                self.visit(condition)
        for result in results:
            self.visit(result)
        self.scope = previous

    def visit_Attribute(self, node: ast.Attribute) -> None:
        name = self._resolve(node)
        if name is not None:
            self.found[node] = name
        if not isinstance(node.value, ast.Attribute):
            self.visit(node.value)

    def _resolve(self, node: ast.Attribute) -> str | None:
        parts: list[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if not isinstance(current, ast.Name):
            return None
        assert self.scope is not None
        binding = self.scope.resolve(current.id)
        if binding is None:
            return None

        module, suppressed = binding
        candidates = [module]
        full = module
        for part in reversed(parts):
            full = f"{full}.{part}"
            candidates.append(full)

        for candidate in reversed(candidates):
            if any(
                candidate == banned or candidate.startswith(f"{banned}.")
                for banned in suppressed
            ):
                return None
        for candidate in reversed(candidates):
            if self.is_banned(candidate)[0]:
                return candidate
        return None

    def _visit_function_signature(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        self._visit_arguments(node.args)
        if node.returns is not None:
            self.visit(node.returns)

    def _visit_arguments(self, args: ast.arguments) -> None:
        for arg in args.posonlyargs + args.args + args.kwonlyargs:
            if arg.annotation is not None:
                self.visit(arg.annotation)
        for default in args.defaults:
            self.visit(default)
        for kw_default in args.kw_defaults:
            if kw_default is not None:
                self.visit(kw_default)
        if args.vararg is not None and args.vararg.annotation is not None:
            self.visit(args.vararg.annotation)
        if args.kwarg is not None and args.kwarg.annotation is not None:
            self.visit(args.kwarg.annotation)


def _argument_names(args: ast.arguments) -> set[str]:
    names = {arg.arg for arg in args.posonlyargs + args.args + args.kwonlyargs}
    if args.vararg is not None:
        names.add(args.vararg.arg)
    if args.kwarg is not None:
        names.add(args.kwarg.arg)
    return names


def _add_target_names(target: ast.expr, scope: _Scope) -> None:
    if isinstance(target, ast.Name):
        scope.shadowed.add(target.id)
    elif isinstance(target, (ast.List, ast.Tuple)):
        for element in target.elts:
            _add_target_names(element, scope)
    elif isinstance(target, ast.Starred):
        _add_target_names(target.value, scope)


def find_banned_attribute_usages(
    tree: ast.AST, is_banned: IsBanned
) -> dict[ast.Attribute, str]:
    visitor = _AttributeVisitor(is_banned)
    visitor.visit(tree)
    return visitor.found
