Call (Call)
====================

Once you found a function call using `find_function_call` or actually any Call, you can then get an extended node and quickly get information out of it, and also modify it

for this examples lets assume this code

```dumas[python]

from cstq import Query

q = Query("""

subprocess.run(["/bin/echo",  "hello world"], text=True, env={"HOME": "/tmp"})

""")

collection = q.find_function_call("subprocess.run")
```

```dumas[python]
node = collection.extended_node()
node
```

```dumas[python]
node.code()
```

name
----

you might want to get the name of the funtion, for this you can just call:

```dumas[python]
node.func_name
```

sadly I still have not made modifying this attribute "simple", but its not really that hard, you just need to do

```dumas[python]
from cstq import str2attr
node.change(func=str2attr("subprocess.check_call"))
node.code()
```

positional arguments
===================

getting and modifying positional arguments its super easy

```dumas[python]
# gets the first positional argument 
node.positional_args[0]
```


```dumas[python]
# gets the first positional argument, turns it into a real python array 
node.positional_args[0].literal_eval()
```

```dumas[python]
# modify it now
import shlex
from cstq import obj2cst
old_array = shlex.join(node.positional_args[0].literal_eval())
node.positional_args[0] = obj2cst(["/bin/bash", "-c", old_array])
node.code()
```

keyword arguments
=================

same as positional arguments, but instead of reading an array, you use a dict (shocker i know!)

```dumas[python]
# gets the env param as a dict
old_env = node.keyword_args["env"].literal_eval()
new_env = {**old_env, "MOD_WITH_CSTQ": "1", "HOME": ":".join(["/usr/local/bin", old_env["HOME"]])} 

# sets a new env param
node.keyword_args["env"] = obj2cst(new_env) 

# remove the text attribute
del node.keyword_args["text"]

# shows all the changes
node.code()
```