from cstq import Query


def test_extended_arg():
    q = Query("hello(1, True, 3, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    assert [arg.literal_eval() for arg in hello.positional_args] == [1, True, 3]


def test_extended_kwarg():
    q = Query("hello(1, True, 3, foo='bar', baz=42)")
    hello = q.find_function_call(func_name="hello").extended_node()
    assert {k: v.literal_eval() for k, v in hello.keyword_args.items()} == {"foo": "bar", "baz": 42}
