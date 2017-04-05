"""Logic related to generated a stream of unique symbols for macros to use.

Exposes this functionality as the `gen_sym` function.
"""

import ast

import macropy.core.macros
import macropy.core.util
import macropy.core.walkers



@macropy.core.util.register(macropy.core.macros.injected_vars)
def gen_sym(tree, **kw):
    """Create a generator that creates symbols which are not used in the given
    `tree`. This means they will be hygienic, i.e. it guarantees that they will
    not cause accidental shadowing, as long as the scope of the new symbol is
    limited to `tree` e.g. by a lambda expression or a function body"""
    @macropy.core.walkers.Walker
    def name_finder(tree, collect, **kw):
        if type(tree) is ast.Name:
            collect(tree.id)
        if type(tree) is ast.Import:
            names = [x.asname or x.name for x in tree.names]
            for name in names: collect(name)
        if type(tree) is ast.ImportFrom:
            names = [x.asname or x.name for x in tree.names]
            for name in names: collect(name)
        if type(tree) in (ast.FunctionDef, ast.ClassDef):
            collect(tree.name)

    found_names = set(name_finder.collect(tree))

    def name_for(name="sym"):

        if name not in found_names:
            found_names.add(name)
            return name
        offset = 1
        while name + str(offset) in found_names:

            offset += 1
        found_names.add(name + str(offset))
        return name + str(offset)
    return name_for

