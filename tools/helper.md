# Commands

## `exec`

This command is used to execute the provided Python code. The code should be passed as a string.

**Example:**

```python
import requests

code = '''
from ipyeos import eos

def test():
    eos.set_info_level("net_plugin_impl")
    eos.set_info_level("default")
    
eos.post(test)
'''

r = requests.post('http://127.0.0.1:7777/exec', data={'code': code})

print(r.text)
```

## `ipython`

This command launches an interactive IPython session.

**Example:**

```bash
    curl -X POST http://127.0.0.1:7777/ipython
```

## `ikernel`

This command starts an IKernel (Interactive Kernel) session. The IKernel provides a Jupyter notebook interface for interactive computing.

**Example:**

```bash
    curl -X POST http://127.0.0.1:7777/ikernel
```

## `quit`

This command is used to exit the application.

**Example:**

```bash
    curl -X POST http://127.0.0.1:7777/quit
```
