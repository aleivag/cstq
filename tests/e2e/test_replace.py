import libcst as cst
import libcst.matchers as m

from cstq import Query

MODULE = """
from foo import bar, baz
from f00 import b4r

one = 1

bar()
baz()
b4r("something")
bar()
baz()
""".strip()


def test_repalce_funtion():
    q = Query(MODULE)
    q.find_function_call(func_name="baz").parent().remove()
    assert (
        q.code()
        == """
from foo import bar, baz
from f00 import b4r

one = 1

bar()
b4r("something")
bar()
""".strip()
    )


def test_repalce_funtion_argument():
    q = Query(MODULE)
    q.find_function_call(func_name="b4r").args[0].value.change(value='"other"')
    assert (
        q.code()
        == """
from foo import bar, baz
from f00 import b4r

one = 1

bar()
baz()
b4r("other")
bar()
baz()
""".strip()
    )


def test_replace_funtion_argument_if_exists():
    q = Query(MODULE)
    fcall = q.find_function_call(func_name="bar").slice(0, 1)

    if len(fcall.args[:]) == 0:
        fcall.change(args=(cst.Arg(value=cst.Name(value="noargs")),))

    assert (
        q.code()
        == """
from foo import bar, baz
from f00 import b4r

one = 1

bar(noargs)
baz()
b4r("something")
bar()
baz()
""".strip()
    )


def test_remove_funct(simple_bzl):
    q = Query(simple_bzl)

    load_glob = q.search(
        m.Call(
            func=m.Name(value="load"),
            args=[
                m.Arg(value=m.SimpleString(value='"@tools//build_defs:glob_defs.bzl"')),
                m.ZeroOrMore(),
                m.Arg(value=m.SimpleString(value='"glob"')),
                m.ZeroOrMore(),
            ],
        )
    )
    args = load_glob.args
    assert len(args[:]) > 1
    args = args[1:]
    if len(args) == 1:
        load_glob.parent().remove()
    else:
        args.filter(m.Arg(value=m.SimpleString(value='"glob"'))).remove()

    assert q.code() == simple_bzl.replace("""load("@tools//build_defs:glob_defs.bzl", "glob")\n""", "")


def test_change_oncall(simple_bzl):
    q = Query(simple_bzl)
    oncall_func = q.find_function_call(func_name="oncall")
    arg_0 = oncall_func.args[0]
    arg_0.value.change(value='"new_oncall"')
    assert q.code() == simple_bzl.replace("there_is_no_oncall", "new_oncall")
