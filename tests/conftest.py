import pytest

import cstq


@pytest.fixture()
def CSTQuery():  # noqa: N802
    return cstq.Query


@pytest.fixture()
def simple_bzl():
    """
    returns a simple bzl file that can be used for testing
    """
    return """
load("@build//:rust_binary.bzl", "rust_binary")
load("@build//:rust_library.bzl", "rust_library", "rust_library_helpers")
load("@tools//build_defs:glob_defs.bzl", "glob")

oncall("there_is_no_oncall")

rust_binary(
  name='greet',
  srcs=[
    'greet.rs',
  ],
  deps=[
    ':greeting',
  ],
)

rust_library(
  name='greeting',
  srcs=[
    'greeting.rs',
  ],
  deps=[
    ':join',
  ],
)

rust_library(
  name='join',
  srcs=[
    'join.rs',
  ],
)
    """.strip()


@pytest.fixture()
def simple_bzl_query(
    CSTQuery,  # noqa: N803
    simple_bzl,
):
    return CSTQuery(simple_bzl)
