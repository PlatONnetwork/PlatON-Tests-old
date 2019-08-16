import rlp
from hexbytes import HexBytes


def send_raw_transaction(account, privatekey, to, w3, value, data):
    """
    发送签名交易
    :param account:
    :param privatekey:
    :param to:
    :param w3:
    :param value:
    :param data:
    :return:
    """
    nonce = w3.eth.getTransactionCount(account)
    data = rlp.encode(data)
    if value > 0:
        transaction_dict = {
            "to": to,
            "gasPrice": "0x8250de00",
            "gas": "0x6fffffff",
            "nonce": nonce,
            "data": data,
            "value": w3.toWei(value, "ether"),
            "chainId": 101,
        }
    elif not to:
        transaction_dict = {
            "gasPrice": "0x8250de00",
            "gas": "0x6fffffff",
            "nonce": nonce,
            "data": data,
            "chainId": 101,
        }
    else:
        transaction_dict = {
            "to": to,
            "gasPrice": "0x8250de00",
            "gas": "0x6fffffff",
            "nonce": nonce,
            "data": data,
            "chainId": 101,
        }
    signedTransactionDict = w3.eth.account.signTransaction(
        transaction_dict, privatekey
    )
    data = signedTransactionDict.rawTransaction
    result = HexBytes(w3.eth.sendRawTransaction(data)).hex()
    return result
