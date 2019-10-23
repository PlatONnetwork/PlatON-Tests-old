import os
from eth_keys import (
    keys,
)
from eth_utils.curried import (
    keccak,
    text_if_str,
    to_bytes,
)


def generate_key():
    """
    生成节点公私钥
    :return:
        私钥
        公钥
    """
    extra_entropy = ''
    extra_key_bytes = text_if_str(to_bytes, extra_entropy)
    key_bytes = keccak(os.urandom(32) + extra_key_bytes)
    privatekey = keys.PrivateKey(key_bytes)
    return privatekey.to_hex()[2:], keys.private_key_to_public_key(privatekey).to_hex()[2:]


def get_pub_key(web3, block_number):
    pass