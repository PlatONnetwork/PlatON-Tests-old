import os
import sys

from eth_keys import (
    keys,
)
from eth_utils.curried import (
    keccak,
    text_if_str,
    to_bytes,
)

from common.abspath import abspath


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


def run(cmd):
    """
    本机执行cmd命令，并获取结果
    :param cmd:
    :return:
    """
    r = os.popen(cmd)
    out = r.read()
    r.close()
    return out


def get_pub_key(url, block):
    """
    根据区块信息获取签名节点
    :param url: 节点url
    :param block: 块高
    :return:
    """
    if sys.platform == "linux":
        run("chmod +x ./utils/pubkey/pubkey")
        output = run(
            "./utils/pubkey/pubkey -url={} -blockNumber={}".format(url, block))
    else:
        output = run("pubkey -url={} -blockNumber={}".format(url, block))
    if not output:
        raise Exception("无法使用获取节点id程序，windows请确保{}配置到环境变量中".format(
            abspath("./utils/pubkey")))
    if "1111" in output or "2222" in output:
        raise Exception("获取节点id异常：{}".format(output))
    return output.strip("\n")



if __name__ == "__main__":
    d = generate_key()
    print(d)
