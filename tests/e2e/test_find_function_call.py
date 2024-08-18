import cstq
import libcst.matchers as m


def test_find_function(simple_bzl_query):
    funcs = simple_bzl_query.find_function_call(func_name="rust_library")
    assert len(funcs) == 2


def test_find_function_with_has_kwargs(simple_bzl_query):
    simple_bzl_query.find_function_call(
        func_name="rust_library",
        has_kwargs={
            "name": m.SimpleString(value="'greeting'"),
        },
    ).parent().remove()

    funcs = simple_bzl_query.find_function_call(func_name="rust_library")
    assert len(funcs) == 1
    assert funcs.search(m.Arg(keyword=m.Name(value="name"))).value.code_for_node().strip("\"'") == "join"


def test_find_function_with_has_args(simple_bzl_query):
    oncall = simple_bzl_query.find_function_call(
        func_name="oncall",
        has_args=[m.SimpleString('"there_is_no_oncall"')],
    )

    assert oncall.code_for_node() == 'oncall("there_is_no_oncall")'


def test_find_function_with_filters(simple_bzl_query):
    simple_bzl_query.find_function_call(func_name="rust_library").search(
        m.Arg(keyword=m.Name(value="name"), value=m.SimpleString()), lambda n: n.value.value.strip("\"'") == "greeting"
    ).parent().parent().remove()

    funcs = simple_bzl_query.find_function_call(func_name="rust_library")
    assert len(funcs) == 1

    assert funcs.search(m.Arg(keyword=m.Name(value="name"))).value.code_for_node().strip("\"'") == "join"


def test_find_class_function_call():
    q = cstq.Query("""
class Foo(TestCase):
    def test_mytest(self):
        self.assertTrue(foo)
""")
    assert q.find_function_call("self.assertTrue").code_for_node() == "self.assertTrue(foo)"
