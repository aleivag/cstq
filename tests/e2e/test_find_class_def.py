import libcst.matchers as m

from cstq import Query
from cstq.matchers_helpers import obj2m

TEXT = """

import unittest
from base import TestMixIn

class Foo(unittest.TestCase, TestMixIn, answer=42):
    ...

"""


def test_find_class_by_name():
    q = Query(TEXT)
    assert q.find_class_def("Foo").extended_node().name.code() == "Foo"


def test_cant_find_class_by_name():
    q = Query(TEXT)
    assert not q.find_class_def("F00")


def test_find_class_by_bases():
    q = Query(TEXT)
    assert q.find_class_def(has_bases=["unittest.TestCase"]).extended_node().name.code() == "Foo"
    assert q.find_class_def(has_bases=["TestMixIn"]).extended_node().name.code() == "Foo"
    assert q.find_class_def(has_bases=["unittest.TestCase", "TestMixIn"]).extended_node().name.code() == "Foo"


def test_cant_find_class_by_bases():
    q = Query(TEXT)
    assert not q.find_class_def(has_bases=["NOtHere"])
    assert not q.find_class_def(has_bases=["unittest.TestCase", "NotHere"])
    assert not q.find_class_def(has_bases=["unittest.TestCase", "NotHere", "TestMixIn"])
    assert not q.find_class_def(
        has_bases=[
            "NotHere",
            "unittest.TestCase",
        ]
    )


def test_find_class_by_keyword():
    q = Query(TEXT)
    assert q.find_class_def(keyword_has_value={"answer": m.Integer("42")}).node().name.value == "Foo"
    assert q.find_class_def(keyword_has_value={"answer": obj2m(42)}).node().name.value == "Foo"
