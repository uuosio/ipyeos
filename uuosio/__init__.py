import sys
from . import _uuos

class CustomImporter(object):
    def find_module(self, fullname, mpath=None):
#        print('+++find_module', fullname)
        if fullname in ['_chain', '_chainapi']:
            return self
        return

    def load_module(self, module_name):
#        print('+++load_module', module_name)
        mod = sys.modules.get(module_name)
        if mod is None:
            uuos_module = sys.modules.get('uuosio._uuos')
            if not uuos_module:
                return
            uuos_so = uuos_module.__file__
            from importlib import util
            spec = util.spec_from_file_location(module_name, uuos_so)
            mod = util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[module_name] = mod
        return mod

sys.meta_path.append(CustomImporter())

import _chain
import _chainapi