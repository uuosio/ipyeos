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
