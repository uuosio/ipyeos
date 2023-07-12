html = """
<html>
<head>
<link href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism.min.css" rel="stylesheet" />
</head>

<body>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>

<h1>Commands</h1>

<h2><code>exec</code></h2>

<p>This command is used to execute the provided Python code. The code should be passed as a string.</p>

<p><strong>Example:</strong></p>

<pre><code class="language-python">
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
</code></pre>

<h2><code>ipython</code></h2>

<p>This command launches an interactive IPython session.</p>

<p><strong>Example:</strong></p>

<pre><code class="language-bash">
    curl -X GET http://127.0.0.1:7777/ipython
</code></pre>

<h2><code>ikernel</code></h2>

<p>This command starts an IKernel (Interactive Kernel) session. The IKernel provides a Jupyter notebook interface for interactive computing.</p>

<p><strong>Example:</strong></p>

<pre><code class="language-bash">
    curl -X GET http://127.0.0.1:7777/ikernel
</code></pre>

<h2><code>quit</code></h2>

<p>This command is used to exit the application.</p>

<p><strong>Example:</strong></p>

<pre><code class="language-bash">
    curl -X GET http://127.0.0.1:7777/quit
</code></pre>

</body>
</html>
"""
