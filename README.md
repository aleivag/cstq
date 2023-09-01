# cstq

[![PyPI - Version](https://img.shields.io/pypi/v/cstq.svg)](https://pypi.org/project/cstq)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cstq.svg)](https://pypi.org/project/cstq)

-----

Very simple and, at least according to the author, intuitive library to navegate python source code, and codemoding.

## Nuf' said, i need some action

In codi as in screenright, it's better to show don't tell, so here are a couple of examples, that scratch the surface of 
this library

### navegate source controll

```python
from cstq import Query

Query("""

import request

page = request.get("https://raw.githack.com/aleivag/libcst-sandbox/main/index.html")

""")


```

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install cstq
```

## License

`cstq` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
