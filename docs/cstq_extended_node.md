# CSTQExtendedNode

This is the node your get when you are filtering, searching, and in general exploring the cst

# Literal eval

Python standard library comes with a very simple function in the ast module called
[literal_eval](https://docs.python.org/3/library/ast.html#ast.literal_eval), this allows to... well\
eval a literal value into a python object *without* executing its contents. I recommend read the docs for that function
as you need to be carefully on what to use it on. But safety aside, its usefull to convert libcst's SimpleString, Integer, List
and other into a python object.

```python

In [1]: from cstq import Query
   ...: 
   ...: q = Query(
   ...:     """
   ...: X = {
   ...:     "a string": "one element",
   ...:     "a int": 42,
   ...:     "a set": {"a", "set"},
   ...:     "a tuple": ("a", "tuple"),
   ...:     "an array": ["an", "array"], 
   ...: }
   ...: 
   ...: """
   ...: )
   ...: 
   ...: q.body


Out[1]: <CollectionOfNodes nodes=['$(Module).body']>
```

```python

In [2]: import libcst.matchers as m
   ...: 
   ...: the_dict = q.search(m.Dict()).literal_eval_for_node()
```

```python

In [3]: the_dict


Out[3]: {'a string': 'one element', 'a int': 42, 'a set': {'a', 'set'}, 'a tuple': ('a', 'tuple'), 'an array': ['an', 'array']}
```

```python

In [4]: the_dict["a int"]


Out[4]: 42
```

this is usefull, because you can also get a literal eval for an extended node

```python

In [5]: node = q.search(m.Dict()).extended_node()
   ...: node.literal_eval()


Out[5]: {'a string': 'one element', 'a int': 42, 'a set': {'a', 'set'}, 'a tuple': ('a', 'tuple'), 'an array': ['an', 'array']}
```

and it can be use in filters and searches, like in this example

```python

In [6]: q.search(m.Dict(), lambda node: node.literal_eval()["a int"] == 42)


Out[6]: <CollectionOfNodes nodes=['$(Module).body[0](SimpleStatementLine).body[0](Assign).value(Dict)']>
```

where we can search for all Dicts, and then liteeral_eval that node and ask for the "a int" element. watchout because not
all Dict can be literal_eval. literal_eval only works for simple python objects.

# parent

A pretty cool feature of extended nodes, is that they know their parents, so you can easily ask for them.

# Specific nodes

* [ClassDef](extended_nodes/class_def.md)
* [Call](extended_nodes/call.md)
