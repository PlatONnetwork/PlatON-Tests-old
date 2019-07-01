# -*- coding: UTF-8 -*-
"""
@author: DouYuewei
@time: 2018/11/6 9:36
@usage:解析event对象data内容
"""
import re
import struct

import rlp
from web3 import Web3


def rlp_decode(data):
    if data[:2] == '0x':
        return rlp.decode(bytes.fromhex(data[2:]))
    else:
        return rlp.decode(bytes.fromhex(data))


class Event:
    """
    初始化对象需要abi的json对象
    """

    def __init__(self, abi):
        self.event_abi = [abi[i] for i in range(len(abi)) if abi[i]['type'] == 'event']

    def _event_contain_type(self, topics):
        if isinstance(topics, list):
            topics = topics[0].hex()
        for event in self.event_abi:
            if Web3.sha3(text=event['name']).hex() == topics:
                return event['inputs'], event['name']
            else:
                continue

    def event_data(self, topics, data):
        result = []
        decoded_data = rlp_decode(data)
        if self._event_contain_type(topics) is None:
            raise Exception('There is no match in your abi like this event topics :{}'.format(topics))
        else:
            event_contain_type, event_name = self._event_contain_type(topics)
        for i in range(len(event_contain_type)):
            if re.search('int', event_contain_type[i]['type'], re.IGNORECASE):
                if decoded_data[i][:1] == int(255).to_bytes(1, 'big'):
                    # unpack_length = len(decoded_data[i]) // 4
                    # fmt = ''
                    # for i in range(unpack_length):
                    #     fmt += 'i'
                    decoded_item = struct.unpack('i', decoded_data[i][::-1])[0]
                else:
                    decoded_item = int.from_bytes(decoded_data[i], byteorder='big')
                if decoded_item == '':
                    result.append(0)
                else:
                    result.append(decoded_item)
            elif re.search('string', event_contain_type[i]['type'], re.IGNORECASE):
                result.append(decoded_data[i].decode('utf-8'))
            elif re.search('bool', event_contain_type[i]['type'], re.IGNORECASE):
                result.append(bool(ord(decoded_data[i])))
            else:
                raise Exception('unsupported type {}'.format(event_contain_type[i]['type']))
        return {event_name: result}
