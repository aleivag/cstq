import pytest
from cstq.obj2cst import str2node
import libcst.matchers as m


@pytest.mark.parametrize(
    "expr,val", 
    [
        ("from foo import bar",  m.ImportFrom()),
        ("import foo, bars",  m.Import()),
        ("class Foo(Bar):...",  m.ClassDef()),
        ("def Foo(Bar):...",  m.FunctionDef()),
        ("foo(barr)",  m.Call()),
        ("1+1",  m.BinaryOperation()),
        ("X=Y",  m.Assign()),
        ("X==Y",  m.Comparison()),
        ("True",  m.Name("True")),
        ("[]",  m.List()),
        ("{}",  m.Dict()),
    ]
)
def test_exp_val(expr, val):
    assert m.matches(str2node(expr) , val)
