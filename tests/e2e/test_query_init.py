import libcst as cst
import pytest

from cstq import Query


def test_init_works_with_string():
    q = Query(
        mod_text := """
# this is a random module
one = 1
two = one + one
    """.strip()
    )
    assert mod_text == q.code()


def test_init_works_with_path(tmp_path):
    test_file = tmp_path / "module.py"
    test_file.write_text(
        mod_text := """
# this is a random module
one = 1
two = one + one
    """.strip()
    )
    assert mod_text == Query(test_file).code()


def test_init_works_with_cstmodule():
    test_module = cst.parse_module(
        mod_text := """
# this is a random module
one = 1
two = one + one
    """.strip()
    )
    assert mod_text == Query(test_module).code()


def test_init_fail_with_non_module_node():
    with pytest.raises(RuntimeError) as exc_info:
        Query(cst.SimpleString(value="'value'"))
    assert str(exc_info.value) == "Cant parse <class 'libcst._nodes.expression.SimpleString'> as module"


def test_write(tmp_path):
    test_file = tmp_path / "dest.py"
    Query(
        mod_text := """
# this is a random module
one = 1
two = one + one
    """.strip()
    ).write(test_file)
    assert test_file.read_text() == mod_text


def test_no_bool(tmp_path):
    q = Query("foo=42")
    u = q.pop
    if u:
        msg = f"we should be False!!!, {u}, {bool(u)}, {len(u)}"
        raise Exception(msg)
