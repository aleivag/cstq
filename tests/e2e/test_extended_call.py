import libcst as cst
import libcst.matchers as m

from cstq import Query


def test_extended_arg():
    q = Query("hello(1, True, 3, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    assert [arg.literal_eval() for arg in hello.positional_args] == [1, True, 3]


def test_extended_kwarg():
    q = Query("hello(1, True, 3, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    assert {k: v.literal_eval() for k, v in hello.keyword_args.items()} == {"foo": "bar", "baz": 42}


def test_extended_kwarg_add():
    q = Query("hello(1, True, 3, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    hello.keyword_args["nope"] = cst.Name(value="None")
    # there is an extra space in nope = None, might want to check that out...
    # formatting will always be a problem
    assert q.code() == "hello(1, True, 3, foo='bar', baz=42, nope = None)"


def test_extended_kwarg_change():
    q = Query("hello(1, True, 3, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    hello.keyword_args["baz"] = cst.Name(value="None")
    # there is an extra space in nope = None, might want to check that out...
    # formatting will always be a problem
    assert q.code() == "hello(1, True, 3, foo='bar', baz=None)"


def test_extended_kwarg_remove():
    q = Query("hello(1, True, 3, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    del hello.keyword_args["baz"]
    # there is an extra space in nope = None, might want to check that out...
    # formatting will always be a problem
    assert q.code() == "hello(1, True, 3, foo='bar', )"


def test_extended_arg_get():
    q = Query("hello(1, True, None, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    assert hello.positional_args[0].literal_eval() == 1
    assert hello.positional_args[1].literal_eval() is True
    assert hello.positional_args[2].literal_eval() is None


def test_extended_arg_set():
    q = Query("hello(1, True, None, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    hello.positional_args[0] = cst.Name("object")
    assert q.code() == "hello(object, True, None, foo='bar', baz=42)"


def test_extended_arg_del():
    q = Query("hello(1, True, None, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    del hello.positional_args[0]
    assert q.code() == "hello(True, None, foo='bar', baz=42)"


def test_extended_arg_insert():
    q = Query("hello(1, True, None, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    hello.positional_args.insert(0, cst.Name("object"))
    assert q.code() == "hello(object, 1, True, None, foo='bar', baz=42)"
