# cstq

[![PyPI - Version](https://img.shields.io/pypi/v/cstq.svg)](https://pypi.org/project/cstq)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cstq.svg)](https://pypi.org/project/cstq)

* * *

A very simple and, at least according to the author, intuitive library to navigate and manipulate Python source code, and code modeling based on [libcst](https://github.com/Instagram/LibCST).

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
# access the body attribute of the main module
In [3]: q.body


Out[3]: <CollectionOfNodes nodes=['$(Module).body']>
```
```python
# you can get all elements
In [4]: q.body[:]


Out[4]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine)', '$(Module).body[1](FunctionDef)', '$(Module).body[2](If)']>
```
```python
# and get the body element of every element in the body of module 
# (if they have one)
In [5]: q.body[:].body


Out[5]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body', '$(Module).body[1](FunctionDef).body(IndentedBlock)', '$(Module).body[2](If).body(IndentedBlock)']>
```

```python
# or just the body elements of the first element of the module
In [6]: q.body[0].body[:]


Out[6]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body[0](Import)']>
```
and then get the node (and the code) back as

```python

In [7]: q.body[0].body[0].node()


Out[7]: Import(
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
# and then get the code for that node
In [8]: q.body[0].body[0].code_for_node()


Out[8]: import sys
```

```python

In [9]: q.body[0].body[:].names[0].name.node()


Out[9]: Name(
    value='sys',
    lpar=[],
    rpar=[],
)
```
### 2. Filtering

The first lookup funtion we will learn is "Filtering", this allows you to "filter" the current selection of nodes to specific ones. Each one of these accepts either a
[`libcst.matchers`](https://libcst.readthedocs.io/en/latest/matchers_tutorial.html) or a callback (more on callbacks later).
`libcst.matchers` presents a very powerful query language, and when that's not enough, you can always fall back to a custom callback.

```python

In [10]: import libcst as cst
    ...: import libcst.matchers as m
```

```python
# main root nodes

In [11]: q.body[:]


Out[11]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine)', '$(Module).body[1](FunctionDef)', '$(Module).body[2](If)']>
```

```python
# filter out function definitions using explicit filter
In [12]: q.body[:].filter(m.FunctionDef())


Out[12]: <CollectionOfNodes nodes=['$(Module).body[1](FunctionDef)']>
```

```python
# filter out function definitions using implicit filter
In [13]: q.body[m.FunctionDef()]


Out[13]: <CollectionOfNodes nodes=['$(Module).body[1](FunctionDef)']>
```

By using the `.filter` method, you can filter any selection. For instance, `q.body[:]` represents the elements of the body of
the module. However, you can also filter out by using the `__getitem__` operation (`[.. add your filter here ...]`),
making it a bit more compact. Filters can also be callables, that takes one argument, the [extended node](docs/cstq_extended_node.md) and return a boolean, so we can write the previous filter as

```python
# filter out function definitions using implicit filter
In [14]: q.body[lambda node: isinstance(node, cst.FunctionDef)]


Out[14]: <CollectionOfNodes nodes=['$(Module).body[1](FunctionDef)']>
```

Finally filters can be chained very easily in some ways, the following example first get all the If that are part of the body, the second filter act over the previous selection and only picks the one that match the if **name** == "**main**" pattern.

```python

In [15]: import re
    ...: 
    ...: IF_MAIN_REGEX = re.compile(r'^ *__name__ *== *"__main__" *$')
    ...: 
    ...: q.body[m.If(), lambda node: IF_MAIN_REGEX.match(node.test.code())].code_for_node()


Out[15]: 
if __name__ == "__main__":
    main()
```

keep in mind that libcst matchers will almost always get you 99% on the way of what you want, then you may just need to take it a bit further with a custom function, for instance the previous example could have been solved with

```python


In [16]: q.body[
    ...:     m.If(
    ...:         test=m.Comparison(
    ...:             left=m.Name("__name__"),
    ...:             comparisons=[
    ...:                 m.ComparisonTarget(
    ...:                     operator=m.Equal(), comparator=m.SimpleString('"__main__"')
    ...:                 )
    ...:             ],
    ...:         )
    ...:     )
    ...: ].code_for_node()


Out[16]: 
if __name__ == "__main__":
    main()
```

I dont know that i would call it intoutive, but the matcher took you ther 100%.

### 3. Searching

The second type of lookup we will look its search. Search looks at the entire tree of teh collection, including childrens Similar
to `.filter`, it accepts a `libcst.matchers` or a callback.

```python

In [17]: q.search(m.Import())


Out[17]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body[0](Import)', '$(Module).body[1](FunctionDef).body(IndentedBlock).body[0](SimpleStatementLine).body[0](Import)']>
```

```python

In [18]: def test_for_if_main(node):
    ...:     return IF_MAIN_REGEX.match(node.test.code())
    ...: 
    ...: 
    ...: # get the __name__ == "__main__" using search and filter
    ...: q.search(m.If()).filter(test_for_if_main)


Out[18]: <CollectionOfNodes nodes=['$(Module).body[2](If)']>
```

```python
# combining multiple search and filters into a single statement 
In [19]: q.search(m.If(), test_for_if_main).code_for_node()


Out[19]: 
if __name__ == "__main__":
    main()
```

### 4. finding

for simplicity there are a couple of `find_*` methods that can be used to find specific structures, that makes things easier. These are

* **find_assignment**: find an assigment   

```python

In [1]: from cstq import Query
   ...: 
   ...: config = Query(
   ...:     """
   ...: MAGIC_CONSTANTS = [
   ...:    1, 
   ...:    2, 
   ...:    3, 
   ...:    "foo", 
   ...:    3j
   ...: ]
   ...: """
   ...: )
   ...: 
   ...: assignment = config.find_assignment(variable_name="MAGIC_CONSTANTS")
   ...: 
   ...: # convert the node into an actuall python object
   ...: assignment.value.literal_eval_for_node()


Out[1]: [1, 2, 3, 'foo', 3j]
```

* **find_function_call**: helps finding a particular funtion call.

```python

In [1]: from cstq import Query
   ...: 
   ...: q = Query(
   ...:     """
   ...: x = [2,1,3]
   ...: sx = sorted(x)
   ...: rx = sorted(x, reverse=True)
   ...: 
   ...: """
   ...: )
   ...: 
   ...: q.find_function_call(func_name="sorted").code_for_nodes()


Out[1]: ['sorted(x)', 'sorted(x, reverse=True)']
```
```python

In [2]: import libcst.matchers as m
   ...: 
   ...: q.find_function_call(
   ...:     func_name="sorted", has_kwargs={"reverse": m.Name("True")}
   ...: ).code_for_node()


Out[2]: sorted(x, reverse=True)
```

### using callbacks

`.filter` and `.search` can take a callback method that takes an *extended version* of a CSTNode and returns true or false.
The extended version of the CSTNode its the regular CSTNode with a couple of extra methods like `.parent()` to give your the parent,
and `.code()` to generate the code that node represents, soo far I haven't added anything else.

### codemod (changes)

If you want to change your python document, it's not hard to do, we provide a couple of simple methods like

* **`.change(callable, **kwargs)`**: to change the contents of a collection of nodes.
* **`.replace(node)`**: change the collection of nodes for a new one.
* **`.remove()`**: removes every node from the collection of nodes.
* **`.insert(index, node)`** : if the collection of nodes are a range, this insert the node, in the position index.
* **`.append(node)`** : add the node to the end of the range of nodes
* **`.extend(list[node] | collection of nodes)`** :extend the range to the collection or list of nodes

for instance removing the first import would be as easy as finding it
(using any combination of `.search` and/or `.filter`) and then call `.remove()`

```python

In [20]: q.body[0].body[0].remove()
```

```python
# print the code on top
In [21]: q.code()


Out[21]: 

def main() -> None:
    import os
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
```

As you can see, there are several empty lines at the top. This is because of 2 things, first the module object is
defined to have 1 empty line as a header, and the funtion def has the leading_lines attribute set to also have a empty line

```python

In [22]: q.header[:].node()


Out[22]: EmptyLine(
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

In [23]: q.body[0]


Out[23]: <CollectionOfNodes nodes=['$(Module).body[0](FunctionDef)']>
```

```python

In [24]: q.body[0].leading_lines[:].node()


Out[24]: EmptyLine(
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

In [25]: q.body[0].change(leading_lines=[])


Out[25]: <CollectionOfNodes nodes=['$(Module).body[0](FunctionDef)']>
```

```python

In [26]: q.code()


Out[26]: 
def main() -> None:
    import os
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
```

for more complex changes, instead of passing the attributes to change, you can pass a callback

```python
# reverse the order of leading lines

In [27]: q.body[0].change(lambda node: node.with_changes(leading_lines=node.leading_lines[::-1]))


Out[27]: <CollectionOfNodes nodes=['$(Module).body[0](FunctionDef)']>
```

you can replace a node with another one

```python
# Lets create an "import from" node and using the serach and node function,
# and then lets use that node to replace the "import" on our module.

In [28]: import_from = Query("from python_wrapper import os").search(m.ImportFrom()).node()
    ...: 
    ...: q.search(m.Import()).replace(import_from)
    ...: q.code()


Out[28]: 
def main() -> None:
    from python_wrapper import os
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
```

To add a import at the top of the file, we can `.insert` the new node at the top, like this

```python
# Let's add the import at the top level

In [29]: import libcst as cst
    ...: 
    ...: q.body.insert(0, cst.SimpleStatementLine(body=[import_from]))
```

```python
# Let's remove the inner import
In [30]: q.search(m.FunctionDef()).search(m.ImportFrom()).remove()
```
```python
# Let's print the result
In [31]: q.code()


Out[31]: 
from python_wrapper import os
def main() -> None:
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
```

adding a call at the end would be as easy as

```python
# using extend to add a few lines at the end of the document


In [32]: EXTRA_LINES = Query(
    ...:     """
    ...: import my_custom_logging
    ...: my_custom_logging.log(__file__)
    ...:     """
    ...: )
    ...: 
    ...: q.body.extend(EXTRA_LINES.body[:])
    ...: 
    ...: q.code()


Out[32]: 
from python_wrapper import os
def main() -> None:
    print('hello world' if os.environ.get("USER") else "who are you?")

if __name__ == "__main__":
    main()
import my_custom_logging
my_custom_logging.log(__file__)
```

### CST to objects and object to CST

One particular thing this library tries to do, its to give you many representations of the data, so you
can interact with the source code as conformable as you can, for this sometimes you want to grab a python
object from the source code and treat it as its regular object and then turn the result back to its
CST representation this is not extremely hard to do 

```python

In [33]: from cstq import Query, obj2cst
    ...: import libcst.matchers as m
    ...: 
    ...: q = Query(
    ...:     """
    ...: X = [1, 2, 3, "foo", 3j]
    ...: """
    ...: )
    ...: 
    ...: the_list = q.search(m.List())
    ...: the_list


Out[33]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body[0](Assign).value(List)']>
```

```python
# now we can turn that cst.List object into a python list using using `literal_eval_for_node`

In [34]: real_list = the_list.literal_eval_for_node()
    ...: f"type({real_list}) = {type(real_list)} "


Out[34]: type([1, 2, 3, 'foo', 3j]) = <class 'list'> 
```

```python
# lets remove non integers for it and lets write it back to the cst


In [35]: only_int_list = obj2cst([e for e in real_list if isinstance(e, int)])
    ...: 
    ...: the_list.replace(only_int_list)
    ...: 
    ...: q.code()


Out[35]: 
X = [1, 2, 3]
```

## License

`cstq` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
