# cstq

[![PyPI - Version](https://img.shields.io/pypi/v/cstq.svg)](https://pypi.org/project/cstq)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cstq.svg)](https://pypi.org/project/cstq)

* * *

A very simple and, at least according to the author, intuitive library to navigate Python source code, and code modeling.

## Enough said, I need some action!

In code as in screenwriting, it's better to show rather than tell. So, here are a couple of examples that scratch the surface of
this library. 

### Installation

First things first, let's install the library

```console
pip install cstq
```

### Example base code

To start working with cstq, you can pass the path to a Python file or pass the module directly by:

```python

In [1]: from cstq import Query
   ...: 
   ...: q = Query(
   ...:     """
   ...: import sys
   ...: 
   ...: def main() -> None:
   ...:     import os
   ...:     print('hello world' if os.environ.get("USER") else "who are you?")
   ...: 
   ...: if __name__ == "__main__":
   ...:     main()
   ...: """
   ...: )
```

Now lets get down to business

## Basic Navigation

There are 3 types of basic navigation:

### 1. Direct Attribute Access

You can navigate by referencing attributes directly.

```python

In [2]: q


Out[2]: <CollectionOfNodes nodes=['$(Module)']>
```
```python

In [3]: q.body


Out[3]: <CollectionOfNodes nodes=['$(Module).body']>
```
```python

In [4]: q.body[:]


Out[4]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine)', '$(Module).body[1](FunctionDef)', '$(Module).body[2](If)']>
```
```python

In [5]: q.body[0].body[:]


Out[5]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body[0](Import)']>
```
and then get the node (and the code) back as

```python

In [6]: q.body[0].body[0].node()


Out[6]: Import(
    names=[
        ImportAlias(
            name=Name(
                value='sys',
                lpar=[],
                rpar=[],
            ),
            asname=None,
            comma=MaybeSentinel.DEFAULT,
        ),
    ],
    semicolon=MaybeSentinel.DEFAULT,
    whitespace_after_import=SimpleWhitespace(
        value=' ',
    ),
)
```

```python

In [7]: q.body[0].body[0].code_for_node()


Out[7]: import sys
```

```python

In [8]: q.body[0].body[:].names[0].name.node()


Out[8]: Name(
    value='sys',
    lpar=[],
    rpar=[],
)
```
### 2. Filtering

Filtering allows you to "filter" the current selection of nodes to specific ones. Each one of these accepts either a
[`libcst.matchers`](https://libcst.readthedocs.io/en/latest/matchers_tutorial.html) or a callback (more on callbacks later).
`libcst.matchers` presents a very powerful query language, and when that's not enough, you can always fall back to a custom callback.

```python

In [9]: import libcst.matchers as m
```

```python
# main root nodes

In [10]: q.body[:]


Out[10]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine)', '$(Module).body[1](FunctionDef)', '$(Module).body[2](If)']>
```

```python
# filter out function definitions using explicit filter
In [11]: q.body[:].filter(m.FunctionDef())


Out[11]: <CollectionOfNodes nodes=['$(Module).body[1](FunctionDef)']>
```

```python
# filter out function definitions using implicit filter
In [12]: q.body[m.FunctionDef()]


Out[12]: <CollectionOfNodes nodes=['$(Module).body[1](FunctionDef)']>
```

By using the `.filter` method, you can filter any selection. For instance, `q.body[:]` represents the elements of the body of
the module. However, you can also filter out by using the `__getitem__` operation (`[.. add your filter here ...]`),
making it a bit more compact.

### 3. Searching

If you want to search, not only in the current selection but also at every level, you can use `.search`. Similar
to `.filter`, it accepts a `libcst.matchers` or a callback.

```python

In [13]: q.search(m.Import())


Out[13]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body[0](Import)', '$(Module).body[1](FunctionDef).body(IndentedBlock).body[0](SimpleStatementLine).body[0](Import)']>
```

```python

# get the __name__ == "__main__" using search and filter
In [14]: q.search(m.If()).filter(lambda n: n.test.code() == '__name__ == "__main__"')


Out[14]: <CollectionOfNodes nodes=['$(Module).body[2](If)']>
```

```python
# combining multiple search and filters into a single statement 
In [15]: q.search(m.If(), lambda n: n.test.code() == '__name__ == "__main__"')


Out[15]: <CollectionOfNodes nodes=['$(Module).body[2](If)']>
```

### using callbacks

`.filter` and `.search` can take a callback method that takes an *extended version* of a CSTNode and returns true or false.
The extended version of the CSTNode its the regular CSTNode with a couple of extra methods like `.parent()` to give your the parent,
and `.code()` to generate the code that node represents, soo far I haven't added anything else.

### codemod (changes)

If you want to change nodes, it's not hard to do, for instance removing the first import would be as easy as finding it
(using any combination of `.search` and/or `.filter`) and then call `.remove()`

```python

In [16]: q.body[0].body[0].remove()
```

```python

# print the code on top

In [17]: print(q.code())
```

As you can see, there are several empty lines at the top. This is because of 2 things, first the module object is
defined to have 1 empty line as a header, and the funtion def has the leading_lines attribute set to also have a empty line

```python

In [18]: q.header[:].node()


Out[18]: EmptyLine(
    indent=True,
    whitespace=SimpleWhitespace(
        value='',
    ),
    comment=None,
    newline=Newline(
        value=None,
    ),
)
```

```python

In [19]: q.body[0]


Out[19]: <CollectionOfNodes nodes=['$(Module).body[0](FunctionDef)']>
```

```python

In [20]: q.body[0].leading_lines[:].node()


Out[20]: EmptyLine(
    indent=True,
    whitespace=SimpleWhitespace(
        value='',
    ),
    comment=None,
    newline=Newline(
        value=None,
    ),
)
```

Let's address this by simply changing the attribute `leading_lines` in that function definition using the method `.change`

```python


In [21]: q.body[0].change(leading_lines=[])


Out[21]: <CollectionOfNodes nodes=['$(Module).body[0](FunctionDef)']>
```

```python

In [22]: print(q.code())
```

you can replace a node with another one

```python
# Lets create an "import from" node and using the serach and node function,
# and then lets use that node to replace the "import" on our module.

In [23]: import_from = Query("from python_wrapper import os").search(m.ImportFrom()).node()
    ...: q.search(m.Import()).replace(import_from)
    ...: 
    ...: q.code()


Out[23]: 
def main() -> None:
    from python_wrapper import os
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
```

```python
# Let's add the import at the top level


In [24]: import libcst as cst
    ...: 
    ...: q.change(
    ...:     lambda n: n.with_changes(
    ...:         body=[cst.SimpleStatementLine(body=[import_from]), *n.body]
    ...:     )
    ...: )


Out[24]: <CollectionOfNodes nodes=['$(Module)']>
```
```python
# Let's remove the inner import
In [25]: q.search(m.FunctionDef()).search(m.ImportFrom()).remove()
```
```python
# Let's print the result
In [26]: q.code()


Out[26]: 
from python_wrapper import os
def main() -> None:
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
```

## License

`cstq` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
