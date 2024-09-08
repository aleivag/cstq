from textwrap import dedent

import libcst.matchers as m

from cstq import Query


def test_str_bases_are_returned():
    class_enode = Query("class Foo(unittest.TestCase, TestMixIn): ...").find_class_def("Foo").extended_node()
    # assert not class_enode
    assert list(class_enode.str_bases) == ["unittest.TestCase", "TestMixIn"]


def test_str_bases_can_be_removed():
    q = Query("class Foo(unittest.TestCase, TestMixIn): ...")
    class_enode = q.find_class_def("Foo").extended_node()
    # assert not class_enode
    class_enode.str_bases.pop()
    assert list(class_enode.str_bases) == ["unittest.TestCase"]
    assert q.code() == "class Foo(unittest.TestCase, ): ..."


def test_str_bases_can_be_changed():
    q = Query("class Foo(unittest.TestCase, TestMixIn): ...")
    class_enode = q.find_class_def("Foo").extended_node()
    # assert not class_enode
    idx = class_enode.str_bases.index("unittest.TestCase")
    class_enode.str_bases[idx] = "unittest.IsolatedAsyncioTestCase"
    assert list(class_enode.str_bases) == ["unittest.IsolatedAsyncioTestCase", "TestMixIn"]
    assert q.code() == "class Foo(unittest.IsolatedAsyncioTestCase, TestMixIn): ..."


def test_str_bases_can_be_added():
    q = Query("class Foo(unittest.TestCase, TestMixIn): ...")
    class_enode = q.find_class_def("Foo").extended_node()
    # assert not class_enode
    class_enode.str_bases.append("internal._asyncio.ASyncTestMixIn")
    assert q.code() == "class Foo(unittest.TestCase, TestMixIn, internal._asyncio.ASyncTestMixIn): ..."


def test_str_bases_add_from_none():
    q = Query("class Foo: ...")
    class_enode = q.find_class_def("Foo").extended_node()
    # assert not class_enode
    class_enode.str_bases.append("Bar")
    assert q.code() == "class Foo(Bar): ..."


def test_str_bases_can_be_assigned_empty_list():
    q = Query("class Foo(unittest.TestCase, TestMixIn): ...")
    class_enode = q.find_class_def("Foo").extended_node()
    # assert not class_enode
    class_enode.str_bases = []
    assert q.code() == "class Foo(): ..."


def test_str_bases_can_be_asigned_partial_list():
    q = Query("class Foo: ...")
    class_enode = q.find_class_def("Foo").extended_node()
    # assert not class_enode
    class_enode.str_bases = ["Bar", "Baz"]
    assert q.code() == "class Foo(Bar, Baz): ..."


def test_str_bases_can_be_deleted():
    q = Query("class Foo(unittest.TestCase, TestMixIn): ...")
    class_enode = q.find_class_def("Foo").extended_node()
    # assert not class_enode
    del class_enode.str_bases
    assert q.code() == "class Foo: ..."


def test_str_bases_can_be_deleted_kepp_par_with_keywords():
    q = Query("class Foo(unittest.TestCase, TestMixIn, answer=42): ...")
    class_enode = q.find_class_def("Foo").extended_node()
    # assert not class_enode
    del class_enode.str_bases
    assert q.code() == "class Foo(answer=42): ..."


### testing changing the import name of a method


def test_change_test_case_to_isolated_asyncio_testcase():
    q = Query(
        dedent(
            """
            import unittest
            from unittest import TestCase, mock

            class Test(unittest.TestCase):
                ...

            class Test2(TestCase):
                ...

            """
        )
    )

    if q.find_import_alias(["unittest"]):
        q.find_class_def(has_bases=["unittest.TestCase"]).change(
            lambda node: node.replace_base("unittest.TestCase", "unittest.IsolatedAsyncioTestCase")
        )

    if imp := q.find_import_from(["unittest"]):
        imp.search(m.Name(value="TestCase")).change(value="IsolatedAsyncioTestCase")  # this should be easier

        # we should change the imp to a much simpler one
        q.find_class_def(has_bases=["TestCase"]).change(
            lambda node: node.replace_base("TestCase", "IsolatedAsyncioTestCase")
        )

    assert q.root.code() == dedent(
        """
        import unittest
        from unittest import IsolatedAsyncioTestCase, mock

        class Test(unittest.IsolatedAsyncioTestCase):
            ...

        class Test2(IsolatedAsyncioTestCase):
            ...

        """
    )
