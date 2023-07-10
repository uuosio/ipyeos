html = """
<html>
<h1>Helper</h1>
<head>
</head>

<p><strong>Commands:</strong></p>
<ul>
<li><code>exec(code)</code>: This command is used to execute the provided Python code. The code should be passed as a string.</li>
</ul>
<p><strong>Example:</strong></p>
<p>```python</p>
<p>import requests</p>
<p>code = '''
  from ipyeos import eos</p>
<p>def test():
      eos.set_info_level("net_plugin_impl")
      eos.set_info_level("default")</p>
<p>eos.post(test)
  '''</p>
<p>r = requests.post('http://127.0.0.1:7777/exec', data={'code': code})
</p>
<p>  print(r.text)</p>
<p>```</p>
<ul>
<li><code>ipython()</code>: This command launches an interactive IPython session.</li>
</ul>
<p><strong>Example:</strong></p>
<pre><code>curl -X POST http://127.0.0.1:7777/ipython
</code></pre>
<ul>
<li>
<p><code>ikernel()</code>: This command starts an IKernel (Interactive Kernel) session. The IKernel provides a Jupyter notebook interface for interactive computing.</p>
</li>
<li>
<p><code>quit()</code>: This command is used to exit the application.</p>
</li>
</ul>
</html>
"""
