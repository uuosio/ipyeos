import os

from .chaintester import ChainTester
from .. import eos
from ..node import node_config
from ..bases import args

config_str = '''
# worker_processes:
#   - "127.0.0.1:8809"
#   - "/tmp/uvicorn.sock"

# debug_port: 7777
# rpc_address: '127.0.0.1:8089'

#-------------------------------------

#resource-monitor-space-absolute-gb: 1
resource-monitor-space-threshold: 99

http-server-address: 0.0.0.0:8889

data_dir: "dd"
config_dir: "cd"

producer-name: eosio
enable-stale-production:

trace-no-abis:

disable-replay-opts:

plugin:
  - eosio::chain_api_plugin
#   - eosio::state_history_plugin

# chain-state-history:
# trace-history:

chain-state-db-size-mb: 256
chain-state-db-guard-size-mb: 10
'''

def init(config_file: str):
    """
    Initializes the testnet environment with the specified configuration file.
    If config_file is empty, load `config-testnet.yaml` if it exists,
    otherwise use `config_str` as the configuration and write it to `config-testnet.yaml`.

    Args:
        config_file: A string that specifies the path to the configuration file to use.

    Returns:
        None.

    Raises:
        KeyError: If the configuration file is missing required keys.
        OSError: If there is an error creating the testnet directories.
    """
    config = None
    if config_file:
        config = node_config.load_config(config_file)
    else:
        if os.path.exists('config-testnet.yaml'):
            config = node_config.load_config('config-testnet.yaml')
        else:
            config = node_config.load_config_from_str(config_str)
            with open('config-testnet.yaml', 'w') as f:
                f.write(config_str)
    try:
        data_dir = config['data_dir']
        config_dir = config['config_dir']
    except KeyError:
        if not os.path.exists('testnet'):
            os.mkdir('testnet')
        data_dir = 'testnet/dd'
        config_dir = 'testnet/cd'
        config['data_dir'] = data_dir
        config['config_dir'] = config_dir

    if not os.path.exists(data_dir):
        # init testnet
        eos.set_error_level("default")
        t = ChainTester(True, data_dir = data_dir, config_dir = config_dir)
        t.free()
        eos.set_info_level("default")
