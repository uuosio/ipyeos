from ipyeos.bases import utils
def test_utils():
    block_id = '12e684f7a9ff29faee988e13ce23c1cf21e3082e71bc69fe589bfdca4cbbda1f'
    assert 317097207 == utils.get_block_num_from_block_id(block_id)
