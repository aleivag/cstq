# Call (Call)

Once you found a function call using `find_function_call` or actually any Call, you can then get an extended node and quickly get information out of it, and also modify it

for this examples lets assume this code

```python

In [1]: from cstq import Query
   ...: 
   ...: q = Query(
   ...:     """
   ...: 
   ...: subprocess.run(["/bin/echo",  "hello world"], text=True, env={"HOME": "/tmp"})
   ...: 
   ...: """
   ...: )
   ...: 
   ...: collection = q.find_function_call("subprocess.run")
```

```python

In [2]: node = collection.extended_node()
   ...: node


Out[2]: Call(
    root=<CollectionOfNodes nodes=['$(Module)']>,
    node_id='$(Module).body[0](SimpleStatementLine).body[0](Expr).value(Call)',
)
```

```python

In [3]: node.code()


Out[3]: subprocess.run(["/bin/echo",  "hello world"], text=True, env={"HOME": "/tmp"})
```

## name

you might want to get the name of the funtion, for this you can just call:

```python

In [4]: node.func_name


Out[4]: subprocess.run
```

sadly I still have not made modifying this attribute "simple", but its not really that hard, you just need to do

```python

In [5]: from cstq import str2attr
   ...: 
   ...: node.change(func=str2attr("subprocess.check_call"))
   ...: node.code()


Out[5]: subprocess.check_call(["/bin/echo",  "hello world"], text=True, env={"HOME": "/tmp"})
```

# positional arguments

getting and modifying positional arguments its super easy

```python
# gets the first positional argument 
In [6]: node.positional_args[0]


Out[6]: List(
    root=<CollectionOfNodes nodes=['$(Module)']>,
    node_id='$(Module).body[0](SimpleStatementLine).body[0](Expr).value(Call).args[0](Arg).value(List)',
)
```

```python
# gets the first positional argument, turns it into a real python array 
In [7]: node.positional_args[0].literal_eval()


Out[7]: ['/bin/echo', 'hello world']
```

```python
# modify it now
In [8]: import shlex
   ...: from cstq import obj2cst
   ...: 
   ...: old_array = shlex.join(node.positional_args[0].literal_eval())
   ...: node.positional_args[0] = obj2cst(["/bin/bash", "-c", old_array])
   ...: node.code()


Out[8]: subprocess.check_call(['/bin/bash', '-c', "/bin/echo 'hello world'"], text=True, env={"HOME": "/tmp"})
```

# keyword arguments

same as positional arguments, but instead of reading an array, you use a dict (shocker i know!)

```python
# gets the env param as a dict
In [9]: old_env = node.keyword_args["env"].literal_eval()
   ...: new_env = {
   ...:     **old_env,
   ...:     "MOD_WITH_CSTQ": "1",
   ...:     "HOME": ":".join(["/usr/local/bin", old_env["HOME"]]),
   ...: }
   ...: 
   ...: # sets a new env param
   ...: node.keyword_args["env"] = obj2cst(new_env)
   ...: 
   ...: # remove the text attribute
   ...: del node.keyword_args["text"]
   ...: 
   ...: # shows all the changes
   ...: node.code()


Out[9]: subprocess.check_call(['/bin/bash', '-c', "/bin/echo 'hello world'"], env={'HOME': '/usr/local/bin:/tmp', 'MOD_WITH_CSTQ': '1'})
```