from functools import partial, singledispatch

import libcst

from .obj2x import obj2x, str2xattr

obj2cst = obj2x(libcst)
str2attr = partial(str2xattr, x=libcst)


@singledispatch
def str2node(module: str):
    """
    If you give it a string, this funtion will try to produce the cst node thats representative of the string,
    unlike libcst.parse_statement that will produce the statement (sometimes SimpleStatementLine, and Expr).
    for instance

        str2node("foo()")

    will produce something like:

        Call(
            func=Name(
                value='foo',
            ),
            args=[],
        )



    """
    module = libcst.parse_module(module)
    assert len(module.body) == 1, "str must represent a single attribute"

    return str2node(module.body[0])


@str2node.register(libcst.SimpleStatementLine)
def _(node: libcst.SimpleStatementLine):
    return str2node(node.body[0])


@str2node.register(libcst.Expr)
def _(node: libcst.Expr):
    return str2node(node.value)


@str2node.register(libcst.CSTNode)
def _(node: libcst.CSTNode):
    return node
